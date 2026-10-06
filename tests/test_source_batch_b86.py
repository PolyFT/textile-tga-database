"""Preserve original textile state, metric and publication-version boundaries."""
import csv,hashlib,json,unittest
from pathlib import Path
from scripts.pairing import evidence_issues,measurement_fingerprint,pair_key,sample_state_id
from scripts.validate_tg_loi import known_issues
ROOT=Path(__file__).resolve().parents[1]
def rows(tag):
    with (ROOT/f'data/incoming/verified_source_batch_20261001_b86_{tag}.csv').open(newline='') as f:
        return list(csv.DictReader(f))
class SourceBatchB86Tests(unittest.TestCase):
    def test_review_bound_inputs_and_state_condition_counts(self):
        m=json.loads((ROOT/'data/curation/archive/source_review_manifest_20261001_b86.json').read_text());all_rows=[]
        for source in m['files']:
            p=ROOT/source['file'];self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),source['published_input_sha256'])
            with p.open(newline='') as f:data=list(csv.DictReader(f))
            self.assertEqual(len(data),source['conditions']);self.assertEqual(len({sample_state_id(r) for r in data}),source['states'])
            for r in data:
                self.assertEqual(r['reviewed_measurement_fingerprint'],measurement_fingerprint(r));self.assertFalse(evidence_issues(r))
            all_rows+=data
        self.assertEqual(len(all_rows),m['summary']['added_verified_condition_records'])
        self.assertEqual(len({pair_key(r) for r in all_rows}),len(all_rows))
        self.assertEqual(len({sample_state_id(r) for r in all_rows}),m['summary']['added_verified_unique_states'])
    def test_triazine_retains_only_explicit_residue_and_own_loi(self):
        data=rows('triazine_cotton2013');self.assertEqual({float(r['LOI_pct']) for r in data},{17.5,26.1})
        self.assertEqual({float(r['R600_pct']) for r in data},{8.8,23.0})
        for r in data:
            self.assertEqual(r['atmosphere'],'air')
            for key in ['T5_C','T10_C','Tonset_C','Tmax1_C','Tmax2_C']:self.assertFalse(r.get(key,''))
    def test_apgdpe_initial_one_state_two_atmospheres_and_final_version_hold(self):
        data=rows('apgdpe2021');self.assertEqual(len(data),2);self.assertEqual(len({sample_state_id(r) for r in data}),1)
        for r in data:
            self.assertEqual(float(r['LOI_pct']),44.5);self.assertEqual(r['publication_type'],'author_preprint')
            self.assertIn('0 durability',r['washing_state']);self.assertEqual(r['DOI'],'10.21203/rs.3.rs-494207/v1')
        with (ROOT/'data/curation/known_pairing_issues.csv').open(newline='') as f:issues=list(csv.DictReader(f))
        self.assertIn('possible_sample_alias',known_issues({'DOI':'10.1007/s10570-021-04049-5','sample_state':'any final-version specimen'},issues))
    def test_deta_three_treated_preprint_states_and_no_borrowed_control(self):
        data=rows('deta_ta_pa2021');self.assertEqual(len(data),3)
        self.assertEqual({float(r['LOI_pct']) for r in data},{20,25,34})
        self.assertEqual({float(r['residue_pct']) for r in data},{23.6,23.2,43})
        for r in data:
            self.assertEqual(r['publication_type'],'author_preprint');self.assertEqual(float(r['residue_temp_C']),700)
            self.assertIn('DETA',r['sample_state']);self.assertIn('no durability',r['washing_state'])
    def test_peipa_control_zero_and_initial_crosslinked_state(self):
        data=rows('peipa2018');self.assertEqual(len(data),2)
        tuples={(float(r['LOI_pct']),float(r['T10_C']),float(r['residue_pct'])) for r in data}
        self.assertEqual(tuples,{(18.2,320,0),(29.6,243,30.7)})
        for r in data:
            self.assertEqual(float(r['residue_temp_C']),500);self.assertFalse(r.get('Tmax1_C',''));self.assertTrue(r.get('source_Tmax_C',''))
    def test_jute_only_clean_treatment_and_explicit_aliquot_bridge(self):
        data=rows('jute_tin2017');self.assertEqual(len(data),1);r=data[0]
        self.assertEqual(float(r['LOI_pct']),34);self.assertEqual(float(r['residue_pct']),27)
        self.assertEqual(float(r['residue_temp_C']),500);self.assertEqual(r['atmosphere'],'air')
        self.assertIn('finely crushed',r['source_material_form_TGA_raw'])
        self.assertIn('corresponding',r['source_material_form_TGA_raw'])
        self.assertIn('solution',r['limitations']);self.assertIn('owf',r['limitations'])
    def test_public_holds_have_no_private_paths(self):
        text=(ROOT/'data/curation/archive/source_review_holds_20261001_b86.json').read_text()
        for marker in ['/workspace/','/tmp/','new-textile-cache/','new-textile-prep/','/root/']:self.assertNotIn(marker,text)
if __name__=='__main__':unittest.main()
