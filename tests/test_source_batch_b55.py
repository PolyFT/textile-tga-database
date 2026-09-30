"""Keep GEL/AMP source conflicts and state-specific treatment distinctions."""
import csv,hashlib,json,unittest
from pathlib import Path
import pandas as pd
from scripts.pairing import evidence_issues,measurement_fingerprint
from scripts.validate_tg_loi import build_tables,numeric_errors
R=Path(__file__).resolve().parents[1]
M=R/'data/curation/source_review_manifest_20260930_b55.json'
def rows():
 return list(csv.DictReader((R/json.loads(M.read_text())['files'][0]['file']).open()))
class Batch55(unittest.TestCase):
 def test_exact_pairs(self):
  self.assertEqual({r['sample_state']:(r['T10_C'],r['Tmax1_C'],r['R700_pct'],r['LOI_pct']) for r in rows()},{'SiO2@COT':('282.2','361.2','40.1','20.5'),'5BL@COT':('281.8','347.9','26.7','23.2'),'5BL-SiO2@COT':('279.5','347.5','44.0','27.1'),'10BL-SiO2@COT':('282.3','342.7','45.5','30.3')})
 def test_fingerprints_and_derived(self):
  for r in rows():
   self.assertFalse(evidence_issues(r));self.assertEqual(measurement_fingerprint(r),r['reviewed_measurement_fingerprint'])
  d=pd.DataFrame(rows());m,_,_,report=build_tables(d);self.assertEqual(len(m),4);self.assertEqual(report['verified_exact_sample_states'],4);self.assertFalse(numeric_errors(d))
 def test_methods_and_uncertainty(self):
  for r in rows():
   self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['gas_flow_mL_min'],r['TG_end_C']),('N2','10','50','700'))
   self.assertEqual(r['LOI_uncertainty_type'],'not specified');self.assertEqual(r['material_form_TGA'],r['material_form_LOI']);self.assertIn('no_durability_washes',r['washing_state'])
 def test_state_specific_preparation(self):
  for r in rows():
   s=r['sample_state'];method=r['treatment_method']
   if s=='SiO2@COT':self.assertIn('not asserted',method);self.assertFalse(r['add_on_pct'])
   else:
    self.assertIn('BeforeLBL',method);self.assertIn('10bilayers' if s.startswith('10') else '5bilayers',method)
    self.assertEqual('Then dipinSiO2' in method,'SiO2' in s)
 def test_hash_and_holds(self):
  for f in json.loads(M.read_text())['files']:self.assertEqual(hashlib.sha256((R/f['file']).read_bytes()).hexdigest(),f['published_input_sha256'])
  h=json.loads((R/'data/curation/source_review_holds_20260930_b55.json').read_text());self.assertEqual(len(h),4)
  s=json.dumps(h);self.assertIn('41.4',s);self.assertIn('41.3',s);self.assertIn('25.6',s);self.assertIn('all10LCstates',s)
