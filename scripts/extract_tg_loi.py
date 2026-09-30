#!/usr/bin/env python3
from __future__ import annotations
import hashlib, io, json, os, re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlparse
import pandas as pd, requests
from bs4 import BeautifulSoup

try:
    from .pairing import normalize_label, normalized_pair_key, reviewed_metadata, evidence_issues
except ImportError:  # Direct script execution.
    from pairing import normalize_label, normalized_pair_key, reviewed_metadata, evidence_issues

ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'; AUTO=DATA/'automation'; INC=DATA/'incoming'
CAND=AUTO/'candidate_extractions.csv'; EXT=AUTO/'auto_extracted.csv'; REVIEW=AUTO/'review_queue.csv'; STATE=AUTO/'auto_extract_state.json'; MASTER=DATA/'tg_loi_master.csv'
PAIR_REVIEWS=DATA/'curation'/'pair_reviews.csv'
AUTO.mkdir(parents=True,exist_ok=True); INC.mkdir(parents=True,exist_ok=True)
EXTRACTOR_VERSION='6'; HEAD={'User-Agent':'textile-tga-database/1.1 (public academic data curation; GitHub PolyFT/textile-tga-database)'}
ALLOWED={'pmc.ncbi.nlm.nih.gov','europepmc.org','www.europepmc.org','www.mdpi.com','mdpi.com','pubs.rsc.org','www.frontiersin.org','link.springer.com','journals.sagepub.com','www.hindawi.com','onlinelibrary.wiley.com'}
NUM=re.compile(r'[-+]?\d+(?:\.\d+)?'); RANGE=re.compile(r'\d+(?:\.\d+)?\s*(?:-|–|—|to)\s*\d+(?:\.\d+)?',re.I); UNC=re.compile(r'(\d+(?:\.\d+)?)\s*(?:±|\+/-)\s*(\d+(?:\.\d+)?)')
RATE1=re.compile(r'(?:heating\s*rate|heated[^.;\n]{0,80}?at|heating\s+at|rate\s+of)[^.;\n]{0,80}?(\d+(?:\.\d+)?)\s*(?:°\s*C|℃|K)\s*(?:/|per)\s*min(?:ute)?',re.I)
RATE2=re.compile(r'(\d+(?:\.\d+)?)\s*(?:°\s*C|℃|K)\s*(?:/|per)\s*min(?:ute)?',re.I)
ATM=[('N2',re.compile(r'\b(?:nitrogen|N\s*2|N₂)\b',re.I)),('air',re.compile(r'\b(?:air|oxidative atmosphere)\b',re.I)),('O2',re.compile(r'\b(?:oxygen|O\s*2|O₂)\b',re.I)),('argon',re.compile(r'\b(?:argon|Ar)\b',re.I))]
TG_PAT=[('T1_C',r'\bT\s*1\b|1\s*%.*loss'),('T5_C',r'\bT\s*5\b|5\s*%.*loss|T\s*d\s*,?\s*5'),('T10_C',r'\bT\s*10\b|10\s*%.*loss|T\s*d\s*,?\s*10'),('T20_C',r'\bT\s*20\b|20\s*%.*loss'),('T40_C',r'\bT\s*40\b|40\s*%.*loss'),('T50_C',r'\bT\s*50\b|50\s*%.*loss'),('Tonset_C',r'T\s*onset|onset\s*(?:temperature)?|initial decomposition temperature'),('Tmax2_C',r'T\s*max\s*2|second.*peak'),('Tmax3_C',r'T\s*max\s*3|third.*peak'),('Tmax1_C',r'T\s*max(?:\s*1)?|T\s*dmax|peak\s*(?:decomposition\s*)?temperature')]
TG_PAT=[(k,re.compile(p,re.I)) for k,p in TG_PAT]
WASH_RE=re.compile(r'(?:after\s*)?(\d+)\s*(?:wash(?:ing)?|launder(?:ing)?)\s*(?:cycles?|times?)?',re.I)

def doi(v):
    x=str(v or '').strip().lower(); x=re.sub(r'^https?://(?:dx\.)?doi\.org/','',x); return re.sub(r'^doi:\s*','',x).rstrip(' .;,')
def ns(v):
    return normalize_label(v)
