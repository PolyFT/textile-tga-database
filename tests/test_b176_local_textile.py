"""Regression protection for full-factor online Lyocell sample-state mapping."""
import csv
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if not(ROOT/'scripts/pairing.py').exists():ROOT=ROOT/'repo'
sys.path.insert(0,str(ROOT/'scripts'));import pairing
PUBLIC=ROOT/'data/incoming/verified_source_batch_20261004_b176_local_textile.csv'
PRIVATE=ROOT.parent/'work/staged-local-textile-b176/publication_proposed.csv'

class SourceFacts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with(PUBLIC if PUBLIC.exists()else PRIVATE).open(newline='')as f:cls.rows=list(csv.DictReader(f))
        cls.accepted=[r for r in cls.rows if r['pairing_status']=='verified_exact']
        cls.washed=[r for r in cls.rows if r['pairing_status']=='held_washed_LOI_no_own_washed_TG']
        cls.baseline=next(r for r in cls.accepted if r['sample_state']=='OLRAF_FR200_BTCA80_160C_initial')
    def test_fact_counts(self):self.assertEqual((len(self.rows),len(self.accepted),len(self.washed)),(27,11,11))
    def test_full_recipe_unique(self):self.assertEqual(len({(r['source_FR_bath_g_L'],r['source_BTCA_bath_g_L'],r['source_heatset_C'])for r in self.accepted}),11)
    def test_repeated_baseline_counted_once(self):self.assertEqual(sum(r['sample_state']=='OLRAF_FR200_BTCA80_160C_initial'for r in self.rows),1)
    def test_baseline_original_TG(self):self.assertEqual((self.baseline['T10_C'],self.baseline['Tmax1_C'],self.baseline['R700_pct']),('287.0','316.2','20.3'))
    def test_baseline_original_LOI(self):self.assertEqual((self.baseline['LOI_pct'],self.baseline['LOI_uncertainty_pct']),('30.2','0.3'))
    def test_all_TG_atmosphere_and_rate(self):self.assertTrue(all((r['atmosphere'],r['heating_rate_C_min'])==('air','20')for r in self.accepted))
    def test_all_residue_explicit700(self):self.assertTrue(all(r['residue_temp_C']=='700'and r['residue_pct']==r['R700_pct']for r in self.accepted))
    def test_temperature_factor_130_150(self):self.assertEqual([(r['source_heatset_C'],r['LOI_pct'])for r in self.accepted if r['source_heatset_C']!='160'],[('130','28.7'),('140','28.8'),('150','29.3')])
    def test_FR_factor_250_350(self):self.assertEqual([(r['source_FR_bath_g_L'],r['LOI_pct'])for r in self.accepted if r['source_FR_bath_g_L']!='200'],[('250','31.3'),('300','32.5'),('350','32.5')])
    def test_crosslinker_factor_20_100(self):self.assertEqual([(r['source_BTCA_bath_g_L'],r['LOI_pct'])for r in self.accepted if r['source_BTCA_bath_g_L']!='80'],[('20','28.4'),('40','28.7'),('60','29.7'),('100','31.2')])
    def test_washed_no_borrowed_TG(self):self.assertTrue(all(not any(r.get(k)for k in ['T10_C','Tmax1_C','R700_pct','atmosphere','heating_rate_C_min'])for r in self.washed))
    def test_washed_exact_LOI_distinct(self):r=next(r for r in self.washed if r['sample_state']=='OLRAF_FR200_BTCA80_160C_after20mildrinses');self.assertEqual((r['LOI_pct'],r['LOI_uncertainty_pct']),('28.7','0.2'))
    def test_mildrinses_not_home_laundering(self):self.assertTrue(all('20successiveDI-watermildrinses'in r['treatment_method']and 'nodetergent'in r['treatment_method']for r in self.washed))
    def test_CF_control_cannot_take_HSF_LOI(self):r=next(r for r in self.rows if r['sample_state']=='OLRAF_CF_coagulated');self.assertFalse(r.get('LOI_pct'));self.assertEqual(r['pairing_status'],'held_CF_TG_no_same_CF_LOI')
    def test_HSF_RAHSF_four_LOI_only(self):held=[r for r in self.rows if r['pairing_status']=='held_HSF_LOI_no_own_HSF_TG'];self.assertEqual([r['LOI_pct']for r in held],['18.2','18.1','27.0','21.4']);self.assertTrue(all(not r.get('Tmax1_C')and not r.get('R700_pct')for r in held))
    def test_conechar_not_TG(self):self.assertEqual(self.baseline['R700_pct'],'20.3');self.assertNotEqual(self.baseline['R700_pct'],'23.0')
    def test_no_T5_Tonset_inferred(self):self.assertTrue(all(not r.get('T5_C')and not r.get('Tonset_C')for r in self.rows))
    def test_publication_and_uncertainty_reported(self):self.assertTrue(all(r['year']=='2024'and 'unreported'in r['LOI_uncertainty_type']for r in self.rows))
    def test_all_exact_reviews_fingerprint_bound(self):self.assertTrue(all(not pairing.evidence_issues(r)for r in self.accepted))
    def test_wash_state_cannot_reuse_initial_review(self):r=dict(self.baseline,washing_state='after20mildrinses');self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(r))

if __name__=='__main__':unittest.main()
