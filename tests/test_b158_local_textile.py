"""Protect native sample states, source contradictions and assay-specific conditions."""
import csv,json,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b158/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261004_b158_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing;import validate_tg_loi as v
A='10.1007/s10570-024-05814-y';B='10.1007/s12221-023-00445-9';C='10.1007/s10570-024-06121-2'
class TextileB158Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def subset(self,d):return[r for r in self.rows if r['DOI']==d]
 def find(self,d,s,gas=None):return next(r for r in self.subset(d)if r['sample_state']==s and(gas is None or r['atmosphere']==gas))
 def accepted(self):return[r for r in self.rows if r['pairing_status']=='verified_exact']
 def no_tg(self,r):self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS))
 def test_three_states_five_conditions_not31facts(self):
  p=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(p['errors']);self.assertEqual((p['verified_exact_sample_states'],p['verified_exact_condition_records']),(3,5));self.assertEqual(len(self.rows),31)
 def test_all26_holds_excluded(self):
  held=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(held),26);self.assertEqual([sum(r['DOI']==d for r in held)for d in [A,B,C]],[13,10,3]);self.assertTrue(all(pairing.evidence_issues(r)for r in held))
 def test_accepted_fingerprints_bind_numeric_values_and_state(self):
  for r in self.accepted():
   self.assertFalse(pairing.evidence_issues(r))
   for k,x in [('LOI_pct','99'),('Tmax1_C','777'),('sample_state','Otherdose'),('washing_state','after50LC'),('atmosphere','Ar'),('heating_rate_C_min','60')]:self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**{k:x})))
 def test_fabric_not_standalone_fiber_or_bulkFR(self):
  for r in self.accepted():self.assertEqual(r['material_form_TGA'],'cotton fabric');self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='cotton fiber')))
  for r in self.rows:
   if r['sample_state'] in {'CPAS_Cotton_initial','BPNFR_CF0_initial','GluCa_COT_initial'}:self.assertEqual(r['washing_state'],'initial_unwashed_control_preparation_unreported')
 def test_CPAS_T10_T50_notT5_Tonset_or_water_peak(self):
  r=self.find(A,'CPAS_Cotton_initial','N2');self.assertEqual((r['T10_C'],r['T50_C'],r['Tmax1_C']),('248.9','341.6','340.4'));self.assertFalse(r.get('T5_C'));self.assertFalse(r.get('Tonset_C'));self.assertIn('notT5/Tonset',r['source_T10_T50_definition'])
 def test_CPAS_residue800_not_waterloss_or_cone(self):
  r=self.find(A,'CPAS_Cotton_initial','air');self.assertEqual((r['R800_pct'],r['residue_temp_C'],r['TG_end_C']),('1.8','800','800'));self.assertEqual(self.find(A,'CPAS_Cotton_initial','N2')['R800_pct'],'15.5')
 def test_CPAS_two_gases_one_own_control_state(self):
  rows=[r for r in self.subset(A)if r['pairing_status']=='verified_exact'];self.assertEqual(len(rows),2);self.assertEqual({r['sample_state']for r in rows},{'CPAS_Cotton_initial'});self.assertEqual({r['LOI_pct']for r in rows},{'18'})
 def test_CPAS_control_no_FR_cure_or_assumed_NaOH(self):
  r=self.find(A,'CPAS_Cotton_initial','air');self.assertIn('pretreatmentstateunreported',r['treatment_method']);self.assertIn('notassignedFR170Ccure',r['treatment_method']);self.assertEqual((r['TG_start_C'],r['heating_rate_C_min']),('25','20'))
 def test_CPAS_all6_treated_gas_conditions_doseheld(self):
  rows=[r for r in self.subset(A)if r['R800_pct']and r['sample_state']!='CPAS_Cotton_initial'];self.assertEqual(len(rows),6);self.assertTrue(all('dose_binding_conflicts'in r['pairing_status']for r in rows));self.assertTrue(all('H6wtversusH5/10/15'in r['source_recipe_conflicts']for r in rows))
 def test_CPAS_native_LOI_and_residue_conflicts_retained(self):
  r=self.find(A,'CPAS_FRH_initial','N2');self.assertEqual((r['LOI_pct'],r['R800_pct']),('34.3','34.2'));self.assertIn('34.21',r['source_residue_rounding_conflict']);self.assertIn('ashigh31',r['source_LOI_conclusion_conflict']);self.assertIn('FRH4wtversusFig9FRH10',r['source_recipe_conflicts'])
 def test_CPAS_washed7_LOI_facts_do_not_borrow_initialTG(self):
  rows=[r for r in self.subset(A)if r['treatment_state']=='washed'];self.assertEqual(len(rows),7)
  for r in rows:self.no_tg(r);self.assertIn('TGMX02-2018No2A',r['washing_state'])
  self.assertEqual(self.find(A,'CPAS_FRH_after20LC')['LOI_pct'],'33.1');self.assertEqual(self.find(A,'CPAS_FR_after50LC')['LOI_pct'],'32.9')
 def test_BPNFR_all6_TG_held_endpoint_contradiction(self):
  rows=[r for r in self.subset(B)if r['R800_pct']];self.assertEqual(len(rows),6)
  for r in rows:self.assertEqual((r['TG_end_C'],r['residue_temp_C']),('750','800'));self.assertIn('end750',r['pairing_status']);self.assertIn('TGIR35-800notstandalone',r['source_TG_end_residue_conflict'])
 def test_BPNFR_air_T5_T10_not_swapped_to_hide_conflict(self):
  for s,values in [('CF0',('294','251')),('CF15',('313','291'))]:
   r=self.find(B,'BPNFR_'+s+'_initial','air');self.assertEqual((r['T5_C'],r['T10_C']),values);self.assertIn('notcolumns-swapped',r['source_air_threshold_conflict']);self.assertNotEqual(r['pairing_status'],'verified_exact')
 def test_BPNFR_native_N2_thresholds_peak_residue_no_relative_conversion(self):
  r=self.find(B,'BPNFR_CF5_initial','N2');self.assertEqual(tuple(r[k]for k in ['T5_C','T10_C','Tmax1_C','R800_pct']),('267','301','326','36.86'));self.assertNotEqual(r['R800_pct'],'36.852');self.assertFalse(r['Tmax2_C'])
 def test_BPNFR_air_second_peaks_preserved_not_water100(self):
  self.assertEqual(self.find(B,'BPNFR_CF0_initial','air')['Tmax2_C'],'490');self.assertEqual(self.find(B,'BPNFR_CF15_initial','air')['Tmax2_C'],'509');self.assertEqual(self.find(B,'BPNFR_CF0_initial','N2')['Tmax1_C'],'364')
 def test_BPNFR_STANDALONE_not_TGIR_flow_program(self):
  r=self.find(B,'BPNFR_CF15_initial','N2');self.assertEqual((r['TGA_instrument'],r['TG_start_C'],r['heating_rate_C_min']),('TG209F3 Netzsch','35','10'));self.assertIn('50mLminnotborrowed',r['source_TG_mass_pan_repeats']);self.assertIn('SeparateSTA449F3',r['source_TGIR_method'])
 def test_BPNFR_measured_WG_not_bath_or_final_fraction(self):
  r=self.find(B,'BPNFR_CF10_initial','N2');self.assertEqual((r['source_weight_gain_wt_pct'],r['LOI_pct']),('10.79','33.3'));self.assertIn('measuredWGnotbath/finalfraction',r['composition'])
 def test_BPNFR_washed4_LOI_only_and_option1A(self):
  rows=[r for r in self.subset(B)if r['treatment_state']=='washed'];self.assertEqual([r['LOI_pct']for r in rows],['35.7','33.2','30.8','28.5'])
  for r in rows:self.no_tg(r);self.assertIn('option1A',r['washing_state'])
 def test_GluCa_native_onset_not_T5(self):
  r=self.find(C,'GluCa_COT_GluCa_initial','air');self.assertEqual((r['Tonset_C'],r['Tmax1_C'],r['R800_pct']),('221.5','291.3','5.6'));self.assertFalse(r.get('T5_C'));self.assertIn('criterionnotexplicit5/10',r['source_Tonset_definition'])
 def test_GluCa_own_control_LOI17point8_not_arithmetic_estimate(self):
  rows=[r for r in self.subset(C)if r['sample_state']=='GluCa_COT_initial'];self.assertEqual(len(rows),2);self.assertTrue(all(r['LOI_pct']=='17.8'and r['pairing_status']=='verified_exact'for r in rows));self.assertEqual([r['R800_pct']for r in rows],['8.1','0.03'])
 def test_GluCa_treatedN2_Tmax_conflict_held_without_cherry_pick(self):
  r=self.find(C,'GluCa_COT_GluCa_initial','N2');self.assertEqual(r['Tmax1_C'],'287.8');self.assertIn('body270.5',r['source_treated_N2_Tmax_conflict']);self.assertNotEqual(r['pairing_status'],'verified_exact');self.assertEqual(self.find(C,'GluCa_COT_GluCa_initial','air')['pairing_status'],'verified_exact')
 def test_GluCa_Ga_rawlabel_does_not_create_new_Ga_formula(self):
  r=self.find(C,'GluCa_COT_GluCa_initial','air');self.assertEqual(r['source_native_TG_sample_label'],'COT-Glu–Ga');self.assertIn('typographicinference',r['source_TG_label_adjudication']);self.assertIn('onlyCaCl2recipe',r['source_TG_label_adjudication']);self.assertIn('noGachemistryinvented',r['source_TG_label_adjudication'])
 def test_GluCa_washed_rechelated_states_do_not_borrow_initialTG(self):
  rows=[r for r in self.subset(C)if r['treatment_state']in ['washed','washed_rechelated']];self.assertEqual([r['LOI_pct']for r in rows],['20.9','31.7']);self.assertNotEqual(rows[0]['washing_state'],rows[1]['washing_state'])
  for r in rows:self.no_tg(r);self.assertIn('own_TG_unreported',r['pairing_status'])
 def test_GluCa_intermediatechemicalstates_not_invented_pairs(self):
  rows=self.subset(C);self.assertEqual(len(rows),6);self.assertTrue(all(not any(k in r['sample_state']for k in ['COT_M_','COT_CMC_','COT_DCMC_','COT_Glu_initial'])for r in rows));self.assertTrue(all(r['LOI_standard']==''for r in rows if r['R800_pct']))
 def test_native_DTG_rate_units_not_residue_or_converted(self):
  r=self.find(A,'CPAS_Cotton_initial','air');self.assertEqual(r['source_DTGmax_pct_per_min'],'9.6');r=self.find(B,'BPNFR_CF0_initial','N2');self.assertEqual(r['source_DTGmax1_pct_per_C'],'1.59');self.assertIn('notpercentpermin',r['source_DTG_rate_definition']);r=self.find(C,'GluCa_COT_GluCa_initial','air');self.assertEqual(r['source_DTGmax_pct_per_min'],'4.4');self.assertNotEqual(r['R800_pct'],'4.4')
if __name__=='__main__':unittest.main(verbosity=2)
