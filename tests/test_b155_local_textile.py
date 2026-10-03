"""Protect original-source identities, criteria, endpoints and held reuse risks."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent; private=P.name=='work'; R=P.parent/'repo' if private else P.parent
F=P/'staged-local-textile-b155/publication_proposed.csv' if private else R/'data/incoming/verified_source_batch_20261004_b155_local_textile.csv'
sys.path.insert(0,str(R/'scripts'))
import pairing
import validate_tg_loi as v
A='10.1007/s10570-022-04430-y'; B='10.1007/s10570-022-04416-w'; C='10.1007/s10570-022-04558-x'
class TextileB155Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='') as h:cls.rows=list(csv.DictReader(h))
 def accepted(self,control=False,gas='N2'):
  return next(r for r in self.rows if r['DOI']==C and r['pairing_status']=='verified_exact' and r['atmosphere']==gas and ('Control' in r['sample_state'])==control)
 def reject(self,r,**changes):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**changes)))
 def held(self,d):return [r for r in self.rows if r['DOI']==d and r['pairing_status']!='verified_exact']
 def test_two_states_four_conditions_not38facts(self):
  p=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(p['errors']);self.assertEqual((p['verified_exact_sample_states'],p['verified_exact_condition_records']),(2,4));self.assertEqual(len(self.rows),38)
 def test_all34held_records_excluded(self):
  self.assertEqual([len(self.held(d)) for d in [A,B,C]],[5,22,7]);self.assertTrue(all(pairing.evidence_issues(r) for d in [A,B,C] for r in self.held(d)))
 def test_native_nitrogen_profiles(self):
  for control,vals in [(True,(257.5,280.7,331.6,18.9)),(False,(184.4,225.9,263.6,28.6))]:
   r=self.accepted(control);self.assertEqual(tuple(float(r[k]) for k in ['T5_C','T10_C','Tmax1_C','R600_pct']),vals)
 def test_native_air_profiles(self):
  for control,vals in [(True,(153.1,259.8,301.4,1)),(False,(178.4,221.8,262.6,12.6))]:
   r=self.accepted(control,'air');self.assertEqual(tuple(float(r[k]) for k in ['T5_C','T10_C','Tmax1_C','R600_pct']),vals)
 def test_only300gLtreated_TG_nototherdoses(self):
  self.assertIn('300gL',self.accepted()['sample_state']);self.assertEqual(self.accepted()['source_weight_gain_wt_pct'],'25.3')
  rows=[r for r in self.held(C) if 'initial' in r['sample_state']];self.assertEqual(len(rows),3);self.assertTrue(all(not r['Tmax1_C'] for r in rows))
 def test_loi_is_own40_5_notcomparative_max_or400gL(self):
  r=self.accepted();self.assertEqual(r['LOI_pct'],'40.5');self.assertEqual(self.accepted(True)['LOI_pct'],'17');self.reject(r,LOI_pct='42')
 def test_washed_loi_notinitial_TG(self):
  r=self.accepted();self.reject(r,LOI_pct='31.5');self.reject(r,washing_state='50launderingcycles')
  washed=[r for r in self.held(C) if 'after50' in r['sample_state']];self.assertEqual([r['LOI_pct'] for r in washed],['31.5','33.9']);self.assertTrue(all(not r['Tmax1_C'] for r in washed))
 def test_waterloss_notdecomposition_peak(self):
  r=self.accepted();self.assertEqual(r['Tmax1_C'],'263.6');self.reject(r,Tmax1_C='79.1');self.assertFalse(r.get('Tmax2_C'))
 def test_abstract_initial_values_are_T10_not_T5_or_Tonset(self):
  r=self.accepted();self.assertEqual((r['T5_C'],r['T10_C']),('184.4','225.9'));self.assertFalse(r.get('Tonset_C'));self.reject(r,T5_C='225.9');self.reject(r,Tonset_C='225.9')
 def test_gas_and_ramp_mutation_invalidates_review(self):
  r=self.accepted();self.assertEqual(r['heating_rate_C_min'],'10');self.reject(r,atmosphere='air');self.reject(r,heating_rate_C_min='20')
 def test_residue600_not_method800(self):
  r=self.accepted();self.assertEqual((r['residue_temp_C'],r['TG_end_C']),('600','600'));self.reject(r,residue_temp_C='800');self.reject(r,R600_pct='',R800_pct='28.6')
 def test_separate_TGIR_range_and_unknown_flow(self):
  r=self.accepted();self.assertEqual((r['TG_start_C'],r['TG_end_C']),('30','600'));self.assertIn('30-800',r['source_TGIR_method']);self.assertFalse(r['source_TG_flow_mL_min'])
 def test_DTG_rates_percent_per_C_not_perminute(self):
  self.assertEqual([self.accepted(c,g)['source_DTGmax_rate_pct_per_C'] for c,g in [(True,'N2'),(False,'N2'),(True,'air'),(False,'air')]],['1.4','1.1','1.1','1.4']);self.assertIn('notpercentpermin',self.accepted()['source_DTG_rate_definition'])
 def test_plainwoven_density_nototherpaper(self):
  r=self.accepted();self.assertIn('plain-woven',r['material_form']);self.assertIn('122g/m2',r['material_form']);self.assertIn('CaifuMarketJilin',r['material_form']);self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='Owncotton textile fabric,134.2g/m2')))
 def test_control_hasno_FR_finalcomponentfractions_unknown(self):
  self.assertIn('noFR',self.accepted(True)['composition']);self.assertIn('FR300g/L',self.accepted()['composition']);self.assertIn('finalcomponentfractionsunknown',self.accepted()['composition']);self.assertIn('160C2min',self.accepted()['treatment_method'])
 def test_unreported_uncertainty_and_repeats_notinvented(self):
  r=self.accepted();self.assertIn('Unreported',r['source_LOI_repeats_uncertainty']);self.assertFalse(r.get('LOI_uncertainty_pct'));self.assertFalse(r.get('TGA_repeats'))
 def test_own_LOI_dimensions(self):
  r=self.accepted();self.assertEqual(r['source_LOI_dimensions_mm'],'150x58');self.assertEqual(r['LOI_standard'],'GB/T5454-1997')
 def test_TECHPA_unproven_residuetemperature_staysraw(self):
  rows=[r for r in self.held(B) if r['source_reported_final_residual_mass_pct']];self.assertEqual([r['source_reported_final_residual_mass_pct'] for r in rows],['3.1','41.1']);self.assertTrue(all(not r.get('residue_temp_C') and not r['R600_pct'] and not r.get('R700_pct') for r in rows));self.assertTrue(all(r['TG_end_C']=='700' for r in rows))
 def test_TECHPA_interval_edges_not_Tonset_T5_Tmax(self):
  rows=[r for r in self.held(B) if r['source_reported_final_residual_mass_pct']];self.assertTrue(all(not r['T5_C'] and not r['T10_C'] and not r['Tmax1_C'] and not r.get('Tonset_C') for r in rows));self.assertEqual(rows[1]['source_reported_decomposition_stage_interval_C'],'250.5-313.5;notT5/T10/Tonset/Tmax')
 def test_all17_TECHPA_washedstates_lackown_TG(self):
  rows=[r for r in self.held(B) if 'after' in r['sample_state']];self.assertEqual(len(rows),17);self.assertTrue(all(not r['Tmax1_C'] for r in rows));self.assertTrue(all('washduration/equivcycledefinitionnotreported' in r['washing_state'] for r in rows))
 def test_TECHPA_addon_uncertainty_not_LOIerrororbulkfraction(self):
  r=next(r for r in self.held(B) if r['sample_state']=='TECHPA40gL initial cotton fabric');self.assertEqual((r['source_weight_gain_initial_wt_pct'],r['source_weight_gain_initial_uncertainty_pct']),('25.2','0.7'));self.assertFalse(r.get('LOI_uncertainty_pct'));self.assertIn('initialaddonnotwashedaddon',r['source_addon_uncertainty_definition'])
 def test_casein_control_reuse_risk_notcounted(self):
  r=next(r for r in self.held(A) if 'control' in r['sample_state']);self.assertEqual((r['Tmax1_C'],r['R600_pct'],r['LOI_pct']),('362','9.25','17.4'));self.assertIn('9b02474',r['source_cross_source_TG_reuse_risk']);self.assertIn('notassertproven_duplicate',r['source_cross_source_TG_reuse_risk']);self.assertIn('reuse_provenance_unresolved',r['pairing_status'])
 def test_generic_CADP_TG_cannotbind40percent(self):
  r=next(r for r in self.held(A) if r['sample_state']=='CADP40% initial cotton fabric');self.assertEqual((r['LOI_pct'],r['R600_pct']),('41.6','42.42'));self.assertIn('doseunresolved',r['source_TG_sample_state']);self.assertFalse(r['Tmax1_C']);self.assertFalse(r.get('Tonset_C'));self.assertEqual(r['source_reported_undefined_significant_mass_loss_C'],'239')
 def test_casein_handandhomewashes_remainseparate(self):
  rows=[r for r in self.held(A) if 'after50' in r['sample_state']];self.assertEqual([r['LOI_pct'] for r in rows],['30.2','26.4']);self.assertTrue(all('numericannotationsunread' in r['source_washed_TG_status'] for r in rows));self.assertTrue(all(not r['Tmax1_C'] for r in rows))
 def test_bulk_FR_cannotpairfinishedcotton(self):
  rows=[r for r in self.held(C) if 'BulkFR' in r['sample_state']];self.assertEqual(len(rows),2);self.assertTrue(all(r['material_form']=='BulkFRcompoundpowder' and not r['material_form_LOI'] and not r['LOI_pct'] for r in rows));self.assertEqual([r['R600_pct'] for r in rows],['21.0','35.9'])
 def test_conechar_and_peakweightloss_not_TGresidue(self):
  r=self.accepted();self.reject(r,R600_pct='36');self.reject(self.accepted(True),R600_pct='7.6');self.assertFalse(r.get('residue_at_Tmax1_pct'));self.reject(self.accepted(False,'air'),R600_pct='30.6')
 def test_allapproved_metrics_bound_to_own_same_state(self):
  rows=[r for r in self.rows if r['pairing_status']=='verified_exact'];self.assertEqual(len(rows),4)
  for r in rows:
   self.assertFalse(pairing.evidence_issues(r));self.reject(r,LOI_pct=str(float(r['LOI_pct'])+1));self.reject(r,sample_state='Remoldedpolymer-sheet')
if __name__=='__main__':unittest.main()
