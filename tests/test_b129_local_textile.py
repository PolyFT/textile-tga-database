"""Guard distinct thermal definitions, original conflicts and textile specimen identity."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
H=Path(__file__).resolve().parent;PVT=H.name=='work';R=H.parent/'repo'if PVT else H.parent
F=H/'staged-local-textile-b129/publication_proposed.csv'if PVT else R/'data/incoming/verified_source_batch_20261002_b129_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing,validate_tg_loi as v
T='10.1002/pol.20230165';A='10.1039/c7ta01106g';M='10.1002/app.43555'
class TextileB129Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def source(self,d):return[r for r in self.rows if r['DOI']==d]
 def exact(self,d,s,gas):return next(r for r in self.source(d)if r['sample_state']==s and r['atmosphere']==gas and r['pairing_status']=='verified_exact')
 def reject(self,r,**kw):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**kw)))
 def test_three_states_five_conditions_not_43facts(self):
  z=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(z['errors']);self.assertEqual((z['verified_exact_sample_states'],z['verified_exact_condition_records']),(3,5));self.assertEqual(len(self.rows),43);self.assertEqual(sum(r['pairing_status']!='verified_exact'for r in self.rows),38)
 def test_thpon_all_six_held_for_missing_rate_and_unmapped_dose(self):
  rr=self.source(T);self.assertEqual(len(rr),6);self.assertTrue(all(r['pairing_status']!='verified_exact'and not r['heating_rate_C_min']and all(not r[k]for k in pairing.TG_FIELDS)for r in rr))
 def test_thpon_t10_not_t5_or_onset_and_tend_not_test_end(self):
  rr=self.source(T);r=next(r for r in rr if r['sample_state']=='THPON-treated cotton;TGdoseunmapped');self.assertEqual((r['source_Table3_T10_C'],r['source_Table3_Tend_C'],r['source_Table3_R800_pct']),('277.33','337.16','40.44'));self.assertIn('notT5',r['source_T10_definition']);self.assertIn('nottestendpoint',r['source_Tend_definition']);self.assertFalse(r['T10_C'])
 def test_thpon_control_tmax_table_prose_conflict_not_chosen(self):
  r=next(r for r in self.source(T)if r['sample_state']=='THPON-0wtpercent');self.assertEqual(r['source_Table3_Tmax_C'],'367.43');self.assertIn('324.17',r['source_Tmax_conflict']);self.assertFalse(r['Tmax1_C'])
 def test_thpon_25_loi_conclusion_conflict_not_chosen(self):
  r=next(r for r in self.source(T)if r['sample_state']=='THPON-25wtpercent');self.assertEqual((r['source_Table1_LOI_pct'],r['source_conclusion_LOI_pct']),('27.34','22.34'));self.assertFalse(r['LOI_pct'])
 def test_thpon_cone25_not_tg_dose_or_wet_wg_dryloading(self):
  r=next(r for r in self.source(T)if 'TGdoseunmapped'in r['sample_state']);self.assertIn('ONLYcone',r['source_TG_dose_identity']);self.assertFalse(r.get('source_bath_THPON_wt_pct'));r=self.source(T)[0];self.assertIn('notassumeddryloading',r['source_native_precuring_WG_range']);self.assertFalse(r.get('additive_loading_wt_pct'))
 def test_aegdp_only_initial120_air_has_unambiguous_fixed_r600(self):
  r=self.exact(A,'AEGDP-120gL','air');self.assertEqual((r['LOI_pct'],r['R600_pct'],r['residue_temp_C'],r['heating_rate_C_min']),('41','27.94','600','20'));self.assertFalse(r['R800_pct']);self.reject(r,residue_temp_C='800',R800_pct='27.94');self.reject(r,atmosphere='N2')
 def test_aegdp_main_conditions_not_separate_tgir_mass_flow(self):
  r=self.exact(A,'AEGDP-120gL','air');self.assertEqual((r['TGA_instrument'],r['TG_start_C'],r['TG_end_C']),('Pyris1PerkinElmer','40','800'));self.assertFalse(r.get('TG_mass_mg'));self.assertFalse(r.get('TG_flow_mL_min'));self.assertFalse(r.get('TG_pan'))
 def test_aegdp_n2_conflicting14point92_and_more42point62_not_absolute(self):
  rr=[r for r in self.source(A)if r['source_reported_atmosphere']=='N2'and r['sample_state']!='PureAEGDP'];self.assertEqual(len(rr),2);self.assertTrue(all(all(not r[k]for k in pairing.TG_FIELDS)for r in rr));r=next(r for r in rr if r['sample_state']=='AEGDP-120gL');self.assertIn('notderived57.54',r['source_N2_residue_wording']);self.assertIn('conflicts',r['source_N2_residue_wording']);self.assertEqual(r['source_N2_Fig3_end_C'],'600')
 def test_aegdp_all15_washed_lois_held_native_cycles_not_guessed(self):
  rr=[r for r in self.source(A)if r.get('source_native_laundering_cycles')not in ('','0')];self.assertEqual(len(rr),15);self.assertEqual({r['source_native_laundering_cycles']for r in rr},{'10','20','30','40','50'});self.assertTrue(all(all(not r[k]for k in pairing.TG_FIELDS)for r in rr));r=next(r for r in rr if r['sample_state']=='AEGDP-120gL'and r['source_native_laundering_cycles']=='50');self.assertEqual((r['LOI_pct'],r['source_Table3_WG_after50Lcs_pct']),('28.4','14.8'))
 def test_aegdp_60_90_initial_not_120_tg_or_bath_wg_same(self):
  rr=[r for r in self.source(A)if r.get('source_native_laundering_cycles')=='0'];self.assertEqual(len(rr),3);r=self.exact(A,'AEGDP-120gL','air');self.assertEqual((r['source_AEGDP_bath_g_L'],r['source_initial_Table3_WG_pct']),('120','23.7'));self.assertFalse(r.get('additive_loading_wt_pct'));self.assertTrue(all(all(not x[k]for k in pairing.TG_FIELDS)for x in rr if x['sample_state']!='AEGDP-120gL'))
 def test_aegdp_control_cited_loi_not_confirmed_own_pair_or_assigned0(self):
  r=next(r for r in self.source(A)if r['sample_state']=='Controlcotton'and r['source_reported_atmosphere']=='air');self.assertEqual((r['source_candidate_control_LOI_pct'],r['source_reported_R500_pct']),('18.4','0'));self.assertFalse(r['LOI_pct']);self.assertFalse(r['R500_pct']);self.assertIn('reference38',r['source_control_LOI_provenance'])
 def test_mcp_two_states_four_gases_generic_onset_not_t5(self):
  vals={('Gauze0','N2'):'324.7',('Gauze4','N2'):'261.7',('Gauze0','air'):'297.4',('Gauze4','air'):'222.3'}
  for(s,g),t in vals.items():
   r=self.exact(M,s,g);self.assertEqual(r['Tonset_C'],t);self.assertFalse(r['T5_C']);self.assertFalse(r['T10_C']);self.assertFalse(r['Tmax1_C']);self.reject(r,Tonset_C='',T5_C=t)
 def test_mcp_printed_r800_annotations_not_burning47point6(self):
  a=self.exact(M,'Gauze4','N2');b=self.exact(M,'Gauze4','air');c=self.exact(M,'Gauze0','N2');self.assertEqual((a['R800_pct'],b['R800_pct'],c['R800_pct']),('42.3','31.4','8'));self.assertEqual(a['source_burning_char_TableI_pct'],'47.6');self.assertIn('notcurveestimated',a['source_R800_evidence']);self.reject(a,R800_pct='47.6',residue_pct='47.6');self.assertEqual(a['residue_temp_C'],'800')
 def test_mcp_air_control_grouped_zero_not_curve_estimated(self):
  r=self.exact(M,'Gauze0','air');self.assertTrue(all(not r[k]for k in ['R800_pct','residue_pct','char_pct','residue_temp_C','char_temp_C']));self.reject(r,R800_pct='0',residue_pct='0',residue_temp_C='800')
 def test_mcp_four_other_dose_lois_not_tg_or_same42point3(self):
  rr=[r for r in self.source(M)if r.get('source_MCP_bath_wt_pct')in ['5','10','15','25']];self.assertEqual([r['LOI_pct']for r in rr],['23.5','24.6','25.4','25.8']);self.assertTrue(all(all(not r[k]for k in pairing.TG_FIELDS)for r in rr));r=next(r for r in rr if r['sample_state']=='Gauze3');self.assertEqual(r['source_burning_char_TableI_pct'],self.exact(M,'Gauze4','N2')['R800_pct']);self.assertNotEqual(r['sample_state'],'Gauze4')
 def test_mcp_purefr_and_aegdp_purefr_not_own_textile_loi(self):
  rr=[r for r in self.rows if r['material_category']=='pureflameretardantreference'];self.assertEqual(len(rr),8);self.assertTrue(all(not r.get('LOI_pct')and not r['material_form_LOI']and all(not r[k]for k in pairing.TG_FIELDS)for r in rr))
 def test_mcp_unknown_prep_counts_and_loi_dims_not_guessed(self):
  r=self.exact(M,'Gauze4','N2');self.assertEqual((r['LOI_standard'],r['LOI_sample_dimensions_mm'],r['heating_rate_C_min'],r['TG_end_C']),('GB/T5454-1997','140x52','10','800'));self.assertIn('fixedcountunassigned',r['treatment_method']);self.assertEqual(r['source_MCP_bath_wt_pct'],'20');self.assertFalse(r.get('additive_loading_wt_pct'));self.assertFalse(r.get('TG_mass_mg'));self.assertFalse(r.get('LOI_repeats'));self.assertIn('notconverted',r['source_native_yarn_wording'])
if __name__=='__main__':unittest.main()
