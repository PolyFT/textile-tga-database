import csv
import unittest
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from pairing import sample_state_id, evidence_issues, measurement_fingerprint

class B90OriginalEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = {}
        for path in ROOT.glob('data/incoming/verified_source_batch_20261001_b90_*.csv'):
            cls.rows[path.stem.split('_b90_', 1)[1]] = list(csv.DictReader(path.open()))

    def test_unique_states_and_review_bindings(self):
        rows = [r for group in self.rows.values() for r in group]
        self.assertEqual((len(rows), len({sample_state_id(r) for r in rows})), (17, 17))
        for row in rows:
            self.assertFalse(evidence_issues(row))
            self.assertIn(row.get('direct_numeric_use', '').lower(), {'yes', 'tg+loi', '是'})
            self.assertEqual(row['reviewed_measurement_fingerprint'], measurement_fingerprint(row))

    def test_poy_second_stage_and_no_reused_control(self):
        rows = self.rows['petpoy2017']
        self.assertEqual([r['Tmax2_C'] for r in rows], ['567.9', '585.0', '567.7', '569.2'])
        for row in rows:
            self.assertFalse(row.get('Tmax_C'))
            self.assertFalse(row.get('Tmax1_C'))
            self.assertIn('Pretepon G', row['washing_state'])
            self.assertNotIn('stand.', row['source_sample_label'])

    def test_pla_own_reference(self):
        rows = self.rows['pla_dp1502016']
        self.assertEqual([(r['source_sample_label'], r['LOI_pct'], r['T5_C']) for r in rows], [('PLA-0', '26.3', '290.5'), ('PLA-200', '35.5', '315.3')])
        self.assertIn('nonwoven', rows[0]['material_form'])

    def test_hppa_onset_is_not_threshold_or_peak(self):
        row = self.rows['hppa_cotton2008'][0]
        self.assertEqual((row['LOI_pct'], row['Tonset_C']), ('18.4', '340'))
        for key in ['T5_C', 'Tmax_C', 'R500_pct', 'TG_end_C']:
            self.assertFalse(row.get(key))

    def test_mattress_air_and_polypropylene_only(self):
        row = self.rows['mattress2013'][0]
        self.assertEqual((row['LOI_pct'], row['R500_pct']), ('20', '1'))
        self.assertEqual(row['atmosphere'].lower(), 'air')
        self.assertIn('polypropylene', row['material_form'])
        self.assertIn('nitrogen is held', row['limitations'])
        self.assertEqual(row['TG_replicates'], '5')
        self.assertFalse(row.get('LOI_replicates'))

    def test_pvpa_conflict_and_apparatus_preserved(self):
        rows = self.rows['pvpa_cotton2022']
        target = next(r for r in rows if r['source_sample_label'] == 'CF-PVPA-3')
        self.assertTrue(target['T10_C'])
        self.assertFalse(target.get('R600_pct'))
        for row in rows:
            self.assertFalse(row.get('Tonset_C'))
            self.assertIn('DSCQ10', row['TGA_instrument'])
            self.assertIn('unresolved', row['TGA_instrument'])
            self.assertNotIn(row['source_sample_label'], ['CF', 'CF-Control'])

    def test_ptap_initial_control_counted_once(self):
        rows = self.rows['ptap_cotton2022']
        self.assertEqual([(r['LOI_pct'], r['T10_C'], r['R600_pct']) for r in rows], [('18.5', '327', '6.1'), ('25.0', '250', '20.9'), ('28.5', '325', '24.0')])
        issues = list(csv.DictReader((ROOT / 'data/curation/known_pairing_issues.csv').open()))
        self.assertTrue(any(r['DOI'] == '10.31788/RJC.2022.1547069' and r['sample_state'] == 'CF' and r['status'] == 'open' for r in issues))
        self.assertFalse(any(r['DOI'] == '10.31788/RJC.2022.1547069' and r['sample_state'] == '*' and r['status'] == 'open' for r in issues))

    def test_public_holds_have_no_private_paths(self):
        text = (ROOT / 'data/curation/source_review_holds_20261001_b90.json').read_text()
        for marker in ['/workspace/', '/tmp/', 'new-textile-cache/', 'new-textile-prep/']:
            self.assertNotIn(marker, text)

if __name__ == '__main__':
    unittest.main()
