"""Protect material identity, native loss definitions and separate hold protocols."""
import csv, sys, unittest
from pathlib import Path
import pandas as pd
H=Path(__file__).resolve().parent; P=H.name=='work'; R=H.parent/'repo'if P else H.parent
F=H/'staged-local-textile-b126/publication_proposed.csv'if P else R/'data/incoming/verified_source_batch_20261002_b126_local_textile.csv'
sys.path.insert(0,str(R/'scripts')); import pairing, validate_tg_loi as v
HF='10.1016/j.polymdegradstab.2004.11.013'; DN='10.1016/j.carbpol.2013.03.066'
class TextileB126Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def source(self,d):return[r for r in self.rows if r['DOI']==d]
 def dynamic(self,s,g):return next(r for r in self.source(DN)if r['sample_state']==s and r['atmosphere']==g and r['pairing_status']=='verified_exact')
 def reject(self,r,**kw):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**kw)))
 def test_four_states_eight_dynamic_conditions_not_thirtyfour_facts(self):
  z=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(z['errors']);self.assertEqual((z['verified_exact_sample_states'],z['verified_exact_condition_records']),(4,8));self.assertEqual(len(self.rows),34);self.assertEqual(sum(r['pairing_status']!='verified_exact'for r in self.rows),26)
 def test_hfpo_all_nineteen_facts_remain_held(self):
  rr=self.source(HF);self.assertEqual(len(rr),19);self.assertTrue(all(r['pairing_status']!='verified_exact'and all(not r.get(k,'')for k in pairing.TG_FIELDS)for r in rr))
 def test_hfpo_pure_pa6_knit_pa66_woven_not_nyco_loi(self):
  rr=[r for r in self.source(HF)if r['pairing_status']=='held_pure_nylon_TG_no_own_LOI'];self.assertEqual(len(rr),6);self.assertTrue(all(not r['LOI_pct']for r in rr));self.assertEqual(len({r['material_form']for r in rr}),2);self.assertTrue(any('PA6knit' in r['material_form']for r in rr));self.assertTrue(any('PA66woven' in r['material_form']for r in rr))
 def test_hfpo_pa6_dsc_not_dtg(self):
  r=next(r for r in self.source(HF)if r['sample_state']=='PA6-control');self.assertEqual((r['source_reported_DTG_Tmax_C'],r['source_reported_DSC_peak_C'],r['source_reported_R500_pct']),('424','425','10'));self.assertFalse(r['Tmax1_C'])
 def test_hfpo_b1_b2_loi_series_and_dash(self):
  rr=[r for r in self.source(HF)if r['pairing_status']=='held_blend_LOI_no_own_blend_TG'];self.assertEqual(len(rr),11);a=[r for r in rr if r['sample_state']=='B1-NYCO'];b=[r for r in rr if r['sample_state']=='B2-NYCO'];self.assertEqual([r['LOI_pct']for r in a],['29.3','28.4','27.2','26.1','24.5']);self.assertEqual([r['LOI_pct']for r in b],['29.5','28.6','28.0','28.1','26.9','26.0']);self.assertTrue(all(r['source_Table8_LC50']=='dashnot0'for r in a))
 def test_hfpo_home_cycles_preserved_without_accelerated_conversion(self):
  r=next(r for r in self.source(HF)if r['sample_state']=='B2-NYCO'and r['source_native_home_laundering_cycles']=='50');self.assertEqual(r['washing_state'],'After50homewashingdryingcycles');self.assertEqual(r['LOI_pct'],'26.0');self.assertIn('AATCC124-1996',r['treatment_method'])
 def test_hfpo_active_bath_solids_not_stock_percent(self):
  r=next(r for r in self.source(HF)if r['sample_state']=='B2-NYCO');self.assertEqual((r['source_FR_bath_wt_pct'],r['source_XMM_bath_wt_pct'],r['source_TMM_bath_wt_pct']),('32','3.4','5.1'));self.assertEqual((r['source_DMDHEU_stock_solids_pct'],r['source_TMM_stock_solids_pct'],r['source_XMM_stock_solids_pct']),('44','80','85'))
 def test_hfpo_phosphorus_conflicts_remain_raw(self):
  r=next(r for r in self.source(HF)if r['sample_state']=='B1-NYCO'and r['source_native_home_laundering_cycles']=='10');self.assertEqual((r['source_Table7_P_pct'],r['source_prose_P_pct']),('1.15','1.55'));r=next(r for r in self.source(HF)if r['sample_state']=='PA6-FR40DMDHEU2.6TMM4.8'and r['source_native_home_laundering_cycles']=='0');self.assertEqual((r['source_Table2_initial_P_pct'],r['source_prose_initial_P_pct']),('6.51','4.51'))
 def test_hfpo_a1_a2_curve_only_no_estimates(self):
  rr=[r for r in self.source(HF)if r['pairing_status']=='held_formula_curve_only_no_numeric_LOI_or_own_TG'];self.assertEqual(len(rr),2);self.assertTrue(all(not r['LOI_pct']for r in rr));self.assertTrue(all('Fig5' in r['LOI_locator']for r in rr))
 def test_dna_native_tonset10_maps_only_t10(self):
  r=self.dynamic('COT_DNA_19%','N2');self.assertEqual(r['T10_C'],'243');self.assertFalse(r['Tonset_C']);self.assertFalse(r['T5_C']);self.reject(r,T10_C='',Tonset_C='243')
 def test_dna_own_loi_matches_initial_addon_states(self):
  self.assertEqual([self.dynamic(s,'N2')['LOI_pct']for s in ['COT','COT_DNA_5%','COT_DNA_10%','COT_DNA_19%']],['18','23','25','28']);r=self.dynamic('COT_DNA_19%','air');self.reject(r,LOI_pct='23');self.assertTrue(all(r['washing_state']=='Initialasprepared0durabilitywashes'for r in self.source(DN)if r['pairing_status']=='verified_exact'))
 def test_dna_measured_addon_not_bath_or_composite_fraction(self):
  r=self.dynamic('COT_DNA_19%','N2');self.assertEqual((r['source_addon_pct'],r['source_DNA_bath_wt_pct'],r['source_native_addon_denominator']),('19','2.5','Wi,untreateddrymass'));self.assertFalse(r.get('additive_loading_wt_pct'));self.assertIn('applicationrepeatcountunreported',r['treatment_method'])
 def test_dna_n2_and_air_have_distinct_peaks(self):
  n=self.dynamic('COT_DNA_10%','N2');a=self.dynamic('COT_DNA_10%','air');self.assertEqual((n['Tmax1_C'],a['Tmax1_C'],a['Tmax2_C']),('314','302','511'));self.assertFalse(n['Tmax2_C']);self.assertFalse(a['Tmax3_C']);self.reject(n,Tmax2_C='511')
 def test_dna_at_peak_residue_not_fixed_char(self):
  r=self.dynamic('COT_DNA_19%','air');self.assertEqual((r['residue_at_Tmax1_pct'],r['residue_at_Tmax2_pct'],r['R600_pct']),('68','29','19'));self.reject(r,R600_pct='68',residue_pct='68');self.reject(r,R600_pct='98',residue_pct='98')
 def test_dna_r600_not_method_endpoint_and_explicit_zero_valid(self):
  r=self.dynamic('COT','air');self.assertEqual((r['R600_pct'],r['residue_pct'],r['residue_temp_C'],r['TG_end_C']),('0','0','600','800'));self.assertFalse(pairing.evidence_issues(r));self.reject(r,residue_temp_C='800')
 def test_dna_separate_isothermal_protocol_retained_without_dynamic_merge(self):
  rr=[r for r in self.source(DN)if r['pairing_status'].startswith('held_distinct_isothermal')];self.assertEqual(len(rr),4);self.assertEqual([r['source_isothermal_R350_pct']for r in rr],['13','30','35','42']);self.assertTrue(all(r['source_isothermal_hold_C']=='350'and r['source_isothermal_hold_min']=='60'and r['source_isothermal_ramp_rate_C_min']=='10'and not r['heating_rate_C_min']and all(not r.get(k,'')for k in pairing.TG_FIELDS)for r in rr));self.assertEqual(self.dynamic('COT_DNA_19%','air')['R600_pct'],'19')
 def test_dna_three_pure_compound_references_have_no_textile_loi(self):
  rr=[r for r in self.source(DN)if r['pairing_status'].startswith('held_pure_DNA')];self.assertEqual(len(rr),3);self.assertTrue(all(not r['LOI_pct']and all(not r.get(k,'')for k in pairing.TG_FIELDS)for r in rr));self.assertEqual({r['source_reported_R600_pct']for r in rr if r.get('source_reported_R600_pct')},{'50','49'})
 def test_dna_alumina_pan_flow_and_unknown_loi_dimensions_not_other_tests(self):
  rr=[r for r in self.source(DN)if r['pairing_status']=='verified_exact'];self.assertTrue(all((r['TG_pan'],r['TG_flow_mL_min'],r['TG_start_C'],r['TG_end_C'])==('Openaluminapans','60','50','800')for r in rr));self.assertTrue(all(not r.get('LOI_sample_dimensions_mm')and not r.get('LOI_repeats')for r in rr));self.assertTrue(all('acceptedmanuscript' in r['source_document_version']and 'PDFp20printed19' in r['TG_locator']for r in rr))
if __name__=='__main__':unittest.main()
