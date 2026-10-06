"""B487 native-source scientific guards; test success is not source approval."""
import copy,csv,json,unittest
from pathlib import Path
import pairing,reader_table
ROOT=Path(__file__).resolve().parents[1]
INCOMING=ROOT/'data/incoming/verified_source_batch_20261007_b487_local_material.csv'
MANIFEST=ROOT/'data/curation/archive/20261007/source_review_manifest_b487.json'
VALUES={'PP':['18.1','371.1','428.9','444.0','454.2','0.3'],'PP/MEG30':['25.3','338.4','433.7','457.2','464.7','25.8'],'PP/EG30':['23.2','367.4','465.2','475.9','476.6','24.9'],'PP/EG/DOPO':['24.2','356.0','454.4','469.2','472.4','24.5']}
def scientific_source_guard(r):
 if pairing.evidence_issues(r):return False
 if r.get('Tonset_C')or r.get('T10_C'):return False
 if r.get('DOI')=='10.1039/c7ra02863f':
  return(r.get('sample_state')=='PP/MOSw'and r.get('LOI_pct')=='24.7'and r.get('T5_C','')==''and r.get('Tmax1_C','')==''and r.get('R700_pct')=='21.7'and r.get('residue_pct')=='21.7'and r.get('residue_temp_C')=='700'and r.get('atmosphere')=='N2'and r.get('heating_rate_C_min')=='5'and r.get('source_T05_C')=='388.6'and r.get('source_Tpeak_C')=='457.6'and r.get('material_form_TGA')=='compression-molded PP composite film'and r.get('material_form_LOI')==r.get('material_form_TGA')and'calculated residual21.5'in r.get('source_residue_temperature_definition',''))
 if r.get('DOI')!='10.1039/c7ra04232a'or r.get('sample_state')not in VALUES:return False
 v=VALUES[r['sample_state']]
 return(all(r.get(k)==z for k,z in zip(['LOI_pct','T5_C','T30_C','T50_C','Tmax1_C','R600_pct'],v))and r.get('residue_pct')==v[-1]and r.get('residue_temp_C')=='600'and r.get('atmosphere')=='N2'and r.get('heating_rate_C_min')=='10'and r.get('gas_flow_mL_min')=='60'and r.get('TG_end_C')=='700'and r.get('material_form_TGA')=='injection-molded PP polymer bar'and r.get('material_form_LOI')==r.get('material_form_TGA'))
