#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, math, os, re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse
import pandas as pd, requests
from bs4 import BeautifulSoup
try:
    from pairing import (evidence_issues, normalize_doi, normalize_label,
                         normalized_atmosphere, normalized_pair_key,
                         normalized_rate, reviewed_metadata, pair_key, source_group_key, is_network_doi, registry_digest)
except ModuleNotFoundError as exc:
    if exc.name!='pairing':
        raise
    from scripts.pairing import (evidence_issues, normalize_doi, normalize_label,
                                 normalized_atmosphere, normalized_pair_key,
                                 normalized_rate, reviewed_metadata, pair_key, source_group_key, is_network_doi, registry_digest)

ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'; AUTO=DATA/'automation'; INC=DATA/'incoming'
REVIEW=AUTO/'review_queue.csv'; MASTER=DATA/'tg_loi_master.csv'
STATE=AUTO/'b_review_state.json'
REVIEWS=DATA/'curation'/'pair_reviews.csv'
PARSER_VERSION='2'
STATE_VERSION=1
FETCH_RETRY=timedelta(hours=6)
REVIEW_RETRY=timedelta(hours=24)
HEAD={'User-Agent':'textile-tga-database/1.2 (public academic data curation; GitHub PolyFT/textile-tga-database)'}
# Match both slash units and the common C min−1 / K·min⁻¹ notation.
_RATE_UNIT=r"(?:°\s*C|℃|K)\s*(?:(?:/|per)\s*min(?:ute)?s?\b|[·⋅]?\s*min(?:ute)?s?\s*(?:\^?\s*[-−–]\s*1|⁻¹))"
RATE=re.compile(r'(\d+(?:\.\d+)?)\s*'+_RATE_UNIT,re.I)
RATE_BARE=re.compile(r'(?:heating\s*rates?|rate\s+of)[^0-9.;\n]{0,40}(\d+(?:\.\d+)?)',re.I)
RATE_CTX=re.compile(r'(?:heating\s*rates?|heated[^.;\n]{0,100}?at|rate\s+of)[^.;\n]{0,100}?(\d+(?:\.\d+)?)\s*'+_RATE_UNIT,re.I)
RATE_LIST=re.compile(r'\d+(?:\.\d+)?\s*(?:,|and|or|to|[-–—])\s*\d+(?:\.\d+)?\s*'+_RATE_UNIT,re.I)
ATM=[('N2',re.compile(r'\b(?:nitrogen|N\s*2|N₂)\b',re.I)),('air',re.compile(r'\b(?:air|oxidative atmosphere)\b',re.I)),('argon',re.compile(r'\b(?:argon|Ar)\b',re.I)),('O2',re.compile(r'\b(?:oxygen|O\s*2|O₂)\b',re.I))]
TG_COLS=['T1_C','T5_C','T10_C','T20_C','T40_C','T50_C','Tonset_C','Tmax1_C','Tmax2_C','Tmax3_C','R400_pct','R500_pct','R550_pct','R600_pct','R650_pct','R700_pct','R800_pct','residue_pct','residue_at_Tmax_pct','residue_at_Tmax1_pct','residue_at_Tmax2_pct','residue_at_Tmax3_pct']

def doi(v):
    return normalize_doi(v)


def ns(v):
    return normalize_label(v)


def rate_s(v):
    return normalized_rate(v)


def norm_key(d,s,w,a,r):
    return normalized_pair_key(d,s,w,a,r)


