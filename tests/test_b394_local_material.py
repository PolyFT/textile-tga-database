"""Portable source-specific counterexamples for B394, once final payload is approved."""
import copy,csv,json,sys,unittest
from pathlib import Path
import pandas as pd
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import pairing as p,textile_scope as scope,validate_tg_loi as v,reader_table as reader
with(ROOT/'data/incoming/verified_source_batch_20261006_b394_local_material.csv').open(newline='')as f:ROWS=list(csv.DictReader(f))
DELTA=json.loads((ROOT/'data/curation/archive/20261006/source_review_manifest_b394.json').read_text())['scope_delta']
NC='10.1021/acsami.2c16343';PC='10.1021/acsami.3c02139';PAT='10.1002/pat.5447';CH='10.1021/acsapm.5c04084';DT='10.1021/acsapm.5c03938'
DOIS={NC,PC,PAT,CH,DT}
def preserve(a,b):assert all(b.get(k,'')==value for k,value in a.items())
def qualified_peak(r):
 if r['DOI']==NC:assert not r.get('Tmax1_C')and r.get('source_Tmax_ambiguous_C')and 'not confirmed'in r['source_Tmax_definition']
 if r['DOI']==PAT:assert not r.get('Tmax1_C')and r.get('source_raw_Tmax_C')and 'no explicit maximum-ratecriterion'in r['source_Tmax_definition']
def unknown_residue(r):
 if r['DOI']==PC:assert not r.get('residue_pct')and not r.get('residue_temp_C')and not r.get('R700_pct')and not r.get('R800_pct')and 'no temperature'in r['source_residue_temperature_status']
def scope_panel(e):
 if e['source_identity']=='10.1002/pc.23872':assert e['decision']=='hold_scope'
