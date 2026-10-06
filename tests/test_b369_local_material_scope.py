"""Portable scientific counterexamples for the B369 factual+scope-only bundle."""
import csv,json,sys,unittest
from pathlib import Path
import pandas as pd
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import pairing as p, textile_scope as scope, validate_tg_loi as v
with(ROOT/'data/incoming/verified_source_batch_20261006_b369_local_material.csv').open(newline='')as h:ROWS=list(csv.DictReader(h))
ENTRIES=json.loads((ROOT/'data/curation/archive/20261006/source_review_manifest_b369.json').read_text())['scope_entries']
AF='10.1016/j.compositesa.2018.10.015';APP='10.1007/s10570-018-1930-0';AZ='10.1007/s10570-019-02668-7';SLS='10.1021/acssuschemeng.4c09671'
EXPECTED={(AF,f'UF/{dose} wt%AF; initial cured and foamed material','N2')for dose in ['1.0','2.0','3.0']}|{(APP,state,gas)for state in ['Control cotton; untreated','APP 30% mass-concentration cotton; 0 LCs','APP 30% mass-concentration cotton; 50 LCs']for gas in ['N2','air']}|{(AZ,'Control bleached cotton; initial','air'),(SLS,'CC; initial','N2')}
def exact_matrix(rows):assert len(rows)==11 and {(r['DOI'],r['sample_state'],r['atmosphere'])for r in rows}==EXPECTED
def full_fields_preserved(a,b):
 assert len(a)==len(b)
 for old,new in zip(a,b):assert all(new.get(k,'')==x for k,x in old.items())
