#!/usr/bin/env python3
from __future__ import annotations
import hashlib, io, json, os, re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
import pandas as pd, requests
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'; AUTO=DATA/'automation'; INC=DATA/'incoming'
CAND=AUTO/'candidate_extractions.csv'; EXT=AUTO/'auto_extracted.csv'; REVIEW=AUTO/'review_queue.csv'; STATE=AUTO/'auto_extract_state.json'; MASTER=DATA/'tg_loi_master.csv'
AUTO.mkdir(parents=True,exist_ok=True); INC.mkdir(parents=True,exist_ok=True)
HEAD={'User-Agent':'textile-tga-database/1.1 (public academic data curation; GitHub PolyFT/textile-tga-database)'}
ALLOWED={'pmc.ncbi.nlm.nih.gov','europepmc.org','www.europepmc.org','www.mdpi.com','mdpi.com','pubs.rsc.org','www.frontiersin.org','link.springer.com','journals.sagepub.com','www.hindawi.com','onlinelibrary.wiley.com'}
NUM=re.compile(r'[-+]?\d+(?:\.\d+)?'); RANGE=re.compile(r'\d+(?:\.\d+)?\s*(?:-|–|—|to)\s*\d+(?:\.\d+)?',re.I); UNC=re.compile(r'(\d+(?:\.\d+)?)\s*(?:±|\+/-)\s*(\d+(?:\.\d+)?)')
RATE1=re.compile(r'(?:heating\s*rate|heated[^.;\n]{0,80}?at|heating\s+at|rate\s+of)[^.;\n]{0,80}?(\d+(?:\.\d+)?)\s*(?:°\s*C|℃|K)\s*(?:/|per)\s*min(?:ute)?',re.I)
RATE2=re.compile(r'(\d+(?:\.\d+)?)\s*(?:°\s*C|℃|K)\s*(?:/|per)\s*min(?:ute)?',re.I)
ATM=[('N2',re.compile(r'\b(?:nitrogen|N\s*2|N₂)\b',re.I)),('air',re.compile(r'\b(?:air|oxidative atmosphere)\b',re.I)),('O2',re.compile(r'\b(?:oxygen|O\s*2|O₂)\b',re.I)),('argon',re.compile(r'\b(?:argon|Ar)\b',re.I))]
TG_PAT=[('T1_C',r'\bT\s*1\b|1\s*%.*loss'),('T5_C',r'\bT\s*5\b|5\s*%.*loss|T\s*d\s*,?\s*5'),('T10_C',r'\bT\s*10\b|10\s*%.*loss|T\s*d\s*,?\s*10'),('T20_C',r'\bT\s*20\b|20\s*%.*loss'),('T40_C',r'\bT\s*40\b|40\s*%.*loss'),('T50_C',r'\bT\s*50\b|50\s*%.*loss'),('Tonset_C',r'T\s*onset|onset\s*(?:temperature)?|initial decomposition temperature'),('Tmax2_C',r'T\s*max\s*2|second.*peak'),('Tmax3_C',r'T\s*max\s*3|third.*peak'),('Tmax1_C',r'T\s*max(?:\s*1)?|T\s*dmax|peak\s*(?:decomposition\s*)?temperature')]
TG_PAT=[(k,re.compile(p,re.I)) for k,p in TG_PAT]

def doi(v):
    x=str(v or '').strip().lower(); x=re.sub(r'^https?://(?:dx\.)?doi\.org/','',x); return re.sub(r'^doi:\s*','',x).rstrip(' .;,')
def ns(v):
    x=str(v or '').replace('₂','2').strip().lower(); x=re.sub(r'\s+',' ',x); return re.sub(r'[^a-z0-9.%+()/-]+','',x)
def exact(v):
    s=str(v or '').strip()
    if not s or RANGE.search(s) or re.search(r'[<>~≈]',s): return None,None
    m=UNC.search(s)
    if m:return float(m.group(1)),float(m.group(2))
    a=NUM.findall(s); return (float(a[0]),None) if len(a)==1 else (None,None)
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
    out=[]
    for m in re.finditer(r'\b(?:TGA|TG/DTG|thermogravimetric|thermogravimetry)\b',text,re.I): out.append(text[max(0,m.start()-500):m.end()+500])
    return ' '.join(out[:12])
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
    for t in [400,500,550,600,650,700,800]:
        if re.search(rf'\b{t}\s*(?:°\s*C|℃|C)?\b',h,re.I): return f'R{t}_pct'
    return None
