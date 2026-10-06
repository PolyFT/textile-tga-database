import csv
import unittest
from pathlib import Path

from scripts import pairing as p


ROOT = Path(__file__).resolve().parents[1]


class LaminateSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / 'data/incoming/verified_source_batch_20261001_b58.csv').open(newline='') as f:
            cls.rows = list(csv.DictReader(f))
        with (ROOT / 'data/curation/archive/source_review_condition_partial_20261001_b58.csv').open(newline='') as f:
            cls.partial = list(csv.DictReader(f))

    def test_same_fabric_table_pairs_and_reviewed_measurements(self):
        expected = {
            'Flax/VE': (19.4, 'Tonset_C', 352, 'n2', 10),
            '5M-flax/VE': (23.6, 'Tonset_C', 348, 'n2', 10),
            '10M-flax/VE': (24.9, 'Tonset_C', 345, 'n2', 10),
            'GFRER': (22.4, 'Tmax1_C', 412, 'helium', 30),
            'GFRER + 6% graphene': (23.9, 'Tmax1_C', 411, 'helium', 30),
            'GFRER + 6% DDM-DOPO': (26.5, 'Tmax1_C', 407, 'helium', 30),
        }
        self.assertEqual(len(self.rows), len(expected))
        for row in self.rows:
            with self.subTest(sample=row['sample_state']):
                loi, field, temperature, gas, rate = expected[row['sample_state']]
                self.assertEqual(float(row['LOI_pct']), loi)
                self.assertEqual(float(row[field]), temperature)
                self.assertEqual(p.normalized_atmosphere(row['atmosphere']), gas)
                self.assertEqual(float(row['heating_rate_C_min']), rate)
                self.assertEqual(row['material_form_TGA'], row['material_form_LOI'])
                self.assertEqual(row['reviewed_measurement_fingerprint'], p.measurement_fingerprint(row))

    def test_flax_endpoint_conflict_cannot_create_fixed_temperature_residue(self):
        for row in self.rows:
            if row['DOI'] == '10.1371/journal.pone.0319421':
                self.assertTrue(row['residue_pct'])
                self.assertFalse(row['residue_temp_C'])
                for field in ['R600_pct', 'R800_pct', 'T5_C', 'T10_C']:
                    self.assertFalse(row.get(field))
                self.assertEqual(row['LOI_method_reported'], 'ASTM D2893')
                self.assertIn('600C', row['TG_endpoint_limitation'])
            else:
                self.assertFalse(row['residue_pct'])
                self.assertFalse(row.get('LOI_uncertainty_pct'))

    def test_felt_conditions_and_conflicting_cfrp_facts_remain_unapproved(self):
        self.assertEqual(len(self.partial), 18)
        felt = [r for r in self.partial if r['DOI'] == '10.3390/polym15081920']
        self.assertEqual(len(felt), 12)
        self.assertEqual(len({r['sample_state'] for r in felt}), 6)
        self.assertEqual({r['atmosphere'] for r in felt}, {'N2', 'air'})
        for row in self.partial:
            self.assertEqual(row['direct_numeric_use'], 'no')
            self.assertNotEqual(row['pairing_status'], 'verified_exact')
        for row in felt:
            self.assertFalse(row['heating_rate_C_min'])
            self.assertTrue(row['R700_pct'])
            if row['sample_state'] == 'FNFs-5':
                self.assertFalse(row['LOI_pct'])


if __name__ == '__main__':
    unittest.main()
