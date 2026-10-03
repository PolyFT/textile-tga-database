"""Protect measured versus calculated LOI, native peak indexing and reused controls."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b150/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261004_b150_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing;import validate_tg_loi as v
A='10.1016/j.porgcoat.2016.10.035';B='10.1016/j.carbpol.2020.116173';C='10.1016/j.surfcoat.2006.10.027'
class TextileB150Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def row(self,d,s):return next(r for r in self.rows if r['DOI']==d and r['sample_state']==s)
 def reject(self,r,**changes):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**changes)))
 def test_eight_pairs_not_forty_facts(self):
  p=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(p['errors']);self.assertEqual((p['verified_exact_sample_states'],p['verified_exact_condition_records']),(8,8));self.assertEqual(len(self.rows),40)
 def test_32holds_excluded(self):
  x=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(x),32);self.assertTrue(all(pairing.evidence_issues(r)for r in x))
 def test_aip_version_year_and_single_DOI_retained(self):
  x=[r for r in self.rows if r['DOI']==A and r['pairing_status']=='verified_exact'];self.assertEqual(len(x),5);self.assertTrue(all(r['year']=='2017'and'ARTICLEINPRESS' in r['source_document_version']for r in x));self.assertTrue(all('localregistry' in r['publication_type_evidence']for r in x))
 def test_initial_loi_is_measured29_not_calculated26_or27(self):
  for s,n in[('COT-A initial','26'),('COT-B initial','27')]:
   r=self.row(A,s);self.assertEqual(r['LOI_pct'],'29');self.reject(r,LOI_pct=n)
 def test_five_model_lois_not_five_extra_measurements(self):
  x=[r for r in self.rows if r['DOI']==A and r['pairing_status']=='held_model_calculated_LOI_not_measurement'];self.assertEqual(len(x),5);self.assertTrue(all(not r['LOI_pct']and all(not r.get(k)for k in pairing.TG_FIELDS)for r in x))
 def test_native_tonset5_is_t5_not_undefined_onset(self):
  r=self.row(A,'COT-A initial');self.assertEqual(r['T5_C'],'255');self.assertFalse(r.get('Tonset_C'));self.reject(r,T5_C='',Tonset_C='255')
 def test_untreated_native_first_peak_dash_kept_missing(self):
  r=self.row(A,'UT initial');self.assertFalse(r['Tmax1_C']);self.assertEqual((r['Tmax2_C'],r['Tmax3_C']),('419','556'));self.reject(r,Tmax1_C='419',Tmax2_C='556',Tmax3_C='')
 def test_mea_first_peak_not_moisture(self):
  a=self.row(A,'COT-A initial');b=self.row(A,'COT-B initial');self.assertEqual((a['Tmax1_C'],b['Tmax1_C']),('293','287'));self.assertIn('MEAfirstpeakgone',a['source_peak_definition']);self.reject(a,Tmax1_C='100')
 def test_native_washed_peak_indices_changed_not_borrowed(self):
  a=self.row(A,'COT-A W one native wash');b=self.row(A,'COT-B W one native wash');self.assertEqual((a['Tmax1_C'],a['Tmax2_C'],b['Tmax1_C'],b['Tmax2_C']),('391','604','384','579'));self.assertFalse(a['Tmax3_C']or b['Tmax3_C']);self.reject(a,Tmax1_C='293')
 def test_peak_residue_attached_to_correct_native_index(self):
  a=self.row(A,'COT-A initial');b=self.row(A,'COT-A W one native wash');self.assertEqual((a['residue_at_Tmax2_pct'],a['source_native_peak_residue_temp_C']),('58.7','387'));self.assertEqual((b['residue_at_Tmax1_pct'],b['source_native_peak_residue_temp_C']),('54.6','391'));self.reject(a,residue_at_Tmax2_pct='',residue_at_Tmax1_pct='58.7')
 def test_750_residue_not_800_endpoint_or_mcc_yield(self):
  a=self.row(A,'COT-B initial');b=self.row(A,'COT-B W one native wash');self.assertEqual((a['R750_pct'],b['R750_pct'],a['TG_end_C']),('13.5','2.9','800'));self.assertFalse(a.get('R800_pct'));self.reject(a,R750_pct='',R800_pct='13.5',residue_temp_C='800');self.reject(b,R750_pct='22')
 def test_washed_loi_20_21_pairs_own_washed_tg(self):
  a=self.row(A,'COT-A W one native wash');b=self.row(A,'COT-B W one native wash');self.assertEqual((a['LOI_pct'],a['T5_C'],b['LOI_pct'],b['T5_C']),('20','340','21','309'));self.reject(a,washing_state='Initial0cycles');self.reject(a,LOI_pct='29')
 def test_washing_options_and_loi_repeats_unreported(self):
  r=self.row(A,'COT-A W one native wash');self.assertIn('temperature/time/detergent/standardoptionunreported',r['washing_state']);self.assertIn('MCC3repsnotborrowed',r['source_LOI_repeats']);self.assertEqual(r['source_LOI_dimensions'],'14x5.2cm')
 def test_air30_tg_not_nitrogen1Csecond_mcc(self):
  r=self.row(A,'COT-A initial');self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['source_TG_mass_mg'],r['source_TG_pan']),('air','30','5','Openplatinum'));self.reject(r,atmosphere='N2');self.reject(r,heating_rate_C_min='60')
 def test_unknown_residue_ranges_and_washed_control_held(self):
  x=[r for r in self.rows if r['DOI']==A and r['pairing_status']=='held_approximate_or_unmapped_residue_scope'];self.assertEqual(len(x),3);self.assertTrue(all(all(not r.get(k)for k in pairing.TG_FIELDS)for r in x));r=self.row(A,'UT washed column LOI without independent washedTG');self.assertEqual(r['LOI_pct'],'19');self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS))
 def test_chitosan_control_both_thresholds_and_whole_pair_held(self):
  r=self.row(B,'Control cotton');self.assertEqual((r['source_raw_T5_C'],r['source_raw_T10_C']),('298','295'));self.assertFalse(r['T5_C']or r['T10_C']);self.assertIn('ACS9b05523',r['source_control_reuse']);self.assertEqual(r['pairing_status'],'held_crosssource_control_and_threshold_conflict')
 def test_three_treated_cs_ap_profiles(self):
  x=[r for r in self.rows if r['DOI']==B and r['pairing_status']=='verified_exact'];self.assertEqual([(r['T5_C'],r['T10_C'],r['Tmax1_C'],r['R700_pct'],r['LOI_pct'])for r in x],[('262','295','363','13.8','21'),('198','229','272','33.3','29'),('209','236','278','34','27')]);self.reject(x[2],LOI_pct='29')
 def test_rmax_rate_not_residue_or_heating_rate(self):
  r=self.row(B,'CS/AP/cotton initial');self.assertEqual(r['source_Rmax_pct_per_C'],'16');self.assertIn('notresidue/heatingrate',r['source_Rmax_definition']);self.assertEqual(r['heating_rate_C_min'],'10');self.reject(r,R700_pct='16');self.reject(r,heating_rate_C_min='16')
 def test_cs_tgftir_own_conditions_not_other_protocol(self):
  r=self.row(B,'CS/AP/cotton initial');self.assertEqual((r['source_TG_flow_mL_min'],r['source_TG_repeats'],r['TG_start_C'],r['TG_end_C']),('50','2','40','700'));self.assertEqual(r['source_TG_mass_pan'],'Unreported');self.assertIn('TG-FTIR',r['source_TG_mode']);self.assertEqual(r['source_LOI_dimensions_mm'],'150x58')
 def test_unknown_cs_concentration_cycles_and_surface_composition(self):
  r=self.row(B,'CS/AP/cotton initial');self.assertEqual(r['source_CS_bath_concentration'],'Unreported');self.assertIn('precisecoatingcyclesunassigned',r['source_layer_count']);self.assertIn('notbulkfabriccomposition',r['source_EDX_definition']);self.assertIn('2imagesunviewedunused',r['supplement_review_status'])
 def test_entire_cf4_ac8_paper_no_own_tg_no_pairs(self):
  x=[r for r in self.rows if r['DOI']==C];self.assertEqual(len(x),22);self.assertTrue(all(r['pairing_status']!='verified_exact'for r in x));self.assertTrue(all(all(not r.get(k)for k in pairing.TG_FIELDS)for r in x));self.assertTrue(all('CannotborrowpreviousFRpaper' in r['limitations']for r in x))
 def test_copolymer120_loi_conflict_and_qualified_pressures(self):
  r=self.row(C,'Cotton120 DEAEPN-AC8 copolymer Table3');self.assertFalse(r['LOI_pct']);self.assertIn('27.5',r['source_raw_LOI']);self.assertIn('28conflict',r['source_raw_LOI']);self.assertIn('distinctqualifiers',r['source_plasma_pressure']);self.assertEqual(self.row(C,'Cotton210 DEAEPN-AC8 copolymer Table3')['LOI_pct'],'28')
if __name__=='__main__':unittest.main()
