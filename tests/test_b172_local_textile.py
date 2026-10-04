"""Prevent missing LOI, ramp and recipe evidence from becoming valid pairs."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b172/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261004_b172_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing;import validate_tg_loi as v
A='10.1007/s10570-025-06897-x';B='10.1007/s10570-026-06988-3';C='10.1007/s12221-026-01505-6'
class TextileB172Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def subset(self,d):return[r for r in self.rows if r['DOI']==d]
 def find(self,d,s,g=''):return next(r for r in self.rows if r['DOI']==d and r['sample_state']==s and r['atmosphere']==g)
 def noTG(self,r):self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS))
 def test_fact_counts_are_not_valid_pairs(self):
  q=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(q['errors']);self.assertEqual((len(self.rows),q['verified_exact_sample_states'],q['verified_exact_condition_records']),(27,0,0));self.assertEqual([len(self.subset(d))for d in[A,B,C]],[13,9,5])
 def test_every_fact_remains_excluded(self):self.assertTrue(all(r['pairing_status']!='verified_exact'and pairing.evidence_issues(r)for r in self.rows))
 def test_flax_has_no_independent_LOI(self):self.assertTrue(all(not r['LOI_pct']for r in self.subset(A)))
 def test_flax_native_N2_profiles(self):
  for s,e in [('Pure',('316','360','','319','18')),('PD5',('215','232','301','210','43')),('PDPD5',('198','216','276','208','46')),('PD10',('215','232','304','217','45')),('PDPD10',('224','254','291','238','48'))]:self.assertEqual(tuple(self.find(A,'FLAX_'+s+'_initial','N2').get(k,'')for k in['T10_C','Tmax1_C','Tmax2_C','Tonset_C','R800_pct']),e)
 def test_flax_native_air_profiles(self):
  for s,e in [('Pure',('292','340','466','298','0')),('PD5',('192','223','507','199','14')),('PDPD5',('201','223','730','198','15')),('PD10',('182','211','708','185','21')),('PDPD10',('208','231','733','213','13'))]:self.assertEqual(tuple(self.find(A,'FLAX_'+s+'_initial','air')[k]for k in['T10_C','Tmax1_C','Tmax2_C','Tonset_C','R800_pct']),e)
 def test_flax_criteria_remain_separate(self):
  for r in self.subset(A):
   self.assertFalse(r.get('T5_C'))
   if r['washing_state']=='initial':self.assertNotEqual(r['T10_C'],r['Tonset_C'])
 def test_flax_high_air_peaks_not_clipped(self):
  for s in['PDPD5','PD10','PDPD10']:self.assertLess(float(self.find(A,'FLAX_'+s+'_initial','air')['Tmax2_C']),800)
 def test_flax_explicit_residue_endpoint(self):self.assertTrue(all(r['residue_temp_C']=='800'and r['heating_rate_C_min']=='10'for r in self.subset(A)))
 def test_flax_initial_SI_repeats_not_extra_tests(self):self.assertEqual(sum(r['washing_state']=='initial'for r in self.subset(A)),10)
 def test_flax_three_leach_profiles_without_LOI(self):
  for h,e in[(8,('234','257','38')),(16,('243','263','30')),(24,('252','284','27'))]:r=self.find(A,f'FLAX_PDPD10_after{h}hleach','N2');self.assertEqual(tuple(r[k]for k in['T10_C','Tmax1_C','R800_pct']),e);self.assertFalse(r['LOI_pct']);self.assertEqual(r['treatment_state'],'leached')
 def test_PN_all_seven_TG_conditions_missing_ramp(self):
  rr=[r for r in self.subset(B)if r['atmosphere']];self.assertEqual(len(rr),7);self.assertTrue(all(not r['heating_rate_C_min']and r['pairing_status']=='held_ordinary_TG_heating_rate_unreported'for r in rr))
 def test_PN_ordinary_peaks_not_TGIR(self):self.assertEqual((self.find(B,'PN_CF_initial','N2')['Tmax1_C'],self.find(B,'PN_DT30_initial','N2')['Tmax1_C']),('365','301'))
 def test_PN_native_N2_residues(self):
  for s,z in[('CF','4.8'),('DT20','17.1'),('DT25','25.3'),('DT30','34.3')]:self.assertEqual(self.find(B,'PN_'+s+'_initial','N2')['R700_pct'],z)
 def test_PN_native_air_residues(self):
  for s,z in[('DT20','1.3'),('DT25','3.4'),('DT30','6.7')]:self.assertEqual(self.find(B,'PN_'+s+'_initial','air')['R700_pct'],z)
 def test_PN_unknown_air_control_is_not_numeric_zero(self):self.assertFalse(any(r['sample_state']=='PN_CF_initial'and r['atmosphere']=='air'for r in self.subset(B)))
 def test_PN_washed_states_do_not_borrow_TG(self):
  for r in self.subset(B):
   if r['treatment_state']=='washed':self.noTG(r)
 def test_PN_source_mean_of_three_not_unknown_repeats(self):self.assertTrue(all(r['source_LOI_repetitions']=='3'for r in self.subset(B)if r['atmosphere']))
 def test_rapeseed_native_TG_and_units(self):
  for s,e in[('Control',('320.47','353.10','21.71','11.60')),('HPRm',('248.63','278.60','14.40','33.32'))]:self.assertEqual(tuple(self.find(C,'RAPE_'+s+'_initial','N2')[k]for k in['T10_C','Tmax1_C','source_DTG_Vmax_pct_per_min','R800_pct']),e)
 def test_rapeseed_control_does_not_gain_inferred_LOI(self):self.assertFalse(self.find(C,'RAPE_Control_initial','N2')['LOI_pct'])
 def test_rapeseed_optimization_and_final_LOIs_not_interchanged(self):self.assertEqual((self.find(C,'RAPE_HPRm_initial','N2')['LOI_pct'],self.find(C,'RAPE_HPRm90_optimization')['LOI_pct']),('39.4','39.1'));self.noTG(self.find(C,'RAPE_HPRm90_optimization'))
 def test_rapeseed_entire_condition_held_for_recipe_correspondence(self):r=self.find(C,'RAPE_HPRm_initial','N2');self.assertEqual(r['pairing_status'],'held_recipe_and_initial_LOI_correspondence_unresolved');self.assertIn('MethodsDCD40gL+MAP40gL+urea20gLvsResultsDCD40alone',r['treatment_method'])
 def test_rapeseed_washed_states_not_initial_TG(self):
  for r in self.subset(C):
   if r['treatment_state']=='washed':self.noTG(r)
 def test_rapeseed_ordinary_start_not_TGIR(self):self.assertTrue(all(tuple(r[k]for k in['TG_start_C','TG_end_C','heating_rate_C_min'])==('30','800','10')for r in self.subset(C)if r['atmosphere']))
 def test_online_first_identity_preserves_missing_issue(self):self.assertTrue(all(r['year']=='2026'and'online publication date 2026/07/01'in r['source_document_version']for r in self.subset(C)))
 def test_public_facts_have_no_private_locations(self):
  for r in self.rows:self.assertFalse(any(p in z for z in r.values()for p in['/'+'Users/','/'+'Volumes/','file'+':','smb'+':']))
if __name__=='__main__':unittest.main()
