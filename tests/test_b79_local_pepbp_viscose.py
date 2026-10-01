"""Regression protection for source-specific TG/LOI admission boundaries."""
import copy
import csv
import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import pairing
import validate_tg_loi as validator

FILE = ROOT / 'data/incoming/verified_source_batch_20261001_b79_local_pepbp_viscose.csv'


def source_rows(suffix=None):
    with FILE.open(newline='') as handle:
        rows = list(csv.DictReader(handle))
    return [row for row in rows if suffix is None or row['DOI'].endswith(suffix)]


class OriginalSourceBoundaries(unittest.TestCase):
    def test_pepbp_native_addon_and_static_air(self):
        rows = source_rows('2012.07.016')
        self.assertEqual(len(rows), 3)
        self.assertEqual([float(row['LOI_pct']) for row in rows], [19.4, 25.7, 33.8])
        self.assertEqual([float(row['add_on']) for row in rows], [0, 5, 21.2])
        self.assertEqual([float(row['R600_pct']) for row in rows], [1, 4.9, 29.1])
        for row in rows:
            self.assertIn('/Wt', row['add_on_basis'])
            self.assertEqual(row['TG_atmosphere_composition'], 'static air')
            self.assertFalse(row.get('TG_gas_flow_mL_min'))
            self.assertFalse(row.get('T5_C'))
            self.assertFalse(row.get('T10_C'))
            self.assertTrue(row['Tonset_C'])
            self.assertEqual(float(row['residue_temp_C']), 600)
            self.assertIn('30wt%', row['limitations'])
            self.assertFalse(row.get('PEPBP_bath_wt_pct'))

    def test_hptp_tg_peaks_approximate_char_and_unpaired_control(self):
        rows = source_rows('s12221-012-0718-3')
        control = next(row for row in rows if row['sample_state'] == 'FRVF-1')
        self.assertFalse(control['LOI_pct'])
        self.assertNotEqual(control['pairing_status'], 'verified_exact')
        accepted = [row for row in rows if row['LOI_pct']]
        self.assertEqual([float(row['LOI_pct']) for row in accepted], [28.4, 28.6, 34.7])
        self.assertEqual([float(row['Tmax1_C']) for row in accepted], [272, 267, 262])
        for row in accepted:
            self.assertFalse(row['residue_temp_C'])
            self.assertEqual(float(row['source_residue_temperature_approx_C']), 590)
            self.assertFalse(row.get('R600_pct'))
            self.assertFalse(row.get('R800_pct'))
            self.assertEqual(row['atmosphere'], 'air')
            self.assertIn('DSC', row['limitations'])
            self.assertIn('initial', row['washing_state'])
        self.assertFalse(any(row['sample_state'] == 'FRVF-2' for row in rows))

    def test_pmep_unwashed_tg_and_500c_endpoint(self):
        rows = source_rows('s12221-015-1005-x')
        self.assertEqual([float(row['LOI_pct']) for row in rows], [19, 27, 31, 33, 35])
        self.assertEqual([float(row['Tmax1_C']) for row in rows], [324.51, 301.16, 295.87, 294.78, 294.19])
        self.assertEqual([float(row['R500_pct']) for row in rows], [11.346, 28.785, 34.152, 32.582, 35.021])
        control = rows[0]
        self.assertEqual(float(control['source_main_stage_end_table_C']), 338.32)
        self.assertEqual(float(control['source_main_stage_end_prose_C']), 338.33)
        for row in rows:
            self.assertEqual(float(row['residue_temp_C']), 500)
            self.assertFalse(row.get('R800_pct'))
            self.assertEqual(row['atmosphere'], 'nitrogen')
            self.assertEqual(row['rate_unit'], '%/min')
            self.assertIn('unwashed', row['LOI_locator'])
            self.assertIn('postspin', row['PMEP_content_basis'])
            self.assertFalse(row.get('Tonset_C'))

    def test_target_counts_exclude_the_tg_only_row(self):
        rows = source_rows()
        report = validator.build_tables(pd.DataFrame(rows), validator.issue_list())[3]
        self.assertFalse(report['errors'])
        self.assertEqual(report['verified_exact_sample_states'], 11)
        self.assertEqual(report['verified_exact_condition_records'], 11)
        self.assertEqual(sum(not row['LOI_pct'] for row in rows), 1)
        self.assertEqual(report['verified_publication_type_counts']['journal_article'],
                         dict(sources=3, sample_states=11, condition_records=11))
        for row in rows:
            if row['LOI_pct']:
                self.assertFalse(pairing.evidence_issues(row))

    def test_value_condition_and_wash_changes_need_fresh_review(self):
        original = next(row for row in source_rows() if row['LOI_pct'])
        for field, value in [('LOI_pct', '80'), ('Tmax1_C', '450'),
                             ('atmosphere', 'nitrogen'), ('heating_rate_C_min', '20'),
                             ('washing_state', 'after 30 durability laundering cycles')]:
            changed = copy.deepcopy(original)
            changed[field] = value
            self.assertIn('measurement_review_pending_or_stale', pairing.evidence_issues(changed))


if __name__ == '__main__':
    unittest.main()
