"""Protect final fiber doses, test-specific conditions and source-bound measurements."""
import csv,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if not (ROOT/'scripts/pairing.py').exists(): ROOT=ROOT/'repo'
sys.path.insert(0,str(ROOT/'scripts')); import pairing
def facts():
    p=ROOT/'data/incoming/verified_source_batch_20261004_b205_local_textile.csv'
    if not p.exists(): p=ROOT.parent/'work/staged-local-textile-b205/publication_proposed.csv'
    with p.open(newline='') as f: return list(csv.DictReader(f))
class NativePLAFiberEvidence(unittest.TestCase):
    def test_final_fiber_doses_are_not_masterbatch_doses(self):
        self.assertEqual([r['source_nominal_OP_wt_pct'] for r in facts()],['0','6','8','10'])
        self.assertEqual([r['source_spinneret_temperature_C'] for r in facts()],['240','227','225','223'])
    def test_neat_additive_is_not_a_fifth_paired_textile(self):
        rows=facts(); self.assertEqual(len(rows),4)
        self.assertTrue(all(r['source_nominal_OP_wt_pct']!='100' and r['source_neat_OP_R700_pct']=='26.50' and r['R700_pct']!='26.50' for r in rows))
    def test_threshold_and_endpoint_preserve_own_definitions(self):
        self.assertEqual([r['T5_C'] for r in facts()],['324.5','317.1','310.2','312.4'])
        self.assertTrue(all(not r.get('Tonset_C') and not r.get('T10_C') and r['residue_temp_C']=='700' for r in facts()))
    def test_room_temperature_and_PyGC_conditions_not_inferred(self):
        self.assertTrue(all(not r.get('TG_start_C') and r['atmosphere']=='air' and r['heating_rate_C_min']=='10' and not r.get('gas_flow_mL_min') and not r.get('LOI_replicates') for r in facts()))
    def test_changed_dose_metrics_or_washing_require_review(self):
        r=facts()[3]; self.assertFalse(pairing.evidence_issues(r))
        for k,v in [('T5_C','368.3'),('R700_pct','26.50'),('LOI_pct','27.2'),('washing_state','after_20_washes')]:
            self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**{k:v})))
    def test_fiber_fabric_mixing_or_curve_estimate_rejected(self):
        r=facts()[0]
        self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_LOI='woven PLA fabric')))
        self.assertIn('numeric_evidence_review_pending',pairing.evidence_issues(dict(r,numeric_evidence_type='curve_estimate')))
if __name__=='__main__': unittest.main()