def get_text(d, source_url=''):
    if not is_network_doi(d):
        return '', ''
    # Prefer Europe PMC XML by DOI for stable article text.
    try:
        q=requests.get('https://www.ebi.ac.uk/europepmc/webservices/rest/search',
            params={'query':f'DOI:"{d}"','format':'json','pageSize':5},headers=HEAD,timeout=25)
        q.raise_for_status()
        for it in q.json().get('resultList',{}).get('result',[]):
            pmcid=it.get('pmcid')
            if not pmcid: continue
            x=requests.get(f'https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML',headers=HEAD,timeout=30)
            if x.ok:
                s=BeautifulSoup(x.text,'xml')
                return s.get_text(' ',strip=True), f'https://europepmc.org/articles/{pmcid}'
    except Exception: pass
    try:
        u=str(source_url or '').strip()
        if u and urlparse(u).netloc.lower() in {'pmc.ncbi.nlm.nih.gov','europepmc.org','www.europepmc.org','www.mdpi.com','mdpi.com','pubs.rsc.org','www.frontiersin.org','link.springer.com','journals.sagepub.com'}:
            r=requests.get(u,headers=HEAD,timeout=30)
            if r.ok and 'html' in r.headers.get('content-type','').lower():
                return BeautifulSoup(r.text,'lxml').get_text(' ',strip=True),u
    except Exception: pass
    # Final fallback: resolve DOI to the publisher OA page and parse the redirected HTML.
    try:
        r=requests.get(f'https://doi.org/{d}',headers=HEAD,timeout=35,allow_redirects=True)
        final_host=urlparse(r.url).netloc.lower()
        allowed={'pubs.rsc.org','www.mdpi.com','mdpi.com','www.frontiersin.org','link.springer.com','journals.sagepub.com','onlinelibrary.wiley.com','pmc.ncbi.nlm.nih.gov'}
        if r.ok and final_host in allowed and 'html' in r.headers.get('content-type','').lower():
            return BeautifulSoup(r.text,'lxml').get_text(' ',strip=True),r.url
    except Exception: pass
    return '',''

def tg_windows(text):
    out=[]
    boundary=re.compile(r'\b(?:differential scanning calorimetry|DSC|X[- ]?ray|XRD|Fourier transform|FTIR|scanning electron|SEM|limiting oxygen|LOI|vertical burning|cone calorim|microscale combustion|MCC)\b',re.I)
    for m in re.finditer(r'\b(?:TGA|TG/DTG|thermogravimetric(?: analysis)?|thermogravimetry)\b',text,re.I):
        z=text[m.start():min(len(text),m.end()+900)]
        bm=boundary.search(z, m.end()-m.start())
        if bm:
            z=z[:bm.start()]
        score=0
        if re.search(r'heating\s*rate|°\s*C|℃|K\s*(?:/|per|[·⋅]?\s*min)',z,re.I): score+=4
        if re.search(r'nitrogen|\bair\b|argon|oxygen',z,re.I): score+=2
        if re.search(r'flow\s*rate|mL\s*/\s*min|from\s+\d+\s*(?:°C|℃).*to\s+\d+',z,re.I): score+=2
        if re.search(r'instrument|analy[sz]er|NETZSCH|TA Instruments|Mettler|PerkinElmer|Shimadzu',z,re.I): score+=2
        if re.search(r'MCC|microscale combustion|UL[- ]?94|vertical burning',z,re.I): score-=4
        out.append((score,z))
    return sorted(out,key=lambda x:x[0],reverse=True)

def infer_rate(text):
    # All eligible TGA windows must agree. Never choose the first of multiple
    # heating programs or turn a list/range into its last numeric value.
    candidates=[]
    values=set()
    ambiguous=False
    for score,z in tg_windows(text):
        if score<4: continue
        vals={float(x) for x in RATE.findall(z)}
        if not vals: continue  # Unitless numbers are diagnostics, not a rate.
        candidates.append(z)
        ambiguous=ambiguous or bool(RATE_LIST.search(z))
        values.update(vals)
    context=' | '.join(dict.fromkeys(candidates))
    if not ambiguous and len(values)==1:
        value=next(iter(values))
        if math.isfinite(value) and 0<value<=1000:
            return value,context
    return None,context

def atmos(s):
    return list(dict.fromkeys(n for n,p in ATM if p.search(str(s or ''))))

def infer_atm(row,text,method_window):
    existing=str(row.get('atmosphere','') or '').strip()
    if existing:
        a=atmos(existing)
        return (a[0],'existing table/context atmosphere') if len(a)==1 else ('','')
    loc=str(row.get('source_location','') or '')
    # LOI testing mentions oxygen/air by definition; only the TG caption may
    # supply a TGA atmosphere when separate table provenance is present.
    marker=re.search(r'\b(?:TG|TGA)\s+table\s*:',loc,re.I)
    if marker:
        loc=loc[marker.end():]
    a=atmos(loc)
    if len(a)==1:return a[0],'source_location'
    a=atmos(method_window)
    if len(a)==1:return a[0],'TGA method window'
    # If full article has one atmosphere uniquely associated with all TGA method windows.
    aa=[]
    for score,z in tg_windows(text)[:5]:
        if score>=4: aa.extend(atmos(z))
    u=list(dict.fromkeys(aa))
    if len(u)==1:return u[0],'TGA method windows'
    return '',''

