"""Guard coded sample correspondence, uncertain peaks and unread supplements."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
H=Path(__file__).resolve().parent;PVT=H.name=='work';R=H.parent/'repo'if PVT else H.parent
F=H/'staged-local-textile-b127/publication_proposed.csv'if PVT else R/'data/incoming/verified_source_batch_20261002_b127_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing,validate_tg_loi as v
HB='10.1007/s10570-019-02923-x';PAN='10.1002/app.46752';PA='10.1016/j.polymdegradstab.2020.109376'
class TextileB127Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def source(self,d):return[r for r in self.rows if r['DOI']==d]
 def exact(self,d,s):return next(r for r in self.source(d)if r['sample_state']==s and r['pairing_status']=='verified_exact')
 def reject(self,r,**kw):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**kw)))
 def test_only_six_states_six_conditions_of_thirtyfive_facts(self):
  z=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(z['errors']);self.assertEqual((z['verified_exact_sample_states'],z['verified_exact_condition_records']),(6,6));self.assertEqual(len(self.rows),35);self.assertEqual(sum(r['pairing_status']!='verified_exact'for r in self.rows),29)
 def test_hb_only_initial_untreated_and_selected160gL_match_tg(self):
  rr=[r for r in self.source(HB)if r['pairing_status']=='verified_exact'];self.assertEqual({r['source_HBPPN_bath_g_L']for r in rr},{'0','160'});self.assertTrue(all(r['source_native_laundering_cycles']=='0'for r in rr));r=self.exact(HB,'HBPPN-160g/L cotton');self.assertEqual((r['LOI_pct'],r['Tmax1_C']),('39.6','316'));self.reject(r,LOI_pct='27.3')
 def test_hb_other_dose_and_wash_facts_have_no_canonical_tg(self):
  rr=[r for r in self.source(HB)if r['pairing_status']!='verified_exact'];self.assertEqual(len(rr),15);self.assertTrue(all(all(not r.get(k,'')for k in pairing.TG_FIELDS)for r in rr));self.assertEqual([r['LOI_pct']for r in rr if r['source_HBPPN_bath_g_L']=='80'],['29','26.4','24.7','20.5'])
 def test_hb_main_tg20_not_tgir10_or_tgir_mass(self):
  r=self.exact(HB,'HBPPN-160g/L cotton');self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['TG_start_C'],r['TG_end_C']),('N2','20','30','800'));self.assertFalse(r.get('TG_mass_mg'));self.assertFalse(r.get('TG_pan'));self.reject(r,heating_rate_C_min='10')
 def test_hb_reported_residue_temperature_unfixed_canonical_blank(self):
  r=self.exact(HB,'HBPPN-160g/L cotton');self.assertEqual(r['source_reported_residue_pct'],'30.6');self.assertTrue(all(not r[k]for k in ['residue_pct','char_pct','residue_temp_C','char_temp_C','R800_pct']));self.reject(r,R800_pct='30.6',residue_pct='30.6',residue_temp_C='800')
 def test_hb_ranges_and_water_stages_not_t5_t10_onset(self):
  r=self.exact(HB,'Untreated cotton');self.assertEqual(r['source_reported_decomposition_interval_C'],'305-398');self.assertTrue(all(not r[k]for k in ['T5_C','T10_C','Tonset_C']));self.reject(r,Tonset_C='305');self.reject(r,Tmax1_C='200')
 def test_hb_native_wg_and_bath_dose_remain_distinct(self):
  r=self.exact(HB,'HBPPN-160g/L cotton');self.assertEqual((r['source_HBPPN_bath_g_L'],r['source_Table2_WG_pct'],r['source_WG_definition']),('160','27.6','(W2-W1)/W1*100'));self.assertIn('basis unreported',r['treatment_method']);self.assertFalse(r.get('additive_loading_wt_pct'))
 def test_hb_native_cycles_not_unreported_fivefold_equivalence(self):
  r=next(r for r in self.source(HB)if r['source_HBPPN_bath_g_L']=='160'and r['source_native_laundering_cycles']=='50');self.assertEqual((r['LOI_pct'],r['washing_state']),('27.3','After50native durabilityLC'));self.assertEqual(r['source_wash_method'],'AATCC61-2006');self.assertFalse(r.get('LOI_repeats'))
 def test_pan_tonset5_is_t5_not_generic_onset(self):
  r=self.exact(PAN,'PAN');self.assertEqual(r['T5_C'],'312');self.assertFalse(r['Tonset_C']);self.assertFalse(r['T10_C']);self.reject(r,T5_C='',Tonset_C='312')
 def test_pan_own_initial_codes_match_loi_tg_not_washed(self):
  self.assertEqual([self.exact(PAN,s)['LOI_pct']for s in ['PAN','PAN-g-GMA (47 wt%)','Am-PAN-g-GMA','FR-PAN']],['17','16.3','17.5','34.2']);r=self.exact(PAN,'FR-PAN');self.reject(r,LOI_pct='30.7');self.reject(r,washing_state='After30native TableIV cycles')
 def test_pan_low_temperature_peaks_unassigned_not_decomposition(self):
  a=self.exact(PAN,'Am-PAN-g-GMA');f=self.exact(PAN,'FR-PAN');self.assertEqual((a['source_native_low_temperature_Tmax1_C'],f['source_native_low_temperature_Tmax1_C']),('52','92'));self.assertFalse(a['Tmax1_C']);self.assertFalse(f['Tmax1_C']);self.assertEqual((a['Tmax2_C'],a['Tmax3_C'],a['Tmax4_C']),('154','332','425'));self.reject(f,Tmax1_C='92')
 def test_pan_fr_conflicting282_285_and_fifth_peak_not_renumbered(self):
  r=self.exact(PAN,'FR-PAN');self.assertEqual((r['source_native_TableII_Tmax4_C'],r['source_prose_cyclization_temperature_C'],r['source_native_TableII_Tmax5_C']),('282','285','396'));self.assertFalse(r['Tmax4_C']);self.assertEqual(r['Tmax3_C'],'218');self.reject(r,Tmax4_C='282');self.reject(r,Tmax3_C='396')
 def test_pan_recipe_gp_conflict_raw_bath_dose_not_invented(self):
  r=self.exact(PAN,'FR-PAN');self.assertEqual((r['source_precursor_GP_method_pct'],r['source_precursor_GP_tables_pct']),('45','47'));self.assertTrue(r['source_scheme_only_urea']);self.assertTrue(r['source_acid_wording_conflict']);self.assertFalse(r.get('source_GMA_bath_wt_pct'));self.assertIn('settings unreported',r['treatment_method'])
 def test_pan_r800_not_cone_residue_or_invented_tg_conditions(self):
  r=self.exact(PAN,'FR-PAN');self.assertEqual((r['R800_pct'],r['residue_pct'],r['residue_temp_C']),('48.1','48.1','800'));self.reject(r,R800_pct='42',residue_pct='42');self.assertFalse(r.get('TG_mass_mg'));self.assertFalse(r.get('TG_flow_mL_min'));self.assertFalse(r.get('TG_start_C'));self.assertEqual(r['source_TG_start_method'],'Room temperature')
 def test_pan_four_native_washed_lois_no_tg_borrowing_or_extra_conversion(self):
  rr=[r for r in self.source(PAN)if r['pairing_status']!='verified_exact'];self.assertEqual([r['LOI_pct']for r in rr],['34.1','33.5','31.6','30.7']);self.assertEqual([r['source_native_laundering_cycles']for r in rr],['5','10','20','30']);self.assertTrue(all(all(not r.get(k,'')for k in pairing.TG_FIELDS)for r in rr));self.assertTrue(all('without extra5x' in r['source_wash_equivalence']for r in rr));r=self.exact(PAN,'PAN');self.assertEqual((r['LOI_repeats'],r['LOI_sample_dimensions_mm']),('5','5x15,as printed; not corrected to cm'))
 def test_pa66_cited_unread_si_all_ten_raw_gas_records_excluded(self):
  rr=self.source(PA);self.assertEqual(len(rr),10);self.assertTrue(all(r['pairing_status']=='held_cited_SI_unread_complete_primary_only'and all(not r.get(k,'')for k in pairing.TG_FIELDS)for r in rr));self.assertEqual({r['source_reported_atmosphere']for r in rr},{'air','N2'});self.assertTrue(all('unread' in r['supplement_review_status']for r in rr))
 def test_pa66_explicit_table_gas_not_conflicting_caption(self):
  a=next(r for r in self.source(PA)if r['sample_state']=='PA66-C-M-A-GPA-3HL'and r['source_reported_atmosphere']=='air');n=next(r for r in self.source(PA)if r['sample_state']==a['sample_state']and r['source_reported_atmosphere']=='N2');self.assertEqual((a['source_reported_T5_C'],a['source_reported_Tmax1_C'],a['source_reported_Tmax2_C'],a['source_reported_R800_pct']),('345','438','639','3.7'));self.assertEqual((n['source_reported_T5_C'],n['source_reported_Tmax1_C'],n['source_reported_Tmax2_C'],n['source_reported_R800_pct']),('378','431','','6.7'));self.assertIn('caption not used',a['TG_locator'])
 def test_pa66_native_bath_units_alias_unknown_control_addon(self):
  r=next(r for r in self.source(PA)if r['sample_state']=='Untreated PA66');self.assertFalse(r['source_native_addon_pct']);r=next(r for r in self.source(PA)if r['sample_state']=='PA66-C-M-A-GPA-3HL');self.assertEqual((r['source_phosphor_bath_g_L'],r['source_native_addon_pct']),('0.1','3.5'));self.assertFalse(r.get('TG_flow_mL_min'));r=next(r for r in self.source(PA)if r['sample_state']=='PA66-C-M-A-4.5QL');self.assertEqual(r['source_noP_label_alias'],'4.5QL/9BL both18layers')
if __name__=='__main__':unittest.main()
