"""Preserve source-specific recipes, uncertainty and specimen preparation."""
import csv,hashlib,json,unittest
from pathlib import Path
import pandas as pd
from scripts.pairing import evidence_issues,measurement_fingerprint
from scripts.validate_tg_loi import build_tables,numeric_errors
R=Path(__file__).resolve().parents[1];M=R/'data/curation/source_review_manifest_20260930_b69.json'
def rows(tag):
 f=next(x['file'] for x in json.loads(M.read_text())['files'] if x['file'].endswith('_'+tag+'.csv'));return list(csv.DictReader((R/f).open()))
class Batch69(unittest.TestCase):
 def test_fingerprints(self):
  for f in json.loads(M.read_text())['files']:
   self.assertEqual(hashlib.sha256((R/f['file']).read_bytes()).hexdigest(),f['published_input_sha256'])
   for r in csv.DictReader((R/f['file']).open()):self.assertFalse(evidence_issues(r));self.assertEqual(measurement_fingerprint(r),r['reviewed_measurement_fingerprint'])
 def test_casein_twenty_bilayers_and_uncertainty(self):
  d=rows('casein_lbl2019');self.assertEqual([(r['LOI_pct'],r['Tonset_C'],r['R600_pct']) for r in d],[('21','330.68','13.97'),('29','275.24','31.11'),('32','274.94','33.97'),('34','276.60','35.77')])
  for r in d:
   self.assertEqual(r['LOI_replicates'],'3');self.assertFalse(r.get('LOI_standard_deviation'));self.assertFalse(r.get('gas_flow_mL_min'))
  for r in d[1:]:self.assertIn('20 bilayers',r['treatment_method'])
 def test_nyco_exact_pairs(self):
  d=rows('nyco_pacys');self.assertEqual([(r['LOI_pct'],r['Tonset_C'],r['R600_pct']) for r in d],[('19.6','360.3','18.67'),('20.1','300.7','25.99'),('26.6','223.4','40.32'),('27.0','210.2','44.33')])
  for r in d:
   self.assertIn('blend ratio not reported',r['composition']);self.assertEqual(r['heating_rate_C_min'],'20');self.assertEqual(r['gas_flow_mL_min'],'20');self.assertEqual(r['TG_end_C'],'800');self.assertFalse(r.get('Tmax1_C'))
 def test_lessan_pairs_and_sd(self):
  d=rows('lessan2011');self.assertEqual([(r['sample_state'],r['LOI_pct'],r['R600_pct']) for r in d],[('Untreated','18.6','7.5'),('4','18.8','15'),('9','23.0','28'),('13','22.7','27'),('23','22.3','26')]);self.assertEqual([r['LOI_standard_deviation'] for r in d],['0.29','0.37','0.38','0.16','0.44'])
  for r in d:
   self.assertEqual(r['LOI_n'],'5');self.assertEqual(r['gas_flow_mL_min'],'100');self.assertFalse(r.get('Tmax1_C'))
 def test_derived_lessan_preparation(self):
  m,_,_,_=build_tables(pd.DataFrame(rows('lessan2011')))
  for r in m.to_dict('records'):
   self.assertEqual(r['material_form_TGA'],'plain woven cotton fabric');self.assertIn('8 mg',r['TGA_specimen_preparation']);self.assertEqual(r['source_material_form_TGA_raw'],'plain woven cotton fabric aliquot');self.assertIn('no_durability_wash',r['washing_state'])
 def test_thirteen_distinct_states(self):
  d=pd.DataFrame(rows('casein_lbl2019')+rows('nyco_pacys')+rows('lessan2011'));m,_,_,v=build_tables(d);self.assertEqual(len(m),13);self.assertEqual(v['verified_exact_sample_states'],13);self.assertFalse(numeric_errors(d))
