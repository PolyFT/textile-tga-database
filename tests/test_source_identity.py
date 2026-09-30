"""Offline, fail-closed source-identity regressions. Every source below is synthetic."""
import contextlib
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from scripts import pairing as p
from scripts import source_identity as si
from scripts import validate_tg_loi as v
from scripts import review_b_tg_loi as b
from scripts import extract_tg_loi as e


def source(name='one', **changes):
    entry = {
        'stable_source_id': 'proceedings:example.test:' + name,
        'source_type': 'original_conference_proceedings',
        'publication_identifier': 'Synthetic Proceedings 2000, paper ' + name + ', pp. 1-5',
        'documents': [{'version': 'original-v1', 'original_primary': True,
                       'primary_source_url': 'https://example.test/' + name + '.pdf',
                       'primary_document_sha256': hashlib.sha256(name.encode()).hexdigest(),
                       'url_aliases': []}],
    }
    entry.update(changes)
    return sign(entry)


def sign(entry):
    entry['identity_review'] = {'approved': True, 'reviewer': 'Fixture reviewer',
                                'reviewed_at': '2000-01-01',
                                'evidence': 'Original proceedings, citation and document bytes verified.',
                                'binding_sha256': si.identity_binding(entry)}
    return entry


def observation(entry=None, **changes):
    entry = entry or source()
    document = entry['documents'][0]
    row = {'DOI': '', 'stable_source_id': entry['stable_source_id'],
           'source_type': entry['source_type'], 'publication_identifier': entry['publication_identifier'],
           'primary_document_version': document['version'],
           'primary_source_url': document['primary_source_url'],
           'primary_document_sha256': document['primary_document_sha256'],
           'TG_locator': 'p. 3, Table 2, Fabric A, Tmax column',
           'LOI_locator': 'p. 4, Table 3, Fabric A, LOI column',
           'conditions_locator': 'p. 2, Methods, TGA paragraph: N2, 10 C/min',
           'sample_state': 'Fabric A', 'washing_state': 'as prepared',
           'atmosphere': 'N2', 'heating_rate_C_min': '10',
           'LOI_pct': '25', 'Tmax1_C': '340', 'material_form': 'woven fabric',
           'direct_numeric_use': 'TG+LOI', 'source_url': document['primary_source_url'],
           'source_location': 'pp. 2-4, Methods and Tables 2-3'}
    row.update(changes)
    return row


def approval(row, **changes):
    review = dict(row, pairing_status='verified_exact',
                  pairing_evidence='Fabric A, unwashed woven fabric, explicitly mapped in Tables 2-3.',
                  material_form_TGA='woven fabric', material_form_LOI='woven fabric',
                  numeric_evidence_type='tabulated', evidence_reviewed_by='Fixture reviewer',
                  evidence_reviewed_at='2000-01-01', source_review_approved='true',
                  measurement_fingerprint=p.measurement_fingerprint(row))
    review.update(changes)
    return review


class SourceIdentityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.registry_path = self.root / 'sources.json'
        self.review_path = self.root / 'reviews.csv'
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        # Both package and direct-script imports are supported by the repository.
        for name in ['scripts.source_identity', 'source_identity']:
            module = sys.modules.get(name)
            if module:
                self.stack.enter_context(patch.object(module, 'REGISTRY', self.registry_path))
        for name in ['scripts.pairing', 'pairing']:
            module = sys.modules.get(name)
            if module:
                self.stack.enter_context(patch.object(module, 'REVIEWS', self.review_path))
        self.stack.enter_context(patch.object(v, 'REGISTRY', self.registry_path))
        self.stack.enter_context(patch.object(e.requests, 'get', side_effect=AssertionError('No network in fixtures')))
        self.entries = [source()]
        self.registry(self.entries)

    def registry(self, entries):
        self.registry_path.write_text(json.dumps({'schema_version': 1, 'sources': entries}))

    def reviews(self, rows, **changes):
        pd.DataFrame([approval(row, **changes) for row in rows]).to_csv(self.review_path, index=False)

    def build(self, rows, issues=None):
        return v.build_tables(pd.DataFrame(rows), issues)

    def assert_held(self, rows, reason=None):
        master, candidates, _, report = self.build(rows)
        self.assertTrue(master.empty)
        self.assertEqual(report['verified_exact_sources'], 0)
        if reason:
            self.assertIn(reason, candidates.iloc[0].review_reasons)
        return candidates

    def test_exact_registry_bound_review_is_admitted_and_reports_disjoint_cohorts(self):
        row = observation()
        self.reviews([row])
        doi = observation(DOI='10.1234/fixture', stable_source_id='', primary_source_url='',
                          primary_document_sha256='', source_url='https://example.test/doi-paper')
        doi = approval(doi)
        doi['reviewed_measurement_fingerprint'] = p.measurement_fingerprint(doi)
        master, _, _, report = self.build([row, doi])
        self.assertEqual(len(master), 2)
        self.assertEqual(p.source_identity(row), 'source:proceedings:example.test:one')
        self.assertEqual(report['verified_exact_dois'], 1)
        self.assertEqual(report['verified_non_doi_sources'], 1)
        self.assertEqual(report['verified_exact_sources'], 2)
        for unit in ['condition_records', 'sample_states']:
            self.assertEqual(report['verified_doi_' + unit], 1)
            self.assertEqual(report['verified_non_doi_' + unit], 1)
            self.assertEqual(report['verified_exact_' + unit], 2)

    def test_distinct_publications_identical_labels_never_merge(self):
        entries = [source('one'), source('two')]
        self.registry(entries)
        rows = [observation(entry) for entry in entries]
        self.reviews(rows)
        master, _, _, report = self.build(rows)
        self.assertEqual(len(master), 2)
        self.assertEqual(report['verified_exact_sample_states'], 2)
        self.assertEqual(report['verified_non_doi_sources'], 2)
        self.assertNotEqual(p.pair_key(rows[0]), p.pair_key(rows[1]))

    def test_repeated_conditions_count_one_state(self):
        rows = [observation(), observation(atmosphere='air', heating_rate_C_min='20',
                conditions_locator='p. 2, Methods: air, 20 C/min')]
        self.reviews(rows)
        _, _, _, report = self.build(rows)
        self.assertEqual(report['verified_non_doi_condition_records'], 2)
        self.assertEqual(report['verified_non_doi_sample_states'], 1)
        self.assertEqual(report['verified_exact_dois'], 0)

    def test_missing_unregistered_and_invalid_ids_are_held(self):
        for value in ['', 'proceedings:example.test:unknown', 'https://example.test/paper']:
            with self.subTest(value=value):
                row = observation(stable_source_id=value)
                self.reviews([row])
                self.assert_held([row])
                self.assertEqual(p.source_identity(row), '')

    def test_missing_and_invalid_document_bindings_are_held(self):
        for field in si.PROVENANCE_FIELDS:
            with self.subTest(missing=field):
                row = observation(**{field: ''})
                self.reviews([row])
                self.assert_held([row])
        for field, value in [('primary_source_url', 'https://example.test/other.pdf'),
                             ('primary_document_sha256', 'bad hash'),
                             ('primary_document_sha256', 'f' * 64),
                             ('primary_document_version', 'unknown'),
                             ('source_url', 'https://unreviewed.test/mirror')]:
            with self.subTest(field=field, value=value):
                row = observation(**{field: value})
                self.reviews([row])
                self.assert_held([row])

    def test_malformed_original_and_mirror_urls_are_held(self):
        for url in ['https://example.test:bad/a', 'https://example.test:65536/a',
                    'https://exa mple.test/a', 'https://example.test/a b',
                    'https://exa\nmple.test/a', 'https://example.test/a\x00b',
                    'https://example.test\\evil/a']:
            for field in ['primary_source_url', 'url_aliases']:
                entry = source()
                entry['documents'][0][field] = [url] if field == 'url_aliases' else url
                self.registry([sign(entry)])
                row = observation(entry)
                self.reviews([row])
                with self.subTest(url=url, field=field):
                    self.assertFalse(si.valid_url(url))
                    self.assert_held([row], 'invalid_registered_document')

    def test_missing_false_string_or_stale_identity_approval_is_held(self):
        for value in [None, False, 'true']:
            entry = source()
            entry['identity_review']['approved'] = value
            self.registry([entry])
            row = observation(entry)
            self.reviews([row])
            self.assert_held([row], 'source_identity_review_pending_or_stale')
        entry = source()
        entry['publication_identifier'] += ' changed'
        self.registry([entry])
        row = observation(entry)
        self.reviews([row])
        self.assert_held([row], 'source_identity_review_pending_or_stale')

    def test_inline_approval_never_bypasses_missing_false_or_duplicate_pair_review(self):
        row = observation()
        inline = approval(row)
        inline['reviewed_measurement_fingerprint'] = p.measurement_fingerprint(row)
        self.assert_held([inline], 'non_doi_registry_review_pending_or_stale')
        for fields in [{'source_review_approved': ''}, {'source_review_approved': 'false'},
                       {'pairing_status': 'rejected'}, {'evidence_reviewed_at': ''},
                       {'pairing_evidence': ''}, {'material_form_TGA': ''}]:
            with self.subTest(fields=fields):
                self.reviews([row], **fields)
                self.assert_held([inline])
                self.assertTrue(p.evidence_issues(inline))
        pd.DataFrame([approval(row), approval(row)]).to_csv(self.review_path, index=False)
        self.assert_held([inline], 'non_doi_registry_review_pending_or_stale')

    def test_measurements_conditions_and_provenance_changes_invalidate_review(self):
        row = observation()
        self.reviews([row])
        changes = {'LOI_pct': '26', 'Tmax1_C': '350', 'LOI_uncertainty_pct': '0.2',
                   'residue_temp_C': '600', 'sample_state': 'Fabric B',
                   'washing_state': 'washed', 'atmosphere': 'air', 'heating_rate_C_min': '20',
                   'TG_locator': 'Table 4', 'LOI_locator': 'Table 5',
                   'conditions_locator': 'Other method', 'source_location': 'Other page',
                   'primary_document_sha256': 'c' * 64, 'primary_source_url': 'https://example.test/new'}
        for field, value in changes.items():
            with self.subTest(field=field):
                changed = dict(row, **{field: value})
                inline = approval(changed)
                inline['reviewed_measurement_fingerprint'] = p.measurement_fingerprint(changed)
                self.assert_held([inline])
        # Even a freshly approved replacement identity cannot reuse old pair review.
        entry = source()
        entry['documents'][0]['url_aliases'] = ['https://example.test/mirror.pdf']
        self.registry([sign(entry)])
        self.assert_held([row], 'non_doi_registry_review_pending_or_stale')

    def test_reviewed_mirror_uses_same_identity_and_counts_once(self):
        entry = source()
        entry['documents'][0]['url_aliases'] = ['https://example.test/mirror.pdf']
        self.registry([sign(entry)])
        rows = [observation(entry), observation(entry, source_url='https://example.test/mirror.pdf')]
        self.reviews(rows)
        _, candidates, _, report = self.build(rows)
        self.assertEqual(len(candidates), 2)
        self.assertEqual(report['verified_exact_sources'], 1)
        self.assertEqual(report['verified_exact_condition_records'], 1)
        self.assertEqual(report['verified_exact_sample_states'], 1)

    def test_reuse_of_url_hash_or_publication_under_new_id_is_held(self):
        for reuse in ['url', 'hash', 'publication', 'id']:
            one, two = source('one'), source('two')
            if reuse == 'id':
                two['stable_source_id'] = one['stable_source_id']
            elif reuse == 'publication':
                two['publication_identifier'] = one['publication_identifier']
            else:
                key = 'primary_source_url' if reuse == 'url' else 'primary_document_sha256'
                two['documents'][0][key] = one['documents'][0][key]
            self.registry([one, sign(two)])
            rows = [observation(one), observation(two)]
            self.reviews(rows)
            with self.subTest(reuse=reuse):
                self.assert_held(rows)

    def test_explicit_alias_and_later_doi_migrations_are_held_without_doublecount(self):
        canonical = source()
        alias = copy.deepcopy(canonical)
        alias.update(stable_source_id='proceedings:example.test:alias', alias_of=canonical['stable_source_id'])
        self.registry([canonical, sign(alias)])
        rows = [observation(canonical), observation(alias)]
        self.reviews(rows)
        master, candidates, _, report = self.build(rows)
        self.assertEqual(len(master), 1)
        self.assertEqual(report['verified_exact_sources'], 1)
        self.assertIn('source_alias_migration_required', candidates.iloc[1].review_reasons)
        canonical['doi_alias'] = '10.1234/later'
        self.registry([sign(canonical)])
        doi = observation(canonical, DOI='10.1234/later')
        doi = approval(doi)
        doi['reviewed_measurement_fingerprint'] = p.measurement_fingerprint(doi)
        row = observation(canonical)
        self.reviews([row])
        master, _, _, report = self.build([row, doi])
        self.assertEqual(len(master), 1)
        self.assertEqual(report['verified_exact_dois'], 1)
        self.assertEqual(report['verified_non_doi_sources'], 0)
        self.assertTrue(master.iloc[0].pair_key.startswith('10.1234/later||'))

    def test_unmapped_later_doi_or_reused_document_never_counts_twice(self):
        row = observation()
        self.reviews([row])
        doi = approval(observation(DOI='10.1234/later'))
        doi['reviewed_measurement_fingerprint'] = p.measurement_fingerprint(doi)
        candidates = self.assert_held([row, doi])
        self.assertIn('source_doi_reuse_review_required', candidates.iloc[0].review_reasons)
        self.assertIn('source_doi_mapping_review_required', candidates.iloc[1].review_reasons)
        # A legacy DOI row without the stable ID retains its identity; only the
        # reused non-DOI observation is held until curation establishes a mapping.
        doi['stable_source_id'] = ''
        master, candidates, _, report = self.build([row, doi])
        self.assertEqual(len(master), 1)
        self.assertEqual(report['verified_exact_sources'], 1)
        self.assertIn('source_doi_reuse_review_required', candidates.iloc[0].review_reasons)

    def test_legacy_doi_fulltext_urls_hold_reused_non_doi_documents(self):
        row = observation()
        self.reviews([row])
        for field in ['fulltext_url', 'additional_fulltext_url']:
            doi = approval(observation(DOI='10.1234/later', stable_source_id='',
                           primary_source_url='', primary_document_sha256='',
                           source_url='https://doi.org/10.1234/later',
                           **{field: row['primary_source_url']}))
            doi['reviewed_measurement_fingerprint'] = p.measurement_fingerprint(doi)
            with self.subTest(field=field):
                master, candidates, _, report = self.build([row, doi])
                self.assertEqual(len(master), 1)
                self.assertEqual(report['verified_exact_sources'], 1)
                self.assertIn('source_doi_reuse_review_required', candidates.iloc[0].review_reasons)

    def test_all_registered_mirrors_and_versions_hold_legacy_doi_collisions(self):
        entry = source()
        entry['documents'][0]['url_aliases'] = ['https://example.test/mirror.pdf']
        entry['documents'].append({
            'version': 'original-v2', 'original_primary': True,
            'primary_source_url': 'https://example.test/v2.pdf',
            'primary_document_sha256': hashlib.sha256(b'new document bytes').hexdigest(),
            'url_aliases': ['https://example.test/v2-mirror.pdf'],
        })
        self.registry([sign(entry)])
        row = observation(entry)  # Only version 1's original URL occurs on this row.
        self.reviews([row])
        for url in ['https://example.test/mirror.pdf', 'https://example.test/v2.pdf',
                    'https://example.test/v2-mirror.pdf']:
            for field in ['source_url', 'fulltext_url', 'additional_fulltext_url']:
                changes = {'DOI': '10.1234/later', 'stable_source_id': '',
                           'primary_source_url': '', 'primary_document_sha256': '',
                           'source_url': 'https://doi.org/10.1234/later', field: url}
                doi = approval(observation(**changes))
                doi['reviewed_measurement_fingerprint'] = p.measurement_fingerprint(doi)
                with self.subTest(url=url, field=field):
                    master, candidates, _, report = self.build([row, doi])
                    self.assertEqual(len(master), 1)
                    self.assertEqual(report['verified_exact_sources'], 1)
                    self.assertEqual(report['verified_exact_sample_states'], 1)
                    self.assertEqual(report['verified_non_doi_sources'], 0)
                    self.assertIn('source_doi_reuse_review_required', candidates.iloc[0].review_reasons)
        # The alternative document's bytes also identify a collision even if
        # the DOI row has no registered URL or stable ID.
        doi = approval(observation(DOI='10.1234/later', stable_source_id='',
                       primary_source_url='', source_url='https://doi.org/10.1234/later',
                       primary_document_sha256=entry['documents'][1]['primary_document_sha256']))
        doi['reviewed_measurement_fingerprint'] = p.measurement_fingerprint(doi)
        master, candidates, _, _ = self.build([row, doi])
        self.assertEqual(len(master), 1)
        self.assertIn('source_doi_reuse_review_required', candidates.iloc[0].review_reasons)

    def test_known_issues_are_scoped_to_source_never_blank_doi(self):
        entries = [source('one'), source('two')]
        self.registry(entries)
        rows = [observation(entry) for entry in entries]
        self.reviews(rows)
        issues = [{'DOI': '', 'stable_source_id': entries[0]['stable_source_id'],
                   'sample_state': '*', 'status': 'open', 'reason_code': 'possible_sample_alias'},
                  {'DOI': '', 'sample_state': '*', 'status': 'open', 'reason_code': 'blank_scope'}]
        master, _, quarantine, _ = self.build(rows, issues)
        self.assertEqual(len(master), 1)
        self.assertEqual(master.iloc[0].stable_source_id, entries[1]['stable_source_id'])
        self.assertEqual(len(quarantine), 1)
        self.assertNotIn('blank_scope', quarantine.iloc[0].review_reasons)

    def test_grade_b_grouping_preserves_non_doi_sources_and_does_not_fetch(self):
        self.registry([source('one'), source('two')])
        rows = [observation(source('one')), observation(source('two'))]
        rows = [dict(row, grade='B', extractor_version=str(i + 5),
                     title='Flame-retardant woven cotton fabric') for i, row in enumerate(rows)]
        self.assertEqual(len(b.latest_b_rows(pd.DataFrame(rows))), 2)
        for row in rows + [dict(rows[0], DOI='source:proceedings:example.test:one')]:
            self.assertEqual(b.get_text(row['DOI']), ('', ''))
            self.assertIn('non_doi_manual_review_required', e.source(row).failures)
        queue = self.root / 'queue.csv'
        pd.DataFrame(rows).to_csv(queue, index=False)
        with patch.object(b, 'REVIEW', queue), patch.object(b, 'STATE', self.root / 'state.json'), \
             patch.object(b, 'MASTER', self.root / 'master.csv'), \
             patch.object(b, 'get_text', side_effect=AssertionError('Non-DOI fetch')), \
             contextlib.redirect_stdout(__import__('io').StringIO()):
            b.main()
        self.assertFalse((self.root / 'state.json').exists())

    def test_registry_changes_invalidate_snapshot_digest(self):
        with patch.object(v, 'ROOT', self.root), patch.object(v, 'DATA', self.root), \
             patch.object(v, 'ISSUES', self.root / 'issues.csv'), \
             patch.object(v, 'input_paths', return_value=[]):
            before = v.snapshot_digest()
            self.registry([source('two')])
            self.assertNotEqual(before, v.snapshot_digest())

    def test_malformed_registry_fails_before_publishing(self):
        self.registry_path.write_text('{broken')
        with self.assertRaises(json.JSONDecodeError):
            self.build([observation(DOI='10.1234/test')])

    def test_invalid_registry_documents_are_held_without_crashing(self):
        for documents in [None, {}, [], [None], [{'version': 'original-v1', 'url_aliases': None}]]:
            entry = source()
            entry['documents'] = documents
            self.registry([sign(entry)])
            row = observation()
            self.reviews([row])
            self.assert_held([row])