def valid_textile(row):
    title=str(row.get('title','') or '')
    loc=str(row.get('source_location','') or '')
    tx=title.lower(); probe=(title+' '+loc).lower()
    if re.search(r'\b(plaque|film|resin|paper)\b',loc,re.I): return False
    if re.search(r'polyester|\bpet\b|polyamide|\bpa6\b|\bpa66\b|nylon|polypropylene|\bpp\b',probe,re.I):
        return bool(re.search(r'fabric|textile|fiber|fibre|yarn|woven|knit|nonwoven',tx+' '+loc.lower(),re.I))
    return bool(re.search(r'fabric|textile|fiber|fibre|yarn|woven|knit|nonwoven|cotton|lyocell|viscose|wool|silk|aramid',probe,re.I))

def material_labels(title,text=''):
    tx=str(title or '').lower()
    bx=str(text or '')[:5000].lower()
    x=tx+' '+bx
    if re.search(r'nylon\s*[/–-]\s*cotton|cotton\s*[/–-]\s*nylon|nyco',x): mat='nylon/cotton blend'
    elif 'cotton' in tx or ('cotton' in bx and re.search(r'fabric|textile|fiber|fibre|yarn',bx)): mat='cotton'
    elif re.search(r'polyester|\bpet\b',x): mat='polyester'
    elif re.search(r'polyamide|\bpa6\b|\bpa66\b|nylon',x): mat='polyamide/nylon'
    elif 'lyocell' in x: mat='lyocell'
    elif 'viscose' in x: mat='viscose'
    elif 'wool' in x: mat='wool'
    elif 'silk' in x: mat='silk'
    elif re.search(r'aramid|kevlar|nomex',x): mat='aramid'
    elif re.search(r'polypropylene|\bpp\b',x): mat='polypropylene'
    elif re.search(r'polyacrylonitrile|\bpan\b',x): mat='polyacrylonitrile'
    else: mat=''
    if 'nonwoven' in tx: form='nonwoven'
    elif re.search(r'knitted|\bknit\b',tx): form='knitted fabric'
    elif 'woven' in tx: form='woven fabric'
    elif re.search(r'fabric|textile',tx): form='fabric'
    elif re.search(r'fibres|fibers|fibre|fiber',tx): form='fiber'
    elif 'yarn' in tx: form='yarn'
    elif ('cotton' in tx or 'lyocell' in tx or 'viscose' in tx or 'wool' in tx or 'silk' in tx or 'aramid' in tx) and re.search(r'fabric|textile|fiber|fibre|yarn',bx): form='fabric'
    else: form=''
    return mat,form
def numeric_tg(row):
    out={}
    for c in TG_COLS:
        v=str(row.get(c,'') or '').strip()
        if not v:continue
        try:n=float(v)
        except:continue
        if not math.isfinite(n):continue
        if c.startswith('R') or 'residue' in c:
            if 0<=n<=100:out[c]=n
        elif 20<=n<=1500: out[c]=n
    return out

# Rejections describe unchanged input, not a permanent claim about an article.
TERMINAL_REASONS={'non_textile','no_valid_tg','invalid_loi','duplicate','promoted','evidence_review_required'}
REASON_TEXT={
    'non_textile':'Rejected: source/table context is not a textile sample state.',
    'no_valid_tg':'Rejected: no valid TG numeric field remains after range checks.',
    'invalid_loi':'Rejected: LOI is not an exact numeric value in the supported range.',
    'missing_loi':'Unresolved: exact LOI is missing.',
    'missing_tg':'Unresolved: TG numeric fields are missing.',
    'missing_context':'Unresolved: textile source/table context is missing.',
    'fetch_failed':'Unresolved: open full text could not be retrieved.',
    'rate_unresolved':'Unresolved: TGA heating rate is missing or ambiguous.',
    'atmosphere_unresolved':'Unresolved: TGA atmosphere is not uniquely tied to this table/state.',
    'material_unresolved':'Unresolved: material category/form is not safely inferred.',
    'evidence_review_required':'Pending: recovered conditions do not establish exact TG–LOI sample-state evidence.',
    'duplicate':'Duplicate of an existing strict master pair.',
    'promoted':'Promoted: recovered conditions and independently reviewed pairing evidence passed the evidence gate.',
}
VOLATILE_FIELDS={'extracted_at_utc','reviewed_at_utc'}


