"""Protect concentration matching, native metric meanings and residue temperatures."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b146/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261003_b146_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing,validate_tg_loi as v
A='10.1016/j.carbpol.2017.06.129';B='10.1007/s12221-019-9071-0'
class TextileB142Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
  cls.rows=[r for r in cls.rows if r['DOI'] in ['10.1016/j.carbpol.2017.06.129', '10.1007/s12221-019-9071-0']]
 def exact(self,d=A,s='Cotton-Control initial',gas='N2'):return next(r for r in self.rows if r['DOI']==d and r['sample_state']==s and r['atmosphere']==gas and r['pairing_status']=='verified_exact')
 def reject(self,r,**kw):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**kw)))
 def test_three_states_four_records_not_twentyseven_facts(self):
  z=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(z['errors']);self.assertEqual((z['verified_exact_sample_states'],z['verified_exact_condition_records']),(3,4));self.assertEqual(len(self.rows),27)
 def test_twenty_three_holds_no_canonical_tg(self):
  rr=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(rr),23);self.assertTrue(all(all(not r[k]for k in pairing.TG_FIELDS)for r in rr))
 def test_exact_ten_percent_loss_not_generic_onset(self):
  r=self.exact();self.assertEqual(r['T10_C'],'317');self.assertFalse(r['T5_C']);self.assertFalse(r['Tonset_C']);self.reject(r,T10_C='',Tonset_C='317')
 def test_nitrogen_ambiguous_peak_kept_raw(self):
  r=self.exact();self.assertEqual(r['source_raw_N2_peak_C'],'370');self.assertFalse(r['Tmax1_C']);self.reject(r,Tmax1_C='370')
 def test_nitrogen_r550_not_program_end600(self):
  r=self.exact();self.assertEqual((r['R550_pct'],r['residue_temp_C'],r['TG_end_C']),('0.91','550','600'));self.assertFalse(r['R600_pct']);self.reject(r,residue_temp_C='600')
 def test_air_generic_residue510_not500_or550(self):
  r=self.exact(gas='air');self.assertEqual((r['residue_pct'],r['residue_temp_C']),('0.02','510'));self.assertFalse(r['R500_pct']);self.assertFalse(r['R550_pct']);self.reject(r,residue_temp_C='500')
 def test_air_initial_decomposition_not_assumed_t10(self):
  r=self.exact(gas='air');self.assertEqual(r['Tmax1_C'],'354');self.assertFalse(r['T10_C']);self.assertFalse(r['Tonset_C']);self.reject(r,T10_C='317')
 def test_air_nitrogen_observations_cannot_swap(self):
  self.reject(self.exact(gas='air'),atmosphere='N2');self.assertEqual(self.exact(gas='air')['TG_end_C'],'800')
 def test_tgir_mass_and_start_not_main_conditions(self):
  r=self.exact();self.assertFalse(r['TG_start_C']);self.assertIn('notseparateTGIR7.55mg40-600',r['source_TG_mass_pan_flow_start']);self.reject(r,heating_rate_C_min='10')
 def test_sixteen_treated_loi_states_no_borrowed_control_tg(self):
  rr=[r for r in self.rows if r['DOI']==A and r['pairing_status']=='held_LOI_without_own_matching_dose_or_washed_TG'];self.assertEqual(len(rr),16);self.assertTrue(all(not r['T10_C']and not r['R550_pct']for r in rr))
 def test_apa_washed_and_initial_loi_do_not_mix(self):
  self.reject(self.exact(),LOI_pct='43.2',washing_state='After30durabilitylaunders');rr=[r for r in self.rows if r['sample_state']=='Cotton-APA20 reportedLC30'];self.assertEqual(len(rr),1);self.assertEqual(rr[0]['LOI_pct'],'30.5');self.assertFalse(rr[0]['Tmax1_C'])
 def test_two_unassigned_treated_gas_records_held(self):
  rr=[r for r in self.rows if r['pairing_status']=='held_TG_without_unambiguous_recipe_state_LOI'];self.assertEqual(len(rr),2);self.assertTrue(all(not r['LOI_pct']and not r['Tmax1_C']for r in rr))
 def test_ni_s_native_cotton_onset_not_pure_additive_t5(self):
  r=self.exact(B,'Cotton-NiS100-Urea50-Boric30 initial');self.assertEqual(r['Tonset_C'],'238.5');self.assertFalse(r['T5_C']);self.reject(r,Tonset_C='',T5_C='238.5')
 def test_ni_s_optimum_exact_same_catalyst_recipe(self):
  r=self.exact(B,'Cotton-NiS100-Urea50-Boric30 initial');self.assertEqual((r['source_bath_NiS_g_L'],r['source_bath_urea_g_L'],r['source_bath_boric_g_L'],r['LOI_pct']),('100','50','30','29.2'));self.reject(r,composition='Cotton/NiS100/urea20/boric30',LOI_pct='26.3')
 def test_bath_wt_percent_not_fabric_dry_addon(self):
  r=self.exact(B,'Cotton-NiS100-Urea50-Boric30 initial');self.assertFalse(r['source_dry_fabric_addon_pct']);self.assertIn('notdryfabricaddon',r['composition']);self.reject(r,sample_state='Cotton-NiS measured10.7percentdryaddon initial',composition='Cottonwithmeasured10.7percentdryNiSaddon')
 def test_ni_s_nitrogen_r700_not_air_or_mcc(self):
  r=self.exact(B,'Cotton-NiS100-Urea50-Boric30 initial');self.assertEqual((r['Tmax1_C'],r['R700_pct'],r['residue_temp_C']),('344.2','31.3','700'));self.reject(r,Tmax1_C='330.2');self.reject(r,atmosphere='air')
 def test_four_nonoptimal_si_loi_endpoints_held(self):
  rr=[r for r in self.rows if r['pairing_status']=='held_LOI_without_own_matching_dose_or_catalyst_TG'];self.assertEqual(len(rr),4);self.assertEqual(sorted(float(r['LOI_pct'])for r in rr),[21.6,22.4,26.3,30.5]);self.assertTrue(all(not r['R700_pct']for r in rr))
 def test_pure_ni_s_no_cotton_loi(self):
  rr=[r for r in self.rows if r['sample_state']=='NeatNiS'];self.assertEqual(len(rr),1);self.assertFalse(rr[0]['LOI_pct']);self.assertFalse(rr[0]['Tmax1_C']);self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(self.exact(B),material_form_TGA='NeatNiSpowder')))
 def test_accepted_apa_not_final_vor_year(self):
  r=self.exact();self.assertFalse(r['year']);self.assertIn('accepted2017-06-30',r['source_document_version']);self.assertEqual(self.exact(B)['year'],'2019')
 def test_whole_fabric_not_fiber_or_washed_state(self):
  r=self.exact(B);self.assertIn('plain woven 184 gsm cotton fabric',r['material_form']);self.assertIn('Initial0durabilitycycles',r['washing_state']);self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_LOI='Freestandingcottonfibers')));self.reject(r,washing_state='After10durabilitywashes')



"""Protect native DOPA group, gas, peak, uncertainty and washing distinctions."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b146/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261003_b146_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing,validate_tg_loi as v
class TextileB143Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
  cls.rows=[r for r in cls.rows if r['DOI'] in ['10.1016/j.polymdegradstab.2020.109158']]
 def exact(self,s,gas='N2'):return next(r for r in self.rows if r['sample_state']==s and r['atmosphere']==gas and r['pairing_status']=='verified_exact')
 def reject(self,r,**kw):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**kw)))
 def test_five_states_not_ten_gases_or_fourteen_facts(self):
  z=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(z['errors']);self.assertEqual((z['verified_exact_sample_states'],z['verified_exact_condition_records']),(5,10));self.assertEqual(len(self.rows),14)
 def test_four_washed_cone_facts_not_paired(self):
  h=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(h),4);self.assertTrue(all(not r['LOI_pct']and all(not r[k]for k in pairing.TG_FIELDS)for r in h));self.assertTrue(all('after5nativewashingcycles'in r['sample_state']for r in h))
 def test_t5_not_t10_or_onset(self):
  r=self.exact('PA66-D-10W');self.assertEqual(r['T5_C'],'368');self.assertFalse(r['T10_C']);self.assertFalse(r['Tonset_C']);self.reject(r,T5_C='',T10_C='368')
 def test_air_nitrogen_columns_not_swapped(self):
  r=self.exact('PA66-g-CS-D-20W','air');self.assertEqual((r['T5_C'],r['Tmax1_C'],r['R800_pct']),('326','387','4.4'));self.reject(r,T5_C='334',Tmax1_C='394',R800_pct='5.6')
 def test_three_native_air_peak_labels_chronological(self):
  r=self.exact('PA66-D-20W','air');self.assertEqual((r['Tmax1_C'],r['Tmax2_C'],r['Tmax3_C']),('400','452','594'));self.assertIn('nativeTmax1AIR->canonicalTmax2',r['source_TG_peak_native_column_map']);self.reject(r,Tmax1_C='452',Tmax2_C='400')
 def test_nitrogen_second_peak_not_borrowed(self):
  r=self.exact('PA66-g-CS-D-10W');self.assertFalse(r['Tmax2_C']);self.assertFalse(r['Tmax3_C']);self.reject(r,Tmax2_C='451')
 def test_control_third_peak_dash_not_zero(self):
  r=self.exact('PA66-Control','air');self.assertEqual(r['Tmax2_C'],'589');self.assertFalse(r['Tmax3_C']);self.reject(r,Tmax3_C='0')
 def test_low_temperature_water_not_dtg_decomposition(self):
  r=self.exact('PA66-Control');self.assertEqual(r['Tmax1_C'],'459');self.assertIn('water',r['source_TG_water_peak_limit']);self.reject(r,Tmax1_C='100')
 def test_coupled_tg_gc_ms_ramp_not_main_tg(self):
  r=self.exact('PA66-D-10W');self.assertEqual(r['heating_rate_C_min'],'20');self.assertIn('TG-GC-MS10C/min',r['source_TG_mass_pan_flow_start_end']);self.reject(r,heating_rate_C_min='10')
 def test_residue_temperature_not_program_endpoint(self):
  r=self.exact('PA66-Control');self.assertEqual((r['R800_pct'],r['residue_temp_C']),('4.9','800'));self.assertFalse(r.get('TG_end_C',''));self.reject(r,residue_temp_C='700')
 def test_native_r800_sd_replicates_not_loi_uncertainty(self):
  r=self.exact('PA66-g-CS-D-20W','air');self.assertEqual((r['source_R800_SD_pct'],r['source_R800_SD_repeats']),('1.2','3'));self.assertEqual(r['source_LOI_repeats'],'Unreported');self.assertFalse(r.get('LOI_uncertainty_pct',''))
 def test_addon_not_native_bath_content(self):
  r=self.exact('PA66-D-20W');self.assertEqual((r['source_DOPA_g_L'],r['source_addon_pct']),('200','14.9'));self.assertIn('notfinalfabricmassfraction',r['composition']);self.assertIn('(W1-W)/Wcontrolbaseline',r['source_addon_definition'])
 def test_addon_plusminus_not_assumed_sd(self):
  r=self.exact('PA66-D-10W');self.assertEqual(r['source_addon_uncertainty'],'0.87');self.assertIn('notassumedSD',r['source_addon_uncertainty_definition'])
 def test_control_addon_dash_not_zero(self):
  r=self.exact('PA66-Control');self.assertFalse(r['source_addon_pct']);self.assertFalse(r['source_DOPA_g_L']);self.assertFalse(r['source_CS_g_L'])
 def test_cs_and_dopa_only_groups_different(self):
  a=self.exact('PA66-D-10W');b=self.exact('PA66-g-CS-D-10W');self.assertEqual((a['LOI_pct'],b['LOI_pct']),('22.2','23.5'));self.assertFalse(a['source_CS_g_L']);self.assertEqual(b['source_CS_g_L'],'20');self.reject(a,LOI_pct='23.5',T5_C='354',Tmax1_C='408',R800_pct='7.5')
 def test_ten_w_twenty_w_content_not_wash_count(self):
  r=self.exact('PA66-D-10W');self.assertIn('initial0durabilitycycles',r['washing_state']);self.assertIn('10W/20WareDOPAcontentlabels',r['limitations']);self.reject(r,washing_state='After10durabilitycycles')
 def test_recipe_temperature_and_duration_not_borrowed(self):
  r=self.exact('PA66-g-CS-D-20W');self.assertIn('100C30mindry130C5mincure',r['treatment_method']);self.assertIn('UVfixedtime/doseunknown',r['treatment_method']);self.reject(r,sample_state='PA66-g-CS-D-20W after190C5mincure')
 def test_actual_textile_not_free_dopa(self):
  r=self.exact('PA66-D-20W');self.assertIn('plain woven fabric',r['material_form']);self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='Free DOPA powder')))
 def test_primary_table_locators_and_si_unread_explicit(self):
  r=self.exact('PA66-Control');self.assertIn('Table4PDFp7',r['LOI_locator']);self.assertIn('Table3PDFp6',r['TG_locator']);self.assertIn('SIunread',r['limitations']);self.assertIn('does not prove SI absent',r['supplement_review_status'])
 def test_cone_char_and_aliases_not_extra_tg_or_states(self):
  r=self.exact('PA66-g-CS-D-20W');self.assertEqual(r['R800_pct'],'5.6');self.reject(r,R800_pct='17.2');self.assertEqual(len({q['sample_state']for q in self.rows if q['pairing_status']=='verified_exact'}),5)



