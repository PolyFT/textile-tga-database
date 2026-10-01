"""Reject control reuse, typo selection and transfers across assays/states."""
import csv
import sys
import unittest
from pathlib import Path
import pandas as pd

R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / 'scripts'))
import pairing
import validate_tg_loi as validator


class PCTSiEvidenceTests(unittest.TestCase):
    source_file = R / 'data/incoming/verified_source_batch_20261001_b103_local_pctsi.csv'

    @classmethod
    def setUpClass(cls):
        with cls.source_file.open(newline='') as handle:
            cls.all_rows = list(csv.DictReader(handle))
        cls.rows = [r for r in cls.all_rows if r['DOI'] == '10.1007/s10570-020-03016-w']
        cls.approved = [r for r in cls.rows if r['pairing_status'] == 'verified_exact']

    def test_two_states_four_conditions_not_four_independent_pairs(self):
        report = validator.build_tables(pd.DataFrame(self.rows).fillna(''), validator.issue_list())[3]
        self.assertEqual(report['errors'], [])
        self.assertEqual((report['verified_exact_sample_states'], report['verified_exact_condition_records']), (2, 4))
        self.assertEqual(len(self.rows), 16)
        self.assertEqual({r['source_bath_concentration_g_L'] for r in self.approved}, {'350', '450'})

    def test_repeated_controls_and_one_degree_conflicts_are_not_new_pairs(self):
        controls = [r for r in self.rows if r['sample_state'] == 'Untreated cotton']
        self.assertEqual(len(controls), 2)
        for row in controls:
            self.assertEqual(row['pairing_status'], 'cross_source_control_reuse_pending')
            self.assertEqual(row['source_control_comparator_DOI'], '10.1007/s10570-021-04054-8')
            self.assertEqual(row['Tmax1_C'], '')
            self.assertEqual(row['reviewed_measurement_fingerprint'], '')
        n2 = next(r for r in controls if r['atmosphere'] == 'N2')
        air = next(r for r in controls if r['atmosphere'] == 'air')
        self.assertEqual((n2['source_Tmax1_table_C'], n2['source_Tmax1_prose_C']), ('369', '368'))
        self.assertEqual((air['source_Tmax1_table_C'], air['source_Tmax1_prose_C']), ('344', '343'))

    def test_250_concentration_typo_is_not_silently_corrected(self):
        rows = [r for r in self.rows if r['source_bath_concentration_g_L'] == '250']
        self.assertEqual(len(rows), 2)
        for row in rows:
            self.assertEqual(row['pairing_status'], 'held_LOI_concentration_conflict_200prose_250Table1')
            self.assertEqual((row['source_LOI_Table1_pct'], row['source_LOI_prose_concentration_g_L']), ('24.8', '200'))
            self.assertEqual(row['LOI_pct'], '')
            self.assertEqual(row['reviewed_measurement_fingerprint'], '')

    def test_air_residue_mapping_concern_remains_raw_only(self):
        treated_air = [r for r in self.rows if r['atmosphere'] == 'air' and r['source_bath_concentration_g_L'] != '0']
        self.assertEqual(len(treated_air), 3)
        for row in treated_air:
            self.assertTrue(all(row[k] == '' for k in ('residue_pct', 'R800_pct', 'residue_temp_C')))
            self.assertIn('terminal ordering', row['source_metric_hold'])
        self.assertEqual([r['source_R800_table_pct'] for r in treated_air], ['10.5', '10.5', '13.3'])

    def test_nitrogen_residue_is_measured_at_explicit_temperature(self):
        n2 = [r for r in self.approved if r['atmosphere'] == 'N2']
        self.assertEqual([r['residue_pct'] for r in n2], ['38.1', '38.9'])
        for row in n2:
            self.assertEqual(row['residue_temp_C'], '800')
            self.assertNotEqual(row['residue_pct'], '29.9')
        calculated = next(r for r in self.rows if r['material_category'] == 'calculated_curve')
        self.assertEqual(calculated['source_R800_calculated_pct'], '29.9')
        self.assertEqual(calculated['residue_pct'], '')
        self.assertNotEqual(calculated['pairing_status'], 'verified_exact')

    def test_washed_and_other_concentrations_have_no_transferred_tg(self):
        held = [r for r in self.rows if r['pairing_status'].startswith('held_LOI_only')]
        self.assertEqual(len(held), 6)
        for row in held:
            self.assertTrue(all(row.get(k, '') == '' for k in pairing.TG_FIELDS))
            self.assertEqual(row['reviewed_measurement_fingerprint'], '')

    def test_regular_tg_methods_are_not_tgftir_or_water_peak(self):
        for row in self.approved:
            self.assertEqual((row['TG_start_C'], row['TG_end_C'], row['source_TG_mass_mg']), ('40', '800', '5'))
            self.assertEqual(row['source_TG_flow'], 'unreported for regularTG')
            self.assertEqual(row.get('source_TG_flow_mL_min', ''), '')
            self.assertNotIn(row['Tmax1_C'], ('135', '162'))
            self.assertEqual(row.get('T5_C', ''), '')
            self.assertEqual(row.get('T10_C', ''), '')
            self.assertIn('amounts unreported', row['treatment_method'])
            self.assertEqual(row['material_form_TGA'], row['material_form_LOI'])

    def test_changed_measurement_cannot_reuse_approval(self):
        for row in self.approved:
            self.assertEqual(pairing.evidence_issues(row), [])
        changed = dict(self.approved[0], LOI_pct='29.5')
        self.assertIn('measurement_review_pending_or_stale', pairing.evidence_issues(changed))


