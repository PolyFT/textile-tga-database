import copy,csv,json,sys,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));import textile_scope as scope
with(R/'data/tg_loi_master.csv').open(newline='')as f:MASTER=list(csv.DictReader(f))
REGISTER=json.loads((R/'data/curation/textile_scope_registry.json').read_text())
COTTON=[r for r in MASTER if r['DOI']=='10.3390/polym16101409'and r['sample_state']=='Cotton']
PAPER=next(r for r in MASTER if r['DOI']=='10.1007/s10570-018-1749-8')
GLASS_EP=[r for r in MASTER if r['DOI']=='10.1016/j.compositesb.2016.10.003'and r['sample_state']=='ASET; initial six-ply woven glass/epoxy laminate; epoxy composition with 0 wt% APP and 0 wt% PNA']
def subset(rows):
 keys={scope.observation_key(r)for r in rows};d=copy.deepcopy(REGISTER);d['entries']=[e for e in d['entries']if(e['source_identity'],e['sample_state_id'],e['reviewed_measurement_fingerprint'])in keys];return d
class ScopeScientificGates(unittest.TestCase):
 def test_keywords_alone_are_not_admissions(self):
  d=subset([]);accepted,report=scope.classify([COTTON[0]],d)
  self.assertEqual(accepted,[]);self.assertEqual(report['pending_scope_sample_states'],1)
 def test_two_TG_atmospheres_count_one_state(self):
  self.assertEqual(len(COTTON),2);accepted,report=scope.classify(COTTON,subset(COTTON))
  self.assertEqual((report['verified_textile_sample_states'],len(accepted)),(1,2))
 def test_reviewed_glass_fabric_epoxy_counts_one_state_two_TG(self):
  self.assertEqual(len(GLASS_EP),2)
  d=subset(GLASS_EP);self.assertEqual({e['scope_class']for e in d['entries']},{'textile_composite'})
  accepted,report=scope.classify(GLASS_EP,d)
  self.assertEqual((report['verified_textile_sample_states'],len(accepted)),(1,2))
  self.assertIn('textile_composite',scope.pairing.MATERIAL_SCOPE_CLASSES)
 def test_textile_composite_keywords_without_review_are_not_admissions(self):
  accepted,report=scope.classify(GLASS_EP,subset([]))
  self.assertEqual((len(accepted),report['pending_scope_sample_states']),(0,1))
  d=subset(GLASS_EP);d['entries'][0]['scope_reviewed_by']=''
  with self.assertRaisesRegex(ValueError,'Missing textile-scope evidence'):scope.classify(GLASS_EP,d)
 def test_textile_composite_form_or_chemistry_change_invalidates_review(self):
  for changed in [{'material_form_TGA':'nonwoven glass felt/epoxy laminate','material_form_LOI':'nonwoven glass felt/epoxy laminate'},
                  {'composition':'six-ply woven glass/polyester laminate'}]:
   with self.subTest(changed=changed):
    with self.assertRaisesRegex(ValueError,'Stale textile-scope material'):
     scope.classify([dict(GLASS_EP[0],**changed)],subset([GLASS_EP[0]]))
 def test_previous_paper_exclusion_requires_expanded_scope_reassessment(self):
  d=subset([PAPER]);d['entries'][0].update(decision='hold_scope',scope_class='paper_sheet')
  accepted,report=scope.classify([PAPER],d)
  self.assertEqual((len(accepted),report['excluded_non_textile_sample_states'],report['pending_scope_sample_states']),(0,0,1))
  d['entries'][0]['decision']='admit_textile'
  with self.assertRaisesRegex(ValueError,'Non-textile class'):scope.classify([PAPER],d)
 def test_same_numbers_do_not_authorize_cloth_to_fibre_substitution(self):
  r=dict(COTTON[0],material_form_TGA='isolated cotton fibers',material_form_LOI='isolated cotton fibers')
  self.assertEqual(scope.observation_key(r),scope.observation_key(COTTON[0]))
  with self.assertRaisesRegex(ValueError,'Stale textile-scope material'):scope.classify([r],subset([COTTON[0]]))
 def test_composition_change_needs_new_scope_review(self):
  r=dict(COTTON[0],composition='dispersed cotton fibre in injection-moulded engineering plastic')
  with self.assertRaisesRegex(ValueError,'Stale textile-scope material'):scope.classify([r],subset([COTTON[0]]))
 def test_preparation_change_needs_new_scope_review(self):
  r=dict(COTTON[0],source_preparation='dispersed fibres in an injection-moulded resin plaque')
  with self.assertRaisesRegex(ValueError,'Stale textile-scope material'):scope.classify([r],subset([COTTON[0]]))
 def test_new_wash_state_cannot_reuse_old_binding(self):
  r=dict(COTTON[0],washing_state='washed20cycles');r['reviewed_measurement_fingerprint']=scope.pairing.measurement_fingerprint(r)
  with self.assertRaisesRegex(ValueError,'absent from'):scope.classify([r],subset([COTTON[0]]))
 def test_duplicate_missing_and_conflicting_scope_evidence_fail(self):
  d=subset(COTTON);d['entries'].append(copy.deepcopy(d['entries'][0]))
  with self.assertRaisesRegex(ValueError,'Duplicate textile-scope'):scope.classify(COTTON,d)
  d=subset(COTTON);d['entries'][0]['scope_evidence']=''
  with self.assertRaisesRegex(ValueError,'Missing textile-scope'):scope.classify(COTTON,d)
  d=subset(COTTON);d['entries'][1]['decision']='exclude_non_textile'
  with self.assertRaisesRegex(ValueError,'Conflicting textile-scope'):scope.classify(COTTON,d)
 def test_partial_or_curve_only_numeric_evidence_is_not_exported(self):
  for changed in [{'pairing_status':'pending_source_review'},{'numeric_evidence_type':'curve_estimate'}]:
   with self.assertRaisesRegex(ValueError,'evidence-reviewed master'):scope.classify([dict(COTTON[0],**changed)],subset([COTTON[0]]))
 def test_material_class_cannot_change_between_TG_conditions(self):
  d=subset(COTTON);d['entries'][1]['scope_class']='fiber_forming_polymer'
  with self.assertRaisesRegex(ValueError,'Conflicting material classes'):scope.classify(COTTON,d)
 def test_identity_fields_cannot_be_reduced_to_pass(self):
  d=subset(COTTON);d['scope_identity_fields'].remove('material_form_TGA')
  with self.assertRaisesRegex(ValueError,'identity fields'):scope.classify(COTTON,d)
if __name__=='__main__':unittest.main()
