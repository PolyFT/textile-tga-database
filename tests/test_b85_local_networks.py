"""Guard original-source disagreements, curve-only facts and native assay definitions."""
import csv
import sys
import unittest
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import pairing
import validate_tg_loi as validator


class CottonNetworkEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / 'data/incoming/verified_source_batch_20261001_b85_local_networks.csv').open(newline='') as handle:
            cls.rows = list(csv.DictReader(handle))

    def source(self, suffix):
        return [r for r in self.rows if r['DOI'].endswith(suffix)]

    def test_counts_exclude_conflicts_and_curve_only_samples(self):
        report = validator.build_tables(pd.DataFrame(self.rows).fillna(''), validator.issue_list())[3]
        self.assertEqual(report['errors'], [])
        self.assertEqual(len(self.rows), 25)
        self.assertEqual(report['verified_exact_sample_states'], 11)
        self.assertEqual(report['verified_exact_condition_records'], 14)

    def test_hpae_conflicts_and_missing_air_char_are_not_filled(self):
        rows = self.source('03645-1')
        for row in rows:
            if row['sample_state'] == 'Control cotton':
                self.assertEqual(float(row['LOI_pct']), 18)
                if row['atmosphere'] == 'air':
                    self.assertEqual(row['R800_pct'], '')
                    self.assertEqual(row['residue_pct'], '')
            else:
                self.assertEqual(row['LOI_pct'], '')
                self.assertEqual(float(row['source_LOI_initial_prose_or_SI_pct']), 28.7)
                self.assertNotEqual(row['pairing_status'], 'verified_exact')
                self.assertEqual(row['reviewed_measurement_fingerprint'], '')

    def test_tiapc_figure_loi_does_not_create_numeric_tg(self):
        expected = {'Control cotton': 18.0, 'Cotton-TIAPC': 19.3, 'Cotton-TIAPC-Cl': 20.4,
                    'Cotton-TIAPC-Al': 21.3, 'Cotton-TIAPC-Cl-Al': 20.7}
        for row in self.source('03716-x'):
            self.assertEqual(float(row['LOI_pct']), expected[row['sample_state']])
            self.assertEqual(row['LOI_specimen_size_mm'], '150x98')
            for field in ['T5_C', 'Tonset_C', 'Tmax1_C', 'R800_pct', 'residue_pct', 'TG_start_C']:
                self.assertEqual(row.get(field, ''), '')
            self.assertNotEqual(row['pairing_status'], 'verified_exact')

    def test_apppda_native_onset_means_t5_and_ddm_state_is_held(self):
        for row in self.source('02586-8'):
            self.assertEqual(float(row['T5_C']), float(row['source_Tonset_header_value_C']))
            self.assertEqual(row.get('Tonset_C', ''), '')
            self.assertEqual(float(row['heating_rate_C_min']), 20)
            self.assertEqual(float(row['residue_temp_C']), 800)
            if row['sample_state'] == 'APP@PDA-cot':
                self.assertNotEqual(row['pairing_status'], 'verified_exact')
                self.assertEqual(row['reviewed_measurement_fingerprint'], '')

    def test_petp_native_flow_preconditioning_and_char_boundary(self):
        expected = {'Control': 9.4, 'Cotton-P10T1': 30.2, 'Cotton-P10T5': 36.7, 'Cotton-P10T10': 37.6}
        for row in self.source('03874-y'):
            self.assertEqual(float(row['R700_pct']), expected[row['sample_state']])
            self.assertIn('60mL/s', row['TGA_purge_flow_reported'])
            self.assertIn('Preheat100C', row['TGA_preconditioning'])
            self.assertEqual(row.get('TGA_sample_mass_mg_reported', ''), '')
            self.assertEqual(float(row['heating_rate_C_min']), 10)
            self.assertNotIn('1X', row['sample_state'])
            self.assertNotIn('2X', row['sample_state'])

    def test_peip_regular_tg_mass_and_initial_washed_boundary(self):
        expected = {'Cotton-0': (18.1, 1.6), 'Cotton-1': (31.4, 21.4),
                    'Cotton-2': (35.8, 26.8), 'Cotton-3': (38.7, 34.2)}
        for row in self.source('03980-x'):
            loi, char = expected[row['sample_state']]
            self.assertEqual(float(row['LOI_pct']), loi)
            self.assertEqual(float(row['R700_pct']), char)
            self.assertEqual(float(row['TGA_sample_mass_mg_reported']), 5)
            self.assertEqual(float(row['TG_start_C']), 30)
            self.assertIn('Initial0LCs', row['washing_state'])

    def test_changed_values_conditions_and_wash_require_new_review(self):
        row = next(r for r in self.rows if r['pairing_status'] == 'verified_exact')
        for field, value in [('LOI_pct', 1), ('heating_rate_C_min', 99), ('washing_state', 'after100LCs')]:
            changed = dict(row, **{field: value})
            self.assertNotEqual(pairing.measurement_fingerprint(changed), row['reviewed_measurement_fingerprint'])
            self.assertTrue(pairing.evidence_issues(changed))


if __name__ == '__main__':
    unittest.main()
