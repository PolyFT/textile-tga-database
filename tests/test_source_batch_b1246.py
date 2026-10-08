"""Protect source definitions, shared controls and visible LOI uncertainty."""
import csv
import json
import re
import unittest
from pathlib import Path

from scripts import pairing


ROOT = Path(__file__).resolve().parents[1]


class SourceBatchB1246Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = ROOT / 'data/incoming/verified_source_batch_20261008_b1246_polymers.csv'
        with path.open(newline='') as handle:
            cls.rows = list(csv.DictReader(handle))
        cls.by_source_key = {r['source_observation_key']: r for r in cls.rows}

    def test_shared_and_unresolved_controls_are_not_recounted(self):
        withheld = {'B1183-S01-R001', 'B1183-S01-R008',
                    'B1183-S05-R001', 'B1183-S05-R004',
                    'B1183-S06-R001', 'B1183-S06-R007',
                    'B1193-S03-R001', 'B1193-S03-R003', 'B1193-S03-R006',
                    'B1203-S03-R001'}
        self.assertTrue(withheld.isdisjoint(self.by_source_key))
        self.assertEqual(len(self.rows), 57)
        self.assertEqual(len({pairing.sample_state_id(r) for r in self.rows}), 45)
        for first, second in [('B1193-S01-R001', 'B1193-S01-R002'),
                              ('B1183-S01-R002', 'B1183-S01-R009')]:
            a, b = self.by_source_key[first], self.by_source_key[second]
            self.assertEqual(pairing.sample_state_id(a), pairing.sample_state_id(b))
            self.assertNotEqual(pairing.pair_key(a), pairing.pair_key(b))

    def test_source_defined_thresholds_and_conflicts(self):
        row = self.by_source_key['B1193-S01-R006']
        self.assertEqual((row['T1_C'], row['T5_C'], row['T10_C']), ('212', '278', '288'))
        self.assertEqual(row.get('T50_C', ''), '')
        raw = json.loads(row['source_metrics_json'])
        self.assertIn('358', json.dumps(raw))
        self.assertIn('353', json.dumps(raw))
        row = self.by_source_key['B1203-S05-R001']
        self.assertEqual((row['T10_C'], row['T50_C'], row['R600_pct']), ('431', '456', '0'))
        self.assertEqual(row.get('T1_C', ''), '')

    def test_unnumbered_peak_and_original_rate_unit_remain_distinct(self):
        row = self.by_source_key['B1183-S01-R002']
        self.assertEqual(row['T5_C'], '274.4')
        self.assertEqual(row['Tmax_unnumbered_C'], '399.6')
        self.assertEqual(row.get('Tmax1_C', ''), '')
        self.assertIn('%/C', row['source_original_TG_details_note'])
        self.assertEqual(row.get('max_mass_loss_rate', ''), '')

    def test_all_six_original_plusminus_literals_are_visible(self):
        expected = {'B1203-S03-R013': '29.4 ± 0.2',
                    'B1203-S05-R001': '18.0 ± 0.1',
                    'B1203-S05-R002': '31.1 ± 0.2',
                    'B1203-S05-R003': '32.5 ± 0.2',
                    'B1203-S05-R004': '35.5 ± 0.2',
                    'B1203-S05-R005': '34.5 ± 0.2'}
        html = (ROOT / 'index.html').read_text()
        payload = json.loads(re.findall(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>', html, re.S)[0])
        by_pair = {r[-1]: r for r in payload['rows']}
        for key, literal in expected.items():
            row = self.by_source_key[key]
            self.assertEqual(row['source_LOI_entry_raw'], literal)
            self.assertEqual(row['source_LOI_original'], literal)
            self.assertIn(literal, by_pair[pairing.pair_key(row)][21])


if __name__ == '__main__':
    unittest.main()
