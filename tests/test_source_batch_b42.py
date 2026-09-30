"""Scientific invariants for the locally staged b42 source review."""
import csv
import unittest
from pathlib import Path
from scripts.pairing import measurement_fingerprint, evidence_issues

ROOT = Path(__file__).resolve().parents[1]

def rows():
    result = []
    for path in sorted((ROOT / 'data/incoming').glob('verified_source_batch_20260930_b42_*.csv')):
        with path.open(newline='', encoding='utf-8') as handle:
            result.extend(csv.DictReader(handle))
    return result

class SourceBatchB42Tests(unittest.TestCase):
    def test_counts_are_sample_states(self):
        source = rows()
        self.assertEqual(len(source), 26)
        self.assertEqual(len({(r['DOI'], r['sample_state'], r['washing_state']) for r in source}), 18)
        self.assertEqual(len({r['DOI'] for r in source}), 4)
        self.assertTrue(all(r['existing_state_status'] == 'existing_state_evidence_upgraded' for r in source))

    def test_fingerprints_and_evidence_are_complete(self):
        for row in rows():
            with self.subTest(doi=row['DOI'], sample=row['sample_state'], atmosphere=row['atmosphere']):
                self.assertEqual(row['reviewed_measurement_fingerprint'], measurement_fingerprint(row))
                self.assertFalse(evidence_issues(row))
                self.assertTrue(row['TG_locator'] and row['LOI_locator'] and row['conditions_locator'])

    def test_acs_malformed_later_table_fields_are_not_inferred(self):
        source = [r for r in rows() if r['DOI'] == '10.1021/acsomega.2c02466']
        self.assertEqual(len(source), 10)
        self.assertTrue(all(not r.get('Tmax2_C') and not r.get('Tmax3_C') for r in source))
        residues = {(r['sample_state'], r['atmosphere']): r['R800_pct'] for r in source if r.get('R800_pct')}
        self.assertEqual(residues, {('PA66-10BL-Ni2+', 'air'): '4.5', ('PA66-10BL-Ni2+', 'N2'): '8.6', ('PA66-10BL-Fe3+', 'air'): '6.3'})
        self.assertTrue(all(not r.get('gas_flow_mL_min') for r in source))

    def test_ijms_uses_tg_not_tgftir_conditions(self):
        source = [r for r in rows() if r['DOI'] == '10.3390/ijms24021093']
        self.assertEqual(len(source), 6)
        self.assertEqual({r['gas_flow_mL_min'] for r in source}, {'25'})
        self.assertEqual({r['tga_start_temperature_C'] for r in source}, {'50'})
        self.assertEqual({r['TG_end_C'] for r in source}, {'700'})
        self.assertEqual({r['sample_state'] for r in source}, {'Control', 'PAP-200', 'PAPBTCA-200'})

    def test_nano_residue_endpoint_and_washing_state(self):
        source = [r for r in rows() if r['DOI'] == '10.3390/nano12224048']
        self.assertEqual(len(source), 4)
        for row in source:
            self.assertFalse(row.get('R800_pct'))
            self.assertEqual(row['residue_temp_C'], '900')
            self.assertEqual(row['washing_state'], 'after_50_laundering_cycles')
            self.assertFalse(row.get('T5_C'))
            self.assertFalse(row.get('Tmax1_C'))
            self.assertLess(float(row['water_removal_peak_C']), 100)
            self.assertGreater(float(row['Tmax2_C']), 280)

    def test_epoly_uncertainty_and_concentration_are_distinct(self):
        source = [r for r in rows() if r['DOI'] == '10.1515/epoly-2020-0059']
        self.assertEqual(len(source), 6)
        self.assertEqual({r['LOI_uncertainty_type'] for r in source}, {'not specified'})
        sample = next(r for r in source if r['sample_state'] == 'C30')
        self.assertEqual(sample['finishing_bath_DMBHP_wt_pct'], '30')
        self.assertEqual(sample['add_on_pct'], '24.7')

    def test_bulk_copolyester_is_not_promoted_as_fiber(self):
        self.assertFalse(any(r['DOI'].lower() == '10.1039/d1ra07410e' for r in rows()))