def utc_now():
    return datetime.now(timezone.utc)


def stable_row(row):
    return {str(k):str(v if v is not None else '') for k,v in row.items()
            if not str(k).startswith('_') and k not in VOLATILE_FIELDS}


def input_fingerprint(rows, known_keys=(), approvals=(), registry_hash=''):
    """Order- and timestamp-independent fingerprint of the review inputs."""
    records=[json.dumps(stable_row(r),sort_keys=True,ensure_ascii=False) for r in rows]
    payload={'rows':sorted(set(records)),'known_keys':sorted(set(known_keys)),
             'approvals':sorted(json.dumps(a,sort_keys=True) for a in approvals),
             'review_registry_hash':registry_hash}
    return hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False).encode()).hexdigest()


def load_state():
    if not STATE.exists():
        return {'schema_version':STATE_VERSION,'processed':{}}
    # A broken state file must be repaired explicitly; never silently erase it.
    state=json.loads(STATE.read_text(encoding='utf-8'))
    if state.get('schema_version')!=STATE_VERSION or not isinstance(state.get('processed'),dict):
        raise ValueError(f'Unsupported B-review state schema: {STATE}')
    return state


def should_review(previous, fingerprint, now):
    if (previous.get('input_fingerprint')!=fingerprint or
            previous.get('parser_version')!=PARSER_VERSION):
        return True
    retry=previous.get('next_retry_utc')
    if not retry:
        return False
    try:
        when=datetime.fromisoformat(retry)
        if when.tzinfo is None:
            when=when.replace(tzinfo=timezone.utc)
        return now>=when
    except (ValueError,TypeError):
        return True


def review_state(previous, fingerprint, reasons, now):
    codes=sorted(set(reasons))
    retry=None
    if any(code not in TERMINAL_REASONS for code in codes):
        retry=now+(FETCH_RETRY if 'fetch_failed' in codes else REVIEW_RETRY)
    status=('retry_pending' if retry else
            ('awaiting_evidence_review' if 'evidence_review_required' in codes else 'complete'))
    return {'input_fingerprint':fingerprint,'parser_version':PARSER_VERSION,
            'reason_codes':codes,'status':status,
            'attempts':int(previous.get('attempts',0))+1,
            'last_attempt_utc':now.isoformat(),
            'next_retry_utc':retry.isoformat() if retry else None}


def write_if_changed(path, content):
    if path.exists() and path.read_text(encoding='utf-8')==content:
        return
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(content,encoding='utf-8')
    temp.replace(path)


def append_records(path, records):
    if not records:
        return
    old=pd.read_csv(path,dtype=str).fillna('') if path.exists() and path.stat().st_size else pd.DataFrame()
    new=pd.DataFrame(records)
    both=pd.concat([old,new],ignore_index=True,sort=False) if not old.empty else new
    write_if_changed(path,both.to_csv(index=False))


def exact_number(value, low, high):
    text=str(value if value is not None else '').strip()
    if not re.fullmatch(r'\d+(?:\.\d+)?',text):
        return None
    number=float(text)
    return number if math.isfinite(number) and low<=number<=high else None


def preliminary_reason(row):
    if not (str(row.get('title','')).strip() or str(row.get('source_location','')).strip()):
        return 'missing_context'
    if not valid_textile(row):
        return 'non_textile'
    if not numeric_tg(row):
        return 'no_valid_tg' if any(str(row.get(c,'')).strip() for c in TG_COLS) else 'missing_tg'
    if not str(row.get('LOI_pct','')).strip():
        return 'missing_loi'
    if exact_number(row.get('LOI_pct'),5,100) is None:
        return 'invalid_loi'
    return ''


