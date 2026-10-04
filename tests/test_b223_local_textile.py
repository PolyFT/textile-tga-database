"""Protect decomposition/water distinction and the explicit 900C residue endpoint."""
import csv
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/'data/incoming/verified_source_batch_20261004_b223_local_textile.csv'
if not FILE.exists():FILE=Path(__file__).resolve().parent/'staged-local-textile-b223/publication_proposed.csv'
class MetalAlginateSourceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with FILE.open()as source:cls.rows=list(csv.DictReader(source))
  cls.by_state={r['sample_state']:r for r in cls.rows}
 def test_own_LOI_and_two_DTG_maxima_are_paired(self):
  expected={'Alginate_acid_initial':('24','250','459'),'Alginate_Ba_initial':('45','254','662'),'Alginate_Cu_initial':('30','248','356'),'Alginate_Zn_initial':('42','238','423')}
  self.assertEqual(set(self.by_state),set(expected))
  for state,values in expected.items():
   r=self.by_state[state];self.assertEqual((r['LOI_pct'],r['Tmax1_C'],r['Tmax2_C']),values)
 def test_water_threshold_is_not_decomposition_onset(self):
  for r in self.rows:
   self.assertFalse(any(r.get(k)for k in ['T5_C','T10_C','Tonset_C']));self.assertLess(float(r['source_water_region_5pct_loss_C']),170);self.assertIn('prosemislabels',r['source_metric_definition'])
 def test_residue900_is_not_assumed_at_other_temperatures(self):
  expected={'Alginate_acid_initial':'0.63','Alginate_Ba_initial':'34.2','Alginate_Cu_initial':'16.1','Alginate_Zn_initial':'16.2'}
  for state,residue in expected.items():
   r=self.by_state[state];self.assertEqual((r['residue_pct'],r['residue_temp_C']),(residue,'900'));self.assertFalse(any(r.get(k)for k in ['R600_pct','R700_pct','R800_pct']))
 def test_air_ordinaryTG_is_separate_from_PyGC_and_cone(self):
  for r in self.rows:
   self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['TGA_sample_mass_mg'],r['source_TGA_pan'],r['TG_start_C']),('air','10','5','platinum crucible',''));self.assertIn('35kWm2',r['source_Cone_conflict']);self.assertFalse(r.get('TGA_gas_flow_ml_min'));self.assertEqual(r['material_form_TGA'],r['material_form_LOI'])
if __name__=='__main__':unittest.main()
