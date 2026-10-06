"""Keep original-source numerical review bindings and private-cache boundaries."""
import csv
import hashlib
import json
import unittest
from pathlib import Path
from scripts.pairing import evidence_issues, measurement_fingerprint, pair_key, sample_state_id
from scripts.validate_tg_loi import known_issues
ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'data/curation/archive/source_review_manifest_20261001_b82.json'
def rows(tag):
    with (ROOT / f'data/incoming/verified_source_batch_20261001_b82_{tag}.csv').open(newline='') as handle:
        return list(csv.DictReader(handle))
def issues():
    with (ROOT / 'data/curation/known_pairing_issues.csv').open(newline='') as handle:
        return list(csv.DictReader(handle))
class SourceBatchB82Tests(unittest.TestCase):
    def test_public_hold_export_does_not_include_private_cache_paths(self):
        text = (ROOT / 'data/curation/archive/source_review_holds_20261001_b82.json').read_text()
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

"""Regression guards for measured PI LOI and exact epoxy fabric state matching."""
import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def rows(doi):
    result = []
    for path in sorted((ROOT / 'data/incoming').glob('verified_source_batch_20261001_b82_*.csv')):
        with path.open(newline='') as handle:
            result.extend(r for r in csv.DictReader(handle) if r['DOI'].lower() == doi)
    return result

class PiEpoxySourceGuards(unittest.TestCase):
    def test_datppo_uses_measured_column_not_char_calculation(self):
        data = rows('10.1007/s10118-017-1896-7')
        self.assertEqual(len(data), 7)
        data.sort(key=lambda r: r['sample_state'])
        self.assertEqual([float(r['LOI_pct']) for r in data], [34.9,42.5,44.6,44.6,44.6,44.7,44.8])
        self.assertEqual([float(r['source_calculated_LOI_pct_excluded']) for r in data], [40.7,41.9,42.3,41.9,41.5,41.1,40.7])
        for row in data:
            self.assertEqual(float(row['draw_ratio']), 1.6)
            self.assertEqual(float(row['residue_temp_C']), 850)
            self.assertEqual(float(row['residue_pct']), float(row['R850_pct']))
            self.assertIn('no durability', row['washing_state'])

    def test_dappo_conflicting_t5_stays_raw(self):
        data = rows('10.3724/sp.j.1095.2014.30424')
        self.assertEqual(len(data), 4)
        row = next(r for r in data if r['sample_state'].startswith('PI4,'))
        self.assertFalse(row['T5_C'])
        self.assertEqual(float(row['source_T5_table_C']), 541)
        self.assertEqual(float(row['source_T5_prose_C']), 539)
        self.assertEqual(float(row['LOI_pct']), 43)
        self.assertEqual(float(row['R800_pct']), 66)
        self.assertIn('1–3', row['source_recipe_holds'])

    def test_epoxy_exact_addon_and_atmospheres_do_not_multiply_states(self):
        data = rows('10.1002/pat.867')
        self.assertEqual(len(data), 8)
        self.assertEqual(len({r['sample_state'] for r in data}), 4)
        treated = [r for r in data if '16.0%' in r['sample_state']]
        self.assertEqual(len(treated), 2)
        for row in treated:
            self.assertEqual(float(row['LOI_pct']), 23.6)
            self.assertEqual(float(row['LOI_sd']), .26)
            self.assertEqual(float(row['LOI_n']), 7)
            self.assertEqual(float(row['residue_temp_C']), 500)
            self.assertIn('Initial finishing rinse', row['washing_protocol'])
            self.assertFalse(row['T5_C'])
            self.assertFalse(row['T10_C'])
        cloth = [r for r in data if r['sample_state'] == 'Print cloth, untreated']
        self.assertEqual(len(cloth), 2)
        for row in cloth:
            self.assertEqual(row['material_form'], 'woven cotton fabric (print cloth)')
            self.assertIn('Print cloth', row['source_material_form_TGA_raw'])



class CsTaGpSourceGuards(unittest.TestCase):
    def test_final_residue_is_generic_and_not_vft_or_mcc(self):
        data = rows('10.1021/acspolymersau.6c00154')
        self.assertEqual(len(data), 2)
        self.assertEqual({(float(r['LOI_pct']),float(r['residue_pct'])) for r in data}, {(23.5,3.4),(27.0,22.4)})
        for row in data:
            self.assertFalse(row['residue_temp_C'])
            self.assertFalse(row['R600_pct'])
            self.assertEqual(float(row['TG_end_C']),600)
            self.assertEqual(float(row['tga_prehold_temperature_C']),100)
            self.assertEqual(float(row['tga_prehold_duration_min']),10)
            self.assertEqual(float(row['LOI_replicates']),3)
            self.assertEqual(row['LOI_uncertainty_type'],'not specified')
            self.assertEqual(row['atmosphere'],'air')
    def test_pre_ao_reuse_holds_are_label_scoped(self):
        source_issues = issues()
        for label in ['PI-0','PI-2','PI-4','PI-6']:
            self.assertIn('possible_sample_alias', known_issues({'DOI':'10.1039/c6ra26941a','sample_state':label},source_issues))
        self.assertNotIn('possible_sample_alias', known_issues({'DOI':'10.1039/c6ra26941a','sample_state':'PI-2 after AO exposure'},source_issues))
if __name__ == '__main__':
    unittest.main()
