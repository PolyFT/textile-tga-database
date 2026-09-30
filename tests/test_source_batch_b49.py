"""Protect printed-label evidence, test conditioning and wrong-form exclusions."""
import csv,hashlib,json,unittest
from pathlib import Path
import pandas as pd
from scripts.pairing import evidence_issues,measurement_fingerprint
from scripts.validate_tg_loi import build_tables
R=Path(__file__).resolve().parents[1];I=R/'data/incoming/verified_source_batch_20261001_b49.csv'
def rows():
    with I.open(newline='') as f:return list(csv.DictReader(f))
class Batch49(unittest.TestCase):
    def test_count_and_scientific_change_invalidates_review(self):
        d=rows();self.assertEqual(len(d),10);self.assertEqual(len({(r['DOI'],r['sample_state'],r['washing_state']) for r in d}),10)
        for r in d:self.assertFalse(evidence_issues(r));self.assertEqual(r['reviewed_measurement_fingerprint'],measurement_fingerprint(r))
        self.assertIn('measurement_review_pending_or_stale',evidence_issues(dict(d[0],LOI_pct='18')))
    def test_nine_original_Figure14_labels_match_states(self):
        d={r['sample_state']:float(r['LOI_pct']) for r in rows() if r['DOI']=='10.3390/polym18070819'}
        self.assertEqual(d,{'CO':19,'CO_PVAmPA':22,'CO_ChiPA':22,'CO/PET':18,'CO/PET_PVAmPA':22,'CO/PET_ChiPA':22,'PET':21,'PET_PVAmPA':22,'PET_ChiPA':21})
        self.assertTrue(all('printed' in r['LOI_locator'] for r in rows() if r['DOI']=='10.3390/polym18070819'))
    def test_phytate_temperature_mass_and_conditioning_are_distinct(self):
        d={r['sample_state']:r for r in rows() if r['DOI']=='10.3390/polym18070819'}
        self.assertTrue(all(r['gas_flow_mL_min']=='90' and r['TG_end_C']=='800' and r['washing_state']=='0 durability laundering cycles' for r in d.values()))
        r=d['CO_PVAmPA'];self.assertEqual((r['R700_pct'],r['residue_at_Tmax1_pct']),('18.2','97.8'))
        self.assertEqual((r['Tmax1_C'],r['Tmax2_C'],r['Tmax3_C']),('280','356','418'))
        self.assertFalse(r.get('R800_pct'));self.assertFalse(r.get('Tonset_C'))
        self.assertEqual(d['CO/PET']['composition'],'50/50 cotton/PET,core yarn PET core/cotton shell,twill2/1,170 g/m2,camouflage')
    def test_new_control_uses_explicit_T5_not_curve_Tmax(self):
        d=[r for r in rows() if r['DOI']=='10.3390/coatings16020202'];self.assertEqual(len(d),1);r=d[0]
        self.assertEqual((r['sample_state'],r['LOI_pct'],r['T5_C'],r['R700_pct']),('Control','17','324.8','10.3'))
        self.assertFalse(r.get('Tmax1_C'));self.assertFalse(r.get('Tonset_C'))
        self.assertEqual(r['gas_flow_mL_min'],'50');self.assertEqual(r['existing_state_status'],'new_source_inventory_state')
    def test_partial_states_stay_outside_target(self):
        with (R/'data/curation/source_review_condition_partial_20261001_b49.csv').open(newline='') as f:d=list(csv.DictReader(f))
        self.assertEqual(len(d),8);m,_,_,r=build_tables(pd.DataFrame(d));self.assertTrue(m.empty);self.assertEqual(r['verified_exact_sample_states'],0)
        pda=next(r for r in d if r['sample_state']=='PDA-2h');self.assertEqual(pda['residue_pct'],'14.3');self.assertFalse(pda['residue_temp_C'])
        h=json.loads((R/'data/curation/source_review_holds_20261001_b49.json').read_text());self.assertTrue(any(x['reason']=='no_TG_measurement' for x in h))
    def test_existing_source_queue_is_updated_once(self):
        with (R/'data/curation/source_review_queue.csv').open(newline='') as f:d=[r for r in csv.DictReader(f) if r['DOI']=='10.3390/polym18070819']
        self.assertEqual(len(d),1);self.assertEqual(d[0]['verified_unique_sample_states'],'9');self.assertEqual(d[0]['status'],'source_reviewed_batch_b49')
    def test_manifest_binds_factual_input_and_counts(self):
        m=json.loads((R/'data/curation/source_review_manifest_20261001_b49.json').read_text());self.assertEqual(m['summary']['existing_paired_states_evidence_upgraded'],9);self.assertEqual(m['summary']['new_source_inventory_states'],1)
        for x in m['files']:self.assertEqual(hashlib.sha256((R/x['file']).read_bytes()).hexdigest(),x['published_input_sha256'])
