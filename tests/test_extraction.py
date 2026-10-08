"""Offline extraction regression tests; every source and clock is controlled."""
from contextlib import ExitStack, redirect_stdout
from datetime import datetime, timedelta, timezone
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import pandas as pd
import requests

from scripts import extract_tg_loi as extract
from scripts.pairing import measurement_fingerprint


NOW = datetime(2026, 9, 30, 5, 0, tzinfo=timezone.utc)
FULL_TEXT = 'Cotton fabric. TGA was performed in nitrogen at a heating rate of 10 °C/min.'
REVIEWED = {
    'pairing_status': 'verified_exact',
    'pairing_evidence': 'Fixture review: both tables refer to the same cotton fabric treatment and washing state.',
    'material_form_TGA': 'fabric',
    'material_form_LOI': 'fabric',
    'numeric_evidence_type': 'tabulated',
    'evidence_reviewed_by': 'Unit-test reviewer',
}


def tables(loi_sample='Cotton_A', tg_sample='Cotton_A', washes=('',)):
    result = []
    for washing in washes:
        result.append((f'LOI of cotton fabrics {washing}', pd.DataFrame({
            'Sample': [loi_sample], 'LOI (%)': [28.5]})))
        result.append((f'TGA of cotton fabrics {washing} in nitrogen; heating rate 10 °C/min', pd.DataFrame({
            'Sample': [tg_sample], 'Tmax1 (°C)': [350.0], 'Residue at 600 °C (%)': [18.2]})))
    return result


def source_result(**kwargs):
    return extract.SourceResult(FULL_TEXT, tables(**kwargs), 'https://europepmc.org/articles/PMC12345')


class PeakHeaderTests(unittest.TestCase):
    def test_generic_names_do_not_invent_a_stage_or_rate_criterion(self):
        for heading in ['Tmax (°C)', 'Tdmax (°C)', 'Tpeak (°C)', 'peak decomposition temperature (°C)',
                        'water peak temperature (°C)', 'hydroxyl peak temperature (°C)',
                        'water Tmax1 (°C)', 'dehydroxylation second peak (°C)']:
            with self.subTest(heading=heading):
                self.assertEqual(extract.tgfield(heading), 'source_raw_Tmax_C')
        for heading in ['Tmax1 (°C)', 'Tmax2 (°C)', 'Tmax3 (°C)', 'Tmax4 (°C)',
                               'Tdmax1 (°C)', 'Tdmax2 (°C)']:
            expected = 'Tmax' + heading.split('max')[1][0] + '_C'
            self.assertEqual(extract.tgfield(heading), expected)
        self.assertNotEqual(extract.tgfield('Tmax10 (°C)'), 'Tmax1_C')

    def test_distinct_generic_header_values_are_not_silently_keep_last(self):
        parsed = extract.tg_rows(FULL_TEXT, [('TGA table in nitrogen', pd.DataFrame({
            'Sample': ['A'], 'Tmax (°C)': [350], 'Tpeak (°C)': [370]}))])
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]['source_raw_Tmax_C'], '')
        originals = json.loads(parsed[0]['source_raw_Tmax_header_values_json'])
        self.assertEqual([v['literal'] for v in originals], ['350', '370'])
        self.assertNotIn('Tmax1_C', parsed[0])


