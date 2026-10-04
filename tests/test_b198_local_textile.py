"""Reject guessed Ti thresholds, conflicting control peak and cloned laundering TG."""
import csv,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if not(ROOT/'scripts/pairing.py').exists():ROOT=ROOT/'repo'
sys.path.insert(0,str(ROOT/'scripts'));import pairing
PUBLIC=ROOT/'data/incoming/verified_source_batch_20261004_b198_local_textile.csv'
PRIVATE=ROOT.parent/'work/staged-local-textile-b198/publication_proposed.csv'
class AHTTPAPreproofFacts(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with(PUBLIC if PUBLIC.exists()else PRIVATE).open(newline='')as f:cls.rows=list(csv.DictReader(f));cls.accepted=cls.rows[:4]
 def test_two_initial_states_four_test_records(self):
  self.assertEqual(len({r['sample_state']for r in self.accepted}),2);self.assertEqual([r['atmosphere']for r in self.accepted],['N2','N2','air','air']);self.assertEqual([r['LOI_pct']for r in self.accepted],['18.0','39.6']*2)
 def test_conflicting_control_peak_is_raw_only(self):
  r=self.accepted[0];self.assertFalse(r['Tmax1_C']);self.assertEqual((r['source_native_Tmax_Table3_C'],r['source_native_Tmax_prose_C']),('397','98'));self.assertEqual(r['R700_pct'],'16.88')
 def test_undefined_Ti_not_onset_T5_or_T10(self):
  self.assertEqual([r['source_Ti_initial_decomposition_C']for r in self.accepted],['308','244','297','241'])
  for r in self.rows:self.assertFalse(any(r.get(k)for k in ['T5_C','T10_C','Tonset_C']))
 def test_char_endpoint_not_cone_residue(self):
  self.assertEqual([r['R700_pct']for r in self.accepted],['16.88','37.03','1.97','9.76'])
  for r in self.accepted:self.assertEqual(r['residue_temp_C'],'700');self.assertEqual(r['residue_pct'],r['R700_pct'])
 def test_unknown_initialdose_and_wash_TG_not_borrowed(self):
  for r in self.rows[4:]:self.assertEqual(r['direct_numeric_use'],'no');self.assertFalse(any(r.get(k)for k in pairing.TG_FIELDS))
  self.assertEqual([r['LOI_pct']for r in self.rows[4:]],['','','26.8','28.4','29.8'])
 def test_ordinary_conditions_and_geometry(self):
  for r in self.accepted:self.assertEqual((r['heating_rate_C_min'],r['TG_start_C'],r['TG_end_C'],r['source_TG_mass_mg']),('20','40','700','5-8'));self.assertEqual(r['source_LOI_dimensions_mm'],'140x50');self.assertFalse(r.get('gas_flow_mL_min'));self.assertFalse(r.get('LOI_replicates'))
 def test_preproof_not_claimed_final_edition(self):
  for r in self.accepted:self.assertTrue(r['source_version'].startswith('PublisherJournalPre-proof'));self.assertIn('notdefinitiveversion',r['source_version']);self.assertIn('cover2018placeholder',r['source_version']);self.assertEqual(r['year'],'2020')
 def test_binding_rejects_guessed_threshold_or_washed_LOI(self):
  for r in self.accepted:
   self.assertFalse(pairing.evidence_issues(r))
   for k,v in [('LOI_pct','29.8'),('Tonset_C','244'),('residue_temp_C','800'),('washing_state','50_laundering_cycles')]:self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**{k:v})))
if __name__=='__main__':unittest.main()
