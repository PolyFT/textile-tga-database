import csv
import unittest
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from pairing import sample_state_id, evidence_issues, measurement_fingerprint

class B92OriginalEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = {p.stem.split('_b92_', 1)[1]: list(csv.DictReader(p.open())) for p in ROOT.glob('data/incoming/verified_source_batch_20261001_b92_*.csv')}

    def test_state_count_excludes_repeat_atmospheres(self):
        rows = [r for rs in self.rows.values() for r in rs]
        self.assertEqual((len(rows), len({sample_state_id(r) for r in rows})), (21, 16))
        for r in rows:
            self.assertFalse(evidence_issues(r))
            self.assertEqual(r['reviewed_measurement_fingerprint'], measurement_fingerprint(r))
            self.assertIn(r['direct_numeric_use'].lower(), {'yes', 'tg+loi', '是'})

    def test_hydrogel_three_ambiguous_temperature_fields_held(self):
        rows = self.rows['pvpa_hydrogel2026']
        self.assertEqual(len({sample_state_id(r) for r in rows}), 5)
        for r in rows:
            self.assertEqual(r['residue_pct'], r['R600_pct'])
            self.assertEqual(r['residue_temp_C'], '600')
            if r['atmosphere'] == 'N2' and r['source_sample_label'] == 'TC10':
                self.assertFalse(r.get('T10_C'))
            if r['atmosphere'] == 'N2' and r['source_sample_label'] in {'TC30', 'TC40'}:
                self.assertFalse(r.get('T50_C'))
            self.assertNotEqual(r['source_sample_label'], 'TC40L')

    def test_hydrogel_control_partial_metric_match_is_not_tuple_identity(self):
        rows = {r['atmosphere']: r for r in self.rows['pvpa_hydrogel2026'] if r['source_sample_label'] == 'PC'}
        self.assertEqual((rows['air']['T10_C'], rows['air']['T50_C']), ('319', '343'))
        self.assertEqual((rows['N2']['T10_C'], rows['N2']['T50_C']), ('321', '347'))

    def test_pepas_control_only_and_explicit_residue_temperature(self):
        rows = self.rows['pepas2019']
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertEqual((r['LOI_pct'], r['Tmax1_C'], r['Tmax2_C'], r['residue_pct'], r['residue_temp_C']), ('20.2', '455.33', '515.68', '0.164', '730'))
        self.assertEqual(r['source_LOI_uncertainty_type'], 'not defined')
        self.assertIn('29.1', r['limitations'])
        self.assertIn('29.3', r['limitations'])

    def test_dhtp_wash_mapping_and_conflicted_metrics(self):
        rows = {r['source_sample_label']: r for r in self.rows['dhtp2012']}
        self.assertEqual(set(rows), {'3', '4', '5', '6', '7', '9', '11', '12', '16', '18'})
        for label in {'3', '4', '5', '6', '7'}:
            self.assertIn('No wash', rows[label]['washing_state'])
        for label in {'9', '11', '12', '16', '18'}:
            self.assertIn('Preparation-washed', rows[label]['washing_state'])
        for label in {'11', '12', '16'}:
            self.assertFalse(rows[label].get('Tonset_C'))
        for label in {'16', '18'}:
            self.assertIn('weaken', rows[label]['limitations'].lower())
        self.assertEqual((rows['12']['LOI_pct'], rows['12']['R600_pct']), ('30', '35.5'))

    def test_public_holds_have_no_private_paths(self):
        text = (ROOT / 'data/curation/archive/source_review_holds_20261001_b92.json').read_text()
        for marker in ['/workspace/', '/tmp/', 'new-textile-cache/', 'new-textile-prep/']:
            self.assertNotIn(marker, text)

if __name__ == '__main__':
    unittest.main()
