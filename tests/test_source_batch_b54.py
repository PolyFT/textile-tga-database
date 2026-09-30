"""Keep exact PAN series values and analytical specimen preparation visible."""
import csv,hashlib,json,unittest
from pathlib import Path
import pandas as pd
from scripts.pairing import evidence_issues,measurement_fingerprint
from scripts.validate_tg_loi import build_tables,numeric_errors
R=Path(__file__).resolve().parents[1]
M=R/'data/curation/source_review_manifest_20260930_b54.json'
def rows():
 f=json.loads(M.read_text())['files'][0]['file']
 return list(csv.DictReader((R/f).open()))
class Batch54(unittest.TestCase):
 def test_all_eleven_states_fingerprint_bound(self):
  d=rows();self.assertEqual(len(d),11);self.assertEqual(len({r['sample_state'] for r in d}),11)
  for r in d:self.assertFalse(evidence_issues(r));self.assertEqual(measurement_fingerprint(r),r['reviewed_measurement_fingerprint'])
  self.assertIn('measurement_review_pending_or_stale',evidence_issues(dict(d[0],R700_pct='99')))
 def test_exact_pairs(self):
  expected={'OPANFs':('18.5','38.7'),'A-1':('20.1','34.5'),'A-2':('21.2','38.3'),'A-4':('21.4','37.1'),'A-6':('22.4','32.0'),'A-8':('21.8','25.9'),'B-1':('20.1','45.3'),'B-2':('22.4','46.2'),'B-4':('26.6','48.1'),'B-6':('33.3','38.9'),'B-8':('47.0','37.5')}
  self.assertEqual({r['sample_state']:(r['LOI_pct'],r['R700_pct']) for r in rows()},expected)
 def test_same_fiber_distinct_assay_preparation(self):
  for r in rows():
   self.assertEqual(r['material_form_TGA'],'wet-spun polyacrylonitrile fibers');self.assertEqual(r['material_form_LOI'],r['material_form_TGA'])
   self.assertEqual(r['TGA_specimen_preparation'],'finely powdered aliquots of the same wet-spun fibers');self.assertEqual(r['LOI_specimen_preparation'],'braided specimens of the same wet-spun fibers')
   self.assertIn('powdered aliquots',r['pairing_evidence']);self.assertIn('braided fibers',r['pairing_evidence'])
 def test_conditions_and_no_thermal_substitutes(self):
  for r in rows():
   self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['TG_end_C'],r['tga_start_temperature_C']),('nitrogen','10','700','100'))
   for field in ['T5_C','Tonset_C','Tmax1_C','Tmax2_C','R800_pct','gas_flow_mL_min']:self.assertFalse(r.get(field))
   self.assertIn('preparative_water_rinse',r['washing_state']);self.assertIn('no_durability_washes',r['washing_state'])
 def test_derived_rows_retain_assay_preparation(self):
  data=pd.DataFrame(rows());master,_,_,report=build_tables(data)
  self.assertEqual(len(master),11);self.assertEqual(report['verified_exact_sample_states'],11);self.assertFalse(numeric_errors(data))
  for r in master.to_dict('records'):
   self.assertEqual(r['TGA_specimen_preparation'],'finely powdered aliquots of the same wet-spun fibers');self.assertEqual(r['LOI_specimen_preparation'],'braided specimens of the same wet-spun fibers')
 def test_input_hash_and_screen_holds(self):
  for f in json.loads(M.read_text())['files']:self.assertEqual(hashlib.sha256((R/f['file']).read_bytes()).hexdigest(),f['published_input_sha256'])
  h=json.loads((R/'data/curation/source_review_holds_20260930_b54.json').read_text());self.assertEqual(len(h),6)
  self.assertTrue(any(x['DOI']=='10.3390/fib6020036' and x['status']=='excluded_no_own_LOI' for x in h))