def exact(v):
    s=str(v or '').strip()
    if not s or RANGE.search(s) or re.search(r'[<>~≈]',s): return None,None
    m=UNC.search(s)
    if m:return float(m.group(1)),float(m.group(2))
    a=NUM.findall(s); return (float(a[0]),None) if len(a)==1 else (None,None)
def wash_state(text):
    m=WASH_RE.search(str(text or ''))
    return f"after {int(m.group(1))} wash cycles" if m else ''

def flat(df):
    d=df.copy(); d.columns=[' | '.join(str(z) for z in c if str(z)!='nan').strip() if isinstance(c,tuple) else str(c).strip() for c in d.columns]; return d.reset_index(drop=True)
def sample_col(df,exclude):
    pref=re.compile(r'sample|specimen|fabric|textile|code|formulation|composition|treatment',re.I)
    for c in df.columns:
        if c not in exclude and pref.search(c): return c
    best=None
    for c in df.columns:
        if c in exclude: continue
        vals=df[c].dropna().astype(str).head(30)
        if len(vals)<2: continue
        score=sum(bool(re.search('[A-Za-z]',v)) for v in vals)-sum(bool(re.fullmatch(r'\s*[-+]?\d+(?:\.\d+)?\s*',v)) for v in vals)
        if best is None or score>best[0]: best=(score,c)
    return best[1] if best else None
def tga_snips(text):
    scored=[]
    for m in re.finditer(r'\b(?:TGA|TG/DTG|thermogravimetric(?: analysis)?|thermogravimetry)\b',text,re.I):
        z=text[m.start():min(len(text),m.end()+650)]
        score=3*bool(re.search(r'heating\s*rate|heated\s+from|°\s*C\s*/\s*min|℃\s*/\s*min',z,re.I))+2*bool(re.search(r'flow\s*rate|mL\s*/\s*min',z,re.I))+bool(re.search(r'nitrogen|\bair\b|argon',z,re.I))
        scored.append((score,z))
    scored.sort(key=lambda x:x[0],reverse=True)
    return scored[0][1] if scored else ''
def atmos(text): return list(dict.fromkeys(n for n,p in ATM if p.search(text)))
def infer_atm(full,context,header=''):
    for p in [header,context]:
        a=atmos(p)
        if len(a)==1:return a[0]
    a=atmos(tga_snips(full)); return a[0] if len(a)==1 else None
def infer_rate(full,context):
    for p in [context,tga_snips(full)]:
        vals={float(x) for x in RATE1.findall(p)} or {float(x) for x in RATE2.findall(p)}
        if len(vals)==1:return next(iter(vals))
    return None
def residue(h):
    if not re.search(r'residue|residual|char(?:\s+yield)?|remaining mass',h,re.I):return None
    if re.search(r'(?:at|@)\s*T\s*max\s*3|T3max',h,re.I): return 'residue_at_Tmax3_pct'
    if re.search(r'(?:at|@)\s*T\s*max\s*2|T2max',h,re.I): return 'residue_at_Tmax2_pct'
    if re.search(r'(?:at|@)\s*T\s*max(?:\s*1)?|T1max',h,re.I): return 'residue_at_Tmax_pct'
    for t in [400,500,550,600,650,700,800]:
        if re.search(rf'\b{t}\s*(?:°\s*C|℃|C)?\b',h,re.I): return f'R{t}_pct'
    return None
def tgfield(h):
    r=residue(h)
    if r:return r
    if re.search(r'T\s*onset\s*10\s*%|onset[^%]{0,15}10\s*%',h,re.I): return 'T10_C'
    for k,p in TG_PAT:
        if p.search(h):return k
    return None

class SourceResult(tuple):
    """Three-value source result, with failure details for safe retry decisions."""
    def __new__(cls, text='', tables=None, url='', failures=()):
        result = super().__new__(cls, (text, tables or [], url))
        result.failures = tuple(sorted(set(failures)))
        return result


