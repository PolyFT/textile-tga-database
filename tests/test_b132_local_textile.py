"""Prevent cross-dose, cross-form, washing and thermal-definition substitutions."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b132/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261002_b132_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing,validate_tg_loi as v
H='10.1007/s12221-019-8914-z';D='10.1007/s10570-019-02503-z';E='10.1002/marc.202400536'
class TextileB132Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def source(self,d):return[r for r in self.rows if r['DOI']==d]
 def exact(self,d,s):return next(r for r in self.source(d)if r['sample_state']==s and r['pairing_status']=='verified_exact')
 def reject(self,r,**kw):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**kw)))
 def test_four_verified_states_and_conditions_not24facts(self):
  z=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(z['errors']);self.assertEqual((z['verified_exact_sample_states'],z['verified_exact_condition_records']),(4,4));self.assertEqual(len(self.rows),24)
 def test_all20_held_facts_excluded_and_without_chosen_tg_fields(self):
  rr=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(rr),20);self.assertTrue(all(all(not r[k]for k in pairing.TG_FIELDS)for r in rr))
 def test_only7bilayer_matches_its_tg_other2and4_held(self):
  rr=self.source(H);self.assertEqual(len(rr),4);self.assertEqual({r['source_bilayers']for r in rr if r['pairing_status']=='verified_exact'},{'0','7'});r=self.exact(H,'CottonSiO2PEIPA7bilayers');self.reject(r,LOI_pct='26');self.reject(r,LOI_pct='29.1')
 def test_native372_and_prose375_control_conflict_no_chosen_tmax(self):
  r=self.exact(H,'Cottoncontrol');self.assertEqual((r['source_printed_DTG_peak_C'],r['source_main_decomposition_peak_prose_C']),('372','375'));self.assertFalse(r['Tmax1_C']);self.reject(r,Tmax1_C='372');self.reject(r,Tmax1_C='375')
 def test_treated323_consistent_own_dtg(self):
  r=self.exact(H,'CottonSiO2PEIPA7bilayers');self.assertEqual(r['Tmax1_C'],'323');self.reject(r,Tmax1_C='372')
 def test_generic_onset_not_t5_t10(self):
  r=self.exact(H,'Cottoncontrol');self.assertEqual(r['Tonset_C'],'310');self.assertFalse(r['T5_C']);self.assertFalse(r['T10_C']);self.reject(r,Tonset_C='',T5_C='310')
 def test_r600_not_edx_carbon_or_other_temperature(self):
  r=self.exact(H,'CottonSiO2PEIPA7bilayers');self.assertEqual((r['R600_pct'],r['residue_pct'],r['residue_temp_C']),('40.7','40.7','600'));self.reject(r,residue_pct='52.95');self.reject(r,residue_temp_C='700')
 def test_explicit_n2_method_not_conclusion_oxidation_wording(self):
  r=self.exact(H,'Cottoncontrol');self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['TG_start_C'],r['TG_end_C']),('N2','10','40','600'));self.reject(r,atmosphere='air');self.assertIn('Unreported',r['source_TG_instrument_flow_pan'])
 def test_unresolved_bath_wording_not_guessed1and2percent(self):
  r=self.exact(H,'CottonSiO2PEIPA7bilayers');self.assertIn('One hundred percent',r['source_bath_concentration_wording']);self.assertIn('unresolved',r['source_bath_concentration_wording']);self.assertEqual(r['source_addon_pct'],'27.7');self.assertIn('denominator unreported',r['source_addon_definition']);self.assertFalse(r.get('additive_loading_wt_pct'))
 def test_ndopa_only_control10percent_not_other_doses(self):
  r=self.exact(D,'CottonNDOPA10percent');self.assertEqual(r['LOI_pct'],'21');self.reject(r,LOI_pct='19.8');self.reject(r,LOI_pct='20.5');self.assertEqual(len([r for r in self.source(D)if 'other_dose'in r['pairing_status']]),2)
 def test_ndopa_t5_defined_5percent_not_generic_onset(self):
  c=self.exact(D,'Cottoncontrol');r=self.exact(D,'CottonNDOPA10percent');self.assertEqual((c['T5_C'],r['T5_C']),('281','239.4'));self.assertFalse(r['Tonset_C']);self.assertFalse(r['Tmax1_C']);self.reject(r,T5_C='',Tonset_C='239.4')
 def test_ndopa_r700_not_method800_or_dtg_range(self):
  r=self.exact(D,'CottonNDOPA10percent');self.assertEqual((r['R700_pct'],r['residue_temp_C'],r['TG_end_C']),('20.9','700','800'));self.assertFalse(r['R800_pct']);self.reject(r,R700_pct='',R800_pct='20.9',residue_temp_C='800');self.assertEqual(r['source_main_massloss_temperature_range_C'],'288.1-349.3')
 def test_ndopa_two_air_records_held_without_borrowed_rate(self):
  rr=[r for r in self.source(D)if r['atmosphere']=='air'];self.assertEqual(len(rr),2);self.assertTrue(all('missing_explicit_heating_rate'in r['pairing_status']and not r['heating_rate_C_min']for r in rr));self.assertEqual({r['source_raw_AIR_residue_temp_C']for r in rr},{'550','700'})
 def test_ndopa_air173_not_defined_t5(self):
  r=next(r for r in self.source(D)if r['atmosphere']=='air'and r['sample_state']=='CottonNDOPA10percent');self.assertEqual(r['source_raw_AIR_generic_initial_C'],'173');self.assertFalse(r['T5_C']);self.assertEqual(r['source_raw_AIR_residue_pct'],'5.4')
 def test_ndopa_washed19_19point6_20point1_not_initial_tg(self):
  rr=[r for r in self.source(D)if r['source_native_LCs']];self.assertEqual(len(rr),3);self.assertEqual({r['LOI_pct']for r in rr},{'19','19.6','20.1'});self.assertTrue(all(r['pairing_status']!='verified_exact'and not r['material_form_TGA']for r in rr));r=self.exact(D,'CottonNDOPA10percent');self.reject(r,washing_state=rr[0]['washing_state'])
 def test_ndopa_wash_equivalence_not_assumed5domestic(self):
  rr=[r for r in self.source(D)if r['source_native_LCs']];self.assertTrue(all(r['source_native_LCs']=='30'and 'equivalence unreported'in r['source_wash_method']for r in rr))
 def test_eapp_all10_fabric_lois_no_neat_tg_pair(self):
  rr=[r for r in self.source(E)if r['LOI_pct']];self.assertEqual(len(rr),10);self.assertTrue(all(r['pairing_status']!='verified_exact'and not r['material_form_TGA']for r in rr));self.assertEqual({r['LOI_pct']for r in rr if r['material_category']=='cotton'},{'17','24','32','36','43','51','59','67'})
 def test_eapp_neat_tg20air_no_own_loi_no_fixed900_residue(self):
  r=next(r for r in self.source(E)if r['sample_state']=='NeatEAPP');self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['source_TG_mass_mg']),('air','20','20'));self.assertFalse(r['LOI_pct']);self.assertFalse(r.get('R900_pct'));self.assertIn('intervalnotfixedR900',r['source_raw_residue_interval']);self.assertNotEqual(r['pairing_status'],'verified_exact')
 def test_eapp_loading_denominator_not_bath_dose(self):
  r=next(r for r in self.source(E)if r['sample_state']=='CottonEAPP15wtpercent');self.assertEqual((r['source_bath_wt_pct'],r['source_FR_loading_pct'],r['LOI_pct']),('15','15.4','36'));self.assertIn('pristinetextile denominator',r['source_FR_loading_definition']);self.assertIn('SI cited',r['supplement_review_status']);self.assertIn('HTTP403',r['supplement_review_status'])
 def test_fabric_form_invalid_input_and_zero_rate_rejected(self):
  r=self.exact(D,'CottonNDOPA10percent');self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='Neat flame retardant liquid')));self.assertTrue(pairing.evidence_issues(dict(r,heating_rate_C_min='0')))
if __name__=='__main__':unittest.main()
