"""Guard burning-char, fixed TG temperature, missing conditions and state identity."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
H=Path(__file__).resolve().parent;P=H.name=='work';R=H.parent/'repo'if P else H.parent
F=H/'staged-local-textile-b124/publication_proposed.csv'if P else R/'data/incoming/verified_source_batch_20261002_b124_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing,validate_tg_loi as v
PL='10.1007/s10570-013-0127-9';AH='10.1007/s10570-015-0641-z';MP='10.1016/j.carbpol.2012.12.008';AT='10.1007/s10570-018-1964-3'
class TextileB124Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def source(self,d):return[r for r in self.rows if r['DOI']==d]
 def row(self,d,s,gas=None):return next(r for r in self.source(d)if r['sample_state']==s and(gas is None or r['atmosphere']==gas))
 def rejected(self,r,**changes):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**changes)))
 def test_four_independent_states_six_conditions_not_fiftyseven_candidates(self):
  z=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(z['errors']);self.assertEqual((z['verified_exact_sample_states'],z['verified_exact_condition_records']),(4,6));self.assertEqual(len(self.rows),57);self.assertEqual(sum(r['pairing_status']!='verified_exact'for r in self.rows),51)
 def test_plasma_complete_burning_char_not_tg_residue(self):
  rr=self.source(PL);self.assertEqual(len(rr),4);self.assertEqual({r['source_complete_burning_char_pct']for r in rr},{'1.9','8.7','5.6','7.6'});self.assertTrue(all(all(not r.get(k)for k in pairing.TG_FIELDS+['residue_temp_C','char_temp_C'])for r in rr))
 def test_plasma_fresh_and_oneyear_samples_remain_distinct(self):
  a=self.row(PL,'N2 plasma treated cotton');b=self.row(PL,'N2 plasma treated cotton after one year');self.assertEqual((a['LOI_pct'],b['LOI_pct']),('21.8','21.2'));self.assertNotEqual(a['treatment_state'],b['treatment_state']);self.assertEqual(b['source_storage_duration_years'],'1')
 def test_plasma_generic_approximate330_and_dta_not_native_dtg_peak(self):
  rr=self.source(PL);self.assertTrue(all(r['source_generic_approximate_TG_onset_C']=='330'and r['source_other_thermal_curve']=='DTAFig8;notDTG'for r in rr));self.assertTrue(all(not r['Tonset_C']and not r['Tmax1_C']for r in rr))
 def test_plasma_conditions_kept_raw_without_promoting_curve_only_pairs(self):
  r=self.row(PL,'Untreated cotton');self.assertEqual((r['source_reported_TG_atmosphere'],r['source_reported_TG_heating_rate_C_min'],r['source_reported_TG_mass_mg'],r['source_reported_TG_flow_mL_min']),('N2','10','8','100'));self.assertFalse(r['atmosphere']);self.assertNotEqual(r['pairing_status'],'verified_exact');self.assertEqual(r['source_LOI_replicates'],'5')
 def test_ahdtmpa_explicit70gl_characterization_not_highest90gl(self):
  rr=[r for r in self.source(AH)if r['pairing_status']=='verified_exact'];self.assertEqual({r['source_AHDTMPA_bath_g_L']for r in rr},{'0','70'});self.assertEqual(self.row(AH,'AHDTMPA70 cotton')['LOI_pct'],'36');self.assertNotEqual(self.row(AH,'AHDTMPA90 cotton')['pairing_status'],'verified_exact')
 def test_ahdtmpa_fixed580_not600_method_endpoint(self):
  r=self.row(AH,'AHDTMPA70 cotton');self.assertEqual((r['residue_pct'],r['residue_temp_C'],r['TG_end_C']),('42.1','580','600'));self.rejected(r,residue_temp_C='600',char_temp_C='600');self.assertEqual(self.row(AH,'Control cotton')['char_pct'],'5.3')
 def test_ahdtmpa_rapidloss_ranges_not_onset_or_dtg(self):
  r=self.row(AH,'AHDTMPA70 cotton');self.assertEqual(r['source_reported_rapid_weight_loss_range_C'],'290-320');self.assertTrue(all(not r[k]for k in ['Tonset_C','T5_C','T10_C','Tmax1_C']));self.rejected(r,Tonset_C='290',Tmax1_C='320');self.rejected(r,residue_pct='26',char_pct='26')
 def test_ahdtmpa_own_control16_and_unreported_initial70wg(self):
  self.assertEqual(self.row(AH,'Control cotton')['LOI_pct'],'16');self.assertFalse(self.row(AH,'AHDTMPA70 cotton')['source_WG_pct']);r=self.row(AH,'AHDTMPA70-LC50');self.assertEqual(r['source_approximate_washed_WG_pct'],'12');self.assertFalse(r['source_WG_pct'])
 def test_ahdtmpa_four_other_doses_four_washes_do_not_borrow_tg(self):
  rr=[r for r in self.source(AH)if r['pairing_status']!='verified_exact'];self.assertEqual(len(rr),8);self.assertEqual(sum(bool(r['source_native_LC'])for r in rr),4);self.assertTrue(all(all(not r.get(k,'')for k in pairing.TG_FIELDS)for r in rr))
 def test_mpd_thirteen_own_lois_preserved_outside_target(self):
  rr=[r for r in self.source(MP)if r['LOI_pct']];self.assertEqual(len(rr),13);self.assertEqual(self.row(MP,'MPD2percent cotton')['LOI_pct'],'18.7');self.assertEqual(self.row(MP,'Pyrovatex5percent cotton')['LOI_pct'],'18.3');self.assertTrue(all(r['pairing_status']!='verified_exact'for r in rr))
 def test_mpd_gas_rate_unreported_and_generic_dose_unmapped(self):
  rr=self.source(MP);self.assertEqual(len(rr),16);self.assertTrue(all(not r['atmosphere']and not r['heating_rate_C_min']for r in rr));r=self.row(MP,'MPD cotton generic TG raw');self.assertFalse(r['LOI_pct']);self.assertIn('doseunmapped',r['limitations'])
 def test_mpd_prose_and_direct_figure_starts_not_silently_reconciled(self):
  r=self.row(MP,'Untreated cotton TG raw');self.assertEqual((r['source_prose_decomposition_start_C'],r['source_Fig4_segment_start_C']),('333','215.87'));r=self.row(MP,'Pyrovatex cotton generic TG raw');self.assertEqual((r['source_prose_decomposition_start_C'],r['source_Fig4_segment_start_C']),('286','127.95'));self.assertTrue(all(not r.get(k,'')for r in self.source(MP)for k in pairing.TG_FIELDS))
 def test_mpd_water_stage_not_onset_and_massloss_not_derived_char(self):
  r=self.row(MP,'MPD cotton generic TG raw');self.assertEqual((r['source_Fig4_low_temperature_water_start_C'],r['source_Fig4_segment_weight_loss_pct']),('24.59','78.944'));self.assertFalse(r['Tonset_C']);self.assertFalse(r['char_pct']);self.assertEqual(r['source_LOI_test_C'],'29');self.assertEqual(r['source_general_conditioning_C'],'20+/-2')
 def test_atepea_explicit250gl_has_four_gas_records_two_states(self):
  rr=[r for r in self.source(AT)if r['pairing_status']=='verified_exact'];self.assertEqual(len(rr),4);self.assertEqual({r['source_ATEPEA_bath_g_L']for r in rr},{'0','250'});self.assertEqual({r['atmosphere']for r in rr},{'N2','air'});self.assertEqual(self.row(AT,'ATEPEA250 cotton','N2')['source_WG_pct'],'23.82')
 def test_atepea_native_t10_definition_not_t5_or_genericonset(self):
  r=self.row(AT,'ATEPEA250 cotton','N2');self.assertEqual(r['T10_C'],'257.58');self.assertFalse(r['T5_C']);self.assertFalse(r['Tonset_C']);self.rejected(r,T10_C='',Tonset_C='257.58')
 def test_atepea_control_n2_char_conflict_and_air_dash_blank(self):
  r=self.row(AT,'Control cotton','N2');self.assertEqual((r['source_conflicting_Table1_R800_pct'],r['source_conflicting_later_prose_R800_pct']),('8.08','8.05'));self.assertFalse(r['char_pct']);self.assertFalse(r['residue_temp_C']);self.assertEqual(r['Tmax1_C'],'374.75');self.rejected(r,char_pct='8.08',residue_pct='8.08',residue_temp_C='800',char_temp_C='800');a=self.row(AT,'Control cotton','air');self.assertEqual(a['source_native_Table1_R800'],'dash');self.assertFalse(a['char_pct'])
 def test_atepea_tgir_mass_and_gaspeaks_cone_char_not_main_tg(self):
  r=self.row(AT,'ATEPEA250 cotton','N2');self.assertEqual((r['Tmax1_C'],r['char_pct'],r['residue_temp_C']),('289.45','38.14','800'));self.assertEqual(r['source_TGIR_mass_mg'],'8');self.assertFalse(r.get('source_TG_mass_mg'));self.rejected(r,Tmax1_C='300');self.rejected(r,char_pct='36.9',residue_pct='36.9');self.assertFalse(r['Tmax2_C'])
 def test_atepea_twenty_native_washed_states_no_own_tg(self):
  rr=[r for r in self.source(AT)if r['source_native_LC']];self.assertEqual(len(rr),20);self.assertEqual({r['source_native_LC']for r in rr},{'10','20','30','40','50'});self.assertTrue(all(all(not r.get(k,'')for k in pairing.TG_FIELDS)for r in rr));self.assertEqual(self.row(AT,'ATEPEA250-LC50')['LOI_pct'],'27.2')
 def test_atepea_native_review_header_and_own_experimental_basis_retained(self):
  rr=self.source(AT);self.assertTrue(all(r['source_native_article_type']=='Review Paper'and r['publication_type']=='journal_article'for r in rr));self.assertTrue(all('OwnExperimental' in r['source_own_measurement_basis']and 'NMRonly' in r['supplement_review_status']for r in rr));self.assertTrue(all(not r.get('LOI_sample_dimensions_mm')for r in rr))
if __name__=='__main__':unittest.main()
