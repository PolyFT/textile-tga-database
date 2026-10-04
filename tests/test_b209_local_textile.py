"""Protect gas bindings, sample identity, and exclusion of ambiguous source metrics."""
import csv, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if not (ROOT/'scripts/pairing.py').exists():ROOT=ROOT/'repo'
sys.path.insert(0,str(ROOT/'scripts'))
import pairing
P=ROOT/'data/incoming/verified_source_batch_20261004_b209_local_textile.csv'
if not P.exists():P=Path(__file__).parent/'staged-local-textile-b209/publication_proposed.csv'
class B209NativeTextile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with P.open(newline='')as f:cls.rows=list(csv.DictReader(f))
        cls.good=[r for r in cls.rows if r['pairing_status']=='verified_exact'];cls.index={(r['source_sample_label'],r['atmosphere']):r for r in cls.good}
    def test_four_samples_eight_conditions(self):
        self.assertEqual(len(self.good),8);self.assertEqual(len({r['sample_state']for r in self.good}),4)
        for label in ['Cotton','CPPE','CPPP','CPPE/P']:self.assertEqual({g for l,g in self.index if l==label},{'air','N2'})
    def test_conflicting_residue_excluded_unambiguous_metrics_remain(self):
        r=self.index['CPPE','N2'];self.assertEqual((r['T5_C'],r['Tmax1_C']),('198','324'))
        for k in ['R800_pct','residue_pct','residue_temp_C']:self.assertFalse(r.get(k))
        self.assertEqual((r['source_excluded_R800_table_pct'],r['source_excluded_R800_body_pct']),('14.35','14.5'))
    def test_air_secondary_peaks_and_absence(self):
        self.assertEqual(self.index['Cotton','air']['Tmax2_C'],'480');self.assertEqual(self.index['CPPE','air']['Tmax2_C'],'489')
        for label in ['CPPP','CPPE/P']:self.assertFalse(self.index[label,'air'].get('Tmax2_C'))
    def test_unknown_conditions_and_thresholds_not_imputed(self):
        for r in self.good:
            for k in ['LOI_standard','LOI_replicates','source_LOI_geometry','Tonset_C','T10_C','TG_flow_mL_min','weight_gain_pct']:self.assertFalse(r.get(k))
            self.assertEqual((r['heating_rate_C_min'],r['TG_start_C'],r['TG_end_C']),('20','30','800'))
    def test_gases_do_not_change_LOI_or_recipe(self):
        for label,mean in [('Cotton','18.5'),('CPPE','18.5'),('CPPP','29.0'),('CPPE/P','28.5')]:
            a=self.index[label,'air'];n=self.index[label,'N2'];self.assertEqual(a['LOI_pct'],mean);self.assertEqual(n['LOI_pct'],mean);self.assertEqual(a['composition'],n['composition'])
            self.assertFalse(pairing.evidence_issues(a));self.assertFalse(pairing.evidence_issues(n))
    def test_undoped_hold_no_doped_metrics(self):
        held=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(held),1);r=held[0];self.assertEqual(r['source_sample_label'],'CPP');self.assertEqual(r['direct_numeric_use'],'no');self.assertFalse(r.get('LOI_pct'))
        self.assertFalse(any(r.get(k)for k in pairing.TG_FIELDS))
    def test_physical_loadings_not_solution_mass_percentages(self):
        r=self.index['CPPE/P','N2'];self.assertEqual((r['source_table1_EG_g'],r['source_table1_PA_g']),('0.9','5'));self.assertEqual((r['source_table1_EG_pct'],r['source_table1_PA_pct']),('8.04','2.59'));self.assertIn('notfinaltotalcoatinggain',r['source_coating_loading']);self.assertFalse(r.get('weight_gain_pct'))
if __name__=='__main__':unittest.main()
