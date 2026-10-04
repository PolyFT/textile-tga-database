"""Protect reported TG metrics, missing LOI and unresolved ordinary TG rate units."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b165/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261004_b165_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing;import validate_tg_loi as v
A='10.1007/s10570-023-05541-w';B='10.1007/s10570-024-05860-6';C='10.1007/s10570-024-06338-1'
class TextileB165Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def subset(self,doi):return[r for r in self.rows if r['DOI']==doi]
 def find(self,doi,sample,gas=None):return next(r for r in self.subset(doi)if r['sample_state']==sample and(gas is None or r['atmosphere']==gas))
 def accepted(self):return[r for r in self.rows if r['pairing_status']=='verified_exact']
 def noTG(self,r):self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS))
 def test_two_states_three_conditions_not28facts(self):
  p=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(p['errors']);self.assertEqual((p['verified_exact_sample_states'],p['verified_exact_condition_records']),(2,3));self.assertEqual(len(self.rows),28)
 def test_all25held_excluded(self):
  rows=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(rows),25);self.assertEqual([sum(r['DOI']==d for r in rows)for d in[A,B,C]],[7,8,10]);self.assertTrue(all(pairing.evidence_issues(r)for r in rows))
 def test_review_fingerprints_reject_changed_numbers_states_and_conditions(self):
  for r in self.accepted():
   self.assertFalse(pairing.evidence_issues(r))
   for k,value in [('LOI_pct','99'),('T5_C','300'),('Tmax1_C','555'),('R700_pct','77'),('atmosphere','oxygen'),('heating_rate_C_min','50'),('washing_state','50LC'),('sample_state','otherdose')]:self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**{k:value})))
 def test_valid_pairs_fabric_not_fiber(self):
  for r in self.accepted():self.assertEqual(r['material_form_TGA'],'cotton fabric');self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='cotton fiber')))
 def test_BNCD_all_seven_TG_profiles_have_no_independent_LOI(self):
  self.assertEqual(len(self.subset(A)),7)
  for r in self.subset(A):self.assertFalse(r['LOI_pct']);self.assertIn('noownLOIorLOImethod',r['source_LOI_missing_scope']);self.assertNotEqual(r['pairing_status'],'verified_exact')
 def test_BNCD_native_T5_Tmax_and_R700_not_UPF_or_MCC(self):
  for s,expected in [('Cotton',('280.8','384.8','10')),('Cotton-4BL',('280.3','377.9','10.1')),('Cotton-8BL',('272.5','378.2','10.4')),('Cotton-12BL',('250.9','379.7','10.8')),('Cotton-CDs-4BL',('240.4','377.2','10.7')),('Cotton-CDs-8BL',('209.4','377.4','11.6')),('Cotton-CDs-12BL',('194.2','377.4','12.4'))]:r=self.find(A,'BNCD_'+s+'_initial');self.assertEqual(tuple(r[k]for k in['T5_C','Tmax1_C','R700_pct']),expected);self.assertFalse(r.get('Tonset_C'));self.assertEqual(r['residue_temp_C'],'700')
 def test_BNCD_standalone_program_not_MCC_one_C_per_second(self):
  for r in self.subset(A):self.assertEqual((r['TGA_instrument'],r['TG_start_C'],r['TG_end_C'],r['heating_rate_C_min']),('TGAQ5000','50','700','20'));self.assertIn('MCC1Cpersecond',r['source_MCC_exclusion'])
 def test_BNCD_replication_and_PF_state_scope_conflicts_retained(self):
  for r in self.subset(A):self.assertIn('DedicatedTGAparagraphn1vsMCCparagraphsaysTGA3',r['source_TGA_repeats_conflict']);self.assertIn('MethodsfinallyPF206versusResultsseparate12BL-H',r['source_PF_state_join_limit']);self.assertIn('notLOI/TG',r['source_wash_TG_limit'])
 def test_DOPSPAP_all_three_accepted_native_numeric_conditions(self):
  for gas,s,expected in [('N2','Control',('377','3.7','17.4')),('N2','25',('296','38.5','44.5')),('air','25',('297','14.2','44.5'))]:
   r=self.find(B,'DOPSPAP_'+s+'_initial',gas);self.assertEqual(tuple(r[k]for k in['Tmax1_C','R700_pct','LOI_pct']),expected);self.assertEqual(r['pairing_status'],'verified_exact')
 def test_DOPSPAP_unknown_initial_decomposition_criterion_not_T5_T10_Tonset(self):
  for gas,s,raw in [('N2','Control','318'),('N2','25','245'),('air','25','242')]:
   r=self.find(B,'DOPSPAP_'+s+'_initial',gas);self.assertEqual(r['source_initial_decomposition_temperature_C'],raw);self.assertTrue(all(not r.get(k)for k in['T5_C','T10_C','Tonset_C']));self.assertIn('notassignT5/T10/Tonset',r['source_initial_decomposition_criterion'])
 def test_DOPSPAP_standalone_gas_ramp_mass_and_temperature(self):
  for r in self.accepted():self.assertEqual((r['TGA_instrument'],r['TG_start_C'],r['TG_end_C'],r['heating_rate_C_min'],r['source_TGA_mass_mg']),('Pyris1','40','700','20','3-5'));self.assertIn('TGIRsameprogramnotneededforjoin',r['source_TGIR_exclusion'])
 def test_DOPSPAP_two_gases_not_two_independent_25_samples(self):
  rows=[r for r in self.accepted()if r['sample_state']=='DOPSPAP_25_initial'];self.assertEqual(len(rows),2);self.assertEqual(len({r['washing_state']for r in rows}),1);self.assertEqual(len({r['treatment_method']for r in rows}),1);self.assertEqual(len({r['LOI_pct']for r in rows}),1)
 def test_DOPSPAP_control_preparation_unknowns_not_borrowed(self):
  r=self.find(B,'DOPSPAP_Control_initial','N2');self.assertIn('NaOH10min;temperature/rinse/dryunreported',r['treatment_method']);self.assertIn('138.32gsm',r['composition']);r=self.find(B,'DOPSPAP_25_initial','N2');self.assertEqual((r['source_bath_DOPSPAP_pct'],r['source_weight_gain_pct']),('25','20.9'));self.assertIn('175C5min',r['treatment_method'])
 def test_DOPSPAP_air_control_qualitative_completely_decomposed_not_zero(self):
  r=self.find(B,'DOPSPAP_Control_initial','air');self.noTG(r);self.assertEqual(r['pairing_status'],'held_aircontrol_numeric_TG_unreported');self.assertIn('notnumericzero',r['source_aircontrol_residue_qualitative']);self.assertEqual((r['source_aircontrol_stage1_C'],r['source_aircontrol_stage2_C']),('313-365','365-502'))
 def test_DOPSPAP_R700_not_cone12_89(self):
  for r in self.accepted():self.assertEqual(r['residue_temp_C'],'700');self.assertIn('notcone12.89',r['source_residue_definition']);self.assertNotEqual(r['R700_pct'],'12.89')
 def test_DOPSPAP_other_doses_have_no_borrowed_TG_or_curve_estimates(self):
  r=self.find(B,'DOPSPAP_15_initial');self.assertEqual((r['LOI_pct'],r['source_weight_gain_pct']),('38.8','15.8'));self.noTG(r);r=self.find(B,'DOPSPAP_20_initial');self.assertFalse(r['LOI_pct']);self.assertFalse(r['source_weight_gain_pct']);self.noTG(r)
 def test_DOPSPAP_all_three_50LC_LOIs_no_initial_TG(self):
  for dose,value in [('15','26.9'),('20','31.5'),('25','34.5')]:r=self.find(B,'DOPSPAP_'+dose+'_after50LC');self.assertEqual(r['LOI_pct'],value);self.noTG(r);self.assertIn('reportedLCnot5xmapping',r['source_wash_details']);self.assertIn('71C45min.15pctdetergent100steelballs',r['source_wash_details'])
 def test_DOPSAP_comparators_not_own_new_pairs(self):
  for s,loi in [('initial','45.6'),('after50LC','29.3')]:r=self.find(B,'DOPSAP_comparator_'+s);self.assertEqual(r['LOI_pct'],loi);self.noTG(r);self.assertIn('ownMethodsnotitsfabricpreparation/ownTG',r['source_comparator_provenance'])
 def test_PZF_native10_C_per_second_preserved_not_corrected10_per_minute(self):
  rows=[r for r in self.subset(C)if r['treatment_state']=='initial'];self.assertEqual(len(rows),8)
  for r in rows:self.assertEqual(r['heating_rate_C_min'],'600');self.assertEqual((r['source_heating_rate_raw'],r['source_heating_rate_raw_unit'],r['source_heating_rate_equivalent_C_min']),('10','C_per_second','600'));self.assertIn('notcorrected10c/min',r['source_rate_hold'].lower());self.assertNotEqual(r['pairing_status'],'verified_exact')
 def test_Q50_600_C_min_exceeds_manufacturer_limit_and_stays_held(self):
  rows=[r for r in self.subset(C)if r['treatment_state']=='initial']
  for r in rows:self.assertEqual(float(r['source_heating_rate_raw'])*60,float(r['heating_rate_C_min']));self.assertGreater(float(r['heating_rate_C_min']),float(r['source_Q50_controlled_heating_rate_max_C_min']));self.assertIn('printedpage40;PDFpage7of27',r['source_Q50_specification_locator']);self.assertTrue(pairing.evidence_issues(r))
  report=v.build_tables(pd.DataFrame(rows).fillna(''),v.issue_list())[3];self.assertFalse(report['errors']);self.assertEqual(report['verified_exact_sample_states'],0)
 def test_PZF_native_T10_and_R700_all_gas_conditions(self):
  for gas,expected in [('N2',{'CF':('321.4','369.6','6.8'),'CF-PA':('279','304.8','27.4'),'CF-PZF':('257.1','295.1','31.6'),'CF-PZF/PDMS':('264.2','291.2','35.7')}),('air',{'CF':('305.5','333.8','1.5'),'CF-PA':('269.3','298.6','14.8'),'CF-PZF':('276.3','288.8','16.5'),'CF-PZF/PDMS':('233.6','282.3','20.2')})]:
   for s,values in expected.items():r=self.find(C,'PZF_'+s+'_initial',gas);self.assertEqual(tuple(r[k]for k in['T10_C','Tmax1_C','R700_pct']),values);self.assertFalse(r.get('T5_C'));self.assertFalse(r.get('Tonset_C'))
 def test_PZF_SI_and_TGIR_not_ordinary_rate_correction(self):
  for r in self.subset(C):
   if r['treatment_state']=='initial':self.assertIn('SeparateTGA55N240-70010C/minnotTable1Q50',r['source_TGIR_exclusion']);self.assertIn('noTGmethodcorrection',r['source_SI_review']);self.assertIn('ElementTableS1wtcontentsnotfinalwhole-fabric',r['source_EDS_composition_limit'])
 def test_PZF_two_washed_LOIs_no_initialTG(self):
  for cycle,value in [('10','31.5'),('20','29.6')]:r=self.find(C,'PZF_CF-PZF_PDMS_after'+cycle+'LC');self.assertEqual(r['LOI_pct'],value);self.noTG(r);self.assertIn('200mLaqueous40plusminus2C45min',r['source_wash_details']);self.assertIn('reportedLCnot5x',r['source_wash_details'])
 def test_public_facts_no_private_paths_or_contacts(self):
  for r in self.rows:self.assertRegex(r['evidence_reviewed_at'],r'^\d{4}-\d{2}-\d{2}$');self.assertFalse(any(('/'+'Volumes'+'/')in str(x)or('/'+'Users'+'/')in str(x)or('smb'+':'+chr(47)*2)in str(x)or'@163.com'in str(x)for x in r.values()))
if __name__=='__main__':unittest.main(verbosity=2)