class ExtractionMainTests(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.root = Path(self.stack.enter_context(tempfile.TemporaryDirectory()))
        data = self.root / 'data'
        auto = data / 'automation'
        incoming = data / 'incoming'
        auto.mkdir(parents=True)
        incoming.mkdir()
        paths = {
            'ROOT': self.root, 'DATA': data, 'AUTO': auto, 'INC': incoming,
            'CAND': auto / 'candidate_extractions.csv',
            'EXT': auto / 'auto_extracted.csv', 'REVIEW': auto / 'review_queue.csv',
            'STATE': auto / 'auto_extract_state.json', 'MASTER': data / 'tg_loi_master.csv',
            'PAIR_REVIEWS': data / 'curation' / 'pair_reviews.csv',
        }
        for name, value in paths.items():
            self.stack.enter_context(patch.object(extract, name, value))
        self.clock = self.stack.enter_context(patch.object(extract, 'utcnow', return_value=NOW))
        self.review = self.stack.enter_context(patch.object(extract, 'reviewed_metadata', return_value={}))
        self.stack.enter_context(patch.dict('os.environ', {'AUTO_MAX_CANDIDATES': '25'}))
        self.stack.enter_context(patch.object(extract.requests, 'get', side_effect=AssertionError('Network is forbidden in extraction tests')))
        self.candidate = {
            'DOI': '10.1234/cotton', 'title': 'Flame-retardant cotton fabric',
            'year': '2026', 'journal': 'Fixture Journal', 'candidate_score': '10',
            'fulltext_url': 'https://europepmc.org/articles/PMC12345',
            'oa_url': 'https://www.mdpi.com/fixture', 'landing_url': 'https://doi.org/10.1234/cotton',
            'LOI_numeric_evidence': 'LOI table', 'TG_numeric_evidence': 'TGA table',
            'supplementary_links': '[]', 'table_candidates': '[]', 'abstract_excerpt': 'Cotton fabric tests',
        }
        self.write_candidates([self.candidate])

    def write_candidates(self, candidates):
        pd.DataFrame(candidates).to_csv(extract.CAND, index=False)

    def run_main(self, result=None, error=None):
        with patch.object(extract, 'source', return_value=result, side_effect=error) as source, redirect_stdout(StringIO()):
            extract.main()
        return source

    def approve(self, metadata=None):
        metadata = REVIEWED if metadata is None else metadata
        self.review.side_effect = lambda row: {**metadata, 'reviewed_measurement_fingerprint': measurement_fingerprint(row)}

    def state(self):
        return json.loads(extract.STATE.read_text())['processed'][self.candidate['DOI']]

    def extracted(self):
        return pd.read_csv(extract.EXT, dtype=str).fillna('')

    def snapshot(self):
        return {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in
                [extract.STATE, extract.EXT, extract.REVIEW] if p.exists()}

    def test_full_main_reviewed_positive_a_path_does_not_crash(self):
        self.approve()
        source = self.run_main(source_result())
        self.assertEqual(source.call_count, 1)
        self.assertEqual(self.state()['grade'], 'A')
        output = next(extract.INC.glob('verified_auto_*.csv'))
        rows = pd.read_csv(output)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows.iloc[0]['LOI_pct'], 28.5)
        self.assertEqual(rows.iloc[0]['Tmax1_C'], 350.0)
        self.assertEqual(rows.iloc[0]['washing_state'] if pd.notna(rows.iloc[0]['washing_state']) else '', '')
        self.assertEqual(rows.iloc[0]['pairing_status'], 'verified_exact')
        self.assertEqual(self.extracted().iloc[0]['grade'], 'A')

    def test_automatic_generic_peak_stays_raw_even_with_same_state_review(self):
        self.approve()
        generic = [('LOI of cotton fabrics', pd.DataFrame({'Sample': ['Cotton_A'], 'LOI (%)': [28.5]})),
                   ('TGA of cotton fabrics in nitrogen; heating rate 10 °C/min',
                    pd.DataFrame({'Sample': ['Cotton_A'], 'Tmax (°C)': [350.0]}))]
        self.run_main(extract.SourceResult(FULL_TEXT, generic, self.candidate['fulltext_url']))
        row = self.extracted().iloc[0]
        self.assertEqual(row['grade'], 'B')
        self.assertEqual(row['source_raw_Tmax_C'], '350.0')
        self.assertIn('not reviewed', row['source_Tmax_definition'])
        self.assertFalse(row.get('Tmax1_C', ''))
        self.assertFalse(row.get('Tmax_unnumbered_C', ''))
        self.assertFalse(list(extract.INC.glob('*.csv')))

    def test_labels_alone_remain_b_without_scientific_attestation(self):
        self.run_main(source_result())
        record = self.extracted().iloc[0]
        self.assertEqual(record['grade'], 'B')
        self.assertIn('same_state_review_pending', record['reason'])
        self.assertFalse(list(extract.INC.glob('*.csv')))

    def test_reviewed_different_forms_cannot_promote(self):
        self.approve({**REVIEWED, 'material_form_TGA': 'film'})
        self.run_main(source_result())
        self.assertEqual(self.extracted().iloc[0]['grade'], 'B')
        self.assertIn('specimen_form_mismatch', self.extracted().iloc[0]['reason'])
        self.assertFalse(list(extract.INC.glob('*.csv')))

    def test_same_reviewed_resin_forms_are_not_textile_evidence(self):
        self.approve({**REVIEWED, 'material_form_TGA': 'resin', 'material_form_LOI': 'resin'})
        self.run_main(source_result())
        self.assertEqual(self.extracted().iloc[0]['grade'], 'B')
        self.assertFalse(list(extract.INC.glob('*.csv')))

    def test_promotion_keeps_distinct_washing_states(self):
        self.approve()
        self.run_main(source_result(washes=('after 0 wash cycles', 'after 5 wash cycles')))
        output = next(extract.INC.glob('verified_auto_*.csv'))
        rows = pd.read_csv(output)
        self.assertEqual(len(rows), 2)
        self.assertEqual(set(rows['washing_state']), {'after 0 wash cycles', 'after 5 wash cycles'})
        self.assertEqual(len(self.extracted()), 2)

    def test_numeric_sample_labels_with_washing_are_not_discarded_or_leaked(self):
        self.approve()
        samples = ['Cotton_A after 5 wash cycles', 'Cotton_B']
        parsed = [
            ('LOI of cotton fabrics', pd.DataFrame({'Sample': samples, 'LOI (%)': [28.5, 29]})),
            ('TGA of cotton fabrics', pd.DataFrame({'Sample': samples, 'Tmax1 (°C)': [350, 360]})),
        ]
        self.run_main(extract.SourceResult(FULL_TEXT, parsed, self.candidate['fulltext_url']))
        rows = pd.read_csv(next(extract.INC.glob('verified_auto_*.csv')), dtype=str).fillna('')
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows['washing_state'].tolist(), ['after 5 wash cycles', ''])
        self.assertEqual(rows['sample_state'].tolist(), samples)

    def test_washing_group_headers_still_apply_to_following_rows(self):
        samples = ['after 5 wash cycles', 'Cotton_A']
        parsed = [
            ('LOI of cotton fabrics', pd.DataFrame({'Sample': samples, 'LOI (%)': ['', 28.5]})),
            ('TGA of cotton fabrics', pd.DataFrame({'Sample': samples, 'Tmax1 (°C)': ['', 350]})),
        ]
        self.run_main(extract.SourceResult(FULL_TEXT, parsed, self.candidate['fulltext_url']))
        rows = self.extracted()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows.iloc[0]['sample_state'], 'Cotton_A')
        self.assertEqual(rows.iloc[0]['washing_state'], 'after 5 wash cycles')

    def test_existing_unwashed_master_does_not_suppress_washed_pair(self):
        self.approve()
        pd.DataFrame([{
            'DOI': self.candidate['DOI'], 'sample_state': 'Cotton_A', 'washing_state': 'after 0 wash cycles',
            'atmosphere': 'N2', 'heating_rate_C_min': '10',
        }]).to_csv(extract.MASTER, index=False)
        self.run_main(source_result(washes=('after 0 wash cycles', 'after 5 wash cycles')))
        rows = pd.read_csv(next(extract.INC.glob('verified_auto_*.csv')))
        self.assertEqual(rows['washing_state'].tolist(), ['after 5 wash cycles'])

    def test_disjoint_washing_states_do_not_pair(self):
        self.approve()
        parsed = [tables(washes=('after 0 wash cycles',))[0], tables(washes=('after 5 wash cycles',))[1]]
        self.run_main(extract.SourceResult(FULL_TEXT, parsed, self.candidate['fulltext_url']))
        self.assertEqual(self.state()['reason_code'], 'no_exact_pair')
        self.assertFalse(self.state()['retryable'])
        self.assertFalse(list(extract.INC.glob('*.csv')))

    def test_punctuation_distinct_labels_do_not_pair(self):
        for left, right in [('A_B', 'AB'), ('A:B', 'AB'), ('A B', 'AB'), ('A+B', 'AB'), ('A-B', 'AB')]:
            self.assertNotEqual(extract.ns(left), extract.ns(right))
        self.run_main(source_result(loi_sample='A_B', tg_sample='AB'))
        self.assertEqual(self.state()['reason_code'], 'no_exact_pair')
        self.assertEqual(self.extracted()['grade'].tolist(), ['C'])

    def test_fetch_failure_retries_only_after_cooldown_without_duplicate_history(self):
        result = extract.SourceResult(failures=['fetch_error'])
        self.run_main(result)
        state = self.state()
        self.assertTrue(state['retryable'])
        self.assertEqual(state['reason_code'], 'fetch_error')
        self.assertEqual(state['next_retry_utc'], (NOW + timedelta(hours=6)).isoformat())
        before = self.snapshot()
        self.assertEqual(self.run_main(result).call_count, 0)
        self.assertEqual(self.snapshot(), before)
        self.clock.return_value = NOW + timedelta(hours=6)
        self.assertEqual(self.run_main(result).call_count, 1)
        state = self.state()
        self.assertEqual(state['attempt_count'], 2)
        self.assertEqual(state['next_retry_utc'], (NOW + timedelta(hours=18)).isoformat())
        self.assertEqual(len(self.extracted()), 1)
        self.assertEqual(extract.EXT.read_bytes(), before[extract.EXT][0])
        self.assertEqual(extract.REVIEW.stat().st_mtime_ns, before[extract.REVIEW][1])

    def test_raised_fetch_and_parse_failures_get_retryable_state(self):
        self.run_main(error=requests.Timeout('fixture'))
        self.assertEqual(self.state()['reason_code'], 'fetch_error')
        self.clock.return_value = NOW + timedelta(hours=6)
        self.run_main(error=ValueError('fixture parser error'))
        self.assertEqual(self.state()['reason_code'], 'parse_error')
        self.assertTrue(self.state()['retryable'])

    def test_partial_parse_failure_is_not_terminal_absence(self):
        result = extract.SourceResult(FULL_TEXT, tables(loi_sample='A', tg_sample='B'), 'https://www.mdpi.com/fixture', ['parse_error'])
        self.run_main(result)
        self.assertEqual(self.state()['reason_code'], 'parse_error')
        self.assertTrue(self.state()['retryable'])

    def test_partial_parse_with_useful_pair_is_retained_and_retried(self):
        result = extract.SourceResult(FULL_TEXT, tables(), self.candidate['fulltext_url'], ['parse_error'])
        self.run_main(result)
        self.assertEqual(self.extracted().iloc[0]['grade'], 'B')
        self.assertEqual(self.state()['reason_code'], 'partial_source_failure')
        self.assertTrue(self.state()['retryable'])
        self.clock.return_value = NOW + timedelta(hours=6)
        self.assertEqual(self.run_main(source_result()).call_count, 1)
        self.assertFalse(self.state()['retryable'])

    def test_genuine_no_pair_stays_terminal_until_input_changes(self):
        result = source_result(loi_sample='A', tg_sample='B')
        self.run_main(result)
        before = self.snapshot()
        self.clock.return_value = NOW + timedelta(days=365)
        self.assertEqual(self.run_main(result).call_count, 0)
        self.assertEqual(before, self.snapshot())
        self.candidate['oa_url'] = 'https://www.mdpi.com/new-evidence'
        self.write_candidates([self.candidate])
        self.assertEqual(self.run_main(result).call_count, 1)
        self.assertEqual(self.state()['attempt_count'], 1)
        self.assertEqual(len(self.extracted()), 2)

    def test_version_change_reprocesses_terminal_candidate_preserving_old_evidence(self):
        self.run_main(source_result(loi_sample='A', tg_sample='B'))
        old = self.extracted().iloc[0].to_dict()
        with patch.object(extract, 'EXTRACTOR_VERSION', 'next-version'):
            self.assertEqual(self.run_main(source_result()).call_count, 1)
        records = self.extracted()
        self.assertEqual(len(records), 2)
        self.assertEqual(records.iloc[0]['candidate_fingerprint'], old['candidate_fingerprint'])
        self.assertEqual(records.iloc[0]['extracted_at_utc'], old['extracted_at_utc'])
        self.assertEqual(records.iloc[1]['extractor_version'], 'next-version')

    def test_new_review_registry_invalidates_cached_candidate(self):
        self.run_main(source_result())
        self.assertEqual(self.run_main(source_result()).call_count, 0)
        extract.PAIR_REVIEWS.parent.mkdir(parents=True)
        extract.PAIR_REVIEWS.write_text('Fixture review registry changed\n')
        self.approve()
        self.assertEqual(self.run_main(source_result()).call_count, 1)
        self.assertEqual(self.state()['grade'], 'A')

    def test_all_urls_and_evidence_but_not_harvest_bookkeeping_change_fingerprint(self):
        original = extract.fp(self.candidate)
        for field in ['fulltext_url', 'oa_url', 'landing_url', 'LOI_numeric_evidence', 'TG_numeric_evidence',
                      'supplementary_links', 'table_candidates', 'abstract_excerpt', 'title', 'new_evidence_field']:
            with self.subTest(field=field):
                self.assertNotEqual(original, extract.fp({**self.candidate, field: 'changed'}))
        self.assertEqual(original, extract.fp({**self.candidate, '_score': 999, 'harvest_run': 100, 'harvest_cycle': 5}))

    def test_legacy_c_is_reclassified_instead_of_permanently_skipped(self):
        extract.STATE.write_text(json.dumps({'version': 1, 'processed': {
            self.candidate['DOI']: {'fingerprint': extract.fp(self.candidate), 'grade': 'C'}
        }}))
        self.assertEqual(self.run_main(source_result()).call_count, 1)
        self.assertEqual(self.state()['grade'], 'B')

    def test_corrupt_state_fails_without_touching_state_or_outputs(self):
        self.run_main(source_result())
        invalid_states = [
            b'{broken json', b'[]', b'{}', b'{"processed": []}',
            b'{"processed": {"10.1234/cotton": []}}',
            b'{"processed": {"10.1234/cotton": {"fingerprint": 3}}}',
            b'{"processed": {"10.1234/cotton": {"grade": []}}}',
            b'{"processed": {"10.1234/cotton": {"retryable": "false"}}}',
        ]
        for contents in invalid_states:
            with self.subTest(contents=contents):
                extract.STATE.write_bytes(contents)
                before = self.snapshot()
                with patch.object(extract, 'source') as source, self.assertRaisesRegex(ValueError, 'refusing to reset existing history'):
                    extract.main()
                source.assert_not_called()
                self.assertEqual(self.snapshot(), before)

    def test_versionless_legacy_state_preserves_other_processed_entries(self):
        old_entry = {'fingerprint': 'historical', 'grade': 'A'}
        extract.STATE.write_text(json.dumps({'processed': {'10.1234/older': old_entry}}))
        self.assertEqual(self.run_main(source_result()).call_count, 1)
        state = json.loads(extract.STATE.read_text())
        self.assertEqual(state['processed']['10.1234/older'], old_entry)
        self.assertEqual(state['version'], extract.STATE_VERSION)

    def test_retry_delay_is_bounded_without_terminal_retry_exhaustion(self):
        previous = {'fingerprint': 'same', 'attempt_count': 999999}
        entry = extract.attempt_state(previous, 'same', 'C', 'fetch_error', True, NOW)
        self.assertLessEqual(entry['attempt_count'], 32)
        self.assertEqual(entry['next_retry_utc'], (NOW + timedelta(days=7)).isoformat())
        self.assertFalse(extract.retry_due(entry, 'same', NOW + timedelta(days=6)))
        self.assertTrue(extract.retry_due(entry, 'same', NOW + timedelta(days=7)))

    def test_batch_limit_still_bounds_retry_work(self):
        self.write_candidates([{**self.candidate, 'DOI': f'10.1234/cotton{i}'} for i in range(4)])
        with patch.dict('os.environ', {'AUTO_MAX_CANDIDATES': '2'}):
            self.assertEqual(self.run_main(extract.SourceResult(failures=['fetch_error'])).call_count, 2)
        self.assertEqual(len(json.loads(extract.STATE.read_text())['processed']), 2)


