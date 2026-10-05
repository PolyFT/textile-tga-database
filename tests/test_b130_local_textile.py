"""Protect material identity, water loss and explicit residue temperatures."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
H=Path(__file__).resolve().parent;PVT=H.name=='work';R=H.parent/'repo'if PVT else H.parent
F=H/'staged-local-textile-b130/publication_proposed.csv'if PVT else R/'data/incoming/verified_source_batch_20261002_b130_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing,validate_tg_loi as v
C='10.1007/s10570-018-1962-5';B='10.1007/s10570-020-03383-4'
class TextileB130Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def source(self,d):return[r for r in self.rows if r['DOI']==d]
 def exact(self,d,s):return next(r for r in self.source(d)if r['sample_state']==s and r['pairing_status']=='verified_exact')
 def reject(self,r,**kw):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**kw)))
 def test_six_states_not_eight_fact_rows(self):
  z=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(z['errors']);self.assertEqual((z['verified_exact_sample_states'],z['verified_exact_condition_records']),(6,6));self.assertEqual(len(self.rows),8)
 def test_air20_flow2_not_implied_n2_records(self):
  rr=[r for r in self.rows if r['pairing_status']=='verified_exact'];self.assertTrue(all((r['atmosphere'],r['heating_rate_C_min'],r['TGA_gas_flow_mL_min'])==('air','20','2')for r in rr));self.reject(rr[0],atmosphere='N2');self.reject(rr[0],heating_rate_C_min='10')
 def test_same_control_loi18_different_fabrics_not_interchangeable(self):
  a=self.exact(C,'Controlcotton');b=self.exact(B,'Controlcotton');self.assertEqual((a['LOI_pct'],b['LOI_pct']),('18','18'));self.assertNotEqual(a['material_form'],b['material_form']);self.assertIn('118g/m2',a['material_form']);self.assertIn('150g/m2',b['material_form']);self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(a,material_form_TGA=b['material_form_TGA'])))
 def test_carbonate_conflicting_letter_sets_join_material_words(self):
  r=self.exact(C,'NanoZnCO3plusNaOHcotton');self.assertEqual((r['source_Table1_fabric_code'],r['source_Fig3_thermal_curve'],r['source_method_solution_code']),('D','D','Bcombined'));r=self.exact(C,'NaOHonlycotton');self.assertEqual((r['source_Table1_fabric_code'],r['source_Fig3_thermal_curve']),('C','E'));self.assertEqual((r['LOI_pct'],r['R550_pct']),('25','30'))
 def test_carbonate_control_range_not_midpoint_or_zero_addon(self):
  r=self.exact(C,'Controlcotton');self.assertEqual((r['R400_pct'],r['residue_pct'],r['residue_temp_C']),('25','25','400'));self.assertFalse(r['R550_pct']);self.assertIn('no midpoint',r['source_Table2_R550_range_pct']);self.assertFalse(r.get('source_Table1_addon_pct'));self.reject(r,R550_pct='1.5',residue_pct='1.5',residue_temp_C='550')
 def test_carbonate_r400_r550_not_raw_r450(self):
  r=self.exact(C,'NanoZnCO3plusNaOHcotton');self.assertEqual((r['R400_pct'],r['source_Table2_R450_pct'],r['R550_pct'],r['residue_temp_C']),('48','44','42','550'));self.reject(r,R550_pct='44',residue_pct='44')
 def test_carbonate_three_major_peak_conflicts_not_chosen(self):
  for label in ['Controlcotton','NeutralnanoZnCO3cotton','NaOHonlycotton']:
   r=self.exact(C,label);self.assertFalse(r['Tmax1_C']);self.assertIn('canonicalTmaxblank',r['source_peak_conflict']);self.assertFalse(r['Tonset_C']);self.assertFalse(r['T5_C'])
 def test_combined_dtg280_not_dsc_water80_or_exotherm250(self):
  r=self.exact(C,'NanoZnCO3plusNaOHcotton');self.assertEqual(r['Tmax1_C'],'280');self.assertIn('DTG',r['source_major_peak_definition']);self.reject(r,Tmax1_C='80');self.reject(r,Tmax1_C='250')
 def test_carbonate_abstract_greater40at600_not_r60042(self):
  r=self.exact(C,'NanoZnCO3plusNaOHcotton');self.assertFalse(r['R600_pct']);self.assertEqual(r['residue_temp_C'],'550');self.assertIn('notfixednumericR60042',r['source_abstract_R600_qualifier']);self.reject(r,R600_pct='42',residue_temp_C='600')
 def test_carbonate_bath4w_v_not_measured_dry_addon9(self):
  r=self.exact(C,'NanoZnCO3plusNaOHcotton');self.assertEqual(r['source_Table1_addon_pct'],'9');self.assertIn('4percentw/v',r['treatment_method']);self.assertIn('untreateddenominator',r['source_addon_definition']);self.assertFalse(r.get('additive_loading_wt_pct'))
 def test_fabric_method_limits_not_powder50to900_or700(self):
  for r in self.rows:
   if r['pairing_status']=='verified_exact':self.assertFalse(r.get('TG_start_C'));self.assertFalse(r.get('TG_end_C'));self.assertFalse(r.get('TG_mass_mg'))
 def test_borate_t5_t10_t50_not_onset_mainpeak(self):
  for s,values in [('Controlcotton',('310','370','380')),('Zincborate12percentaddoncotton',('280','310','410'))]:
   r=self.exact(B,s);self.assertEqual((r['T5_C'],r['T10_C'],r['source_Table1_T50_C']),values);self.assertFalse(r['Tonset_C']);self.assertFalse(r['Tmax1_C']);self.assertIn('canonicalTonset/Tmax1blank',r['source_peak_identity_conflict']);self.reject(r,T5_C=r['source_Table1_main_peak_C'])
 def test_borate_t5_includes_water_and_powder100not_fabric280(self):
  r=self.exact(B,'Zincborate12percentaddoncotton');self.assertIn('includingdehydration',r['pairing_evidence']);self.assertEqual(r['T5_C'],'280');p=next(x for x in self.source(B)if x['material_category']=='pureflameretardantreference');self.assertEqual(p['source_Table1_T5_C'],'100');self.assertFalse(p['T5_C']);self.reject(r,T5_C='100')
 def test_borate_r50045_not_edx12point68_or_highertemp1point5(self):
  r=self.exact(B,'Zincborate12percentaddoncotton');c=self.exact(B,'Controlcotton');self.assertEqual((r['R500_pct'],c['R500_pct'],r['residue_temp_C']),('45','6','500'));self.assertIn('notpurecarbon',r['source_residue_definition']);self.assertIn('rawqualifier',r['source_conclusion_residue_qualifier']);self.reject(r,R500_pct='12.68',residue_pct='12.68');self.reject(c,R500_pct='1.5',residue_pct='1.5')
 def test_borate_only12addon_route_uncertainty_and_dimensions(self):
  r=self.exact(B,'Zincborate12percentaddoncotton');self.assertEqual((r['source_native_addon_pct'],r['LOI_sample_dimensions_mm']),('12','100x40'));self.assertIn('denominatorunreported',r['source_addon_status']);self.assertIn('diptemperatureunreported',r['treatment_method']);self.assertIn('uncertaintyretained',r['treatment_method']);self.assertFalse(r.get('additive_loading_wt_pct'));self.assertEqual(sum(x['pairing_status']=='verified_exact'for x in self.source(B)),2)
 def test_pure_powders_no_textile_loi_water_t50_not_numeric(self):
  rr=[r for r in self.rows if r['material_category']=='pureflameretardantreference'];self.assertEqual(len(rr),2);self.assertTrue(all(not r.get('LOI_pct')and not r['material_form_LOI']and all(not r.get(k,'')for k in pairing.TG_FIELDS)for r in rr));p=next(r for r in rr if r['DOI']==B);self.assertIn('notnumericT50',p['source_Table1_T50_wording']);self.assertEqual(p['source_Table1_R500_pct'],'78')
if __name__=='__main__':unittest.main()
