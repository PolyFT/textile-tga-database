"""Protect sample lineage, native thresholds and quantities from other tests."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
H=Path(__file__).resolve().parent;P=H.name=='work';R=H.parent/'repo'if P else H.parent
F=H/'staged-local-textile-b122/publication_proposed.csv'if P else R/'data/incoming/verified_source_batch_20261002_b122_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing,validate_tg_loi as v
A='10.1007/s10570-018-2193-5';PVD='10.1007/s13726-017-0595-0';PET='10.1007/s12221-011-0166-5';C='10.1016/j.porgcoat.2019.05.010'
class TextileB122Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def row(self,doi,state,gas=None):return next(r for r in self.rows if r['DOI']==doi and r['sample_state']==state and(gas is None or r['atmosphere']==gas))
 def rejected(self,r,**changes):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**changes)))
 def test_independent_states_differ_from_condition_records(self):
  q=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(q['errors']);self.assertEqual((q['verified_exact_sample_states'],q['verified_exact_condition_records']),(4,7));self.assertEqual(len(self.rows),44)
 def test_asxpea_air_onset_not_t5_t10_or_water_loss(self):
  r=self.row(A,'ASXPEA7 cotton','air');self.assertEqual(r['Tonset_C'],'240');self.assertFalse(r['T5_C']);self.assertFalse(r['T10_C']);self.assertFalse(r['Tmax1_C']);self.rejected(r,Tonset_C='',T5_C='240');self.rejected(r,Tonset_C='100')
 def test_asxpea_nitrogen_range_endpoints_not_temps(self):
  r=self.row(A,'ASXPEA7 cotton','N2');self.assertEqual(r['source_N2_main_loss_temperature_range_C'],'240-306');self.assertFalse(r['Tonset_C']);self.assertFalse(r['Tmax1_C']);self.rejected(r,Tonset_C='240',Tmax1_C='306')
 def test_asxpea_fixed_residue_is700_not800_endpoint(self):
  r=self.row(A,'ASXPEA7 cotton','N2');self.assertEqual((r['char_pct'],r['char_temp_C'],r['TG_end_C']),('38.7','700','800'));self.rejected(r,char_temp_C='800',residue_temp_C='800')
 def test_asxpea_air_stage_loss_not_air_residue_or_nitrogen_swap(self):
  r=self.row(A,'ASXPEA7 cotton','air');self.assertEqual((r['source_air_firststage_mass_loss_pct'],r['char_pct']),('38.7','15.3'));self.rejected(r,char_pct='38.7',residue_pct='38.7')
 def test_asxpea_control_near_zero_char_not_exact_zero(self):
  r=self.row(A,'Control cotton','air');self.assertFalse(r['char_pct']);self.assertFalse(r['char_temp_C']);self.assertEqual(r['Tmax1_C'],'346');self.rejected(r,char_pct='0',residue_pct='0',char_temp_C='700')
 def test_asxpea_tgir_mass_and_endpoint_not_main_tg(self):
  r=self.row(A,'ASXPEA7 cotton','N2');self.assertEqual((r['source_TGIR_mass_mg'],r['source_TGIR_range_C'],r['TG_end_C']),('8','40-600','800'));self.assertFalse(r.get('source_TG_mass_mg'))
 def test_asxpea_other_doses_and_all_washed_loi_have_no_tg(self):
  rr=[r for r in self.rows if r['DOI']==A and r['pairing_status']!='verified_exact'];self.assertEqual(len(rr),18);self.assertEqual(sum(bool(r['source_native_LC'])for r in rr),15);self.assertTrue(all(all(not r.get(k)for k in pairing.TG_FIELDS)for r in rr));self.assertTrue(all(r['source_ASXPEA_bath_native_pct']=='7'for r in self.rows if r['DOI']==A and r['pairing_status']=='verified_exact'and r['sample_state']!='Control cotton'))
 def test_asxpea_own_control_loi_not_cited18(self):
  r=self.row(A,'Control cotton','N2');self.assertEqual(r['LOI_pct'],'17.6');self.rejected(r,LOI_pct='18');t=self.row(A,'ASXPEA7 cotton','N2');self.assertEqual((t['source_ASXPEA_bath_native_pct'],t['source_ASXPEA_bath_Table1_g_L']),('7','70'));self.assertIn('notdefined',t['source_ASXPEA_percent_basis'])
 def test_pvdf_serial_draw_speeds_are_one_state(self):
  rr=[r for r in self.rows if r['DOI']==PVD];self.assertEqual(len(rr),1);self.assertEqual(rr[0]['source_drawing_stages_m_min'],'2.6/3.5/4.8serialnotindependentgroups')
 def test_pvdf_dtg_peak_not_dsc_melting(self):
  r=self.row(PVD,'PVDF porous fiber');self.assertEqual((r['Tonset_C'],r['Tmax1_C'],r['source_DSC_Tm_C']),('463.8','478.86','158.8'));self.assertFalse(r['T5_C']);self.rejected(r,Tmax1_C='158.8')
 def test_pvdf_curve_only_char_stays_blank(self):
  r=self.row(PVD,'PVDF porous fiber');self.assertTrue(all(not r.get(k)for k in ['char_pct','residue_pct','char_temp_C','residue_temp_C']));self.rejected(r,char_pct='24',residue_pct='24',char_temp_C='800',residue_temp_C='800')
 def test_pvdf_loi_fiber_mat_not_cone_specimen(self):
  r=self.row(PVD,'PVDF porous fiber');self.assertEqual((r['source_LOI_sample_mass_g'],r['source_LOI_dimensions_mm']),('10','100x40x2'));self.assertIn('fibers',r['material_form_LOI']);self.assertEqual(r['material_form_LOI'],r['material_form_TGA'])
 def test_pvdf_nitrogen_tg_range_not_dsc_or_air(self):
  r=self.row(PVD,'PVDF porous fiber');self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['TG_start_C'],r['TG_end_C'],r['source_DSC_range_C']),('N2','10','25','800','50-350'));self.rejected(r,atmosphere='air')
 def test_pet_textile_loi_does_not_borrow_bulk_tg(self):
  rr=[r for r in self.rows if r['DOI']==PET];self.assertEqual({r['LOI_pct']for r in rr},{'22','29','31'});self.assertEqual(len(rr),3);self.assertTrue(all(all(not r.get(k)for k in pairing.TG_FIELDS)for r in rr));self.assertTrue(all(r['pairing_status']=='held_fiber_LOI_no_own_fiber_TG'for r in rr))
 def test_pet_fiber_loading_and_dimensions_not_plastic(self):
  r=self.row(PET,'PET-ZnPCD');self.assertIn('0.5wtpercent',r['composition']);self.assertIn('not20wtpercent',r['composition']);self.assertFalse(r.get('source_LOI_dimensions_mm'));self.assertIn('noLOIfiberdimensionsreported',r['material_form_LOI'])
 def test_chapp_reused_labels_require_alkali_lineage(self):
  rr=[r for r in self.rows if r['DOI']==C and r['pairing_status']!='verified_exact'];self.assertEqual(len(rr),16);self.assertEqual(sum(r['pairing_status']=='held_TG_alkali_lineage_unresolved'for r in rr),8);self.assertTrue(all(all(not r.get(k)for k in pairing.TG_FIELDS)for r in rr));a=self.row(C,'PET-20BL-NaOH');b=self.row(C,'PET-20BL-noNaOH');self.assertEqual(a['native_sample_label'],b['native_sample_label']);self.assertEqual((a['LOI_pct'],b['LOI_pct']),('26.5','26.2'));self.assertNotEqual(a['source_addon_pct'],b['source_addon_pct'])
 def test_chapp_native_onset_t10_not_t5_or_generic_onset(self):
  r=self.row(C,'Uncoated PET','N2');self.assertEqual((r['T10_C'],r['Tmax1_C']),('402','436'));self.assertFalse(r['Tonset_C']);self.assertFalse(r['T5_C']);self.rejected(r,T10_C='',Tonset_C='402')
 def test_chapp_gas_specific_r600_not_endpoint650(self):
  n=self.row(C,'Uncoated PET','N2');a=self.row(C,'Uncoated PET','air');self.assertEqual((n['char_pct'],a['char_pct'],a['Tmax2_C']),('5.09','0.42','564'));self.assertEqual(n['char_temp_C'],'600');self.assertEqual(n['TG_end_C'],'650');self.rejected(n,char_temp_C='650',residue_temp_C='650');self.rejected(a,char_pct='5.09',residue_pct='5.09')
 def test_all_held_facts_remain_outside_verified_target(self):
  rr=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(rr),37);self.assertTrue(all(r['review_disposition']=='held_outside_verified_target'and all(not r.get(k)for k in pairing.TG_FIELDS)for r in rr))
if __name__=='__main__':unittest.main()
