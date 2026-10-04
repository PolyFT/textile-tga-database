"""Prevent incomplete textile source facts from becoming valid TG-LOI pairs."""
import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCAL = Path(__file__).resolve().parent

def rows(batch):
    path = ROOT / f'data/incoming/verified_source_batch_20261004_b{batch}_local_textile.csv'
    if not path.exists():
        path = LOCAL / f'staged-local-textile-b{batch}/publication_proposed.csv'
    with path.open(newline='') as stream:
        return list(csv.DictReader(stream))

class IncompleteTextileEvidenceTests(unittest.TestCase):
    def test_PA6_missing_gas_and_unbound_char_remain_held(self):
        data = rows(213)
        self.assertEqual(len(data), 7)
        for r in data:
            self.assertEqual(r['direct_numeric_use'], 'no')
            self.assertNotEqual(r['pairing_status'], 'verified_exact')
            self.assertTrue(r['T5_C'] and r['Tmax1_C'] and r['LOI_pct'])
            self.assertFalse(any(r.get(k) for k in ['atmosphere', 'R700_pct', 'residue_pct', 'residue_temp_C']))
            self.assertTrue(r['source_unbound_char_yield_pct'])

    def test_19_acrylic_draw_states_do_not_borrow_neat_additive_TG(self):
        data = rows(216)
        self.assertEqual(len({r['sample_state'] for r in data}), 19)
        for r in data:
            self.assertEqual(r['direct_numeric_use'], 'no')
            self.assertTrue(r['LOI_pct'] and r['drawing_ratio'])
            self.assertFalse(any(r.get(k) for k in ['atmosphere', 'heating_rate_C_min', 'T5_C', 'T10_C', 'Tonset_C', 'Tmax1_C', 'Tmax2_C', 'residue_pct']))

    def test_12_PAN_PVA_treatment_states_do_not_use_MCC_HRR_peak_as_DTG(self):
        data = rows(221)
        self.assertEqual(len({r['sample_state'] for r in data}), 12)
        for r in data:
            self.assertEqual(r['direct_numeric_use'], 'no')
            self.assertEqual(r['LOI_standard'], 'ISO 4589-2')
            self.assertIn('HRRpeaktemperatures', r['source_thermal_assay_exclusion'])
            self.assertFalse(any(r.get(k) for k in ['material_form_TGA', 'atmosphere', 'heating_rate_C_min', 'Tmax1_C', 'Tmax2_C', 'residue_pct']))

if __name__ == '__main__':
    unittest.main()
