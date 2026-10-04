"""Guard native condition evidence, water-loss criteria and washed-state pairing."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b168/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261004_b168_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing;import validate_tg_loi as v
A='10.1007/s10570-025-06924-x';B='10.1007/s10570-022-04596-5';C='10.1007/s12221-025-00994-1'
class TextileB168Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def subset(self,doi):return[r for r in self.rows if r['DOI']==doi]
 def find(self,doi,sample,gas=None):return next(r for r in self.subset(doi)if r['sample_state']==sample and(gas is None or r['atmosphere']==gas))
 def accepted(self):return[r for r in self.rows if r['pairing_status']=='verified_exact']
 def noTG(self,r):self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS))
 def test_eight_states_twelve_conditions_not20facts(self):
  p=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(p['errors']);self.assertEqual((p['verified_exact_sample_states'],p['verified_exact_condition_records']),(8,12));self.assertEqual(len(self.rows),20)
 def test_eight_held_excluded(self):
  rows=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(rows),8);self.assertEqual([sum(r['DOI']==d for r in rows)for d in[A,B,C]],[5,1,2]);self.assertTrue(all(pairing.evidence_issues(r)for r in rows))
 def test_review_rejects_mutated_metric_condition_or_state(self):
  for r in self.accepted():
   self.assertFalse(pairing.evidence_issues(r))
   for k,value in [('LOI_pct','99'),('T5_C','300'),('Tmax1_C','555'),('R800_pct','77'),('atmosphere','oxygen'),('heating_rate_C_min','50'),('washing_state','50LC'),('sample_state','otherdose')]:self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**{k:value})))
 def test_fabric_not_fiber(self):
  for r in self.accepted():self.assertIn(r['material_form_TGA'],['lyocell fabric','PET fabric']);self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='cotton fiber')))
 def test_TGPA_all_four_native_conditions(self):
  for gas,expected in [('N2',{'LF':('283','337','13.6','18.2'),'TGPA30':('214','248','33.6','38.9')}),('air',{'LF':('282','318','0.5','18.2'),'TGPA30':('216','246','18.2','38.9')})]:
   for sample,e in expected.items():r=self.find(A,'TGPA_'+sample+'_initial',gas);self.assertEqual(tuple(r[k]for k in['Tonset_C','Tmax1_C','R800_pct','LOI_pct']),e);self.assertEqual(r['pairing_status'],'verified_exact')
 def test_TGPA_Tonset_not_guessed_T5_or_water_peak(self):
  for r in self.subset(A):
   if r['atmosphere']:self.assertFalse(r.get('T5_C'));self.assertFalse(r.get('T10_C'));self.assertIn('waterstagequalitativekeptdistinct',r['source_metric_definition'])
 def test_TGPA_own_global_ordinary_program_both_gases(self):
  for r in self.subset(A):
   if r['atmosphere']:self.assertEqual((r['TG_start_C'],r['TG_end_C'],r['heating_rate_C_min'],r['TGA_instrument']),('40','800','20','Netzsch TG209F3'));self.assertEqual(r['source_TGA_mass_flow_repeats'],'unreported')
 def test_TGPA_at_peak_mass_not_final_char(self):
  r=self.find(A,'TGPA_TGPA30_initial','N2');self.assertEqual((r['source_at_Tmax_remaining_mass_pct'],r['R800_pct']),('61.2','33.6'));self.assertEqual(r['residue_temp_C'],'800');self.assertNotEqual(r['residue_pct'],r['source_at_Tmax_remaining_mass_pct'])
 def test_TGPA_two_gases_not_four_sample_identities(self):
  rows=[r for r in self.subset(A)if r['pairing_status']=='verified_exact'];self.assertEqual((len(rows),len({r['sample_state']for r in rows})),(4,2));self.assertEqual(len({r['washing_state']for r in rows if 'TGPA30'in r['sample_state']}),1)
 def test_TGPA_bath_and_addon_not_identical(self):
  r=self.find(A,'TGPA_TGPA30_initial','N2');self.assertEqual((r['source_bath_TGPA_wt_pct'],r['source_weight_gain_pct']),('30','21.36'));self.assertIn('1:2550C20min120pctpickup180C10min',r['treatment_method'])
 def test_TGPA_lowdose_LOI_conflict_whole_fact_held(self):
  r=self.find(A,'TGPA_TGPA10_initial');self.assertEqual((r['LOI_pct'],r['source_LOI_body_pct']),('30.5','30.1'));self.noTG(r);self.assertNotEqual(r['pairing_status'],'verified_exact');r=self.find(A,'TGPA_TGPA20_initial');self.assertEqual(r['LOI_pct'],'33.5');self.noTG(r)
 def test_TGPA_three_25LC_LOIs_no_initial_TG(self):
  for sample,loi,wg in [('TGPA10','20.8','8.93'),('TGPA20','24.5','13.85'),('TGPA30','29.6','19.02')]:r=self.find(A,'TGPA_'+sample+'_after25LC');self.assertEqual((r['LOI_pct'],r['source_weight_gain_pct']),(loi,wg));self.noTG(r);self.assertIn('reported25LCnotmultiplied',r['source_wash_details'])
 def test_Sodium_native_six_TG_profiles(self):
  for gas,profiles in [('N2',{'Lyocell':('294.83','339.48','338.32','','13.62'),'G':('147.46','306.17','289.96','','27.07'),'A':('227.47','335.77','324.67','','30.71')}),('air',{'Lyocell':('272.9','326.46','323.21','464.02','3.88'),'G':('208.52','312.02','277.97','698.4','10.58'),'A':('172.47','301.47','280.34','694.93','15.65')})]:
   for sample,e in profiles.items():r=self.find(B,'Sodium_'+sample+'_initial',gas);self.assertEqual(tuple(r[k]for k in['T5_C','T50_C','Tmax1_C','Tmax2_C','R800_pct']),e);self.assertFalse(r.get('Tonset_C'))
 def test_Sodium_N2_A_water_stage_conflict_entire_condition_held(self):
  r=self.find(B,'Sodium_A_initial','N2');self.assertEqual((r['T5_C'],r['source_N2_water_stage_C'],r['source_N2_water_stage_massloss_pct']),('227.47','50-150','5.35'));self.assertEqual(r['pairing_status'],'held_N2_water_stage_T5_inconsistency');self.assertIn('wholeN2conditionheld',r['source_water_T5_conflict']);self.assertTrue(pairing.evidence_issues(r))
 def test_Sodium_air_A_separate_valid_condition(self):
  r=self.find(B,'Sodium_A_initial','air');self.assertEqual((r['pairing_status'],r['LOI_pct'],r['R800_pct']),('verified_exact','30.5','15.65'));self.assertFalse(r['source_water_T5_conflict']);self.assertFalse(r['source_N2_water_stage_massloss_pct'])
 def test_Sodium_R800_not_unknown_program_end_or_TGIR_flow(self):
  for r in self.subset(B):self.assertFalse(r['TG_start_C']);self.assertFalse(r['TG_end_C']);self.assertEqual(r['residue_temp_C'],'800');self.assertEqual(r['heating_rate_C_min'],'10');self.assertIn('notordinarySTA449F3flow',r['source_TGIR_exclusion'])
 def test_Sodium_high_air_second_peak_not_water(self):
  for sample in ['G','A']:r=self.find(B,'Sodium_'+sample+'_initial','air');self.assertGreater(float(r['Tmax2_C']),690);self.assertIn('Tmax2airhigh-Tcharoxidationnotwater',r['source_metric_definition'])
 def test_Sodium_Asp_concentration_not_borrowed_from_glycine(self):
  r=self.find(B,'Sodium_A_initial','air');self.assertIn('Aspconcentrationnotexplicitlyreportednotassigned2M',r['treatment_method']);self.assertIn('formaldehydeconc_volumeunreported',r['treatment_method']);self.assertEqual(r['source_weight_gain_pct'],'14.5')
 def test_Sodium_cone_char_conflicts_not_TGchar(self):
  for r in self.subset(B):self.assertIn('Table3conechar8.9/60.0/51.9versusbody2.3/12.4/15.3notTG',r['source_cone_char_conflict']);self.assertIn('notbathorwholefabricloading',r['source_composition_limit'])
 def test_PET_three_accepted_own_profiles(self):
  for sample,e in [('PET-0',('395','425','6.5','20.6')),('PET-a',('385','422','12.5','24.2')),('PET-b',('325','426','18.2','27.4'))]:r=self.find(C,'DTA_'+sample+'_initial');self.assertEqual(tuple(r[k]for k in['T5_C','Tmax1_C','R700_pct','LOI_pct']),e);self.assertEqual(r['pairing_status'],'verified_exact')
 def test_PET_C_LOI_Table_Conclusion_conflict_entire_pair_held(self):
  r=self.find(C,'DTA_PET-c_initial');self.assertEqual((r['LOI_pct'],r['source_LOI_Conclusion_pct']),('29.3','29.2'));self.assertEqual(r['pairing_status'],'held_LOI_Table2_Conclusion_conflict');self.assertTrue(pairing.evidence_issues(r))
 def test_PET_d_LOI_has_no_reused_c_TG(self):
  r=self.find(C,'DTA_PET-d_initial');self.assertEqual(r['LOI_pct'],'30.1');self.noTG(r);self.assertFalse(r['heating_rate_C_min'])
 def test_PET_loading_basis_and_unknowns_not_guessed(self):
  r=self.find(C,'DTA_PET-b_initial');self.assertEqual((r['source_component_DTA_added_wt_pct'],r['source_component_KH602_added_wt_pct']),('5','5'));self.assertIn('basisunreported',r['source_component_loading_basis']);self.assertFalse(r['TGA_instrument']);self.assertIn('gsm/weave/purityfractionunreported',r['composition'])
 def test_PET_ordinary_N2_program_not_helium_pyrolysis(self):
  for r in self.subset(C):
   if r['atmosphere']:self.assertEqual((r['atmosphere'],r['TG_start_C'],r['TG_end_C'],r['heating_rate_C_min']),('N2','50','700','10'));self.assertIn('600CHe30mLminnotordinaryTG',r['source_PyGCMS_exclusion'])
 def test_PET_roll_bake_and_LOI_method(self):
  r=self.find(C,'DTA_PET-b_initial');self.assertIn('dip-rollapprox80pctpickup/80C5minpredry/120C3minbake',r['treatment_method']);self.assertEqual((r['LOI_instrument'],r['LOI_standard']),('JF3','GB/T5454-2008'))
 def test_materials_are_lyocell_and_PET_fabrics(self):
  for r in self.accepted():self.assertEqual(r['material_category'],'polyester'if r['DOI']==C else'lyocell');self.assertEqual(r['material_form'],'PET fabric'if r['DOI']==C else'lyocell fabric')
 def test_public_facts_no_private_paths_or_contacts(self):
  for r in self.rows:self.assertRegex(r['evidence_reviewed_at'],r'^\d{4}-\d{2}-\d{2}$');self.assertFalse(any(('/'+'Volumes'+'/')in str(x)or('/'+'Users'+'/')in str(x)or('smb'+':'+chr(47)*2)in str(x)or'@163.com'in str(x)for x in r.values()))
if __name__=='__main__':unittest.main(verbosity=2)
