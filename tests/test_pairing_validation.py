import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd
from scripts import textile_scope as scope
from scripts import pairing as p
from scripts import validate_tg_loi as v


def observation(**changes):
    row = {'DOI': '10.1234/example', 'sample_state': 'A+B', 'washing_state': '',
           'atmosphere': 'N2', 'heating_rate_C_min': '10', 'LOI_pct': '25',
           'Tmax1_C': '340', 'material_form': 'woven fabric', 'direct_numeric_use': 'TG+LOI',
           'source_url': 'https://example.org/paper', 'source_location': 'Tables 1, 2; Methods 2.3',
           'source_file': 'fixture.csv', 'source_row': 2}
    row.update(changes)
    return row


def approve(row):
    return dict(row, pairing_status='verified_exact', pairing_evidence='Tables 1 and 2: A+B, unwashed woven fabric; Methods 2.3.',
                material_form_TGA='woven fabric', material_form_LOI='woven fabric',
                numeric_evidence_type='tabulated', evidence_reviewed_by='test reviewer',
                reviewed_measurement_fingerprint=p.measurement_fingerprint(row))


class PairIdentityTests(unittest.TestCase):
    def test_punctuation_does_not_create_false_equivalence(self):
        self.assertNotEqual(p.normalize_label('A+B'), p.normalize_label('AB'))
        self.assertNotEqual(p.normalize_label('A-B'), p.normalize_label('AB'))
        self.assertEqual(p.normalize_label(' A   B '), p.normalize_label('a b'))

    def test_keys_normalize_rate_doi_atmosphere_not_washing(self):
        self.assertEqual(p.pair_key(observation()), p.pair_key(observation(DOI='https://doi.org/10.1234/EXAMPLE', heating_rate_C_min='10.0', atmosphere='nitrogen')))
        self.assertNotEqual(p.pair_key(observation()), p.pair_key(observation(washing_state='after 5 wash cycles')))
        self.assertNotEqual(p.pair_key(observation()), p.pair_key(observation(atmosphere='O2')))

    def test_review_bound_to_measurements_and_unique_record(self):
        row = observation()
        review = approve(row)
        review['measurement_fingerprint'] = p.measurement_fingerprint(row)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'reviews.csv'
            pd.DataFrame([review]).to_csv(path, index=False)
            self.assertEqual(p.reviewed_metadata(row, path)['pairing_status'], 'verified_exact')
            self.assertFalse(p.reviewed_metadata(observation(LOI_pct='26'), path))
            pd.DataFrame([review, review]).to_csv(path, index=False)
            self.assertEqual(p.reviewed_metadata(row, path)['pairing_status'], 'ambiguous_review')

    def test_stale_inline_review_cannot_authorize_changed_numbers(self):
        row = approve(observation())
        self.assertFalse(p.evidence_issues(row))
        row['Tmax1_C'] = '350'
        self.assertIn('measurement_review_pending_or_stale', p.evidence_issues(row))


