"""Protect the ordinary TG evidence against furnace and cone substitutions."""
import csv
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/'data/incoming/verified_source_batch_20261004_b225_local_textile.csv'
if not FILE.exists():FILE=Path(__file__).resolve().parent/'staged-local-textile-b225/publication_proposed.csv'
class CalciumAlginateSourceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with FILE.open()as source:cls.rows=list(csv.DictReader(source))
  cls.cal,cls.vis=cls.rows
 def test_explicit_R900_is_paired_with_Ca_LOI34(self):
  r=self.cal;self.assertEqual((r['LOI_pct'],r['residue_pct'],r['residue_temp_C'],r['atmosphere'],r['heating_rate_C_min']),('34','12.5','900','air','10'));self.assertIn('p809',r['TG_locator']);self.assertEqual(r['material_form_TGA'],r['material_form_LOI'])
 def test_furnace_and_water_do_not_supply_TG_metrics_or_range(self):
  self.assertFalse(any(self.cal.get(k)for k in ['T5_C','T10_C','Tonset_C','Tmax1_C','Tmax2_C','TG_start_C','TG_end_C','TGA_sample_mass_mg','TGA_gas_flow_ml_min']));self.assertIn('tube-furnace',self.cal['source_metric_definition'])
 def test_viscose_LOI17_and_cone9_remain_unpaired(self):
  self.assertEqual((self.vis['LOI_pct'],self.vis['source_Cone_residue_pct'],self.vis['direct_numeric_use']),('17','9','no'));self.assertFalse(any(self.vis.get(k)for k in ['residue_pct','residue_temp_C','Tmax1_C','Tmax2_C','heating_rate_C_min','atmosphere']));self.assertEqual(self.cal['source_Cone_residue_pct'],'25')
 def test_LOI_conditions_are_not_cone_conditions(self):
  self.assertEqual(self.cal['LOI_standard'],'GB/T 5454-1997');self.assertIn('triplicatenotLOI',self.cal['source_LOI_unreported_conditions']);self.assertIn('retainedCaquantityunreported',self.cal['composition'])
if __name__=='__main__':unittest.main()
