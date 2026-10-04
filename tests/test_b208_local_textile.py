"""Keep own SI LOI, ordinary gas records and washed/dose exclusions separate."""
import csv,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if not(ROOT/'scripts/pairing.py').exists():ROOT=ROOT/'repo'
sys.path.insert(0,str(ROOT/'scripts'));import pairing
def facts():
    p=ROOT/'data/incoming/verified_source_batch_20261004_b208_local_textile.csv'
    if not p.exists():p=ROOT.parent/'work/staged-local-textile-b208/publication_proposed.csv'
    with p.open(newline='')as f:return list(csv.DictReader(f))
class NativeCottonPAODATiO2(unittest.TestCase):
    def test_four_initial_states_eight_gas_records(self):
        a=[r for r in facts()if r['pairing_status']=='verified_exact'];self.assertEqual(len(a),8);self.assertEqual(len({r['sample_state']for r in a}),4)
        self.assertEqual({r['source_sample_label']:r['LOI_pct']for r in a},{'CO':'18.0','P-CO':'45.0','PO-CO':'45.5','POT-CO-5':'48.5'})
    def test_LOI_own_geometry_repeats_and_TG_ramp(self):
        a=[r for r in facts()if r['pairing_status']=='verified_exact'];self.assertTrue(all(r['LOI_replicates']=='5'and r['source_LOI_geometry']=='150mmx58mm'and r['heating_rate_C_min']=='10'and not r.get('gas_flow_mL_min')for r in a))
    def test_native_gas_residue_anomaly_not_corrected(self):
        a={r['atmosphere']:r for r in facts()if r['source_sample_label']=='CO'};self.assertEqual((a['air']['R800_pct'],a['N2']['R800_pct']),('10.3','0.9'))
    def test_T10_not_T5_or_Tonset(self):
        self.assertTrue(all(not r.get('T5_C')and not r.get('Tonset_C')for r in facts()))
    def test_washed_lower_bound_not_exact_or_initial_TG(self):
        r=next(r for r in facts()if r['washing_state']=='after20_domestic_equivalent_washes');self.assertEqual((r['LOI_pct'],r['source_LOI_lower_bound_pct'],r['source_LOI_relation']),('','36.2','greater_than'));self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS));self.assertEqual(r['direct_numeric_use'],'no')
    def test_other_doses_and_formulations_do_not_borrow_TG(self):
        held=[r for r in facts()if r['pairing_status']!='verified_exact'];self.assertEqual(len(held),6);self.assertTrue(all(not r.get(k)for r in held for k in pairing.TG_FIELDS))
    def test_changed_metrics_or_state_invalidate_review(self):
        r=next(r for r in facts()if r['source_sample_label']=='POT-CO-5');self.assertFalse(pairing.evidence_issues(r))
        for k,v in [('LOI_pct','45.0'),('T10_C','243.5'),('R800_pct','34.2'),('washing_state','after20_domestic_equivalent_washes')]:self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**{k:v})))
if __name__=='__main__':unittest.main()