def pmc(doi_):
    failures = []
    try:
        q=requests.get('https://www.ebi.ac.uk/europepmc/webservices/rest/search',params={'query':f'DOI:"{doi_}"','format':'json','pageSize':5},headers=HEAD,timeout=30)
        q.raise_for_status()
        records=q.json().get('resultList',{}).get('result',[])
    except requests.RequestException:
        return SourceResult(failures=['fetch_error'])
    except (ValueError, TypeError, AttributeError):
        return SourceResult(failures=['parse_error'])
    for it in records:
        if not it.get('pmcid'):continue
        try:
            x=requests.get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{it['pmcid']}/fullTextXML",headers=HEAD,timeout=35)
            x.raise_for_status()
        except requests.RequestException:
            failures.append('fetch_error')
            continue
        try:
            s=BeautifulSoup(x.text,'xml'); text=s.get_text(' ',strip=True); tabs=[]
            for w in s.find_all('table-wrap'):
                ctx=' '.join(z.get_text(' ',strip=True) for z in [w.find('label'),w.find('caption')] if z); t=w.find('table')
                if t:
                    try:
                        df=flat(pd.read_html(io.StringIO(str(t)))[0]); tabs.append((ctx,df))
                    except (ValueError, TypeError, IndexError):
                        failures.append('parse_error')
            if text and tabs:return SourceResult(text,tabs,f"https://europepmc.org/articles/{it['pmcid']}",failures)
        except (ValueError, TypeError, AttributeError):
            failures.append('parse_error')
    return SourceResult(failures=failures)


def html(url):
    if not url or urlparse(url).netloc.lower() not in ALLOWED:
        return SourceResult()
    try:
        r=requests.get(url,headers=HEAD,timeout=35)
        r.raise_for_status()
    except requests.RequestException:
        return SourceResult(url=url,failures=['fetch_error'])
    if 'html' not in r.headers.get('content-type','').lower():
        return SourceResult(url=url,failures=['unsupported_content'])
    failures=[]
    try:
        s=BeautifulSoup(r.text,'lxml'); tabs=[]
        for t in s.find_all('table')[:80]:
            ctx=''; cap=t.find('caption'); prev=t.find_previous(['h2','h3','h4','p'])
            if cap:ctx+=cap.get_text(' ',strip=True)+' '
            if prev:ctx+=prev.get_text(' ',strip=True)[-500:]
            try:tabs.append((ctx,flat(pd.read_html(io.StringIO(str(t)))[0])))
            except (ValueError, TypeError, IndexError):failures.append('parse_error')
        return SourceResult(s.get_text(' ',strip=True),tabs,url,failures)
    except (ValueError, TypeError, AttributeError):
        return SourceResult(url=url,failures=['parse_error'])


def source(row):
    result=pmc(doi(row.get('DOI')))
    if result[0] and result[1]:return result
    failures=list(getattr(result,'failures',()))
    seen=set()
    for c in ['fulltext_url','oa_url','landing_url']:
        u=str(row.get(c,'') or '').strip()
        if not u or u in seen:continue
        seen.add(u)
        candidate=html(u)
        if candidate[0] and candidate[1]:return candidate
        failures.extend(getattr(candidate,'failures',()))
    return SourceResult(result[0],result[1],result[2],failures)

def loi_rows(tables):
    out=[]
    for ctx,df in tables:
        lcols=[c for c in df.columns if re.search(r'\bLOI\b|limiting oxygen index|oxygen index',c,re.I)]
        if not lcols:continue
        sc=sample_col(df,set(lcols))
        if not sc:continue
        current_wash=''
        for _,r in df.iterrows():
            cells=[str(v).strip() for v in r.tolist() if str(v).strip() and str(v).lower()!='nan']
            joined=' '.join(cells)
            marker=wash_state(joined)
            if marker and not any(exact(r.get(c))[0] is not None for c in lcols):
                current_wash=marker
                # A washing group header has no measurement; a numeric sample
                # label mentioning washing remains a real observation.
                probe=str(r.get(sc,'') or '').strip()
                if wash_state(probe):continue
            s=str(r.get(sc,'') or '').strip()
            if not s or s.lower()=='nan':continue
            for lc in lcols:
                v,u=exact(r.get(lc))
                if v is not None and 5<=v<=100:
                    w=wash_state(str(lc)) or wash_state(s) or current_wash or wash_state(ctx)
                    out.append({'sample_state':s,'sample_norm':ns(s),'washing_state':w,'LOI_pct':v,'LOI_uncertainty_pct':u,'ctx':ctx})
    return out