def tgfield(h):
    r=residue(h)
    if r:return r
    for k,p in TG_PAT:
        if p.search(h):return k
    return None

def pmc(doi_):
    try:
        q=requests.get('https://www.ebi.ac.uk/europepmc/webservices/rest/search',params={'query':f'DOI:"{doi_}"','format':'json','pageSize':5},headers=HEAD,timeout=30); q.raise_for_status()
        for it in q.json().get('resultList',{}).get('result',[]):
            if not it.get('pmcid'):continue
            x=requests.get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{it['pmcid']}/fullTextXML",headers=HEAD,timeout=35)
            if not x.ok:continue
            s=BeautifulSoup(x.text,'xml'); text=s.get_text(' ',strip=True); tabs=[]
            for w in s.find_all('table-wrap'):
                ctx=' '.join(z.get_text(' ',strip=True) for z in [w.find('label'),w.find('caption')] if z); t=w.find('table')
                if t:
                    try:
                        df=flat(pd.read_html(io.StringIO(str(t)))[0]); tabs.append((ctx,df))
                    except Exception:pass
            if text and tabs:return text,tabs,f"https://europepmc.org/articles/{it['pmcid']}"
    except Exception:pass
    return '',[],''
def html(url):
    try:
        if not url or urlparse(url).netloc.lower() not in ALLOWED:return '',[]
        r=requests.get(url,headers=HEAD,timeout=35)
        if not r.ok or 'html' not in r.headers.get('content-type','').lower():return '',[]
        s=BeautifulSoup(r.text,'lxml'); tabs=[]
        for t in s.find_all('table')[:80]:
            ctx=''; cap=t.find('caption'); prev=t.find_previous(['h2','h3','h4','p'])
            if cap:ctx+=cap.get_text(' ',strip=True)+' '
            if prev:ctx+=prev.get_text(' ',strip=True)[-500:]
            try:tabs.append((ctx,flat(pd.read_html(io.StringIO(str(t)))[0])))
            except Exception:pass
        return s.get_text(' ',strip=True),tabs
    except Exception:return '',[]
def source(row):
    d=doi(row.get('DOI')); text,tabs,url=pmc(d)
    if text and tabs:return text,tabs,url
    for c in ['fulltext_url','oa_url','landing_url']:
        u=str(row.get(c,'') or '').strip(); t,ts=html(u)
        if t and ts:return t,ts,u
    return text,tabs,url

def loi_rows(tables):
    out=[]
    for ctx,df in tables:
        lcols=[c for c in df.columns if re.search(r'\bLOI\b|limiting oxygen index|oxygen index',c,re.I)]
        if not lcols:continue
        sc=sample_col(df,set(lcols))
        if not sc:continue
        for _,r in df.iterrows():
            s=str(r.get(sc,'') or '').strip()
            if not s or s.lower()=='nan':continue
            for lc in lcols:
                v,u=exact(r.get(lc))
                if v is not None and 5<=v<=100:out.append({'sample_state':s,'sample_norm':ns(s),'LOI_pct':v,'LOI_uncertainty_pct':u,'ctx':ctx})
    return out
def tg_rows(full,tables):
    out=[]
    for ctx,df in tables:
        cols=[(c,tgfield(c)) for c in df.columns]; cols=[x for x in cols if x[1]]
        if not cols:continue
        sc=sample_col(df,{c for c,_ in cols})
        if not sc:continue
        for _,r in df.iterrows():
            s=str(r.get(sc,'') or '').strip()
            if not s or s.lower()=='nan':continue
            groups={}
            for c,f in cols:
                v,_=exact(r.get(c))
                if v is None:continue
                if f.startswith('R') and not (0<=v<=100):continue
                if f.endswith('_C') and not (20<=v<=1500):continue
                a=infer_atm(full,ctx,c) or ''; groups.setdefault(a,{})[f]=v
            for a,vals in groups.items():
                if vals:out.append({'sample_state':s,'sample_norm':ns(s),'atmosphere':a or (infer_atm(full,ctx) or ''),'heating_rate_C_min':infer_rate(full,ctx),'ctx':ctx,**vals})
    return out

