"""Keep supercritical cotton pairs, atmosphere and source caveats exact."""
import csv,hashlib,json,unittest
from pathlib import Path
import pandas as pd
from scripts.pairing import evidence_issues,measurement_fingerprint
from scripts.validate_tg_loi import build_tables,numeric_errors
R=Path(__file__).resolve().parents[1]
M=R/'data/curation/archive/source_review_manifest_20260930_b57.json'
def rows():
 return list(csv.DictReader((R/json.loads(M.read_text())['files'][0]['file']).open()))
class Batch57(unittest.TestCase):
 def test_exact_pairs(self):
  self.assertEqual([(r['add_on_pct'],r['R600_pct'],r['LOI_pct']) for r in rows()],[('5.6','16.2','24.5'),('7.0','22.8','26.5'),('14.7','33.7','29.8'),('11.2','8.8','23.6'),('14.2','18.5','24.0'),('17.0','27.3','24.8')])
 def test_fingerprints_and_derived(self):
  for r in rows():
   self.assertFalse(evidence_issues(r));self.assertEqual(measurement_fingerprint(r),r['reviewed_measurement_fingerprint'])
  d=pd.DataFrame(rows());m,_,_,report=build_tables(d);self.assertEqual(len(m),6);self.assertEqual(report['verified_exact_sample_states'],6);self.assertFalse(numeric_errors(d))
 def test_conditions_and_no_inferred_peaks(self):
  for r in rows():
   self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['TG_end_C']),('nitrogen','10','600'))
   self.assertEqual(r['LOI_replicates'],'4');self.assertEqual(r['material_form_TGA'],r['material_form_LOI'])
   for f in ['Tmax1_C','Tmax2_C','Tonset_C','R800_pct','gas_flow_mL_min']:self.assertFalse(r.get(f))
   self.assertTrue(r['source_reported_degradation_onsets_C']);self.assertIn('edition conflicts',r['LOI_method']);self.assertIn('scribd.com/document/1047390503',r['additional_fulltext_url'])
 def test_hash_and_holds(self):
  for f in json.loads(M.read_text())['files']:self.assertEqual(hashlib.sha256((R/f['file']).read_bytes()).hexdigest(),f['published_input_sha256'])
  h=json.loads((R/'data/curation/archive/source_review_holds_20260930_b57.json').read_text());self.assertEqual(len(h),3)
  s=json.dumps(h);self.assertIn('17-19%',s);self.assertIn('air',s);self.assertIn('D2863-13',s)
