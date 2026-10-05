"""Protect threshold definitions, fire-residue boundaries and paper treatment state."""
import csv
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if not (ROOT / 'scripts/pairing.py').exists():
    ROOT = Path(__file__).resolve().parent.parent / 'repo'
sys.path.insert(0, str(ROOT / 'scripts'))
import pairing

def rows():
    path = ROOT / 'data/incoming/verified_source_batch_20261005_b294_local_textile.csv'
    if not path.exists():
        path = Path(__file__).resolve().parent / 'staged-local-textile-b294/publication_proposed.csv'
    with path.open(newline='') as handle:
        return list(csv.DictReader(handle))

class CellulosePaperTreatmentBoundaries(unittest.TestCase):
    def test_Tonset10_is_T10_not_generic_onset_or_water_peak(self):
        for r in rows():
            self.assertEqual(r['T10_C'], r['source_raw_Table3_Tonset10pct_C'])
            self.assertFalse(r['Tonset_C'])
            self.assertFalse(r['T5_C'])
            self.assertFalse(r['Tmax2_C'])
            self.assertEqual(r['Tmax1_C'], r['source_raw_Table3_Tmax_C'])
            changed = dict(r, T10_C='', Tonset_C=r['T10_C'])
            self.assertIn('measurement_review_pending_or_stale', pairing.evidence_issues(changed))
            self.assertIn('measurement_review_pending_or_stale', pairing.evidence_issues(dict(r, Tmax2_C='100')))

    def test_fire_residues_and_ambiguous_LOI_summary_cannot_replace_table_values(self):
        for r in rows():
            self.assertEqual(r['LOI_pct'], r['source_raw_Table4_LOI_percent'])
            self.assertEqual(r['R800_pct'], r['source_raw_Table3_R800_percent'])
            self.assertEqual(r['residue_pct'], r['R800_pct'])
            self.assertEqual(r['residue_temp_C'], '800')
            self.assertIn('explicit_Table4_measurements_used_without_correction', r['source_LOI_wording_limit'])
            self.assertIn('Table4HFT/VFTresiduecolumnsnotTGA', r['source_metric_definition'])
            if 'HMw' in r['sample_state']:
                self.assertIn('measurement_review_pending_or_stale', pairing.evidence_issues(dict(r, LOI_pct='25')))
            changed = dict(r, R800_pct='82', residue_pct='82')
            self.assertIn('measurement_review_pending_or_stale', pairing.evidence_issues(changed))

    def test_paper_preparation_routes_and_unknown_assay_conditions_remain_distinct(self):
        data = rows()
        self.assertEqual(len(data), 9)
        self.assertEqual(len({pairing.sample_state_id(r) for r in data}), 9)
        for r in data:
            self.assertEqual(r['material_form_TGA'], r['material_form_LOI'])
            self.assertIn('cellulose fibers', r['material_form_TGA'])
            self.assertFalse(r['LOI_replicates'])
            self.assertFalse(r['LOI_uncertainty_pct'])
            self.assertFalse(r['source_LOI_geometry'])
            self.assertFalse(r['TGA_conditioning'])
            self.assertFalse(r['TGA_mass_mg'])
            self.assertFalse(r['source_retained_SHMP_fraction'])
            self.assertEqual(r['source_TGA_mass_reported_mg'], '10plusminus1')
            self.assertEqual(r['heating_rate_C_min'], '10')
            self.assertEqual(r['TGA_gas_flow_ml_min'], '50')
            if r['source_PVAm_feed_mg_per_g_fiber']:
                self.assertEqual(r['source_PVAm_feed_mg_per_g_fiber'], '10')
                self.assertEqual(r['source_PVAm_Mw_Da'], '340000')
                if '3.5BL' in r['sample_state']:
                    self.assertIn('starts_ANIONIC_SHMP', r['source_LbL_order'])
                    self.assertIn('noassumedfinalPEI', r['source_LbL_order'])
            elif '3.5BL' in r['sample_state']:
                self.assertIn('starts_PEIpH9', r['source_LbL_order'])
            self.assertIn('measurement_review_pending_or_stale', pairing.evidence_issues(dict(r, washing_state='washed_after_20_cycles')))
            self.assertIn('specimen_form_mismatch', pairing.evidence_issues(dict(r, material_form_TGA='isolated cellulose fibers')))

if __name__ == '__main__':
    unittest.main()