def tg_rows(full,tables):
    out=[]
    for ctx,df in tables:
        signature=(ctx+' '+' '.join(map(str,df.columns)))
        if not re.search(r'thermograv|\bTGA\b|TG/DTG|thermal (?:decomposition|degradation)|residu(?:e|al)|char yield',signature,re.I): continue
        if re.search(r'UL[- ]?94|flame spread|afterflame|afterglow',signature,re.I) and not re.search(r'thermograv|\bTGA\b|TG/DTG',signature,re.I): continue
        cols=[(c,tgfield(c)) for c in df.columns]; cols=[x for x in cols if x[1]]
        if not cols:continue
        sc=sample_col(df,{c for c,_ in cols})
        if not sc:continue
        current_wash=''
        for _,r in df.iterrows():
            cells=[str(v).strip() for v in r.tolist() if str(v).strip() and str(v).lower()!='nan']
            joined=' '.join(cells)
            marker=wash_state(joined)
            if marker and not any(exact(r.get(c))[0] is not None for c,_ in cols):
                current_wash=marker
                probe=str(r.get(sc,'') or '').strip()
                if wash_state(probe):continue
            sample=str(r.get(sc,'') or '').strip()
            if not sample or sample.lower()=='nan':continue
            groups={}
            for c,f in cols:
                v,_=exact(r.get(c))
                if v is None:continue
                if (f.startswith('R') or 'residue' in f.lower()) and not (0<=v<=100):continue
                if f.endswith('_C') and not (20<=v<=1500):continue
                a=infer_atm(full,ctx,c) or ''; groups.setdefault(a,{})[f]=v
            for a,vals in groups.items():
                if vals:
                    w=wash_state(sample) or current_wash or wash_state(ctx)
                    out.append({'sample_state':sample,'sample_norm':ns(sample),'washing_state':w,'atmosphere':a or (infer_atm(full,ctx) or ''),'heating_rate_C_min':infer_rate(full,ctx),'ctx':ctx,**vals})
    return out

RETRY_BASE_HOURS=6
RETRY_MAX_HOURS=7*24
STATE_VERSION=2
# These describe the harvesting run, not the extraction inputs. Everything else
# (including all URLs, abstracts, supplementary evidence, and review fields) is
# fingerprinted so new evidence invalidates an earlier terminal result.
FINGERPRINT_IGNORED={'_score','harvest_cycle','harvest_run','harvested_at_utc','last_seen_utc'}


def utcnow():
    return datetime.now(timezone.utc)


def load_state():
    if not STATE.exists():
        return {'version':STATE_VERSION,'processed':{}}
    try:
        state=json.loads(STATE.read_text())
    except (ValueError, UnicodeError) as exc:
        raise ValueError(f'Invalid extraction state in {STATE}; refusing to reset existing history.') from exc
    # Version-less dictionaries are legitimate legacy state. Broken containers
    # or entries are not: stop before any source fetch or output write rather
    # than replacing the stored history with an empty processed dictionary.
    valid=isinstance(state,dict) and isinstance(state.get('processed'),dict)
    if valid:
        for entry in state['processed'].values():
            if not isinstance(entry,dict):
                valid=False; break
            if ('fingerprint' in entry and not isinstance(entry['fingerprint'],str)
                    or 'grade' in entry and entry['grade'] not in ('A','B','C')
                    or 'retryable' in entry and not isinstance(entry['retryable'],bool)):
                valid=False; break
    if not valid:
        raise ValueError(f'Invalid extraction state structure in {STATE}; refusing to reset existing history.')
    return state


def fp(r):
    values={str(k):str(v or '') for k,v in r.items() if k not in FINGERPRINT_IGNORED}
    review_digest=hashlib.sha256(PAIR_REVIEWS.read_bytes()).hexdigest() if PAIR_REVIEWS.exists() else ''
    payload=json.dumps({'extractor_version':EXTRACTOR_VERSION,'inputs':values,'pair_reviews':review_digest},sort_keys=True,ensure_ascii=False,separators=(',',':'))
    return hashlib.sha256(payload.encode()).hexdigest()[:20]


def retry_due(previous, fingerprint, now):
    if previous.get('fingerprint')!=fingerprint:
        return True
    if previous.get('grade')!='C' and 'retryable' not in previous:
        return False
    # Legacy C entries did not distinguish transient fetch failures. Retry once
    # to classify them instead of carrying a permanent false-negative forward.
    if 'retryable' not in previous:
        return True
    if not previous.get('retryable'):
        return False
    try:
        due=datetime.fromisoformat(previous.get('next_retry_utc',''))
        if due.tzinfo is None:due=due.replace(tzinfo=timezone.utc)
        return now>=due
    except (ValueError, TypeError):
        return True


