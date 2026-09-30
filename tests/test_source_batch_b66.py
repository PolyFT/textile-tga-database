"""Preserve source-specific BC preparations, residue temperatures and state counts."""
import csv,hashlib,json,unittest
from pathlib import Path
import pandas as pd
from scripts.pairing import evidence_issues,measurement_fingerprint
from scripts.validate_tg_loi import build_tables,numeric_errors
R=Path(__file__).resolve().parents[1];M=R/'data/curation/source_review_manifest_20260930_b66.json'
def rows(tag):
 f=next(x['file'] for x in json.loads(M.read_text())['files'] if x['file'].endswith('_'+tag+'.csv'));return list(csv.DictReader((R/f).open()))
class Batch66(unittest.TestCase):
 def test_fingerprints_and_input_hashes(self):
  for f in json.loads(M.read_text())['files']:
   self.assertEqual(hashlib.sha256((R/f['file']).read_bytes()).hexdigest(),f['published_input_sha256'])
   for r in csv.DictReader((R/f['file']).open()):self.assertFalse(evidence_issues(r));self.assertEqual(measurement_fingerprint(r),r['reviewed_measurement_fingerprint'])
 def test_plants_exact_pairs_and_atmospheres(self):
  self.assertEqual([(r['sample_state'],r['atmosphere'],r['LOI_pct'],r['R800_pct']) for r in rows('bc_plants')],[('OBC','nitrogen','20','4.590'),('OBC','air','20','0.845'),('SMN-BC','nitrogen','36','30.933'),('BP-BC','nitrogen','40','32.740'),('BP-BC','air','40','14.947'),('BT-BC','nitrogen','44','33.864'),('BT-BC','air','44','2.515')])
 def test_protein_residue_temperature(self):
  self.assertEqual([(r['LOI_pct'],r['residue_pct']) for r in rows('bc_proteins')],[('25','29.890'),('50','17.048')])
  for r in rows('bc_proteins')+rows('bc_marine'):
   self.assertEqual(r['residue_temp_C'],'1000');self.assertFalse(r.get('R800_pct'));self.assertEqual(r['gas_flow_mL_min'],'60')
 def test_marine_final_crosslinked_states(self):
  self.assertEqual([(r['sample_state'],r['LOI_pct'],r['residue_pct']) for r in rows('bc_marine')],[('BC-AN-EC','29','43.875'),('BC-MU-EC','30','47.311'),('BC-SH-EC','31','49.489')])
  for r in rows('bc_marine'):
   self.assertIn('crosslinker:catalyst molar ratio 1:1',r['treatment_method']);self.assertIn('160 C for 5 min',r['treatment_method'])
 def test_nine_states_twelve_conditions(self):
  d=pd.DataFrame(rows('bc_plants')+rows('bc_proteins')+rows('bc_marine'));m,_,_,v=build_tables(d);self.assertEqual(len(m),12);self.assertEqual(v['verified_exact_sample_states'],9);self.assertFalse(numeric_errors(d))
 def test_sheet_form_and_assay_preparations_survive_derivation(self):
  m,_,_,_=build_tables(pd.DataFrame(rows('bc_proteins')+rows('bc_marine')))
  for r in m.to_dict('records'):
   self.assertEqual(r['material_form'],'bacterial cellulose nanofibrous sheet textile');self.assertIn('not reported',r['TGA_specimen_preparation']);self.assertIn('mm',r['LOI_specimen_preparation']);self.assertIn('initial',r['washing_state'])
 def test_whole_paper_holds_are_retained(self):
  h=json.dumps(json.loads((R/'data/curation/source_review_holds_20260930_b66.json').read_text()));self.assertIn('SP-BC',h);self.assertIn('pH8',h);self.assertIn('dose',h);self.assertIn('control',h);self.assertIn('entrapment-only',h)
