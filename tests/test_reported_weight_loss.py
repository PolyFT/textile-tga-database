import unittest

import pandas as pd
from scripts import pairing as p, reader_table as reader, validate_tg_loi as v
from tests.test_pairing_validation import observation, approve


class ReportedWeightLossTests(unittest.TestCase):
    temperature = 800
    field = 'source_weight_loss_800_pct'

    def row(self, loss='84.7', **changes):
        return observation(Tmax1_C='', **{self.field: loss}, **changes)

    def test_loss_only_is_a_candidate_but_requires_source_review(self):
        master, candidates, _, _ = v.build_tables(pd.DataFrame([self.row()]))
        self.assertTrue(master.empty)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates.iloc[0].pair_quality, 'pending_review')

    def test_reviewed_loss_only_admitted_without_invented_residue_or_peak(self):
        row = approve(self.row())
        master, _, _, report = v.build_tables(pd.DataFrame([row]))
        self.assertEqual(len(master), 1)
        self.assertEqual(report['errors'], [])
        for field in ['R500_pct', 'R800_pct', 'residue_pct', 'T5_C', 'Tonset_C']:
            self.assertFalse(master.iloc[0].get(field, ''))
        self.assertEqual(master.iloc[0]['Tmax1_C'], '')

    def test_loss_value_changes_invalidate_source_review(self):
        row = approve(self.row())
        old = p.measurement_fingerprint(row)
        row[self.field] = '85.7'
        self.assertNotEqual(old, p.measurement_fingerprint(row))
        self.assertIn('measurement_review_pending_or_stale', p.evidence_issues(row))

    def test_disagreeing_loss_at_same_condition_is_quarantined(self):
        a, b = approve(self.row()), approve(self.row('85.7'))
        master, _, quarantine, _ = v.build_tables(pd.DataFrame([a, b]))
        self.assertTrue(master.empty)
        self.assertEqual(len(quarantine), 2)
        self.assertTrue(all('conflicting_measurements' in x for x in quarantine.review_reasons))

    def test_different_gas_is_another_record_for_same_sample(self):
        a, b = approve(self.row()), approve(self.row(atmosphere='air'))
        self.assertEqual(p.sample_state_id(a), p.sample_state_id(b))
        self.assertNotEqual(p.pair_key(a), p.pair_key(b))

    def test_finite_percentage_range_and_invalid_literals(self):
        for value in ['0', '100', '84.7', '', '  ']:
            with self.subTest(value=value):
                self.assertEqual(v.numeric_errors(pd.DataFrame([self.row(value)])), [])
        for value in ['-1', '101', 'NaN', 'inf', '-inf', 'unknown', '84.7±0.1']:
            with self.subTest(value=value):
                self.assertTrue(v.numeric_errors(pd.DataFrame([self.row(value)])))

    def test_blank_and_unregistered_loss_fields_do_not_make_TG(self):
        for row in [self.row(''), observation(Tmax1_C='', source_weight_loss_700_pct='84.7')]:
            master, candidates, _, _ = v.build_tables(pd.DataFrame([row]))
            self.assertTrue(master.empty)
            self.assertTrue(candidates.empty)

    def test_reader_preserves_loss_direction_temperature_and_zero(self):
        for loss in ['84.7', '0', '100']:
            row = self.row(loss, TG_locator='PDFp4 TableIII', source_weight_loss_definition=f'Weight loss (%) at {self.temperature} C')
            display = reader.reading_row(row, {'scope_class': 'textile_cloth'})
            self.assertEqual(display[10], '')
            self.assertIn(f'原文{self.temperature}℃失重（%）=' + loss, display[20])
            self.assertIn(f'Weight loss (%) at {self.temperature} C', display[20])
            self.assertEqual(display[17], 'PDFp4 TableIII')
            self.assertNotIn('15.3', str(display))
            self.assertEqual(len(display), 25)


class ReportedWeightLoss500Tests(ReportedWeightLossTests):
    temperature = 500
    field = 'source_weight_loss_500_pct'
