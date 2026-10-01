"""Keep publication-version holds, assay conditions and source metric limits explicit."""
import csv
import hashlib
import json
import unittest
from pathlib import Path

from scripts.pairing import evidence_issues, measurement_fingerprint, pair_key, sample_state_id
from scripts.validate_tg_loi import known_issues

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'data/curation/source_review_manifest_20261001_b76.json'


def rows(tag):
    with (ROOT / f'data/incoming/verified_source_batch_20261001_b76_{tag}.csv').open(newline='') as handle:
        return list(csv.DictReader(handle))


class SourceBatchB76Tests(unittest.TestCase):
    def test_exact_sources_and_reviewed_observations_remain_bound(self):
        manifest = json.loads(MANIFEST.read_text())
        all_rows = []
        for source in manifest['files']:
            path = ROOT / source['file']
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), source['published_input_sha256'])
            with path.open(newline='') as handle:
                source_rows = list(csv.DictReader(handle))
            all_rows.extend(source_rows)
            self.assertEqual(len(source_rows), source['conditions'])
            self.assertEqual(len({sample_state_id(r) for r in source_rows}), source['states'])
            for row in source_rows:
                self.assertEqual(row['reviewed_measurement_fingerprint'], measurement_fingerprint(row))
                self.assertFalse(evidence_issues(row), row['sample_state'])
        self.assertEqual(len(all_rows), manifest['summary']['added_verified_condition_records'])
        self.assertEqual(len({pair_key(r) for r in all_rows}), len(all_rows))
        self.assertEqual(len({sample_state_id(r) for r in all_rows}), manifest['summary']['added_verified_unique_states'])

    def test_preprints_remain_preprints_and_related_journal_versions_are_held(self):
        with (ROOT / 'data/curation/known_pairing_issues.csv').open(newline='') as handle:
            issues = list(csv.DictReader(handle))
        observations = [r for tag in ['pei_pa_gradient2021', 'psn2022', 'fpec2024', 'pda_pha2022'] for r in rows(tag)]
        self.assertEqual(len(observations), 21)
        self.assertEqual(len({sample_state_id(r) for r in observations}), 12)
        self.assertEqual(len({r['DOI'] for r in observations}), 4)
        for row in observations:
            self.assertEqual(row['publication_type'], 'author_preprint')
            self.assertIn('v1', row['source_version'])
            self.assertNotEqual(row['DOI'], row['related_version_doi'])
            self.assertNotIn('possible_sample_alias', known_issues(row, issues))
            journal_row = dict(row, DOI=row['related_version_doi'])
            self.assertIn('possible_sample_alias', known_issues(journal_row, issues))

    def test_gradient_washed_states_have_own_tg_and_atmospheres_do_not_add_states(self):
        observations = rows('pei_pa_gradient2021')
        self.assertEqual(len(observations), 14)
        self.assertEqual(len({sample_state_id(r) for r in observations}), 7)
        washed = [r for r in observations if 'after20LCs' in r['sample_state']]
        self.assertEqual(len(washed), 6)
        self.assertEqual({float(r['LOI_pct']) for r in washed}, {22.3, 24.0, 26.3})
        self.assertTrue(all('20_home_laundering' in r['washing_state'] for r in washed))
        self.assertTrue(all(r['TG_locator'] and r['R800_pct'] for r in washed))
        self.assertTrue(all('5LC' not in r['sample_state'] and '10LC' not in r['sample_state'] for r in observations))

    def test_psn_control_is_preparatively_rinsed_process_control(self):
        controls = [r for r in rows('psn2022') if r['sample_state'].startswith('Control')]
        self.assertEqual(len(controls), 2)
        for row in controls:
            self.assertEqual(row['LOI_pct'], '18.3')
            self.assertIn('preparative', row['washing_state'])
            self.assertIn('5wt%dicyandiamide', row['treatment_chemistry'])
            self.assertNotIn('untreated', row['washing_state'])

    def test_fpec_conflicting_fluorinated_variant_stays_excluded(self):
        observations = rows('fpec2024')
        self.assertEqual(len(observations), 2)
        self.assertEqual({float(r['LOI_pct']) for r in observations}, {18.5, 29.0})
        self.assertTrue(all(not r['Tmax1_C'] for r in observations))
        self.assertTrue(all('F-PEC' not in r['sample_state'] for r in observations))

    def test_pda_generic_residue_does_not_infer_endpoint_temperature(self):
        row, = rows('pda_pha2022')
        self.assertEqual((row['LOI_pct'], row['residue_pct']), ('31.4', '40.3'))
        self.assertFalse(row['residue_temp_C'])
        self.assertFalse(row.get('R600_pct'))
        self.assertEqual(row['TG_end_C'], '600')

    def test_modacryl_unassigned_residue_temperatures_and_air_control_onset_stay_blank(self):
        observations = rows('modacryl2017')
        self.assertEqual(len(observations), 8)
        self.assertEqual(len({sample_state_id(r) for r in observations}), 4)
        for row in observations:
            if row['atmosphere'] == 'nitrogen':
                self.assertFalse(row['residue_temp_C'])
                self.assertFalse(row['TG_end_C'])
            elif row['sample_state'].startswith('C40:M60'):
                self.assertFalse(row['residue_temp_C'])
            else:
                self.assertEqual(row['residue_temp_C'], '850')
            if row['atmosphere'] == 'air' and row['sample_state'].startswith('C100'):
                self.assertFalse(row['Tonset_C'])

    def test_goat_maximum_weight_loss_temperatures_are_not_invented_dtg_peaks(self):
        row, = rows('goat2018')
        self.assertEqual((row['LOI_pct'], row['T5_C'], row['R800_pct']), ('41', '92', '4.9'))
        self.assertFalse(row['Tmax1_C'])
        self.assertFalse(row['Tmax2_C'])
        self.assertEqual(row['source_reported_Tmax1_C'], '247')
        self.assertEqual(row['source_reported_Tmax2_C'], '526')
        self.assertEqual(row['publication_type'], 'conference_proceedings')
        self.assertTrue(row['DOI'])


    def test_related_uv_journal_source_is_reuse_held(self):
        observations = rows('uv_mmep_tmep2008')
        self.assertEqual(len(observations), 7)
        self.assertEqual(len({sample_state_id(r) for r in observations}), 7)
        with (ROOT / 'data/curation/known_pairing_issues.csv').open(newline='') as handle:
            issues = list(csv.DictReader(handle))
        self.assertIn('possible_sample_alias', known_issues(dict(observations[0], DOI='10.1007/s12221-008-0105-2'), issues))

    def test_pa6_control_does_not_borrow_slope_burning_geometry_or_related_source_values(self):
        row, = rows('pa6_hpcp2021')
        self.assertEqual((row['LOI_pct'], row['R800_pct']), ('23.4', '0.23'))
        self.assertFalse(row['Tmax1_C'])
        self.assertIn('not documented LOI preparation', row['limitations'])
        self.assertIn('filter dimension is omitted', row['limitations'])
        with (ROOT / 'data/curation/known_pairing_issues.csv').open(newline='') as handle:
            issues = list(csv.DictReader(handle))
        self.assertIn('possible_sample_alias', known_issues(dict(row, DOI='10.1002/app.48458'), issues))


    def test_silica_below_start_t5_remains_source_native_only(self):
        row, = rows('silica_cotton2016')
        self.assertEqual((row['LOI_pct'], row['R600_pct'], row['Tmax1_C']), ('17.4', '11.4', '338'))
        self.assertFalse(row.get('T5_C'))
        self.assertEqual(row['tga_start_temperature_C'], '50')
        with (ROOT / 'data/curation/known_pairing_issues.csv').open(newline='') as handle:
            issues = list(csv.DictReader(handle))
        self.assertIn('possible_sample_alias', known_issues(dict(row, DOI='10.2298/TSCI1603863G'), issues))

    def test_aatmpeg_initial_states_and_explicit_zero_remain_distinct_from_wash_series(self):
        observations = rows('aatmpeg2022')
        self.assertEqual(len(observations), 4)
        self.assertEqual(len({sample_state_id(r) for r in observations}), 2)
        self.assertEqual({float(r['LOI_pct']) for r in observations}, {17.8, 45.0})
        control = [r for r in observations if float(r['LOI_pct']) == 17.8]
        self.assertTrue(all('NaOH' in ' '.join(r.values()) for r in control))
        air_control = next(r for r in control if r['atmosphere'] == 'air')
        self.assertEqual(float(air_control['R700_pct']), 0.0)


if __name__ == '__main__':
    unittest.main()
