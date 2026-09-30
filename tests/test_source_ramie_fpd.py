import csv
import unittest
from pathlib import Path

import pandas as pd

from scripts import validate_tg_loi as v


ROOT = Path(__file__).resolve().parents[1]


class RamieFpdSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / 'data/incoming/verified_source_batch_20261001_b62.csv').open(newline='') as f:
            cls.rows = list(csv.DictReader(f))

    def test_unresolved_rmax_is_not_promoted_to_a_dtg_temperature(self):
        master, _, _, report = v.build_tables(pd.DataFrame(self.rows))
        self.assertEqual(report['verified_exact_sample_states'], 4)
        self.assertEqual(len(master), 4)
        for row in self.rows:
            self.assertTrue(row['T10_C'])
            self.assertTrue(row['R800_pct'])
            self.assertFalse(row.get('T5_C'))
            self.assertFalse(row.get('Tonset_C'))
            self.assertFalse(row.get('Tmax1_C'))
            self.assertEqual(row['source_Rmax_unit_reported'], '%/C')
            self.assertIn('unresolved', row['source_Rmax_use'])

    def test_final_laminate_protocol_does_not_inherit_intermediate_or_tg_ir(self):
        for row in self.rows:
            self.assertEqual(row['material_form_TGA'], row['material_form_LOI'])
            self.assertIn('twelve-ply', row['material_form_TGA'])
            self.assertEqual(float(row['heating_rate_C_min']), 20)
            self.assertEqual(float(row['gas_flow_mL_min']), 25)
            self.assertEqual(row['atmosphere'], 'N2')
            self.assertIn('thickness unreported', row['LOI_specimen_dimensions_mm'])
            self.assertIn('not reconciled', row['treatment_method'])
            self.assertFalse(row.get('add_on_pct'))


if __name__ == '__main__':
    unittest.main()
