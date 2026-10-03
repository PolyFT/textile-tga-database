"""Protect supplementary column mappings, native processing states and source limitations."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b140/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261003_b140_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing,validate_tg_loi as v
A='10.1016/j.ijbiomac.2019.11.220';B='10.1016/s0141-3910(01)00172-0'
class TextileB140Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def exact(self,s,gas='N2'):return next(r for r in self.rows if r['DOI']==A and r['sample_state']==s and r.get('atmosphere')==gas and r['pairing_status']=='verified_exact')
 def reject(self,r,**kw):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**kw)))
 def test_six_states_not_twelve_gas_tests_or_twentyseven_facts(self):
  z=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(z['errors']);self.assertEqual((z['verified_exact_sample_states'],z['verified_exact_condition_records']),(6,12));self.assertEqual(len(self.rows),27)
 def test_fifteen_holds_no_canonical_tg(self):
  rr=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(rr),15);self.assertTrue(all(all(not r[k]for k in pairing.TG_FIELDS)for r in rr))
 def test_native_t5_not_t10_or_onset(self):
  r=self.exact('PA66-OP-10M-UV');self.assertEqual(r['T5_C'],'405');self.assertFalse(r['T10_C']);self.assertFalse(r['Tonset_C']);self.reject(r,T5_C='',T10_C='405')
 def test_supplement_air_nitrogen_columns_cannot_swap(self):
  r=self.exact('PA66-OP-10M-UV','air');self.assertEqual((r['T5_C'],r['Tmax1_C'],r['R800_pct']),('379','468','3.1'));self.reject(r,T5_C='405',Tmax1_C='448',R800_pct='4.5')
 def test_air_char_oxidation_peak_not_nitrogen_peak(self):
  r=self.exact('PA66-10BL-UV','air');self.assertEqual(r['Tmax2_C'],'599');n=self.exact('PA66-10BL-UV');self.assertFalse(n['Tmax2_C']);self.reject(n,Tmax2_C='599')
 def test_800_residue_not_program_end(self):
  r=self.exact('PA66-10BL');self.assertEqual((r['R800_pct'],r['residue_temp_C']),('6.3','800'));self.assertNotIn('TG_end_C',r);self.reject(r,residue_temp_C='600')
 def test_gas_and_ramp_source_bound(self):
  r=self.exact('PA66-5BL-UV');self.assertEqual(r['heating_rate_C_min'],'20');self.reject(r,heating_rate_C_min='10');self.reject(r,atmosphere='air')
 def test_onepot_five_ten_minutes_not_layers(self):
  a=self.exact('PA66-OP-5M-UV');b=self.exact('PA66-OP-10M-UV');self.assertEqual((a['source_soak_minutes'],b['source_soak_minutes']),('5','10'));self.assertEqual((a['source_BL'],b['source_BL']),('0','0'));self.reject(a,LOI_pct='22')
 def test_uv_and_thermal_ten_layers_not_same_state(self):
  a=self.exact('PA66-10BL-UV');b=self.exact('PA66-10BL');self.assertEqual((a['LOI_pct'],b['LOI_pct']),('23','22'));self.assertEqual((a['source_crosslink_mode'],b['source_crosslink_mode']),('UV','thermal'));self.reject(a,T5_C=b['T5_C'],Tmax1_C=b['Tmax1_C'],R800_pct=b['R800_pct'])
 def test_unknown_processing_parameters_not_invented(self):
  rr=[r for r in self.rows if r['pairing_status']=='verified_exact'and r['sample_state']!='PA66-Control'];self.assertTrue(all('unreadable'in r['source_processing_condition_limit']and'Scheme1imageunviewed'in r['source_processing_condition_limit']for r in rr));self.assertTrue(all('notinferred'in r['limitations']for r in rr))
 def test_control_addon_dash_not_zero(self):
  r=self.exact('PA66-Control');self.assertFalse(r['source_addon_pct']);self.assertIn('controldashnotzero',r['source_addon_definition'])
 def test_addon_not_bath_percent(self):
  r=self.exact('PA66-10BL-UV');self.assertEqual(r['source_addon_pct'],'6.5');self.assertIn('(W1-W)/W',r['source_addon_definition']);self.assertIn('notfinalmassfraction',r['composition'])
 def test_loi_uncertainty_not_sd_or_replicate_count(self):
  r=self.exact('PA66-OP-5M-UV');self.assertEqual(r['source_LOI_uncertainty'],'0.5');self.assertIn('SDorSEnotdefined',r['source_LOI_uncertainty_definition']);self.assertEqual(r['source_LOI_repeats'],'Unreported')
 def test_accepted_date_not_final_publication_year(self):
  r=self.exact('PA66-Control');self.assertFalse(r['year']);self.assertIn('accepted 2019-11-27',r['source_document_version']);self.assertIn('VOR not reviewed',r['source_document_version'])
 def test_si_table_and_primary_loi_locators_separate(self):
  r=self.exact('PA66-Control');self.assertIn('Table1PDFp16',r['LOI_locator']);self.assertIn('SupplementaryTableS1',r['TG_locator']);self.assertTrue(r['supplement_source_url'].endswith('S0141813019378110-mmc1.docx'))
 def test_initial_fabric_not_free_coating_or_washed_form(self):
  r=self.exact('PA66-10BL-UV');self.assertIn('100% PA66 woven',r['material_form']);self.assertIn('Initial0durabilitycycles',r['washing_state']);self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='PCS/PASfreepowder')));self.reject(r,washing_state='After5durabilitycycles')
 def test_eight_washed_vertical_records_without_tg_loi(self):
  rr=[r for r in self.rows if r['pairing_status']=='held_washed_vertical_only_without_own_LOI_TG'];self.assertEqual(len(rr),8);self.assertTrue(all(not r['LOI_pct']and not r['R800_pct']for r in rr));self.assertEqual({r['sample_state'].split(' after')[1]for r in rr},{'5washcycles','10washcycles'})
 def test_cotton_two_fabrics_and_ramp_unit_remain_unresolved(self):
  rr=[r for r in self.rows if r['DOI']==B];self.assertEqual(len(rr),7);self.assertTrue(all('230or175'in r['material_form']and'7.5C/mmunitunresolved'in r['source_TG_method']for r in rr));self.assertTrue(all(not r['heating_rate_C_min']for r in rr))
 def test_aps_120_and_180_cure_states_cannot_mix(self):
  rr=[r for r in self.rows if r['DOI']==B and r['sample_state'].startswith('APS15')];self.assertEqual(len(rr),2);loi=next(r for r in rr if 'dry180C'in r['sample_state']);tg=next(r for r in rr if 'dry120C'in r['sample_state']);self.assertEqual(loi['LOI_pct'],'30');self.assertFalse(tg['LOI_pct']);self.assertIn('45',tg['source_raw_observation']);self.assertTrue(all(not r['R400_pct']for r in rr))
 def test_diguanidine_dose_pickup_cure_mismatch_held(self):
  rr=[r for r in self.rows if r['DOI']==B and r['sample_state'].startswith('diGuaHP')];self.assertEqual(len(rr),2);loi=next(r for r in rr if '100gL'in r['sample_state']);tg=next(r for r in rr if '150gL'in r['sample_state']);self.assertEqual(loi['LOI_pct'],'36');self.assertFalse(tg['LOI_pct']);self.assertIn('40',tg['source_raw_observation']);self.assertTrue(all(not r['R400_pct']for r in rr))
if __name__=='__main__':unittest.main()
