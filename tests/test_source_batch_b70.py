"""Preserve generic residues, thermal preholds and two-atmosphere state counts."""
import csv,hashlib,json,unittest
from pathlib import Path
import pandas as pd
from scripts.pairing import evidence_issues,measurement_fingerprint
from scripts.validate_tg_loi import build_tables,numeric_errors
R=Path(__file__).resolve().parents[1];M=R/'data/curation/source_review_manifest_20260930_b70.json'
def rows(tag):
 f=next(x['file'] for x in json.loads(M.read_text())['files'] if x['file'].endswith('_'+tag+'.csv'));return list(csv.DictReader((R/f).open()))
class Batch70(unittest.TestCase):
 def test_fingerprints(self):
  for f in json.loads(M.read_text())['files']:
   self.assertEqual(hashlib.sha256((R/f['file']).read_bytes()).hexdigest(),f['published_input_sha256'])
   for r in csv.DictReader((R/f['file']).open()):self.assertFalse(evidence_issues(r));self.assertEqual(measurement_fingerprint(r),r['reviewed_measurement_fingerprint'])
 def test_boron_means_prehold_and_uncertainty(self):
  d=rows('boron2023');self.assertEqual([(r['atmosphere'],r['LOI_pct'],r['T5_C'],r['residue_pct']) for r in d],[('nitrogen','34.0','304.7','38.8'),('air','34.0','302.8','24.5'),('nitrogen','35.5','305.2','42.2'),('air','35.5','301.3','28.8')]);self.assertEqual([r['T5_reported_plus_minus'] for r in d],['0.5','0.6','1.2','0.5'])
  for r in d:
   self.assertIn('120C for20min',r['TG_prehold']);self.assertFalse(r['residue_temp_C']);self.assertEqual(r['TG_end_C'],'705');self.assertEqual(r['residue_pct'],r['terminal_residue_pct']);self.assertIn('40mL/min',r['gas_flow_reference'])
 def test_lpu_five_unconflicted_labels(self):
  d=rows('lpu2025');self.assertEqual([(r['sample_state'],r['LOI_pct'],r['Tonset_C'],r['residue_pct']) for r in d],[('COT','18.4','317.0','13.96'),('SiO2@COT','20.4','293.33','35.0'),('DCD@COT','19.6','313.17','20.76'),('SiO2-DCD@COT','22.4','300.33','36.07'),('SiO2-LPU@COT','29.5','264.0','45.45')]);self.assertEqual(d[0]['residue_temp_C'],'700')
  for r in d[1:]:self.assertFalse(r['residue_temp_C']);self.assertFalse(r.get('R700_pct'))
 def test_derived_assay_metadata_and_unknown_residue_temperature(self):
  m,_,_,_=build_tables(pd.DataFrame(rows('boron2023')))
  for r in m.to_dict('records'):
   self.assertEqual(r['material_form_TGA'],r['material_form_LOI']);self.assertEqual(r['source_material_form_TGA_raw'],'treated cotton fabric aliquot');self.assertIn('120C',r['TG_prehold']);self.assertTrue(pd.isna(r.get('residue_temp_C')) or not str(r.get('residue_temp_C','')).strip())
 def test_seven_states_nine_conditions(self):
  d=pd.DataFrame(rows('boron2023')+rows('lpu2025'));m,_,_,v=build_tables(d);self.assertEqual(len(m),9);self.assertEqual(v['verified_exact_sample_states'],7);self.assertFalse(numeric_errors(d))
 def test_holds_preserve_conflicts_and_prior_screening(self):
  h=(R/'data/curation/source_review_holds_20260930_b70.json').read_text();self.assertIn('31.9',h);self.assertIn('15 min',h);self.assertIn('polym15051183',h);self.assertIn('d5ra00402k',h)