def attempt_state(previous, fingerprint, grade, reason_code, retryable, now):
    same_input=previous.get('fingerprint')==fingerprint
    try:attempts=int(previous.get('attempt_count',0)) if same_input else 0
    except (TypeError,ValueError):attempts=0
    # Keep state bounded while continuing weekly retries for unavailable sources.
    attempts=min(max(attempts,0)+1,32)
    entry={'fingerprint':fingerprint,'extractor_version':EXTRACTOR_VERSION,
           'grade':grade,'reason_code':reason_code,'retryable':retryable,
           'attempt_count':attempts,'last_attempt_utc':now.isoformat()}
    if retryable:
        delay=min(RETRY_BASE_HOURS * 2**min(attempts-1,5),RETRY_MAX_HOURS)
        entry['next_retry_utc']=(now+timedelta(hours=delay)).isoformat()
    return entry


def write_if_changed(path, content):
    if path.exists() and path.read_text()==content:
        return False
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(content)
    return True

def rate_s(r):
    if r is None:return ''
    try:return str(float(r))
    except:return str(r).strip()
def pairkey(d,s,w,a,r):return f'{d}||{s.strip()}||{str(w or "").strip()}||{a.strip()}||{rate_s(r)}'
def norm_pairkey(d,s,w,a,r):return normalized_pair_key(d,s,w,a,r)
def master_keys():
    if not MASTER.exists():return set(),set()
    try:d=pd.read_csv(MASTER,dtype=str).fillna('')
    except:return set(),set()
    raw=set(d['pair_key']) if 'pair_key' in d else set()
    norm=set()
    for _,r in d.iterrows():
        norm.add(norm_pairkey(doi(r.get('DOI','')),r.get('sample_state',''),r.get('washing_state',''),r.get('atmosphere',''),r.get('heating_rate_C_min','')))
    return raw,norm
def material_labels(title,full):
    tx=str(title or '').lower()
    bx=str(full or '')[:5000].lower()
    x=tx+' '+bx
    if re.search(r'nylon\s*[/–-]\s*cotton|cotton\s*[/–-]\s*nylon|nyco',x): mat='nylon/cotton blend'
    elif 'cotton' in tx or ('cotton' in bx and re.search(r'fabric|textile|fiber|fibre|yarn',bx)): mat='cotton'
    elif re.search(r'polyester|\bpet\b',x): mat='polyester'
    elif re.search(r'polyamide|\bpa6\b|\bpa66\b|nylon',x): mat='polyamide/nylon'
    elif 'lyocell' in x: mat='lyocell'
    elif 'viscose' in x: mat='viscose'
    elif 'wool' in x: mat='wool'
    elif 'silk' in x: mat='silk'
    elif 'aramid' in x or 'kevlar' in x or 'nomex' in x: mat='aramid'
    elif re.search(r'polypropylene|\bpp\b',x): mat='polypropylene'
    elif re.search(r'polyacrylonitrile|\bpan\b',x): mat='polyacrylonitrile'
    else: mat=''
    # Material form must be explicit in the title for synthetic polymers; body-only generic mentions are insufficient.
    if 'nonwoven' in tx: form='nonwoven'
    elif 'knitted' in tx or re.search(r'\bknit\b',tx): form='knitted fabric'
    elif 'woven' in tx: form='woven fabric'
    elif 'fabric' in tx or 'textile' in tx: form='fabric'
    elif 'fibre' in tx or 'fiber' in tx: form='fiber'
    elif 'yarn' in tx: form='yarn'
    elif ('cotton' in tx or 'lyocell' in tx or 'viscose' in tx or 'wool' in tx or 'silk' in tx or 'aramid' in tx) and re.search(r'fabric|textile|fiber|fibre|yarn',bx): form='fabric'
    else: form=''
    return mat,form
