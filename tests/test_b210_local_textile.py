"""Regressions for form, ambiguous temperatures, and incomplete UHMWPE states."""
import csv,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if not(ROOT/'scripts/pairing.py').exists():ROOT=ROOT/'repo'
sys.path.insert(0,str(ROOT/'scripts'));import pairing
P=ROOT/'data/incoming/verified_source_batch_20261004_b210_local_textile.csv'
if not P.exists():P=ROOT.parent/'work/staged-local-textile-b210/publication_proposed.csv'
class B210UHMWPE(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with P.open(newline='')as f:cls.rows=list(csv.DictReader(f))
        cls.index={r['source_sample_label']:r for r in cls.rows};cls.good=[r for r in cls.rows if r['pairing_status']=='verified_exact']
    def test_two_initial_fabric_pairs_four_holds(self):
        self.assertEqual(len(self.good),2);self.assertEqual(len(self.rows),6)
        for r in self.good:self.assertEqual(r['material_form_TGA'],r['material_form_LOI']);self.assertEqual(r['material_form'],'UHMWPE fabric');self.assertFalse(pairing.evidence_issues(r))
    def test_explicit_absolute_peak_and_delta_anomaly(self):
        r=self.index['g-APP@UHMWPE-OH'];self.assertEqual((r['LOI_pct'],r['Tmax1_C']),('22.9','497.8'));self.assertEqual(r['source_reported_Tmax_increment_C'],'19');self.assertEqual(self.index['UHMWPE']['Tmax1_C'],'482.8')
    def test_unbound_chars_do_not_become_R700(self):
        self.assertEqual(self.index['UHMWPE']['source_unbound_char_residue_pct'],'5.49');self.assertEqual(self.index['g-APP@UHMWPE-OH']['source_unbound_char_residue_pct'],'52.6')
        for r in self.rows:
            for k in ['R600_pct','R700_pct','R800_pct','residue_pct','residue_temp_C','TG_end_C']:self.assertFalse(r.get(k))
    def test_missing_LOI_and_curve_TG_do_not_join(self):
        self.assertFalse(self.index['UHMWPE-OH']['LOI_pct']);self.assertEqual(self.index['UHMWPE-OH']['Tmax1_C'],'482.8')
        for label,loi in [('APP@UHMWPE','21.8'),('APP@UHMWPE-OH','21.9')]:self.assertEqual(self.index[label]['LOI_pct'],loi);self.assertFalse(any(self.index[label].get(k)for k in pairing.TG_FIELDS));self.assertEqual(self.index[label]['direct_numeric_use'],'no')
    def test_MCC_and_VFT_conditions_not_imputed(self):
        for r in self.rows:self.assertEqual(r['heating_rate_C_min'],'10');self.assertEqual(r['atmosphere'],'N2');self.assertFalse(r.get('LOI_replicates'));self.assertFalse(r.get('source_LOI_geometry'));self.assertFalse(r.get('TG_start_C'))
    def test_area_unit_and_solution_dose_not_invented(self):
        for r in self.rows:self.assertEqual(r['source_areal_weight_as_reported'],'180gcm2');self.assertFalse(r.get('area_density_g_m2'));self.assertFalse(r.get('weight_gain_pct'));self.assertEqual(r['source_fabric_yarn_linear_density_dtex'],'442');self.assertIn('880dtex',r['source_separate_fiber_specimen'])
if __name__=='__main__':unittest.main()
