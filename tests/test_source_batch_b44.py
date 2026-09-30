"""Strict source-state safeguards for newly completed and new b44 pairs."""
import csv, hashlib, json, unittest
from pathlib import Path
from scripts.pairing import measurement_fingerprint,evidence_issues
ROOT=Path(__file__).resolve().parents[1]
def rows():
    data=[]
    for p in sorted((ROOT/'data/incoming').glob('verified_source_batch_20260930_b44_*.csv')):
        with p.open(newline='',encoding='utf-8') as h:data.extend(csv.DictReader(h))
    return data
class SourceBatchB44Tests(unittest.TestCase):
    def test_distinct_states_and_novelty_accounting(self):
        data=rows();self.assertEqual(len(data),21)
        self.assertEqual(len({(r['DOI'].lower(),r['sample_state'],r['washing_state']) for r in data}),21)
        self.assertEqual(len({r['DOI'].lower() for r in data}),5)
        self.assertEqual(sum(r['existing_state_status']=='existing_TG_only_state_newly_completed_pair' for r in data),13)
    def test_fingerprints_and_source_crosswalks(self):
        for r in rows():
            with self.subTest(sample=r['sample_state'],doi=r['DOI']):
                self.assertEqual(r['reviewed_measurement_fingerprint'],measurement_fingerprint(r))
                self.assertFalse(evidence_issues(r))
                self.assertTrue(r['TG_locator'] and r['LOI_locator'] and r['conditions_locator'])
    def test_cotton_figure_labels_and_initial_wash_mapping(self):
        data=[r for r in rows() if r['DOI']=='10.1038/s41598-024-71071-5']
        self.assertEqual(len(data),13)
        self.assertTrue(all('Figure 8' in r['LOI_locator'] for r in data))
        self.assertEqual(sum(r['sample_state'].endswith('W') for r in data),6)
        self.assertFalse(any(r['sample_state'].lower() in {'mercerized cotton','pure mercerized cotton'} for r in data))
        sample=next(r for r in data if r['sample_state']=='S10M');self.assertEqual(sample['Tmax1_C'],'252')
    def test_nylon_terminal_residues_do_not_become_R600(self):
        data=[r for r in rows() if r['DOI']=='10.7317/pk.2018.42.2.157']
        self.assertEqual(len(data),3)
        self.assertEqual({r['Tonset_C'] for r in data},{'360','220','260'})
        self.assertEqual({r['terminal_residue_pct'] for r in data},{'1.6','19.0','8.6'})
        self.assertTrue(all(not r.get('R600_pct') for r in data))
    def test_conflicted_DOPO_state_is_held(self):
        data=[r for r in rows() if r['DOI']=='10.13543/j.bhxbzr.2016.02.004']
        self.assertEqual({r['sample_state'] for r in data},{'PA66','GMA-PA66'})
        self.assertEqual({r['R800_pct'] for r in data},{'1.6','17.9'})
    def test_wool_untreated_only(self):
        data=[r for r in rows() if r['DOI']=='10.33263/briac123.36473663']
        self.assertEqual(len(data),1);self.assertEqual(data[0]['LOI_pct'],'24.8');self.assertEqual(float(data[0]['R750_pct']),20)
    def test_DMPP_same_35percent_state_and_no_literature_control(self):
        data=[r for r in rows() if r['DOI']=='10.1177/1528083719881816']
        self.assertEqual(len(data),2)
        self.assertEqual({r['LOI_pct'] for r in data},{'28.7','30.2'})
        self.assertTrue(all('100%' not in r.get('composition','') for r in data))
    def test_manifest_hashes(self):
        j=json.loads((ROOT/'data/curation/source_review_manifest_20260930_b44.json').read_text())
        for item in j['files']:self.assertEqual(hashlib.sha256((ROOT/item['file']).read_bytes()).hexdigest(),item['published_input_sha256'])
