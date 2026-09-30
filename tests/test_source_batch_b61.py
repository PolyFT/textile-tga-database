"""Keep heating protocols and separate thermal assays tied to original sample states."""
import csv,hashlib,json,unittest
from pathlib import Path
import pandas as pd
from scripts.pairing import evidence_issues,measurement_fingerprint
from scripts.validate_tg_loi import build_tables,numeric_errors
R=Path(__file__).resolve().parents[1];M=R/'data/curation/source_review_manifest_20260930_b61.json'
def rows(tag):
 f=next(x['file'] for x in json.loads(M.read_text())['files'] if tag in x['file']);return list(csv.DictReader((R/f).open()))
class Batch61(unittest.TestCase):
 def test_fingerprints(self):
  for tag,n in [('silk38961',2),('cotton1997',22)]:
   d=rows(tag);self.assertEqual(len(d),n)
   for r in d:self.assertFalse(evidence_issues(r));self.assertEqual(measurement_fingerprint(r),r['reviewed_measurement_fingerprint'])
 def test_cotton_exact_pairs(self):
  e=[('Untreated','18.6','368.6','12.8','382.9','10.9'),('FYR-1','21.4','310.2','21.6','317.6','22.9'),('FYR-2','24.4','295.8','29.5','305.7','33.8'),('FYR-3','24.8','289.3','39.1','297.0','38.8'),('FYR-4','26.4','284.1','37.8','293.3','39.5'),('NMA-1','19.3','367.7','15.1','385.4','15.6'),('NMA-2','19.6','368.3','17.4','384.2','20.6'),('NMA-3','20.3','372.6','23.4','386.0','20.6'),('F/N-1','24.9','324.8','34.4','336.3','36.0'),('F/N-2','27.6','307.3','32.1','317.1','38.0'),('F/N-3','27.2','296.3','36.4','307.0','40.1')]
  expected=[]
  for s,loi,t10,r10,t20,r20 in e:expected.extend([(s,'10',loi,t10,r10),(s,'20',loi,t20,r20)])
  self.assertEqual([(r['sample_state'],r['heating_rate_C_min'],r['LOI_pct'],r['Tmax1_C'],r['R600_pct']) for r in rows('cotton1997')],expected)
 def test_cotton_protocol_not_aging(self):
  for r in rows('cotton1997'):
   self.assertEqual((r['atmosphere'],r['gas_flow_mL_min'],r['TG_end_C']),('nitrogen','30','600'));self.assertIn('hold for 20 min',r['TGA_preconditioning']);self.assertIn('100 C',r['TGA_preconditioning']);self.assertIn('2 mm squares',r['TGA_specimen_preparation']);self.assertNotIn('NMA-4',r['sample_state'])
   for f in ['T5_C','T10_C','Tonset_C','Tmax2_C']:self.assertFalse(r.get(f))
 def test_silk_exact_pairs(self):
  self.assertEqual([(r['LOI_pct'],r['R600_pct'],r['Tmax1_C'],r['Tmax2_C']) for r in rows('silk38961')],[('23.21','34','327',''),('32.38','40','238','307')])
 def test_silk_no_incineration_or_td11_substitution(self):
  for r in rows('silk38961'):
   self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['gas_flow_mL_min']),('nitrogen','10','100'))
   for f in ['T5_C','T10_C','Tonset_C','add_on_pct']:self.assertFalse(r.get(f))
   self.assertIn('initial_no_durability',r['washing_state']);self.assertIn('incineration',r['limitations']);self.assertIn('modifier decomposition',r['limitations'])
 def test_state_counts_not_ramp_counts(self):
  c=pd.DataFrame(rows('cotton1997'));m,_,_,v=build_tables(c);self.assertEqual(len(m),22);self.assertEqual(v['verified_exact_sample_states'],11)
  d=pd.DataFrame(rows('silk38961')+rows('cotton1997'));m,_,_,v=build_tables(d);self.assertEqual(len(m),24);self.assertEqual(v['verified_exact_sample_states'],13);self.assertFalse(numeric_errors(d))
 def test_derived_protocol_metadata(self):
  m,_,_,_=build_tables(pd.DataFrame(rows('cotton1997')))
  for r in m.to_dict('records'):self.assertIn('hold for 20 min',r['TGA_preconditioning']);self.assertIn('2 mm squares',r['TGA_specimen_preparation'])
 def test_source_hashes_and_holds(self):
  for f in json.loads(M.read_text())['files']:self.assertEqual(hashlib.sha256((R/f['file']).read_bytes()).hexdigest(),f['published_input_sha256'])
  h=json.loads((R/'data/curation/source_review_holds_20260930_b61.json').read_text());self.assertEqual(len(h),9);s=json.dumps(h);self.assertIn('NMA-4',s);self.assertIn('21.5',s);self.assertIn('10.34133/research.0910',s)
