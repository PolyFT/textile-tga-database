"""Regression protection for original fiber peaks and explicitly held states."""
import csv
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if not(ROOT/'scripts/pairing.py').exists():ROOT=ROOT/'repo'
sys.path.insert(0,str(ROOT/'scripts'));import pairing
PUBLIC=ROOT/'data/incoming/verified_source_batch_20261004_b175_local_textile.csv'
PRIVATE=ROOT.parent/'work/staged-local-textile-b175/publication_proposed.csv'

class SourceFacts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with(PUBLIC if PUBLIC.exists()else PRIVATE).open(newline='')as f:cls.rows=list(csv.DictReader(f))
        cls.aso=[r for r in cls.rows if r['DOI'].endswith('6922-4')]
        cls.hpp=[r for r in cls.rows if r['DOI'].endswith('5394-2')]
        cls.naca=[r for r in cls.rows if r['DOI'].endswith('2016.11.034')]
        cls.accepted=[r for r in cls.rows if r['pairing_status']=='verified_exact']
    def test_fact_and_accepted_counts(self):self.assertEqual((len(self.rows),len(self.accepted)),(25,7))
    def test_five_original_ASO_LOI(self):self.assertEqual([r['LOI_pct']for r in self.aso],['19','21','23','25','28'])
    def test_ASO_DTGrate_peaks(self):self.assertEqual([r['Tmax1_C']for r in self.aso],['329.8','328.6','327.8','325.7','320.0'])
    def test_ASO_unknown_residue_endpoint(self):self.assertTrue(all(not r.get('residue_pct')and not r.get('R600_pct')and not r.get('residue_temp_C')for r in self.aso))
    def test_ASO_raw_residue_retained(self):self.assertEqual([r['source_unbound_residual_mass_pct']for r in self.aso],['23.60','29.30','27.00','28.50','24.05'])
    def test_ASO_decomposition_end_not_onset(self):self.assertEqual([r['source_decomposition_end_C']for r in self.aso],['370.8','365.2','362.0','361.0','364.4']);self.assertTrue(all(not r.get('Tonset_C')for r in self.aso))
    def test_ASO_DSC_peaks_not_TG(self):self.assertTrue(all(not r.get('Tmax2_C')and not r.get('T5_C')and not r.get('T10_C')for r in self.aso))
    def test_ASO_own_method(self):self.assertTrue(all((r['atmosphere'],r['heating_rate_C_min'])==('N2','10')for r in self.aso))
    def test_HPP_forms_separate(self):self.assertEqual([r['LOI_pct']for r in self.hpp if r['material_form_LOI']=='cellulose fibers'],['18.6','25.4','29.1','35.2']);self.assertEqual([r['LOI_pct']for r in self.hpp if r['material_form_LOI']=='cellulose membrane'],['18.6','27.1','32.5','38.8'])
    def test_HPP_no_numeric_curve_conversion(self):self.assertTrue(all(r['pairing_status'].startswith('held_')and not r.get('Tmax1_C')and not r.get('R600_pct')for r in self.hpp))
    def test_NACA_exact_continuous_profiles(self):self.assertEqual([(r['LOI_pct'],r['Tmax1_C'],r['R800_pct'])for r in self.naca if r['pairing_status']=='verified_exact'],[('19','350','11.95'),('31','312','24.80')])
    def test_NACA_1number_recipe_held(self):self.assertTrue(all(r['pairing_status'].startswith('held_')for r in self.naca if '1#'in r['sample_state']))
    def test_NACA_Ca_mislabels_not_corrected(self):self.assertTrue(all(not r.get('R800_pct')and not r.get('Tmax1_C')for r in self.naca if '_Ca'in r['sample_state']))
    def test_NACA_trigger_program_separate(self):self.assertEqual(len([r for r in self.naca if 'trigger mode'in r['TGA_instrument']]),5)
    def test_NACA_trigger_not_T5_T10_Tmax(self):self.assertTrue(all(not any(r.get(k)for k in ['T5_C','T10_C','Tonset_C','Tmax1_C','R800_pct'])for r in self.naca if 'trigger mode'in r['TGA_instrument']))
    def test_NACA_accepted_version_not_final_year(self):self.assertTrue(all(not r['year']and 'Accepted Manuscript'in r['source_document_version']for r in self.naca))
    def test_fingerprint_bound_reviews(self):self.assertTrue(all(not pairing.evidence_issues(r)for r in self.accepted))
    def test_added_guessed_char_invalidates_review(self):r=dict(self.aso[0],R600_pct='23.60',residue_temp_C='600');self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(r))
    def test_form_mutation_cannot_mix_fiber_and_fabric(self):r=dict(self.aso[0],material_form_LOI='woven fabric');self.assertIn('specimen_form_mismatch',pairing.evidence_issues(r))
    def test_18held_facts_excluded(self):self.assertEqual(sum(r['pairing_status'].startswith('held_')for r in self.rows),18);self.assertTrue(all(r['direct_numeric_use']=='no'for r in self.rows if r['pairing_status'].startswith('held_')))

if __name__=='__main__':unittest.main()