class B394ScientificBoundaries(unittest.TestCase):
 def test_exact_parentapproved_states_no_powders_donor_or_held(self):
  self.assertEqual(len(ROWS),21);self.assertEqual(len({p.sample_state_id(r)for r in ROWS}),18);self.assertEqual({r['DOI']for r in ROWS},DOIS)
  self.assertTrue(all('isolated coating powder'not in r['sample_state']and 'Rinsed cotton'not in r['sample_state']and not r['sample_state'].startswith(('4FR@PET','CH/LAP@PET','DT@PET'))for r in ROWS))
 def test_ambiguous_stage_temperatures_never_DTGrate_peaks(self):
  rs=[r for r in ROWS if r['DOI']==NC];self.assertEqual(len(rs),6);self.assertEqual([r['source_Tmax_ambiguous_C']for r in rs],['371','315','317','317','317','316'])
  for r in ROWS:qualified_peak(r)
  wrong=dict(rs[0]);wrong['Tmax1_C']=wrong['source_Tmax_ambiguous_C']
  with self.assertRaises(AssertionError):qualified_peak(wrong)
 def test_qualifying_T5_and_R700_survive_peak_definition_downselection(self):
  rs=[r for r in ROWS if r['DOI']==NC];self.assertEqual([r['T5_C']for r in rs],['315','305','310','309','309','304']);self.assertTrue(all(r['R700_pct']and r['residue_temp_C']=='700'and r['LOI_pct']for r in rs));self.assertTrue(all(not p.evidence_issues(r)for r in rs))
 def test_original_defined_R700_not800_program_endpoint(self):
  rs=[r for r in ROWS if r['DOI']==PAT];self.assertEqual(len(rs),6);self.assertEqual([r['R700_pct']for r in rs],['12.4','20.2','19.7','20.1','22.0','19.8']);self.assertTrue(all(r['residue_temp_C']=='700'and not r.get('R800_pct')for r in rs));self.assertTrue(all('Bath25wt% notfabricadd-on'in r['limitations']for r in rs))
 def test_original_T70_conflict_not_T10_or_T75(self):
  for r in ROWS:
   if r['DOI']==CH:self.assertFalse(r.get('T10_C'));self.assertFalse(r.get('T70_C'));self.assertFalse(r.get('T75_C'));self.assertIn('10%massloss conflict',r['source_T70_definition'])
 def test_N2_PET_second_column_not_silently_first_peak(self):
  r=next(r for r in ROWS if r['DOI']==CH and r['sample_state'].startswith('PET;'));self.assertFalse(r['Tmax1_C']);self.assertTrue(r['Tmax2_C']);self.assertIn('singlepeak isTmax2columnnotshifted',r['source_Tmax_definition'])
 def test_control_branch_preparation_is_explicitly_qualified(self):
  rs=[r for r in ROWS if r['DOI']in {CH,DT}];self.assertEqual(len(rs),3)
  for r in rs:self.assertTrue(r['source_preparation_scope_note']);self.assertIn('本行实际制备见treatment_method',r['source_preparation_scope_note'])
  self.assertIn('不含LAP/CH',next(r for r in rs if r['sample_state'].startswith('PEI-PA@PET'))['source_preparation_scope_note'])
 def test_per_condition_not_new_sample(self):
  rs=[r for r in ROWS if r['DOI']==PC];self.assertEqual(len(rs),6);self.assertEqual(len({p.sample_state_id(r)for r in rs}),3);self.assertEqual(len({p.pair_key(r)for r in rs}),6)
  self.assertEqual([r['source_raw_residue_pct']for r in rs],['1.3','14.0','7.4','22.4','13.9','31.6'])
  for r in rs:unknown_residue(r)
  invalid=dict(rs[0]);invalid.update(residue_pct=invalid['source_raw_residue_pct'],residue_temp_C='800',R800_pct=invalid['source_raw_residue_pct'])
  with self.assertRaises(AssertionError):unknown_residue(invalid)
 def test_new_and_old_scope_bindings_exclude_glassmat_panels(self):
  self.assertEqual(len(DELTA),42);newkeys={scope.observation_key(r)for r in ROWS};entries={tuple(e[k]for k in ['source_identity','sample_state_id','reviewed_measurement_fingerprint']):e for e in DELTA}
  for r in ROWS:
   e=entries[scope.observation_key(r)];self.assertEqual(e['scope_identity_sha256'],scope.scope_identity_sha256(r));self.assertEqual(e['decision'],'admit_textile')
  old=[e for k,e in entries.items()if k not in newkeys];self.assertEqual(sum(e['decision']=='admit_textile'for e in old),9);self.assertEqual(sum(e['decision']=='hold_scope'for e in old),12)
  for e in old:scope_panel(e)
  invalid=copy.deepcopy(next(e for e in old if e['decision']=='hold_scope'));invalid['decision']='admit_textile'
  with self.assertRaises(AssertionError):scope_panel(invalid)
 def test_missing_TG_gas_rate_or_own_LOI_does_not_pass(self):
  for field in ['atmosphere','heating_rate_C_min','LOI_pct']:
   r=dict(ROWS[0]);r[field]='';r['reviewed_measurement_fingerprint']=p.measurement_fingerprint(r);_,_,_,report=v.build_tables(pd.DataFrame([r],dtype=object).fillna(''),[]);self.assertEqual(report['verified_exact_condition_records'],0)
 def test_allfield_guard_needed_for_treatment_not_fingerprint(self):
  r=ROWS[0];bad=dict(r);bad['treatment_method']='Inventedwashed50cycles'
  self.assertEqual(p.measurement_fingerprint(r),p.measurement_fingerprint(bad));self.assertEqual(scope.scope_identity_sha256(r),scope.scope_identity_sha256(bad))
  with self.assertRaises(AssertionError):preserve(r,bad)
 def test_updated_peak_value_rejects_stale_binding(self):
  r=next(r for r in ROWS if r['DOI']==NC);e=next(e for e in DELTA if tuple(e[k]for k in ['source_identity','sample_state_id','reviewed_measurement_fingerprint'])==scope.observation_key(r));changed=dict(r);changed['Tmax1_C']=r['source_Tmax_ambiguous_C'];changed['reviewed_measurement_fingerprint']=p.measurement_fingerprint(changed);reg=json.loads((ROOT/'data/curation/textile_scope_registry.json').read_text());reg['entries']=[e]
  # A binding for the qualified-only measurement cannot admit an altered peak observation.
  with self.assertRaisesRegex(ValueError,'Stale textile-scope observation'):scope.classify([changed],reg)
if __name__=='__main__':unittest.main()
