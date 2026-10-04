"""Protect source-defined thresholds, sample states and unknown conditions."""
import csv,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if not(ROOT/'scripts/pairing.py').exists():ROOT=ROOT/'repo'
sys.path.insert(0,str(ROOT/'scripts'));import pairing
def facts():
 p=ROOT/'data/incoming/verified_source_batch_20261004_b201_local_textile.csv'
 if not p.exists():p=ROOT.parent/'work/staged-local-textile-b201/publication_proposed.csv'
 with p.open(newline='')as f:return list(csv.DictReader(f))
class NativeCottonCoatingEvidence(unittest.TestCase):
 def test_defined_five_percent_is_not_tangent_onset(self):
  r=facts();self.assertEqual([x['T5_C']for x in r],['315','276','258']);self.assertTrue(all(not x.get('Tonset_C')and not x.get('T10_C')for x in r))
 def test_hydrophobic_state_keeps_own_TG_and_LOI(self):
  r=facts()[2];self.assertEqual((r['source_sample_label'],r['Tmax1_C'],r['R600_pct'],r['LOI_pct']),('Cotton/SiO2-PEI/PPA/REPELLAN FF','307','41','28.2'))
 def test_unreported_bilayers_and_final_cure_not_invented(self):
  self.assertTrue(all(r['source_bilayer_count']=='Unreported'and r['source_final_Repellan_cure_temperature_time']=='Unreported'for r in facts()))
 def test_addon_basis_and_LOI_geometry_not_borrowed(self):
  self.assertTrue(all(not r.get('weight_gain_pct')and not r.get('LOI_replicates')and r['source_LOI_dimensions_replicates_conditioning'].startswith('Unreported')for r in facts()))
 def test_changes_in_measurements_or_washing_invalidate_review(self):
  r=facts()[2]
  for k,v in [('T5_C','276'),('R600_pct','44'),('LOI_pct','29.6'),('washing_state','after_20_washes')]:self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**{k:v})))
 def test_fiber_fabric_mixing_and_curve_estimates_rejected(self):
  r=facts()[0];self.assertFalse(pairing.evidence_issues(r));self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='cotton fibers')));self.assertIn('numeric_evidence_review_pending',pairing.evidence_issues(dict(r,numeric_evidence_type='curve_estimate')))
if __name__=='__main__':unittest.main()
