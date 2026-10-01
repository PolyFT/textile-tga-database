"""Protect TG mass-loss definitions and distinct conditions for water-glass cotton."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
H=Path(__file__).resolve().parent;P=H.name=='work';R=H.parent/'repo'if P else H.parent
F=H/'staged-local-textile-b118/publication_proposed.csv'if P else R/'data/incoming/verified_source_batch_20261002_b118_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing;import validate_tg_loi as v
class WaterglassB118Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def test_two_atmospheres_are_six_states_twelve_conditions(self):
  p=v.build_tables(pd.DataFrame(self.rows),v.issue_list())[3];self.assertFalse(p['errors']);self.assertEqual((p['verified_exact_sample_states'],p['verified_exact_condition_records']),(6,12))
 def test_native_five_percent_threshold_is_not_generic_decomposition_onset(self):
  r=next(r for r in self.rows if r['sample_state']=='COT_WG'and r['atmosphere']=='N2');self.assertEqual((r['T5_C'],r['Tmax1_C']),('118','374'));self.assertFalse(r.get('Tonset_C'));self.assertIn('water/silanol',r['source_T5_guard']);self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,T5_C='',Tonset_C='118')))
 def test_six_hundred_char_is_not_eight_hundred_scan_endpoint(self):
  for r in [r for r in self.rows if r['DOI'].endswith('0671-6')]:
   self.assertEqual(r['TG_end_C'],'800');self.assertFalse(r.get('R800_pct'))
   if r.get('R600_pct'):self.assertEqual(r['residue_temp_C'],'600');self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,residue_temp_C='800')))
 def test_air_control_residue_bound_never_becomes_zero_or_one(self):
  r=next(r for r in self.rows if r['sample_state']=='COT'and r['atmosphere']=='air');self.assertEqual(r['source_R600_reported'],'<1.0');self.assertFalse(r.get('R600_pct'));self.assertFalse(r.get('residue_pct'));self.assertFalse(r.get('residue_temp_C'));self.assertEqual((r['Tmax1_C'],r['Tmax2_C']),('356','481'));self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,R600_pct='1',residue_temp_C='600')))
 def test_variable_peak_residue_does_not_replace_fixed_temperature_char(self):
  r=next(r for r in self.rows if r['sample_state']=='COT_U240_AP115_WG'and r['atmosphere']=='N2');self.assertEqual((r['source_residue_at_Tmax_reported_pct'],r['R600_pct']),('66','39'));self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,R600_pct='66',residue_pct='66')))
 def test_pcfc_rate_and_cone_size_do_not_transfer_to_tg_or_loi(self):
  for r in [r for r in self.rows if r['DOI'].endswith('0671-6')]:self.assertEqual((r['heating_rate_C_min'],r['source_TG_flow_mL_min'],r['source_TG_replicates']),('10','60','2'));self.assertFalse(r['LOI_sample_dimensions_mm']);self.assertNotEqual(r['heating_rate_C_min'],'60')
 def test_all_thirty_one_held_facts_stay_outside_verified_target(self):
  rr=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(rr),31)
  for r in rr:self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS));self.assertFalse(r.get('reviewed_measurement_fingerprint'));self.assertFalse(r['heating_rate_C_min'])
 def test_manganese_cotton_never_borrows_mcc_rate_or_washed_char(self):
  rr=[r for r in self.rows if r['DOI']=='10.1002/vnl.21910'];self.assertEqual(len(rr),14)
  initial=next(r for r in rr if r['sample_state']=='Mn-15BL'and r['treatment_state']=='Initialpreparedstate');washed=next(r for r in rr if r['sample_state']=='Mn-15BL'and r['treatment_state']=='Washeddurabilitystate')
  self.assertEqual((initial['source_R800_reported_pct'],initial['source_MCC_residue_pct']),('38.2','34.7'));self.assertEqual((washed['LOI_pct'],washed['source_MCC_residue_pct']),('26.8','32.43'));self.assertFalse(washed['source_R800_reported_pct'])
 def test_gbcae_silk_curves_and_missing_rate_never_become_pairs(self):
  rr=[r for r in self.rows if r['DOI']=='10.1016/j.reactfunctpolym.2020.104731'];self.assertEqual(len(rr),17)
  tg=next(r for r in rr if r['native_sample_label']=='Silk-1'and not r['source_washing_cycles']);self.assertEqual((tg['source_T10_reported_C'],tg['source_R700_reported_pct']),('168.2','17'));self.assertFalse(tg['LOI_pct']);self.assertFalse(tg['source_TG_heating_rate_C_min'])
  w=next(r for r in rr if r['native_sample_label']=='Silk-2'and r['source_washing_cycles']=='5');self.assertEqual(w['source_LOI_explicit_reported_pct'],'26.5');self.assertFalse(w['LOI_pct']);self.assertFalse(w['source_R700_reported_pct'])
if __name__=='__main__':unittest.main()
