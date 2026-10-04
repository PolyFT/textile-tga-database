"""Protect missing-TG dose states and non-textile/assay boundaries."""
import csv,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/'data/incoming/verified_source_batch_20261005_b240_local_textile.csv'
if not FILE.exists():FILE=Path(__file__).resolve().parent/'staged-local-textile-b240/publication_proposed.csv'
class AramidCompositeTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with FILE.open()as f:cls.rows={int(r['source_sample_label'].split('-')[1]):r for r in csv.DictReader(f)}
 def test_other_doses_never_borrow_numeric_TG(self):
  self.assertEqual({i for i,r in self.rows.items()if r['pairing_status']=='verified_exact'},{3,7,8})
  for i in [4,5,6,9,10]:
   r=self.rows[i];self.assertEqual(r['direct_numeric_use'],'no');self.assertTrue(r['LOI_pct']);self.assertFalse(r['T5_C']);self.assertFalse(r['Tmax1_C']);self.assertFalse(r['R800_pct']);self.assertFalse(r['atmosphere'])
 def test_fiber_free_comparators_and_intro_fiber_claim_are_excluded(self):
  for i in [1,2]:
   r=self.rows[i];self.assertEqual(r['pairing_status'],'outside_textile_fiber_free_comparator');self.assertEqual(r['direct_numeric_use'],'no');self.assertIn('fiber-free',r['material_form']);self.assertIn('zeroAF',r['source_fiber_preparation'])
 def test_rate_residual_mass_and_assay_conditions_remain_distinct(self):
  r=self.rows[7];self.assertEqual((r['Tmax1_C'],r['source_maximum_mass_loss_rate_pct_min']),('471','1.21'));self.assertEqual((r['R800_pct'],r['source_residual_mass_350C_pct']),('28.0','95.8'))
  for i in [3,7,8]:
   r=self.rows[i];self.assertIn('unitdiscrepancypreserved',r['source_composite_preparation']);self.assertIn('Table1reportedwtpercent',r['composition']);self.assertEqual(r['LOI_standard'],'GB/T 10707');self.assertIn('100x10x4mm',r['source_LOI_geometry']);self.assertFalse(r.get('TG_start_C'));self.assertFalse(r.get('T10_C'));self.assertFalse(r.get('Tonset_C'));self.assertEqual(r['residue_temp_C'],'800')
if __name__=='__main__':unittest.main()
