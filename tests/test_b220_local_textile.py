"""Protect source-specific scientific exclusions and sample correspondence."""
import csv
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/'data/incoming/verified_source_batch_20261004_b220_local_textile.csv'
if not FILE.exists():FILE=Path(__file__).resolve().parent/'staged-local-textile-b220/publication_proposed.csv'
class PLANonwovenSourceEvidenceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with FILE.open()as source:cls.rows=list(csv.DictReader(source))
  cls.by_label={r['source_sample_label']:r for r in cls.rows}
 def test_only_two_native_numeric_LOI_pairs_are_admitted(self):
  self.assertEqual(set(self.by_label),{'PLA','PLA/6%TPA','PLA/11%TPA','PLA/23%TPA'})
  for label,loi in [('PLA','18.0'),('PLA/23%TPA','26.5')]:
   r=self.by_label[label];self.assertEqual((r['LOI_pct'],r['pairing_status'],r['direct_numeric_use']),(loi,'verified_exact','yes'))
  for label in ['PLA/6%TPA','PLA/11%TPA']:
   r=self.by_label[label];self.assertFalse(r['LOI_pct']);self.assertEqual(r['direct_numeric_use'],'no');self.assertIn('noimageestimate',r['source_hold_reason'])
 def test_experimental_and_calculated_residue_remain_distinct(self):
  r=self.by_label['PLA/23%TPA'];self.assertEqual((r['R800_pct'],r['residue_pct'],r['residue_temp_C'],r['source_calculated_char_800C_pct']),('11.6','11.6','800','8.4'))
  self.assertEqual(self.by_label['PLA']['R800_pct'],'1.8')
 def test_T50_and_DTG_rate_do_not_replace_T5_or_Tmax(self):
  r=self.by_label['PLA/23%TPA'];self.assertEqual((r['T5_C'],r['source_T50_C'],r['Tmax1_C'],r['source_DTGmax_pct_per_C']),('250.8','382.4','390.9','1.6'))
  for r in self.rows:self.assertFalse(any(r.get(k)for k in ['T10_C','Tonset_C','Tmax2_C']))
 def test_23percent_is_weightgain_not_final_fraction(self):
  r=self.by_label['PLA/23%TPA'];self.assertEqual(r['source_TPA_weight_gain_pct'],'23');self.assertIn('notfinalTPAmassfraction',r['composition']);self.assertIn('15wtpercentbath',r['treatment_method'])
 def test_same_initial_nonwoven_and_assay_specific_conditions(self):
  for r in self.rows:
   self.assertEqual((r['material_form_TGA'],r['material_form_LOI'],r['washing_state']),('PLA nonwoven fabric','PLA nonwoven fabric','initial_unlaundered'))
   self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['TGA_gas_flow_ml_min']),('N2','10','60'));self.assertEqual(r['LOI_standard'],'ASTM D2863-2000');self.assertIn('5parallel',r['source_LOI_replicates']);self.assertIn('approximate',r['source_TGA_mass_qualifier'])
if __name__=='__main__':unittest.main()