class UnnumberedPeakTests(unittest.TestCase):
    def row(self, value='363.6'):
        return observation(Tmax1_C='', Tmax_unnumbered_C=value,
                           source_raw_Tmax_C=value,
                           source_Tmax_definition='Original unnumbered Tpeak: maximum decomposition rate; Table 6.')

    def test_defined_unnumbered_peak_is_a_sole_TG_metric(self):
        row = approve(self.row())
        master, _, _, report = v.build_tables(pd.DataFrame([row]))
        self.assertEqual(len(master), 1)
        self.assertEqual(report['verified_exact_sample_states'], 1)
        self.assertFalse(master.iloc[0]['Tmax1_C'])
        self.assertEqual(master.iloc[0]['Tmax_unnumbered_C'], '363.6')

    def test_unknown_raw_peak_is_not_a_numeric_TG_candidate(self):
        row = approve(observation(Tmax1_C='', source_raw_Tmax_C='348',
                                  source_Tmax_definition='Maximum label; rate criterion unknown.'))
        master, candidates, _, _ = v.build_tables(pd.DataFrame([row]))
        self.assertTrue(master.empty)
        self.assertTrue(candidates.empty)

    def test_empty_alias_keeps_fingerprint_but_actual_generic_value_is_bound(self):
        base = observation(Tmax1_C='')
        self.assertEqual(p.measurement_fingerprint(base), p.measurement_fingerprint(dict(base, Tmax_unnumbered_C='')))
        generic = self.row()
        self.assertNotEqual(p.measurement_fingerprint(base), p.measurement_fingerprint(generic))
        self.assertNotEqual(p.measurement_fingerprint(generic),
                            p.measurement_fingerprint(observation(Tmax1_C='363.6')))
        self.assertEqual(p.measurement_fingerprint(generic),
                         p.measurement_fingerprint(dict(generic, source_raw_Tmax_C='999')))
        self.assertEqual(p.pair_key(base), p.pair_key(generic))

    def test_historical_Tmax_C_is_not_silently_promoted(self):
        base = observation(Tmax1_C='')
        legacy = dict(base, Tmax_C='418')
        self.assertEqual(p.measurement_fingerprint(base), p.measurement_fingerprint(legacy))
        master, candidates, _, _ = v.build_tables(pd.DataFrame([approve(legacy)]))
        self.assertTrue(master.empty)
        self.assertTrue(candidates.empty)

    def test_unnumbered_peak_cannot_reuse_stale_numeric_review(self):
        row = approve(self.row())
        row['Tmax_unnumbered_C'] = '397.7'
        self.assertIn('measurement_review_pending_or_stale', p.evidence_issues(row))

    def test_generic_temperature_invalid_values_reject(self):
        for value in ['19', '1501', 'inf', '-inf', 'nan', 'bad', '350–360']:
            with self.subTest(value=value):
                self.assertTrue(v.numeric_errors(pd.DataFrame([self.row(value)])))

    def test_raw_alias_is_one_observation_and_scope_binding_changes_with_value(self):
        row = approve(self.row())
        master, _, _, report = v.build_tables(pd.DataFrame([row]))
        self.assertEqual(len(master), 1)
        self.assertEqual(report['verified_exact_condition_records'], 1)
        alias = dict(row, source_raw_Tmax_C='363.6', source_Tmax_label='Tpeak')
        self.assertEqual(scope.observation_key(row), scope.observation_key(alias))
        changed = approve(dict(row, Tmax_unnumbered_C='397.7'))
        self.assertNotEqual(scope.observation_key(row), scope.observation_key(changed))
        self.assertEqual(p.sample_state_id(row), p.sample_state_id(changed))

    def test_invalid_unnumbered_temperature_cannot_publish_over_previous_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = [Path(tmp) / name for name in ['master.csv', 'candidates.csv', 'quarantine.csv', 'report.json']]
            for path in paths:
                path.write_text('previous valid snapshot')
            row = approve(self.row('bad'))
            with patch.object(v, 'load_all', return_value=pd.DataFrame([row])), \
                 patch.object(v, 'issue_list', return_value=[]), \
                 patch.object(v, 'MASTER', paths[0]), patch.object(v, 'CANDIDATES', paths[1]), \
                 patch.object(v, 'QUARANTINE', paths[2]), patch.object(v, 'REPORT', paths[3]):
                with self.assertRaises(SystemExit):
                    v.main()
            self.assertTrue(all(path.read_text() == 'previous valid snapshot' for path in paths))

    def test_same_state_two_gases_does_not_add_a_mother(self):
        rows = [approve(self.row()), approve(dict(self.row(), atmosphere='air'))]
        _, _, _, report = v.build_tables(pd.DataFrame(rows))
        self.assertEqual(report['verified_exact_condition_records'], 2)
        self.assertEqual(report['verified_exact_sample_states'], 1)


