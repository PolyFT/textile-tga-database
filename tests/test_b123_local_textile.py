"""Protect residue temperature, formulation identity, gas and wash boundaries."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
H=Path(__file__).resolve().parent;P=H.name=='work';R=H.parent/'repo'if P else H.parent
F=H/'staged-local-textile-b123/publication_proposed.csv'if P else R/'data/incoming/verified_source_batch_20261002_b123_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing,validate_tg_loi as v
A='10.1007/s10570-016-1163-z';B='10.1016/j.porgcoat.2018.04.031'
class TextileB123Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def row(self,doi,state,gas=None):return next(r for r in self.rows if r['DOI']==doi and r['sample_state']==state and(gas is None or r['atmosphere']==gas))
 def rejected(self,r,**changes):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**changes)))
 def test_independent_state_and_condition_counts(self):
  q=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(q['errors']);self.assertEqual((q['verified_exact_sample_states'],q['verified_exact_condition_records']),(9,16));self.assertEqual(len(self.rows),38)
 def test_apttp_fixed_air_r600_not_endpoint800(self):
  r=self.row(A,'APTTP140 cotton','air');self.assertEqual((r['residue_pct'],r['residue_temp_C'],r['TG_end_C']),('21.3','600','800'));self.rejected(r,residue_temp_C='800',char_temp_C='800')
 def test_apttp_unlocated_nitrogen_char_not_assigned600(self):
  rr=[r for r in self.rows if r['DOI']==A and r['pairing_status']=='held_N2_numeric_residue_temperature_unlocated'];self.assertEqual(len(rr),2);self.assertEqual({r['source_reported_remaining_residue_pct']for r in rr},{'11.8','43.5'});self.assertTrue(all(not r['source_reported_residue_temp_C']and all(not r.get(k)for k in pairing.TG_FIELDS)for r in rr))
 def test_apttp_decomposition_ranges_not_t5_t10_onset_or_peak(self):
  r=self.row(A,'APTTP140 cotton','air');self.assertTrue(all(not r.get(k)for k in ['T5_C','T10_C','Tonset_C','Tmax1_C','Tmax2_C']));h=self.row(A,'APTTP140-N2raw');self.assertEqual(h['source_reported_decomposition_range_C'],'219-298');self.rejected(r,Tonset_C='219',Tmax1_C='298')
 def test_apttp_only_explicit140gl_has_tg_pair(self):
  rr=[r for r in self.rows if r['DOI']==A and r['pairing_status']=='verified_exact'];self.assertEqual({r['source_APTTP_bath_g_L']for r in rr},{'0','140'});self.assertEqual({r['LOI_pct']for r in rr},{'18','43.8'});self.assertTrue(all(r['atmosphere']=='air'for r in rr));self.assertNotEqual(self.row(A,'APTTP80 cotton')['pairing_status'],'verified_exact');self.assertNotEqual(self.row(A,'APTTP110 cotton')['pairing_status'],'verified_exact')
 def test_apttp_eighteen_washed_loi_do_not_borrow_tg(self):
  rr=[r for r in self.rows if r['DOI']==A and r['source_native_LC']];self.assertEqual(len(rr),18);self.assertEqual({r['source_native_LC']for r in rr},{'5','10','20','30','40','50'});self.assertTrue(all(all(not r.get(k)for k in pairing.TG_FIELDS)for r in rr))
 def test_apttp_cone_char_not_air_tg(self):
  r=self.row(A,'APTTP140 cotton','air');self.assertEqual(r['char_pct'],'21.3');self.rejected(r,residue_pct='32.0',char_pct='32.0');c=self.row(A,'Control cotton','air');self.assertEqual(c['char_pct'],'0.13');self.rejected(c,char_pct='7.4',residue_pct='7.4')
 def test_apttp_tgir_mass_and_pipe_temp_not_tg(self):
  r=self.row(A,'APTTP140 cotton','air');self.assertEqual((r['source_TGIR_mass_mg'],r['source_TGIR_transfer_pipe_C']),('8','200'));self.assertFalse(r.get('source_TG_mass_mg'));self.assertFalse(r.get('source_TG_flow_mL_min'));self.rejected(r,Tonset_C='200')
 def test_borate_seven_named_formulations_have_two_gases_each(self):
  rr=[r for r in self.rows if r['DOI']==B];self.assertEqual(len(rr),14);self.assertEqual(len({r['sample_state']for r in rr}),7);self.assertTrue(all({r['atmosphere']for r in rr if r['sample_state']==s}=={'air','N2'}for s in {r['sample_state']for r in rr}))
 def test_borate_suffix_w_is_bath_not_laundering(self):
  r=self.row(B,'PA66-10BL-B5W','N2');self.assertEqual((r['source_borate_bath_wt_pct'],r['source_borate_Table1_g_L']),('5','50'));self.assertIn('0durabilitylaundering',r['washing_state']);self.assertFalse(r['source_native_LC']);self.assertEqual(r['source_BL'],'10')
 def test_borate_t5_not_generic_onset_or_t10(self):
  r=self.row(B,'PA66-10BL-B5W','air');self.assertEqual(r['T5_C'],'301');self.assertFalse(r['Tonset_C']);self.assertFalse(r['T10_C']);self.rejected(r,T5_C='',Tonset_C='301')
 def test_borate_gas_specific_peaks_no_second_nitrogen_peak(self):
  a=self.row(B,'PA66-10BL-B5W','air');n=self.row(B,'PA66-10BL-B5W','N2');self.assertEqual((a['Tmax1_C'],a['Tmax2_C'],n['Tmax1_C']),('446','664','427'));self.assertFalse(n['Tmax2_C']);self.rejected(n,Tmax2_C='664')
 def test_borate_exact_table_r800_not_rounded_prose(self):
  a=self.row(B,'PA66-10BL-B5W','air');n=self.row(B,'PA66-10BL-B5W','N2');self.assertEqual((a['char_pct'],n['char_pct'],a['source_prose_rounded_char_pct'],n['source_prose_rounded_char_pct']),('9.1','12.4','9','12'));self.assertEqual(a['residue_temp_C'],'800');self.rejected(a,char_pct='9',residue_pct='9');self.rejected(a,char_pct='12.4',residue_pct='12.4')
 def test_borate_tgir55_flow_not_main_tg(self):
  r=self.row(B,'PA66-5BL','N2');self.assertEqual(r['source_TGIR_N2_flow_mL_min'],'55');self.assertFalse(r.get('source_TG_flow_mL_min'));self.assertFalse(r.get('source_TG_mass_mg'));self.assertEqual(r['heating_rate_C_min'],'20')
 def test_borate_method_range_not_guessed_from_r800_or_axis(self):
  r=self.row(B,'PA66-Control','air');self.assertFalse(r.get('TG_start_C'));self.assertFalse(r.get('TG_end_C'));self.assertEqual(r['residue_temp_C'],'800')
 def test_borate_stock_and_bath_concentrations_remain_distinct(self):
  r=self.row(B,'PA66-5BL','N2');self.assertEqual((r['source_CS_bath_g_L'],r['source_PA_bath_g_L'],r['source_PA_stock_wt_pct']),('10','20','70'));self.assertEqual(r['source_addon_pct'],'8.7');self.assertEqual(r['source_borate_bath_wt_pct'],'0')
 def test_borate_missing_crosslink_times_explicit_and_no_washed_loi(self):
  r=self.row(B,'PA66-5BL-B1W','air');self.assertEqual((r['source_crosslink_immersion_time'],r['source_crosslink_heat_C'],r['source_crosslink_heat_duration']),('Designatedtimeunreported','90','Unreported'));self.assertTrue(all(not x['source_native_LC']for x in self.rows if x['DOI']==B));self.assertEqual(r['LOI_sample_dimensions_mm'],'150x58x0.2')
 def test_all_twenty_two_held_facts_outside_target(self):
  rr=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(rr),22);self.assertTrue(all(r['review_disposition']=='held_outside_verified_target'and all(not r.get(k)for k in pairing.TG_FIELDS)for r in rr))
if __name__=='__main__':unittest.main()
