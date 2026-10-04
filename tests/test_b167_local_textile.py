"""Guard native condition evidence, water-loss criteria and washed-state pairing."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b167/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261004_b167_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing;import validate_tg_loi as v
A='10.1007/s10570-023-05287-5';B='10.1007/s10570-023-05586-x';C='10.1007/s10570-024-06172-5'
class TextileB167Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def subset(self,doi):return[r for r in self.rows if r['DOI']==doi]
 def find(self,doi,sample,gas=None):return next(r for r in self.subset(doi)if r['sample_state']==sample and(gas is None or r['atmosphere']==gas))
 def accepted(self):return[r for r in self.rows if r['pairing_status']=='verified_exact']
 def noTG(self,r):self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS))
 def test_two_states_two_conditions_not29facts(self):
  p=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(p['errors']);self.assertEqual((p['verified_exact_sample_states'],p['verified_exact_condition_records']),(2,2));self.assertEqual(len(self.rows),29)
 def test_twentyseven_held_excluded(self):
  rows=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(rows),27);self.assertEqual([sum(r['DOI']==d for r in rows)for d in[A,B,C]],[8,3,16]);self.assertTrue(all(pairing.evidence_issues(r)for r in rows))
 def test_review_rejects_mutated_metric_condition_or_state(self):
  for r in self.accepted():
   self.assertFalse(pairing.evidence_issues(r))
   for k,value in [('LOI_pct','99'),('T5_C','300'),('Tmax1_C','555'),('R800_pct','77'),('atmosphere','oxygen'),('heating_rate_C_min','50'),('washing_state','50LC'),('sample_state','otherdose')]:self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**{k:value})))
 def test_fabric_not_fiber(self):
  for r in self.accepted():self.assertEqual(r['material_form_TGA'],'cotton fabric');self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='cotton fiber')))
 def test_LBL_PAAPS15chlorinated_own_TG_LOI(self):
  r=self.find(A,'LBL_PAAPS15Cl_initial');self.assertEqual(tuple(r[k]for k in['T5_C','T10_C','Tmax1_C','R700_pct','LOI_pct']),('135','234','352','17.0','27.3'));self.assertEqual(r['pairing_status'],'verified_exact');self.assertIn('initial_chlorinated',r['washing_state'])
 def test_LBL_control_Tmax_conflict_entire_pair_held(self):
  r=self.find(A,'LBL_Control_initial');self.assertEqual((r['Tmax1_C'],r['source_Tmax_body_C']),('357','355'));self.assertNotEqual(r['pairing_status'],'verified_exact');self.assertTrue(pairing.evidence_issues(r))
 def test_LBL_native_water_massloss_criterion_not_decomposition_onset(self):
  for r in self.subset(A):
   if r['atmosphere']:self.assertFalse(r.get('Tonset_C'));self.assertIn('Controlbodywaterclaimandnative317retained',r['source_metric_definition'])
 def test_LBL_own_ordinary_program_not_TGIR(self):
  r=self.find(A,'LBL_PAAPS15Cl_initial');self.assertEqual((r['TGA_instrument'],r['TG_start_C'],r['TG_end_C'],r['heating_rate_C_min'],r['source_TGA_mass_mg']),('TA Q500','30','700','10','5'));self.assertIn('staticN2',r['source_atmosphere_detail']);self.assertIn('notseparateTGIR50-800',r['source_TGIR_exclusion'])
 def test_LBL_APS15LOI_unknown_not_PA15_LOI(self):
  r=self.find(A,'LBL_APS15Cl_initial');self.assertFalse(r['LOI_pct']);self.assertEqual(r['R700_pct'],'15.9');self.assertNotEqual(r['pairing_status'],'verified_exact')
 def test_LBL_other_BL_no_borrowed_numbers(self):
  for chem in ['APS','PAAPS']:
   for bl in [5,10]:r=self.find(A,'LBL_'+chem+str(bl)+'Cl_initial');self.noTG(r);self.assertFalse(r['LOI_pct']);self.assertIn('notLOI',r['source_join_limit'])
 def test_LBL_washed_LOI_and_version_conflict_not_initial_TG(self):
  r=self.find(A,'LBL_PAAPS15Cl_after5LC');self.assertFalse(r['LOI_pct']);self.noTG(r);r=self.find(A,'LBL_PAAPS15Cl_after10LC');self.assertEqual(r['LOI_pct'],'24.3');self.noTG(r);self.assertIn('61-2006vsFig8AATCC61-1996',r['source_wash_details'])
 def test_TSNP_control_explicit_TG_and_LOI(self):
  r=self.find(B,'TSNP_Uncoated_initial');self.assertEqual(tuple(r[k]for k in['T5_C','Tmax1_C','R700_pct','LOI_pct']),('268.6','343','18.9','17.8'));self.assertEqual(r['pairing_status'],'verified_exact');self.assertEqual((r['TG_start_C'],r['TG_end_C'],r['heating_rate_C_min']),('40','700','10'));self.assertIn('N2caption/Table2explicit',r['pairing_evidence'])
 def test_TSNP_all_three_coated_recipe_conflicts_held(self):
  for sample in ['W10','W15','W20']:
   r=self.find(B,'TSNP_'+sample+'_initial');self.assertEqual(r['pairing_status'],'held_recipe_dose_label_body_table_conflict');self.assertIn('otherW15/W20prepared10/15pctversusTable1W10/W15/W20=10/15/20pct',r['source_recipe_conflict']);self.assertTrue(pairing.evidence_issues(r))
 def test_TSNP_native_all_coated_profiles_not_discarded(self):
  for s,e in [('W10',('269.7','329','16.1','23.1')),('W15',('271.6','321','34.8','24.2')),('W20',('259.5','302','31.6','26.5'))]:r=self.find(B,'TSNP_'+s+'_initial');self.assertEqual(tuple(r[k]for k in['T5_C','Tmax1_C','R700_pct','LOI_pct']),e)
 def test_TSNP_DTGrate_sign_and_uncertainty_type_retained(self):
  r=self.find(B,'TSNP_Uncoated_initial');self.assertEqual(r['source_DTGmax_signed_pct_per_C'],'-1.5');self.assertEqual((r['source_LOI_uncertainty_pct'],r['source_uncertainty_type']),('0.2','unreported'));self.assertFalse(r.get('Tonset_C'))
 def test_graft_all_sixteen_facts_held(self):
  self.assertEqual(len(self.subset(C)),16);self.assertTrue(all(r['pairing_status']!='verified_exact'for r in self.subset(C)))
 def test_graft_ordinary_ramp_absent_TGIR_not_borrowed(self):
  for sample in ['Graft_Control_initial','Graft_DAMCFCl_MBA6_initial']:
   r=self.find(C,sample);self.assertFalse(r['heating_rate_C_min']);self.assertEqual((r['TG_start_C'],r['TG_end_C']),('30','700'));self.assertIn('TGIR10Cmincannotborrow',r['source_ordinary_ramp_hold'])
 def test_graft_control18_citation_not_own_measured_LOI(self):
  r=self.find(C,'Graft_Control_initial');self.assertFalse(r['LOI_pct']);self.assertIn('citedgeneralcottonflammabilitythreshold',r['source_control_LOI_limit']);self.assertEqual(tuple(r[k]for k in['T5_C','Tmax1_C','R700_pct']),('317','356','11.1'))
 def test_graft_MBA6_selected_not8_and_amount_conflict_retained(self):
  r=self.find(C,'Graft_DAMCFCl_MBA6_initial');self.assertEqual(tuple(r[k]for k in['T5_C','Tmax1_C','R700_pct','LOI_pct']),('162','295','30.3','27.6'));self.assertIn('6MBAonly',r['source_optimum_scope']);self.assertIn('0.18-0.24gfor2-8wt%',r['source_MBA_mass_conflict']);r=self.find(C,'Graft_DAMCFCl_MBA8_initial');self.noTG(r);self.assertFalse(r['LOI_pct'])
 def test_graft_DA_feed_has_no_borrowed_DAM_profile(self):
  for i in range(1,8):r=self.find(C,'Graft_DACFCl_'+str(i)+'_initial');self.noTG(r);self.assertEqual(r['LOI_pct'],'27.3'if i==2 else'');self.assertIn('DAMMBA6TGnotDAnocrosslinkerTG',r['source_LOI_limit'])
 def test_graft_washed_LOI_not_initial_or_rechlorinated_TG(self):
  for cycle,value in [(1,'23.0'),(2,'21.0'),(5,'18.3'),(10,'18.1')]:r=self.find(C,'Graft_DAMCFCl_MBA6_after'+str(cycle)+'LC');self.assertEqual(r['LOI_pct'],value);self.noTG(r);self.assertIn('noAATCCfivefoldconversion',r['source_wash_details']);self.assertIn('rechlorinatedchlorinepercentnotwashedLOI',r['source_wash_TG_limit'])
 def test_public_facts_no_private_paths_or_contacts(self):
  for r in self.rows:self.assertRegex(r['evidence_reviewed_at'],r'^\d{4}-\d{2}-\d{2}$');self.assertFalse(any(('/'+'Volumes'+'/')in str(x)or('/'+'Users'+'/')in str(x)or('smb'+':'+chr(47)*2)in str(x)or'@163.com'in str(x)for x in r.values()))
if __name__=='__main__':unittest.main(verbosity=2)
