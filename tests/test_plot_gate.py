import argparse
import unittest
from scripts.plot_scatter import select_rows, to_float
from scripts.pairing import measurement_fingerprint


class PlotGateTests(unittest.TestCase):
    def args(self, **values):
        base = dict(exploratory=False, atmosphere=None, heating_rate=None, material=None,
                    dataset=None, x='Tmax1_C', y='LOI_pct')
        base.update(values)
        return argparse.Namespace(**base)

    def test_legacy_a_label_alone_is_not_scientific_admission(self):
        row = dict(pair_quality='A', Tmax1_C='300', LOI_pct='25')
        self.assertEqual(select_rows([row], self.args()), [])
        self.assertEqual(len(select_rows([row], self.args(exploratory=True))), 1)

    def test_nonfinite_points_are_rejected(self):
        self.assertIsNone(to_float('nan'))
        self.assertIsNone(to_float('inf'))

    def test_reviewed_row_and_condition_filter(self):
        row = dict(DOI='10.1234/test', sample_state='A', atmosphere='N2', heating_rate_C_min='10',
                   Tmax1_C='300', LOI_pct='25', pair_quality='A', pairing_status='verified_exact',
                   pairing_evidence='Tables 1 and 2 same unwashed woven fabric', material_form_TGA='woven fabric',
                   material_form_LOI='woven fabric', numeric_evidence_type='tabulated',
                   evidence_reviewed_by='fixture reviewer', source_url='https://example.org', source_location='Tables 1 and 2')
        row['reviewed_measurement_fingerprint'] = measurement_fingerprint(row)
        self.assertEqual(len(select_rows([row], self.args(heating_rate=10))), 1)
        self.assertEqual(select_rows([row], self.args(heating_rate=20)), [])
        row['LOI_pct'] = '30'
        self.assertEqual(select_rows([row], self.args()), [])


if __name__ == '__main__':
    unittest.main()
