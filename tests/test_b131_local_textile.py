"""Guard orthogonal formulation identity, gas-specific thresholds and washed states."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
H=Path(__file__).resolve().parent;PVT=H.name=='work';R=H.parent/'repo'if PVT else H.parent
F=H/'staged-local-textile-b131/publication_proposed.csv'if PVT else R/'data/incoming/verified_source_batch_20261002_b131_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing,validate_tg_loi as v
I='10.1007/s12221-015-0388-z';P='10.1007/s10570-021-03767-0'
class TextileB131Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def source(self,d):return[r for r in self.rows if r['DOI']==d]
 def exact(self,d,s,g='N2'):return next(r for r in self.source(d)if r['sample_state']==s and r['atmosphere']==g and r['pairing_status']=='verified_exact')
 def reject(self,r,**kw):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**kw)))
 def test_twelve_states_twenty_two_conditions_not62facts(self):
  z=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(z['errors']);self.assertEqual((z['verified_exact_sample_states'],z['verified_exact_condition_records']),(12,22));self.assertEqual(len(self.rows),62)
 def test_all40_held_orthogonal_and_wash_facts_have_no_paired_tg(self):
  rr=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(rr),40);self.assertTrue(all(all(not r.get(k,'')for k in pairing.TG_FIELDS)and not r['material_form_TGA']for r in rr))
 def test_ispa_native_dtg_and_fixed600_residue_not_estimates(self):
  c=self.exact(I,'Purecottoncontrol');o=self.exact(I,'ISPAoptimalA5B4C5D4');self.assertEqual((c['Tmax1_C'],c['Tmax2_C'],c['R600_pct'],o['Tmax1_C'],o['R600_pct']),('350','525','0.1','300','30'));self.assertFalse(o['Tmax2_C']);self.assertFalse(c['R800_pct']);self.assertFalse(o['R800_pct'])
 def test_ispa_scarcely_char_not_control_zero(self):
  r=self.exact(I,'Purecottoncontrol');self.assertEqual(r['residue_pct'],'0.1');self.reject(r,residue_pct='0',R600_pct='0')
 def test_ispa_optimal_not_trial21_or24_loi(self):
  r=self.exact(I,'ISPAoptimalA5B4C5D4');self.assertEqual((r['LOI_pct'],r['source_phosphoricacid_bath_wt_pct'],r['source_cyanuricacid_bath_wt_pct'],r['source_cure_C']),('36.6','1.5','2','170'));self.reject(r,LOI_pct='34.2');self.reject(r,LOI_pct='34.0');self.assertIn('ONLYcontrolandoptimal',r['pairing_evidence'])
 def test_ispa98percent_mass_not_t5_t10_or_assumed_onset(self):
  for s in ['Purecottoncontrol','ISPAoptimalA5B4C5D4']:
   r=self.exact(I,s);self.assertTrue(all(not r[k]for k in ['T5_C','T10_C','Tonset_C']));self.assertIn('98percent',r['source_printed_TG_annotations']);self.reject(r,T5_C=r['source_generic_degradation_begin_C'])
 def test_all25_orthogonal_formulations_unique_and_no_own_tg(self):
  rr=[r for r in self.source(I)if r['source_orthogonal_trial']];self.assertEqual({int(r['source_orthogonal_trial'])for r in rr},set(range(1,26)));self.assertEqual(len({(r['source_ISPA_bath_wt_pct'],r['source_phosphoricacid_bath_wt_pct'],r['source_cyanuricacid_bath_wt_pct'],r['source_cure_C'])for r in rr}),25);self.assertTrue(all(r['pairing_status']!='verified_exact'for r in rr))
 def test_ispa_factor_levels_and_cure_temperature_not_row_order(self):
  rr=[r for r in self.source(I)if r['source_orthogonal_trial']];a=next(r for r in rr if r['source_orthogonal_trial']=='9');b=next(r for r in rr if r['source_orthogonal_trial']=='21');self.assertEqual((a['source_ISPA_bath_wt_pct'],a['source_cure_C'],a['LOI_pct']),('15','140','28.7'));self.assertEqual((b['source_phosphoricacid_bath_wt_pct'],b['source_cure_C'],b['LOI_pct']),('0','170','34.2'))
 def test_ispa_processing_boiling_not_durability_and_dose_not_dryloading(self):
  r=self.exact(I,'ISPAoptimalA5B4C5D4');self.assertIn('preparationboilnotdurability',r['washing_state']);self.assertIn('wtpercentbasisunreported',r['treatment_method']);self.assertFalse(r.get('additive_loading_wt_pct'));self.assertIn('notunreactedSPDPC',r['source_ISPA_identity'])
 def test_ispa_own_n2_conditions_and_loi_dimensions_not_vertical_repeats(self):
  r=self.exact(I,'ISPAoptimalA5B4C5D4');self.assertEqual((r['heating_rate_C_min'],r['TGA_gas_flow_mL_min'],r['TG_start_C'],r['TG_end_C'],r['source_TG_sample_mass_range_mg'],r['LOI_sample_dimensions_mm']),('10','50','50','800','3-5','130x60'));self.assertIn('notLOI',r['source_LOI_repeats']);self.reject(r,atmosphere='air')
 def test_cotp_ten_initial_codes_twenty_gas_records(self):
  rr=[r for r in self.source(P)if r['pairing_status']=='verified_exact'];self.assertEqual(len(rr),20);states={r['sample_state']for r in rr};self.assertEqual(len(states),10);self.assertEqual(states,{'COT'}|{f'COTP{x}-{t}'for x in [1,2,3]for t in [30,60,90]});self.assertTrue(all({r['atmosphere']for r in rr if r['sample_state']==s}=={'N2','air'}for s in states))
 def test_cotp_source_t10_not_t5_onset(self):
  r=self.exact(P,'COTP3-90');self.assertEqual(r['T10_C'],'227.32');self.assertFalse(r['T5_C']);self.assertFalse(r['Tonset_C']);self.reject(r,T10_C='',T5_C='227.32')
 def test_cotp_air_secondary_peaks_not_n2_second_peak(self):
  a=self.exact(P,'COTP3-90','air');n=self.exact(P,'COTP3-90');self.assertEqual((a['Tmax1_C'],a['Tmax2_C'],n['Tmax1_C']),('257.06','522.56','262.12'));self.assertFalse(n['Tmax2_C']);self.reject(n,Tmax2_C='522.56')
 def test_cotp_same_sample_residue_depends_on_gas(self):
  n=self.exact(P,'COTP3-90');a=self.exact(P,'COTP3-90','air');self.assertEqual((n['R800_pct'],a['R800_pct'],n['residue_temp_C'],a['residue_temp_C']),('39.33','4.55','800','800'));self.reject(a,R800_pct='39.33',residue_pct='39.33');self.reject(n,atmosphere='air')
 def test_cotp_main10_not_tgir20_rate(self):
  r=self.exact(P,'COTP2-60');self.assertEqual(r['heating_rate_C_min'],'10');self.assertIn('separateTGIR20',r['source_main_TG_mass_pan_flow_range']);self.reject(r,heating_rate_C_min='20')
 def test_cotp_unknown_mass_flow_end_not_borrowed_from_tgir(self):
  rr=[r for r in self.source(P)if r['pairing_status']=='verified_exact'];self.assertTrue(all(not r.get('TGA_gas_flow_mL_min')and not r.get('TG_mass_mg')and not r.get('TG_start_C')and not r.get('TG_end_C')for r in rr));self.assertEqual({r['TGA_instrument']for r in rr},{'NetzschTG209F1'})
 def test_cotp_all15_washed_lois_held_native_domestic_equivalence(self):
  rr=[r for r in self.source(P)if r['source_native_domestic_equivalent_LCs']];self.assertEqual(len(rr),15);self.assertEqual({r['source_native_domestic_equivalent_LCs']for r in rr},{'10','20','30','40','50'});self.assertTrue(all(r['pairing_status']!='verified_exact'and 'onewash=5domesticLCsexplicit'in r['source_wash_method']for r in rr))
 def test_cotp_precise_printed_loi_not_rounded_extra_states(self):
  a=self.exact(P,'COTP2-90');b=self.exact(P,'COTP3-90');self.assertEqual((a['LOI_pct'],a['source_SI4_initial_rounded_LOI_pct'],b['LOI_pct'],b['source_SI4_initial_rounded_LOI_pct']),('40.77','40.8','42.53','42.5'));self.assertIn('printedLOInumber',a['pairing_evidence']);self.reject(b,LOI_pct='42.5')
 def test_cotp_grafting_increment_not_mass_ratio_or_composite_loading(self):
  r=self.exact(P,'COTP3-90');self.assertEqual((r['source_COT_PA_urea_mass_ratio'],r['source_GR_pct'],r['source_graft_time_min']),('1:3:6','12.3','90'));self.assertIn('beforemodificationdenominator',r['source_GR_definition']);self.assertFalse(r.get('additive_loading_wt_pct'));self.assertIn('activeacidbasisunreported',r['treatment_method'])
 def test_cotp_comparison_reference_lois_not_own_control(self):
  r=self.exact(P,'COT');self.assertEqual(r['LOI_pct'],'17.2');self.assertEqual({r['DOI']for r in self.rows},{I,P});self.assertFalse(any(r['sample_state']in ['PCQS/phyticacid/PEI','DNA/chitosan','P-N-COT']for r in self.rows));self.reject(r,LOI_pct='29.8')
 def test_cotp_si5_conflicting_burn_char_label_not_washed_tg(self):
  rr=[r for r in self.source(P)if r['source_native_domestic_equivalent_LCs']];self.assertTrue(all('CaptionCOTP3-90butfirstcolumnCOTP3-30'in r['source_SI5_label_conflict']and not r['R800_pct']for r in rr))
 def test_same32point6_initial_and_washed_loi_not_same_state(self):
  a=self.exact(P,'COTP1-90');b=next(r for r in self.source(P)if r['sample_state']=='COTP2-90'and r['source_native_domestic_equivalent_LCs']=='10');self.assertEqual((a['LOI_pct'],b['LOI_pct']),('32.6','32.6'));self.assertNotEqual(a['sample_state'],b['sample_state']);self.assertNotEqual(a['washing_state'],b['washing_state']);self.assertFalse(b['T10_C']);self.reject(a,washing_state=b['washing_state'])
if __name__=='__main__':unittest.main()
