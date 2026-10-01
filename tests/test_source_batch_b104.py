import csv
import unittest
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from pairing import sample_state_id, evidence_issues, measurement_fingerprint

class B104TextileEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = {}
        for path in ROOT.glob('data/incoming/verified_source_batch_20261001_b104_*.csv'):
            with path.open(newline='') as handle:
                cls.rows[path.stem.split('_b104_', 1)[1]] = list(csv.DictReader(handle))

    def test_exact_states_and_review_binding(self):
        rows = [row for group in self.rows.values() for row in group]
        self.assertEqual((len(rows), len({sample_state_id(row) for row in rows})), (4, 4))
        self.assertEqual(len({row['DOI'] for row in rows}), 2)
        for row in rows:
            self.assertFalse(evidence_issues(row))
            self.assertEqual(row['reviewed_measurement_fingerprint'], measurement_fingerprint(row))

    def test_ttctg_conflicting_residue_and_initial_wash(self):
        rows = {r['source_sample_label']: r for r in self.rows['ttctg2023']}
        treated = rows['TTCTG200-CF']
        self.assertEqual((treated['LOI_pct'], treated['Tmax1_C'], treated['Tmax2_C']), ('27.3', '284', '406'))
        for field in ['R700_pct', 'residue_pct', 'residue_temp_C', 'Tonset_C', 'T5_C']:
            self.assertFalse(treated.get(field))
        self.assertIn('zero additional durability', treated['washing_state'])
        control = rows['纯棉织物']
        self.assertEqual((control['LOI_pct'], control['Tmax1_C'], control['R700_pct']), ('18.1', '357', '15.9'))
        self.assertEqual(control['residue_temp_C'], '700')

    def test_gelatin_distinct_states_and_unknown_endpoint(self):
        rows = {r['source_sample_label']: r for r in self.rows['gelatin_silica2019']}
        self.assertEqual(set(rows), {'D', 'F'})
        self.assertEqual((rows['D']['LOI_pct'], rows['D']['T5_C'], rows['D']['Tmax1_C']), ('21.8', '287.2', '342.9'))
        self.assertEqual((rows['F']['LOI_pct'], rows['F']['T5_C'], rows['F']['Tmax1_C'], rows['F']['residue_pct']), ('25.2', '284.3', '368.2', '31.1'))
        for row in rows.values():
            self.assertFalse(row['TG_end_C'])
            self.assertFalse(row['residue_temp_C'])
            self.assertFalse(row.get('R600_pct'))
            self.assertFalse(row.get('R800_pct'))

    def test_repeated_journal_states_have_scoped_guards(self):
        with (ROOT / 'data/curation/known_pairing_issues.csv').open(newline='') as handle:
            issues = list(csv.DictReader(handle))
        labels = {r['sample_state'] for r in issues if r['DOI'].lower() == '10.3969/j.issn.1004-5309.2019.04.08' and r['status'] == 'open'}
        self.assertTrue({'A', 'B', 'C', 'E'} <= labels)
        self.assertNotIn('*', labels)
        source = ROOT / 'data/incoming/verified_source_batch_20261001_b102_sio2_dopo2019.csv'
        with source.open(newline='') as handle:
            conference = {r['source_sample_label']: r for r in csv.DictReader(handle)}
        self.assertEqual((conference['C']['LOI_pct'], conference['C']['residue_pct']), ('22.2', '41.40'))
        self.assertFalse(conference['C']['Tmax1_C'])

if __name__ == '__main__':
    unittest.main()
