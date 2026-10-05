"""Scientific regressions for threshold identity, formulation borrowing and cloth controls."""
import csv,json,sys,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));import pairing
with(R/'data/incoming/verified_source_batch_20261005_b310_local_textile.csv').open(newline='')as f:ROWS=list(csv.DictReader(f))
class CottonScientificBoundaries(unittest.TestCase):
 def test_higher_POSS_loadings_cannot_inherit_baseline_TG(self):
  baseline=next(r for r in ROWS if r['source_sample_label']=='Cotton + E + 1%POSS')
  for held in [r for r in ROWS if r['pairing_status']=='LOI_only_TG_unreported']:
   self.assertTrue(pairing.evidence_issues(held));self.assertEqual(held['LOI_pct'],'21');self.assertFalse(any(held.get(k)for k in pairing.TG_FIELDS))
   borrowed=dict(baseline,sample_state=held['sample_state'],composition=held['composition'],LOI_pct='21')
   self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(borrowed))
 def test_source_five_percent_threshold_is_not_generic_onset(self):
  r=next(r for r in ROWS if r['source_sample_label']=='Cotton')
  self.assertEqual(r['T5_C'],'274');self.assertFalse(r['Tonset_C']);self.assertFalse(r['R800_pct']);self.assertFalse(r['residue_pct']);self.assertFalse(r['residue_temp_C'])
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,Tonset_C=r['T5_C'],T5_C='')))
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,R800_pct='0')))
 def test_fabric_gas_and_wash_substitutions_invalidate_review(self):
  for r in [r for r in ROWS if r['pairing_status']=='verified_exact']:
   self.assertFalse(pairing.evidence_issues(r));self.assertEqual(r['atmosphere'],'air')
   self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,atmosphere='N2')))
   self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,washing_state='after20launderings')))
   self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='isolated cotton fibers')))
 def test_distinct_commercial_FR_control_is_not_relabelled_214gsm(self):
  r=next(r for r in ROWS if r['source_sample_label']=='Cotton + FR')
  self.assertIn('210g/m2',r['material_form_TGA']);self.assertIn('13wt%',r['composition']);self.assertIn('usedasreceived',r['source_preparation'])
  self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='plain-weave cotton textile fabric214g/m2')))
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,sample_state='Cotton_initial_214gsm')))
if __name__=='__main__':unittest.main()