def load_state():
    try:return json.loads(STATE.read_text()) if STATE.exists() else {'version':1,'processed':{}}
    except:return {'version':1,'processed':{}}
def fp(r):
    cols=['DOI','fulltext_url','candidate_score','status','LOI_numeric_evidence','TG_numeric_evidence','table_candidates','supplementary_links']; return hashlib.sha256('|'.join(str(r.get(c,'') or '') for c in cols).encode()).hexdigest()[:20]
def rate_s(r):
    if r is None:return ''
    try:return str(float(r))
    except:return str(r).strip()
def pairkey(d,s,a,r):return f'{d}||{s.strip()}||{a.strip()}||{rate_s(r)}'
def norm_pairkey(d,s,a,r):return f'{d}||{ns(s)}||{str(a).strip().lower()}||{rate_s(r)}'
def master_keys():
    if not MASTER.exists():return set(),set()
    try:d=pd.read_csv(MASTER,dtype=str).fillna('')
    except:return set(),set()
    raw=set(d['pair_key']) if 'pair_key' in d else set()
    norm=set()
    for _,r in d.iterrows():
        norm.add(norm_pairkey(doi(r.get('DOI','')),r.get('sample_state',''),r.get('atmosphere',''),r.get('heating_rate_C_min','')))
    return raw,norm
def material_labels(title,full):
    x=(str(title)+' '+str(full)[:3000]).lower()
    if re.search(r'nylon\s*[/–-]\s*cotton|cotton\s*[/–-]\s*nylon|nyco',x): mat='nylon/cotton blend'
    elif 'cotton' in x: mat='cotton'
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
    if 'nonwoven' in x: form='nonwoven'
    elif 'knitted' in x or 'knit' in x: form='knitted fabric'
    elif 'woven' in x: form='woven fabric'
    elif 'fabric' in x or 'textile' in x: form='fabric'
    elif 'fibre' in x or 'fiber' in x: form='fiber'
    elif 'yarn' in x: form='yarn'
    else: form=''
    return mat,form
def merge(path,new,keys):
    try:old=pd.read_csv(path,dtype=str) if path.exists() else pd.DataFrame()
    except:old=pd.DataFrame()
    both=pd.concat([old,new],ignore_index=True,sort=False) if not old.empty else new.copy()
    for k in keys:
        if k not in both:both[k]=''
    if not both.empty:both=both.drop_duplicates(subset=keys,keep='last')
    both.to_csv(path,index=False); return both

