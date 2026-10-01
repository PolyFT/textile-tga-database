import csv
import unittest
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from pairing import sample_state_id, evidence_issues, measurement_fingerprint

class B96LaminateAndSilkEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = {p.stem.split('_b96_', 1)[1]: list(csv.DictReader(p.open())) for p in ROOT.glob('data/incoming/verified_source_batch_20261001_b96_*.csv')}

    def test_state_counts_and_completed_reviews(self):
        rows = [r for rs in self.rows.values() for r in rs]
        self.assertEqual((len(rows), len({sample_state_id(r) for r in rows})), (20, 14))
        for r in rows:
            self.assertFalse(evidence_issues(r))
            self.assertEqual(r['reviewed_measurement_fingerprint'], measurement_fingerprint(r))
            self.assertIn(r['direct_numeric_use'].lower(), {'yes', 'tg+loi', '是'})

    def test_glass_atmospheres_and_nine_hundred_degree_residues(self):
        rows = self.rows['app_pna_glass2017']
        self.assertEqual(len({sample_state_id(r) for r in rows}), 6)
        self.assertEqual({r['source_sample_label'] for r in rows}, {'ASET', '5APP', '10APP', '5PNA', '10PNA', '20PNA'})
        for r in rows:
            self.assertEqual(r['residue_temp_C'], '900')
            self.assertTrue(r['residue_pct'])
            self.assertIn('accepted manuscript', r['source_version'].lower())
            if r['atmosphere'] == 'air' and r['source_sample_label'] in {'5APP', '5PNA'}:
                self.assertFalse(r.get('T5_C'))
            self.assertIn('does not imply', r['Tmax1_assignment'])

    def test_jute_loi_conflicts_excluded_and_ratio_bases_preserved(self):
        rows = {r['source_sample_label']: r for r in self.rows['jute_dap2024']}
        self.assertEqual(set(rows), {'UJ3DE', 'UJ9DE', '9DJE', '27DJE', '54DJE'})
        self.assertEqual(rows['27DJE']['source_DAP_in_jute_pct'], '27')
        self.assertEqual(rows['54DJE']['source_DAP_in_jute_pct'], '54')
        self.assertEqual(rows['UJ9DE']['source_DAP_in_epoxy_pct'], '9')
        self.assertEqual(rows['54DJE']['source_DAP_in_composite_pct'], '12.50')
        for r in rows.values():
            self.assertEqual(r['R700_pct'], r['residue_pct'])
            self.assertEqual(r['residue_temp_C'], '700')
            self.assertFalse(r.get('Tonset_C'))
            self.assertIn('70', r['limitations'])
            self.assertIn('80', r['limitations'])
            self.assertIn('DTA', r['source_peak_caption'])
            self.assertIn('derivative weight', r['source_peak_caption'])

    def test_jute_third_stage_remains_separately_named(self):
        rows = {r['source_sample_label']: r for r in self.rows['jute_dap2024']}
        self.assertEqual(rows['9DJE']['source_Tpeak3_C'], '359.02')
        self.assertEqual(rows['27DJE']['source_Tpeak3_C'], '344.41')
        self.assertEqual(rows['54DJE']['source_Tpeak3_C'], '340.98')
        self.assertEqual(rows['54DJE']['Tmax2_C'], '268.00')

    def test_alpi_composite_thresholds_and_unknown_residues(self):
        rows = self.rows['alpi_glass2025']
        self.assertEqual({(r['source_sample_label'], r['T5_C'], r['LOI_pct']) for r in rows}, {('E70AlPi30LPS:GF-BD', '361', '73.8'), ('E70AlPi30HPS:GF-BD', '359', '59.5')})
        for r in rows:
            self.assertFalse(r.get('residue_pct'))
            self.assertFalse(r.get('Tmax1_C'))
            self.assertIn('Cryo-milling', r['limitations'])
            self.assertIn('glass-subtracted', r['limitations'])
            self.assertIn('without correcting', r['limitations'])

    def test_silk_control_air_only(self):
        rows = self.rows['silk_flavonoid2019']
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertEqual((r['LOI_pct'], r['R600_pct'], r['atmosphere']), ('24.0', '6.8', 'air'))
        self.assertEqual(r['heating_rate_C_min'], '10')
        self.assertIn('original', r['source_sample_label'].lower())

    def test_public_holds_have_no_private_paths(self):
        text = (ROOT / 'data/curation/source_review_holds_20261001_b96.json').read_text()
        for marker in ['/workspace/', '/tmp/', 'new-textile-cache/', 'new-textile-prep/']:
            self.assertNotIn(marker, text)

if __name__ == '__main__':
    unittest.main()
