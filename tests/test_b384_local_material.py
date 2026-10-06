"""Portable factual counterexamples for the eight B384 source-approved states."""
import copy,csv,json,sys,unittest
from pathlib import Path
import pandas as pd
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'));import pairing as p,textile_scope as scope,validate_tg_loi as v,reader_table as reader
with(ROOT/'data/incoming/verified_source_batch_20261006_b384_local_material.csv').open(newline='')as h:ROWS=list(csv.DictReader(h))
ENTRIES=json.loads((ROOT/'data/curation/archive/20261006/source_review_manifest_b384.json').read_text())['scope_entries']
PA='10.1002/pc.23781';PP='10.1016/j.compositesa.2017.12.001';TPU='10.1002/pat.5638'
EXPECTED={(PA,s+'; initial prepared state')for s in ['A3','B2','C3']}|{(PP,s)for s in ['PP','PP/IFR-3']}|{(TPU,s+'; initial prepared state')for s in ['TPU/ANF0.250','TPU/ANF-PC0.180','TPU/ANF-PC0.250']}
def exact_matrix(rows):assert len(rows)==8 and {(r['DOI'],r['sample_state'])for r in rows}==EXPECTED
def preserve(a,b):assert all(b.get(k,'')==x for k,x in a.items())
def residue_limit(row):
 if row['DOI']in [PA,TPU]:assert not row.get('residue_pct')and not row.get('residue_temp_C')and not row.get('R750_pct')and not row.get('R700_pct')
def branch(row):
 if row['DOI']==TPU and row['sample_state'].startswith('TPU/ANF0.250'):assert 'not PC-grafted'in row['treatment_method']and 'PC:ANF'not in row['treatment_method']
