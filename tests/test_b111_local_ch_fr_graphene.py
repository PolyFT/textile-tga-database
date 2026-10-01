"""Guard source scope, exact mass-loss definitions and unresolved LOI references."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import pairing
import validate_tg_loi as v
class CottonBariumSourceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with (R/'data/incoming/verified_source_batch_20261001_b111_local_ch_fr_graphene.csv').open(newline='')as f:cls.rows=[r for r in csv.DictReader(f) if r['DOI']=='10.1016/j.ijbiomac.2019.08.049']
 def test_two_gas_conditions_share_three_approved_states(self):
  r=v.build_tables(pd.DataFrame(self.rows),v.issue_list())[3];self.assertEqual(r['errors'],[]);self.assertEqual((r['verified_exact_sample_states'],r['verified_exact_condition_records']),(3,6))
 def test_own_control_zero_residue_is_reported_not_missing(self):
  for r in [r for r in self.rows if r['sample_state']=='Control']:
   self.assertEqual(r['LOI_pct'],'16.2');self.assertEqual(r['R600_pct'],'0');self.assertEqual(r['residue_temp_C'],'600');self.assertEqual(r['source_measured_weight_gain_pct_owf'],'')
   self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,LOI_pct='18.1')))
 def test_ten_percent_loss_does_not_become_five_percent_onset(self):
  for r in [r for r in self.rows if r['pairing_status']=='verified_exact']:
   self.assertNotEqual(r['T10_C'],'');self.assertEqual(r.get('T5_C',''),'');self.assertEqual(r.get('Tonset_C',''),'')
   self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,T5_C=r['T10_C'])))
 def test_pa_ba_table_and_synergy_reference_scope_hold(self):
  held=[r for r in self.rows if r['sample_state']=='PA/Ba/PA/Ba'];self.assertEqual(len(held),2)
  for r in held:
   self.assertEqual(r['source_LOI_Table4_abstract_pct'],'18.0');self.assertEqual(r['source_LOI_Lewis_synergist_reference_pct'],'16.4');self.assertEqual(r['LOI_pct'],'');self.assertEqual(r['reviewed_measurement_fingerprint'],'')
   self.assertNotEqual(r['T10_C'],'');self.assertIn('held',r['pairing_status'])
 def test_waterdurability_has_no_borrowed_tg_or_loi(self):
  rows=[r for r in self.rows if 'after6hDIwaterstir'in r['sample_state']];self.assertEqual(len(rows),3)
  for r in rows:
   self.assertEqual(r.get('LOI_pct',''),'');self.assertTrue(all(r.get(k,'')==''for k in pairing.TG_FIELDS));self.assertEqual(r['reviewed_measurement_fingerprint'],'');self.assertIn('notstandardlaundering',r['washing_state'])
 def test_regular_tg_does_not_borrow_mcc_methods_or_char(self):
  r=next(r for r in self.rows if r['sample_state']=='CH/PA/Ba/PA'and r['atmosphere']=='N2')
  self.assertEqual(r['heating_rate_C_min'],'15');self.assertEqual(r['R600_pct'],'29.4');self.assertEqual(r['source_TG_mass_mg'],'')
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,residue_pct='29.7',R600_pct='29.7')))
 def test_addon_uncertainty_and_assay_specific_repeats_distinct(self):
  r=next(r for r in self.rows if r['sample_state']=='CH/PA/CH/PA'and r['atmosphere']=='air')
  self.assertEqual(r['source_measured_weight_gain_pct_owf'],'10.7');self.assertEqual(r['source_weight_gain_SD_pct'],'0.5');self.assertEqual(r['source_weight_gain_replicates'],'5');self.assertEqual(r['source_CH_bath_wt_pct'],'1');self.assertEqual(r['source_PA_bath_wt_pct'],'3')
  self.assertEqual(r['source_TG_replicates'],'');self.assertEqual(r['source_LOI_replicates'],'');self.assertEqual(r['source_LOI_specimen_size_mm'],'120x50')


class AminoGrapheneTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with (R/'data/incoming/verified_source_batch_20261001_b111_local_ch_fr_graphene.csv').open(newline='') as f:
   rows=list(csv.DictReader(f))
  cls.fr=[r for r in rows if r['DOI']=='10.1007/s10570-019-02599-3']
  cls.gr=[r for r in rows if r['DOI']=='10.1007/s10853-020-04989-6']
 def test_amino_initial_4_states_8_conditions(self):
  r=v.build_tables(pd.DataFrame(self.fr),v.issue_list())[3]
  self.assertEqual((r['verified_exact_sample_states'],r['verified_exact_condition_records']),(4,8))
  self.assertEqual(len(self.fr),50)
 def test_amino_air_control_second_peak_is_char_oxidation(self):
  r=next(r for r in self.fr if r['sample_state']=='C0' and r['atmosphere']=='air')
  self.assertEqual(r['Tmax2_C'],'491.2');self.assertEqual(r['R600_pct'],'0');self.assertEqual(r['residue_temp_C'],'600')
  self.assertEqual(r.get('water_removal_peak_C',''),'')
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,Tmax2_C='')))
 def test_amino_r600_and_t10_are_not_scan_endpoint_or_t5(self):
  r=next(r for r in self.fr if r['sample_state']=='CL-30' and r['atmosphere']=='N2')
  self.assertEqual(r['T10_C'],'272.8');self.assertEqual(r['R600_pct'],'43.32');self.assertEqual(r['TG_end_C'],'700')
  self.assertEqual(r.get('R700_pct',''),'');self.assertEqual(r.get('T5_C',''),'');self.assertEqual(r.get('Tonset_C',''),'')
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,residue_temp_C='700')))
 def test_amino_unknown_percent_basis_and_uncertainty_type(self):
  r=next(r for r in self.fr if r['sample_state']=='CG-30' and r['atmosphere']=='N2')
  self.assertEqual(r['source_FR_bath_pct'],'30');self.assertIn('Unreported',r['source_FR_bath_percent_basis'])
  self.assertEqual(r['source_measured_weight_gain_pct_owf'],'16.3');self.assertEqual(r['source_weight_gain_uncertainty_type'],'Unreported')
  self.assertEqual(r['source_LOI_specimen_size_mm'],'');self.assertEqual(r.get('source_weight_gain_SD_pct',''),'')
 def test_amino_42_held_states_do_not_borrow_initial_tg(self):
  h=[r for r in self.fr if r['pairing_status']!='verified_exact'];self.assertEqual(len(h),42)
  self.assertEqual(sum(bool(r['LOI_pct']) for r in h),3)
  for r in h:
   self.assertTrue(all(not r.get(k,'') for k in pairing.TG_FIELDS));self.assertEqual(r['reviewed_measurement_fingerprint'],'')
  self.assertEqual({r['LOI_pct'] for r in h if r['LOI_pct']},{'26.4','26.0','27.1'})
 def test_graphene_three_initial_states_not_loi_replicates(self):
  r=v.build_tables(pd.DataFrame(self.gr),v.issue_list())[3]
  self.assertEqual((r['verified_exact_sample_states'],r['verified_exact_condition_records']),(3,3))
  self.assertEqual(len(self.gr),15)
 def test_graphene_k2co3_recipe_conflict_is_held(self):
  r=next(r for r in self.gr if r['sample_state']=='K2CO3/fabric')
  self.assertEqual(r['source_K2CO3_solution_preparation_mg_mL'],'60');self.assertEqual(r['source_K2CO3_coating_statement_mg_mL'],'2')
  self.assertEqual(r['source_LOI_Table1_mean_pct'],'23.0');self.assertEqual(r['LOI_pct'],'');self.assertEqual(r['reviewed_measurement_fingerprint'],'')
 def test_graphene_dsc_peaks_and_generic_onset_not_dtg(self):
  for r in [r for r in self.gr if r['pairing_status']=='verified_exact']:
   self.assertNotEqual(r['source_SI_S6_DSC_peak_C'],'');self.assertEqual(r.get('Tmax1_C',''),'');self.assertEqual(r.get('Tonset_C',''),'')
   self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,Tmax1_C=r['source_SI_S6_DSC_peak_C'])))
 def test_graphene_nitrogen_fixed_temperature_mass_not_endpoint(self):
  r=next(r for r in self.gr if r['sample_state']=='FGO/fabric')
  self.assertEqual(r['atmosphere'],'N2');self.assertEqual(r['heating_rate_C_min'],'20');self.assertEqual(r['TG_end_C'],'')
  self.assertEqual(r['R600_pct'],'68.6');self.assertEqual(r['R700_pct'],'64.24');self.assertEqual(r['source_main_TG_nominal_end_C'],'700')
  self.assertEqual(r['source_SI_S5_TG_run_end_C'],'796.06');self.assertEqual(r.get('R800_pct',''),'')
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,atmosphere='air')))
 def test_graphene_washed_binder_char_and_feedratios_remain_held(self):
  h=[r for r in self.gr if r['sample_state'] not in {'Blank fabric','GO/fabric','K2CO3/fabric','FGO/fabric'}]
  self.assertEqual(len(h),11);self.assertEqual(sum(bool(r['LOI_pct']) for r in h),5)
  for r in h:
   self.assertTrue(all(not r.get(k,'') for k in pairing.TG_FIELDS));self.assertEqual(r['reviewed_measurement_fingerprint'],'')
if __name__=='__main__':unittest.main()
