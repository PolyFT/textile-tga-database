"""Keep source conflicts, native TG metrics and unpaired states outside the target."""
import csv
import sys
import unittest
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import pairing
import validate_tg_loi as validator


class CottonSourceEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / 'data/incoming/verified_source_batch_20261001_b87_local_cotton.csv').open(newline='') as handle:
            cls.rows = list(csv.DictReader(handle))

    def source(self, suffix):
        return [r for r in self.rows if r['DOI'].endswith(suffix)]

    def test_counts_exclude_unpaired_and_approximate_facts(self):
        report = validator.build_tables(pd.DataFrame(self.rows).fillna(''), validator.issue_list())[3]
        self.assertEqual(report['errors'], [])
        self.assertEqual(len(self.rows), 16)
        self.assertEqual(report['verified_exact_sample_states'], 5)
        self.assertEqual(report['verified_exact_condition_records'], 9)
        self.assertFalse(self.source('04049-5'))

    def test_adbspa_t10_and_peak_residue_remain_distinct(self):
        for row in self.source('03728-7'):
            self.assertEqual(row.get('T5_C', ''), '')
            self.assertEqual(row.get('Tonset_C', ''), '')
            self.assertNotEqual(float(row['residue_at_Tmax1_pct']), float(row['R700_pct']))
            self.assertEqual(float(row['residue_temp_C']), 700)
            self.assertEqual(float(row['LOI_uncertainty_pct']), .2)
            self.assertIn('unspecified', row['uncertainty_definition'])
            self.assertIn('Initial0LCs', row['washing_state'])
        treated = next(r for r in self.source('03728-7') if r['sample_state'] == 'ADBSPA-cotton-4' and r['atmosphere'] == 'nitrogen')
        self.assertEqual(float(treated['T10_C']), 246)
        self.assertEqual(float(treated['Tmax1_C']), 282)
        self.assertEqual(float(treated['source_IPDT_C']), 1317.8)

    def test_dopo_stage_boundaries_are_not_tg_metric_values(self):
        for row in self.source('03981-w'):
            self.assertEqual(row.get('TG_start_C', ''), '')
            self.assertEqual(float(row['source_TG_method_start_C']), 40)
            self.assertEqual(float(row['source_TG_table_stage_start_C']), 35)
            for field in ['T5_C', 'T10_C', 'Tonset_C', 'Tmax1_C', 'TGA_sample_mass_mg']:
                self.assertEqual(row.get(field, ''), '')
            if row['sample_state'] == 'Pure cotton':
                self.assertEqual(row['R700_pct'], '')
                self.assertEqual(row['residue_pct'], '')
                self.assertNotEqual(row['pairing_status'], 'verified_exact')
            else:
                expected = 39.81 if row['atmosphere'] == 'nitrogen' else 16.19
                self.assertEqual(float(row['R700_pct']), expected)
                self.assertEqual(float(row['LOI_pct']), 40.2)

    def test_ppdms_generic_treated_formulation_is_unpaired(self):
        for row in self.source('04054-8'):
            self.assertEqual(row.get('T5_C', ''), '')
            self.assertIn('not T5/T10', row['Tonset_definition'])
            self.assertEqual(float(row['TGA_sample_mass_mg']), 5)
            self.assertEqual(row.get('TGA_gas_flow_mL_min', ''), '')
            if row['sample_state'].startswith('Treated'):
                self.assertEqual(row['LOI_pct'], '')
                self.assertEqual(row['pairing_status'], 'treated_formulation_crosswalk_unresolved')
                self.assertEqual(row['reviewed_measurement_fingerprint'], '')

    def test_spptms_approximate_residue_does_not_create_exact_n2_pair(self):
        for row in self.source('04019-x'):
            self.assertEqual(row['residue_pct'], '')
            self.assertEqual(row.get('R750_pct', ''), '')
            self.assertEqual(row['source_residue_qualifier'], 'about')
            self.assertEqual(float(row['TG_end_C']), 750)
            self.assertEqual(float(row['TG_start_C']), 35)
            if row['sample_state'] == 'Untreated cotton' and row['atmosphere'] == 'nitrogen':
                self.assertEqual(row.get('Tmax1_C', ''), '')
                self.assertNotEqual(row['pairing_status'], 'verified_exact')
            elif row['sample_state'] == 'Untreated cotton':
                self.assertEqual((float(row['Tmax1_C']), float(row['Tmax2_C'])), (338, 487))
                self.assertEqual(row['pairing_status'], 'verified_exact')

    def test_spptms_loi_conflict_and_water_stage_numbering_are_held(self):
        for row in self.source('04019-x'):
            if row['sample_state'] == 'Untreated cotton':
                continue
            self.assertEqual(row['LOI_pct'], '')
            self.assertEqual(float(row['source_LOI_initial_table_pct']), 31.2)
            self.assertEqual(float(row['source_LOI_initial_washing_prose_pct']), 31.5)
            self.assertEqual(row['reviewed_measurement_fingerprint'], '')
            if row['atmosphere'] == 'nitrogen':
                self.assertEqual(row.get('Tmax1_C', ''), '')
                self.assertEqual((float(row['Tmax2_C']), float(row['Tmax3_C'])), (247, 299))
                self.assertIn('afterwaterstage1', row['peak_numbering_definition'])

    def test_changed_measurement_and_state_require_another_review(self):
        row = next(r for r in self.rows if r['pairing_status'] == 'verified_exact')
        for field, value in [('LOI_pct', 1), ('heating_rate_C_min', 99), ('washing_state', 'after100LCs')]:
            changed = dict(row, **{field: value})
            self.assertNotEqual(pairing.measurement_fingerprint(changed), row['reviewed_measurement_fingerprint'])
            self.assertTrue(pairing.evidence_issues(changed))


if __name__ == '__main__':
    unittest.main()
