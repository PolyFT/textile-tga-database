"""Protect source-specific textile state, method and metric correspondence."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b153/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261004_b153_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing;import validate_tg_loi as v
A='10.1007/s10570-022-04693-5';B='10.1007/s10570-021-04191-0'
class TextileB153Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def row(self,doi,label):return next(r for r in self.rows if r['DOI']==doi and r['sample_state']==label)
 def reject(self,r,**changes):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**changes)))
 def test_five_states_conditions_not27facts(self):
  p=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(p['errors']);self.assertEqual((p['verified_exact_sample_states'],p['verified_exact_condition_records']),(5,5));self.assertEqual(len(self.rows),27)
 def test_22_staged_holds_excluded(self):
  rs=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(rs),22);self.assertTrue(all(pairing.evidence_issues(r)for r in rs))
 def test_nyco_three_native_initial_profiles(self):
  rs=[r for r in self.rows if r['DOI']==A and r['pairing_status']=='verified_exact'];self.assertEqual([(r['LOI_pct'],r['T5_C'],r['Tmax1_C'],r['R800_pct'])for r in rs],[('18.5','','','9.9'),('26.3','267','324','30.9'),('29.8','278','329','39.1')])
 def test_control_missing_t5_tmax_not_filled(self):
  r=self.row(A,'NYCO13/87 initial control fabric');self.assertFalse(r['T5_C']);self.assertFalse(r['Tmax1_C']);self.reject(r,Tmax1_C='329')
 def test_cone_char_not_tg_char(self):
  r=self.row(A,'G-PEI/PA-NYCO13/87 initial fabric');self.assertEqual(r['R800_pct'],'39.1');self.reject(r,R800_pct='38.3')
 def test_nyco_t5_not_undefined_onset(self):
  r=self.row(A,'PEI/PA-NYCO13/87 initial fabric');self.assertFalse(r.get('Tonset_C'));self.reject(r,T5_C='',Tonset_C='267')
 def test_waterloss_before120_not_decomposition_peak(self):
  r=self.row(A,'G-PEI/PA-NYCO13/87 initial fabric');self.assertEqual(r['Tmax1_C'],'329');self.reject(r,Tmax1_C='120')
 def test_nyco_native_nitrogen10_not_microwave20(self):
  r=self.row(A,'PEI/PA-NYCO13/87 initial fabric');self.assertEqual((r['atmosphere'],r['heating_rate_C_min']),('N2','10'));self.reject(r,atmosphere='air');self.reject(r,heating_rate_C_min='20')
 def test_initial_loi_repeats_not_laundry_repeats(self):
  r=self.row(A,'PEI/PA-NYCO13/87 initial fabric');self.assertEqual((r['source_LOI_initial_repeats'],r['source_washed_LOI_repeats'],r['source_LOI_dimensions_mm']),('5','3','150x58'))
 def test_unknown_gptms_concentration_not_invented(self):
  r=self.row(A,'G-PEI/PA-NYCO13/87 initial fabric');self.assertIn('GPTMSconcentrationunreported',r['treatment_method']);self.assertIn('weightgain19.8wt',r['composition']);self.assertIn('PEI2wt/PA4wt',r['composition'])
 def test_no_gptms_comparator_remains_distinct(self):
  r=self.row(A,'PEI/PA-NYCO13/87 initial fabric');self.assertIn('NoGPTMS',r['treatment_method']);self.reject(r,sample_state='G-PEI/PA-NYCO13/87 initial fabric')
 def test_five_laundry_lois_no_native_tg(self):
  rs=[r for r in self.rows if r['DOI']==A and 'after' in r['sample_state']];self.assertEqual([r['LOI_pct']for r in rs],['29','28','26.7','25.8','24.3']);self.assertTrue(all(not r.get(k)for r in rs for k in pairing.TG_FIELDS));self.assertTrue(all('not5labcycles'in r['washing_state']for r in rs))
 def test_six_other_blends_with_uncertainty_no_tg(self):
  rs=[r for r in self.rows if r['DOI']==A and 'other_blend'in r['pairing_status']];self.assertEqual([r['LOI_pct']for r in rs],['18.7','29','19.2','26','19.8','27.8']);self.assertTrue(all(r['LOI_uncertainty_pct']=='0.1'for r in rs));self.assertTrue(all(not r.get(k)for r in rs for k in pairing.TG_FIELDS))
 def test_washed_value_cannot_replace_initial_value(self):
  r=self.row(A,'G-PEI/PA-NYCO13/87 initial fabric');self.reject(r,LOI_pct='25.8');self.reject(r,washing_state='20launderingcycles')
 def test_two_microwave_source_profiles(self):
  rs=[r for r in self.rows if r['DOI']==B and r['pairing_status']=='verified_exact'];self.assertEqual([(r['LOI_pct'],r['T5_C'],r['Tmax1_C'],r['R600_pct'])for r in rs],[('31','202','279','37.5'),('30.5','223','284','34.3')])
 def test_p3_t4_one_state_one_condition(self):
  rs=[r for r in self.rows if r.get('source_aliases')=='P3;T4;MTC'];self.assertEqual(len(rs),1);self.assertEqual(rs[0]['sample_state'],'MTC initial600Wtotal4min cotton fabric P3=T4');self.assertFalse(any(r['sample_state']in ['P3 initial microwave-treated cotton fabric','T4 initial microwave-treated cotton fabric']for r in self.rows))
 def test_total_four_minutes_not_each_face(self):
  r=self.row(B,'MTC initial600Wtotal4min cotton fabric P3=T4');self.assertIn('total4min',r['treatment_method']);self.assertIn('not4mineachface',r['treatment_method'])
 def test_pa_stock_volume_not_inferred_mass_fraction(self):
  r=self.row(B,'MTC initial600Wtotal4min cotton fabric P3=T4');self.assertIn('50wt%aqueousPAstock2mL',r['source_bath_recipe']);self.assertIn('notconvertvolumeintomass',r['source_bath_recipe'])
 def test_microwave_room_temperature_start_not_exact25(self):
  r=self.row(B,'CTC initial155C45min cotton fabric');self.assertFalse(r.get('TG_start_C'));self.assertIn('noexact25Cinferred',r['source_TG_start']);self.assertEqual(r['TG_end_C'],'600')
 def test_mcc_one_c_per_second_not_tga_ramp(self):
  r=self.row(B,'CTC initial155C45min cotton fabric');self.assertEqual(r['heating_rate_C_min'],'20');self.reject(r,heating_rate_C_min='60')
 def test_ten_tg_only_groups_no_other_loi_borrowed(self):
  rs=[r for r in self.rows if r['DOI']==B and 'TG_without_own_group_LOI'in r['pairing_status']];self.assertEqual(len(rs),10);self.assertTrue(all(not r.get('LOI_pct')for r in rs));r=self.row(B,'T3 initial microwave-treated cotton fabric');self.assertEqual(r['source_group_condition'],'600W/total3min');self.assertEqual((r['T5_C'],r['Tmax1_C'],r['R600_pct']),('238','290','37.5'))
 def test_unproven_control_forged_approval_rejected(self):
  r=dict(self.row(B,'Control TG/pristine LOI processing unresolved'),pairing_status='verified_exact');r['reviewed_measurement_fingerprint']=pairing.measurement_fingerprint(r);self.assertIn('specimen_form_mismatch',pairing.evidence_issues(r));self.assertIn('stateunproven',r['source_control_conflict'])
 def test_ctc_and_mtc_not_cross_assigned(self):
  r=self.row(B,'CTC initial155C45min cotton fabric');self.reject(r,LOI_pct='30.5');self.reject(r,R600_pct='34.3');self.assertIn('9wt',r['treatment_method']);self.assertNotIn('9wt',self.row(B,'MTC initial600Wtotal4min cotton fabric P3=T4')['treatment_method'])
 def test_native_tg_mass_flow_different_between_papers(self):
  a=self.row(A,'PEI/PA-NYCO13/87 initial fabric');b=self.row(B,'CTC initial155C45min cotton fabric');self.assertEqual((a['source_TG_mass_mg'],a['source_TG_flow_pan']),('3-5','Unreported'));self.assertEqual((b['source_TG_mass_mg'],b['source_TG_flow_mL_min']),('Approximately5','30'))
 def test_nyco_weave_type_remains_unreported(self):
  rs=[r for r in self.rows if r['DOI']==A];self.assertTrue(all('woven'not in r['material_form']for r in rs));self.assertTrue(all('weaveunreported'in r['material_form']for r in rs));self.assertTrue(all('150g/m2'in r['material_form']for r in rs if r['pairing_status']=='verified_exact'))
 def test_material_form_change_rejected(self):
  r=self.row(A,'PEI/PA-NYCO13/87 initial fabric');self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='Remolded nylon-cotton polymer sheet')))
 def test_all_accepted_metrics_are_explicit_native_text(self):
  rs=[r for r in self.rows if r['pairing_status']=='verified_exact'];self.assertTrue(all(r['numeric_evidence_type']=='explicit_text'for r in rs));self.assertTrue(all('primarytablepagesunread'in r['source_document_version']for r in rs));self.assertTrue(all('noimages'in r['supplement_review_status']for r in rs))
if __name__=='__main__':unittest.main()
