"""Protect source metric definitions, missing/conflicting LOI and specimen identity."""
import csv
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if not (ROOT / 'scripts/pairing.py').exists():
    ROOT = Path(__file__).resolve().parent.parent / 'repo'
sys.path.insert(0, str(ROOT / 'scripts'))
import pairing

def rows():
    path = ROOT / 'data/incoming/verified_source_batch_20261005_b304_local_textile.csv'
    if not path.exists():
        path = Path(__file__).resolve().parent / 'staged-local-textile-b304/publication_proposed.csv'
    with path.open(newline='') as handle:
        return list(csv.DictReader(handle))

class CottonIonicLiquidEvidenceBoundaries(unittest.TestCase):
    def test_conflicting_and_missing_LOI_are_not_verified(self):
        data = rows()
        held = {r['sample_state'].split('_initial')[0]: r for r in data if r['direct_numeric_use'] != 'yes'}
        self.assertEqual(set(held), {'MCPTS_Cl', 'MCPTS_BF4', 'PCPTS_BF4'})
        self.assertEqual(held['MCPTS_Cl']['LOI_pct'], '23.33')
        self.assertEqual(held['MCPTS_Cl']['source_body_LOI_alternate_percent'], '23.0')
        for name, r in held.items():
            self.assertNotEqual(r['pairing_status'], 'verified_exact')
            self.assertTrue(pairing.evidence_issues(r))
            self.assertFalse(r.get('reviewed_measurement_fingerprint'))
            if name.endswith('BF4'):
                self.assertFalse(r['LOI_pct'])

    def test_T10_and_R600_cannot_be_replaced_by_onset_or_end_temperature(self):
        for r in rows():
            self.assertFalse(r['T5_C'])
            self.assertFalse(r['Tonset_C'])
            self.assertEqual(r['residue_temp_C'], '600')
            self.assertEqual(r['residue_pct'], r['R600_pct'])
            self.assertEqual(r['TG_end_C'], '800')
            if r['pairing_status'] == 'verified_exact':
                self.assertFalse(pairing.evidence_issues(r))
                for changed in [dict(r, T10_C='', Tonset_C=r['T10_C']),
                                dict(r, residue_temp_C='800'),
                                dict(r, Tmax2_C='100')]:
                    self.assertIn('measurement_review_pending_or_stale', pairing.evidence_issues(changed))

    def test_fabric_state_and_TG_methods_are_not_replaced_by_MCC(self):
        accepted = [r for r in rows() if r['pairing_status'] == 'verified_exact']
        self.assertEqual(len({pairing.sample_state_id(r) for r in accepted}), 8)
        for r in accepted:
            self.assertIn('cotton textile fabric', r['material_form_TGA'])
            self.assertEqual(r['material_form_TGA'], r['material_form_LOI'])
            self.assertEqual(r['source_textile_scope_status'], 'source_confirmed_textile_fabric')
            self.assertEqual(r['heating_rate_C_min'], '10')
            self.assertEqual(r['TGA_gas_flow_ml_min'], '25')
            self.assertFalse(r['TGA_mass_mg'])
            self.assertFalse(r['TGA_replicates'])
            self.assertFalse(r['LOI_replicates'])
            self.assertIn('specimen_form_mismatch', pairing.evidence_issues(dict(r, material_form_TGA='isolated cotton fibers')))
            self.assertIn('measurement_review_pending_or_stale', pairing.evidence_issues(dict(r, washing_state='washed_20_cycles')))
            self.assertIn('measurement_review_pending_or_stale', pairing.evidence_issues(dict(r, heating_rate_C_min='60')))

if __name__ == '__main__':
    unittest.main()
