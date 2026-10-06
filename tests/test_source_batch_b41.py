"""Scientific invariants for the bounded b41 source review."""
import csv
import json
import unittest
from pathlib import Path
from scripts.pairing import measurement_fingerprint

ROOT = Path(__file__).resolve().parents[1]

def source_rows():
    rows = []
    for path in sorted((ROOT / 'data/incoming').glob('verified_source_batch_20260930_b41_*.csv')):
        with path.open(newline='', encoding='utf-8') as handle:
            rows.extend(csv.DictReader(handle))
    return rows

class SourceBatchB41Tests(unittest.TestCase):
    def test_counts_are_states_not_metrics(self):
        rows = source_rows()
        self.assertEqual(len(rows), 59)
        identities = {(r['DOI'], r['sample_state'], r['washing_state']) for r in rows}
        self.assertEqual(len(identities), 59)
        self.assertEqual(len({r['DOI'] for r in rows}), 7)
        self.assertTrue(all(r['existing_state_status'] == 'existing_state_evidence_upgraded' for r in rows))

    def test_approvals_are_fingerprint_bound(self):
        for row in source_rows():
            with self.subTest(doi=row['DOI'], sample=row['sample_state']):
                self.assertEqual(row['reviewed_measurement_fingerprint'], measurement_fingerprint(row))
                for key in ['TG_locator', 'LOI_locator', 'conditions_locator', 'pairing_evidence', 'source_url']:
                    self.assertTrue(row[key])

    def test_microwave_cotton_does_not_import_mcc_peak(self):
        rows = [r for r in source_rows() if r['DOI'] == '10.3390/fib6040085']
        self.assertEqual(len(rows), 9)
        self.assertTrue(all(not r.get('Tmax1_C') for r in rows))
        for row in rows:
            if row['sample_state'] in {'U1', 'U2', 'U3', 'U4'}:
                self.assertFalse(row.get('Tonset_C'))
                self.assertTrue(row['source_onset1_C'] and row['source_onset2_C'])

    def test_control_peak_numbering_is_preserved(self):
        row = next(r for r in source_rows() if r['DOI'] == '10.3390/polym18060682' and r['sample_state'] == 'Control')
        self.assertFalse(row.get('Tmax1_C'))
        self.assertEqual(row['Tmax2_C'], '439.5')
        self.assertEqual(row['Tmax3_C'], '575.2')
        self.assertEqual(row['R800_pct'], '0.3')

    def test_conflicted_cotton_control_and_air_are_not_promoted(self):
        rows = [r for r in source_rows() if r['DOI'] == '10.3390/polym17070945']
        self.assertEqual({r['sample_state'] for r in rows}, {'3BL', '6BL', '9BL', '12BL'})
        self.assertEqual({r['atmosphere'] for r in rows}, {'N2'})

    def test_shared_post_soak_series_keeps_duration_unresolved(self):
        rows = [r for r in source_rows() if r['washing_state'] == 'after_water_soak_duration_unresolved']
        self.assertEqual(len(rows), 9)
        for row in rows:
            self.assertIn('30 min', row['limitations'])
            self.assertIn('30 s', row['limitations'])
            self.assertFalse(row.get('soak_duration_min'))

    def test_unresolved_sources_stay_outside_this_batch(self):
        blocked = {'10.3390/ma19020265', '10.1021/acsaenm.6c00308', '10.3390/polym18010127', '10.1039/d4mh01684j'}
        self.assertFalse(blocked & {r['DOI'] for r in source_rows()})
        holds = json.loads((ROOT / 'data/curation/archive/source_review_holds_20260930_b41.json').read_text())
        self.assertTrue(blocked <= {r['DOI'] for r in holds})