"""Protect primary FRPET correspondence without inventing residue or recipe metadata."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b146/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261003_b146_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing,validate_tg_loi as v
class TextileB144Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
  cls.rows=[r for r in cls.rows if r['DOI'] in ['10.1016/j.polymdegradstab.2020.109405']]
 def exact(self,s):return next(r for r in self.rows if r['sample_state']==s and r['pairing_status']=='verified_exact')
 def reject(self,r,**kw):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**kw)))
 def test_seven_initial_states_not_ten_facts(self):
  z=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(z['errors']);self.assertEqual((z['verified_exact_sample_states'],z['verified_exact_condition_records']),(7,7));self.assertEqual(len(self.rows),10)
 def test_three_washed_loi_facts_no_canonical_tg(self):
  h=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(h),3);self.assertTrue(all(all(not r[k]for k in pairing.TG_FIELDS)for r in h));self.assertEqual({r['LOI_pct']for r in h},{'30.4','26.4','29'})
 def test_native_t5_not_t10_or_onset(self):
  r=self.exact('FRPET');self.assertEqual(r['T5_C'],'387.2');self.assertFalse(r['T10_C']);self.assertFalse(r['Tonset_C']);self.reject(r,T5_C='',Tonset_C='387.2')
 def test_maximum_rate_tmax_not_negative_dtg_rate(self):
  r=self.exact('FRPET');self.assertEqual((r['Tmax1_C'],r['source_DTGmax_pct_min']),('431','-20.76'));self.reject(r,Tmax1_C='20.76')
 def test_unknown_residue_temperature_not_assumed800(self):
  r=self.exact('FRPET');self.assertEqual((r['source_raw_TG_residue_pct'],r['TG_end_C']),('15.7','800'));self.assertFalse(r['R800_pct']);self.assertFalse(r['residue_pct']);self.assertFalse(r.get('residue_temp_C',''));self.reject(r,R800_pct='15.7',residue_temp_C='800')
 def test_all_canonical_residue_unbound_values_blank(self):
  rr=[r for r in self.rows if r['pairing_status']=='verified_exact'];self.assertTrue(all(all(not r[k]for k in ['R400_pct','R500_pct','R600_pct','R700_pct','R800_pct','residue_pct'])for r in rr))
 def test_nitrogen_rate_not_air_or_invented_rate(self):
  r=self.exact('FRPET-g-PAA');self.assertEqual((r['atmosphere'],r['heating_rate_C_min']),('N2','10'));self.reject(r,atmosphere='air');self.reject(r,heating_rate_C_min='20')
 def test_rt_start_not_coupled_ir20(self):
  r=self.exact('FRPET');self.assertFalse(r['TG_start_C']);self.assertIn('TG-IR20Cnotborrowed',r['source_TG_start']);self.assertEqual(r['TGA_instrument'],'NetzschTG209F1')
 def test_paa_table_loi_not_ambiguous_prose_percentage(self):
  r=self.exact('FRPET-g-PAA');self.assertEqual((r['LOI_pct'],r['LOI_uncertainty_pct']),('26.4','0.3'));self.reject(r,LOI_pct='25.7')
 def test_six_and_nine_ks_layers_different(self):
  a=self.exact('FRPET-g-PAA@(K/S)6');b=self.exact('FRPET-g-PAA@(K/S)9');self.assertEqual((a['source_KS_bilayers'],b['source_KS_bilayers']),('6','9'));self.assertEqual((a['LOI_pct'],b['LOI_pct']),('27.9','26.8'));self.reject(a,sample_state=b['sample_state'])
 def test_three_and_nine_kd_layers_different(self):
  a=self.exact('FRPET-g-PAA@(K/D)3');b=self.exact('FRPET-g-PAA@(K/D)9');self.assertEqual((a['source_KD_bilayers'],b['source_KD_bilayers']),('3','9'));self.assertEqual((a['LOI_pct'],b['LOI_pct']),('33.1','33.8'));self.reject(a,T5_C=b['T5_C'],LOI_pct=b['LOI_pct'])
 def test_hybrid_six_plus_three_not_si_five_plus_three(self):
  r=self.exact('FRPET-g-PAA@(K/S+K/D)6+3');self.assertEqual((r['source_KS_bilayers'],r['source_KD_bilayers']),('6','3'));self.reject(r,sample_state='FRPET-g-PAA@(K/S+K/D)5+3');self.assertFalse(r['source_addon_pct'])
 def test_si_addon_groups_not_primary_addon(self):
  rr=[r for r in self.rows if r['pairing_status']=='verified_exact'and'@'in r['sample_state']];self.assertTrue(all(not r['source_addon_pct']for r in rr));r=self.exact('FRPET-g-PAA');self.assertEqual((r['source_addon_pct'],r['source_addon_uncertainty']),('2.9','0.7'))
 def test_recipe_table_and_prose_conflict_retained(self):
  r=self.exact('FRPET-g-PAA@(K/D)9');self.assertIn('wtpercent',r['source_bath_recipe_limit']);self.assertIn('molL',r['source_bath_recipe_limit']);self.assertIn('exactbathconcentrationunknown',r['source_bath_recipe_limit'])
 def test_backbone_phosphorus_invalid_unit_not_corrected(self):
  r=self.exact('FRPET');self.assertIn('6000mg/ginvalidphysicalunit',r['source_backbone_phosphorus_limit']);self.assertIn('retainednotcorrected',r['source_backbone_phosphorus_limit']);self.assertIn('backboneconcentrationunknown',r['composition'])
 def test_actual_copolyester_fabric_not_neat_pet_resin(self):
  r=self.exact('FRPET');self.assertIn('PET-co-CEPPA160gsm',r['material_form']);self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='Neat PET resin pellet')))
 def test_reported_loi_standard_not_silently_replaced(self):
  r=self.exact('FRPET');self.assertEqual(r['LOI_standard'],'NativeGB/T5455-1997');self.assertIn('notcorrectedto5454',r['source_LOI_standard_limit'])
 def test_uncertainty_and_vft_repeats_not_assumed_sd(self):
  r=self.exact('FRPET');self.assertIn('SD/SEdefinitionandrepeatsunreported',r['source_uncertainty_definition']);self.assertIn('threeVFTrepeatsnotborrowed',r['source_LOI_repeats'])
 def test_water_wash_zero_not_extra_initial_group(self):
  r=self.exact('FRPET-g-PAA@(K/S+K/D)6+3');self.assertIn('initial0durabilitycycles',r['washing_state']);self.assertEqual(len({q['sample_state']for q in self.rows if q['pairing_status']=='verified_exact'}),7);self.reject(r,washing_state='After10waterwashcycles');h=next(q for q in self.rows if 'after10' in q['sample_state']);self.assertEqual(h['LOI_pct'],'26.4');self.assertFalse(h['T5_C'])
 def test_accepted_source_version_locators_and_title_variant(self):
  r=self.exact('FRPET');self.assertFalse(r['year']);self.assertIn('accepted2020-10-17',r['source_document_version']);self.assertIn('Table2PDFp6',r['TG_locator']);self.assertIn('Table3PDFp7',r['LOI_locator']);self.assertIn('drafttitlevariant',r['source_supplement_identity'])



"""Protect native quadralayer measurements and unresolved source recipe conditions."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b146/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261003_b146_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing,validate_tg_loi as v
class TextileB145Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
  cls.rows=[r for r in cls.rows if r['DOI'] in ['10.1016/j.eurpolymj.2021.110320']]
 def exact(self,s,gas='N2'):return next(r for r in self.rows if r['sample_state']==s and r['atmosphere']==gas and r['pairing_status']=='verified_exact')
 def reject(self,r,**kw):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**kw)))
 def test_five_states_not_ten_gases_or_fourteen_facts(self):
  z=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(z['errors']);self.assertEqual((z['verified_exact_sample_states'],z['verified_exact_condition_records']),(5,10));self.assertEqual(len(self.rows),14)
 def test_four_washed_vertical_facts_no_tg_loi(self):
  h=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(h),4);self.assertTrue(all(not r['LOI_pct']and all(not r[k]for k in pairing.TG_FIELDS)for r in h));self.assertTrue(all('after20nativewashingcycles'in r['sample_state']for r in h))
 def test_native_t5_not_t10_or_onset(self):
  r=self.exact('PA6.6-g-PCS-8QL');self.assertEqual(r['T5_C'],'278');self.assertFalse(r['T10_C']);self.assertFalse(r['Tonset_C']);self.reject(r,T5_C='',T10_C='278')
 def test_air_nitrogen_columns_cannot_swap(self):
  r=self.exact('PA6.6-g-PCS-8QL','air');self.assertEqual((r['T5_C'],r['Tmax1_C'],r['R700_pct']),('260','376.9','4.27'));self.reject(r,T5_C='278',Tmax1_C='377',R700_pct='10.59')
 def test_three_air_peaks_in_source_order(self):
  r=self.exact('PA6.6-g-PCS-2QL','air');self.assertEqual((r['Tmax1_C'],r['Tmax2_C'],r['Tmax3_C']),('397.1','465.2','605.5'));self.reject(r,Tmax1_C='465.2',Tmax2_C='397.1')
 def test_treated_nitrogen_second_peak_not_air_oxidation(self):
  r=self.exact('PA6.6-g-PCS-4QL');self.assertEqual(r['Tmax2_C'],'459.6');self.assertFalse(r['Tmax3_C']);self.reject(r,Tmax2_C='466',Tmax3_C='598.1')
 def test_control_dash_peaks_not_zero(self):
  n=self.exact('PA6.6 Control');a=self.exact('PA6.6 Control','air');self.assertFalse(n['Tmax2_C']);self.assertEqual(a['Tmax2_C'],'561.5');self.assertFalse(a['Tmax3_C']);self.reject(n,Tmax2_C='0')
 def test_water_stage_not_low_temperature_numeric_peak(self):
  r=self.exact('PA6.6-g-PCS');self.assertEqual(r['Tmax1_C'],'398.6');self.assertIn('noestimatedlowTpeak',r['source_TG_water_limit']);self.reject(r,Tmax1_C='100')
 def test_700_residue_not_800_or_muffle_char(self):
  r=self.exact('PA6.6-g-PCS-8QL');self.assertEqual((r['R700_pct'],r['residue_temp_C']),('10.59','700'));self.assertFalse(r['R800_pct']);self.reject(r,R700_pct='',R800_pct='10.59',residue_temp_C='800');self.reject(r,residue_temp_C='500')
 def test_700_not_inferred_program_endpoint(self):
  r=self.exact('PA6.6 Control');self.assertFalse(r.get('TG_end_C',''));self.assertIn('R700notinferredprogramend',r['source_TG_flow_start_end'])
 def test_main_mass_pan_not_coupled_tg_ir(self):
  r=self.exact('PA6.6 Control');self.assertEqual((r['source_TG_mass_mg'],r['source_TG_pan']),('3-5','Openaluminapan'));self.assertIn('TGIR55mL/min5mgseparate',r['source_TG_flow_start_end']);self.assertTrue(r['source_TG_flow_start_end'].startswith('Unreported'))
 def test_main_rate_and_atmosphere_bound(self):
  r=self.exact('PA6.6-g-PCS-2QL');self.assertEqual(r['heating_rate_C_min'],'20');self.reject(r,heating_rate_C_min='10');self.reject(r,atmosphere='air')
 def test_pcs_only_not_two_quadralayers(self):
  a=self.exact('PA6.6-g-PCS');b=self.exact('PA6.6-g-PCS-2QL');self.assertEqual((a['source_QL'],b['source_QL']),('0','2'));self.assertEqual((a['LOI_pct'],b['LOI_pct']),('20.5','22'));self.reject(a,LOI_pct='22',T5_C='316')
 def test_two_four_eight_ql_different_initial_groups(self):
  rr=[self.exact('PA6.6-g-PCS-'+str(k)+'QL')for k in [2,4,8]];self.assertEqual([r['source_reported_WG_pct']for r in rr],['7.6','9.4','12.8']);self.reject(rr[0],sample_state=rr[2]['sample_state'])
 def test_native_concentration_conflicts_not_repaired(self):
  r=self.exact('PA6.6-g-PCS-8QL');self.assertEqual((r['source_native_PCS_percent_table'],r['source_native_PCS_percent_prose'],r['source_native_ME_percent_table'],r['source_native_ME_percent_prose']),('5','0.5','1','0.1'));self.assertIn('unknownactualconcentrations',r['source_recipe_condition_limit'])
 def test_wg_ambiguous_denominator_not_final_composition(self):
  r=self.exact('PA6.6-g-PCS-8QL');self.assertIn('(A0-A1)/A0',r['source_WG_definition_limit']);self.assertIn('notcorrected',r['source_WG_definition_limit']);self.assertFalse(r.get('source_addon_pct',''));self.assertIn('notfinalfabricmassfractions',r['composition'])
 def test_unknown_uv_duration_and_quartet_order_retained(self):
  r=self.exact('PA6.6-g-PCS-8QL');self.assertIn('UV80W/cm340-360nmAIRdurationunknown',r['treatment_method']);self.assertIn('quartetsequenceconflictretained',r['treatment_method']);self.assertIn('initiator4wtpercentbasisunknown',r['limitations'])
 def test_loi_table23point5_not_coarse_prose23(self):
  r=self.exact('PA6.6-g-PCS-8QL');self.assertEqual(r['LOI_pct'],'23.5');self.assertIn('Nativeprose23percent',r['source_LOI_8QL_conflict']);self.reject(r,LOI_pct='23')
 def test_exact_textile_and_initial_wash_identity(self):
  r=self.exact('PA6.6-g-PCS-4QL');self.assertIn('SuzhouXinganling',r['material_form']);self.assertIn('initial0durabilitycycles',r['washing_state']);self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='Free PCS powder')));self.reject(r,washing_state='After20nativewashingcycles')
 def test_native_version_standard_and_table_locators(self):
  r=self.exact('PA6.6 Control');self.assertEqual(r['year'],'2021');self.assertEqual(r['LOI_standard'],'ASTMD2863-19');self.assertIn('Table3PDFp7',r['LOI_locator']);self.assertIn('Table5PDFp9',r['TG_locator']);self.assertIn('NoSIcited',r['supplement_review_status']);self.assertEqual(r['source_LOI_repeats'],'Unreported')


if __name__=='__main__':unittest.main()
