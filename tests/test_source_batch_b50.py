"""Guard microwave casein source pairing and omitted disputed/reused fields."""
import csv,hashlib,json,unittest
from pathlib import Path
import pandas as pd
from scripts.pairing import evidence_issues,measurement_fingerprint
from scripts.validate_tg_loi import build_tables,numeric_errors
R=Path(__file__).resolve().parents[1]
M=R/'data/curation/archive/source_review_manifest_20260930_b50.json'
def files():return json.loads(M.read_text())['files']
def rows():
    result=[]
    for entry in files():
        with (R/entry['file']).open(newline='') as f:result.extend(csv.DictReader(f))
    return result
def microwave():return [x for x in rows() if x['DOI']=='10.1007/s12221-020-9965-x']
def ptco():return [x for x in rows() if x['DOI']=='10.1016/j.aiepr.2024.03.001']
class Batch50(unittest.TestCase):
    def test_counts_and_fingerprint_binding(self):
        data=rows();self.assertEqual(len(data),10)
        self.assertEqual(len({(x['DOI'],x['sample_state'],x['washing_state']) for x in data}),7)
        for x in data:
            self.assertFalse(evidence_issues(x));self.assertEqual(measurement_fingerprint(x),x['reviewed_measurement_fingerprint'])
        self.assertIn('measurement_review_pending_or_stale',evidence_issues(dict(data[0],R600_pct='99')))
        master,_,_,report=build_tables(pd.DataFrame(data));self.assertEqual(len(master),10);self.assertEqual(report['verified_exact_sample_states'],7);self.assertFalse(numeric_errors(pd.DataFrame(data)))
    def test_published_input_hash(self):
        for f in files():self.assertEqual(hashlib.sha256((R/f['file']).read_bytes()).hexdigest(),f['published_input_sha256'])
    def test_exact_same_state_values_and_conditions(self):
        d=microwave();self.assertEqual({(x['sample_state'],x['LOI_pct'],x['R600_pct']) for x in d},{('CUD-9','32','32.3'),('CUD-11','34','32.9'),('CUD-18','41','35.1'),('CUD-23','44','40.4')})
        self.assertTrue(all(x['atmosphere']=='N2' and x['heating_rate_C_min']=='10' and x['TG_end_C']=='600' for x in d))
        self.assertTrue(all(x['material_form_TGA']==x['material_form_LOI'] and x['washing_state']=='as_prepared_no_post_finish_laundering_reported' for x in d))
    def test_conflicting_metadata_and_mcc_not_imported(self):
        d={x['sample_state']:x for x in microwave()};self.assertFalse(d['CUD-11']['add_on_pct']);self.assertFalse(d['CUD-11']['source_onset2_C'])
        self.assertEqual(d['CUD-11']['source_onset1_C'],'144.8')
        self.assertEqual((d['CUD-9']['source_onset1_C'],d['CUD-9']['source_onset2_C']),('146.4','268.5'))
        self.assertTrue(all(not x.get('Tmax1_C') and not x.get('T5_C') and not x.get('T10_C') for x in d.values()))
    def test_possible_reused_control_and_unpaired_sources_excluded(self):
        self.assertNotIn('Control',{x['sample_state'] for x in rows()})
        self.assertEqual({x['DOI'] for x in rows()},{'10.1007/s12221-020-9965-x','10.1016/j.aiepr.2024.03.001'})
        holds=json.loads((R/'data/curation/archive/source_review_holds_20260930_b50.json').read_text())
        self.assertTrue(any(h.get('related_DOI')=='10.11648/j.ijmsa.20200904.11' and h.get('values',{}).get('R600_pct')==13.9 for h in holds))
        self.assertTrue(any(h.get('DOI')=='10.1177/1528083717750885' for h in holds))

    def test_ptco_condition_values_and_stage_numbering(self):
        d={(x['sample_state'],x['atmosphere']):x for x in ptco()};self.assertEqual(len(d),6)
        expected={('PTCO','N2'):('340','','384','426','8.6','18.8'),('PTCO/PPOA','N2'):('231','243','373','427','16.4','27.2'),('PTCO/POU','N2'):('216','239','378','421','17.5','30.1'),('PTCO','air'):('313','349','426','504','0.6','18.8'),('PTCO/PPOA','air'):('216','233','368','505','2.2','27.2'),('PTCO/POU','air'):('220','236','362','505','2.6','30.1')}
        for k,v in expected.items():self.assertEqual(tuple(d[k][f] for f in ['T5_C','Tmax1_C','Tmax2_C','Tmax3_C','R700_pct','LOI_pct']),v)
        self.assertTrue(all(x['heating_rate_C_min']=='10' and x['gas_flow_mL_min']=='25' and x['tga_start_temperature_C']=='40' and x['TG_end_C']=='700' for x in d.values()))
    def test_ptco_disputed_addon_and_legacy_completion(self):
        d=ptco();self.assertTrue(all(not x['add_on_pct'] for x in d if x['sample_state']=='PTCO/PPOA'))
        self.assertTrue(all(x['add_on_pct']=='25.2' for x in d if x['sample_state']=='PTCO/POU'))
        self.assertEqual({x['legacy_sample_id'] for x in d},{'L018-S001','L018-S002','L018-S003'})
        self.assertTrue(all(x['existing_state_status']=='existing_separate_TG_and_LOI_state_newly_completed' for x in d))