def merge(path, new, keys=None):
    """Append distinct extraction evidence; never replace old audit history."""
    try:old=pd.read_csv(path,dtype=str).fillna('') if path.exists() else pd.DataFrame()
    except pd.errors.EmptyDataError:old=pd.DataFrame()
    new=new.fillna('').astype(str)
    both=pd.concat([old,new],ignore_index=True,sort=False).fillna('')
    if keys is None:
        # A cooldown retry of unchanged evidence updates state, not the evidence
        # timestamp. Different values, versions or input fingerprints append.
        keys=[c for c in both if c!='extracted_at_utc']
        seen={tuple(row) for row in both.iloc[:len(old)][keys].itertuples(index=False,name=None)}
        keep=list(range(len(old)))
        for idx,row in enumerate(both.iloc[len(old):][keys].itertuples(index=False,name=None),len(old)):
            if row not in seen:
                seen.add(row); keep.append(idx)
        both=both.iloc[keep].reset_index(drop=True)
    elif not both.empty:
        for k in keys:
            if k not in both:both[k]=''
        both=both.drop_duplicates(subset=keys,keep='last')
    write_if_changed(path,both.to_csv(index=False))
    return both


def source_url(candidate, resolved=''):
    return resolved or next((str(candidate.get(c,'') or '').strip() for c in
                            ('fulltext_url','oa_url','landing_url')
                            if str(candidate.get(c,'') or '').strip()),'')


def c_record(candidate, fingerprint, now, reason_code, reason, url=''):
    return {'DOI':doi(candidate.get('DOI')),'title':candidate.get('title',''),
            'year':candidate.get('year',''),'journal':candidate.get('journal',''),
            'grade':'C','reason_code':reason_code,'reason':reason,
            'source_url':source_url(candidate,url),'candidate_fingerprint':fingerprint,
            'extractor_version':EXTRACTOR_VERSION,'extracted_at_utc':now.isoformat()}


