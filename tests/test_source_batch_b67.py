"""Keep unknown residue assessment temperatures distinct from scan endpoints."""
import csv,hashlib,json,unittest
from pathlib import Path
import pandas as pd
from scripts.pairing import evidence_issues,measurement_fingerprint
from scripts.validate_tg_loi import build_tables,numeric_errors
R=Path(__file__).resolve().parents[1];M=R/'data/curation/archive/source_review_manifest_20260930_b67.json'
def rows(tag):
 f=next(x['file'] for x in json.loads(M.read_text())['files'] if x['file'].endswith('_'+tag+'.csv'));return list(csv.DictReader((R/f).open()))
class Batch67(unittest.TestCase):
 def test_fingerprints_and_input_hashes(self):
  for f in json.loads(M.read_text())['files']:
   self.assertEqual(hashlib.sha256((R/f['file']).read_bytes()).hexdigest(),f['published_input_sha256'])
   for r in csv.DictReader((R/f['file']).open()):self.assertFalse(evidence_issues(r));self.assertEqual(measurement_fingerprint(r),r['reviewed_measurement_fingerprint'])
 def test_citrus_generic_residue_not_R800(self):
  self.assertEqual([(r['LOI_pct'],r['residue_pct']) for r in rows('bc_citrus')],[('25','53.30'),('32','49.11')])
  for r in rows('bc_citrus'):
   self.assertFalse(r['residue_temp_C']);self.assertEqual(r['TG_end_C'],'800');self.assertFalse(r.get('R800_pct'));self.assertIn('unspecified',r['treatment_method'])
 def test_jute_explicit_500C_residue(self):
  self.assertEqual([(r['LOI_pct'],r['residue_pct']) for r in rows('jute_smsn')],[('21','13'),('43','32')])
  for r in rows('jute_smsn'):
   self.assertEqual(r['residue_temp_C'],'500');self.assertEqual(r['TG_end_C'],'800');self.assertFalse(r.get('R800_pct'));self.assertFalse(r.get('add_on'));self.assertEqual(r['material_form'],'plain woven jute fabric')
 def test_derived_temperatures_do_not_infer(self):
  m,_,_,_=build_tables(pd.DataFrame(rows('bc_citrus')))
  for r in m.to_dict('records'):
   self.assertTrue(pd.isna(r.get('residue_temp_C')) or not str(r.get('residue_temp_C','')).strip());self.assertTrue(pd.isna(r.get('R800_pct')) or not str(r.get('R800_pct','')).strip());self.assertEqual(float(r['TG_end_C']),800)
 def test_four_initial_states(self):
  d=pd.DataFrame(rows('bc_citrus')+rows('jute_smsn'));m,_,_,v=build_tables(d);self.assertEqual(len(m),4);self.assertEqual(v['verified_exact_sample_states'],4);self.assertFalse(numeric_errors(d))
  for r in d.to_dict('records'):
   self.assertEqual(r['heating_rate_C_min'],'10');self.assertEqual(r['atmosphere'],'nitrogen');self.assertIn('initial',r['washing_state'])
 def test_whole_paper_holds(self):
  h=(R/'data/curation/archive/source_review_holds_20260930_b67.json').read_text();self.assertIn('4% SMSN',h);self.assertIn('cowhide',h);self.assertIn('washed',h);self.assertIn('4.59',h)
