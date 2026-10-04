"""Protect decomposition definitions, unknown assay standard and unmatched graft doses."""
import csv,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/'data/incoming/verified_source_batch_20261005_b243_local_textile.csv'
if not FILE.exists():FILE=Path(__file__).resolve().parent/'staged-local-textile-b243/publication_proposed.csv'
class PANFabricTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with FILE.open()as f:cls.rows={r['source_sample_label']:r for r in csv.DictReader(f)}
 def test_water_DSC_and_stage_bounds_never_become_canonical_peaks(self):
  a=self.rows['PAN'];b=self.rows['FR-PAN-g-HEMA23'];self.assertEqual(a['Tonset_C'],'298.60');self.assertFalse(b['Tonset_C']);self.assertEqual(b['R800_pct'],'40.55');self.assertEqual(b['residue_temp_C'],'800')
  for r in self.rows.values():self.assertFalse(r.get('T5_C'));self.assertFalse(r.get('T10_C'));self.assertFalse(r.get('Tmax1_C'));self.assertFalse(r.get('TG_start_C'));self.assertEqual(r['TG_end_C'],'800')
 def test_wrong_standard_is_retained_without_inventing_replacement(self):
  for r in self.rows.values():self.assertFalse(r.get('LOI_standard'));self.assertEqual(r['source_reported_LOI_standard'],'ASTM D6413-08');self.assertIn('actualLOIstandardunverified',r['source_LOI_standard_anomaly'])
 def test_graft_doses_and_generic_residue_do_not_borrow_FR_LOI(self):
  self.assertEqual({k for k,r in self.rows.items()if r['pairing_status']=='verified_exact'},{'PAN','FR-PAN-g-HEMA23'})
  for k in ['PAN-g-HEMA23','PAN-g-HEMA49','PAN-g-HEMA74']:self.assertFalse(self.rows[k]['LOI_pct']);self.assertFalse(self.rows[k]['R800_pct']);self.assertEqual(self.rows[k]['direct_numeric_use'],'no')
  r=self.rows['PAN-g-HEMA_concentration_unbound'];self.assertEqual(r['R800_pct'],'28.9');self.assertFalse(r['LOI_pct']);self.assertEqual(r['direct_numeric_use'],'no')
if __name__=='__main__':unittest.main()
