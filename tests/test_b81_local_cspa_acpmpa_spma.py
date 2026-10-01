"""Original-source scientific boundaries for CS/PA, ACPMPA and SPMA fabrics."""
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

FILES = list((ROOT / 'data/incoming').glob('verified_source_batch_*_local_cspa_acpmpa_spma.csv'))


def source_rows(suffix=None):
    assert len(FILES) == 1
    with FILES[0].open(newline='') as handle:
        rows = list(csv.DictReader(handle))
    return [row for row in rows if suffix is None or row['DOI'].endswith(suffix)]


class OriginalSourceBoundaries(unittest.TestCase):
    def test_cspa_air_ramp_is_not_inferred_and_initial_states_match(self):
        rows = source_rows('2021.02.023')
        self.assertEqual(len(rows), 6)
        nitrogen = [row for row in rows if row['atmosphere'] == 'nitrogen']
        self.assertEqual([float(row['LOI_pct']) for row in nitrogen], [17.3, 23.7, 29.2])
        self.assertEqual([float(row['T10_C']) for row in nitrogen], [350, 291, 257])
        self.assertEqual([float(row['R700_pct']) for row in nitrogen], [.30, 4.97, 6.50])
        for row in nitrogen:
            self.assertEqual(row['pairing_status'], 'verified_exact')
            self.assertFalse(row.get('T5_C'))
            self.assertFalse(row.get('Tonset_C'))
            self.assertFalse(row.get('R800_pct'))
            self.assertEqual(float(row['TG_end_method_C']), 800)
            self.assertEqual(float(row['residue_temp_C']), 700)
            self.assertIn('washed20BLLOI24.8', row['limitations'])
        for row in rows:
            if row['atmosphere'] == 'air':
                self.assertFalse(row['heating_rate_C_min'])
                self.assertFalse(row.get('reviewed_measurement_fingerprint'))
                self.assertEqual(row['pairing_status'], 'TG_LOI_condition_pending')
        report = validator.build_tables(pd.DataFrame(rows), validator.issue_list())[3]
        self.assertEqual(report['verified_exact_sample_states'], 3)
        self.assertEqual(report['verified_exact_condition_records'], 3)
        self.assertEqual(report['rows_missing_heating_rate_among_pair_candidates'], 3)

    def test_acpmpa_residue_temperatures_and_water_stage_remain_distinct(self):
        rows = source_rows('2020.11.022')
        self.assertEqual(len(rows), 4)
        expected = {
            ('nitrogen', 'Raw cotton'): ('362', '11.24', ''),
            ('nitrogen', '35% ACPMPA-treated cotton'): ('295', '39.79', '697'),
            ('air', 'Raw cotton'): ('371', '1.61', '656'),
            ('air', '35% ACPMPA-treated cotton'): ('303', '35.22', ''),
        }
        for row in rows:
            self.assertEqual((row['Tmax1_C'], row['residue_pct'], row['residue_temp_C']),
                             expected[(row['atmosphere'], row['sample_state'])])
            self.assertFalse(row.get('R700_pct'))
            self.assertFalse(row.get('T5_C'))
            self.assertFalse(row.get('T10_C'))
            self.assertFalse(row.get('Tonset_C'))
            self.assertTrue(row['water_stage_mass_loss_pct'])
            self.assertEqual(row['rate_unit'], '%/C')
            self.assertIn('in-press', row['source_document_version'])
            self.assertIn('row0durabilitycycles', row['LOI_locator'])
        treated = next(row for row in rows
                       if row['atmosphere'] == 'nitrogen' and row['sample_state'].startswith('35'))
        self.assertEqual(float(treated['source_stage3_mass_loss_table_pct']), 24.23)
        self.assertEqual(float(treated['source_stage3_mass_loss_prose_pct']), 26.96)
        report = validator.build_tables(pd.DataFrame(rows), validator.issue_list())[3]
        self.assertEqual(report['verified_exact_sample_states'], 2)
        self.assertEqual(report['verified_exact_condition_records'], 4)

    def test_spma_compounds_and_tgir_assignment_conflicts_stay_unapproved(self):
        rows = source_rows('s42114-021-00348-4')
        self.assertEqual(len(rows), 3)
        accepted = next(row for row in rows if row['sample_state'] == 'SPMA-5')
        self.assertEqual(float(accepted['LOI_pct']), 23.5)
        self.assertEqual(float(accepted['Tonset_C']), 182.7)
        self.assertEqual(float(accepted['R800_pct']), 26.1)
        self.assertEqual(accepted['TG_atmosphere_composition'], 'static nitrogen')
        self.assertFalse(accepted.get('Tmax1_C'))
        self.assertFalse(accepted.get('T5_C'))
        for row in rows:
            self.assertIn('oneembeddedFigureS1', row['supplement_review_status'])
            self.assertIn('Ti swapped', row['limitations'])
            if row['sample_state'] != 'SPMA-5':
                self.assertFalse(row['Tonset_C'])
                self.assertFalse(row['residue_temp_C'])
                self.assertFalse(row['R800_pct'])
                self.assertFalse(row.get('reviewed_measurement_fingerprint'))
                self.assertNotEqual(row['pairing_status'], 'verified_exact')
        report = validator.build_tables(pd.DataFrame(rows), validator.issue_list())[3]
        self.assertEqual(report['verified_exact_sample_states'], 1)
        self.assertEqual(report['verified_exact_condition_records'], 1)

    def test_independent_states_exclude_repeated_atmosphere_and_held_candidates(self):
        rows = source_rows()
        report = validator.build_tables(pd.DataFrame(rows), validator.issue_list())[3]
        self.assertFalse(report['errors'])
        self.assertEqual(report['verified_exact_sample_states'], 6)
        self.assertEqual(report['verified_exact_condition_records'], 8)
        self.assertEqual(report['verified_publication_type_counts']['journal_article'],
                         dict(sources=3, sample_states=6, condition_records=8))
        self.assertEqual(len(rows), 13)
        self.assertEqual(sum(row['pairing_status'] == 'verified_exact' for row in rows), 8)
        for row in rows:
            if row['pairing_status'] == 'verified_exact':
                self.assertFalse(pairing.evidence_issues(row))

    def test_value_condition_and_washing_mutations_invalidate_review(self):
        original = next(row for row in source_rows() if row['pairing_status'] == 'verified_exact')
        for field, value in [('LOI_pct', '80'), ('Tmax1_C', '600'), ('residue_temp_C', '800'),
                             ('atmosphere', 'air'), ('heating_rate_C_min', '20'),
                             ('washing_state', 'afterfive durabilitywashcycles')]:
            changed = copy.deepcopy(original)
            changed[field] = value
            self.assertIn('measurement_review_pending_or_stale', pairing.evidence_issues(changed))


if __name__ == '__main__':
    unittest.main()
