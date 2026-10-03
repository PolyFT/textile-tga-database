"""Protect source attribution, washing identity and gasspecific thermal metrics."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b139/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261003_b139_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing,validate_tg_loi as v
A='10.1016/j.porgcoat.2019.01.010';B='10.1016/j.polymdegradstab.2012.05.023';C='10.1016/j.ijbiomac.2018.08.043'
class TextileB139Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def source(self,d):return[r for r in self.rows if r['DOI']==d]
 def exact(self,s,gas='N2'):return next(r for r in self.source(A)if r['sample_state']==s and r['atmosphere']==gas and r['pairing_status']=='verified_exact')
 def reject(self,r,**kw):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**kw)))
 def test_five_states_not_ten_gas_tests_or_thirty_facts(self):
  z=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(z['errors']);self.assertEqual((z['verified_exact_sample_states'],z['verified_exact_condition_records']),(5,10));self.assertEqual(len(self.rows),30)
 def test_twenty_held_rows_no_canonical_tg(self):
  rr=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(rr),20);self.assertTrue(all(all(not r[k]for k in pairing.TG_FIELDS)for r in rr))
 def test_native_t5_not_t10_or_generic_onset(self):
  r=self.exact('PA66-2BL-APTES');self.assertEqual(r['T5_C'],'229');self.assertFalse(r['T10_C']);self.assertFalse(r['Tonset_C']);self.reject(r,T5_C='',T10_C='229')
 def test_gas_t5_values_cannot_be_swapped(self):
  r=self.exact('PA66-2BL-APTES','air');self.assertEqual((r['T5_C'],r['Tmax1_C']),('280','464'));self.reject(r,T5_C='229',Tmax1_C='457')
 def test_air_second_peak_not_nitrogen_peak(self):
  r=self.exact('PA66-5BL-B-d-APTES','air');self.assertEqual(r['Tmax2_C'],'567');n=self.exact('PA66-5BL-B-d-APTES');self.assertFalse(n['Tmax2_C']);self.reject(n,Tmax2_C='567')
 def test_fixed800_residue_not_unknown_program_endpoint(self):
  r=self.exact('PA66-5BL-B-d-APTES');self.assertEqual((r['R800_pct'],r['residue_temp_C']),('10.0','800'));self.assertNotIn('TG_end_C',r);self.reject(r,residue_temp_C='600')
 def test_gas_and_ramp_are_source_bound(self):
  r=self.exact('PA66-5BL-APTES');self.assertEqual(r['heating_rate_C_min'],'20');self.reject(r,atmosphere='air');self.reject(r,heating_rate_C_min='10')
 def test_initial_process_rinse_not_durability_wash(self):
  r=self.exact('PA66-5BL-APTES');self.assertIn('DIwash60C1h',r['treatment_method']);self.assertIn('Initial0durabilitycycles',r['washing_state']);self.reject(r,washing_state='After5durabilitycycles')
 def test_same_fabric_form_not_free_additive_tg(self):
  r=self.exact('PA66-5BL-APTES');self.assertIn('100% PA66 woven',r['material_form']);self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='APTESsolpowder')))
 def test_loi_same_formulation_not_borrowed_5bl(self):
  r=self.exact('PA66-5BL-B-d-APTES');self.assertEqual(r['LOI_pct'],'20.6');self.reject(r,LOI_pct='21.2')
 def test_borrowed_reference_not_new_independent_group(self):
  rr=[r for r in self.source(A)if r['sample_state']=='PA66-5BL borrowed Ref6'];self.assertEqual(len(rr),2);self.assertTrue(all(r['source_borrowed_DOI']=='10.1016/j.porgcoat.2018.04.031'and r['pairing_status'].startswith('held_borrowed')for r in rr));self.assertEqual({r['source_raw_R800_pct']for r in rr},{'4.3','9.6'})
 def test_borrowed_loi_conflict_retained_not_overwritten(self):
  rr=[r for r in self.source(A)if r['sample_state']=='PA66-5BL borrowed Ref6'];self.assertTrue(all('21.2'in r['source_borrowed_LOI_conflict']and'21.0'in r['source_borrowed_LOI_conflict']for r in rr))
 def test_washed_dripping_not_tg_loi(self):
  rr=[r for r in self.source(A)if 'after5timeswash'in r['sample_state']];self.assertEqual(len(rr),6);self.assertTrue(all(not r['LOI_pct']and not r['R800_pct']for r in rr));self.assertTrue(all(r['pairing_status'].startswith('held_')for r in rr))
 def test_addon_and_bath_are_distinct(self):
  r=self.exact('PA66-5BL-APTES');self.assertEqual(r['source_addon_pct'],'13.2');self.assertIn('CS10g/LPA20g/L',r['composition']);self.assertIn('(W1-W)/W',r['source_addon_definition'])
 def test_loi_dimensions_not_cone_or_vertical(self):
  r=self.exact('PA66-Control');self.assertEqual(r['source_LOI_dimensions_mm'],'150x58');self.assertEqual(r['LOI_standard'],'ASTMD2863');self.assertEqual(r['source_LOI_repeats'],'Unreported')
 def test_neofr_control_approx_loi_not_exact(self):
  r=next(r for r in self.source(B)if r['sample_state']=='control');self.assertFalse(r['LOI_pct']);self.assertIn('17.8',r['source_raw_observation']);self.assertIn('approximate',r['pairing_status'])
 def test_neofr_tg_weightgain_not_26point5_loi(self):
  r=next(r for r in self.source(B)if r['sample_state']=='NeoFR TG unspecified dryweightgain');self.assertFalse(r['LOI_pct']);self.assertFalse(r['T5_C']);self.assertIn('36.5',r['source_raw_observation']);self.assertIn('240',r['source_raw_observation'])
 def test_neofr_two_loi_gain_endpoints_remain_unpaired(self):
  rr=[r for r in self.source(B)if r['sample_state'].startswith('NeoFR ')and'dryweightgain'in r['sample_state']and 'TG unspecified'not in r['sample_state']];self.assertEqual({r['LOI_pct']for r in rr},{'21','33.8'});self.assertTrue(all(not r['R500_pct']for r in rr))
 def test_pet_argon20_not_mcc_nitrogen1csec(self):
  rr=self.source(C);self.assertEqual(len(rr),6);self.assertTrue(all('ARGON20C/min'in r['source_TG_method']for r in rr));self.assertTrue(all(not r['LOI_pct']and not r['R650_pct']for r in rr))
 def test_pet_approx_residues_retained_as_raw_only(self):
  self.assertEqual({r['source_raw_R650_approx_pct']for r in self.source(C)},{'3.3','4.8','4.4','8.7','4.5','6.1'});self.assertTrue(all(r['pairing_status']=='held_unannotated_LOI_and_explicit_approximate_TG_residue'for r in self.source(C)))
if __name__=='__main__':unittest.main()
