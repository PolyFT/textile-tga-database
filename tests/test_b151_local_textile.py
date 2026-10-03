"""Protect specimen forms, gas strata, native metric definitions and explicit holds."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b151/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261004_b151_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing;import validate_tg_loi as v
A='10.1016/j.carbpol.2016.05.087';B='10.1002/app.49385';C='10.1002/app.1992.070460312';D='10.1039/d4ta04320k'
class TextileB151Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def row(self,d,s,gas=None):return next(r for r in self.rows if r['DOI']==d and r['sample_state']==s and(gas is None or r.get('atmosphere')==gas))
 def reject(self,r,**changes):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**changes)))
 def test_eight_states_eleven_conditions_not21facts(self):
  p=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(p['errors']);self.assertEqual((p['verified_exact_sample_states'],p['verified_exact_condition_records']),(8,11));self.assertEqual(len(self.rows),21)
 def test_ten_holds_are_excluded(self):
  x=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(x),10);self.assertTrue(all(pairing.evidence_issues(r)for r in x))
 def test_three_cotton_states_two_gases(self):
  x=[r for r in self.rows if r['DOI']==A and r['pairing_status']=='verified_exact'];self.assertEqual(len(x),6);self.assertEqual(len({r['sample_state']for r in x}),3);self.assertTrue(all(r['heating_rate_C_min']=='10'for r in x));r=self.row(A,'3wt% APP/BPEI cotton initial','N2');self.reject(r,atmosphere='air')
 def test_cotton_measured_loi_shared_only_with_own_states(self):
  for s,l in [('Control cotton initial','18.4'),('3wt% APP/BPEI cotton initial','21'),('5wt% APP/BPEI cotton initial','22.2')]:
   for g in ['N2','air']:self.assertEqual(self.row(A,s,g)['LOI_pct'],l)
  self.reject(self.row(A,'3wt% APP/BPEI cotton initial','N2'),LOI_pct='22.2')
 def test_air_native_second_oxidation_peak_kept(self):
  for s,t in [('Control cotton initial','484'),('3wt% APP/BPEI cotton initial','502'),('5wt% APP/BPEI cotton initial','510')]:self.assertEqual(self.row(A,s,'air')['Tmax2_C'],t)
  self.reject(self.row(A,'5wt% APP/BPEI cotton initial','air'),Tmax2_C='319')
 def test_t5_and_rate_maximum_not_undefined_onset(self):
  r=self.row(A,'Control cotton initial','N2');self.assertEqual((r['T5_C'],r['Tmax1_C']),('304','368'));self.assertFalse(r.get('Tonset_C'));self.reject(r,T5_C='',Tonset_C='304')
 def test_zero_air_residue_is_exact_not_missing(self):
  r=self.row(A,'Control cotton initial','air');self.assertEqual((r['R600_pct'],r['residue_pct'],r['residue_temp_C']),('0','0','600'));self.reject(r,R600_pct='11.9')
 def test_cotton_mass_pan_flow_and_program_unknown(self):
  r=self.row(A,'5wt% APP/BPEI cotton initial','N2');self.assertEqual(r['source_TG_mass_pan_flow'],'Unreported');self.assertIn('Unreported',r['source_TG_program_start_end']);self.assertFalse(r.get('TG_end_C')or r.get('TG_start_C'))
 def test_bath_dose_volume_ratio_not_fabric_weight(self):
  r=self.row(A,'5wt% APP/BPEI cotton initial','N2');self.assertEqual((r['source_APP_bath_wt_pct'],r['source_BPEI_bath_wt_pct'],r['source_APP_BPEI_volume_ratio']),('1','0.2','1.2:1'));self.assertIn('massbasisnotexplicit',r['source_addon_definition']);self.assertIn('countunreported',r['source_coating_cycles'])
 def test_two_washed_lois_have_no_tg(self):
  for h,l in [(3,'21'),(6,'20')]:
   r=self.row(A,f'5wt% APP/BPEI cotton W{h}h');self.assertEqual(r['LOI_pct'],l);self.assertIn('40C300rpm0.5wt%Ariel',r['washing_state']);self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS));self.assertIn('held_',r['pairing_status'])
 def test_four_finished_fiber_native_profiles(self):
  x=[r for r in self.rows if r['DOI']==B];self.assertEqual([(r['T5_C'],r['Tmax1_C'],r['R600_pct'],r['LOI_pct'])for r in x],[('278.3','386.8','35.2','42.3'),('298.9','394.7','35.9','42.7'),('228.8','365.4','32.3','40.4'),('260.6','374.5','34','41.1')]);self.reject(x[3],LOI_pct='40.4')
 def test_fiber_table_rounding_and_prose_precision_separate(self):
  x=[r for r in self.rows if r['DOI']==B];self.assertEqual([r['source_body_R600_higher_precision_pct']for r in x],['35.22','35.86','32.33','33.98']);self.assertTrue(all('consistentrounding' in r['source_R600_definition']for r in x))
 def test_fiber_t5_water_or_pva_not_tonset(self):
  r=self.row(B,'FMF/PVA initial finished fiber');self.assertFalse(r.get('Tonset_C'));self.assertIn('earlywater/PVA',r['source_T5_definition']);self.reject(r,T5_C='',Tonset_C='228.8')
 def test_fiber_nitrogen_mass_pan_flow_not_ftir_air(self):
  r=self.row(B,'FMF initial finished fiber');self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['source_TG_mass_mg'],r['source_TG_pan'],r['source_TG_flow_mL_min'],r['TG_end_C']),('N2','10','6','Alumina','40','600'));self.reject(r,atmosphere='air')
 def test_fiber_plaits_are_finished_fibers_not_bulkresin(self):
  r=self.row(B,'FMF/SiO2 initial finished fiber');self.assertIn('finished dry-spun',r['material_form']);self.assertIn('twistedintoplaits',r['source_LOI_specimen']);self.assertEqual(r['source_LOI_dimensions_mm'],'50x6x3');self.assertIn('postsolidification230-250C1h',r['treatment_method'])
 def test_other_fiber_feed_not_renormalized_or_final_fractions(self):
  r=self.row(B,'FMF/PVA initial finished fiber');self.assertIn('noautomaticrenormalization',r['source_other_variant_feed']);self.assertIn('notfinalfiberfractions',r['source_full_variant_feed']);self.assertIn('DMSO7daysswellingtestnotTGorLOIstate',r['washing_state'])
 def test_nylon_pair_is_explicit_residue_not_dsc(self):
  r=self.row(C,'CP-MN initial nylon6 textile');self.assertEqual((r['LOI_pct'],r['R700_pct'],r['atmosphere'],r['heating_rate_C_min']),('31.4','3.5','air','10'));self.assertTrue(all(not r.get(k)for k in ['T5_C','Tonset_C','Tmax1_C']));self.reject(r,Tonset_C='329');self.reject(r,Tmax1_C='434')
 def test_nylon_xray_mass_loss_not_tg_and_ir_only_extraction(self):
  r=self.row(C,'CP-MN initial nylon6 textile');self.assertFalse(r.get('R550_pct'));self.assertIn('noR550calculated',r['source_XRD_exclusion']);self.assertIn('IR-only70hwaterextractionnotTGLOIstate',r['washing_state']);self.assertIn('notassignedexactcuring',r['treatment_method'])
 def test_nylon_control_N_vs_CP_N_not_aliased(self):
  r=self.row(C,'N versus CP-N unresolved control');self.assertIn('CP-N23.6',r['source_raw_LOI']);self.assertIn('N23.6',r['source_raw_LOI']);self.assertEqual(r['pairing_status'],'held_control_N_CP_N_alias_unproven');self.assertFalse(r.get('LOI_pct'))
 def test_nylon_source_identity_has_registry_not_filename_only(self):
  r=self.row(C,'CP-MN initial nylon6 textile');self.assertIn('localregistrytitle/year/3authors',r['publication_type_evidence']);self.assertEqual(r['year'],'1992')
 def test_rsc_all_seven_facts_held_without_si_tg(self):
  x=[r for r in self.rows if r['DOI']==D];self.assertEqual(len(x),7);self.assertTrue(all(r['pairing_status']!='verified_exact'for r in x));self.assertTrue(all(all(not r.get(k)for k in pairing.TG_FIELDS)for r in x));self.assertTrue(all('unreadnotproofabsence' in r['supplement_review_status']for r in x))
 def test_rsc_singlelayer_and_janus_and_wash_are_distinct(self):
  a=self.row(D,'PUC@MHPP7.5 initial');b=self.row(D,'PUC@MHPP7.5@BP initial Janus');c=self.row(D,'PUC@MHPP7.5 after20washes');self.assertEqual((a['LOI_pct'],b['LOI_pct'],c['LOI_pct']),('28','28','27.3'));self.assertNotEqual(a['sample_state'],b['sample_state']);self.assertIn('20nativewashingcycles',c['washing_state'])
if __name__=='__main__':unittest.main()
