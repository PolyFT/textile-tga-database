import csv
import unittest
from pathlib import Path

import pandas as pd

from scripts import validate_tg_loi as v


ROOT = Path(__file__).resolve().parents[1]


class AramidBmiSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / 'data/incoming/verified_source_batch_20261001_b60.csv').open(newline='') as f:
            cls.rows = list(csv.DictReader(f))
        with (ROOT / 'data/curation/source_review_additional_LOI_conditions_20261001_b60.csv').open(newline='') as f:
            cls.hot_loi = list(csv.DictReader(f))

    def test_five_ramps_do_not_inflate_independent_sample_count(self):
        master, _, _, report = v.build_tables(pd.DataFrame(self.rows))
        self.assertEqual(len(master), 8)
        self.assertEqual(report['verified_exact_sample_states'], 4)
        glass = [r for r in self.rows if r['DOI'] == '10.3390/polym15102275']
        self.assertEqual({float(r['heating_rate_C_min']) for r in glass}, {5, 10, 20, 30, 40})
        self.assertEqual(len({r['sample_state'] for r in glass}), 1)
        for row in glass:
            self.assertEqual(float(row['LOI_pct']), 47.8)
            self.assertEqual(float(row['LOI_test_temperature_C']), 20)
            self.assertFalse(row['T5_C'])
            self.assertFalse(row['R700_pct'])
            self.assertFalse(row.get('residue_pct'))

    def test_matrix_and_fiber_peaks_and_explicit_residue_stay_separate(self):
        aramid = [r for r in self.rows if r['DOI'] == '10.3390/ma17164028']
        self.assertEqual(len(aramid), 3)
        for row in aramid:
            self.assertTrue(row['T5_C'])
            self.assertFalse(row['Tonset_C'])
            self.assertLess(float(row['Tmax1_C']), float(row['Tmax2_C']))
            self.assertTrue(row['R700_pct'])
            self.assertIn('TableS1', row['TG_locator'])
            self.assertEqual(row['material_form_TGA'], row['material_form_LOI'])

    def test_hot_loi_is_assay_temperature_not_four_new_materials(self):
        self.assertEqual(len(self.hot_loi), 4)
        self.assertEqual(len({r['sample_state'] for r in self.hot_loi}), 1)
        self.assertEqual({float(r['LOI_test_temperature_C']) for r in self.hot_loi}, {50, 100, 150, 220})
        for row in self.hot_loi:
            self.assertEqual(row['direct_numeric_use'], 'no')
            self.assertNotEqual(row['pairing_status'], 'verified_exact')
            self.assertFalse(row.get('Tmax1_C'))


if __name__ == '__main__':
    unittest.main()
