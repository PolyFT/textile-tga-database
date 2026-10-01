"""Original-source boundaries: washed states, uncertainties and unresolved conflicts."""
import csv
import sys
import unittest
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import pairing
import validate_tg_loi as validator


class OriginalCottonBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / 'data/incoming/verified_source_batch_20261001_b83_local_cotton.csv').open(newline='') as handle:
            cls.rows = list(csv.DictReader(handle))

    def source(self, suffix):
        return [r for r in self.rows if r['DOI'].endswith(suffix)]

    def test_counts_keep_ten_held_conditions_outside_target(self):
        report = validator.build_tables(pd.DataFrame(self.rows).fillna(''), validator.issue_list())[3]
        self.assertEqual(report['errors'], [])
        self.assertEqual(len(self.rows), 30)
        self.assertEqual(report['verified_exact_sample_states'], 10)
        self.assertEqual(report['verified_exact_condition_records'], 20)

    def test_asndp_uncertainties_and_integral_index_are_distinct(self):
        rows = self.source('03632-6')
        self.assertEqual(len(rows), 4)
        treated = next(r for r in rows if r['sample_state'] == 'Cotton-ASNDP-4' and r['atmosphere'] == 'nitrogen')
        self.assertEqual(float(treated['source_IPDT_C']), 1402.8)
        self.assertEqual(float(treated['Tonset_C']), 159)
        self.assertEqual(float(treated['source_Tonset_uncertainty_C']), 6)
        self.assertEqual(float(treated['residue_temp_C']), 750)
        self.assertEqual(float(treated['R750_pct']), 42.3)
        self.assertEqual(treated.get('T5_C', ''), '')
        self.assertEqual(float(treated['LOI_repeats_reported']), 2)

    def test_abtmpa_control_conflict_and_explicit600c_points(self):
        for row in self.source('03615-7'):
            if row['sample_state'] == 'Control cotton':
                self.assertEqual(row['LOI_pct'], '')
                self.assertEqual(float(row['source_LOI_control_table_pct']), 17.5)
                self.assertEqual(float(row['source_LOI_control_prose_pct']), 17.1)
                self.assertNotEqual(row['pairing_status'], 'verified_exact')
            else:
                self.assertEqual(float(row['LOI_pct']), 50.2)
                self.assertEqual(float(row['residue_temp_C']), 600)
                self.assertEqual(float(row['heating_rate_C_min']), 20)

    def test_fedopo_recipe_and_pristine_metric_conflicts_remain_held(self):
        for row in self.source('03636-2'):
            if row['sample_state'] != 'Pristine cotton':
                self.assertEqual(float(row['source_Fe_graft_duration_main_h']), 6)
                self.assertEqual(float(row['source_Fe_graft_duration_scheme_h']), 4)
                self.assertNotEqual(row['pairing_status'], 'verified_exact')
                self.assertEqual(row['reviewed_measurement_fingerprint'], '')
            elif row['atmosphere'] == 'nitrogen':
                self.assertEqual(row['Tmax1_C'], '')
                self.assertEqual(float(row['source_Tmax1_table_C']), 379)
                self.assertEqual(float(row['source_Tmax1_prose_C']), 375)
            else:
                self.assertEqual(row['T5_C'], '')
                self.assertEqual(float(row['source_T5_table_C']), 337)
                self.assertEqual(float(row['source_T5_prose_C']), 325)

    def test_plueg_washed_state_has_its_own_printed_tg(self):
        rows = self.source('03714-z')
        approved = [r for r in rows if r['pairing_status'] == 'verified_exact']
        self.assertEqual(len(approved), 4)
        self.assertEqual(len({pairing.sample_state_id(r) for r in approved}), 2)
        for row in approved:
            washed = 'after50LCs' in row['sample_state']
            self.assertEqual(float(row['LOI_pct']), 28.6 if washed else 42.7)
            expected = (31.26 if washed else 43.79) if row['atmosphere'] == 'nitrogen' else (13.87 if washed else 25.30)
            self.assertEqual(float(row['R600_pct']), expected)
            self.assertEqual(float(row['residue_temp_C']), 600)
            self.assertEqual(row.get('R700_pct', ''), '')
        for row in rows:
            if row['sample_state'] == 'Control cotton fabric':
                self.assertEqual(row['LOI_pct'], '')

    def test_asmpea_exact_labels_native_unit_and_dsc_boundary(self):
        expected = {'C0': 17.1, 'FRC-20': 37.9, 'FRC-25': 39.0, 'FRC-30': 40.2}
        rows = self.source('2021.07.130')
        self.assertEqual(len(rows), 8)
        for row in rows:
            self.assertEqual(float(row['LOI_pct']), expected[row['sample_state']])
            self.assertEqual(float(row['heating_rate_C_min']), 20)
            self.assertEqual(float(row['residue_temp_C']), 700)
            self.assertEqual(row.get('TGA_sample_mass_mg_reported', ''), '')
            if row['atmosphere'] == 'air':
                self.assertIn('Celsius', row['source_air_residue_at_Tmax2_header_unit'])
                self.assertEqual(row.get('residue_at_Tmax2_pct', ''), '')

    def test_frlo_form_equivalence_is_not_assumed(self):
        for row in self.source('03648-y'):
            self.assertNotEqual(row['material_form_TGA'], row['material_form_LOI'])
            self.assertNotEqual(row['pairing_status'], 'verified_exact')
            self.assertEqual(row['reviewed_measurement_fingerprint'], '')
            self.assertEqual(float(row['residue_temp_C']), 700)

    def test_changed_values_conditions_and_wash_invalidate_review(self):
        row = next(r for r in self.rows if r['pairing_status'] == 'verified_exact')
        for field, value in [('LOI_pct', 1), ('heating_rate_C_min', 99), ('washing_state', 'after100LCs'), ('atmosphere', 'argon')]:
            changed = dict(row, **{field: value})
            self.assertNotEqual(pairing.measurement_fingerprint(changed), row['reviewed_measurement_fingerprint'])
            self.assertTrue(pairing.evidence_issues(changed))


if __name__ == '__main__':
    unittest.main()
