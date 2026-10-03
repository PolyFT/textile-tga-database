"""Protect molded-fiber identity, source conflicts and char/decomposition semantics."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b137/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261003_b137_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing,validate_tg_loi as v
A='10.1002/pi.2715';B='10.1016/j.carbpol.2013.06.014';C='10.1002/pc.26685'
class TextileB137Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def source(self,d):return[r for r in self.rows if r['DOI']==d]
 def exact(self,d,s):return next(r for r in self.source(d)if r['sample_state']==s and r['pairing_status']=='verified_exact')
 def reject(self,r,**kw):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**kw)))
 def test_fifteenstates_fifteenconditions_not_seventeenfacts(self):
  z=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(z['errors']);self.assertEqual((z['verified_exact_sample_states'],z['verified_exact_condition_records']),(15,15));self.assertEqual(len(self.rows),17)
 def test_twoholds_no_canonical_tg(self):
  rr=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(rr),2);self.assertTrue(all(all(not r[k]for k in pairing.TG_FIELDS)for r in rr))
 def test_pi_three_molded_samples_not_raw_fibers(self):
  rr=[r for r in self.source(A)if r['pairing_status']=='verified_exact'];self.assertEqual(len(rr),3);self.assertTrue(all('Hot-pressed'in r['material_form']for r in rr));self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(self.exact(A,'FPLA-NF'),material_form_TGA='Raw ramie fiber')))
 def test_pi_content_conflict_not_chosen(self):
  r=next(r for r in self.source(A)if r['sample_state']=='PLA-FNF');self.assertIn('unresolved',r['pairing_status']);self.assertIn('5.3',r['composition']);self.assertIn('4.5',r['composition']);self.assertEqual((r['LOI_pct'],r['source_raw_R400_pct']),('25','13.31'));self.assertFalse(r['R400_pct'])
 def test_pi_char400_not700(self):
  r=self.exact(A,'FPLA-FNF');self.assertEqual((r['R400_pct'],r['residue_temp_C'],r['TG_end_C']),('21.9','400','700'));self.assertFalse(r['R700_pct']);self.reject(r,residue_temp_C='700')
 def test_pi_air20_not_n2_or10(self):
  r=self.exact(A,'FPLA-NF');self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['source_TG_flow_mL_min']),('air','20','80'));self.reject(r,atmosphere='N2');self.reject(r,heating_rate_C_min='10')
 def test_pi_water_interval_not_decomposition_peak(self):
  r=self.exact(A,'PLA-NF');self.assertEqual(r['source_initial_water_loss_interval_C'],'50-150;notDTGpeak');self.assertFalse(r['Tmax1_C']);self.reject(r,Tmax1_C='150')
 def test_pi_compositions_total_app_not_swapped(self):
  r=self.exact(A,'FPLA-FNF');self.assertIn('APPmatrix5.2',r['composition']);self.assertIn('APPfiber5.3',r['composition']);self.assertEqual(r['LOI_pct'],'35.6');self.reject(r,LOI_pct='28.1')
 def test_pi_volume_year_not_online_year(self):
  self.assertTrue(all(r['year']=='2010'for r in self.source(A)))
 def test_boron_two_initial_cotton_samples(self):
  rr=[r for r in self.source(B)if r['pairing_status']=='verified_exact'];self.assertEqual(len(rr),2);self.assertEqual({r['LOI_pct']for r in rr},{'17.5','27.5'});self.assertTrue(all('Initial0durabilitycycles'in r['washing_state']for r in rr))
 def test_boron_r600_not_element_composition(self):
  r=self.exact(B,'TriHTACBoronCotton');self.assertEqual((r['R600_pct'],r['residue_temp_C']),('40.45','600'));self.reject(r,R600_pct='0.733',residue_pct='0.733')
 def test_boron_dehydration_not_tmax_or_onset(self):
  r=self.exact(B,'TriHTACBoronCotton');self.assertIn('boricacidwaterdehydration',r['source_raw_initial_rapid_loss_C']);self.assertFalse(r['Tonset_C']);self.assertFalse(r['Tmax1_C']);self.reject(r,Tmax1_C='270')
 def test_boron_control309_is_raw_only(self):
  r=self.exact(B,'ControlCotton');self.assertEqual((r['source_raw_initial_rapid_loss_C'],r['R600_pct']),('309','6.3'));self.assertFalse(r['T5_C']);self.assertFalse(r['Tonset_C']);self.reject(r,T5_C='309')
 def test_boron_trihtac_only_no_tg(self):
  r=next(r for r in self.source(B)if r['sample_state']=='TriHTACOnlyCotton');self.assertEqual(r['LOI_pct'],'22');self.assertIn('without_own_TG',r['pairing_status']);self.assertFalse(r['R600_pct'])
 def test_pc_ten_table_matched_formulations(self):
  rr=self.source(C);self.assertEqual(len(rr),10);self.assertTrue(all(r['pairing_status']=='verified_exact'and r['atmosphere']=='N2'for r in rr));self.assertEqual({r['LOI_pct']for r in rr},{'19.8','32.4','35.2','34.4','32.9','27.3','31.9','31.6','31.4','30.1'})
 def test_pc_table_one_fixed_fiber_tgic_content(self):
  self.assertTrue(all(r['source_RF_wt_pct']=='20'and r['source_TGIC_wt_pct']=='0.6'for r in self.source(C)));r=self.exact(C,'RRP/2AMS');self.assertEqual((r['source_AlPi_wt_pct'],r['source_MCA_wt_pct'],r['source_SiO2_wt_pct']),('15','7.5','7.5'));self.assertEqual(r['source_PLA_wt_pct'],'49.4')
 def test_pc_t5_and_three_decomposition_peaks(self):
  r=self.exact(C,'RRP/3A');self.assertEqual((r['T5_C'],r['Tmax1_C'],r['Tmax2_C'],r['Tmax3_C']),('259.3','317','381.5','485'));self.assertFalse(r['Tonset_C']);self.reject(r,T5_C='',Tonset_C='259.3')
 def test_pc_missing_third_peak_not_zero(self):
  r=self.exact(C,'RRP/3M');self.assertEqual((r['Tmax1_C'],r['Tmax2_C']),('367.7','409.9'));self.assertFalse(r['Tmax3_C']);self.reject(r,Tmax3_C='0')
 def test_pc_char_temperature_and_conflict_preserved(self):
  r=self.exact(C,'RRP');self.assertEqual((r['R600_pct'],r['residue_temp_C']),('11.4','600'));rr=[r for r in self.source(C)if r['sample_state']!='RRP'];self.assertTrue(all(not r['R600_pct']and not r['residue_temp_C']and r['source_raw_Table2_char_pct']for r in rr));a=self.exact(C,'RRP/3A');self.assertIn('22.8',a['source_raw_char_prose_conflict']);self.reject(a,R600_pct='23',residue_pct='23',residue_temp_C='600')
 def test_pc_native_loi_standard_and_dimensions(self):
  r=self.exact(C,'RRP/AMS');self.assertEqual(r['LOI_standard'],'GB/T2046-2009;nativecode');self.assertEqual(r['source_LOI_dimensions_mm'],'80x10x4');self.assertIn('UL94fiverepeatsnotborrowed',r['source_LOI_repeats']);self.assertEqual((r['TG_start_C'],r['TG_end_C'],r['heating_rate_C_min']),('30','600','10'));self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_LOI='Woven ramie fabric')))
if __name__=='__main__':unittest.main()
