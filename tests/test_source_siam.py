import csv
import unittest
from pathlib import Path

import pandas as pd

from scripts import pairing
from scripts import validate_tg_loi as v


ROOT = Path(__file__).resolve().parents[1]


class SiamSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / 'data/incoming/verified_source_batch_20261001_b63.csv').open(newline='') as f:
            cls.row = next(csv.DictReader(f))

    def test_scan_endpoint_does_not_assign_generic_residue_temperature(self):
        master, _, _, report = v.build_tables(pd.DataFrame([self.row]))
        self.assertEqual(report['verified_exact_sample_states'], 1)
        self.assertEqual(float(master.iloc[0]['residue_pct']), 56.12)
        self.assertFalse(master.iloc[0].get('residue_temperature_C', ''))
        self.assertFalse(master.iloc[0].get('R800_pct', ''))
        self.assertFalse(master.iloc[0].get('Tmax1_C', ''))
        self.assertEqual(float(master.iloc[0]['TG_end_C']), 800)

    def test_missing_tg_gas_stays_unpairable_after_fingerprint_refresh(self):
        row = dict(self.row, atmosphere='')
        row['reviewed_measurement_fingerprint'] = pairing.measurement_fingerprint(row)
        master, _, _, report = v.build_tables(pd.DataFrame([row]))
        self.assertTrue(master.empty)
        self.assertEqual(report['verified_exact_sample_states'], 0)


if __name__ == '__main__':
    unittest.main()
