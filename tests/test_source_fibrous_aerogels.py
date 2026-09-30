import csv
import unittest
from pathlib import Path

import pandas as pd

from scripts import pairing
from scripts import validate_tg_loi as v


ROOT = Path(__file__).resolve().parents[1]


class FibrousAerogelSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / 'data/incoming/verified_source_batch_20261001_b65.csv').open(newline='') as f:
            cls.rows = list(csv.DictReader(f))

    def test_source_definition_conflict_does_not_become_t5_or_scan_endpoint(self):
        rows = [r for r in self.rows if r['DOI'] == '10.1007/s40820-025-01728-x']
        master, _, _, report = v.build_tables(pd.DataFrame(rows))
        self.assertEqual(report['verified_exact_sample_states'], 2)
        self.assertEqual(set(master['R800_pct'].map(float)), {33.57, 36.92})
        self.assertEqual(set(master['residue_temp_C'].map(float)), {800})
        for row in master.to_dict('records'):
            self.assertFalse(row.get('T5_C', ''))
            self.assertFalse(row.get('Tonset_C', ''))
            self.assertFalse(row.get('TG_end_C', ''))
            self.assertIn('95%weight loss', row['source_Ti_definition'])

    def test_shell_tg_cannot_pair_with_completed_coaxial_fiber_loi(self):
        row = next(r for r in self.rows if r['DOI'] == '10.1007/s40820-023-01200-8')
        master, _, _, report = v.build_tables(pd.DataFrame([row]))
        self.assertEqual(report['verified_exact_sample_states'], 1)
        self.assertEqual(float(master.iloc[0]['residue_pct']), 58.5)
        self.assertFalse(master.iloc[0].get('residue_temp_C', ''))
        self.assertFalse(master.iloc[0].get('R800_pct', ''))
        self.assertFalse(master.iloc[0].get('Tmax1_C', ''))
        mixed = dict(row, material_form_LOI='completed coaxial core-shell thermoelectric fiber')
        mixed['reviewed_measurement_fingerprint'] = pairing.measurement_fingerprint(mixed)
        master, _, quarantine, report = v.build_tables(pd.DataFrame([mixed]))
        self.assertTrue(master.empty)
        self.assertFalse(quarantine.empty)
        self.assertEqual(report['verified_exact_sample_states'], 0)


if __name__ == '__main__':
    unittest.main()
