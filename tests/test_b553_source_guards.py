"""Portable B553 source constraints. Defaults exercise the real planned archive path."""
import csv
import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'data/curation/archive/20261007/source_review_manifest_b553.json'
INCOMING=ROOT/'data/incoming/verified_source_batch_20261007_b553_local_material.csv'
def usable_tg(row):
 return bool(row.get('T5_C') or row.get('R700_pct')) and row.get('pairing_status')=='verified_exact' and row.get('source_numeric_role')=='candidate'
class SourceGuards(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.manifest=json.loads(MANIFEST.read_text())
  with INCOMING.open(newline='') as f:cls.rows=list(csv.DictReader(f))
  cls.by={r['sample_state']:r for r in cls.rows}
 def test_actual_default_archive_path(self):
  self.assertEqual(self.manifest['archive_path'],'data/curation/archive/20261007/source_review_manifest_b553.json')
  self.assertEqual(self.manifest['incoming_path'],'data/incoming/verified_source_batch_20261007_b553_local_material.csv')
 def test_four_source_states_not_gas_multiplier(self):
  self.assertEqual(len(self.rows),4);self.assertEqual(len(self.by),4)
  self.assertEqual({r['atmosphere'] for r in self.rows},{'N2'})
 def test_actual_loi_values(self):
  self.assertEqual([r['LOI_pct'] for r in self.rows],['27.8','27.5','26.8','30'])
 def test_actual_t5_values(self):
  self.assertEqual([r['T5_C'] for r in self.rows],['360','341','358.1','356.2'])
 def test_actual_residue_measured_values(self):
  self.assertEqual([r['R700_pct'] for r in self.rows],['16.51','15.61','11.42','11.1'])
 def test_no_calculated_residue_substitution(self):
  self.assertEqual(self.by['PET/10%PNCP']['R700_pct'],'16.51')
  self.assertNotEqual(self.by['PET/10%PNCP']['R700_pct'],'6.44')
  self.assertEqual(self.by['PET/7.5%PNCP/2.5%TSCA']['R700_pct'],'11.1')
  self.assertNotEqual(self.by['PET/7.5%PNCP/2.5%TSCA']['R700_pct'],'6.78')
 def test_residue_exact_temperature_and_definition(self):
  for r in self.rows:
   self.assertEqual(r['residue_temp_C'],'700');self.assertEqual(r['residue_pct'],r['R700_pct'])
   self.assertIn('measurement',r['source_residue_temperature_definition'])
   self.assertFalse(r.get('R800_pct'));self.assertFalse(r.get('TG_end_C'))
 def test_unresolved_control_not_admitted(self):
  self.assertNotIn('Pure PET',self.by)
  r=self.manifest['held_control_reuse']
  self.assertEqual(r['decision'],'wholehold_reuse_identity_unknown');self.assertFalse(r['counted'])
  self.assertEqual((r['LOI_pct'],r['T5_C'],r['Tmax1_C'],r['R700_pct']),('26.5','410','428','7.08'))
 def test_modified_tmax_criterion_not_guessed(self):
  expected=['407','373','422.6','419.7']
  for r,raw in zip(self.rows,expected):
   self.assertFalse(r['Tmax1_C']);self.assertEqual(r['source_Tmax_ambiguous_C'],raw)
   self.assertIn('criterion not independently explicit',r['source_Tmax_definition'])
 def test_rate_amplitudes_not_peak_temperature(self):
  self.assertEqual([r['source_Rmax_wt_pct_min'] for r in self.rows],['12.3','12.5','16.24','15.79'])
  for r in self.rows:self.assertIn('rate amplitude not temperature',r['source_Rmax_definition'])
 def test_t5_not_independent_tonset(self):
  for r in self.rows:
   self.assertIn('5wt%',r['source_T5_definition']);self.assertFalse(r.get('Tonset_C'));self.assertFalse(r.get('T10_C'))
 def test_mcc_temp_not_ordinarytg(self):
  for r in self.rows:
   self.assertNotIn(r.get('Tmax1_C',''),['474.3','391.1','430.4','435.0'])
   self.assertIn('MCC Table2',r['source_metric_limits'])
 def test_feed_grams_not_normalized_weight(self):
  r=self.by['PET/10%PNCP'];self.assertIn('PET100g; PNCP10g; TSCA0g',r['composition'])
  self.assertIn('not normalized final wt%',r['composition'])
 def test_actual_ifr_mapping(self):
  r=self.by['PET/7.5%PNCP/2.5%TSCA'];self.assertIn('ratio3:1 explicitly',r['pairing_evidence'])
  self.assertEqual(r['LOI_pct'],'30');self.assertEqual(r['T5_C'],'356.2')
 def test_no_interpolated_loionly_formulations(self):
  for n in ['PET/8.33%PNCP/1.67%TSCA','PET/6.67%PNCP/3.33%TSCA','PET/5%PNCP/5%TSCA']:self.assertNotIn(n,self.by)
 def test_preparation_whole_series_and_separate_dsc(self):
  for r in self.rows:
   self.assertIn('Whole Table1 series',r['source_preparation']);self.assertIn('3MPa/280C/30s',r['source_preparation'])
   self.assertIn('DSC erase history',r['source_preparation_scope_note']);self.assertIn('not initial TG/LOI',r['source_preparation_scope_note'])
 def test_missing_tg_methods_remain_unknown(self):
  for r in self.rows:
   self.assertEqual(r['heating_rate_C_min'],'10');self.assertFalse(r.get('gas_flow_mL_min'))
   self.assertIn('mass/pan/flow/start/end/exact cutting unknown',r['source_TG_unknowns'])
 def test_hold_and_calculated_roles_not_candidate_count(self):
  c=self.manifest['counts'];self.assertEqual(c['physical_conditions'],38);self.assertEqual(c['wholeheld_TG'],15)
  self.assertEqual(c['wholeheld_states'],8);self.assertEqual(c['calculated_views'],5)
  self.assertEqual(c['TG_only_modifier_conditions'],9);self.assertEqual(c['LOI_only_states'],10)
 def test_processing_hold_cannot_become_usable_by_copying_values(self):
  q=dict(self.rows[0]);q.update(pairing_status='hold_processing_bridge',source_numeric_role='whole_pair_hold')
  self.assertFalse(usable_tg(q));self.assertTrue(usable_tg(self.rows[0]))
 def test_root_source_reuse_phase_not_publication(self):
  self.assertTrue(self.manifest['rootapproved']);self.assertEqual(self.manifest['published'],0)
  for r in self.rows:self.assertIn('PENDING_NONAUTHOR_ROOT_FULLREUSE',r['evidence_reviewed_by'])
 def test_public_paths_and_uncertainty_not_fabricated(self):
  for r in self.rows:
   self.assertNotIn('/'+'Volumes/',str(r));self.assertNotIn('/'+'Users/',str(r))
   self.assertIn('do not infer SD/zero',r['source_uncertainty_definition']);self.assertFalse(r.get('LOI_uncertainty_pct'))
if __name__=='__main__':unittest.main()
