"""Protect rinsing, wash states, water-loss thresholds and TG conditions."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b133/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261002_b133_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing,validate_tg_loi as v
A='10.1002/pat.5335';B='10.1021/acsami.0c17778'
class TextileB133Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def source(self,d):return[r for r in self.rows if r['DOI']==d]
 def exact(self,d,s):return next(r for r in self.source(d)if r['sample_state']==s and r['pairing_status']=='verified_exact')
 def reject(self,r,**kw):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**kw)))
 def test_eight_verified_not_twentyfour_facts(self):
  z=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(z['errors']);self.assertEqual((z['verified_exact_sample_states'],z['verified_exact_condition_records']),(8,8));self.assertEqual(len(self.rows),24)
 def test_all16_held_without_chosen_tg_fields(self):
  rr=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(rr),16);self.assertTrue(all(all(not r.get(k,'')for k in pairing.TG_FIELDS)for r in rr))
 def test_rinsed_al_loi20point5_not_unrinsed21point7(self):
  r=self.exact(A,'Al3PA66rinsed');self.assertEqual(r['LOI_pct'],'20.5');self.reject(r,LOI_pct='21.7');self.assertEqual(len([x for x in self.source(A)if x['pairing_status'].startswith('held_other')]),5)
 def test_rinsed_ip6_loi19point3_not_unrinsed19point5(self):
  r=self.exact(A,'IP6PA66rinsed');self.assertEqual(r['LOI_pct'],'19.3');self.reject(r,LOI_pct='19.5');self.assertEqual(r['source_addon_pct'],'dash')
 def test_no_other_bilayer_tg_from20bilayer(self):
  r=self.exact(A,'PA66AlIP620BL');self.assertEqual(r['LOI_pct'],'27.8');self.reject(r,LOI_pct='26.4');self.reject(r,LOI_pct='23.2');self.reject(r,LOI_pct='22.5')
 def test_101point2_water_t10_not_polyamide_onset(self):
  r=self.exact(A,'PA66AlIP620BL');self.assertEqual(r['T10_C'],'101.2');self.assertFalse(r['Tonset_C']);self.assertFalse(r['T5_C']);self.assertIn('water',r['source_thermal_water_note']);self.reject(r,T10_C='',Tonset_C='101.2')
 def test_polyamide_main_tmax431point2_not_salt_water108point5(self):
  r=self.exact(A,'PA66AlIP620BL');self.assertEqual(r['Tmax1_C'],'431.2');self.reject(r,Tmax1_C='108.5');self.assertFalse(r.get('Tmax2_C'))
 def test_explicit_zero_r800_not_missing_or_estimated(self):
  for d in [A,B]:
   r=self.exact(d,'UntreatedPA66');self.assertEqual((r['R800_pct'],r['residue_pct'],r['residue_temp_C']),('0','0','800'));self.reject(r,residue_pct='1');self.reject(r,residue_temp_C='600')
 def test_static_air_main10_not_n2_or_mcc60(self):
  r=self.exact(A,'PA66AlIP620BL');self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['TG_start_C'],r['TG_end_C']),('air','10','100','800'));self.reject(r,atmosphere='N2');self.reject(r,heating_rate_C_min='60')
 def test_pat_water_and_detergent_sixwashed_no_tg(self):
  rr=[r for r in self.source(A)if r['source_native_wash_count']];self.assertEqual(len(rr),6);self.assertEqual({r['source_wash_medium']for r in rr},{'water_only','commercial_detergent'});self.assertTrue(all(not r['material_form_TGA']and not r['heating_rate_C_min']for r in rr));r=self.exact(A,'PA66AlIP620BL');self.reject(r,LOI_pct='26.2',washing_state='10nativewashings;water_only');self.reject(r,LOI_pct='23.5',washing_state='10nativewashings;commercial_detergent')
 def test_neat_salt_no_own_loi_no_fabric_pair(self):
  r=next(r for r in self.source(A)if r['sample_state']=='NeatAl3IP6salt');self.assertFalse(r['LOI_pct']);self.assertEqual(r['source_raw_Tmax_C'],'108.5');self.assertNotEqual(r['pairing_status'],'verified_exact');self.assertIn('water',r['source_thermal_water_note'])
 def test_same_supplier_controls_distinct_thermal_profiles(self):
  a=self.exact(A,'UntreatedPA66');b=self.exact(B,'UntreatedPA66');self.assertEqual((a['T10_C'],a['Tmax1_C']),('370.5','418.3'));self.assertEqual((b['T10_C'],b['Tmax1_C']),('368','418.5'));self.assertEqual(a['LOI_pct'],b['LOI_pct']);self.reject(a,T10_C=b['T10_C'],Tmax1_C=b['Tmax1_C'])
 def test_acs_four_initial_formulations_not_cross_dose(self):
  r=self.exact(B,'Fe3AAMBAAnPA66');self.assertEqual((r['LOI_pct'],r['source_bath_AA_wt_pct'],r['source_bath_MBAAn_wt_pct'],r['source_bath_Fe_mol_L']),('33.4','15','1','1'));self.reject(r,LOI_pct='32.2');self.reject(r,LOI_pct='19')
 def test_acs_t10_not_t5_or_generic_onset(self):
  r=self.exact(B,'AAMBAAnPA66');self.assertEqual(r['T10_C'],'244.2');self.assertFalse(r['T5_C']);self.assertFalse(r['Tonset_C']);self.reject(r,T10_C='',T5_C='244.2')
 def test_acs_peak_count_not_secondary_temperature(self):
  r=self.exact(B,'Fe3AAMBAAnPA66');self.assertEqual((r['source_reported_DTG_peak_count'],r['Tmax1_C']),('5','466.9'));self.assertFalse(r['Tmax2_C']);self.reject(r,Tmax2_C='5')
 def test_acs_fourwashed20and45cycles_held_no_tg(self):
  rr=[r for r in self.source(B)if r['source_native_wash_count']];self.assertEqual(len(rr),4);self.assertEqual({r['source_native_wash_count']for r in rr},{'20','45'});self.assertEqual({r['LOI_pct']for r in rr},{'21.7','20.3','28.1','27.8'});self.assertTrue(all(not r['material_form_TGA']and r['pairing_status']!='verified_exact'for r in rr));self.reject(self.exact(B,'Fe3AAMBAAnPA66'),LOI_pct='27.8',washing_state='45nativewashings;AATCC124-2001')
 def test_addon_and_uv_units_preserved_without_invented_composition(self):
  r=self.exact(B,'Fe3AAMBAAnPA66');self.assertEqual(r['source_addon_pct'],'39.4');self.assertIn('denominator unreported',r['source_addon_definition']);self.assertFalse(r.get('additive_loading_wt_pct'));self.assertIn('100W/cm2',r['treatment_method']);self.assertIn('OVEN DRY90C15min',r['source_preparation_pretreatment']);self.assertIn('unreported',r['source_preparation_pretreatment'])
 def test_form_mismatch_and_invalid_rate_rejected(self):
  r=self.exact(B,'Fe3AAMBAAnPA66');self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='Neat iron salt')));self.assertTrue(pairing.evidence_issues(dict(r,heating_rate_C_min='0')))
if __name__=='__main__':unittest.main()
