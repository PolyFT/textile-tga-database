"""Protect native S6 profiles, source conflicts and unchanged-state correspondence."""
import csv,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if not(ROOT/'scripts/pairing.py').exists():ROOT=ROOT/'repo'
sys.path.insert(0,str(ROOT/'scripts'));import pairing
PUBLIC=ROOT/'data/incoming/verified_source_batch_20261004_b187_local_textile.csv'
PRIVATE=ROOT.parent/'work/staged-local-textile-b187/publication_proposed.csv'
class NativeAAPPFacts(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with(PUBLIC if PUBLIC.exists()else PRIVATE).open(newline='')as f:cls.rows=list(csv.DictReader(f));cls.accepted=[r for r in cls.rows if r['pairing_status']=='verified_exact']
 def test_onlyone_initial_ownfiber_pair(self):self.assertEqual(len(self.rows),12);self.assertEqual(len(self.accepted),1);self.assertEqual(self.accepted[0]['source_sample_label'],'15%-AAPP/lyocell fibers');self.assertTrue(self.accepted[0]['washing_state'].startswith('initial_'))
 def test_native_complete_S6_profile(self):
  r=self.accepted[0];self.assertEqual(tuple(r[k]for k in ['T5_C','T50_C','Tmax1_C','R600_pct','residue_temp_C','LOI_pct']),('242.00','372.83','275.66','16.29','600','39'));self.assertFalse(r['Tonset_C']);self.assertEqual(r['source_DTG_max_rate_pct_per_C'],'1.73')
 def test_control_temperature_rate_conflicts_wholeheld(self):
  r=self.rows[0];self.assertEqual((r['source_SI_Tmax_C'],r['source_body_Tmax_C'],r['source_SI_DTG_rate_pct_per_C'],r['source_body_DTG_rate_pct_per_C']),('327.88','372.8','2.95','2.93'));self.assertFalse(r['Tmax1_C']);self.assertEqual(r['direct_numeric_use'],'no')
 def test_otherdose_and_washed_TG_not_borrowed(self):
  for r in self.rows[1:]:
   if r in self.accepted:continue
   with self.subTest(state=r['sample_state']):self.assertFalse(any(r.get(k)for k in pairing.TG_FIELDS));self.assertFalse(r.get('residue_temp_C'));self.assertEqual(r['direct_numeric_use'],'no')
 def test_conflicting_dose_and_wash_LOI_retained(self):
  self.assertEqual((self.rows[4]['LOI_pct'],self.rows[4]['source_SI_initial_LOI_pct']),('44','45'));self.assertEqual((self.rows[5]['LOI_pct'],self.rows[5]['source_SI_initial_LOI_pct']),('45','46'));self.assertEqual((self.rows[6]['LOI_pct'],self.rows[6]['source_SI_washed_LOI_pct']),('32','35'))
 def test_retained_addon_and_ordinary_method_scope(self):
  r=self.accepted[0];self.assertEqual((r['source_finishing_bath_concentration_pct'],r['source_retained_AAPP_content_pct']),('15','15.18'));self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['TG_start_C'],r['TG_end_C'],r['TGA_instrument']),('N2','10','30','600','Rigaku TG-DTA8122'));self.assertIn('Unreported',r['source_LOI_assembly_mass_dimensions_repetitions'])
 def test_review_binding_rejects_changed_endpoint_or_wash_LOI(self):
  r=self.accepted[0];self.assertFalse(pairing.evidence_issues(r));self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,residue_temp_C='800')));self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,LOI_pct='35')))
if __name__=='__main__':unittest.main()
