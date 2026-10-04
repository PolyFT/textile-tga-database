"""Guard critical native conflicts, formula assignment and partial control reuse."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b169/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261004_b169_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing;import validate_tg_loi as v
A='10.1007/s10570-022-04690-8';B='10.1007/s10570-022-04927-6';C='10.1007/s10570-023-05543-8'
class TextileB169Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def find(self,doi,name,gas=None):return next(r for r in self.rows if r['DOI']==doi and r['sample_state']==name and(gas is None or r['atmosphere']==gas))
 def accepted(self):return[r for r in self.rows if r['pairing_status']=='verified_exact']
 def subset(self,doi):return[r for r in self.rows if r['DOI']==doi]
 def noTG(self,r):self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS))
 def test_three_states_three_conditions_not_sixty_facts(self):
  x=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(x['errors']);self.assertEqual((x['verified_exact_sample_states'],x['verified_exact_condition_records']),(3,3));self.assertEqual(len(self.rows),60)
 def test_fiftyseven_held_excluded(self):
  h=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(h),57);self.assertTrue(all(pairing.evidence_issues(r)for r in h));self.assertEqual([sum(r['DOI']==d for r in h)for d in[A,B,C]],[17,21,19])
 def test_measured_values_or_state_mutations_rejected(self):
  for r in self.accepted():
   self.assertFalse(pairing.evidence_issues(r))
   for key,value in [('LOI_pct','99'),('residue_pct','77'),('residue_temp_C','999'),('heating_rate_C_min','20'),('atmosphere','air'),('sample_state','otherformula'),('washing_state','washed')]:self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**{key:value})))
 def test_same_fabric_form_required(self):
  for r in self.accepted():self.assertEqual(r['material_form_TGA'],r['material_form_LOI']);self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='fiber')))
 def test_DMCFR_own_N2_twenty_percent_profile(self):
  r=self.find(A,'DMCFR_FR20_initial','N2');self.assertEqual(tuple(r[k]for k in['T10_C','T50_C','Tmax1_C','R800_pct','LOI_pct']),('234.33','482.73','267.58','42.54','30'));self.assertEqual(r['pairing_status'],'verified_exact');self.assertEqual(r['source_LOI_uncertainty_pct'],'0.1')
 def test_DMCFR_T10_not_T5_or_Tonset(self):
  for r in self.subset(A):self.assertFalse(r.get('T5_C'));self.assertFalse(r.get('Tonset_C'))
 def test_DMCFR_ordinary_TGA_not_TGIR_reciprocal_unit(self):
  r=self.find(A,'DMCFR_FR20_initial','N2');self.assertEqual(tuple(r[k]for k in['TGA_instrument','TG_start_C','TG_end_C','heating_rate_C_min']),('TA Instruments TGA-Q5000','50','800','10'));self.assertIn('TGIR10minperCunitnotordinaryTGA10Cmin',r['source_metric_definition'])
 def test_DMCFR_entire_air_pair_R800_conflict_held(self):
  r=self.find(A,'DMCFR_FR20_initial','air');self.assertEqual((r['R800_pct'],r['source_R800_body_pct']),('9.1','9.15'));self.assertEqual(r['pairing_status'],'held_R800_Table5_body_conflict');self.assertTrue(pairing.evidence_issues(r))
 def test_DMCFR_explicit_twenty_percent_selection_and_loading(self):
  r=self.find(A,'DMCFR_FR20_initial','N2');self.assertEqual((r['source_bath_DMCFR_wt_pct'],r['source_weight_gain_pct']),('20','14.2'));self.assertIn('20wtselectedexplicitlyforfollowingexperiments',r['treatment_method']);self.assertIn('DCDA7wtrelativeDMCFR',r['treatment_method'])
 def test_DMCFR_other_doses_no_borrowed_TG(self):
  for dose,loi in [(30,'33'),(40,'36')]:r=self.find(A,f'DMCFR_FR{dose}_initial');self.noTG(r);self.assertEqual(r['LOI_pct'],loi)
 def test_DMCFR_twelve_washed_LOIs_not_initial_TG(self):
  r=[r for r in self.subset(A)if r['treatment_state']=='washed'];self.assertEqual(len(r),12)
  for x in r:self.noTG(x);self.assertIn('reportedLCunitnotmultiplied',x['source_wash_details'])
 def test_crosspaper_controls_held_in_both_atmospheres(self):
  for doi,prefix in [(A,'DMCFR'),(B,'Luffa')]:
   for gas in ['N2','air']:r=self.find(doi,prefix+'_Lyocell_initial',gas);self.assertEqual(r['pairing_status'],'held_crosspaper_partial_control_provenance');self.assertIn('Partial control provenance unresolved',r['source_critical_hold'])
 def test_shared_T50_residue_not_resolved_duplicate(self):
  a=self.find(A,'DMCFR_Lyocell_initial','N2');b=self.find(B,'Luffa_Lyocell_initial','N2');self.assertEqual((a['T50_C'],a['R800_pct']),(b['T50_C'],b['R800_pct']));self.assertNotEqual(a['Tmax1_C'],b['Tmax1_C']);self.assertIn('not asserted a resolved duplicate',b['source_critical_hold'])
 def test_Luffa_unqualified_TG_labels_not_assigned_to_thirty_percent(self):
  for sample in ['FR','EDFR']:
   for gas in ['N2','air']:r=self.find(B,'Luffa_'+sample+'_initial',gas);self.assertEqual(r['pairing_status'],'held_unqualified_TG_dose_mapping');self.assertFalse(r['LOI_pct']);self.assertIn('notjoinedbyassuming30wt',r['source_critical_hold'])
 def test_Luffa_native_six_TG_records_retained(self):
  expected=[('N2','FR','196.82','242.72','44.9'),('N2','EDFR','212.47','249.37','45.38'),('air','FR','195.12','243.12','20.8'),('air','EDFR','216.02','251.72','26.99')]
  for gas,s,t5,tm,res in expected:r=self.find(B,'Luffa_'+s+'_initial',gas);self.assertEqual((r['T5_C'],r['Tmax1_C'],r['R800_pct']),(t5,tm,res));self.assertEqual((r['TG_start_C'],r['TG_end_C'],r['heating_rate_C_min']),('40','800','10'))
 def test_Luffa_at_peak_mass_not_R800(self):
  r=self.find(B,'Luffa_FR_initial','N2');self.assertEqual((r['source_remaining_mass_at_Tmax1_pct'],r['R800_pct']),('77.16','44.9'));self.assertNotEqual(r['source_remaining_mass_at_Tmax1_pct'],r['residue_pct'])
 def test_Luffa_own_three_initial_LOIs_and_WG_separate(self):
  for name,loi,wg in [('FR20','36.8','17.2'),('FR30','38.9','19.5'),('EDFR30','38.6','19.6')]:r=self.find(B,'Luffa_'+name+'_initial');self.assertEqual((r['LOI_pct'],r['source_weight_gain_pct']),(loi,wg));self.noTG(r)
 def test_Luffa_twelve_washed_LOIs_no_initial_reuse(self):
  rr=[r for r in self.subset(B)if r['treatment_state']=='washed'];self.assertEqual(len(rr),12)
  for r in rr:self.noTG(r)
 def test_cotton_two_accepted_own_reported_residue_pairs(self):
  for name,loi,res in [('Control','18.0','13.15'),('AS24','30.34','35.9')]:r=self.find(C,'ASSS_'+name+'_initial');self.assertEqual((r['LOI_pct'],r['residue_pct'],r['residue_temp_C']),(loi,res,'500'));self.assertEqual(r['pairing_status'],'verified_exact')
 def test_cotton_SS_interval_char_discrepancy_whole_pair_held(self):
  r=self.find(C,'ASSS_SS24_initial');self.assertEqual((r['LOI_pct'],r['residue_pct'],r['audit_interval_weightloss_sum_pct'],r['audit_reported_char_balance_difference_pct']),('32.5','38.13','61.74','0.13'));self.assertEqual(r['pairing_status'],'held_stage_weightloss_reported_char_balance_unresolved');self.assertTrue(pairing.evidence_issues(r));self.assertIn('reportedcharpreservednotcomputedreplacement',r['source_interval_char_conflict'])
 def test_cotton_ZA_additional_mass_balance_hold_no_correction(self):
  r=self.find(C,'ASSS_AS16_SS8_ZA5_initial');self.assertEqual((r['residue_pct'],r['audit_interval_weightloss_sum_pct'],r['audit_reported_char_balance_difference_pct']),('41.79','57.86','0.35'));self.assertNotEqual(r['pairing_status'],'verified_exact')
 def test_cotton_intervals_not_decomposition_temperatures(self):
  for r in self.subset(C):
   if r['atmosphere']:
    for k in ['T5_C','T10_C','Tonset_C','Tmax1_C','Tmax2_C']:self.assertFalse(r.get(k))
    self.assertIn('residualcharreportednotcomputed',r['source_interval_metric_limit'])
 def test_cotton_own_N2_program_and_unknown_instrument(self):
  for r in self.accepted():
   if r['DOI']==C:self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['TG_end_C']),('N2','10','500'));self.assertFalse(r['TGA_instrument']);self.assertIn('ambient_temperature_unreported',r['source_TGA_start'])
 def test_cotton_ZA_entire_pair_LOI_conflict(self):
  r=self.find(C,'ASSS_AS16_SS8_ZA5_initial');self.assertEqual((r['LOI_pct'],r['source_LOI_Table3_withoutwash_pct']),('38.3','38'));self.assertEqual(r['residue_pct'],'41.79');self.assertNotEqual(r['pairing_status'],'verified_exact')
 def test_cotton_without_ZA_initial_conflict_not_new_sample(self):
  r=self.find(C,'ASSS_AS16_SS8_ZA0_initial');a=self.find(C,'ASSS_AS16_SS8_ZA0_Table3_withoutwash');self.assertEqual((r['LOI_pct'],a['LOI_pct']),('38.2','38.3'));self.noTG(r);self.noTG(a);self.assertIn('NOTnewindependentsample',a['source_identity_limit'])
 def test_cotton_eight_washed_LOIs_no_initial_TG(self):
  rr=[r for r in self.subset(C)if r['treatment_state']=='washed'];self.assertEqual(len(rr),8)
  for r in rr:self.noTG(r);self.assertIn('IS687-197840rpm',r['source_wash_details']);self.assertIn('notAATCCmultiplier',r['source_wash_details'])
 def test_cotton_LOI_method_not_tenacity_or_inclined_dimensions(self):
  r=self.find(C,'ASSS_Control_initial');self.assertEqual(r['LOI_standard'],'ASTMD2863-77');self.assertIn('inclined150x50mmnotLOIdimensions;tenacity10/stiffness5notLOIreplicates',r['source_LOI_instrument_dimensions_repeats_uncertainty'])
 def test_cotton_loading_basis_not_gsm_calculated_addon(self):
  r=self.find(C,'ASSS_AS24_initial');self.assertIn('percentagebasisunreported',r['treatment_method']);self.assertIn('Table4gsmchange15.55notassumedFRwtpct',r['source_percentage_basis'])
 def test_public_facts_no_private_paths_or_contacts(self):
  for r in self.rows:self.assertFalse(any(('/'+'Volumes'+'/')in str(x)or('/'+'Users'+'/')in str(x)or('smb'+':'+chr(47)*2)in str(x)for x in r.values()))
if __name__=='__main__':unittest.main(verbosity=2)