def resolve_row(row, text, url, rate, window):
    """Recover conditions while retaining the original table-level provenance."""
    reason=preliminary_reason(row)
    if reason:
        return reason,None
    existing=str(row.get('heating_rate_C_min','')).strip()
    use_rate=exact_number(existing,0.001,1000) if existing else rate
    if use_rate is None:
        return ('fetch_failed' if not text and not existing else 'rate_unresolved'),None
    atmosphere,atm_source=infer_atm(row,text,window)
    if not atmosphere:
        return ('fetch_failed' if not text else 'atmosphere_unresolved'),None
    material,form=material_labels(row.get('title',''),text)
    if not material or not form:
        return ('fetch_failed' if not text else 'material_unresolved'),None
    resolved={k:v for k,v in row.items() if not k.startswith('_')}
    resolved.update({
        'DOI':doi(row.get('DOI')),'dataset_type':'literature',
        'material_category':material,'material_form':form,
        'source_title':row.get('title',''),'atmosphere':atmosphere,
        'heating_rate_C_min':use_rate,**numeric_tg(row),
        'extraction_source_url':row.get('source_url',''),
        'extraction_source_location':row.get('source_location',''),
        'method_source_url':url,'method_window_excerpt':re.sub(r'\s+',' ',window).strip(),
        'atmosphere_resolution_source':atm_source,
        'heating_rate_resolution_source':'existing table/context rate' if existing else 'TGA method windows',
        'b_review_parser_version':PARSER_VERSION,
    })
    return '',resolved


def latest_b_rows(queue):
    if 'grade' not in queue or 'extractor_version' not in queue or 'DOI' not in queue:
        return queue.iloc[0:0].copy()
    queue=queue.copy()
    queue['DOI']=queue['DOI'].map(doi)
    queue['_source_identity']=queue.apply(source_group_key,axis=1)
    queue['_version']=pd.to_numeric(queue['extractor_version'],errors='coerce')
    # Ignore unversioned historical extractions; use the newest version for a
    # DOI before selecting Grade B so an old B does not override a newer C.
    newest=queue.groupby('_source_identity')['_version'].transform('max')
    queue=queue[(queue['_version']==newest)&queue['grade'].eq('B')].copy()
    for col in ['sample_state','washing_state','LOI_pct','source_location','atmosphere',
                'heating_rate_C_min','extracted_at_utc']:
        if col not in queue:
            queue[col]=''
    queue['_sample_identity']=queue['sample_state'].map(normalize_label)
    queue['_wash_identity']=queue['washing_state'].map(normalize_label)
    queue['_atmosphere_identity']=queue['atmosphere'].map(normalized_atmosphere)
    queue['_rate_identity']=queue['heating_rate_C_min'].map(normalized_rate)
    queue['_ts']=pd.to_datetime(queue['extracted_at_utc'],errors='coerce',utc=True)
    return queue.sort_values('_ts',kind='stable',na_position='first').drop_duplicates(
        subset=['_source_identity','_sample_identity','_wash_identity','LOI_pct','source_location',
                '_atmosphere_identity','_rate_identity'],keep='last')


