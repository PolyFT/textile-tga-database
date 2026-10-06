"""Protect experimental state mapping and exclusions in primary-source batch47."""
import csv,hashlib,json,unittest
from pathlib import Path
import pandas as pd
from scripts.pairing import evidence_issues,measurement_fingerprint
from scripts.validate_tg_loi import build_tables
R=Path(__file__).resolve().parents[1]
I=R/'data/incoming/verified_source_batch_20261001_b47.csv'
def rows():
    with I.open(newline='') as f:return list(csv.DictReader(f))
class Batch47(unittest.TestCase):
    def test_verified_count_and_value_binding(self):
        data=rows();self.assertEqual(len(data),9)
        self.assertEqual(len({(x['DOI'],x['sample_state'],x['washing_state']) for x in data}),9)
        for x in data:
            self.assertFalse(evidence_issues(x));self.assertEqual(measurement_fingerprint(x),x['reviewed_measurement_fingerprint'])
        self.assertIn('measurement_review_pending_or_stale',evidence_issues(dict(data[0],R500_pct='99')))
    def test_heavy_cotton_is_air_not_furnace_or_neat_FR(self):
        d=[r for r in rows() if r['DOI']=='10.1177/0734904107083553']
        self.assertEqual(len(d),5);self.assertNotIn('Fyrol 51/250',{r['sample_state'] for r in d})
        self.assertTrue(all(r['atmosphere']=='air' and r['heating_rate_C_min']=='20' and r['gas_flow_mL_min']=='100' for r in d))
        self.assertTrue(all('360 g/m2' in r['composition'] and not r.get('R700_pct') for r in d))
        self.assertEqual({float(r['R500_pct']) for r in d},{30.9,26.1,18.3,18.8,25.0})
    def test_SI_only_initial_blend_not_calculated_or_washed(self):
        d=[r for r in rows() if r['DOI']=='10.1021/acssuschemeng.3c00028'];self.assertEqual(len(d),1)
        r=d[0];self.assertEqual(r['sample_state'],'PEC21.5/Fabric-3');self.assertEqual(r['washing_state'],'0 durability laundering cycles')
        self.assertEqual((r['T5_C'],r['Tmax1_C'],r['Tmax2_C'],r['R700_pct']),('281.7','311.5','436.5','26'))
        self.assertEqual((r['LOI_pct'],r['LOI_uncertainty_pct']),('28.5','0.5'))
        self.assertFalse(r.get('TG_end_C'));self.assertFalse(r.get('gas_flow_mL_min'))
    def test_source_conflicts_stay_out_of_clean_PET_fields(self):
        d={r['sample_state']:r for r in rows() if r['DOI']=='10.1016/j.ejpe.2015.04.001'}
        self.assertEqual(set(d),{'AZ1','AZ2','AZ10'});self.assertFalse(d['AZ2']['T80_C'])
        self.assertTrue(all(r['TG_end_C']=='750' and r['atmosphere']=='N2' and r['gas_flow_mL_min']=='30' for r in d.values()))
        self.assertFalse(any(r.get('Tonset_C') for r in d.values()))
        h=json.loads((R/'data/curation/archive/source_review_holds_20261001_b47.json').read_text())
        self.assertEqual(next(x['source_values'] for x in h if x.get('field')=='T80_C'),{'Table6':472,'Section3.7':471})
    def test_incomplete_condition_and_LOI_facts_are_not_verified(self):
        with (R/'data/curation/archive/source_review_condition_partial_20261001_b47.csv').open(newline='') as f:d=list(csv.DictReader(f))
        self.assertEqual(len(d),8);m,_,_,r=build_tables(pd.DataFrame(d));self.assertTrue(m.empty);self.assertEqual(r['verified_exact_sample_states'],0)
        cotton=[x for x in d if x['DOI']=='10.1021/acsomega.8b00822'];self.assertEqual(len(cotton),3);self.assertTrue(all(not x['atmosphere'] for x in cotton))
    def test_manifest_input_hash(self):
        m=json.loads((R/'data/curation/archive/source_review_manifest_20261001_b47.json').read_text())
        for x in m['files']:self.assertEqual(hashlib.sha256((R/x['file']).read_bytes()).hexdigest(),x['published_input_sha256'])