def main():
    if not CAND.exists():print('No candidate queue.');return
    cands=pd.read_csv(CAND,dtype=str).fillna(''); cands['_score']=pd.to_numeric(cands.get('candidate_score',0),errors='coerce').fillna(0); cands=cands.sort_values('_score',ascending=False)
    st=load_state(); st.setdefault('processed',{}); mk,mnk=master_keys(); extracted=[]; promoted=[]; examined=0; limit=int(os.getenv('AUTO_MAX_CANDIDATES','25'))
    for _,c in cands.iterrows():
        if examined>=limit: break
        d=doi(c.get('DOI')); f=fp(c)
        if not d or st['processed'].get(d,{}).get('fingerprint')==f:continue
        examined+=1; full,tabs,url=source(c); mat,form=material_labels(c.get('title',''),full)
        if not full or not tabs:
            extracted.append({'DOI':d,'title':c.get('title',''),'year':c.get('year',''),'journal':c.get('journal',''),'grade':'C','reason':'No structured open-full-text tables could be parsed.','source_url':url or c.get('fulltext_url','') or c.get('oa_url',''),'candidate_fingerprint':f,'extracted_at_utc':datetime.now(timezone.utc).isoformat()}); st['processed'][d]={'fingerprint':f,'grade':'C'};continue
        L=loi_rows(tabs); T=tg_rows(full,tabs); anypair=False; grades=[]
        for l in L:
            for t in [x for x in T if x['sample_norm'] and x['sample_norm']==l['sample_norm']]:
                anypair=True; a=str(t.get('atmosphere','') or '').strip(); r=t.get('heating_rate_C_min'); nums={k:v for k,v in t.items() if (k.endswith('_C') or k.startswith('R')) and isinstance(v,(int,float))}; g='A' if a and r is not None and nums else 'B'; grades.append(g)
                rec={'DOI':d,'title':c.get('title',''),'year':c.get('year',''),'journal':c.get('journal',''),'sample_state':l['sample_state'],'sample_norm':l['sample_norm'],'LOI_pct':l['LOI_pct'],'LOI_uncertainty_pct':l.get('LOI_uncertainty_pct'),'atmosphere':a,'heating_rate_C_min':r,**nums,'grade':g,'reason':'Exact normalized sample-state match; exact LOI; structured TG numeric fields; complete TGA conditions.' if g=='A' else 'Exact numeric pairing found, but TGA atmosphere or heating rate is ambiguous/missing.','source_url':url or c.get('fulltext_url','') or c.get('oa_url',''),'source_location':f"LOI table: {l['ctx']}; TG table: {t['ctx']}",'evidence':'Automatically extracted from structured open-full-text tables; sample states matched exactly after conservative normalization.','direct_numeric_use':'TG+LOI' if g=='A' else 'review','candidate_fingerprint':f,'extracted_at_utc':datetime.now(timezone.utc).isoformat()}; rec['pair_key']=pairkey(d,rec['sample_state'],a,r); extracted.append(rec)
                if g=='A' and rec['pair_key'] not in mk and norm_pairkey(d,rec['sample_state'],a,r) not in mnk:
                    promoted.append({'batch_id':'AUTO-'+datetime.now(timezone.utc).strftime('%Y%m%d'),'dataset_type':'literature','material_category':mat,'material_form':form,'sample_state':rec['sample_state'],'atmosphere':a,'heating_rate_C_min':r,'LOI_pct':rec['LOI_pct'],'LOI_uncertainty_pct':rec.get('LOI_uncertainty_pct'),**nums,'direct_numeric_use':'TG+LOI','evidence':rec['evidence'],'source_title':c.get('title',''),'year':c.get('year',''),'journal':c.get('journal',''),'DOI':d,'source_url':rec['source_url'],'source_location':rec['source_location'],'limitations':'Automatically promoted only because exact table-level sample matching and complete TGA conditions satisfied conservative Grade-A rules.'}); mk.add(rec['pair_key']); mnk.add(norm_pairkey(d,rec['sample_state'],a,r))
        if not anypair:
            extracted.append({'DOI':d,'title':c.get('title',''),'year':c.get('year',''),'journal':c.get('journal',''),'grade':'C','reason':'Structured LOI/TG tables found, but no exact sample-state match was established.','source_url':url or c.get('fulltext_url','') or c.get('oa_url',''),'candidate_fingerprint':f,'extracted_at_utc':datetime.now(timezone.utc).isoformat()}); grades=['C']
        st['processed'][d]={'fingerprint':f,'grade':'A' if 'A' in grades else ('B' if 'B' in grades else 'C')}
    st['last_run_utc']=datetime.now(timezone.utc).isoformat(); st['last_examined_candidates']=examined; STATE.write_text(json.dumps(st,ensure_ascii=False,indent=2))
    allx=merge(EXT,pd.DataFrame(extracted),['DOI','sample_state','atmosphere','heating_rate_C_min','grade','reason']) if extracted else (pd.read_csv(EXT,dtype=str) if EXT.exists() else pd.DataFrame())
    if not allx.empty: allx[allx.get('grade','')!='A'].to_csv(REVIEW,index=False)
    elif not REVIEW.exists(): pd.DataFrame().to_csv(REVIEW,index=False)
    if promoted:
        out=INC/f"verified_auto_{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv"; merged=merge(out,pd.DataFrame(promoted),['DOI','sample_state','atmosphere','heating_rate_C_min']); print(f'Promoted {len(promoted)} Grade-A rows into {out.relative_to(ROOT)}; file rows={len(merged)}')
    print(f'Examined={examined}; extraction_rows={len(extracted)}; promoted={len(promoted)}')
if __name__=='__main__':main()
