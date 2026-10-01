"""Publication metadata describes sources; it never grants scientific admission."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from scripts import pairing as p
from scripts import source_identity as si
from scripts import validate_tg_loi as v
from test_pairing_validation import approve, observation
from test_source_identity import source, observation as non_doi_observation, approval


class PublicationTypeReportingTests(unittest.TestCase):
    def assert_totals(self, report):
        counts = report['verified_publication_type_counts']
        for unit, total in [('sources', 'verified_exact_sources'),
                            ('sample_states', 'verified_exact_sample_states'),
                            ('condition_records', 'verified_exact_condition_records')]:
            self.assertEqual(sum(item[unit] for item in counts.values()), report[total])
            self.assertEqual(counts['author_preprint'][unit],
                             report['verified_author_preprint_' + unit])

    def test_empty_cohort_has_explicit_zero_counts(self):
        report = v.publication_type_report(pd.DataFrame(), pd.DataFrame([
            observation(publication_type='author_preprint')]))
        self.assertEqual(tuple(report['verified_publication_type_counts']),
                         v.PUBLICATION_TYPE_CATEGORIES)
        for counts in report['verified_publication_type_counts'].values():
            self.assertEqual(counts, {'sources': 0, 'sample_states': 0, 'condition_records': 0})
        self.assertEqual(report['verified_publication_type_metadata_issues'], [])
        self.assertEqual(report['verified_author_preprint_sources'], 0)
        self.assertEqual(report['verified_author_preprint_sample_states'], 0)
        self.assertEqual(report['verified_author_preprint_condition_records'], 0)

    def test_missing_metadata_does_not_make_doi_a_journal(self):
        _, _, _, report = v.build_tables(pd.DataFrame([approve(observation(
            source_type='original_conference_proceedings'))]))
        self.assertEqual(report['verified_publication_type_counts']['unspecified']['sources'], 1)
        self.assertEqual(report['verified_publication_type_counts']['journal_article']['sources'], 0)
        self.assertEqual(report['verified_publication_type_counts']['conference_proceedings']['sources'], 0)
        self.assert_totals(report)

    def test_mixed_doi_and_registered_non_doi_sources_are_disjoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry = Path(tmp) / 'registry.json'
            registry.write_text(json.dumps({'schema_version': 1, 'sources': [source()]}))
            reviews = Path(tmp) / 'reviews.csv'
            with patch.object(si, 'REGISTRY', registry), patch.object(p, 'REVIEWS', reviews):
                proceedings = non_doi_observation()
                pd.DataFrame([approval(proceedings)]).to_csv(reviews, index=False)
                rows = [proceedings, approve(observation(publication_type='author_preprint')),
                        approve(observation(DOI='10.1234/journal', publication_type='journal_article')),
                        approve(observation(DOI='10.1234/proceedings', publication_type='conference_proceedings'))]
                _, _, _, report = v.build_tables(pd.DataFrame(rows))
        counts = report['verified_publication_type_counts']
        self.assertEqual(counts['author_preprint'], {'sources': 1, 'sample_states': 1, 'condition_records': 1})
        self.assertEqual(counts['conference_proceedings']['sources'], 2)
        self.assertEqual(counts['journal_article']['sources'], 1)
        self.assertEqual(report['verified_exact_dois'], 3)
        self.assertEqual(report['verified_non_doi_sources'], 1)
        self.assert_totals(report)

    def test_duplicate_sources_states_and_conditions_are_counted_once(self):
        row = approve(observation(publication_type='author_preprint', source_version='v1'))
        rows = [row, dict(row, DOI='https://doi.org/10.1234/EXAMPLE', source_version='v2'),
                approve(observation(atmosphere='air', publication_type=' AUTHOR_PREPRINT ')),
                approve(observation(sample_state='Other fabric', publication_type='author_preprint'))]
        _, _, _, report = v.build_tables(pd.DataFrame(rows))
        self.assertEqual(report['verified_publication_type_counts']['author_preprint'],
                         {'sources': 1, 'sample_states': 2, 'condition_records': 3})
        self.assert_totals(report)

    def test_unknown_labels_are_reported_without_guessing(self):
        _, _, _, report = v.build_tables(pd.DataFrame([
            approve(observation(publication_type='repository_manuscript')),
            approve(observation(DOI='10.1234/another', publication_type='journal-article'))]))
        self.assertEqual(report['verified_publication_type_counts']['unrecognized']['sources'], 2)
        self.assertEqual(report['verified_publication_type_metadata_issues'], [
            {'source_identity': '10.1234/another', 'category': 'unrecognized',
             'observed_types': ['journal-article']},
            {'source_identity': '10.1234/example', 'category': 'unrecognized',
             'observed_types': ['repository_manuscript']}])
        self.assert_totals(report)

    def test_conflicting_types_are_not_hidden_by_duplicate_observations(self):
        rows = [approve(observation(publication_type='author_preprint')),
                approve(observation(publication_type='journal_article'))]
        master, _, _, report = v.build_tables(pd.DataFrame(rows))
        self.assertEqual(len(master), 1)
        self.assertEqual(report['verified_publication_type_counts']['conflicting_metadata'],
                         {'sources': 1, 'sample_states': 1, 'condition_records': 1})
        self.assertEqual(report['verified_author_preprint_sources'], 0)
        self.assertEqual(report['verified_publication_type_metadata_issues'][0]['observed_types'],
                         ['author_preprint', 'journal_article'])
        reversed_report = v.build_tables(pd.DataFrame(rows[::-1]))[3]
        self.assertEqual(report['verified_publication_type_counts'],
                         reversed_report['verified_publication_type_counts'])
        self.assertEqual(report['verified_publication_type_metadata_issues'],
                         reversed_report['verified_publication_type_metadata_issues'])
        self.assert_totals(report)

    def test_pending_rows_cannot_change_verified_source_type(self):
        rows = [approve(observation(publication_type='author_preprint')),
                observation(sample_state='Pending fabric', publication_type='journal_article'),
                observation(DOI='10.1234/unreviewed', publication_type='author_preprint')]
        _, _, _, report = v.build_tables(pd.DataFrame(rows))
        self.assertEqual(report['verified_publication_type_counts']['conflicting_metadata']['sources'], 0)
        self.assertEqual(report['verified_author_preprint_sources'], 1)
        self.assert_totals(report)

    def test_pending_same_doi_preprint_cannot_classify_verified_unspecified_source(self):
        rows = [approve(observation()),
                observation(sample_state='Pending fabric', publication_type='author_preprint')]
        _, _, _, report = v.build_tables(pd.DataFrame(rows))
        self.assertEqual(report['verified_publication_type_counts']['unspecified']['sources'], 1)
        self.assertEqual(report['verified_author_preprint_sources'], 0)
        self.assert_totals(report)

    def test_quarantined_rows_cannot_classify_verified_source(self):
        rows = [approve(observation()), approve(observation(
            sample_state='Held fabric', publication_type='author_preprint'))]
        issues = [{'DOI': '10.1234/example', 'sample_state': 'Held fabric',
                   'reason_code': 'possible_sample_alias', 'status': 'open'}]
        _, _, quarantine, report = v.build_tables(pd.DataFrame(rows), issues)
        self.assertEqual(len(quarantine), 1)
        self.assertEqual(report['verified_publication_type_counts']['unspecified']['sources'], 1)
        self.assertEqual(report['verified_author_preprint_sources'], 0)
        self.assert_totals(report)

    def test_missing_rows_do_not_contradict_explicit_source_type(self):
        rows = [approve(observation()), approve(observation(publication_type='author_preprint'))]
        _, _, _, report = v.build_tables(pd.DataFrame(rows))
        self.assertEqual(report['verified_publication_type_counts']['author_preprint'],
                         {'sources': 1, 'sample_states': 1, 'condition_records': 1})
        self.assert_totals(report)

    def test_non_doi_proceedings_disagreeing_with_explicit_type_are_conflicting(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry = Path(tmp) / 'registry.json'
            registry.write_text(json.dumps({'schema_version': 1, 'sources': [source()]}))
            reviews = Path(tmp) / 'reviews.csv'
            with patch.object(si, 'REGISTRY', registry), patch.object(p, 'REVIEWS', reviews):
                row = non_doi_observation(publication_type='author_preprint')
                pd.DataFrame([approval(row)]).to_csv(reviews, index=False)
                _, _, _, report = v.build_tables(pd.DataFrame([row]))
        self.assertEqual(report['verified_publication_type_counts']['conflicting_metadata']['sources'], 1)
        self.assertEqual(report['verified_publication_type_metadata_issues'][0]['observed_types'],
                         ['author_preprint', 'conference_proceedings'])
        self.assertEqual(report['verified_author_preprint_sources'], 0)
        self.assert_totals(report)

    def test_publication_metadata_does_not_change_identity_fingerprints_or_admission(self):
        row = observation()
        updated = dict(row, publication_type='author_preprint', source_version='v2')
        for identity in [p.pair_key, p.sample_state_id, p.measurement_fingerprint]:
            self.assertEqual(identity(row), identity(updated))
        master, _, _, report = v.build_tables(pd.DataFrame([updated]))
        self.assertTrue(master.empty)
        self.assertEqual(report['verified_author_preprint_sources'], 0)
        self.assert_totals(report)

    def test_readme_snapshot_uses_report_totals_and_explains_uncertainty(self):
        _, _, _, report = v.build_tables(pd.DataFrame([approve(observation(
            publication_type='author_preprint'))]))
        report['snapshot_sha256'] = 'fixture-digest'
        with tempfile.TemporaryDirectory() as tmp:
            readme = Path(tmp) / 'README.md'
            readme.write_text('Fixture README\n')
            with patch.object(v, 'README', readme):
                v.update_readme(report)
                content = readme.read_text()
                stamp = readme.stat().st_mtime_ns
                v.update_readme(report)
                self.assertEqual(stamp, readme.stat().st_mtime_ns)
        self.assertIn('author_preprint: **1**', content)
        self.assertIn('Sources explicitly marked `author_preprint` (without conflicting type metadata): **1 sources / 1 conditions / 1 states**', content)
        self.assertIn('do not establish journal publication or peer review', content)
        self.assertIn('does not establish that no legacy source is a preprint', content)
        self.assertIn('do not invalidate accepted numerical evidence', content)
        self.assertIn('`source_version`', content)


if __name__ == '__main__':
    unittest.main()
