#!/usr/bin/env python3
from __future__ import annotations
import io, os, re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
import pandas as pd, requests
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'; AUTO=DATA/'automation'; INC=DATA/'incoming'
REVIEW=AUTO/'review_queue.csv'; MASTER=DATA/'tg_loi_master.csv'
HEAD={'User-Agent':'textile-tga-database/1.2 (public academic data curation; GitHub PolyFT/textile-tga-database)'}
RATE=re.compile(r'(\d+(?:\.\d+)?)\s*(?:°\s*C|℃|K)\s*(?:/|per)\s*min(?:ute)?',re.I)
RATE_CTX=re.compile(r'(?:heating\s*rate|heated[^.;\n]{0,100}?at|rate\s+of)[^.;\n]{0,100}?(\d+(?:\.\d+)?)\s*(?:°\s*C|℃|K)\s*(?:/|per)\s*min(?:ute)?',re.I)
ATM=[('N2',re.compile(r'\b(?:nitrogen|N\s*2|N₂)\b',re.I)),('air',re.compile(r'\b(?:air|oxidative atmosphere)\b',re.I)),('argon',re.compile(r'\b(?:argon|Ar)\b',re.I)),('O2',re.compile(r'\b(?:oxygen|O\s*2|O₂)\b',re.I))]
TG_COLS=['T1_C','T5_C','T10_C','T20_C','T40_C','T50_C','Tonset_C','Tmax1_C','Tmax2_C','Tmax3_C','R400_pct','R500_pct','R550_pct','R600_pct','R650_pct','R700_pct','R800_pct','residue_pct','residue_at_Tmax_pct','residue_at_Tmax1_pct','residue_at_Tmax2_pct','residue_at_Tmax3_pct']

def doi(v):
    x=str(v or '').strip().lower()
    x=re.sub(r'^https?://(?:dx\.)?doi\.org/','',x)
    return re.sub(r'^doi:\s*','',x).rstrip(' .;,')

def ns(v):
    x=str(v or '').replace('₂','2').strip().lower()
    x=re.sub(r'\s+',' ',x)
    return re.sub(r'[^a-z0-9.%+()/-]+','',x)

def rate_s(v):
    try:return str(float(v))
    except:return str(v or '').strip()

def norm_key(d,s,a,r):
    return f'{doi(d)}||{ns(s)}||{str(a or "").strip().lower()}||{rate_s(r)}'

def get_text(d, source_url=''):
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
    return '',''

def tg_windows(text):
    out=[]
    for m in re.finditer(r'\b(?:TGA|TG/DTG|thermogravimetric(?: analysis)?|thermogravimetry)\b',text,re.I):
        z=text[m.start():min(len(text),m.end()+850)]
        # Method-like windows outrank discussion-only windows.
        score=0
        if re.search(r'heating\s*rate|°\s*C\s*/\s*min|℃\s*/\s*min|K\s*/\s*min',z,re.I): score+=4
        if re.search(r'nitrogen|\bair\b|argon|oxygen',z,re.I): score+=2
        if re.search(r'flow\s*rate|mL\s*/\s*min|from\s+\d+\s*(?:°C|℃).*to\s+\d+',z,re.I): score+=2
        if re.search(r'instrument|analy[sz]er|NETZSCH|TA Instruments|Mettler|PerkinElmer|Shimadzu',z,re.I): score+=2
        if re.search(r'MCC|microscale combustion|UL[- ]?94|vertical burning',z,re.I): score-=4
        out.append((score,z))
    return sorted(out,key=lambda x:x[0],reverse=True)

def infer_rate(text):
    wins=tg_windows(text)
    for score,z in wins:
        if score<4: continue
        vals={float(x) for x in RATE_CTX.findall(z)}
        if not vals: vals={float(x) for x in RATE.findall(z)}
        if len(vals)==1:return next(iter(vals)),z
    return None,''

def atmos(s):
    return list(dict.fromkeys(n for n,p in ATM if p.search(str(s or ''))))

def infer_atm(row,text,method_window):
    existing=str(row.get('atmosphere','') or '').strip()
    if existing:return existing,'existing table/context atmosphere'
    loc=str(row.get('source_location','') or '')
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

def material_labels(title,text=''):
    x=(str(title or '')+' '+str(text or '')[:5000]).lower()
    if re.search(r'nylon\s*[/–-]\s*cotton|cotton\s*[/–-]\s*nylon|nyco',x): mat='nylon/cotton blend'
    elif 'cotton' in x: mat='cotton'
    elif re.search(r'polyester|\bpet\b|co-polyester|copolyester',x): mat='polyester'
    elif re.search(r'polyamide|\bpa6\b|\bpa66\b|nylon',x): mat='polyamide/nylon'
    elif 'lyocell' in x: mat='lyocell'
    elif 'viscose' in x: mat='viscose'
    elif 'wool' in x: mat='wool'
    elif 'silk' in x: mat='silk'
    elif re.search(r'aramid|kevlar|nomex',x): mat='aramid'
    elif re.search(r'polypropylene|\bpp\b',x): mat='polypropylene'
    elif re.search(r'polyacrylonitrile|\bpan\b',x): mat='polyacrylonitrile'
    else: mat=''
    if 'nonwoven' in x: form='nonwoven'
    elif re.search(r'knitted|\bknit\b',x): form='knitted fabric'
    elif 'woven' in x: form='woven fabric'
    elif re.search(r'fabric|textile',x): form='fabric'
    elif re.search(r'fibres|fibers|fibre|fiber',x): form='fiber'
    elif 'yarn' in x: form='yarn'
    else: form=''
    return mat,form

