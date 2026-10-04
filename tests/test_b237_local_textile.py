"""Protect gas, washing and temperature correspondence for AASMP cotton."""
import csv,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/'data/incoming/verified_source_batch_20261005_b237_local_textile.csv'
if not FILE.exists():FILE=Path(__file__).resolve().parent/'staged-local-textile-b237/publication_proposed.csv'
class AASMPCottonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with FILE.open() as q:cls.rows=list(csv.DictReader(q))
        cls.paired=[r for r in cls.rows if r['pairing_status']=='verified_exact']
    def test_two_gases_share_four_sample_states(self):
        self.assertEqual(len(self.paired),8);self.assertEqual(len({r['sample_state'] for r in self.paired}),4)
        for state in {r['sample_state'] for r in self.paired}:
            rs=[r for r in self.paired if r['sample_state']==state];self.assertEqual({r['atmosphere'] for r in rs},{'nitrogen','air'});self.assertEqual(len({r['LOI_pct'] for r in rs}),1)
    def test_washed_and_low_concentrations_do_not_borrow_TG(self):
        held=[r for r in self.rows if r['direct_numeric_use']=='no'];self.assertEqual(len(held),5)
        for r in held:self.assertFalse(any(r.get(k) for k in ['R700_pct','residue_pct','residue_temp_C','atmosphere','heating_rate_C_min']))
        self.assertEqual({r['LOI_pct'] for r in held if r['washing_state']=='washed_50_laundering_cycles'},{'26','27.5','31'})
    def test_cone_abstract_and_water_values_are_not_canonical_TG(self):
        for r in self.paired:
            self.assertEqual(r['residue_temp_C'],'700');self.assertEqual(r['R700_pct'],r['residue_pct']);self.assertFalse(any(r.get(k) for k in ['R800_pct','T5_C','T10_C','Tonset_C','Tmax1_C','Tmax2_C']))
            self.assertIn('34.2gasunbound',r['source_metric_limits']);self.assertIn('panelreferencescontradict',r['source_panel_conflict'])
        thirty={r['atmosphere']:r for r in self.paired if r['source_finishing_bath_percent']=='30'}
        self.assertEqual((thirty['nitrogen']['R700_pct'],thirty['air']['R700_pct']),('39.2','25.4'))
        self.assertEqual({r['LOI_pct'] for r in thirty.values()},{'45'})
if __name__=='__main__':unittest.main()
