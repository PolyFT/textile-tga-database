"""Keep literal residue temperatures, source recipe uncertainty and scoped reuse holds."""
import csv
import hashlib
import json
import unittest
from pathlib import Path
from scripts.pairing import evidence_issues, measurement_fingerprint, pair_key, sample_state_id
from scripts.validate_tg_loi import known_issues
ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'data/curation/archive/source_review_manifest_20261001_b80.json'
def rows(tag):
    with (ROOT / f'data/incoming/verified_source_batch_20261001_b80_{tag}.csv').open(newline='') as handle:
        return list(csv.DictReader(handle))
def issues():
    with (ROOT / 'data/curation/known_pairing_issues.csv').open(newline='') as handle:
        return list(csv.DictReader(handle))
class SourceBatchB80Tests(unittest.TestCase):
    def test_public_hold_export_does_not_include_private_cache_paths(self):
        text = (ROOT / 'data/curation/archive/source_review_holds_20261001_b80.json').read_text()
        for marker in ['/workspace/', '/tmp/', 'new-textile-cache/', 'new-textile-prep/', '/root/']:
            self.assertNotIn(marker, text)
    def test_exact_inputs_and_unique_states_remain_review_bound(self):
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
    def test_banana_exact880_residues_are_not_endpoint_inferences(self):
        observations = rows('banana_peel2021')
        self.assertEqual(len(observations), 10)
        self.assertEqual({r['sample_state'] for r in observations}, {f'{group}{i}' for group in ['N','M'] for i in range(1,6)})
        for row in observations:
            self.assertEqual(row['R880_pct'], row['residue_pct'])
            self.assertEqual(row['residue_temp_C'], '880')
            self.assertFalse(row['TG_end_C'])
            self.assertFalse(row['tga_start_temperature_C'])
            self.assertFalse(row['Tmax1_C'])
            self.assertFalse(row['R800_pct'])
            self.assertEqual(row['heating_rate_C_min'], '20')
        control = next(r for r in observations if r['sample_state'] == 'N1')
        self.assertEqual(control['R880_pct'], '0')
    def test_literal_banana_drying_uncertainty_is_not_silently_corrected(self):
        row = next(r for r in rows('banana_peel2021') if r['sample_state'] == 'N2')
        self.assertIn('750', row['treatment_method'])
        self.assertIn('unresolved', row['treatment_method'])
        self.assertIn('750', row['source_recipe_holds'])
    def test_later_controls_and_commercial_comparators_are_scoped_holds(self):
        source_issues = issues()
        doi = '10.21605/cukurovaumfd.1146075'
        for label in ['A','B','A2','A4','B2','B4']:
            self.assertIn('possible_sample_alias', known_issues({'DOI':doi,'sample_state':label},source_issues))
        for label in ['A1','A3','B1','B3']:
            self.assertNotIn('possible_sample_alias', known_issues({'DOI':doi,'sample_state':label},source_issues))
        self.assertFalse(any(r['DOI'].lower()==doi and r['sample_state']=='*' and r['status']=='open' for r in source_issues))
    def test_licorice_bounded_nitrogen_and_unrounded_residue_temperatures(self):
        observations = rows('licorice2022')
        self.assertEqual(len(observations), 2)
        self.assertEqual({r['sample_state'] for r in observations}, {'A1', 'B1'})
        self.assertEqual({r['atmosphere'] for r in observations}, {'nitrogen'})
        self.assertEqual({float(r['Tmax1_C']) for r in observations}, {410.0})
        self.assertEqual({(r['residue_pct'],r['residue_temp_C']) for r in observations}, {('6.449','885'),('7.256','884')})
        self.assertTrue(all(not r.get('R880_pct') and not r.get('R800_pct') for r in observations))
if __name__ == '__main__':
    unittest.main()
