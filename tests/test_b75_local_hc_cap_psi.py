"""Protect exact specimen matching and original-source metric conflicts."""
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

FILE = ROOT / 'data/incoming/verified_source_batch_20261001_b75_local_hc_cap_psi.csv'


def source_rows(suffix=None):
    with FILE.open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    return [row for row in rows if suffix is None or row['DOI'].endswith(suffix)]


class OriginalSourceBoundaries(unittest.TestCase):
    def test_hc_unmatched_label_and_thresholds(self):
        rows = source_rows('2017.11.018')
        extra = next(row for row in rows if row['sample_state'] == '2HC')
        self.assertFalse(extra['LOI_pct'])
        self.assertFalse(extra['HC_bath_wt_pct'])
        self.assertFalse(extra['weight_gain_pct'])
        treated = next(row for row in rows if row['sample_state'] == '5HC')
        self.assertEqual(float(treated['LOI_pct']), 19.9)
        self.assertEqual(float(treated['HC_bath_wt_pct']), 5)
        self.assertEqual(float(treated['weight_gain_pct']), 8.6)
        self.assertEqual(float(treated['T1_C']), 41.9)
        self.assertEqual(float(treated['Tmax1_C']), 320.3)
        self.assertFalse(treated.get('Tonset_C'))
        self.assertEqual(treated['atmosphere_reported'], 'synthetic air')
        self.assertIn('not reported', treated['TG_atmosphere_composition'])
        self.assertEqual(float(treated['TG_gas_flow_mL_min']), 60)
        self.assertEqual(float(treated['heating_rate_C_min']), 10)
        self.assertIn('not claimed asSD', treated['LOI_uncertainty_description'])

    def test_psi_initial_state_and_native_definitions(self):
        rows = source_rows('2016.02.009')
        self.assertEqual(len(rows), 4)
        control = next(row for row in rows if row['sample_state'] == 'COT')
        self.assertEqual(float(control['phosphorus_content_mg_g']), .79)
        treated = next(row for row in rows if row['sample_state'] == 'COT-PSi9.4')
        self.assertEqual(float(treated['T5_C']), 250)
        self.assertFalse(treated.get('Tonset_C'))
        self.assertEqual(float(treated['Tmax1_C']), 329)
        self.assertEqual(float(treated['source_Vmax_pct_min']), -34.7)
        self.assertEqual(float(treated['R600_pct']), 13.4)
        self.assertEqual(float(treated['residue_temp_C']), 600)
        self.assertEqual(float(treated['LOI_pct']), 21.2)
        self.assertEqual(float(treated['PSi_emulsion_g_L']), 100)
        self.assertTrue(treated['supplement_source_url'].endswith('-mmc1.docx'))
        self.assertIn('all4embedded', treated['supplement_review_status'])
        self.assertFalse(any('wash' in row['sample_state'] or 'COT-Si' in row['sample_state'] for row in rows))

    def test_cap_residue_conflict_and_control_preparation(self):
        rows = source_rows('2019.109028')
        treated = next(row for row in rows if row['sample_state'] == 'CAP2')
        self.assertEqual(float(treated['source_R800_table_pct']), 27.3)
        self.assertEqual(float(treated['source_Vmax1_pct_min']), -.0075)
        self.assertEqual(float(treated['T5_C']), 219)
        self.assertEqual(float(treated['Tmax1_C']), 386)
        self.assertEqual(float(treated['LOI_pct']), 28.1)
        self.assertEqual(float(treated['TG_gas_flow_mL_min']), 50)
        for row in rows:
            self.assertFalse(row.get('R800_pct'))
            self.assertFalse(row.get('residue_at_Tmax_pct'))
            self.assertFalse(row.get('Tonset_C'))
        control = next(row for row in rows if row['sample_state'] == 'Untreated')
        self.assertIn('notasserted', control['treatment_method'])
        self.assertEqual(float(control['LOI_pct']), 21.2)
        dpp = next(row for row in rows if row['sample_state'] == 'DPP')
        self.assertFalse(dpp['LOI_pct'])
        self.assertEqual([float(dpp[f'Tmax{i}_C']) for i in (1, 2, 3)], [288, 342, 428])

    def test_changes_to_measurements_or_state_invalidate_review(self):
        row = next(row for row in source_rows() if row['LOI_pct'])
        for field, changed in [('LOI_pct', '40'), ('T5_C', '500'),
                               ('heating_rate_C_min', '20'), ('atmosphere', 'nitrogen'),
                               ('washing_state', 'after five durability washes')]:
            edited = copy.deepcopy(row)
            edited[field] = changed
            self.assertIn('measurement_review_pending_or_stale', pairing.evidence_issues(edited))

    def test_counts_and_explicit_publication_type(self):
        rows = source_rows()
        _, _, _, report = validator.build_tables(pd.DataFrame(rows), validator.issue_list())
        self.assertFalse(report['errors'])
        self.assertEqual(report['verified_exact_sample_states'], 14)
        self.assertEqual(report['verified_exact_condition_records'], 14)
        self.assertEqual(sum(not row['LOI_pct'] for row in rows), 2)
        self.assertEqual(report['verified_publication_type_counts']['journal_article'],
                         {'sources': 3, 'sample_states': 14, 'condition_records': 14})
        self.assertEqual(report['verified_author_preprint_sources'], 0)
        for row in rows:
            if row['LOI_pct']:
                self.assertFalse(pairing.evidence_issues(row))
                self.assertIn(row['source_document_version'], ('accepted manuscript', 'journal preproof'))


if __name__ == '__main__':
    unittest.main()
