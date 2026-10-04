"""Protect washing correspondence, heating-rate counts and assay-specific evidence."""
import csv
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/'data/incoming/verified_source_batch_20261004_b224_local_textile.csv'
if not FILE.exists():FILE=Path(__file__).resolve().parent/'staged-local-textile-b224/publication_proposed.csv'
class CottonLotusSourceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with FILE.open()as source:cls.rows=list(csv.DictReader(source))
  cls.approved=[r for r in cls.rows if r['pairing_status']=='verified_exact']
 def test_two_rates_do_not_create_new_sample_states(self):
  self.assertEqual(len(self.approved),6);self.assertEqual(len({(r['sample_state'],r['washing_state'])for r in self.approved}),4)
  for label in ['CO(OP)','CO(FAS?OP)']:
   initial=[r for r in self.approved if r['source_sample_label']==label and r['source_washing_cycles']=='0'];self.assertEqual({r['heating_rate_C_min']for r in initial},{'2','10'});self.assertEqual({r['LOI_pct']for r in initial},{'34'})
 def test_washed_LOI_not_borrowed_from_initial_or_neighbor(self):
  for label,loi in [('CO(OP)','28'),('CO(FAS?OP)','25')]:
   r=next(r for r in self.approved if r['source_sample_label']==label and r['source_washing_cycles']=='10');self.assertEqual((r['LOI_pct'],r['heating_rate_C_min'],r['washing_state']),(loi,'10','washed_10_cycles'));self.assertIn('190C10s',r['treatment_method'])
  for r in self.rows:
   if r.get('source_washing_cycles')in ['1','5']:self.assertFalse(r['LOI_pct']);self.assertEqual(r['direct_numeric_use'],'no')
 def test_measured700_residue_is_not_peak_bound_residue(self):
  r=next(r for r in self.approved if r['source_sample_label']=='CO(OP)'and r['heating_rate_C_min']=='2');self.assertEqual((r['Tonset_C'],r['Tmax1_C'],r['R700_pct'],r['residue_temp_C'],r['source_residue_at_Tmax1_pct']),('262.2','283.2','40.0','700','76.8'))
  for r in self.approved:self.assertFalse(any(r.get(k)for k in ['T5_C','T10_C','R800_pct']))
 def test_single_stage_at2Cmin_does_not_copy_second_peak(self):
  for r in self.approved:
   if r['heating_rate_C_min']=='2':self.assertFalse(r['Tmax2_C']);self.assertFalse(r['source_residue_at_Tmax2_pct'])
   else:self.assertTrue(r['Tmax2_C'])
 def test_unbound_baseline_and_OPonly_recipe_stay_held(self):
  for r in self.rows:
   if r['source_sample_label']in ['CO(UN)','CO(FAS)']:self.assertFalse(r['LOI_pct']);self.assertEqual(r['direct_numeric_use'],'no');self.assertEqual(r['source_unbound_baseline_LOI_pct'],'19')
  rb=next(r for r in self.rows if r['source_sample_label']=='CO(OP-RB)');self.assertFalse(any(rb.get(k)for k in ['LOI_pct','Tonset_C','Tmax1_C','Tmax2_C','R700_pct','atmosphere','heating_rate_C_min']));self.assertIn('withoutMR_H3PO4',rb['composition'])
 def test_LOI_n2_and_staticair_conditions_are_assay_specific(self):
  for r in self.approved:
   self.assertEqual((r['atmosphere'],r['TGA_sample_mass_mg'],r['TG_start_C'],r['TG_end_C']),('air','1','','700'));self.assertIn('static air',r['source_TGA_gas_mode']);self.assertFalse(r.get('TGA_gas_flow_ml_min'));self.assertIn('2measurementsinwarp',r['source_LOI_replicates']);self.assertIn('VFTnotLOI',r['source_LOI_geometry_conditioning']);self.assertIn('30daystorage',r['source_other_exclusions'])
if __name__=='__main__':unittest.main()
