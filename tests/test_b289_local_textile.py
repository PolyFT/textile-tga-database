"""Protect supplementary metric definitions and excluded source conflicts."""
import csv,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if not (ROOT/'scripts/pairing.py').exists():ROOT=Path(__file__).resolve().parent.parent/'repo'
sys.path.insert(0,str(ROOT/'scripts'));import pairing
def rows():
 p=ROOT/'data/incoming/verified_source_batch_20261005_b289_local_textile.csv'
 if not p.exists():p=Path(__file__).resolve().parent/'staged-local-textile-b289/publication_proposed.csv'
 with p.open(newline='') as f:return list(csv.DictReader(f))
class CellulosePaperSupplementaryBoundaries(unittest.TestCase):
 def test_SI_Tonset_is_T10_and_cannot_reuse_generic_onset_review(self):
  for r in rows():
   self.assertTrue(r['T10_C']);self.assertFalse(r['Tonset_C']);self.assertFalse(r['T5_C'])
   self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,T10_C='',Tonset_C=r['T10_C'])))
 def test_conflicting_peak_or_residue_cannot_be_reintroduced_using_old_review(self):
  for r in rows():
   if r['source_sample_label']=='Pure cellulose paper':
    self.assertFalse(r['R800_pct']);self.assertFalse(r['residue_pct']);self.assertEqual(r['source_raw_TableS1_R800_percent'],'17.35');self.assertEqual(r['source_raw_body_control_residue_percent'],'19.63')
    changed=dict(r,R800_pct='17.35',residue_pct='17.35',residue_temp_C='800')
   else:
    self.assertFalse(r['Tmax1_C']);self.assertEqual(r['residue_temp_C'],'800');self.assertTrue(r['source_raw_TableS1_Tmax_C']);self.assertTrue(r['source_raw_body_cellulose_component_peak_C'])
    changed=dict(r,Tmax1_C=r['source_raw_TableS1_Tmax_C'])
   self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(changed))
 def test_final_fiber_paper_form_and_unreported_LOI_method_are_preserved(self):
  data=rows();self.assertEqual(len(data),4);self.assertEqual(len({r['sample_state'] for r in data}),4)
  for r in data:
   self.assertEqual(r['material_form_TGA'],r['material_form_LOI']);self.assertIn('cellulose fibers',r['material_form_TGA']);self.assertFalse(r['LOI_standard']);self.assertFalse(r['LOI_replicates']);self.assertFalse(r['TGA_mass_mg']);self.assertEqual(r['TGA_gas_flow_ml_min'],'50');self.assertEqual(r['heating_rate_C_min'],'10')
   if r['source_sample_label']!='Pure cellulose paper':self.assertEqual(r['LOI_pct'],'99.5');self.assertIn('noinstrumentceilinginferred',r['source_LOI_method_limits'])
   self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,washing_state='washed_after_20_cycles')))
if __name__=='__main__':unittest.main()
