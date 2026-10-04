"""Protect the source-specific endpoint, fiber-state mapping and missing peaks."""
import csv
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/'data/incoming/verified_source_batch_20261004_b219_local_textile.csv'
if not FILE.exists():FILE=Path(__file__).resolve().parent/'staged-local-textile-b219/publication_proposed.csv'
class AlginateSourceEvidenceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with FILE.open() as source:cls.rows=list(csv.DictReader(source))
  cls.by_label={r['source_sample_label']:r for r in cls.rows}
 def test_every_formulation_uses_own_LOI_and_explicit_R800(self):
  expected={'Alginic acid fiber':('24.5','22.7'),'1#Alg-Zn':('30.0','25.0'),'2#Alg-Zn':('31.0','24.8'),'3#Alg-Zn':('32.4','26.0'),'4#Alg-Zn':('35.0','28.7')}
  self.assertEqual(set(self.by_label),set(expected))
  for label,(loi,residue) in expected.items():
   r=self.by_label[label];self.assertEqual((r['LOI_pct'],r['R800_pct'],r['residue_pct'],r['residue_temp_C']),(loi,residue,residue,'800'));self.assertIn('p770',r['TG_locator'])
 def test_group_DTG_and_water_are_not_individual_peaks(self):
  for r in self.rows:
   self.assertFalse(any(r.get(k)for k in ['T5_C','T10_C','Tonset_C','Tmax1_C','Tmax2_C']));self.assertIn('GenericDTG210and250',r['source_metric_definition'])
 def test_ordinary_conditions_are_not_cone_conditions(self):
  for r in self.rows:
   self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['TGA_sample_mass_mg'],r['TGA_gas_flow_ml_min'],r['TG_start_C']),('N2','10','3','50',''));self.assertIn('CONEonly',r['source_LOI_standard_replicates_conditioning'])
 def test_bath_and_retained_ions_have_distinct_bases(self):
  r=self.by_label['2#Alg-Zn'];self.assertEqual((r['source_ZnSO4_7H2O_bath_wt_pct'],r['source_Zn_content_wt_pct'],r['source_Ca_content_wt_pct']),('8.0','2.85','0.077'))
  for r in self.rows:self.assertEqual((r['material_form_TGA'],r['material_form_LOI'],r['washing_state']),('alginate fiber','alginate fiber','initial_unlaundered'))
if __name__=='__main__':unittest.main()