class SourceDiagnosticsTests(unittest.TestCase):
    def test_pmc_transport_failure_is_reported(self):
        with patch.object(extract.requests, 'get', side_effect=requests.Timeout('fixture')):
            result = extract.pmc('10.1234/fixture')
        self.assertEqual(result.failures, ('fetch_error',))
        self.assertEqual(tuple(result), ('', [], ''))

    def test_html_parse_failure_is_reported_without_network(self):
        response = Mock()
        response.headers = {'content-type': 'text/html'}
        response.text = '<html><p>Thermal table</p><table><tr><td>bad</td></tr></table></html>'
        with patch.object(extract.requests, 'get', return_value=response), patch.object(extract.pd, 'read_html', side_effect=ValueError('fixture')):
            result = extract.html('https://www.mdpi.com/fixture')
        self.assertIn('parse_error', result.failures)
        self.assertEqual(result[1], [])

    def test_html_partial_table_parse_keeps_failure_marker(self):
        response = Mock()
        response.headers = {'content-type': 'text/html'}
        response.text = '<html><table><tr><td>a</td></tr></table><table><tr><td>b</td></tr></table></html>'
        with patch.object(extract.requests, 'get', return_value=response), patch.object(extract.pd, 'read_html', side_effect=[[pd.DataFrame({'Sample': ['A']})], ValueError('fixture')]):
            result = extract.html('https://www.mdpi.com/fixture')
        self.assertIn('parse_error', result.failures)
        self.assertEqual(len(result[1]), 1)


if __name__ == '__main__':
    unittest.main()
