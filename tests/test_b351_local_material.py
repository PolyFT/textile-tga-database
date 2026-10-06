"""Reject unverified state, threshold and assay substitutions in original-source pairs."""
import csv,json,sys,unittest
from pathlib import Path
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'scripts'))
import pairing as p
import textile_scope as scope
with(R/'data/incoming/verified_source_batch_20261006_b351_local_material.csv').open(newline='')as f:ROWS=list(csv.DictReader(f))
REG=json.loads((R/'data/curation/textile_scope_registry.json').read_text())
D='10.1021/acsami.1c05884';PP='10.1016/j.carbpol.2020.115891';C='10.1002/app.40584';NS='10.1016/j.surfcoat.2016.03.059'
class NativeSourceBoundaries(unittest.TestCase):
 def test_unpaired_controls_and_durability_states_cannot_enter(self):
  self.assertEqual(len(ROWS),17);self.assertEqual(len({p.sample_state_id(x)for x in ROWS}),12)
  self.assertEqual({x['sample_state']for x in ROWS if x['DOI']==PP},{'PP/SA@LDHs(70/30)'})
  cloth=[x for x in ROWS if x['DOI']==D];self.assertEqual(len(cloth),10);self.assertEqual(len({p.sample_state_id(x)for x in cloth}),5)
  self.assertFalse({'PDMP','cotton-PDMP-9.7%','cotton-PDMP-9.7%-50Lc'}&{x['sample_state']for x in cloth})
  self.assertEqual({x['sample_state']for x in ROWS if x['DOI']==NS},{'IFR20','NS4_IFR16'})
  for x in cloth:
   self.assertFalse(p.evidence_issues(x));changed=dict(x,washing_state='after50launderingcycles',LOI_pct='28.6')
   self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(changed))
 def test_undefined_onset_and_conflicting_thresholds_not_promoted(self):
  for x in ROWS:
   self.assertFalse(p.evidence_issues(x));self.assertFalse(x.get('Tonset_C'));self.assertFalse(x.get('T10_C'))
   if x['DOI']!=NS:self.assertFalse(x.get('T5_C'))
   if x['DOI']==D:
    self.assertTrue(x['source_raw_Tonset_C']);bad=dict(x,T10_C=x['source_raw_Tonset_C'])
   elif x['DOI']==PP:
    self.assertFalse(x['T50_C']);self.assertNotEqual(x['source_Table1_T10_C'],x['source_prose_T10_C']);bad=dict(x,T10_C=x['source_Table1_T10_C'])
   elif x['DOI']==C:
    self.assertFalse(x.get('Tmax1_C'));bad=dict(x,Tmax1_C='300')
   else:
    self.assertIn('water',x['source_T5_definition']);self.assertIn('second',x['source_Tmax_definition'])
    self.assertEqual((x['T5_C'],x['Tmax1_C']),('164.0','302.6')if x['sample_state']=='IFR20'else('161.4','296.4'))
    bad=dict(x,Tonset_C=x['source_Tini_C'])
   self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(bad))
 def test_residue_temperature_and_methods_are_not_assay_transfers(self):
  for x in ROWS:
   if x['DOI']==C:
    self.assertEqual((x['residue_temp_C'],x['TG_end_C']),('900','1000'))
    bad=dict(x,residue_temp_C=x['TG_end_C'])
   else:
    self.assertEqual(x['residue_temp_C'],'800');bad=dict(x,residue_pct='8.0')
   self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(bad))
  for x in ROWS:
   if x['DOI']==D:
    self.assertEqual((x['heating_rate_C_min'],x['gas_flow_mL_min']),('20','50'))
    self.assertFalse(x.get('LOI_specimen_geometry'));self.assertIn('denominator unverified',x['composition_basis'])
    self.assertFalse(x.get('LOI_uncertainty_pct'));self.assertFalse(x.get('LOI_replicates'))
 def test_documentary_scope_binding_rejects_changed_composition(self):
  for x in ROWS:
   e=next(e for e in REG['entries']if(e['source_identity'],e['sample_state_id'],e['reviewed_measurement_fingerprint'])==(p.source_identity(x),p.sample_state_id(x),x['reviewed_measurement_fingerprint']))
   self.assertEqual(e['scope_identity_sha256'],scope.scope_identity_sha256(x))
  keys={(p.source_identity(x),p.sample_state_id(x),x['reviewed_measurement_fingerprint'])for x in ROWS}
  subset=dict(REG,entries=[e for e in REG['entries']if(e['source_identity'],e['sample_state_id'],e['reviewed_measurement_fingerprint'])in keys])
  _,report=scope.classify([dict(x,pair_quality='A')for x in ROWS],subset)
  self.assertEqual((report['verified_target_sample_states'],report['verified_target_condition_records']),(12,17))
  invalid=[dict(x,pair_quality='A')for x in ROWS];invalid[0]['composition']+=' altered'
  with self.assertRaisesRegex(ValueError,'Stale textile-scope'):scope.classify(invalid,subset)
if __name__=='__main__':unittest.main(verbosity=2)