def valid_textile(row):
    title=str(row.get('title','') or '')
    loc=str(row.get('source_location','') or '')
    probe=(title+' '+loc).lower()
    # reject known non-textile test-piece states
    if re.search(r'\b(plaque|film|resin|paper|composite)\b',loc,re.I): return False
    return bool(re.search(r'fabric|textile|fiber|fibre|yarn|cotton|polyester|\bpet\b|nylon|polyamide|lyocell|viscose|wool|silk|aramid',probe,re.I))

def numeric_tg(row):
    out={}
    for c in TG_COLS:
        v=str(row.get(c,'') or '').strip()
        if not v:continue
        try:n=float(v)
        except:continue
        if c.startswith('R') or 'residue' in c:
            if 0<=n<=100:out[c]=n
        elif 20<=n<=1500: out[c]=n
    return out

def main():
    if not REVIEW.exists(): print('No review queue.'); return
    b=pd.read_csv(REVIEW,dtype=str).fillna('')
    b=b[b.get('grade','').eq('B')].copy()
    if b.empty: print('No Grade-B rows.'); return
    # keep the newest version of each evidence row; old extractor versions remain in audit files
    b['_ts']=pd.to_datetime(b.get('extracted_at_utc',''),errors='coerce')
    b=b.sort_values('_ts').drop_duplicates(subset=['DOI','sample_norm','LOI_pct','source_location'],keep='last')
    master=pd.read_csv(MASTER,dtype=str).fillna('') if MASTER.exists() else pd.DataFrame()
    known=set()
    for _,r in master.iterrows():
        known.add(norm_key(r.get('DOI',''),r.get('sample_state',''),r.get('atmosphere',''),r.get('heating_rate_C_min','')))
    limit=int(os.getenv('B_REVIEW_MAX_DOIS','30'))
    promoted=[]; audit=[]; seen_doi=0
    for d,g in b.groupby(b['DOI'].map(doi),sort=False):
        if seen_doi>=limit:break
        if not d:continue
        seen_doi+=1
        first=g.iloc[0].to_dict()
        text,url=get_text(d,first.get('source_url',''))
        rate,win=infer_rate(text) if text else (None,'')
        for _,rr in g.iterrows():
            row=rr.to_dict(); nums=numeric_tg(row)
            reason=''
            if not valid_textile(row): reason='Rejected: source/table context is not a textile sample state.'
            elif not nums: reason='Rejected: no valid TG numeric field remains after range checks.'
            elif not str(row.get('LOI_pct','')).strip(): reason='Rejected: exact LOI is missing.'
            elif rate is None and not str(row.get('heating_rate_C_min','')).strip(): reason='Unresolved: TGA heating rate not uniquely identified.'
            else:
                use_rate=float(row['heating_rate_C_min']) if str(row.get('heating_rate_C_min','')).strip() else rate
                atm,atm_src=infer_atm(row,text,win)
                if not atm: reason='Unresolved: TGA atmosphere not uniquely tied to this table/state.'
                else:
                    k=norm_key(d,row.get('sample_state',''),atm,use_rate)
                    if k in known: reason='Duplicate of an existing strict master pair.'
                    else:
                        mat,form=material_labels(row.get('title',''),text)
                        if not mat or not form: reason='Unresolved: material category/form is not safely inferred from title.'
                        else:
                            promoted.append({
                                'batch_id':'BREVIEW-'+datetime.now(timezone.utc).strftime('%Y%m%d'),
                                'dataset_type':'literature','material_category':mat,'material_form':form,
                                'sample_state':row.get('sample_state',''),'atmosphere':atm,
                                'heating_rate_C_min':use_rate,'LOI_pct':row.get('LOI_pct',''),
                                'LOI_uncertainty_pct':row.get('LOI_uncertainty_pct',''),**nums,
                                'direct_numeric_use':'TG+LOI',
                                'evidence':'Grade-B second-pass promotion: original table-level TG/LOI sample match retained; TGA conditions re-resolved from the original full-text method section.',
                                'source_title':row.get('title',''),'year':row.get('year',''),'journal':row.get('journal',''),
                                'DOI':d,'source_url':url or row.get('source_url',''),
                                'source_location':row.get('source_location',''),
                                'limitations':'Promoted only after deterministic second-pass recovery of TGA atmosphere/heating rate; no midpoint/range inference used.'
                            }); known.add(k); reason=f'Promoted: atmosphere={atm} ({atm_src}); heating_rate={use_rate} C/min.'
            audit.append({'DOI':d,'sample_state':row.get('sample_state',''),'LOI_pct':row.get('LOI_pct',''),
                          'original_atmosphere':row.get('atmosphere',''),'original_heating_rate_C_min':row.get('heating_rate_C_min',''),
                          'review_result':reason,'reviewed_at_utc':datetime.now(timezone.utc).isoformat()})
    pd.DataFrame(audit).to_csv(AUTO/'b_review_audit.csv',index=False)
    if promoted:
        out=INC/f"verified_breview_{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv"
        new=pd.DataFrame(promoted)
        if out.exists():
            old=pd.read_csv(out,dtype=str).fillna('')
            new=pd.concat([old,new],ignore_index=True,sort=False)
            new['_k']=new.apply(lambda r:norm_key(r.get('DOI',''),r.get('sample_state',''),r.get('atmosphere',''),r.get('heating_rate_C_min','')),axis=1)
            new=new.drop_duplicates('_k',keep='last').drop(columns='_k')
        new.to_csv(out,index=False)
        print(f'B-review promoted {len(promoted)} rows; output={out.relative_to(ROOT)} rows={len(new)}')
    else:
        print('B-review promoted 0 rows.')
    print(f'B-review examined DOIs={seen_doi}; audit rows={len(audit)}')

if __name__=='__main__': main()
