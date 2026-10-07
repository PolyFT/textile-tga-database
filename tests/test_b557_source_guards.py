"""Finite B557 source counterexamples; default repository paths are part of the test."""
import csv,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
INCOMING=ROOT/'data/incoming/verified_source_batch_20261007_b557_local_precursors.csv'
MANIFEST=ROOT/'data/curation/archive/20261007/source_review_manifest_b557.json'
class SourceGuards(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with INCOMING.open(newline='') as f: cls.rows=list(csv.DictReader(f))
  cls.man=json.loads(MANIFEST.read_text())
 def test_exact_single_pending_state(self):
  self.assertEqual(len(self.rows),1);r=self.rows[0];self.assertEqual(r['sample_state'],'PET/AlPi (92/8)');self.assertEqual(r['LOI_pct'],'30.1');self.assertEqual(self.man['rootapproved'],0);self.assertEqual(self.man['published'],0)
 def test_two_percent_not_five(self):
  r=self.rows[0];self.assertEqual(r['source_raw_T2pct_C'],'384');self.assertFalse(r.get('T5_C'));self.assertFalse(r.get('Tonset_C'));self.assertIn('2%',r['source_T2_definition'])
 def test_measured_residue_not_calculated(self):
  r=self.rows[0];self.assertEqual(r['R800_pct'],'12.2');self.assertEqual(r['residue_temp_C'],'800');self.assertNotEqual(r['R800_pct'],'8.5');self.assertIn('experimental',r['source_residue_definition'])
 def test_explicit_rate_peak_and_amplitude_unit(self):
  r=self.rows[0];self.assertEqual(r['Tmax1_C'],'447');self.assertEqual(r['source_Rmax_pct_min'],'36.3');self.assertIn('%/min',r['source_Rmax_definition']);self.assertIn('maximum mass loss rate',r['source_Tmax_definition'])
 def test_native_uncertainty_not_invented_sd_or_sign(self):
  r=self.rows[0];self.assertEqual(r['LOI_uncertainty_pct'],'0.5');self.assertIn('unresolved',r['LOI_uncertainty_type']);self.assertEqual(r['source_LOI_error_sign_status'],'native_glyph_unresolved');self.assertFalse(r.get('LOI_SD_pct'));self.assertFalse(r.get('LOI_replicates'))
 def test_actual_common_testing_parent_not_literal_cut(self):
  r=self.rows[0];self.assertIn('Samples for testing',r['source_testing_parent_quote']);self.assertIn('exact TG cutting is not claimed',r['pairing_evidence']);self.assertNotIn('cut from injection',r['pairing_evidence'])
 def test_only_nitrogen_polymer_numbers(self):
  self.assertEqual(self.rows[0]['atmosphere'],'N2');self.assertEqual(self.rows[0]['heating_rate_C_min'],'20');self.assertIn('onlyN2',self.rows[0]['source_TG_unknowns'])
 def test_no_oxide_purecarbon_assertion(self):self.assertIn('not pure carbon',self.rows[0]['source_residue_definition'])
 def test_hold_reasons_not_erased(self):
  ds={x['DOI']:x for x in self.man['processed_source_queue_facts']};self.assertIn('Sbbranch',ds['10.1016/j.polymdegradstab.2013.12.023']['scientific_decision']);self.assertIn('noownLOI',ds['10.1002/app.45912']['scientific_decision']);self.assertIn('dose unknown',ds['10.1002/pat.4015']['scientific_decision'])
 def test_washed_state_not_initial_TG(self):self.assertIn('washedLOI notinitialTG',self.man['processed_source_queue_facts'][2]['scientific_decision'])
 def test_no_ambiguous_modifier_or_control_in_incoming(self):
  self.assertFalse(any('Sb' in r['sample_state'] or r['sample_state']=='PET' for r in self.rows))
 def test_modifier_actual_preparation_separate_from_background(self):
  rs=self.man['nonadmitted_role_examples'];self.assertEqual(len(rs),9)
  for r in rs:
   self.assertIn('background for another material branch only',r['preparation_scope_note']);self.assertTrue('No PET' in r['actual_treatment'] or 'no PET' in r['actual_treatment'] or 'No PA6' in r['actual_treatment'] or 'no PA6' in r['actual_treatment'] or 'No composite extrusion/injection assigned.' in r['actual_treatment'])
 def test_default_archive_location(self):
  self.assertTrue(MANIFEST.is_file());self.assertEqual(self.man['archive_path'],'data/curation/archive/20261007/source_review_manifest_b557.json');self.assertFalse((ROOT/'archive').exists())
 def test_public_manifest_no_private_paths_or_fulltext(self):
  v=json.dumps(self.man,ensure_ascii=False);self.assertNotIn('/'+'Volumes/',v);self.assertNotIn('/'+'Users/',v);self.assertNotIn('complete full text',v)
 def test_own_document_version_not_other_source_counterpart(self):
  r=self.rows[0];self.assertTrue(r['source_version'].startswith('Own published PDF:'))
  self.assertIn('PAT4015 HTML belongs to a different source',r['source_version'])
 def test_selected_binary_residue_no_sb_assignment(self):
  r=self.rows[0];self.assertIn('no Sb assigned to this binary sample',r['source_residue_definition'])
  self.assertIn('exact residue chemistry not inferred',r['source_residue_definition'])
if __name__=='__main__':unittest.main()
