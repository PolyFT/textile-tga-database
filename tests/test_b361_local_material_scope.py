"""Portable source-specific counterexamples for the eight new factual pairs.

Use the committed factual input and documentary manifest bindings.
Only local factual payloads and existing scientific validators are read.
"""
import csv,json,sys,unittest
from pathlib import Path
import pandas as pd
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1]
ROOT=R
sys.path.insert(0,str(R/'scripts'))
import pairing as p
import validate_tg_loi as v
import textile_scope as scope
with(R/'data/incoming/verified_source_batch_20261006_b361_local_material.csv').open()as h:ROWS=list(csv.DictReader(h))
ENTRIES=json.loads((R/'data/curation/source_review_manifest_20261006_b361.json').read_text())['bindings']
EXPECTED={'10.1016/j.surfcoat.2015.05.023':{'Untreated','10 P','10 A','10 BL'},'10.1039/c5ra09963c':{'Pristine cotton','Superhydrophobic sample'},'10.1007/s10904-022-02395-w':{'CF/EVA/SiO2','CF/EVA/Al2O3'}}
def check_state_matrix(rows):
 assert len(rows)==8
 assert {(r['DOI'],r['sample_state'])for r in rows}=={(doi,state)for doi,states in EXPECTED.items()for state in states}
def all_fields_match(before,after):
 assert len(before)==len(after)
 for old,new in zip(before,after):assert all(new.get(k,'')==x for k,x in old.items())
class B361ScientificGuards(unittest.TestCase):
 def test_exact_state_matrix_rejects_PS_washed_and_unknown_TG_states(self):
  check_state_matrix(ROWS)
  for forbidden in['Sample + PS','Superhydrophobic sample;5minultrasonicwash','CF/EVA','CF/EVA/SiO2/Al2O3']:
   invalid=[dict(r)for r in ROWS];invalid[-1]['sample_state']=forbidden
   with self.assertRaises(AssertionError):check_state_matrix(invalid)
 def test_497_is_inorganic_stage_end_not_programme_end(self):
  for r in ROWS:
   if r['DOI']=='10.1007/s10904-022-02395-w':
    self.assertEqual((r['residue_temp_C'],r['TG_end_C']),('497','600'));self.assertIn('ends497C',r['source_residue_temperature_definition']);self.assertIn('notpurechar',r['source_residue_phase']);self.assertTrue(all(not r.get(k)for k in['T5_C','T10_C','Tonset_C','Tmax1_C','R600_pct']));self.assertEqual(r['residue_pct'],'2.6'if r['sample_state']=='CF/EVA/SiO2'else'13.8')
 def test_missing_TG_rate_or_unknown_residue_temperature_not_promoted(self):
  r=dict(ROWS[0]);r['heating_rate_C_min']='';r['reviewed_measurement_fingerprint']=p.measurement_fingerprint(r)
  _,candidate,_,report=v.build_tables(pd.DataFrame([r],dtype=object).fillna(''),[]);self.assertEqual(report['verified_exact_condition_records'],0);self.assertIn('missing_or_invalid_heating_rate',candidate.iloc[0]['review_reasons'])
  r=next(dict(r)for r in ROWS if r['DOI']=='10.1007/s10904-022-02395-w');r['sample_state']='CF/EVA/SiO2/Al2O3';r['LOI_pct']='29.3'
  for field in p.TG_FIELDS:r[field]=''
  r['residue_temp_C']='';r['source_native_residue_pct']='15.7';r['source_native_stage_start_C']='418';r['reviewed_measurement_fingerprint']=p.measurement_fingerprint(r)
  master,_,_,report=v.build_tables(pd.DataFrame([r],dtype=object).fillna(''),[]);self.assertEqual(report['verified_exact_condition_records'],0);self.assertEqual(len(master),0)
 def test_air_secondary_peak_and_original_T5_remain_distinct(self):
  for r in ROWS:
   if r['DOI']=='10.1016/j.surfcoat.2015.05.023':
    self.assertIn('oxidation',r['source_Tmax2_definition']);self.assertEqual(r['source_native_residue_at_Tmax1_temp_C'],r['Tmax1_C']);self.assertEqual(r['residue_temp_C'],'600');self.assertFalse(r.get('T5_C'));self.assertFalse(r.get('T10_C'))
   if r['DOI']=='10.1039/c5ra09963c':self.assertIn('5wtpercent',r['source_T5_definition']);self.assertEqual(r['residue_temp_C'],'750')
 def test_scope_only_module_has_no_numeric_import_and_hold_is_not_admit(self):
  new_fps={r['reviewed_measurement_fingerprint']for r in ROWS};new_entries=[e for e in ENTRIES if e['reviewed_measurement_fingerprint']in new_fps];old=[e for e in ENTRIES if e['reviewed_measurement_fingerprint']not in new_fps]
  self.assertEqual(len(new_entries),8);self.assertEqual(len(old),65);self.assertEqual(sum(e['decision']=='admit_textile'for e in old),64);self.assertEqual(len({e['sample_state_id']for e in old if e['decision']=='admit_textile'}),59)
  held=[e for e in old if e['decision']=='hold_scope'];self.assertEqual(len(held),1);self.assertIn('zero-acid',held[0]['scope_evidence'].lower());self.assertEqual(len({p.sample_state_id(r)for r in ROWS}),8)
  self.assertTrue(all(e['scope_class']=='textile_cloth'for e in new_entries));self.assertTrue(all(not r['material_scope_class']for r in ROWS))
 def test_stale_cloth_inline_and_extra_R1000_mutation_rejected(self):
  r=dict(ROWS[0]);r['material_scope_class']='textile_cloth';r['reviewed_material_scope_fingerprint']=p.material_scope_fingerprint(r);self.assertIn('material_scope_review_pending_or_stale',p.evidence_issues(r))
  e=dict(next(e for e in ENTRIES if e['reviewed_measurement_fingerprint']==ROWS[0]['reviewed_measurement_fingerprint']));e['reviewed_measurement_fingerprint']='stale';registry=json.loads((ROOT/'data/curation/textile_scope_registry.json').read_text());registry['entries']=[e]
  with self.assertRaisesRegex(ValueError,'Stale textile-scope'):scope.classify(ROWS,registry)
  original={'pair_key':'existing_source_state','LOI_pct':'31.5','residue_pct':'2.50','source_raw_R1000_pct':'3.70','limitations':'Originalconflictretained'};mutated=dict(original);mutated['source_raw_R1000_pct']='4.00'
  with self.assertRaises(AssertionError):all_fields_match([original],[mutated])
if __name__=='__main__':unittest.main()