class B487SourceGuards(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with INCOMING.open(newline='')as f:cls.rows=list(csv.DictReader(f))
  cls.manifest=json.loads(MANIFEST.read_text());cls.mosw=next(r for r in cls.rows if r['sample_state']=='PP/MOSw');cls.pp=next(r for r in cls.rows if r['sample_state']=='PP');cls.meg=next(r for r in cls.rows if r['sample_state']=='PP/MEG30');cls.facts={r['DOI']:r for r in cls.manifest['processed_source_queue_facts']}
 def changed(self,row,**changes):
  r=copy.deepcopy(row);r.update(changes);r['reviewed_measurement_fingerprint']=pairing.measurement_fingerprint(r);r['reviewed_material_scope_fingerprint']=pairing.material_scope_fingerprint(r);return r
 def test_default_paths_actually_load(self):
  self.assertEqual(str(INCOMING.relative_to(ROOT)),self.manifest['public_incoming_path']);self.assertEqual(str(MANIFEST.relative_to(ROOT)),self.manifest['public_archive_path']);self.assertEqual(len(self.rows),5)
 def test_current_primary_source_fields(self):
  self.assertTrue(all(scientific_source_guard(r)for r in self.rows))
 def test_unknown_t05_not_inferred_t5(self):
  self.assertFalse(scientific_source_guard(self.changed(self.mosw,T5_C='388.6')))
 def test_tpeak_not_inferred_maxrate(self):
  self.assertFalse(scientific_source_guard(self.changed(self.mosw,Tmax1_C='457.6')))
 def test_unknown_definition_raw_display(self):
  r=reader_table.reading_row(self.mosw,{'scope_class':'fiber_forming_polymer_composite'});self.assertEqual(r[6:10],['','','','']);self.assertIn('388.6',r[20]);self.assertIn('457.6',r[20])
 def test_calculated_residue_not_observed(self):
  self.assertFalse(scientific_source_guard(self.changed(self.mosw,R700_pct='21.5',residue_pct='21.5')))
 def test_cone_residue_not_tg(self):
  for value in ['0.83','24.80','27.15']:self.assertFalse(scientific_source_guard(self.changed(self.mosw,R700_pct=value,residue_pct=value)))
 def test_ddpmosw_unknown_residue_temp_not_bridged(self):
  self.assertFalse(scientific_source_guard(self.changed(self.mosw,sample_state='PP/DDPMOSw',LOI_pct='26.1',R700_pct='26.1',residue_pct='26.1')));self.assertEqual(self.facts['10.1039/c7ra02863f']['wholeheld_states'],2)
 def test_mosw_pure_control_missing_preparation(self):
  self.assertFalse(scientific_source_guard(self.changed(self.mosw,sample_state='Neat PP',LOI_pct='18.0',R700_pct='0',residue_pct='0')))
 def test_mosw_crystalwater_not_matrix_peak(self):
  for value in ['250','282','371','411','848','888']:self.assertFalse(scientific_source_guard(self.changed(self.mosw,Tmax1_C=value)))
 def test_t5_not_generic_onset(self):
  self.assertFalse(scientific_source_guard(self.changed(self.pp,Tonset_C='371.1')))
 def test_t30_not_t50_or_peak(self):
  self.assertFalse(scientific_source_guard(self.changed(self.meg,T50_C='433.7')));self.assertFalse(scientific_source_guard(self.changed(self.meg,Tmax1_C='433.7')))
 def test_residue600_not_program_end700(self):
  self.assertFalse(scientific_source_guard(self.changed(self.meg,residue_temp_C='700',R600_pct='',R700_pct='25.8')))
 def test_agent_not_polymer_pair(self):
  for label in ['EG','MEG','MOSw']:self.assertFalse(scientific_source_guard(self.changed(self.meg,sample_state=label)))
 def test_meg10_meg20_no_interpolation(self):
  for label in ['PP/MEG10','PP/MEG20']:self.assertFalse(scientific_source_guard(self.changed(self.meg,sample_state=label)));self.assertEqual(self.facts['10.1039/c7ra04232a']['LOI_only_conditions'],2)
 def test_xps_atoms_not_remaining_mass(self):
  for value in ['96.02','93.96']:self.assertFalse(scientific_source_guard(self.changed(self.meg,R600_pct=value,residue_pct=value)))
 def test_different_form_after_process_rejected(self):
  for form in ['PP granules before injection','PP powder','post-cone char']:self.assertFalse(scientific_source_guard(self.changed(self.meg,material_form_TGA=form)))
 def test_wrong_gas_or_tgftir_conditions(self):
  self.assertFalse(scientific_source_guard(self.changed(self.meg,atmosphere='air')));self.assertFalse(scientific_source_guard(self.changed(self.meg,gas_flow_mL_min='25')))
 def test_eb_loi_not_initial_loi(self):
  self.assertFalse(scientific_source_guard(self.changed(self.meg,DOI='10.1039/c7py01315a',sample_state='EB PP/35% AAPP',LOI_pct='33.7')));self.assertEqual(self.facts['10.1039/c7py01315a']['TG_only_polymer_conditions'],4)
 def test_c7py_no_moldbridge_shortcut(self):
  self.assertEqual(self.facts['10.1039/c7py01315a']['candidate_unique_states'],0);self.assertEqual(self.facts['10.1039/c7py01315a']['wholeheld_states'],4)
 def test_magnitude_qualifier_and_no_guessed_loi_error(self):
  self.assertIn('about0.3',self.pp['source_residue_qualifier']);self.assertTrue(all(r.get('LOI_uncertainty_pct','')==''for r in self.rows))
 def test_undefined_source_temperature_not_universal_reader_allow(self):
  z=reader_table.reading_row(self.changed(self.meg,source_initial_C='999',source_unapproved_TG_C='998'),{'scope_class':'fiber_forming_polymer_composite'});self.assertNotIn('999',z[20]);self.assertNotIn('998',z[20])
 def test_inorganic_residue_not_pure_carbon(self):
  self.assertIn('not purecarbon',self.meg['source_residue_definition']);self.assertIn('not pure-carbon',self.mosw['source_residue_definition'])
 def test_public_facts_no_private_location_or_fulltext(self):
  text=INCOMING.read_text()+MANIFEST.read_text()
  for value in ['/'+'Users/','/'+'Volumes/','smb'+':','file'+':']:self.assertNotIn(value,text)
 def test_derived_root_approval_preserves_primary_snapshot(self):
  self.assertEqual((self.manifest['sourceapproved'],self.manifest['rootapproved'],self.manifest['published']),(1,1,0))
  for key in ['sourceapproved','rootapproved','published']:self.assertEqual(self.manifest['primary_snapshot'][key],0)
  self.assertEqual(self.manifest['primary_snapshot']['immutable_manifest_sha256'],'c27d46780cdc4997b294206f8751d90601d35243a127037eec4383fdd4bb7322')
  self.assertTrue(self.manifest['root_source_approval_sha256'])
  self.assertTrue(self.manifest['independent_source_peer_ready_sha256'])
 def test_derived_five_measurement_fingerprints_still_original(self):
  expected={'PP/MOSw':'30dcba86e8053e03d45cbe23e36c0a9667f15548ed409e31fdb32afb51a8b92d','PP':'286e3771099066045d2ff803c7987b3cd41e71ace8b956b8caf5ead1ec9344ef','PP/MEG30':'10e2a07757f0ff44c71f307e180cfbd5da1849f006d6117f9315d953d4241bdb','PP/EG30':'13758d56056335a019d2da86da7f7f1f19412ba6abe6e2579f83c9ee583e5b35','PP/EG/DOPO':'dbfa20a99947ae1f9e205892d77f25704ed08c264701a5ec4d76f45fa6197c3d'}
  self.assertEqual({r['sample_state']:pairing.measurement_fingerprint(r)for r in self.rows},expected)
 def test_changed_preparation_without_rebinding_fails_scope(self):
  self.assertTrue(pairing.material_scope_review_matches(self.mosw))
  r=copy.deepcopy(self.mosw);r['source_preparation']=r['source_preparation'].replace('raw glyph U+0006 unresolved','plusminus sign confirmed')
  self.assertFalse(pairing.material_scope_review_matches(r))
 def test_storage_temperature_undecoded_sign_not_guessed(self):
  text=self.mosw['source_preparation']
  self.assertIn('store dry23C with source error magnitude2C',text)
  self.assertIn('raw glyph U+0006 unresolved',text)
  self.assertNotIn('23plusminus2C',text)
  self.assertNotIn('23±2',text)
 def test_mosw_actual_film_preparation_separated_from_ddp_branch(self):
  view=reader_table.reading_row(self.mosw,{'scope_class':'fiber_forming_polymer_composite'})[14]
  actual=view.split('\n')[0]
  self.assertIn('PP/MOSw30wt% film',actual)
  self.assertIn('compression190C8min',actual)
  self.assertNotIn('DDP',actual)
  self.assertIn('DDPMOSw modifier branch and are background only',view)
  self.assertIn('文献其他分支的方法背景',view)
 def test_related_ref6_cohort_uncertainty_visible(self):
  view=reader_table.reading_row(self.pp,{'scope_class':'fiber_forming_polymer'})[20]
  self.assertIn('10.1002/pen.24075',view)
  self.assertIn('resin batch and cohort reuse are not explicitly reported',view)
  self.assertIn('no differentbatch claim',view)
 def test_four_actual_bars_display_before_other_synthesis_branches(self):
  for r in self.rows:
   if r['DOI']=='10.1039/c7ra04232a':
    view=reader_table.reading_row(r,{'scope_class':r['material_scope_class']})[14]
    self.assertTrue(view.startswith('Actual Table1 '+r['sample_state']+' initial polymer bar'))
    self.assertIn('injection200/210/205C',view.split('\n')[0])
    self.assertIn('modifier synthesis background',view)

if __name__=='__main__':unittest.main()
