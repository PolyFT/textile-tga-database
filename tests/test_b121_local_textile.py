"""Guard native thresholds, gas-specific values, dose identity and washed-state holds."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
H=Path(__file__).resolve().parent;P=H.name=='work';R=H.parent/'repo'if P else H.parent
F=H/'staged-local-textile-b121/publication_proposed.csv'if P else R/'data/incoming/verified_source_batch_20261002_b121_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing,validate_tg_loi as v
PE='10.1016/j.apsusc.2019.145175';DH='10.1016/j.carbpol.2017.05.054';DP='10.1007/s10570-019-02900-4'
class TextileB121Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def row(self,doi,state,gas=None):return next(r for r in self.rows if r['DOI']==doi and r['sample_state']==state and(gas is None or (r['atmosphere']or r.get('source_reported_atmosphere'))==gas))
 def rejected(self,row,**changes):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(row,**changes)))
 def test_independent_state_count_differs_from_condition_count(self):
  q=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(q['errors']);self.assertEqual((q['verified_exact_sample_states'],q['verified_exact_condition_records']),(6,12));self.assertEqual(len(self.rows),42)
 def test_pepas_air_onset_is_not_t5_or_water_loss(self):
  r=self.row(PE,'TCFSi','air');self.assertEqual((r['Tonset_C'],r['Tmax1_C']),('246.98','305.65'));self.assertFalse(r['T5_C']);self.assertFalse(r['T10_C']);self.rejected(r,Tonset_C='110');self.rejected(r,Tonset_C='',T5_C='246.98')
 def test_pepas_nitrogen_does_not_borrow_air_temperatures(self):
  r=self.row(PE,'TCFSi','N2');self.assertEqual((r['char_pct'],r['char_temp_C']),('37.94','700'));self.assertFalse(r['Tonset_C']);self.assertFalse(r['Tmax1_C']);self.rejected(r,Tonset_C='246.98')
 def test_pepas_silica_is_not_tcf_without_silica(self):
  r=self.row(PE,'TCFSi','air');h=self.row(PE,'TCF3');self.assertEqual((r['source_nanoSiO2_deposition'],h['source_nanoSiO2_deposition']),('yes','no'));self.assertEqual((r['LOI_pct'],h['LOI_pct']),('31.8','29.4'));self.assertTrue(all(not h.get(k)for k in pairing.TG_FIELDS));self.assertNotEqual(h['pairing_status'],'verified_exact')
 def test_pepas_uncertainty_not_assumed_standard_deviation(self):
  r=self.row(PE,'OCF','air');self.assertEqual(r['LOI_uncertainty_pct'],'0.45');self.assertIn('typeandreplicatesunreported',r['source_LOI_uncertainty_type']);self.assertEqual(r['LOI_sample_dimensions_mm'],'150x48');self.assertEqual((r['source_TG_mass_mg'],r['source_TG_mass_qualifier']),('5','approximately'))
 def test_pepas_washed_tcf_and_tcfsi_do_not_borrow_initial_tg(self):
  rr=[r for r in self.rows if r['DOI']==PE and r['source_native_LC']];self.assertEqual(len(rr),4);self.assertEqual({r['source_native_LC']for r in rr},{'20','50'});self.assertTrue(all(all(not r.get(k)for k in pairing.TG_FIELDS)for r in rr))
 def test_pepas_gas_specific_residues_cannot_be_swapped(self):
  r=self.row(PE,'TCFSi','air');self.assertEqual(r['residue_pct'],'15.02');self.rejected(r,char_pct='37.94',residue_pct='37.94')
 def test_dhtp_native_tonset10_is_t10_not_generic_onset(self):
  r=self.row(DH,'2%DHTP treated','N2');self.assertEqual((r['T10_C'],r['Tmax1_C']),('305','339'));self.assertFalse(r['Tonset_C']);self.assertFalse(r['T5_C']);self.rejected(r,T10_C='',Tonset_C='305')
 def test_dhtp_fixed_r600_is_not_method_endpoint_or_peak_residue(self):
  r=self.row(DH,'5%DHTP treated','N2');self.assertEqual((r['char_pct'],r['char_temp_C'],r['TG_end_C'],r['source_residue_at_Tmax1_pct']),('45.2','600','800','68.8'));self.rejected(r,residue_temp_C='800',char_temp_C='800');self.rejected(r,residue_pct='68.8',char_pct='68.8')
 def test_dhtp_less_than_one_bound_not_exact_zero(self):
  r=self.row(DH,'Untreated','air');self.assertEqual(r['source_native_R600'],'less than1.0');self.assertFalse(r['char_pct']);self.assertFalse(r['residue_pct']);self.assertEqual((r['T10_C'],r['Tmax2_C']),('318','488'));self.rejected(r,residue_pct='0',char_pct='0',residue_temp_C='600')
 def test_dhtp_mptes_only_pretreated_has_no_own_loi(self):
  rr=[r for r in self.rows if r['DOI']==DH and r['sample_state']=='MPTES-only pretreated'];self.assertEqual(len(rr),2);self.assertEqual({r['source_reported_atmosphere']for r in rr},{'N2','air'});self.assertTrue(all(not r['LOI_pct']and all(not r.get(k)for k in pairing.TG_FIELDS)for r in rr))
 def test_dhtp_eight_percent_addon_conflict_keeps_explicit_bath_identity(self):
  r=self.row(DH,'8%DHTP treated','air');self.assertEqual((r['source_DHTP_bath_wt_pct'],r['source_addon_Table2_pct'],r['source_addon_prose_conclusion_pct']),('8','60.4','61.4'));self.assertFalse(r['source_addon_pct']);self.assertFalse(pairing.evidence_issues(r))
 def test_dhtp_washed_records_not_duplicate_initial_or_borrow_tg(self):
  rr=[r for r in self.rows if r['DOI']==DH and r['source_native_LC']];self.assertEqual(len(rr),9);self.assertEqual({r['source_native_LC']for r in rr},{'1','5','30'});self.assertTrue(all(all(not r.get(k)for k in pairing.TG_FIELDS)for r in rr))
 def test_dhtp_nitrogen_and_air_dtg_are_distinct(self):
  n=self.row(DH,'2%DHTP treated','N2');a=self.row(DH,'2%DHTP treated','air');self.assertEqual((n['Tmax1_C'],a['Tmax1_C'],a['Tmax2_C']),('339','322','511'));self.assertFalse(n['Tmax2_C']);self.rejected(n,Tmax1_C='322')
 def test_dopopipsi_generic_treated_tg_is_not_400gl(self):
  rr=[r for r in self.rows if r['DOI']==DP and r['sample_state']=='Treated cotton unspecified dose'];self.assertEqual(len(rr),2);self.assertEqual({r['source_reported_R800_pct']for r in rr},{'19.1','42.0'});self.assertTrue(all(not r['LOI_pct']and not r['source_DOPO_PiP_Si_bath_g_L']and all(not r.get(k)for k in pairing.TG_FIELDS)for r in rr))
 def test_dopopipsi_initial_three_doses_do_not_share_generic_tg(self):
  rr=[r for r in self.rows if r['DOI']==DP and r['source_DOPO_PiP_Si_bath_g_L']];self.assertEqual(len(rr),3);self.assertEqual({r['source_DOPO_PiP_Si_bath_g_L']for r in rr},{'200','300','400'});self.assertTrue(all(all(not r.get(k)for k in pairing.TG_FIELDS)for r in rr))
 def test_dopopipsi_air_control_possible_shared_identity_retains_raw_values(self):
  r=self.row(DP,'Untreated cotton','air');self.assertEqual(r['source_native_R800'],'dash');self.assertEqual((r['source_reported_Tonset_C'],r['source_reported_Tmax1_C'],r['source_reported_Tmax2_C']),('294','344','489'));self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS));self.assertEqual(r['pairing_status'],'held_possible_cross_source_shared_control')
 def test_dopopipsi_exact_nitrogen_profile_is_not_new_independent_control(self):
  r=self.row(DP,'Untreated cotton','N2');self.assertEqual((r['source_reported_Tonset_C'],r['source_reported_Tmax1_C'],r['source_reported_residue_pct']),('312','369','17.3'));self.assertEqual(r['source_duplicate_candidate_DOI'],'10.1007/s10570-020-03488-w');self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS));self.assertFalse(r['reviewed_measurement_fingerprint']);self.assertNotEqual(r['pairing_status'],'verified_exact')
 def test_dopopipsi_si_washed_dose_and_tg_stay_unmapped(self):
  rr=[r for r in self.rows if r['DOI']==DP and r['source_native_LC']];self.assertEqual(len(rr),3);self.assertEqual({r['LOI_pct']for r in rr},{'26.5','26.0','25.7'});self.assertTrue(all(not r['source_DOPO_PiP_Si_bath_g_L']and all(not r.get(k)for k in pairing.TG_FIELDS)for r in rr))
 def test_all_held_facts_remain_outside_verified_target(self):
  rr=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(rr),30);self.assertTrue(all(r['review_disposition']=='held_outside_verified_target'and all(not r.get(k)for k in pairing.TG_FIELDS)for r in rr))
if __name__=='__main__':unittest.main()
