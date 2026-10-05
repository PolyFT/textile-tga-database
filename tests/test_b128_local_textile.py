"""Protect wash/dose identity, source conflicts and unavailable TG definitions."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
H=Path(__file__).resolve().parent;PVT=H.name=='work';R=H.parent/'repo'if PVT else H.parent
F=H/'staged-local-textile-b128/publication_proposed.csv'if PVT else R/'data/incoming/verified_source_batch_20261002_b128_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing,validate_tg_loi as v
B='10.1007/s10570-021-04056-6';P='10.1002/app.49253'
class TextileB128Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def source(self,d):return[r for r in self.rows if r['DOI']==d]
 def exact(self,d,s):return next(r for r in self.source(d)if r['sample_state']==s and r['pairing_status']=='verified_exact')
 def reject(self,r,**kw):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**kw)))
 def test_six_states_six_conditions_not_fifteen_facts(self):
  z=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(z['errors']);self.assertEqual((z['verified_exact_sample_states'],z['verified_exact_condition_records']),(6,6));self.assertEqual(len(self.rows),15);self.assertEqual(sum(r['pairing_status']!='verified_exact'for r in self.rows),9)
 def test_bamboo_own_initial_four_codes_and_values(self):
  self.assertEqual([self.exact(B,s)['LOI_pct']for s in ['BF-0','BF-10','BF-20','BF-30']],['20.3','39.3','48.3','50.2']);r=self.exact(B,'BF-30');self.assertEqual((r['T5_C'],r['Tmax1_C'],r['Tmax2_C'],r['R700_pct']),('235','248','288','46.6'));self.reject(r,LOI_pct='44.5')
 def test_bamboo_tonset_defined_fivepercent_loss_maps_t5(self):
  r=self.exact(B,'BF-0');self.assertEqual(r['T5_C'],'264');self.assertFalse(r['Tonset_C']);self.assertFalse(r['T10_C']);self.reject(r,T5_C='',Tonset_C='264')
 def test_bamboo_main_tg_conditions_without_borrowed_tgir_start(self):
  r=self.exact(B,'BF-30');self.assertEqual((r['TGA_instrument'],r['atmosphere'],r['heating_rate_C_min'],r['TG_flow_mL_min'],r['TG_end_C'],r['TG_repeats']),('TAQ50','N2','10','40','700','3'));self.assertFalse(r.get('TG_start_C'));self.assertFalse(r.get('TG_mass_mg'));self.assertEqual(r['source_TG_mass_range_mg'],'About5-10');self.assertIn('Alumina',r['TG_pan'])
 def test_bamboo_dtg_and_fixed_char_not_cone_or_gasrelease_peaks(self):
  r=self.exact(B,'BF-30');self.assertEqual((r['residue_pct'],r['residue_temp_C']),('46.6','700'));self.reject(r,residue_pct='35.3',R700_pct='35.3');self.reject(r,Tmax1_C='373');self.assertFalse(self.exact(B,'BF-0')['Tmax2_C'])
 def test_bamboo_four_washed_lois_remain_without_tg(self):
  rr=[r for r in self.source(B)if r['pairing_status']!='verified_exact'];self.assertEqual([r['LOI_pct']for r in rr],['48.3','47.6','46.7','44.5']);self.assertEqual([r['source_native_laundering_cycles']for r in rr],['10','20','30','50']);self.assertTrue(all(r['source_wash_cycle_min']=='5'and r['source_wash_temperature_C']=='49'and r['source_neutral_detergent_g_L']=='2'and all(not r.get(k,'')for k in pairing.TG_FIELDS)for r in rr))
 def test_bamboo_bath_dose_and_measured_wg_not_same_loading(self):
  r=self.exact(B,'BF-30');self.assertEqual((r['source_ATTPMA_bath_wt_pct'],r['source_Table2_WG_pct'],r['source_WG_definition']),('30','33.8','(W2-W1)/W1*100'));self.assertFalse(r.get('additive_loading_wt_pct'));self.assertIn('basis/explicitidentityunreported',r['treatment_method']);self.assertEqual(r['source_catalyst_bath_wt_pct'],'8')
 def test_bamboo_loi_geometry_repeats_and_uncertainty_not_other_tests(self):
  r=self.exact(B,'BF-0');self.assertEqual((r['LOI_sample_dimensions_mm'],r['LOI_repeats'],r['LOI_standard']),('52x140','4','ASTM-D2863'));self.assertEqual(r['LOI_uncertainty_pct'],'0.1');self.assertIn('notassumedSD',r['source_LOI_uncertainty_definition']);self.assertIn('three-layer',r['material_form'])
 def test_bamboo_same48point3_is_not_same_sample_or_extra_initial_row(self):
  a=self.exact(B,'BF-20');w=next(r for r in self.source(B)if r.get('source_native_laundering_cycles')=='10');self.assertEqual(a['LOI_pct'],w['LOI_pct']);self.assertEqual(w['sample_state'],'BF-30');self.assertNotEqual(a['sample_state'],w['sample_state']);self.assertNotEqual(a['washing_state'],w['washing_state']);self.assertEqual(sum(r['sample_state']=='BF-30'and r['pairing_status']=='verified_exact'for r in self.source(B)),1)
 def test_pet_cot_own_two_initial_t5_values_not_generic_onset(self):
  a=self.exact(P,'(PAH/APP)10');m=self.exact(P,'(PAH-MEL/APP)10');self.assertEqual((a['T5_C'],a['LOI_pct'],m['T5_C'],m['LOI_pct']),('290','26.3','300','28.4'));self.assertFalse(a['Tonset_C']);self.assertFalse(a['Tmax1_C']);self.reject(a,T5_C='',Tonset_C='290')
 def test_pet_cot_main_tg_not_pcfc_rate_mass_or_air(self):
  r=self.exact(P,'(PAH-MEL/APP)10');self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['TG_end_C'],r['TG_mass_mg']),('N2','10','700','20'));self.assertFalse(r.get('TG_start_C'));self.assertFalse(r.get('TG_flow_mL_min'));self.assertFalse(r.get('TG_pan'));self.reject(r,heating_rate_C_min='60');self.reject(r,atmosphere='air')
 def test_pet_cot_explicit_residue_unfixed_temp_raw_not_r700(self):
  r=self.exact(P,'(PAH-MEL/APP)10');self.assertEqual(r['source_reported_residue_pct'],'23.4');self.assertTrue(all(not r[k]for k in ['R700_pct','residue_pct','char_pct','residue_temp_C','char_temp_C']));self.reject(r,R700_pct='23.4',residue_pct='23.4',residue_temp_C='700')
 def test_pet_cot_control20point1_20point8_conflict_held_both_gases(self):
  rr=[r for r in self.source(P)if r['sample_state']=='Uncoated'];self.assertEqual(len(rr),2);self.assertTrue(all(r['source_Table1_LOI_pct']=='20.1'and r['source_abstract_LOI_pct']=='20.8'and not r['LOI_pct']and all(not r.get(k,'')for k in pairing.TG_FIELDS)for r in rr))
 def test_pet_cot_three_air_records_not_estimated_or_temp_assumed(self):
  rr=[r for r in self.source(P)if r['source_reported_atmosphere']=='air'];self.assertEqual(len(rr),3);self.assertTrue(all(r['pairing_status']!='verified_exact'and all(not r.get(k,'')for k in pairing.TG_FIELDS)for r in rr));self.assertEqual({r['source_reported_rough_residue_pct']for r in rr},{'3','7',''})
 def test_pet_cot_mixed_dip_not_same_treatment_as_lblyield(self):
  r=next(r for r in self.source(P)if r['sample_state']=='PAH/MEL/APP mixture dip');self.assertEqual((r['LOI_pct'],r['source_Table1_weightgain_pct']),('26.8','15.6'));self.assertTrue(all(not r.get(k,'')for k in pairing.TG_FIELDS));self.assertIn('noLbL',r['composition']);self.assertEqual(self.exact(P,'(PAH-MEL/APP)10')['source_Table1_weightgain_pct'],'9')
 def test_pet_cot_missing_recipe_and_loi_conditions_not_wafer_or_stock(self):
  r=self.exact(P,'(PAH-MEL/APP)10');self.assertTrue(all(not r.get(k)for k in ['LOI_standard','LOI_instrument','LOI_sample_dimensions_mm','LOI_repeats','source_MEL_bath_wt_pct']));self.assertIn('MELdoseunreported',r['treatment_method']);self.assertIn('fabricdurations/BPEIbaseuncertain',r['treatment_method']);self.assertIn('65percentPET/35percentcotton',r['material_form']);self.assertIn('154g/m2,0.23mm',r['material_form'])
if __name__=='__main__':unittest.main()
