"""Protect native gas-condition pairing, unresolved source reuse and peak conflicts."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b164/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261004_b164_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing;import validate_tg_loi as v
A='10.1007/s10570-024-05944-3';B='10.1007/s10570-023-05540-x';C='10.1007/s10570-023-05306-5'
class TextileB164Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def subset(self,doi):return[r for r in self.rows if r['DOI']==doi]
 def find(self,doi,sample,gas=None):return next(r for r in self.subset(doi)if r['sample_state']==sample and(gas is None or r['atmosphere']==gas))
 def accepted(self):return[r for r in self.rows if r['pairing_status']=='verified_exact']
 def noTG(self,r):self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS))
 def test_five_independent_states_seven_conditions_not30facts(self):
  p=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(p['errors']);self.assertEqual((p['verified_exact_sample_states'],p['verified_exact_condition_records']),(5,7));self.assertEqual(len(self.rows),30)
 def test_all23held_excluded(self):
  held=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(held),23);self.assertEqual([sum(r['DOI']==d for r in held)for d in[A,B,C]],[17,3,3]);self.assertTrue(all(pairing.evidence_issues(r)for r in held))
 def test_review_fingerprints_reject_numeric_and_state_changes(self):
  for r in self.accepted():
   self.assertFalse(pairing.evidence_issues(r))
   for k,value in [('LOI_pct','99'),('T5_C','350'),('T10_C','350'),('Tmax1_C','555'),('R700_pct','77'),('atmosphere','oxygen'),('heating_rate_C_min','50'),('washing_state','50LC'),('sample_state','otherdose')]:self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**{k:value})))
 def test_all_pairs_fabric_not_fiber(self):
  for r in self.accepted():self.assertEqual(r['material_form_TGA'],'cotton fabric');self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='cotton fiber')))
 def test_all_journal_FPEC_facts_preserve_existing_preprint_hold(self):
  for r in self.subset(A):self.assertNotEqual(r['pairing_status'],'verified_exact');self.assertIn('10.21203/rs.3.rs-3748177/v1',r['source_version_reuse_hold']);self.assertIn('publicationversionnotindependentnewstate',r['source_version_reuse_hold'])
 def test_FPEC_native_profiles_not_counted_as_new(self):
  for s,values in [('Pristine',('312','374','4.8','18.5')),('PEC',('286','318','32.6','29')),('FPEC',('269','314','26.2','28.5'))]:
   r=self.find(A,'PEC_'+s+'_initial');self.assertEqual(tuple(r[k]for k in['T5_C','Tmax1_C','R700_pct','LOI_pct']),values);self.assertFalse(r.get('Tonset_C'));self.assertFalse(r.get('reviewed_measurement_fingerprint'))
 def test_FPEC_TG_remaining_mass_temperature_bounds_not_cone(self):
  r=self.find(A,'PEC_Pristine_initial');self.assertEqual((r['R300_pct'],r['R370_pct']),('96','52.6'));r=self.find(A,'PEC_PEC_initial');self.assertEqual((r['R300_pct'],r['R370_pct'],r['residue_temp_C']),('90.8','48.6','700'));self.assertIn('notcone0/13.2/10',r['source_residue_definition'])
 def test_FPEC_LOI_conflict_and_specific_Fdose_not_assumed(self):
  r=self.find(A,'PEC_FPEC_initial');self.assertIn('bodycoatedPECandFPECLOI29vsTable2FPEC28.5',r['source_FPEC_conflict']);self.assertIn('WholeFPECconditionheld',r['source_FPEC_conflict']);self.assertIn('notexplicitlyjoined',r['treatment_method'])
 def test_all_four_Fdose_SI_LOIs_remain_unjoined(self):
  for dose,loi in [('0.1','27'),('0.5','28.5'),('0.75','27.5'),('1','29')]:
   r=self.find(A,'PEC_F'+dose+'pct_SI_initial');self.assertEqual(r['LOI_pct'],loi);self.noTG(r);self.assertIn('possiblysameinitialgenericFPEC',r['source_state_join_limit']);self.assertIn('notfabricmassfraction',r['composition'])
 def test_FPEC_all_ten_washed_LOIs_NO_initial_TG(self):
  rows=[r for r in self.subset(A)if r['treatment_state']=='washed'];self.assertEqual(len(rows),10)
  for r in rows:self.noTG(r);self.assertIn('40plusminus2C_800rpm_30min_70C4hdry',r['washing_state']);self.assertIn('zeroWsameinitialnotnewidentity',r['source_zero_wash_rule'])
  self.assertEqual(self.find(A,'PEC_FPEC_after20W')['LOI_pct'],'26.5');self.assertEqual(self.find(A,'PEC_PEC_after20W')['LOI_pct'],'18.5')
 def test_APPEHA_all_four_native_T10_profiles(self):
  for gas,expected in [('N2',{'Control':('342','376','8.9'),'30':('246','286','40.2')}),('air',{'Control':('335','363','0.8'),'30':('249','283','21.1')})]:
   for s,values in expected.items():r=self.find(B,'APPEHA_'+s+'_initial',gas);self.assertEqual(tuple(r[k]for k in['T10_C','Tmax1_C','R700_pct']),values);self.assertFalse(r.get('T5_C'));self.assertFalse(r.get('Tonset_C'))
 def test_APPEHA_two_gases_share_same_initial_state(self):
  rows=[r for r in self.subset(B)if r['pairing_status']=='verified_exact'];self.assertEqual(len(rows),4);self.assertEqual(len({r['sample_state']for r in rows}),2)
  for s in ['Control','30']:
   n=self.find(B,'APPEHA_'+s+'_initial','N2');a=self.find(B,'APPEHA_'+s+'_initial','air');self.assertEqual(n['LOI_pct'],a['LOI_pct']);self.assertEqual(n['washing_state'],a['washing_state']);self.assertEqual(n['treatment_method'],a['treatment_method'])
 def test_APPEHA_R700_explicit_body_not_cone_or_bulkFR(self):
  for r in self.subset(B):
   if r['pairing_status']=='verified_exact':self.assertEqual(r['residue_temp_C'],'700');self.assertIn('boundat700byownThermaldegradationbody',r['source_residue_definition']);self.assertIn('notcone5.0/20.9orbulkAPPEHA22.6',r['source_residue_definition'])
 def test_APPEHA_standalone_TG_not_TGFTIR_start30(self):
  for r in self.subset(B):
   if r['pairing_status']=='verified_exact':self.assertEqual((r['TGA_instrument'],r['TG_start_C'],r['TG_end_C'],r['heating_rate_C_min'],r['source_TGA_mass_mg']),('Pyris1','25','700','20','3-5'));self.assertIn('separateTGFTIR30-700norampnotborrowed',r['source_TGIR_exclusion'])
 def test_APPEHA_explicit_own_LOI_and_control_preparation(self):
  for s,loi in [('Control','18'),('30','48.9')]:r=self.find(B,'APPEHA_'+s+'_initial','N2');self.assertEqual(r['LOI_pct'],loi);self.assertEqual(r['source_LOI_numeric_evidence_type'],'explicit_text');self.assertEqual(r['LOI_standard'],'ASTMD2863-2000')
  self.assertIn('20wtNaOHRT10min',self.find(B,'APPEHA_Control_initial','N2')['treatment_method']);self.assertIn('132.92gsm',self.find(B,'APPEHA_Control_initial','N2')['composition'])
 def test_APPEHA_bath_30_not_WG23_and_other_doses_not_estimated(self):
  r=self.find(B,'APPEHA_30_initial','N2');self.assertEqual((r['source_bath_APPEHA_pct'],r['source_weight_gain_pct']),('30','23'))
  for dose,wg in [('20','18.2'),('25','21.2')]:r=self.find(B,'APPEHA_'+dose+'_initial');self.assertFalse(r['LOI_pct']);self.noTG(r);self.assertEqual(r['source_weight_gain_pct'],wg);self.assertIn('curveimagesunreadnotestimated',r['source_missing_measurements'])
 def test_APPEHA_50LC_LOI42_7_has_no_initial_TG(self):
  r=self.find(B,'APPEHA_30_after50LC');self.assertEqual(r['LOI_pct'],'42.7');self.noTG(r);self.assertIn('reported50LCkeptnotmultiplied',r['source_wash_details']);self.assertIn('71C50mL100steelballs45min',r['source_wash_details'])
 def test_PAzP_three_accepted_profiles_T5_not_Tonset(self):
  for s,values in [(0,('296','381','3.8','19')),(1,('251','349','28.4','25.4')),(2,('247','324','35.8','28.8'))]:
   r=self.find(C,'PAzP_Cotton'+str(s)+'_initial');self.assertEqual(tuple(r[k]for k in['T5_C','Tmax1_C','R700_pct','LOI_pct']),values);self.assertFalse(r.get('T10_C'));self.assertFalse(r.get('Tonset_C'));self.assertEqual(r['pairing_status'],'verified_exact')
 def test_PAzP_Cotton3_Tmax316vs314_holds_whole_pair(self):
  r=self.find(C,'PAzP_Cotton3_initial');self.assertEqual((r['Tmax1_C'],r['T5_C'],r['R700_pct'],r['LOI_pct']),('316','251','37.1','33.3'));self.assertEqual(r['pairing_status'],'held_Tmax_table_body_conflict');self.assertIn('Table2Tmax316vsThermaldegradationbody314',r['source_Tmax_conflict']);self.assertIn('nocherrypickunaffectedT5/R700',r['source_Tmax_conflict'])
 def test_PAzP_standalone_program_and_distinct_repeats(self):
  for r in self.subset(C):
   if r['treatment_state']=='initial':self.assertEqual((r['TG_start_C'],r['TG_end_C'],r['heating_rate_C_min'],r['source_TGA_flow_mL_min'],r['source_TGA_repeats'],r['source_LOI_repeats']),('40','700','10','20','1','5'));self.assertEqual(r['source_LOI_dimensions_mm'],'150x58')
 def test_PAzP_DTG_rate_and_bath_vs_addon(self):
  for s,dose,wg,rate in [(1,'5','7.5','13.9'),(2,'7.5','10.3','26.3'),(3,'10','11.8','24.9')]:r=self.find(C,'PAzP_Cotton'+str(s)+'_initial');self.assertEqual((r['source_bath_PAzP_pct'],r['source_weight_gain_pct'],r['source_DTGmax_pct_per_min']),(dose,wg,rate));self.assertIn('DTGmaxpctperminnotpctperC',r['source_metric_definition'])
 def test_PAzP_synthesis_name_conflict_preserved_not_inferred_chemistry(self):
  for r in self.subset(C):
   if r['treatment_state']=='initial':self.assertIn('MaterialsphosphorousacidvsPreparationphosphoricacidunresolved',r['source_synthesis_reagent_conflict']);self.assertIn('donotassignacidchoice/Poxidationstate',r['source_synthesis_reagent_conflict'])
 def test_PAzP_washed_LOIs_no_initialTG_or_5x_count(self):
  for cycle,loi in [('10','30.7'),('30','27.8')]:r=self.find(C,'PAzP_Cotton3_after'+cycle+'LC');self.assertEqual(r['LOI_pct'],loi);self.noTG(r);self.assertIn('reported10/30LCnotmultiplied',r['source_wash_details']);self.assertIn('body10LCcharlength97vsTable398',r['source_wash_TG_limit'])
 def test_PAzP_SI_has_no_Tmax_correction(self):
  r=self.find(C,'PAzP_Cotton3_initial');self.assertIn('zeroSItables',r['source_SI_review']);self.assertIn('noTG/Tmaxcorrection',r['source_SI_review']);self.assertIn('embeddedimagesunread',r['source_SI_review'])
 def test_public_facts_no_privatepaths_or_contacts(self):
  for r in self.rows:self.assertRegex(r['evidence_reviewed_at'],r'^\d{4}-\d{2}-\d{2}$');self.assertFalse(any(('/'+'Volumes'+'/')in str(x)or('/'+'Users'+'/')in str(x)or('smb'+':'+chr(47)*2)in str(x)or'@126.com'in str(x)for x in r.values()))
if __name__=='__main__':unittest.main(verbosity=2)