class LegacyDoiIdentityTests(unittest.TestCase):
    def test_old_normalized_api_and_fingerprints_are_byte_identical(self):
        row = observation(DOI='https://doi.org/10.1234/TEST')
        expected_key = p.normalized_pair_key(row['DOI'], row['sample_state'], row['washing_state'],
                                              row['atmosphere'], row['heating_rate_C_min'])
        expected_state = hashlib.sha256('10.1234/test||fabric a||as prepared'.encode()).hexdigest()[:20]
        expected_fp = hashlib.sha256(json.dumps({'pair_key': expected_key,
            'measurements': {'LOI_pct': '25', 'Tmax1_C': '340'}},
            sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        self.assertEqual(p.pair_key(row), expected_key)
        self.assertEqual(p.sample_state_id(row), expected_state)
        self.assertEqual(p.measurement_fingerprint(row), expected_fp)
        self.assertEqual(p.measurement_fingerprint(dict(row, TG_locator='changed')), expected_fp)

    def test_b71_doi_identities_and_scientific_counts_stay_fixed(self):
        master, _, _, report = v.build_tables(v.load_all(), v.issue_list())
        baseline_inputs = [
            'data/incoming/verified_source_batch_20260930_b38.csv',
            'data/incoming/verified_source_batch_20260930_b39.csv',
            'data/incoming/verified_source_batch_20260930_b40.csv',
            'data/incoming/verified_source_batch_20260930_b41_acsomega6c00738.csv',
            'data/incoming/verified_source_batch_20260930_b41_fib6020031_01.csv',
            'data/incoming/verified_source_batch_20260930_b41_fib6020031_02.csv',
            'data/incoming/verified_source_batch_20260930_b41_fib6020031_03.csv',
            'data/incoming/verified_source_batch_20260930_b41_fib6020031_04.csv',
            'data/incoming/verified_source_batch_20260930_b41_fib6040085.csv',
            'data/incoming/verified_source_batch_20260930_b41_polym11121969.csv',
            'data/incoming/verified_source_batch_20260930_b41_polym17070945.csv',
            'data/incoming/verified_source_batch_20260930_b41_polym17111529_01.csv',
            'data/incoming/verified_source_batch_20260930_b41_polym18060682.csv',
            'data/incoming/verified_source_batch_20260930_b42_acsomega.2c02466.csv',
            'data/incoming/verified_source_batch_20260930_b42_epoly-2020-0059.csv',
            'data/incoming/verified_source_batch_20260930_b42_ijms24021093.csv',
            'data/incoming/verified_source_batch_20260930_b42_nano12224048.csv',
            'data/incoming/verified_source_batch_20260930_b43_1528083716648761.csv',
            'data/incoming/verified_source_batch_20260930_b43_1528083718798636.csv',
            'data/incoming/verified_source_batch_20260930_b43_1528083720938158.csv',
            'data/incoming/verified_source_batch_20260930_b43_d1ra06573d.csv',
            'data/incoming/verified_source_batch_20260930_b44_1528083719881816.csv',
            'data/incoming/verified_source_batch_20260930_b44_briac123.36473663.csv',
            'data/incoming/verified_source_batch_20260930_b44_j.bhxbzr.2016.02.004.csv',
            'data/incoming/verified_source_batch_20260930_b44_pk.2018.42.2.157.csv',
            'data/incoming/verified_source_batch_20260930_b44_s41598-024-71071-5.csv',
            'data/incoming/verified_source_batch_20260930_b46_1528083704045848.csv',
            'data/incoming/verified_source_batch_20260930_b46_j.polymdegradstab.2024.110764.csv',
            'data/incoming/verified_source_batch_20260930_b48_acs_chas4c00050.csv',
            'data/incoming/verified_source_batch_20260930_b48_ajr163.csv',
            'data/incoming/verified_source_batch_20260930_b48_carrageenan.csv',
            'data/incoming/verified_source_batch_20260930_b48_casein20200904.csv',
            'data/incoming/verified_source_batch_20260930_b48_lttfd000213.csv',
            'data/incoming/verified_source_batch_20260930_b48_silk.csv',
            'data/incoming/verified_source_batch_20260930_b50_microwave.csv',
            'data/incoming/verified_source_batch_20260930_b50_ptco.csv',
            'data/incoming/verified_source_batch_20260930_b51_lyocell_cop.csv',
            'data/incoming/verified_source_batch_20260930_b51_po_radical.csv',
            'data/incoming/verified_source_batch_20260930_b52_cej_cotton.csv',
            'data/incoming/verified_source_batch_20260930_b52_cej_dd.csv',
            'data/incoming/verified_source_batch_20260930_b52_dopo_etes.csv',
            'data/incoming/verified_source_batch_20260930_b54_pan_zinc.csv',
            'data/incoming/verified_source_batch_20260930_b55_gel_amp.csv',
            'data/incoming/verified_source_batch_20260930_b56_mchp_cotton.csv',
            'data/incoming/verified_source_batch_20260930_b57_supercritical2017.csv',
            'data/incoming/verified_source_batch_20260930_b59_fibers1972.csv',
            'data/incoming/verified_source_batch_20260930_b59_mof3.csv',
            'data/incoming/verified_source_batch_20260930_b61_cotton1997.csv',
            'data/incoming/verified_source_batch_20260930_b61_silk38961.csv',
            'data/incoming/verified_source_batch_20260930_b64_cn3.csv',
            'data/incoming/verified_source_batch_20260930_b64_cn_mono.csv',
            'data/incoming/verified_source_batch_20260930_b64_ehp_mhp.csv',
            'data/incoming/verified_source_batch_20260930_b64_woolboron2026.csv',
            'data/incoming/verified_source_batch_20260930_b66_bc_marine.csv',
            'data/incoming/verified_source_batch_20260930_b66_bc_plants.csv',
            'data/incoming/verified_source_batch_20260930_b66_bc_proteins.csv',
            'data/incoming/verified_source_batch_20260930_b67_bc_citrus.csv',
            'data/incoming/verified_source_batch_20260930_b67_jute_smsn.csv',
            'data/incoming/verified_source_batch_20260930_b69_casein_lbl2019.csv',
            'data/incoming/verified_source_batch_20260930_b69_lessan2011.csv',
            'data/incoming/verified_source_batch_20260930_b69_nyco_pacys.csv',
            'data/incoming/verified_source_batch_20260930_b70_boron2023.csv',
            'data/incoming/verified_source_batch_20260930_b70_lpu2025.csv',
            'data/incoming/verified_source_batch_20261001_b45.csv',
            'data/incoming/verified_source_batch_20261001_b47.csv',
            'data/incoming/verified_source_batch_20261001_b49.csv',
            'data/incoming/verified_source_batch_20261001_b53.csv',
            'data/incoming/verified_source_batch_20261001_b58.csv',
            'data/incoming/verified_source_batch_20261001_b60.csv',
            'data/incoming/verified_source_batch_20261001_b62.csv',
            'data/incoming/verified_source_batch_20261001_b63.csv',
            'data/incoming/verified_source_batch_20261001_b65.csv',
            'data/incoming/verified_source_batch_20261001_b68_pla_aptris.csv',
            'data/incoming/verified_source_batch_20261001_b71_fiber_network.csv',
            'data/incoming/verified_tg_batch_20260921_b14_wool_phytic_acid.csv',
            'data/incoming/verified_web_batch_20260921_b4.csv',
            'data/incoming/verified_web_batch_20260921_b6.csv',
            'data/incoming/verified_web_batch_20260927_b36_cotton_plasma_uv_wash.csv',
        ]
        master = master[master.source_file.isin(baseline_inputs)].copy()
        fields = ['DOI', 'sample_state', 'washing_state', 'atmosphere', 'heating_rate_C_min',
                  'pair_key', 'sample_state_id', 'measurement_fingerprint']
        records = master[fields].astype(str).to_dict('records')
        digest = hashlib.sha256(json.dumps(records, sort_keys=True, ensure_ascii=False,
                                          separators=(',', ':')).encode()).hexdigest()
        self.assertEqual(digest, '747803e1986bf35c3165dcf13e652a0a4fc7ff5ecdc8bdddb4dffb893982fde3')
        self.assertEqual((master.DOI.map(p.normalize_doi).nunique(), len(master),
                          master.sample_state_id.nunique()), (117, 577, 501))


if __name__ == '__main__':
    unittest.main()
