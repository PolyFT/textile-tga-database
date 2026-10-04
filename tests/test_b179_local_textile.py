"""Protect native PAN source-state/method identity and review binding."""
import csv,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if not(ROOT/'scripts/pairing.py').exists():ROOT=ROOT/'repo'
sys.path.insert(0,str(ROOT/'scripts'));import pairing
PUBLIC=ROOT/'data/incoming/verified_source_batch_20261004_b179_local_textile.csv'
PRIVATE=ROOT.parent/'work/staged-local-textile-b179/publication_proposed.csv'
class SourceFacts(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with(PUBLIC if PUBLIC.exists()else PRIVATE).open(newline='')as f:cls.rows=list(csv.DictReader(f))
  cls.control=next(r for r in cls.rows if r['source_sample_label']=='PAN')
  cls.hybrid=next(r for r in cls.rows if r['source_sample_label']=='2wt% TA-MoS2/PAN')
 def test_allfive_unique_initialstates(self):self.assertEqual(len(self.rows),5);self.assertEqual(len({r['sample_state']for r in self.rows}),5);self.assertTrue(all(r['washing_state']=='initial'for r in self.rows))
 def test_control_T5_two_peaks_char(self):self.assertEqual(tuple(self.control[k]for k in ['T5_C','Tmax1_C','Tmax2_C','R800_pct']),('315.9','325.8','443.4','42.8'))
 def test_final_hybrid_exact_profile(self):self.assertEqual(tuple(self.hybrid[k]for k in ['T5_C','Tmax1_C','Tmax2_C','R800_pct','LOI_pct']),('330.4','333.2','444.7','49.7','26.0'))
 def test_all_original_LOI_labels(self):self.assertEqual([r['LOI_pct']for r in self.rows],['17.8','19.1','21.3','23.1','26.0'])
 def test_halfpercent_presentation_not_two_samples(self):self.assertEqual(sum(r['source_loading_pct']=='0.5'for r in self.rows),1)
 def test_ordinaryTG_not_TGIRprogram(self):self.assertTrue(all((r['atmosphere'],r['heating_rate_C_min'],r['TG_start_C'],r['TG_end_C'])==('N2','10','50','800')for r in self.rows))
 def test_unknownordinarymass_not_TGIR5mg(self):self.assertTrue(all('unreported'in r['source_TGA_mass_flow_repetitions']and not r.get('source_TGA_sample_mass_mg')for r in self.rows))
 def test_explicitR800_not_conechar(self):self.assertTrue(all(r['residue_pct']==r['R800_pct']and r['residue_temp_C']=='800'for r in self.rows));self.assertNotIn(self.hybrid['R800_pct'],['21','14','10'])
 def test_same_fiberform_both_tests(self):self.assertTrue(all(r['material_form_TGA']==r['material_form_LOI']and 'wet-spun'in r['material_form']for r in self.rows))
 def test_no_inferred_T10_Tonset(self):self.assertTrue(all(not r.get('T10_C')and not r.get('Tonset_C')for r in self.rows))
 def test_articleinpress_finalyear_unknown(self):self.assertTrue(all(r['year']==''and'placeholder'in r['source_document_version']for r in self.rows))
 def test_fingerprint_binds_original_measurements(self):self.assertTrue(all(not pairing.evidence_issues(r)for r in self.rows))
 def test_wrong_TGIRramp_invalidates_review(self):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(self.control,heating_rate_C_min='20')))
 def test_changed_wash_invalidates_review(self):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(self.hybrid,washing_state='after20washes')))
 def test_changed_form_invalidates_review(self):self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(self.hybrid,material_form_LOI='polyacrylonitrile fabric')))
if __name__=='__main__':unittest.main()
