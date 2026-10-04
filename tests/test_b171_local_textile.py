"""Protect source-specific native criteria, sample states, method scope and holds."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b171/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261004_b171_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing;import validate_tg_loi as v
A='10.1007/s10570-024-06307-8';B='10.1007/s10570-023-05728-1';C='10.1007/s10570-024-06209-9'
class TextileB171Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def subset(self,d):return[r for r in self.rows if r['DOI']==d]
 def find(self,d,s,g=None):return next(r for r in self.subset(d)if r['sample_state']==s and(g is None or r['atmosphere']==g))
 def accepted(self):return[r for r in self.rows if r['pairing_status']=='verified_exact']
 def noTG(self,r):self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS))
 def test_six_states_ten_conditions_not_fiftyfacts(self):
  p=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(p['errors']);self.assertEqual((p['verified_exact_sample_states'],p['verified_exact_condition_records']),(6,10));self.assertEqual(len(self.rows),50)
 def test_forty_held_facts_excluded(self):
  rr=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(rr),40);self.assertEqual([sum(r['DOI']==d for r in rr)for d in[A,B,C]],[1,21,18]);self.assertTrue(all(pairing.evidence_issues(r)for r in rr))
 def test_measurement_state_and_method_changes_invalidate_review(self):
  for r in self.accepted():
   self.assertFalse(pairing.evidence_issues(r))
   for k,z in [('LOI_pct','99'),('Tmax1_C','555'),('residue_pct','77'),('residue_temp_C','710'),('heating_rate_C_min','20'),('washing_state','washed'),('sample_state','anotherformula')]:self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**{k:z})))
 def test_fabric_not_bulk_or_fiber(self):
  for r in self.accepted():self.assertEqual(r['material_form_TGA'],r['material_form_LOI']);self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='fiber')))
 def test_APDP_six_own_N2_profiles(self):
  for s,e in [('Lyocell',('19.5','308','323','357','10.8')),('PA',('23.5','239','257','287','33.0')),('APD',('25.8','285','293','308','17.8')),('APDP1',('26.4','276','282','297','30.3')),('APDP2',('27.9','275','283','298','35.2')),('APDP3',('30.4','273','281','297','37.5'))]:r=self.find(A,'APDP_'+s+'_initial','N2');self.assertEqual(tuple(r[k]for k in['LOI_pct','T5_C','T10_C','Tmax1_C','R700_pct']),e)
 def test_APDP_four_own_air_profiles(self):
  for s,e in [('Lyocell',('303','318','339','498','0.5')),('PA',('239','258','289','508','1.0')),('APD',('283','293','306','512','7.2')),('APDP2',('272','279','294','506','11.2'))]:r=self.find(A,'APDP_'+s+'_initial','air');self.assertEqual(tuple(r[k]for k in['T5_C','T10_C','Tmax1_C','Tmax2_C','R700_pct']),e)
 def test_APDP_gases_do_not_duplicate_samplecount(self):
  rr=self.accepted();self.assertEqual(len({r['sample_state']for r in rr}),6);self.assertEqual([sum(r['atmosphere']==g for r in rr)for g in['N2','air']],[6,4])
 def test_APDP_method_end710_not_residue700(self):
  for r in self.accepted():self.assertEqual(tuple(r[k]for k in['TG_start_C','TG_end_C','heating_rate_C_min','residue_temp_C']),('40','710','10','700'));self.assertEqual(r['TGA_instrument'],'TA 5500 as reported');self.assertEqual(r['source_TGA_sample_mass_flow_repeats'],'unreported')
 def test_APDP_T5_T10_not_Tonset(self):
  for r in self.accepted():self.assertFalse(r.get('Tonset_C'));self.assertNotEqual(r['T5_C'],r['T10_C'])
 def test_APDP_DTG_per_C_not_per_minute(self):
  r=self.find(A,'APDP_APDP2_initial','air');self.assertEqual((r['source_DTG_Rmax1_pct_per_C'],r['source_DTG_Rmax2_pct_per_C']),('2.5','0.25'));self.assertIn('notpermin',r['source_metric_definition'])
 def test_APDP_N2_dash_peak_notzero(self):
  for r in self.accepted():
   if r['atmosphere']=='N2':self.assertFalse(r.get('Tmax2_C'))
 def test_APDP_measured_WG_not_bath(self):
  for s,wg in [('APDP1','10'),('APDP2','13'),('APDP3','16')]:r=self.find(A,'APDP_'+s+'_initial','N2');self.assertEqual(r['source_weight_gain_pct'],wg);self.assertIn('notbath/vendor70pctPAstock',r['source_loading_basis_limit'])
 def test_APDP_PA_APD_unknown_individual_recipe_not_borrowed(self):
  for s in ['PA','APD']:
   r=self.find(A,'APDP_'+s+'_initial','N2');self.assertFalse(r['source_weight_gain_pct']);self.assertIn('individual treatment process/loading unreported',r['treatment_method']);self.assertIn('notassignedAPDPloadingorpreparation',r['treatment_method'])
 def test_APDP_conechar_not_TGchar(self):
  r=self.find(A,'APDP_APDP2_initial','N2');self.assertEqual(r['R700_pct'],'35.2');self.assertIn('40.2residuesnotTG',r['source_ancillary_limit'])
 def test_APDP_friction_state_no_initial_TG(self):
  r=self.find(A,'APDP_APDP2_after100dryfriction');self.assertEqual(r['LOI_pct'],'27.5');self.noTG(r);self.assertNotEqual(r['washing_state'],'initial');self.assertIn('PACG',r['source_friction_method'])
 def test_PALPAP_four_entire_conditions_held_for_scope(self):
  rr=[r for r in self.subset(B)if r['Tmax1_C']];self.assertEqual(len(rr),4)
  for r in rr:self.assertEqual(r['pairing_status'],'held_ordinary_fabric_TG_method_scope_unresolved');self.assertFalse(r['heating_rate_C_min']);self.assertFalse(r.get('TG_end_C'));self.assertIn('notexplicitlyordinaryfabricmethod',r['source_bulk_TG_method'])
 def test_PALPAP_TGIR_flow_not_ordinaryflow(self):
  r=self.find(B,'PALPAP_FR3_initial','N2');self.assertIn('60mLminnotordinaryTGprogram',r['source_TGIR_method']);self.assertTrue(pairing.evidence_issues(r))
 def test_PALPAP_native_T5_Tmax_residue_unchanged(self):
  for s,g,e in [('Control','N2',('307','363','3.5','18.1')),('FR3','N2',('229','294','36.7','50.7')),('Control','air',('304','350','0','18.1')),('FR3','air',('208','291','16.3','50.7'))]:r=self.find(B,'PALPAP_'+s+'_initial',g);self.assertEqual(tuple(r[k]for k in['T5_C','Tmax1_C','R700_pct','LOI_pct']),e)
 def test_PALPAP_at_peak_mass_not_final_residue(self):
  r=self.find(B,'PALPAP_FR3_initial','N2');self.assertEqual((r['residue_at_Tmax1_pct'],r['R700_pct']),('71.1','36.7'))
 def test_PALPAP_two_otherdoses_no_FR3_TG(self):
  for s,loi in [('FR1','37.5'),('FR2','48.6')]:r=self.find(B,'PALPAP_'+s+'_initial');self.assertEqual(r['LOI_pct'],loi);self.noTG(r)
 def test_PALPAP_fifteen_washed_LOIs_have_no_initialTG(self):
  rr=[r for r in self.subset(B)if r['treatment_state']=='washed'];self.assertEqual(len(rr),15)
  for r in rr:self.noTG(r);self.assertIn('cycleunitasreportednotmultiplied',r['source_wash_details'])
 def test_GAMMA_all18facts_held(self):
  self.assertEqual(len(self.subset(C)),18);self.assertTrue(all(r['pairing_status']!='verified_exact'for r in self.subset(C)))
 def test_GAMMA_approximate_DTGs_not_exact_numeric_table(self):
  for s,tm in [('Control','350'),('BCF24','370')]:r=self.find(C,'GAMMA_'+s+'_initial');self.assertEqual(r['Tmax1_C'],tm);self.assertEqual(r['pairing_status'],'held_approximate_DTG_curve_description_not_numeric_table');self.assertFalse(r.get('R800_pct'))
 def test_GAMMA_shoulder_water_char_enhancement_not_canonical(self):
  r=self.find(C,'GAMMA_B2MEP23_initial');self.noTG(r);self.assertIn('shoulderaround340notmainTmax',r['source_metric_definition']);self.assertIn('notactualR800',r['source_metric_definition'])
 def test_GAMMA_same_ratio_distinct_GYs(self):
  rr=[r for r in self.subset(C)if r['source_monomer_ratio']=='1:1'and r['treatment_state']=='initial'];self.assertEqual({r['source_grafting_yield_pct_approx']for r in rr},{'24','45','68','84'});self.assertEqual(len({r['sample_state']for r in rr}),4)
 def test_GAMMA_stockunit_conflict_notcorrected(self):
  r=self.find(C,'GAMMA_BCF48_initial');self.assertIn('80v/vMaterialsversus80w/vResultsunresolvednotcorrected',r['treatment_method'])
 def test_GAMMA_washing_units_sameidentity_no_initialTG(self):
  rr=[r for r in self.subset(C)if r['treatment_state']=='washed'];self.assertEqual(len(rr),9)
  for r in rr:self.noTG(r);self.assertEqual(r['washing_state'],'5AWC_asreported_equivalent25homeLC');self.assertIn('oneidentitynotduplicatepairs',r['source_wash_details'])
 def test_public_facts_no_privatepaths_or_contacts(self):
  for r in self.rows:self.assertFalse(any(('/'+'Volumes'+'/')in str(z)or('/'+'Users'+'/')in str(z)or('smb'+':'+chr(47)*2)in str(z)or'Email:'in str(z)or'@nefu.edu'in str(z)for z in r.values()))
if __name__=='__main__':unittest.main(verbosity=2)