def main():
    if not CAND.exists():print('No candidate queue.');return
    cands=pd.read_csv(CAND,dtype=str).fillna('')
    cands['_score']=pd.to_numeric(cands.get('candidate_score',pd.Series(0,index=cands.index)),errors='coerce').fillna(0)
    cands=cands.sort_values('_score',ascending=False,kind='stable')
    st=load_state(); st.setdefault('processed',{})
    mk,mnk=master_keys(); extracted=[]; promoted=[]; examined=0
    limit=max(0,int(os.getenv('AUTO_MAX_CANDIDATES','25')))
    now=utcnow()
    for _,c in cands.iterrows():
        if examined>=limit:break
        d=doi(c.get('DOI')); f=fp(c); previous=st['processed'].get(d,{})
        if not d or not retry_due(previous,f,now):continue
        examined+=1
        try:
            result=source(c)
            full,tabs,url=result
            failures=getattr(result,'failures',())
        except requests.RequestException:
            full,tabs,url,failures='',[],'',('fetch_error',)
        except (ValueError,TypeError,AttributeError):
            full,tabs,url,failures='',[],'',('parse_error',)
        mat,form=material_labels(c.get('title',''),full)
        if not full or not tabs:
            code='parse_error' if 'parse_error' in failures else ('fetch_error' if 'fetch_error' in failures else 'source_unavailable')
            extracted.append(c_record(c,f,now,code,'No structured open-full-text tables could be parsed; retry after cooldown.',url))
            st['processed'][d]=attempt_state(previous,f,'C',code,True,now)
            continue
        try:
            L=loi_rows(tabs); T=tg_rows(full,tabs)
        except (ValueError,TypeError,KeyError,IndexError):
            extracted.append(c_record(c,f,now,'parse_error','Structured table interpretation failed; retry after cooldown.',url))
            st['processed'][d]=attempt_state(previous,f,'C','parse_error',True,now)
            continue
        anypair=False; grades=[]
        for l in L:
            matches=[x for x in T if x['sample_norm'] and x['sample_norm']==l['sample_norm']
                     and normalize_label(x.get('washing_state',''))==normalize_label(l.get('washing_state',''))]
            for t in matches:
                anypair=True
                a=str(t.get('atmosphere','') or '').strip(); r=t.get('heating_rate_C_min')
                nums={k:v for k,v in t.items() if (k.endswith('_C') or k.startswith('R') or k.startswith('residue_')) and isinstance(v,(int,float))}
                nontext=bool(re.search(r'plaque|film|resin|composite|paper',str(l.get('ctx',''))+' '+str(t.get('ctx','')),re.I))
                rec={'DOI':d,'title':c.get('title',''),'year':c.get('year',''),'journal':c.get('journal',''),
                     'sample_state':l['sample_state'],'sample_norm':l['sample_norm'],'washing_state':l.get('washing_state',''),
                     'LOI_pct':l['LOI_pct'],'LOI_uncertainty_pct':l.get('LOI_uncertainty_pct'),
                     'atmosphere':a,'heating_rate_C_min':r,**nums,
                     'source_url':source_url(c,url),'source_location':f"LOI table: {l['ctx']}; TG table: {t['ctx']}",
                     'evidence':'Structured table values with matching labels; matching labels alone do not verify identical specimen form or treatment state.',
                     'numeric_evidence_type':'tabulated','candidate_fingerprint':f,
                     'extractor_version':EXTRACTOR_VERSION,'extracted_at_utc':now.isoformat()}
                rec['pair_key']=pairkey(d,rec['sample_state'],rec.get('washing_state',''),a,r)
                # Only source-bound human review may attest same-state scientific
                # equivalence; title words and matching labels cannot do so.
                rec.update(reviewed_metadata(rec))
                issues=evidence_issues(rec)
                reviewed_form=normalize_label(rec.get('material_form_TGA',''))
                textile_review=bool(re.search(r'\b(?:fabric|textile|fibers?|fibres?|yarn|nonwoven)\b',reviewed_form))
                complete=bool(a and r is not None and nums and mat and form and not nontext and textile_review)
                g='A' if complete and not issues else 'B'
                rec.update({'grade':g,'direct_numeric_use':'TG+LOI' if g=='A' else 'review',
                            'reason_code':'verified_pair' if g=='A' else 'pair_requires_review',
                            'reason':'Reviewed exact same-state pairing; exact LOI; tabulated TG numbers; complete TGA conditions.' if g=='A'
                            else 'Numeric label pairing requires review: '+('; '.join(issues) if issues else 'TGA condition or textile-form criterion is ambiguous/missing.')})
                grades.append(g); extracted.append(rec)
                normkey=norm_pairkey(d,rec['sample_state'],rec.get('washing_state',''),a,r)
                if g=='A' and rec['pair_key'] not in mk and normkey not in mnk:
                    promoted.append({**rec,
                        'batch_id':'AUTO-'+now.strftime('%Y%m%d'),'dataset_type':'literature',
                        'material_category':mat,'material_form':form,
                        'LOI_state':rec.get('washing_state','') or 'as prepared',
                        'source_title':c.get('title',''),
                        'limitations':'Promoted with source-bound reviewed same-state evidence and complete TGA conditions; labels alone were not sufficient.'})
                    mk.add(rec['pair_key']); mnk.add(normkey)
        if not anypair:
            # A partially parsed source cannot establish the absence of a pair.
            code='parse_error' if failures else 'no_exact_pair'
            reason=('Some source tables could not be parsed; no exact pair established; retry after cooldown.'
                    if failures else 'Structured LOI/TG tables found, but no exact sample-state match was established.')
            extracted.append(c_record(c,f,now,code,reason,url)); grades=['C']
        else:
            code='partial_source_failure' if failures else ('verified_pair' if 'A' in grades else 'pair_requires_review')
        grade='A' if 'A' in grades else ('B' if 'B' in grades else 'C')
        st['processed'][d]=attempt_state(previous,f,grade,code,bool(failures),now)
    # A no-op scheduled run must not create a timestamp-only commit.
    if examined:
        st.update({'version':STATE_VERSION,'last_run_utc':now.isoformat(),'last_examined_candidates':examined})
        write_if_changed(STATE,json.dumps(st,ensure_ascii=False,indent=2)+'\n')
    allx=merge(EXT,pd.DataFrame(extracted)) if extracted else (pd.read_csv(EXT,dtype=str).fillna('') if EXT.exists() else pd.DataFrame())
    if not allx.empty:
        write_if_changed(REVIEW,allx[allx['grade']!='A'].to_csv(index=False))
    if promoted:
        out=INC/f"verified_auto_{now.strftime('%Y%m%d')}.csv"
        merged=merge(out,pd.DataFrame(promoted),['DOI','sample_state','washing_state','atmosphere','heating_rate_C_min'])
        print(f'Promoted {len(promoted)} Grade-A rows into {out.relative_to(ROOT)}; file rows={len(merged)}')
    print(f'Examined={examined}; extraction_rows={len(extracted)}; promoted={len(promoted)}')


if __name__=='__main__':main()
