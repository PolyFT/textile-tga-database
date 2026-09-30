"""Keep MCHP cotton assays and source-native weight gain separate."""
import csv,hashlib,json,unittest
from pathlib import Path
import pandas as pd
from scripts.pairing import evidence_issues,measurement_fingerprint
from scripts.validate_tg_loi import build_tables,numeric_errors
R=Path(__file__).resolve().parents[1]
M=R/'data/curation/source_review_manifest_20260930_b56.json'
def rows():
 return list(csv.DictReader((R/json.loads(M.read_text())['files'][0]['file']).open()))
class Batch56(unittest.TestCase):
 def test_exact_pairs(self):
  self.assertEqual({r['sample_state']:(r['T10_C'],r['Tmax1_C'],r['residue_pct'],r['LOI_pct']) for r in rows()},{'MP30':('298','375','20.9','36.3'),'nCH30':('291','378','19.8','57.9'),'MCHP30':('237','383','27.5','58.2')})
 def test_fingerprints_and_derived(self):
  for r in rows():
   self.assertFalse(evidence_issues(r));self.assertEqual(measurement_fingerprint(r),r['reviewed_measurement_fingerprint'])
  d=pd.DataFrame(rows());m,_,_,report=build_tables(d);self.assertEqual(len(m),3);self.assertEqual(report['verified_exact_sample_states'],3);self.assertFalse(numeric_errors(d))
 def test_conditions_and_endpoint(self):
  for r in rows():
   self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['gas_flow_mL_min'],r['TG_end_C'],r['residue_temp_C']),('nitrogen','10','30','750','750'))
   self.assertEqual(r['material_form_TGA'],r['material_form_LOI']);self.assertIn('no_durability_washes',r['washing_state']);self.assertEqual(r['LOI_replicates'],'3')
   for f in ['R700_pct','R800_pct','Tonset_C','LOI_uncertainty_pct']:self.assertFalse(r.get(f))
 def test_weight_gain_not_normalized(self):
  for r in rows():
   self.assertFalse(r.get('add_on_pct'));self.assertIn(r['source_reported_weight_gain_pct'],['44.4','44.7','46.4']);self.assertIn('reverse',r['weight_gain_definition_status'])
 def test_hash_and_holds(self):
  for f in json.loads(M.read_text())['files']:self.assertEqual(hashlib.sha256((R/f['file']).read_bytes()).hexdigest(),f['published_input_sha256'])
  h=json.loads((R/'data/curation/source_review_holds_20260930_b56.json').read_text());self.assertEqual(len(h),4)
  s=json.dumps(h);self.assertIn('17.2 versus 17.1',s);self.assertIn('MCHP30/alone',s);self.assertIn('all post-wash states',s)
