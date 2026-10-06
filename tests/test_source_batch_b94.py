import csv
import unittest
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from pairing import sample_state_id, evidence_issues, measurement_fingerprint

class B94PolypropyleneEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = {p.stem.split('_b94_', 1)[1]: list(csv.DictReader(p.open())) for p in ROOT.glob('data/incoming/verified_source_batch_20261001_b94_*.csv')}

    def test_six_prepared_states_and_bound_reviews(self):
        rows = [r for rs in self.rows.values() for r in rs]
        self.assertEqual((len(rows), len({sample_state_id(r) for r in rows})), (6, 6))
        for r in rows:
            self.assertFalse(evidence_issues(r))
            self.assertEqual(r['reviewed_measurement_fingerprint'], measurement_fingerprint(r))
            self.assertIn(r['direct_numeric_use'].lower(), {'yes', 'tg+loi', '是'})

    def test_nonwoven_fibers_have_defined_five_percent_threshold(self):
        rows = self.rows['pp_masterbatch2015']
        self.assertEqual([r['T5_C'] for r in rows], ['375', '390', '376', '383', '383'])
        self.assertEqual([r['LOI_pct'] for r in rows], ['17.9', '23.1', '24.9', '24.3', '24.0'])
        for r in rows:
            self.assertIn('nonwoven', r['material_form'])
            self.assertEqual(r['atmosphere'], 'N2')
            self.assertFalse(r.get('Tonset_C'))
            self.assertFalse(r.get('residue_pct'))
            self.assertFalse(r.get('R600_pct'))

    def test_only_printed_control_rate_peak_is_retained(self):
        rows = self.rows['pp_masterbatch2015']
        self.assertEqual(rows[0]['Tmax1_C'], '466')
        for r in rows[1:]:
            self.assertFalse(r.get('Tmax1_C'))
            self.assertFalse(r.get('Tmax2_C'))

    def test_modified_pp_control_is_not_neat_pp_or_temperature_pair(self):
        rows = self.rows['pp_ifr2021']
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertEqual(r['source_sample_label'], 'mPP')
        self.assertEqual(r['atmosphere'], 'air')
        self.assertEqual((r['LOI_pct'], r['R500_pct'], r['R600_pct'], r['R700_pct']), ('18', '0.99', '0.36', '0.07'))
        for k in ['T5_C', 'T10_C', 'Tmax1_C', 'Tmax2_C', 'Tonset_C']:
            self.assertFalse(r.get(k))
        text = ' '.join(r.values())
        self.assertIn('MA-g-PP', text)
        self.assertIn('95', text)
        self.assertIn('3.4', text)
        self.assertIn('32.3', text)

    def test_no_private_paths_in_public_holds(self):
        text = (ROOT / 'data/curation/archive/source_review_holds_20261001_b94.json').read_text()
        for marker in ['/workspace/', '/tmp/', 'new-textile-cache/', 'new-textile-prep/']:
            self.assertNotIn(marker, text)

if __name__ == '__main__':
    unittest.main()
