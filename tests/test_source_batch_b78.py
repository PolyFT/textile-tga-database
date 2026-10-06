"""Preserve reviewed source versions, washed states and metric-specific exclusions."""
import csv
import hashlib
import json
import unittest
from pathlib import Path

from scripts.pairing import evidence_issues, measurement_fingerprint, pair_key, sample_state_id
from scripts.validate_tg_loi import known_issues

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'data/curation/archive/source_review_manifest_20261001_b78.json'


def rows(tag):
    with (ROOT / f'data/incoming/verified_source_batch_20261001_b78_{tag}.csv').open(newline='') as handle:
        return list(csv.DictReader(handle))


def issues():
    with (ROOT / 'data/curation/known_pairing_issues.csv').open(newline='') as handle:
        return list(csv.DictReader(handle))


class SourceBatchB78Tests(unittest.TestCase):
    def test_exact_inputs_and_state_counts_are_bound_to_reviewed_manifest(self):
        manifest = json.loads(MANIFEST.read_text())
        all_rows = []
        for source in manifest['files']:
            path = ROOT / source['file']
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), source['published_input_sha256'])
            with path.open(newline='') as handle:
                observations = list(csv.DictReader(handle))
            all_rows.extend(observations)
            self.assertEqual(len(observations), source['conditions'])
            self.assertEqual(len({sample_state_id(r) for r in observations}), source['states'])
            for row in observations:
                self.assertEqual(row['reviewed_measurement_fingerprint'], measurement_fingerprint(row))
                self.assertFalse(evidence_issues(row), row['sample_state'])
        self.assertEqual(len(all_rows), manifest['summary']['added_verified_condition_records'])
        self.assertEqual(len({pair_key(r) for r in all_rows}), len(all_rows))
        self.assertEqual(len({sample_state_id(r) for r in all_rows}), manifest['summary']['added_verified_unique_states'])

    def test_version_holds_work_in_both_preprint_and_journal_directions(self):
        source_issues = issues()
        for tag, kind in [('eggwhite_ha2021', 'journal_article'), ('mtp2021', 'author_preprint')]:
            for row in rows(tag):
                self.assertEqual(row['publication_type'], kind)
                self.assertTrue(row['source_version'])
                self.assertNotEqual(row['DOI'], row['related_version_doi'])
                self.assertNotIn('possible_sample_alias', known_issues(row, source_issues))
                related = dict(row, DOI=row['related_version_doi'])
                self.assertIn('possible_sample_alias', known_issues(related, source_issues))

    def test_chitosan_reuse_holds_do_not_exclude_accepted_distinct_treated_states(self):
        source_issues = issues()
        doi = '10.1016/j.porgcoat.2021.106627'
        for label in ['Control sample', 'Cotton (control sample)', 'C/PVA']:
            self.assertIn('possible_sample_alias', known_issues({'DOI': doi, 'sample_state': label}, source_issues))
        for label in ['MP30', 'nCH30', 'MCHP30']:
            self.assertNotIn('possible_sample_alias', known_issues({'DOI': doi, 'sample_state': label}, source_issues))
        self.assertFalse(any(r['DOI'].lower() == doi and r['sample_state'] == '*' and r['status'] == 'open' for r in source_issues))

    def test_eggwhite_residue_conflicts_and_undefined_temperature_symbols_stay_held(self):
        observations = rows('eggwhite_ha2021')
        self.assertEqual(len(observations), 8)
        self.assertEqual(len({sample_state_id(r) for r in observations}), 4)
        self.assertEqual({float(r['LOI_pct']) for r in observations}, {18, 22, 23, 26})
        held = [r for r in observations if r['atmosphere'] == 'nitrogen' and (r['sample_state'].startswith('CT initial') or r['sample_state'].startswith('CTW+HA'))]
        self.assertEqual(len(held), 2)
        self.assertTrue(all(not r['R800_pct'] for r in held))
        self.assertTrue(all(r['R600_pct'] for r in observations))
        self.assertTrue(all(not r['T10_C'] and not r['Tmax1_C'] for r in observations))
        self.assertTrue(all(r['source_reported_T10_C'] and r['source_reported_Tmax_C'] for r in observations))

    def test_radiant_fabrics_remain_virgin_states_with_own_loi_means(self):
        observations = rows('radiant2019')
        self.assertEqual(len(observations), 2)
        self.assertEqual({r['sample_state'] for r in observations}, {'PSA virgin twill fabric', 'Nomex IIIA virgin twill fabric'})
        self.assertTrue(all(r['LOI_replicates'] == '5' for r in observations))
        self.assertEqual({r['Tmax1_C'] for r in observations}, {'493.9', '462.9'})
        self.assertTrue(all(r['R500_pct'] and r['R700_pct'] and r['R800_pct'] for r in observations))

    def test_mtp_initial_preprint_pairs_do_not_promote_raw_tmax_or_washed_values(self):
        observations = rows('mtp2021')
        self.assertEqual(len(observations), 3)
        self.assertEqual({r['sample_state'].split()[0] for r in observations}, {'C0', 'C1', 'C7'})
        self.assertEqual({float(r['LOI_pct']) for r in observations}, {17.1, 19.4, 68.4})
        self.assertTrue(all(not r['Tmax1_C'] and r['source_reported_Tmax_C'] for r in observations))
        self.assertTrue(all(r['T10_C'] and r['T50_C'] and r['R750_pct'] for r in observations))
        self.assertTrue(all('before durability' in r['washing_state'] for r in observations))
        control = next(r for r in observations if r['sample_state'].startswith('C0'))
        self.assertEqual((control['T50_C'], control['source_reported_Tmax_C']), ('347', '348'))

    def test_dopo_assay_pairing_retains_unknown_joint_selection_and_raw_metrics(self):
        observations = rows('dopo_insitu2025')
        self.assertEqual(len(observations), 2)
        self.assertEqual({r['T5_C'] for r in observations}, {'322', '215'})
        self.assertEqual({r['R700_pct'] for r in observations}, {'10.1', '10.9'})
        for row in observations:
            self.assertEqual(row['publication_type'], 'journal_article')
            self.assertFalse(row['Tmax1_C'])
            self.assertTrue(row['source_reported_Tmax_C'])
            self.assertIn('PET', row['source_specimen_handling_review'])
            self.assertIn('unknown', row['source_specimen_handling_review'].lower())
            self.assertEqual(row['heating_rate_C_min'], '20')
            self.assertEqual(row['gas_flow_mL_min'], '90')


    def test_phosphine_washed_states_have_their_own_loi_and_two_atmospheres(self):
        observations = rows('phosphine2021')
        self.assertEqual(len(observations), 16)
        self.assertEqual(len({sample_state_id(r) for r in observations}), 8)
        self.assertEqual({r['atmosphere'] for r in observations}, {'nitrogen', 'air'})
        for row in observations:
            self.assertIn('5', row['washing_state'])
            self.assertIn('simulat', row['washing_state'])
            self.assertFalse(row['Tonset_C'])
            self.assertTrue(row['Tmax1_C'])
            self.assertTrue(row['R800_pct'])
            self.assertIn('wash', row['pairing_evidence'].lower())


if __name__ == '__main__':
    unittest.main()
