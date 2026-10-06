import csv
import unittest
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from pairing import sample_state_id, evidence_issues, measurement_fingerprint

class B102TextileEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = {}
        for path in ROOT.glob('data/incoming/verified_source_batch_20261001_b102_*.csv'):
            with path.open(newline='') as handle:
                cls.rows[path.stem.split('_b102_', 1)[1]] = list(csv.DictReader(handle))

    def test_state_count_and_review_binding(self):
        rows = [r for group in self.rows.values() for r in group]
        self.assertEqual((len(rows), len({sample_state_id(r) for r in rows})), (10, 10))
        self.assertEqual(len({r['DOI'] for r in rows}), 4)
        for row in rows:
            self.assertFalse(evidence_issues(row))
            self.assertEqual(row['reviewed_measurement_fingerprint'], measurement_fingerprint(row))

    def test_flax_bath_is_not_retained_addon(self):
        rows = self.rows['flax_dapu2020']
        self.assertEqual([(r['LOI_pct'], r['R500_pct']) for r in rows], [('20', '18'), ('38', '38')])
        for row in rows:
            self.assertEqual(row['residue_temp_C'], '500')
            self.assertEqual(row['residue_pct'], row['R500_pct'])
            self.assertFalse(row.get('T5_C'))
        self.assertIn('1:1', rows[1]['source_sample_label'])
        self.assertNotIn('5 w/V%', ' '.join(r['source_sample_label'] for r in rows))

    def test_microfiber_finished_base_and_held_thresholds(self):
        rows = {r['source_sample_label']: r for r in self.rows['microfiber_leather2024']}
        self.assertEqual(set(rows), {'MF-WPU', 'MFP-WPU100', 'MFP-WPU100/75'})
        for row in rows.values():
            self.assertIn('nonwoven', row['material_form_TGA'])
            self.assertIn('preparatory washes', row['washing_state'])
            for field in ['T5_C', 'T10_C', 'T50_C', 'Tonset_C']:
                self.assertFalse(row.get(field))
        self.assertEqual(rows['MF-WPU']['Tmax1_C'], '387.70')
        self.assertEqual(rows['MFP-WPU100']['Tmax2_C'], '429.70')
        self.assertFalse(rows['MFP-WPU100']['residue_pct'])
        self.assertEqual((rows['MFP-WPU100/75']['Tmax1_C'], rows['MFP-WPU100/75']['Tmax2_C']), ('172.80', '360.70'))
        self.assertEqual(rows['MFP-WPU100/75']['R600_pct'], '19.54')
        self.assertEqual(rows['MF-WPU']['R600_pct'], '2.59')

    def test_conference_reuse_holds_and_unknown_char_temperature(self):
        rows = {r['source_sample_label']: r for r in self.rows['sio2_dopo2019']}
        self.assertEqual(set(rows), {'C', 'D', 'F'})
        self.assertEqual([(rows[k]['LOI_pct'], rows[k]['residue_pct']) for k in ['C', 'D', 'F']], [('22.2', '41.40'), ('20.6', '3.30'), ('22.8', '19.30')])
        for row in rows.values():
            self.assertEqual(row['publication_type'], 'conference_proceedings')
            self.assertFalse(row['residue_temp_C'])
            self.assertFalse(row.get('R600_pct'))
            self.assertFalse(row.get('R800_pct'))
            self.assertFalse(row.get('T5_C'))
            self.assertFalse(row.get('Tmax1_C'))

    def test_glass_residue_temperature_and_geometry_limit(self):
        rows = {r['source_sample_label']: r for r in self.rows['gf_psb2024']}
        self.assertEqual(set(rows), {'GF-PSB/PX-200', 'GF-PSB/DOPO-POSS'})
        self.assertEqual((rows['GF-PSB/PX-200']['T5_C'], rows['GF-PSB/PX-200']['Tmax1_C'], rows['GF-PSB/PX-200']['residue_pct']), ('431', '450', '77.0'))
        self.assertEqual((rows['GF-PSB/DOPO-POSS']['T5_C'], rows['GF-PSB/DOPO-POSS']['Tmax1_C'], rows['GF-PSB/DOPO-POSS']['residue_pct']), ('446', '461', '80.8'))
        for row in rows.values():
            self.assertEqual(row['residue_temp_C'], '555')
            self.assertFalse(row.get('R800_pct'))
            self.assertFalse(row.get('LOI_sd'))
            self.assertIn('0.25', row['LOI_specimen_preparation'])
            self.assertIn('3.2', row['LOI_specimen_preparation'])

    def test_public_holds_exclude_private_paths(self):
        text = (ROOT / 'data/curation/archive/source_review_holds_20261001_b102.json').read_text()
        for marker in ['/workspace/', '/tmp/', 'new-textile-cache/', 'new-textile-prep/']:
            self.assertNotIn(marker, text)

if __name__ == '__main__':
    unittest.main()