class B384ScienceBoundaries(unittest.TestCase):
 def test_only_sourceapproved_states_no_controls_or_recipe_hold(self):
  exact_matrix(ROWS);self.assertEqual(len({p.sample_state_id(r)for r in ROWS}),8);self.assertEqual(len({p.pair_key(r)for r in ROWS}),8)
  for doi,bad in [(PA,'A0'),(TPU,'TPU'),(TPU,'TPU/ANF-PC0.125; initial prepared state')]:
   invalid=copy.deepcopy(ROWS);invalid[-1].update(DOI=doi,sample_state=bad)
   with self.assertRaises(AssertionError):exact_matrix(invalid)
 def test_PA_massloss_thresholds_not_ambiguous_Tmax(self):
  r=[r for r in ROWS if r['DOI']==PA];self.assertEqual([(q['LOI_pct'],q['T5_C'],q['T10_C'],q['T50_C'])for q in r],[('27.3','393','409','447'),('26.9','375','390','441'),('27.9','380','399','442')]);self.assertTrue(all(not q['Tmax1_C']and not q['Tonset_C']for q in r));self.assertTrue(all('not established DTGmaximum-rate'in q['limitations']for q in r))
 def test_unknown_residue_temperatures_cannot_use_program_endpoint(self):
  for r in ROWS:residue_limit(r)
  invalid=dict(next(r for r in ROWS if r['DOI']==TPU));invalid.update(residue_pct=invalid['source_residue_pct_unknown_temperature'],residue_temp_C='750',R750_pct=invalid['source_residue_pct_unknown_temperature'])
  with self.assertRaises(AssertionError):residue_limit(invalid)
 def test_PA_base_ratio_and_RP_masterbatch_not_renormalized(self):
  for r in ROWS:
   if r['DOI']==PA:self.assertIn('85/15/5/5/5 retained as ratio',r['composition']);self.assertIn('without inferred pure phosphorus fraction',r['composition']);self.assertIn('TGaliquot cutting/geometry',r['source_preparation'])
 def test_PP_own_experimental_Ti_is5percent_with_zero_residue(self):
  rs=[r for r in ROWS if r['DOI']==PP];self.assertEqual([(r['LOI_pct'],r['T5_C'],r['Tmax1_C'],r['R800_pct'])for r in rs],[('18.0','278','347','0'),('32.5','293','365','20.6')]);self.assertTrue(all(r['residue_temp_C']=='800'and not r['Tonset_C']and '5.0wt%massloss'in r['source_Ti_definition']for r in rs));self.assertEqual(reader.reading_row(rs[0],{'scope_class':'fiber_forming_polymer'})[10],'800℃: 0%; 800℃: 0%')
 def test_TPU_specific_branch_no_grafting_on_ungrafted_ANF(self):
  for r in ROWS:branch(r)
  r=dict(next(r for r in ROWS if r['DOI']==TPU and r['sample_state'].startswith('TPU/ANF0.250')));r['treatment_method']='ANF-PC50:1 grafting RT4h'
  with self.assertRaises(AssertionError):branch(r)
 def test_TPU_T30_definition_and_replicates_not_computed_THRI_peak(self):
  rs=[r for r in ROWS if r['DOI']==TPU];self.assertEqual([(r['T5_C'],r['T30_C'],r['Tmax1_C'],r['LOI_replicates'])for r in rs],[('288.1','361.9','380.2','5'),('321.5','383.7','404.5','5'),('329.4','384.0','403.5','5')]);self.assertTrue(all('5/30% massloss'in r['source_T5_T30_definition']and 'maximum degradation rate'in r['source_Tmax_definition']for r in rs));self.assertTrue(all(not r.get('T50_C')and 'No canonical THRI invented'in r['source_THRI_definition']for r in rs))
 def test_all8_current_measurement_and_scope_bindings(self):
  self.assertEqual(len(ENTRIES),8)
  for r,e in zip(ROWS,ENTRIES):
   self.assertFalse(p.evidence_issues(r));self.assertEqual(e['scope_identity_sha256'],scope.scope_identity_sha256(r));self.assertEqual(e['sample_state_id'],p.sample_state_id(r));self.assertEqual(e['reviewed_measurement_fingerprint'],p.measurement_fingerprint(r));self.assertEqual(e['decision'],'admit_textile')
 def test_missing_gas_or_rate_fails_science_even_refingerprinted(self):
  for field in ['atmosphere','heating_rate_C_min']:
   r=dict(ROWS[0]);r[field]='';r['reviewed_measurement_fingerprint']=p.measurement_fingerprint(r);_,candidate,_,report=v.build_tables(pd.DataFrame([r],dtype=object).fillna(''),[]);self.assertEqual(report['verified_exact_condition_records'],0);self.assertEqual(len(candidate),1)
 def test_fullfield_guard_catches_preparation_omitted_by_fingerprint(self):
  r=next(r for r in ROWS if r['DOI']==TPU);changed=dict(r);changed['treatment_method']='invented PCgrafting forungraftedANF';self.assertEqual(p.measurement_fingerprint(r),p.measurement_fingerprint(changed));self.assertEqual(scope.scope_identity_sha256(r),scope.scope_identity_sha256(changed))
  with self.assertRaises(AssertionError):preserve(r,changed)
 def test_reader_retains_unknown_char_and_original_definitions(self):
  for r,e in zip(ROWS,ENTRIES):
   view=reader.reading_row(r,e);self.assertEqual(len(view),25)
   if r['DOI']in [PA,TPU]:self.assertIn('source_residue_pct_unknown_temperature='+r['source_residue_pct_unknown_temperature'],view[20])
   if r['DOI']==PA:
    self.assertIn('source_T5_T10_T50_definition=',view[20]);self.assertIn('source_Tmax_ambiguous_C='+r['source_Tmax_ambiguous_C'],view[20]);self.assertEqual(view[9],'')
   if r['DOI']==TPU:self.assertIn('source_T5_T30_definition=',view[20]);self.assertIn('LOI_replicates=5',view[21]);self.assertIn('T30_C='+r['T30_C'],view[13])
 def test_stale_scope_binding_rejected(self):
  r=dict(ROWS[0]);e=dict(ENTRIES[0]);e['scope_identity_sha256']='stale';reg=json.loads((ROOT/'data/curation/textile_scope_registry.json').read_text());reg['entries']=[e]
  with self.assertRaisesRegex(ValueError,'Stale textile-scope'):scope.classify([r],reg)
 def test_finished_textile_subtotal_keeps_fibres_separate(self):
  report=json.loads((ROOT/'data/automation/textile_scope_report.json').read_text());progress=json.loads((ROOT/'data/curation/source_verification_progress.json').read_text());classes={'textile_cloth','textile_nonwoven','textile_yarn'};legacy=progress['textile_only_target_scope']
  self.assertEqual(legacy['verified_textile_only_states'],sum(report['verified_sample_states_by_material_class'][k]for k in classes));self.assertEqual(legacy['verified_textile_TG_conditions'],sum(report['verified_condition_records_by_material_class'][k]for k in classes));self.assertEqual(progress['urban_material_target_scope']['verified_target_sample_states'],report['verified_target_sample_states'])
if __name__=='__main__':unittest.main()