class SPDPPTMSHeldEvidenceTests(unittest.TestCase):
    source_file = PCTSiEvidenceTests.source_file

    @classmethod
    def setUpClass(cls):
        with cls.source_file.open(newline='') as handle:
            cls.rows = [r for r in csv.DictReader(handle) if r['DOI'] == '10.1007/s10570-020-03370-9']

    def test_no_state_admitted_from_conflicting_preparation(self):
        report = validator.build_tables(pd.DataFrame(self.rows).fillna(''), validator.issue_list())[3]
        self.assertEqual(report['errors'], [])
        self.assertEqual((report['verified_exact_sample_states'], report['verified_exact_condition_records']), (0, 0))
        self.assertEqual(len(self.rows), 12)
        for row in self.rows:
            self.assertEqual(row['reviewed_measurement_fingerprint'], '')

    def test_500_scope_known_but_neither_ph_selected(self):
        treated = [r for r in self.rows if r['pairing_status'] == 'preparation_pH_scope_conflict_pending']
        self.assertEqual(len(treated), 2)
        for row in treated:
            self.assertEqual((row['source_preparation_prose_pH'], row['source_preparation_Scheme2_pH']), ('3.6', '3'))
            self.assertEqual(row['source_bath_concentration_g_L'], '500')
            self.assertEqual(row['LOI_pct'], '29.5')
            self.assertIn('Fig6caption500gL', row['pairing_evidence'])
            self.assertNotEqual(row['pairing_status'], 'verified_exact')

    def test_tg_vector_reuse_is_held_despite_different_loi(self):
        controls = [r for r in self.rows if r['sample_state'] == 'Untreated cotton']
        self.assertEqual(len(controls), 2)
        for row in controls:
            self.assertEqual(row['LOI_pct'], '18.1')
            self.assertEqual(row['pairing_status'], 'cross_source_control_TG_reuse_pending')
            self.assertEqual(row['source_control_comparator_DOI'], '10.1007/s10570-021-04054-8')

    def test_native_second_stage_onset_is_not_second_maximum(self):
        n2 = next(r for r in self.rows if r['sample_state'].startswith('SPDP-PTMS500g/L treated') and r['atmosphere'] == 'N2')
        self.assertEqual((n2['Tonset_C'], n2['source_Tonset_stage2_C']), ('205', '295'))
        self.assertEqual((n2['Tmax1_C'], n2['Tmax2_C'], n2['residue_pct'], n2['residue_temp_C']), ('287', '315', '44.0', '800'))
        air = next(r for r in self.rows if r['sample_state'].startswith('SPDP-PTMS500g/L treated') and r['atmosphere'] == 'air')
        self.assertEqual((air['Tmax1_C'], air['Tmax2_C'], air['residue_pct']), ('306', '', '23.8'))
        self.assertEqual(n2.get('T5_C', ''), '')
        self.assertEqual(n2.get('T10_C', ''), '')

    def test_methods_and_material_not_borrowed_from_related_paper(self):
        tg_rows = [r for r in self.rows if r['atmosphere']]
        for row in tg_rows:
            self.assertEqual((row['source_TG_mass_mg'], row['source_TG_flow_mL_min'], row['source_TG_repeat_count']), ('5', '20', '2'))
            self.assertEqual((row['TG_start_C'], row['TG_end_C']), ('40', '800'))
            self.assertEqual(row['TGA_instrument'], 'TG851,Mettler-Toledo')
            self.assertNotIn('122g', row['material_form_TGA'])
            self.assertIn('unreported', row['material_form_TGA'])

    def test_other_baths_and_washes_do_not_inherit_500_tg(self):
        held = [r for r in self.rows if r['pairing_status'].startswith('LOI_only')]
        self.assertEqual(len(held), 8)
        for row in held:
            self.assertTrue(all(row.get(k, '') == '' for k in pairing.TG_FIELDS))
            self.assertEqual(row['atmosphere'], '')

    def test_synthetic_mass_labels_are_retained_without_loading_correction(self):
        row = next(r for r in self.rows if r['sample_state'].startswith('SPDP-PTMS500g/L treated'))
        self.assertEqual((row['source_synthesis_APTMS_mass_g'], row['source_synthesis_APTMS_amount_mol']), ('116.53', '0.2'))
        self.assertEqual((row['source_synthesis_product_mass_g'], row['source_synthesis_product_amount_mol']), ('138.93', '0.09'))
        self.assertIn('no correction', row['source_synthetic_mass_mole_anomaly'])
        self.assertEqual(row['source_measured_weight_gain_pct_owf'], '32.3')


if __name__ == '__main__':
    unittest.main()
