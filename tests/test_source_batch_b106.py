import csv
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from pairing import sample_state_id, evidence_issues, measurement_fingerprint


class B106TextileEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = {}
        for path in ROOT.glob('data/incoming/verified_source_batch_20261001_b106_*.csv'):
            with path.open(newline='') as handle:
                cls.rows[path.stem.split('_b106_', 1)[1]] = list(csv.DictReader(handle))

    def test_unique_states_and_review_binding(self):
        rows = [row for group in self.rows.values() for row in group]
        self.assertEqual((len(rows), len({sample_state_id(row) for row in rows})), (10, 10))
        self.assertEqual(len({row['DOI'] for row in rows}), 3)
        for row in rows:
            self.assertFalse(evidence_issues(row))
            self.assertEqual(row['reviewed_measurement_fingerprint'], measurement_fingerprint(row))

    def test_argon_peaks_exclude_both_conflicted_ddm_states(self):
        rows = {r['source_sample_label']: r for r in self.rows['glass_ddm2023']}
        self.assertEqual(set(rows), {'GFRER', '1.5% graphene', '3% graphene'})
        self.assertEqual([rows[k]['Tmax1_C'] for k in rows], ['442', '442', '448'])
        for row in rows.values():
            self.assertEqual((row['atmosphere'], row['heating_rate_C_min']), ('Ar', '30'))
            self.assertFalse(row['residue_pct'])
            self.assertFalse(row['residue_temp_C'])

    def test_veil_generic_residues_do_not_inherit_scan_endpoint(self):
        rows = {r['source_sample_label']: r for r in self.rows['glass_veil2024']}
        self.assertEqual(set(rows), {'C-N0-D0', 'C-N0-D5', 'C-N2-D3', 'C-N5-D0'})
        self.assertEqual((rows['C-N2-D3']['LOI_pct'], rows['C-N2-D3']['residue_pct']), ('31.6', '60.2'))
        for row in rows.values():
            self.assertEqual(row['TG_end_C'], '800')
            self.assertFalse(row['R800_pct'])
            self.assertFalse(row['residue_temp_C'])
            self.assertFalse(row['Tmax1_C'])

    def test_smpic_explicit_r800_and_conflict_exclusions(self):
        rows = {r['source_sample_label']: r for r in self.rows['smpic2024']}
        self.assertEqual(set(rows), {'SMPIC-10', 'SMPIC-15', 'SMPIC-30'})
        expected = {'SMPIC-10': ('50.5', '69.3'), 'SMPIC-15': ('51.4', '75.7'), 'SMPIC-30': ('57.9', '80.4')}
        for label, row in rows.items():
            self.assertEqual((row['LOI_pct'], row['R800_pct']), expected[label])
            self.assertEqual(row['residue_temp_C'], '800')
            self.assertFalse(row['Tmax1_C'])
            self.assertIn('pure SMPI resin', row['limitations'])


if __name__ == '__main__':
    unittest.main()
