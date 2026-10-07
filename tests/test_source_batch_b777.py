import csv,json,unittest
from pathlib import Path
from scripts import pairing
ROOT=Path(__file__).resolve().parents[1]
def read(rel):
    with (ROOT/rel).open(newline='') as f:return list(csv.DictReader(f))
class B777SourceGuards(unittest.TestCase):
    def setUp(self):
        self.rows=read('data/incoming/verified_source_batch_20261007_b777_tpe_pa6_pa11.csv')
    def test_distinct_states_and_gas_conditions(self):
        self.assertEqual(len(self.rows),17)
        self.assertEqual(len({pairing.sample_state_id(r) for r in self.rows}),12)
        self.assertTrue(all(not pairing.evidence_issues(r) for r in self.rows))
    def test_missing_air_rate_is_not_borrowed(self):
        pending=read('data/curation/archive/20261007/pending_conditions_b777.csv')
        self.assertEqual(len(pending),7)
        self.assertTrue(all(r['atmosphere']=='air' and not r['heating_rate_C_min'] and r['direct_numeric_use']=='pending' for r in pending))
        self.assertFalse({pairing.pair_key(r) for r in pending}&{pairing.pair_key(r) for r in self.rows})
    def test_original_criteria_and_qualified_residue(self):
        rows=[r for r in self.rows if r['DOI']=='10.1002/app.46888']
        self.assertEqual(len(rows),7)
        self.assertTrue(all(r['source_T3_C'] and not r.get('T5_C') and not r.get('Tonset_C') and not r.get('Tmax1_C') and r['residue_temp_C']=='700' for r in rows))
        r=next(r for r in self.rows if r['DOI']=='10.1002/pat.3755' and r['sample_id']=='PA6-0' and r['atmosphere']=='air')
        self.assertEqual(r['source_R450_qualifier'],'about')
        self.assertEqual(r['source_R450_pct'],'10.5')
        self.assertFalse(r.get('R450_pct'))
    def test_held_controls_and_processing_branches_stay_excluded(self):
        self.assertFalse(any(r['DOI']=='10.1002/pat.4591' and r['sample_id']=='PA11' for r in self.rows))
        self.assertFalse(any(r['DOI']=='10.1002/pat.3755' and r['sample_id']=='PA6-3' for r in self.rows))
        self.assertFalse(any(r['DOI']=='10.1016/j.polymdegradstab.2011.01.035' for r in self.rows))
