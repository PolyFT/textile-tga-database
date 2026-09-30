"""Observation-scoped source safeguards for the two-paper b46 batch."""
import csv,hashlib,json,unittest
from pathlib import Path
from scripts.pairing import measurement_fingerprint,evidence_issues
ROOT=Path(__file__).resolve().parents[1]
def rows():
    data=[]
    for p in sorted((ROOT/'data/incoming').glob('verified_source_batch_20260930_b46_*.csv')):
        with p.open(newline='',encoding='utf-8') as h:data.extend(csv.DictReader(h))
    return data
class SourceBatchB46Tests(unittest.TestCase):
    def test_distinct_state_and_condition_counts(self):
        data=rows();self.assertEqual(len(data),7)
        self.assertEqual(len({(r['DOI'],r['sample_state'],r['washing_state']) for r in data}),5)
        self.assertEqual(len({r['DOI'] for r in data}),2)
        self.assertTrue(all(r['existing_state_status']=='wholly_new_source_observation' for r in data))
    def test_fingerprints_and_locators(self):
        for r in rows():
            with self.subTest(doi=r['DOI'],sample=r['sample_state'],atm=r['atmosphere']):
                self.assertEqual(r['reviewed_measurement_fingerprint'],measurement_fingerprint(r));self.assertFalse(evidence_issues(r))
                self.assertTrue(r['TG_locator'] and r['LOI_locator'] and r['conditions_locator'])
    def test_guanidine_conflicted_rows_are_not_admitted(self):
        data=[r for r in rows() if r['DOI']=='10.1177/1528083704045848']
        self.assertEqual({r['source_draft_batch_id'][-2:] for r in data},{'01','06','08'})
        self.assertEqual({r['LOI_pct'] for r in data},{'19','64','66'})
        self.assertTrue(all(r['washing_state']=='as prepared before soaking' for r in data))
        self.assertTrue(all(not r.get('T5_C') and not r.get('Tmax1_C') for r in data))
    def test_PAA_states_share_LOI_across_atmospheres_not_samples(self):
        data=[r for r in rows() if r['DOI']=='10.1016/j.polymdegradstab.2024.110764']
        self.assertEqual({r['sample_state'] for r in data},{'COT','COT/MMT (2% MMT add-on)'})
        self.assertEqual({r['LOI_pct'] for r in data},{'18'})
        self.assertEqual({r['atmosphere'] for r in data},{'N2','air'})
        self.assertTrue(all(r['heating_rate_C_min']=='10' and r['gas_flow_mL_min']=='20' for r in data))
    def test_PAA_T10_definition_and_explicit_zero(self):
        data=[r for r in rows() if r['DOI']=='10.1016/j.polymdegradstab.2024.110764']
        self.assertTrue(all(r.get('T10_C') and not r.get('Tonset_C') for r in data))
        control=next(r for r in data if r['sample_state']=='COT' and r['atmosphere']=='air')
        self.assertEqual(control['R800_pct'],'0');self.assertEqual(control['Tmax2_C'],'472')
    def test_review_manifest_hashes(self):
        j=json.loads((ROOT/'data/curation/source_review_manifest_20260930_b46.json').read_text())
        self.assertEqual(j['summary']['held_guanidine_states'],5);self.assertEqual(j['summary']['held_PAA_states'],6)
        for f in j['files']:self.assertEqual(hashlib.sha256((ROOT/f['file']).read_bytes()).hexdigest(),f['published_input_sha256'])