def main():
    if not REVIEW.exists():
        print('No review queue.')
        return
    try:
        queue=pd.read_csv(REVIEW,dtype=str).fillna('')
    except pd.errors.EmptyDataError:
        print('No Grade-B rows.')
        return
    b=latest_b_rows(queue)
    if b.empty:
        print('No Grade-B rows.')
        return
    state=load_state()
    master=pd.read_csv(MASTER,dtype=str).fillna('') if MASTER.exists() else pd.DataFrame()
    known={pair_key(r) for r in master.to_dict('records')}
    limit=max(0,int(os.getenv('B_REVIEW_MAX_DOIS','30')))
    audit=[]; debug=[]; resolved_rows=[]; promoted=[]; examined=0; skipped=0
    now=utc_now()
    registry_hash=hashlib.sha256(REVIEWS.read_bytes()).hexdigest() if REVIEWS.exists() else ''
    registry_hash=hashlib.sha256((registry_hash + registry_digest()).encode()).hexdigest()
    for identity,group in b.groupby('_source_identity',sort=False):
        d=doi(group.iloc[0].get('DOI'))
        if not is_network_doi(d):
            continue  # Non-DOI evidence requires manual source review; never query a synthetic DOI.
        rows=group.to_dict('records')
        approvals=[reviewed_metadata(row) for row in rows]
        fingerprint=input_fingerprint(rows,[k for k in known if k.startswith(d+'||')],approvals,registry_hash)
        previous=state['processed'].get(d,{})
        if not should_review(previous,fingerprint,now):
            skipped+=1
            continue
        if examined>=limit:
            break
        examined+=1
        row_cache=(previous.get('row_results',{}) if previous.get('input_fingerprint')==fingerprint
                   and previous.get('parser_version')==PARSER_VERSION else {})
        active_rows=[row for row in rows if row_cache.get(input_fingerprint([row])) not in TERMINAL_REASONS]
        text=''; url=''; rate=None; window=''
        if any(not preliminary_reason(row) for row in active_rows):
            source_url=next((r.get('source_url','') for r in active_rows if r.get('source_url','')),'')
            text,url=get_text(d,source_url)
            if text:
                rate,window=infer_rate(text)
        debug.append({
            'DOI':d,'input_fingerprint':fingerprint,'parser_version':PARSER_VERSION,
            'resolved_rate':rate if rate is not None else '',
            'rate_ctx_candidates':'|'.join(RATE_CTX.findall(window)),
            'rate_unit_candidates':'|'.join(RATE.findall(window)),
            'rate_bare_candidates':'|'.join(RATE_BARE.findall(window)),
            'method_source_url':url,
            'method_window_excerpt':re.sub(r'\s+',' ',window)[:900],
            'reviewed_at_utc':now.isoformat(),
        })
        reasons=[]
        for row in rows:
            row_fp=input_fingerprint([row])
            if row_cache.get(row_fp) in TERMINAL_REASONS:
                reasons.append(row_cache[row_fp])
                continue
            reason,resolved=resolve_row(row,text,url,rate,window)
            issues=[]
            if resolved is not None:
                # An exact label match plus a recovered rate is not scientific
                # confirmation of the same tested form, wash state or sample.
                resolved.update(reviewed_metadata(resolved))
                issues=evidence_issues(resolved)
                if issues:
                    reason='evidence_review_required'
                else:
                    key=pair_key(resolved)
                    if key in known:
                        reason='duplicate'
                    else:
                        reason='promoted'
                        approved=dict(resolved)
                        approved.update({'batch_id':'BREVIEW-'+now.strftime('%Y%m%d'),
                                         'grade':'A','direct_numeric_use':'TG+LOI',
                                         'LOI_state':row.get('LOI_state','') or row.get('washing_state',''),
                                         'limitations':'Conditions recovered by B-review; exact sample-state pairing requires the independent evidence review retained in this record.'})
                        promoted.append(approved)
                        known.add(key)
                resolved.update({'b_review_reason_code':reason,'b_review_evidence_issues':'|'.join(issues),
                                 'input_fingerprint':fingerprint,'reviewed_at_utc':now.isoformat()})
                resolved_rows.append(resolved)
            reasons.append(reason)
            row_cache[row_fp]=reason
            audit.append({
                'DOI':d,'sample_state':row.get('sample_state',''),'LOI_pct':row.get('LOI_pct',''),
                'original_atmosphere':row.get('atmosphere',''),
                'original_heating_rate_C_min':row.get('heating_rate_C_min',''),
                'source_url':row.get('source_url',''),'source_location':row.get('source_location',''),
                'reason_code':reason,'review_result':REASON_TEXT[reason],
                'evidence_issues':'|'.join(issues),'input_fingerprint':fingerprint,
                'parser_version':PARSER_VERSION,'reviewed_at_utc':now.isoformat(),
            })
        state['processed'][d]=review_state(previous,fingerprint,reasons,now)
        state['processed'][d]['row_results']=row_cache
    if not examined:
        print(f'B-review examined DOIs=0; cached={skipped}; no files changed.')
        return
    # Preserve historic audits and original input; only real attempts add rows.
    append_records(AUTO/'b_review_audit.csv',audit)
    append_records(AUTO/'b_review_method_debug.csv',debug)
    append_records(AUTO/'b_review_resolved.csv',resolved_rows)
    if promoted:
        output=INC/f"verified_breview_{now.strftime('%Y%m%d')}.csv"
        existing=pd.read_csv(output,dtype=str).fillna('') if output.exists() else pd.DataFrame()
        existing_keys={pair_key(r) for r in existing.to_dict('records')}
        append_records(output,[r for r in promoted if pair_key(r) not in existing_keys])
    write_if_changed(STATE,json.dumps(state,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
    print(f'B-review examined DOIs={examined}; cached={skipped}; promoted={len(promoted)}; audit rows={len(audit)}')


if __name__=='__main__':
    main()
