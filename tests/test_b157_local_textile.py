"""Protect native sample joins, residue endpoints and the six source-specific holds."""
import csv,json,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b157/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261004_b157_local_textile.csv'
sys.path.insert(0,str(R/'scripts'))
import pairing
import validate_tg_loi as v
A='10.1007/s10570-021-04255-1';B='10.1007/s10570-022-04923-w';C='10.1007/s10570-022-04991-y'
D='10.1007/s10570-021-04293-9';E='10.1007/s10570-022-04436-6';G='10.1007/s10570-022-04478-w'
class TextileB157Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as h:cls.rows=list(csv.DictReader(h))
 def subset(self,doi):return[r for r in self.rows if r['DOI']==doi]
 def approved(self,doi):return next(r for r in self.rows if r['DOI']==doi and r['pairing_status']=='verified_exact')
 def find(self,doi,sample,gas=None):return next(r for r in self.rows if r['DOI']==doi and r['sample_state']==sample and(gas is None or r['atmosphere']==gas))
 def reject(self,r,**changes):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**changes)))
 def no_tg(self,r):self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS))
 def test_two_states_two_conditions_not56facts(self):
  p=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(p['errors']);self.assertEqual((p['verified_exact_sample_states'],p['verified_exact_condition_records']),(2,2));self.assertEqual(len(self.rows),56)
 def test_all54holds_excluded(self):
  held=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(held),54);self.assertEqual([sum(r['DOI']==d for r in held)for d in [A,B,C,D,E,G]],[8,4,6,6,3,27]);self.assertTrue(all(pairing.evidence_issues(r)for r in held))
 def test_approved_values_states_washes_and_gases_bound(self):
  for doi in [A,E]:
   r=self.approved(doi);self.assertFalse(pairing.evidence_issues(r));self.reject(r,LOI_pct='99');self.reject(r,sample_state='Differentformula');self.reject(r,washing_state='after50LC');self.reject(r,atmosphere='Ar');self.reject(r,heating_rate_C_min='10')
 def test_approved_form_must_remain_cotton_fabric(self):
  for doi in [A,E]:self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(self.approved(doi),material_form_TGA='cotton fiber')))
 def test_methionine_air_residue_at567_not_programend750(self):
  r=self.approved(A);self.assertEqual((r['atmosphere'],r['LOI_pct'],r['residue_pct'],r['residue_temp_C']),('air','43.9','25.73','567'));self.reject(r,residue_temp_C='750');self.assertFalse(r.get('R750_pct'));self.assertEqual(r['source_residue_uncertainty_pct'],'2')
 def test_methionine_water_stage_not_T5_or_decomposition_peak(self):
  r=self.approved(A)
  for k in pairing.TG_FIELDS:
   if k!='residue_pct':self.assertFalse(r.get(k),k)
  self.reject(r,T5_C='261');self.reject(r,Tmax1_C='305');self.assertIn('dehydration',r['source_T5_definition'])
 def test_methionine_N2_residue_temp_unknown(self):
  r=self.find(A,'Methionine_29pct_initial_cotton_fabric','N2');self.assertEqual(r['residue_pct'],'34.95');self.assertFalse(r['residue_temp_C']);self.assertIn('temperature_unreported',r['pairing_status']);self.assertNotEqual(r['pairing_status'],'verified_exact')
 def test_methionine_own_control_cannot_borrow_intro18(self):
  rows=[r for r in self.subset(A)if'Control'in r['sample_state']];self.assertEqual(len(rows),2);self.assertTrue(all(not r['LOI_pct']for r in rows));self.assertTrue(all(r['pairing_status']!='verified_exact'for r in rows))
 def test_methionine_other_doses_no_TG(self):
  for dose,loi in [(19,'39.4'),(24,'41.5')]:r=self.find(A,f'Methionine_{dose}pct_initial_LOI_only');self.assertEqual(r['LOI_pct'],loi);self.no_tg(r)
 def test_methionine_three_washed_LOI_states_no_initial_TG(self):
  rows=[r for r in self.subset(A)if'after50LC'in r['sample_state']];self.assertEqual([r['LOI_pct']for r in rows],['31.5','35.1','37.7'])
  for r in rows:self.no_tg(r);self.assertIn('duration_balls_equivalence_unreported',r['washing_state'])
 def test_methionine_standalone_mass_rate_and_start_conflict(self):
  r=self.approved(A);self.assertEqual((r['heating_rate_C_min'],r['TG_start_C'],r['TG_end_C']),('20','','750'));self.assertIn('6mg',r['source_TG_mass_pan_repeats']);self.assertIn('Table3stage1 begins20C',r['source_TG_start_conflict']);self.assertIn('rate/flowunreported',r['source_TGIR_method'])
 def test_CSAPP_missing_standalone_method_not_TGIR_substitution(self):
  for r in self.subset(B):self.assertFalse(r['heating_rate_C_min']);self.assertFalse(r['TGA_instrument']);self.assertIn('20Cmin50-700',r['source_TGIR_method']);self.assertNotEqual(r['pairing_status'],'verified_exact')
 def test_CSAPP_native_control_Tmax_conflict_not_silently_corrected(self):
  r=self.find(B,'CF_initial','N2');self.assertEqual(r['Tmax1_C'],'369.3');self.assertIn('body369.5',r['source_control_Tmax_conflict'])
 def test_CSAPP_density_rawunit_not_silently_changed(self):
  for r in self.subset(B):self.assertEqual((r['source_native_density_value'],r['source_native_density_unit']),('160','g/cm2'));self.assertIn('unresolved',r['source_areal_density_issue'])
 def test_CSAPP_same_initial_two_states_four_tests_all_held(self):
  rows=self.subset(B);self.assertEqual(len(rows),4);self.assertEqual(len({r['sample_state']for r in rows}),2);self.assertEqual({r['LOI_pct']for r in rows},{'18.5','53.5'});self.assertTrue(all(r['residue_temp_C']=='700'for r in rows))
 def test_TSTDP_native_onset_not_T5_and_second_peak_indices(self):
  r=self.find(C,'TSTDP_generic_dose_initial','air');self.assertEqual((r['Tonset_C'],r['Tmax1_C'],r['Tmax2_C'],r['R800_pct']),('236','262','566','11.3'));self.assertFalse(r.get('T5_C'));self.assertEqual(self.find(C,'TSTDP_own_control_initial','air')['Tmax2_C'],'462');self.assertFalse(self.find(C,'TSTDP_generic_dose_initial','N2')['Tmax2_C'])
 def test_TSTDP_unknown_TG_dose_not_assigned_cone300gL(self):
  for r in self.subset(C):
   if r['R800_pct']:self.assertFalse(r['LOI_pct']);self.assertIn('do notprove',r['source_TG_dose_binding']);self.assertNotEqual(r['pairing_status'],'verified_exact')
 def test_TSTDP100gL_LOI_and_above300inequality_not_TG_join(self):
  r=self.find(C,'TSTDP100gL_initial_LOI_only');self.assertEqual(r['LOI_pct'],'26.7');self.no_tg(r);q=self.find(C,'TSTDP_above300gL_LOI_inequality_only');self.assertFalse(q['LOI_pct']);self.assertEqual(q['source_LOI_lower_bound_pct'],'29.9');self.assertIn('higherthan',q['source_LOI_qualifier']);self.no_tg(q)
 def test_conductive_S3_missing_all6TG_no_own_LOI(self):
  rows=self.subset(D);self.assertEqual(len(rows),6);self.assertTrue(all(not r['LOI_pct']for r in rows));self.assertTrue(all('absentinallnativeSI'in r['source_location']for r in rows))
 def test_conductive_plainTG700_not_TGIR900(self):
  for r in self.subset(D):self.assertEqual((r['TG_start_C'],r['TG_end_C'],r['source_TG_flow_mL_min']),('30','700','40'));self.assertIn('30-900',r['source_TGIR_method'])
 def test_conductive_DTG_unit_per_min_not_per_degree(self):
  r=self.find(D,'SFRC_CF_initial','N2');self.assertEqual(r['source_DTGmax_rate_pct_per_min'],'20.4');self.assertIn('notpctperC',r['source_DTG_rate_definition']);self.assertFalse(r.get('source_DTGmax_rate_pct_per_C'))
 def test_conductive_native_residue34point8_not_prose38point4(self):
  r=self.find(D,'P_HNTs_PA6_CF_initial','N2');self.assertEqual(r['R700_pct'],'34.8');self.assertIn('main38.4',r['source_residue_conflict'])
 def test_LFPN_own_selected_initial_N2_native_profile(self):
  r=self.approved(E);self.assertEqual(tuple(r[k]for k in ['LOI_pct','T5_C','Tmax1_C','R700_pct','atmosphere','heating_rate_C_min']),('46.7','249.4','269.3','47.3','N2','20'));self.assertIn('repeatonefurthercycle',r['treatment_method']);self.assertIn('9.43wtLFPNasreportedbasisunknown',r['composition'])
 def test_LFPN_residue700_not_end750_or_cone34point62(self):
  r=self.approved(E);self.assertEqual((r['residue_temp_C'],r['TG_end_C']),('700','750'));self.reject(r,residue_temp_C='750');self.reject(r,R700_pct='34.62')
 def test_LFPN_controls_both_held_and_air_ramp_unknown(self):
  rows=self.subset(E);controls=[r for r in rows if r['sample_state']=='Cotton_own_control_initial'];self.assertEqual(len(controls),2);self.assertTrue(all('provenance'in r['pairing_status']for r in controls));self.assertTrue(all(not r['heating_rate_C_min']for r in rows if r['atmosphere']=='air'));self.assertTrue(all('Tmax346.9vs346.8'in r['source_control_provenance_issue']for r in rows))
 def test_LFPN_density_unit_mass_pan_not_invented(self):
  r=self.approved(E);self.assertEqual(r['source_native_density_unit'],'g/cm2');self.assertIn('~10mgAl2O3',r['source_TG_mass_pan_repeats']);self.assertIn('notassignedair',r['source_TG_mass_pan_repeats'])
 def test_bio_five_own_fabric_TG_with_unknown_inert_identity(self):
  rows=[r for r in self.subset(G)if'_S6_'in r['sample_state']];self.assertEqual(len(rows),5)
  for r in rows:self.assertEqual(r['material_form_TGA'],'cotton fabric');self.assertFalse(r['atmosphere']);self.assertIn('N2/Aridentitynotreported',r['source_TG_reported_atmosphere']);self.assertFalse(r['LOI_pct'])
 def test_bio_weightloss_not_computed_residue_or_T5(self):
  rows=[r for r in self.subset(G)if'_S6_'in r['sample_state']];self.assertEqual([r['source_reported_weight_loss_at800C_pct']for r in rows],['72','60','72','',''])
  for r in rows:self.no_tg(r);self.assertIn('no100-minus-lossconversion',r['source_reported_weight_loss_qualifier']);self.assertEqual(r['TG_end_C'],'800')
 def test_bio_twelve_layer_LOIs_not_generic_S3_states(self):
  rows=[r for r in self.subset(G)if'coats_S4'in r['sample_state']];self.assertEqual(len(rows),12)
  for r in rows:self.no_tg(r)
  self.assertEqual(self.find(G,'Bio_GAB_P_3coats_S4_initial')['LOI_pct'],'48.6');self.assertEqual(self.find(G,'Bio_GAB_P_S3_initial_coating_count_unknown')['LOI_pct'],'49.5');self.assertEqual(self.find(G,'Bio_GTP_P_3coats_S4_initial')['LOI_pct'],'51.4')
 def test_bio_ABP_reportedmean_rawreplica_and_body_conflicts_preserved(self):
  r=self.find(G,'Bio_AB_P_S3_initial_coating_count_unknown');self.assertEqual(r['LOI_pct'],'36.4');self.assertEqual(json.loads(r['source_LOI_raw_replicates_json']),[35,34.1,36.7,35,37.2]);self.assertIn('primary38.4',r['source_LOI_mean_conflict']);self.assertIn('mean35.6',r['source_LOI_mean_conflict']);self.assertEqual(r['source_LOI_reported_replica_rows'],'5')
 def test_bio_four_wash_massloss_groups_not_TG_or_LOI(self):
  rows=[r for r in self.subset(G)if r['treatment_state']=='washed'];self.assertEqual(len(rows),4)
  for r in rows:self.no_tg(r);self.assertFalse(r['LOI_pct']);self.assertEqual(len(json.loads(r['source_wash_weight_loss_replicates_pct_json'])),3);self.assertIn('cyclecountunknown',r['washing_state'])
 def test_bio_DTA_DSC_not_TG_onset_or_peaks(self):
  for r in self.subset(G):
   self.no_tg(r)
   if r['source_DTA_DSC_exclusion']:self.assertIn('notTGmetrics',r['source_DTA_DSC_exclusion'])
 def test_issue_year_not_assumed_from_DOI_prefix(self):
  for d,y in [(A,'2021'),(B,'2023'),(C,'2023'),(D,'2022'),(E,'2022'),(G,'2022')]:self.assertTrue(all(r['year']==y for r in self.subset(d)))
if __name__=='__main__':unittest.main()