class EvidenceValidationTests(unittest.TestCase):
    def test_complete_legacy_record_is_pending_not_invalid(self):
        master, candidates, quarantine, report = v.build_tables(pd.DataFrame([observation()]))
        self.assertEqual(len(master), 0)
        self.assertEqual(candidates.iloc[0].pair_quality, 'pending_review')
        self.assertTrue(quarantine.empty)
        self.assertEqual(report['legacy_field_complete_condition_records'], 1)
        self.assertEqual(report['eligible_pending_condition_records'], 1)
        self.assertEqual(report['errors'], [])

    def test_verified_exact_row_enters_master(self):
        master, _, _, report = v.build_tables(pd.DataFrame([approve(observation())]))
        self.assertEqual(len(master), 1)
        self.assertEqual(report['verified_exact_sample_states'], 1)
        self.assertEqual(report['plot_ready_verified_counts']['Tmax1_C'], 1)

    def test_conflicting_registry_overrides_old_inline_approval(self):
        row = approve(observation())
        valid = dict(row, measurement_fingerprint=p.measurement_fingerprint(row))
        rejected = dict(valid, pairing_status='rejected')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'reviews.csv'
            pd.DataFrame([valid, rejected]).to_csv(path, index=False)
            with patch.object(p, 'REVIEWS', path):
                master, candidates, _, _ = v.build_tables(pd.DataFrame([row]))
            self.assertTrue(master.empty)
            self.assertEqual(candidates.iloc[0].pairing_status, 'ambiguous_review')
            pd.DataFrame([dict(valid, pairing_status='')]).to_csv(path, index=False)
            with patch.object(p, 'REVIEWS', path):
                master, _, _, _ = v.build_tables(pd.DataFrame([row]))
            self.assertTrue(master.empty)

    def test_equal_reviewed_resin_forms_cannot_enter_textile_master(self):
        row = approve(observation())
        row.update(material_form_TGA='resin', material_form_LOI='resin')
        master, candidates, _, _ = v.build_tables(pd.DataFrame([row]))
        self.assertTrue(master.empty)
        self.assertIn('reviewed_specimen_not_textile', candidates.iloc[0].review_reasons)

    def test_reviewed_legacy_chinese_form_and_affirmative_are_reachable(self):
        row = approve(observation(material_form='织物', direct_numeric_use='是'))
        master, candidates, _, _ = v.build_tables(pd.DataFrame([row]))
        self.assertEqual(len(master), 1)
        self.assertEqual(candidates.iloc[0].material_form, '织物')
        self.assertEqual(candidates.iloc[0].direct_numeric_use, '是')

    def test_chinese_affirmative_does_not_bypass_review_or_negative_tag(self):
        for row in [observation(material_form='织物', direct_numeric_use='是'),
                    approve(observation(material_form='织物', direct_numeric_use='否')),
                    approve(observation(material_form='织物', direct_numeric_use='是但需复核'))]:
            with self.subTest(row=row):
                master, _, _, _ = v.build_tables(pd.DataFrame([row]))
                self.assertTrue(master.empty)

    def test_same_sample_two_conditions_only_one_independent_state(self):
        rows = [approve(observation()), approve(observation(atmosphere='air'))]
        master, _, _, report = v.build_tables(pd.DataFrame(rows))
        self.assertEqual(len(master), 2)
        self.assertEqual(report['verified_exact_sample_states'], 1)
        self.assertEqual(report['remaining_to_target'], 1999)

    def test_form_mismatch_and_alias_quarantined_without_deletion(self):
        rows = [approve(observation(material_form_TGA='fiber', material_form_LOI='woven fabric')),
                observation(sample_state='8'), observation(sample_state='8 BL')]
        # approve() sets equal forms; make the actual mismatch explicit afterwards.
        rows[0]['material_form_TGA'] = 'fiber'
        issues = [{'DOI': '10.1234/example', 'sample_state': name,
                   'reason_code': 'possible_sample_alias', 'status': 'open'} for name in ['8', '8 BL']]
        master, candidates, quarantine, report = v.build_tables(pd.DataFrame(rows), issues)
        self.assertTrue(master.empty)
        self.assertEqual(len(candidates), 3)
        self.assertEqual(len(quarantine), 3)
        self.assertEqual(report['quarantine_reason_counts'], {'specimen_form_mismatch': 1, 'possible_sample_alias': 2})

    def test_conflicting_duplicate_values_never_silently_keep_first(self):
        rows = [approve(observation()), approve(observation(LOI_pct='26'))]
        master, candidates, quarantine, report = v.build_tables(pd.DataFrame(rows))
        self.assertTrue(master.empty)
        self.assertEqual(len(quarantine), 2)
        self.assertEqual(len(candidates), 2)

    def test_range_failure_does_not_replace_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = [Path(tmp) / name for name in ['master.csv', 'candidates.csv', 'quarantine.csv', 'report.json']]
            for path in paths:
                path.write_text('previous valid snapshot')
            with patch.object(v, 'load_all', return_value=pd.DataFrame([approve(observation(LOI_pct='101'))])), \
                 patch.object(v, 'issue_list', return_value=[]), \
                 patch.object(v, 'MASTER', paths[0]), patch.object(v, 'CANDIDATES', paths[1]), \
                 patch.object(v, 'QUARANTINE', paths[2]), patch.object(v, 'REPORT', paths[3]):
                with self.assertRaises(SystemExit):
                    v.main()
            self.assertTrue(all(x.read_text() == 'previous valid snapshot' for x in paths))

    def test_output_write_is_noop_when_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'out.csv'
            v.write_if_changed(path, 'a,b\n1,2\n')
            stamp = path.stat().st_mtime_ns
            v.write_if_changed(path, 'a,b\n1,2\n')
            self.assertEqual(stamp, path.stat().st_mtime_ns)


if __name__ == '__main__':
    unittest.main()
