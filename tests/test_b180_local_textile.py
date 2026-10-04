"""Protect ordinary PAN measurements and unknown residue endpoint exclusions."""
import csv,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if not(ROOT/'scripts/pairing.py').exists():ROOT=ROOT/'repo'
sys.path.insert(0,str(ROOT/'scripts'));import pairing
PUBLIC=ROOT/'data/incoming/verified_source_batch_20261004_b180_local_textile.csv'
PRIVATE=ROOT.parent/'work/staged-local-textile-b180/publication_proposed.csv'
class SourceFacts(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with(PUBLIC if PUBLIC.exists()else PRIVATE).open(newline='')as f:cls.rows=list(csv.DictReader(f))
  cls.control=next(r for r in cls.rows if r['source_sample_label']=='PAN')
  cls.hybrid=next(r for r in cls.rows if r['source_sample_label']=='Co-Zn ZIF/MoS2/PAN')
 def test_onlyfour_own_formulations(self):self.assertEqual(len(self.rows),4);self.assertEqual(len({r['sample_state']for r in self.rows}),4)
 def test_exact_control_threshold_peaks(self):self.assertEqual(tuple(self.control[k]for k in ['T5_C','Tmax1_C','Tmax2_C']),('316.3','327','441.3'))
 def test_hybrid_tabulated_values_not_adjusted(self):self.assertEqual(tuple(self.hybrid[k]for k in ['T5_C','Tmax1_C','Tmax2_C']),('344.9','344.3','461'))
 def test_original_four_LOI_values(self):self.assertEqual([r['LOI_pct']for r in self.rows],['17.8','20.3','22.8','26.2'])
 def test_allfour_raw_chars_auxiliary(self):self.assertEqual([r['source_unbound_residual_mass_pct']for r in self.rows],['44.6','48.2','49.5','50.9'])
 def test_no_inferred_R800(self):self.assertTrue(all(not any(r.get(k)for k in ['R800_pct','residue_pct','residue_temp_C','source_unbound_residual_mass_temperature_C'])for r in self.rows))
 def test_ordinary_N2_20_not_muffle(self):self.assertTrue(all((r['atmosphere'],r['heating_rate_C_min'],r['TG_start_C'],r['TG_end_C'])==('N2','20','50','800')for r in self.rows))
 def test_ordinary_mass_not_TGIRmass(self):self.assertTrue(all(not r.get('source_TGA_sample_mass_mg')and'unreported'in r['source_TGA_mass_flow_repetitions']for r in self.rows))
 def test_no_Tonset_from_onset_T5_wording(self):self.assertTrue(all(not r.get('Tonset_C')and not r.get('T10_C')for r in self.rows))
 def test_same_initial_fiber_form(self):self.assertTrue(all(r['washing_state']=='initial'and r['material_form_TGA']==r['material_form_LOI']for r in self.rows))
 def test_actual_TG_tableS3_locator(self):self.assertTrue(all('TableS3'in r['TG_locator']for r in self.rows))
 def test_copolymer_identity_and_loading_basis(self):self.assertTrue(all('methylacrylate/sodium p-styrenesulfonate'in r['composition']for r in self.rows));self.assertEqual([r['source_loading_pct']for r in self.rows],['0','2','2','2'])
 def test_review_fingerprints_bound(self):self.assertTrue(all(not pairing.evidence_issues(r)for r in self.rows))
 def test_false_endpoint_invalidates_review(self):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(self.hybrid,R800_pct='50.9')))
 def test_muffle_program_invalidates_review(self):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(self.control,atmosphere='air',heating_rate_C_min='3')))
 def test_changed_wash_invalidates_review(self):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(self.hybrid,washing_state='after20washes')))
if __name__=='__main__':unittest.main()
