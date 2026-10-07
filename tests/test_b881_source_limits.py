"""Protect source-specific distinctions retained in the B881 PP pairs."""
import csv
import unittest
from pathlib import Path
from scripts import reader_table

ROOT = Path(__file__).resolve().parents[1]

class TestB881SourceLimits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT/'data/incoming/verified_source_batch_20261008_b881_pp.csv').open(newline='') as f:
            cls.rows = list(csv.DictReader(f))

    def group(self, doi):
        rows = [r for r in self.rows if r['DOI'] == doi]
        self.assertTrue(rows, doi)
        return rows

    def test_original_peak_ordinals_and_unknown_rate_units(self):
        for r in self.group('10.1002/app.37910'):
            self.assertEqual(r['Tmax1_C'], '')
            self.assertTrue(r['source_T1p_C'])
            self.assertIn('U+0003', r['source_Rpeak_unit_raw'])
            notes = reader_table.reading_row(r, {'scope_class':r['material_scope_class']})[20]
            self.assertIn(r['source_Rpeak_unit_raw'], notes)
            if r['sample_id'] != 'sample1':
                self.assertIn('no minus sign', r['source_limitations'])

    def test_undefined_Td_and_unknown_residue_temperature(self):
        for r in self.group('10.1002/pi.6236'):
            self.assertEqual(r['T5_C'], '')
            self.assertEqual(r['R750_pct'], '')
            self.assertTrue(r['source_Td_raw_C'])
            self.assertTrue(r['source_raw_residue_pct'])
            self.assertIn('cannot derive from program750', r['source_TG_method_original'])

    def test_two_percent_loss_and_original_LOI_error(self):
        for r in self.group('10.1002/vnl.20235'):
            self.assertEqual(r['T5_C'], '')
            self.assertFalse(r.get('Tonset_C'))
            self.assertTrue(r['source_T2_C'])
            self.assertEqual(r['source_LOI_error_type'], 'not reported')
            self.assertFalse(r.get('LOI_standard_deviation'))
            shown = reader_table.reading_row(r, {'scope_class':r['material_scope_class']})
            self.assertIn('2%massloss', shown[20])
            self.assertIn(r['source_LOI_error_raw'], shown[21])

    def test_approximate_residue_and_wash_state_remain_qualified(self):
        r = self.group('10.1002/pen.21198')[0]
        self.assertEqual((r['R800_pct'],r['source_residue_qualifier']), ('5','about'))
        self.assertIn('washed LOI not paired', r['source_limitations'])
        self.assertIn('about', reader_table.reading_row(r, {'scope_class':r['material_scope_class']})[20])
        self.assertEqual(r['source_original_sample_state'], 'initial')

if __name__ == '__main__':
    unittest.main()
