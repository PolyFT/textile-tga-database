"""Preserve source-state distinctions and the first reviewed non-DOI cohort."""
import csv
import hashlib
import json
import unittest
from pathlib import Path

from scripts.pairing import evidence_issues, measurement_fingerprint, pair_key, sample_state_id
from scripts.source_identity import source_gate_issues

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'data/curation/archive/source_review_manifest_20261001_b73.json'


def rows(tag):
    path = ROOT / f'data/incoming/verified_source_batch_20261001_b73_{tag}.csv'
    with path.open(newline='') as handle:
        return list(csv.DictReader(handle))


class SourceBatchB73Tests(unittest.TestCase):
    def test_exact_input_hashes_and_observation_reviews_remain_bound(self):
        manifest = json.loads(MANIFEST.read_text())
        all_rows = []
        for source in manifest['files']:
            path = ROOT / source['file']
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), source['published_input_sha256'])
            with path.open(newline='') as handle:
                source_rows = list(csv.DictReader(handle))
            all_rows.extend(source_rows)
            for row in source_rows:
                self.assertEqual(row['reviewed_measurement_fingerprint'], measurement_fingerprint(row))
                self.assertFalse(evidence_issues(row), row['sample_state'])
        self.assertEqual(len(all_rows), 33)
        self.assertEqual(len({pair_key(row) for row in all_rows}), 33)
        self.assertEqual(len({sample_state_id(row) for row in all_rows}), 29)
        doi_rows = [row for row in all_rows if row['DOI']]
        non_doi_rows = [row for row in all_rows if not row['DOI']]
        self.assertEqual(len({row['DOI'] for row in doi_rows}), 8)
        self.assertEqual(len({sample_state_id(row) for row in doi_rows}), 21)
        self.assertEqual(len(non_doi_rows), 8)

    def test_proceedings_have_registered_documents_and_real_blank_dois(self):
        for tag, count in [('nam_beltwide2010', 6), ('ttf_bpei2018', 2)]:
            observations = rows(tag)
            self.assertEqual(len(observations), count)
            self.assertEqual(len({row['stable_source_id'] for row in observations}), 1)
            for row in observations:
                self.assertEqual(row['DOI'], '')
                self.assertFalse(source_gate_issues(row))
                self.assertTrue(row['TG_locator'])
                self.assertTrue(row['LOI_locator'])
                self.assertTrue(row['conditions_locator'])
                self.assertTrue(row['primary_source_url'].startswith('https://'))

    def test_uv_atmospheres_do_not_duplicate_states_or_restore_conflicting_residue(self):
        observations = rows('uv_taep2011')
        self.assertEqual(len(observations), 8)
        self.assertEqual(len({sample_state_id(row) for row in observations}), 4)
        held = next(row for row in observations if row['sample_state'] == 'Cotton 3' and row['atmosphere'] == 'air')
        self.assertEqual(held['T5_C'], '268.3')
        self.assertEqual(held['LOI_pct'], '24.5')
        self.assertFalse(held['R700_pct'])
        self.assertFalse(held['residue_pct'])
        self.assertFalse(held['residue_temp_C'])

    def test_opf_is_only_explicit_t5_with_test_specific_preparation(self):
        row, = rows('opf2020_t5')
        self.assertEqual((row['T5_C'], row['LOI_pct']), ('104', '40.1'))
        self.assertFalse(row['residue_pct'])
        self.assertFalse(row['residue_temp_C'])
        self.assertNotIn('Tonset_C', {key: value for key, value in row.items() if value})
        self.assertEqual(row['source_reported_TG_end_C'], '700')
        self.assertIn('powdered', row['source_material_form_TGA_raw'])
        self.assertIn('twisting', row['source_material_form_LOI_raw'])
        self.assertEqual(row['material_form_TGA'], row['material_form_LOI'])
        self.assertIn('moisture', row['limitations'])
        self.assertIn('800 C', row['limitations'])

    def test_cloisite_residue_temperature_is_not_rounded_to600(self):
        observations = rows('cloisite2020')
        self.assertEqual(len(observations), 3)
        self.assertEqual({row['residue_temp_C'] for row in observations}, {'594.30'})
        self.assertTrue(all(not row.get('R600_pct') for row in observations))
        a, d = [next(row for row in observations if row['sample_state'] == label) for label in ['Sample A', 'Sample D']]
        self.assertEqual(a['residue_pct'], d['residue_pct'])
        self.assertNotEqual(a['LOI_pct'], d['LOI_pct'])
        self.assertNotEqual(a['treatment_method'], d['treatment_method'])

    def test_pesbo_explicit_r600_does_not_resolve_run_endpoint(self):
        observations = rows('pesbo2023')
        self.assertEqual(len(observations), 6)
        for row in observations:
            self.assertEqual(row['residue_temp_C'], '600')
            self.assertEqual(row['R600_pct'], row['residue_pct'])
            self.assertFalse(row['TG_end_C'])
            self.assertTrue(row['T5_C'])
            self.assertTrue(row['T50_C'])

    def test_ttf_untreated_control_has_no_invented_interlayer_rinsing(self):
        observations = rows('ttf_bpei2018')
        control = next(row for row in observations if float(row['LOI_pct']) == 18.5)
        self.assertNotIn('interlayer', control['washing_state'])
        self.assertTrue(all(not row['residue_temp_C'] for row in observations))
        self.assertEqual({float(row['LOI_pct']) for row in observations}, {18.5, 29.0})


if __name__ == '__main__':
    unittest.main()
