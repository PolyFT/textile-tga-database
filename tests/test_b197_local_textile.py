"""Protect gas-specific thresholds, unresolved loading and assay conditions."""
import csv,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if not(ROOT/'scripts/pairing.py').exists():ROOT=ROOT/'repo'
sys.path.insert(0,str(ROOT/'scripts'));import pairing
PUBLIC=ROOT/'data/incoming/verified_source_batch_20261004_b197_local_textile.csv'
PRIVATE=ROOT.parent/'work/staged-local-textile-b197/publication_proposed.csv'
class SolGelCottonFacts(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with(PUBLIC if PUBLIC.exists()else PRIVATE).open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def test_three_states_six_test_records(self):
  self.assertEqual(len(self.rows),6);self.assertEqual(len({r['sample_state']for r in self.rows}),3);self.assertEqual([r['LOI_pct']for r in self.rows],['19','23','29']*2)
 def test_T5_N2_and_T10_air_are_distinct(self):
  for r in self.rows:
   if r['atmosphere']=='air':self.assertFalse(r['T5_C']);self.assertTrue(r['T10_C']);self.assertTrue(r['Tmax2_C'])
   else:self.assertTrue(r['T5_C']);self.assertFalse(r['T10_C']);self.assertFalse(r['Tmax2_C'])
   self.assertFalse(r.get('Tonset_C'))
 def test_endpoint_residue_not_cone_char(self):
  self.assertEqual([r['R800_pct']for r in self.rows],['13','23','36','0','7.8','9.3'])
  for r in self.rows:self.assertEqual(r['residue_pct'],r['R800_pct']);self.assertEqual(r['residue_temp_C'],'800')
 def test_unknown_air_scan_flow_mass_not_borrowed(self):
  for r in self.rows:
   self.assertFalse(r.get('gas_flow_mL_min'));self.assertFalse(r.get('source_TG_mass_mg'))
   if r['atmosphere']=='air':self.assertFalse(r['TG_start_C']);self.assertFalse(r['TG_end_C'])
   else:self.assertEqual((r['TG_start_C'],r['TG_end_C']),('35','800'))
 def test_FR2_loading_conflict_kept_without_choosing(self):
  for r in self.rows:
   if r['source_sample_label']=='FR-2':self.assertFalse(r['weight_gain_pct']);self.assertEqual((r['source_weight_gain_preparation_wt_pct'],r['source_weight_gain_conclusion_wt_pct']),('9.5','9.3'))
 def test_LOI_plusminus_not_assumedSD(self):
  self.assertEqual([r['LOI_reported_plus_minus']for r in self.rows],['0.1','0.2','0.1']*2)
  for r in self.rows:self.assertIn('Unreported',r['LOI_uncertainty_type']);self.assertFalse(r.get('LOI_replicates'));self.assertEqual(r['source_LOI_dimensions_mm'],'150x58')
 def test_DTGrates_native_pct_per_C_not_per_min(self):
  self.assertEqual([r['source_max_mass_loss_rate_pct_per_C']for r in self.rows[:3]],['1.7','1.6','1.5']);self.assertEqual([r['source_max_mass_loss_rate1_pct_per_C']for r in self.rows[3:]],['1.59','1.05','0.94'])
 def test_binding_rejects_condition_or_durability_edits(self):
  for r in self.rows:
   self.assertFalse(pairing.evidence_issues(r))
   for k,v in [('LOI_pct','49.2'),('residue_temp_C','600'),('sample_state','FR-2_50LC')]:self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**{k:v})))
if __name__=='__main__':unittest.main()
