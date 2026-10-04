"""Protect specimen form, chemical identity and source-version exclusions."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b173/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261004_b173_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing;import validate_tg_loi as v
A='10.1007/s10570-023-05148-1';B='10.1007/s10570-024-05756-5';C='10.1007/s10570-024-05808-w'
class TextileB173Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def subset(self,d):return[r for r in self.rows if r['DOI']==d]
 def find(self,d,s,g=''):return next(r for r in self.rows if r['DOI']==d and r['sample_state']==s and r['atmosphere']==g)
 def noTG(self,r):self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS))
 def test_eighteen_facts_are_not_valid_pairs(self):q=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(q['errors']);self.assertEqual((len(self.rows),q['verified_exact_sample_states'],q['verified_exact_condition_records']),(18,0,0));self.assertEqual([len(self.subset(d))for d in[A,B,C]],[8,8,2])
 def test_every_fact_stays_excluded(self):self.assertTrue(all(r['pairing_status']!='verified_exact'and pairing.evidence_issues(r)for r in self.rows))
 def test_TPP_four_entire_form_correspondences_held(self):
  rr=[r for r in self.subset(A)if r['atmosphere']];self.assertEqual(len(rr),4)
  for r in rr:self.assertEqual((r['material_form_TGA'],r['material_form_LOI']),('lyocell fiber','lyocell fabric'));self.assertIn('specimen_form_mismatch',pairing.evidence_issues(r));self.assertEqual(r['pairing_status'],'held_TG_fiber_fabric_scope_correspondence_unresolved')
 def test_TPP_native_profiles_preserved(self):
  for s,g,e in[('Control','air',('292.3','335.2','323.4','4.9')),('TPP20','air',('251.5','400.4','273.4','25.9')),('Control','N2',('292.5','339.8','361.1','15.7')),('TPP20','N2',('237.3','355.7','273.8','34.6'))]:self.assertEqual(tuple(self.find(A,'TPP_'+s+'_initial',g)[k]for k in['T10_C','T50_C','Tmax1_C','R800_pct']),e)
 def test_TPP_ordinary_method_not_TGIR_rate_or_flow(self):self.assertTrue(all(tuple(r[k]for k in['heating_rate_C_min','TG_start_C','TG_end_C'])==('10','40','800')for r in self.subset(A)if r['atmosphere']))
 def test_TPP_other_doses_do_not_borrow_TG(self):
  for r in self.subset(A):
   if not r['atmosphere']:self.noTG(r)
 def test_TPP_washed_fabric_keeps_only_own_LOI(self):r=self.find(A,'TPP20_after40LC');self.assertEqual(r['LOI_pct'],'28.3');self.assertEqual(r['treatment_state'],'washed');self.noTG(r)
 def test_Cu_modified_conditions_held_for_THEIC_ATHEIC_conflict(self):
  rr=[r for r in self.subset(B)if r['pairing_status']=='held_THEIC_ATHEIC_formulation_identity_conflict'];self.assertEqual(len(rr),4)
  for r in rr:self.assertIn('30wtpctTHEIC',r['treatment_method']);self.assertIn('ATHEIC',r['treatment_method'])
 def test_Cu_controls_stay_held_for_provenance(self):self.assertEqual(sum(r['pairing_status']=='held_control_partial_profile_provenance_unresolved'for r in self.subset(B)),2)
 def test_Cu_N2_native_profiles(self):
  for s,e in[('Control',('295','339','338','13.6')),('FR',('215','538','257','43.4')),('FR-Cu',('210','752','249','48.6'))]:self.assertEqual(tuple(self.find(B,'ATHEIC_'+s+'_initial','N2')[k]for k in['T5_C','T50_C','Tmax1_C','R800_pct']),e)
 def test_Cu_air_native_profiles(self):
  for s,e in[('Control',('110','331','326','462','1.6')),('FR',('206','425','253','','7.5')),('FR-Cu',('209','457','246','768','27.3'))]:self.assertEqual(tuple(self.find(B,'ATHEIC_'+s+'_initial','air').get(k,'')for k in['T5_C','T50_C','Tmax1_C','Tmax2_C','R800_pct']),e)
 def test_Cu_second_peak768_is_within_program_not_clipped(self):r=self.find(B,'ATHEIC_FR-Cu_initial','air');self.assertEqual(r['TG_end_C'],'800');self.assertLess(float(r['Tmax2_C']),800)
 def test_Cu_N2_dash_peak_not_numeric_zero(self):self.assertTrue(all(not r.get('Tmax2_C')for r in self.subset(B)if r['atmosphere']=='N2'))
 def test_Cu_roomtemperature_start_not_assumed25(self):self.assertTrue(all(not r.get('TG_start_C')and r['source_TG_start']=='roomtemperature_asreported_numericunreported'for r in self.subset(B)if r['atmosphere']))
 def test_Cu_washed_LOI_and_loading_without_TG(self):
  for s,e in[('FR',('31.9','10.87')),('FR-Cu',('28.7','9.53'))]:r=self.find(B,'ATHEIC_'+s+'_after20LC');self.assertEqual(tuple(r[k]for k in['LOI_pct','source_weight_gain_pct']),e);self.noTG(r)
 def test_blended_textile_has_no_independent_LOI(self):self.assertTrue(all(not r['LOI_pct']for r in self.subset(C)))
 def test_blended_ordinary_gas_and_ramp_unknown(self):self.assertTrue(all(not r['atmosphere']and not r['heating_rate_C_min']for r in self.subset(C)))
 def test_blended_char_endpoint_not_program700(self):
  self.assertEqual([r['residue_pct']for r in self.subset(C)],['3.6','16.4'])
  for r in self.subset(C):self.assertFalse(r['residue_temp_C']);self.assertFalse(r.get('R700_pct'));self.assertEqual(r['TG_end_C'],'700')
 def test_blended_stage_descriptions_not_canonical_TG_metrics(self):self.assertTrue(all(not r.get(k)for r in self.subset(C)for k in['T5_C','T10_C','Tonset_C','Tmax1_C','Tmax2_C']))
 def test_formal_correction_stays_unresolved(self):self.assertTrue(all('05864-2'in r['source_location']and'localreadsearchpending'in r['source_critical_limits']for r in self.subset(C)))
 def test_public_facts_have_no_private_locations(self):
  for r in self.rows:self.assertFalse(any(p in z for z in r.values()for p in['/'+'Users/','/'+'Volumes/','file'+':','smb'+':']))
if __name__=='__main__':unittest.main()