class B369ScientificGuards(unittest.TestCase):
 def test_allstates_conditions_reject_unproven_groups(self):
  exact_matrix(ROWS);self.assertEqual(len({p.sample_state_id(r)for r in ROWS}),8)
  for bad in ['UF; initial','UF/0.5 wt%AF; initial','FRC30; initial','APP 22% mass-concentration cotton; 0 LCs','Control bleached cotton; 30% triazole']:
   invalid=[dict(r)for r in ROWS];invalid[-1]['sample_state']=bad
   with self.assertRaises(AssertionError):exact_matrix(invalid)
 def test_499point6_is_explicit_stage_endpoint_not_R800(self):
  r=next(r for r in ROWS if r['DOI']==APP and r['sample_state']=='Control cotton; untreated'and r['atmosphere']=='air');self.assertEqual((r['residue_pct'],r['residue_temp_C'],r['TG_end_C']),('0.0012','499.6','800'));self.assertEqual(r['R800_pct'],'');self.assertEqual(r.get('R500_pct',''),'');invalid=dict(r);invalid['residue_temp_C']='800';self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(invalid))
 def test_wash_pre_and_post_same_dose_not_mix(self):
  expected={('0 LCs','N2'):('50.1','36.49'),('0 LCs','air'):('50.1','10.22'),('50 LCs','N2'):('28.5','31.80'),('50 LCs','air'):('28.5','8.02')}
  for r in ROWS:
   if r['DOI']==APP and r['sample_state'].startswith('APP'):
    self.assertEqual((r['LOI_pct'],r['R800_pct']),expected[(r['sample_state'].split('; ')[-1],r['atmosphere'])]);self.assertIn('mass-concentration',r['sample_state']);self.assertEqual(r['residue_temp_C'],'800')
 def test_same_curve_multiple_residue_temperatures_not_more_pairs(self):
  self.assertEqual(len([r for r in ROWS if r['DOI']==APP]),6);self.assertEqual(len({p.sample_state_id(r)for r in ROWS if r['DOI']==APP}),3);self.assertEqual(len({p.pair_key(r)for r in ROWS}),11)
 def test_sourceT70_notT75_or_Tmax(self):
  expected={'1.0':('39.5','289.8','334.8','472.3','14.9'),'2.0':('40.0','289.8','337.3','492.3','17.1'),'3.0':('41.5','290.1','339.6','510.2','18.7')}
  for r in ROWS:
   if r['DOI']==AF:
    dose=r['sample_state'].split('/')[1].split(' ')[0];self.assertEqual(tuple(r[k]for k in ['LOI_pct','T30_C','T50_C','source_T70_C','residue_pct']),expected[dose]);self.assertFalse(r.get('T75_C'));self.assertFalse(r['Tmax1_C']);self.assertEqual(r['residue_temp_C'],'700');self.assertEqual(r['material_scope_class'],'fiber_forming_polymer_composite')
 def test_bothgas_not_inherit_LOI_durability_condition(self):
  n2=next(r for r in ROWS if r['DOI']==APP and r['sample_state'].endswith('50 LCs')and r['atmosphere']=='N2');air=next(r for r in ROWS if r['DOI']==APP and r['sample_state'].endswith('50 LCs')and r['atmosphere']=='air');self.assertEqual(p.sample_state_id(n2),p.sample_state_id(air));self.assertNotEqual(p.pair_key(n2),p.pair_key(air))
 def test_original_onset_not_T5_or_T10(self):
  r=next(r for r in ROWS if r['DOI']==AZ);self.assertEqual((r['LOI_pct'],r['Tonset_C']),('18','360'));self.assertFalse(r['T5_C']);self.assertFalse(r['T10_C']);self.assertFalse(r['residue_pct']);self.assertFalse(r['TG_end_C'])
 def test_CC_N2_only_independent_supportedR(self):
  rs=[r for r in ROWS if r['DOI']==SLS];self.assertEqual(len(rs),1);r=rs[0];self.assertEqual((r['sample_state'],r['atmosphere'],r['LOI_pct'],r['Tmax1_C'],r['residue_pct'],r['residue_temp_C']),('CC; initial','N2','18.5','357.78','5.34','700'));self.assertEqual(r.get('T5_C',''),'')
 def test_source_scope_module0_numeric_import46states58conditions(self):
  fps={r['reviewed_measurement_fingerprint']for r in ROWS};new=[e for e in ENTRIES if e['reviewed_measurement_fingerprint']in fps];old=[e for e in ENTRIES if e['reviewed_measurement_fingerprint']not in fps];self.assertEqual((len(new),len(old)),(11,115));admit=[e for e in old if e['decision']=='admit_textile'];hold=[e for e in old if e['decision']=='hold_scope'];self.assertEqual((len(admit),len({e['sample_state_id']for e in admit})),(105,88));self.assertEqual((len(hold),len({e['sample_state_id']for e in hold})),(10,9));self.assertTrue(all(e['scope_identity_sha256']for e in old))
 def test_full_field_guard_protects_preparation_beyond_scopehash(self):
  with(ROOT/'data/tg_loi_master.csv').open()as h:old=list(csv.DictReader(h))
  r=dict(next(q for q in old if q.get('treatment_method')));changed=dict(r);changed['treatment_method']=r['treatment_method']+'; changed drying80Covernight'
  self.assertEqual(scope.scope_identity_sha256(r),scope.scope_identity_sha256(changed))
  with self.assertRaises(AssertionError):full_fields_preserved([r],[changed])
 def test_missing_rate_no_science_approval(self):
  r=dict(ROWS[0]);r['heating_rate_C_min']='';r['reviewed_measurement_fingerprint']=p.measurement_fingerprint(r);_,candidate,_,report=v.build_tables(pd.DataFrame([r],dtype=object).fillna(''),[]);self.assertEqual(report['verified_exact_condition_records'],0);self.assertIn('missing_or_invalid_heating_rate',candidate.iloc[0]['review_reasons'])
 def test_held_unknown_temperature_without_independent_metric_no_pair(self):
  r=dict(next(r for r in ROWS if r['DOI']==SLS));r['sample_state']='FRC30; initial';r['LOI_pct']='57.6'
  for k in p.TG_FIELDS:r[k]=''
  r['residue_temp_C']='';r['source_residue_pct_unknown_temperature']='37.16';r['reviewed_measurement_fingerprint']=p.measurement_fingerprint(r);master,_,_,report=v.build_tables(pd.DataFrame([r],dtype=object).fillna(''),[]);self.assertEqual(report['verified_exact_condition_records'],0);self.assertEqual(len(master),0)
 def test_binding_and_extra_rawmetric_staleness(self):
  r=dict(ROWS[0]);e=dict(next(e for e in ENTRIES if e['reviewed_measurement_fingerprint']==r['reviewed_measurement_fingerprint']));e['scope_identity_sha256']='stale';reg=json.loads((ROOT/'data/curation/textile_scope_registry.json').read_text());reg['entries']=[e]
  with self.assertRaisesRegex(ValueError,'Stale textile-scope'):scope.classify([r],reg)
  altered=dict(r);altered['source_T70_C']='999'
  with self.assertRaises(AssertionError):full_fields_preserved([r],[altered])
if __name__=='__main__':unittest.main()
