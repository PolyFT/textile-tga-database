"""Regression checks for source conflicts and unsupported cross-pairing."""
import csv,copy,sys,unittest
from pathlib import Path
import pandas as pd
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import pairing
import validate_tg_loi as v
FILE=R/'data/incoming/verified_source_batch_20261001_b72_local_greige_pan.csv'
def rows():
    with FILE.open(newline='') as f:return list(csv.DictReader(f))
class SourceScientificBoundaries(unittest.TestCase):
    def test_greige_exact_loi_and_native_metrics(self):
        a=[x for x in rows() if 'polymdegradstab' in x['DOI']]
        self.assertEqual(len(a),11)
        paired={x['sample_state']:x for x in a if x.get('LOI_pct')}
        self.assertEqual(set(paired),{'Untreated','D1U2','D2'})
        self.assertEqual(float(paired['D1U2']['LOI_pct']),30.0)
        self.assertIn('uniquely matches Table1 D1U2',paired['D1U2']['pairing_evidence'])
        self.assertEqual(float(paired['D1U2']['urea_decomposition_peak_C']),158.0)
        self.assertEqual(float(paired['D1U2']['Tmax1_C']),287.0)
        self.assertEqual(float(paired['D1U2']['source_Tf_C']),300.9)
        self.assertEqual(paired['D1U2'].get('Tmax2_C',''),'')
        for x in a:self.assertEqual(x.get('Tonset_C',''),'');self.assertEqual(float(x['heating_rate_C_min']),5.0)
        d=next(x for x in a if x['sample_state']=='D2D4');self.assertFalse(d.get('LOI_pct'));self.assertIn('do not silently rename',d['composition'])
        wrong=copy.deepcopy(paired['D1U2']);wrong['heating_rate_C_min']=18
        self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(wrong))
    def test_pan_water_and_conflict_do_not_fill_clean_fields(self):
        a={x['sample_state']:x for x in rows() if 'apsusc' in x['DOI']}
        self.assertEqual(set(a),{'PAN','A-PAN','P-A-PAN'})
        for key,water in [('A-PAN',86),('P-A-PAN',93)]:
            self.assertEqual(float(a[key]['water_removal_peak_C']),water)
            self.assertEqual(a[key].get('Tmax1_C',''),'');self.assertEqual(a[key].get('Tonset_C',''),'')
        self.assertEqual(a['A-PAN'].get('R800_pct',''),'');self.assertIn('47.39',a['A-PAN']['limitations']);self.assertIn('47.59',a['A-PAN']['limitations'])
        self.assertEqual(float(a['PAN']['LOI_pct']),18.1)
        wrong=copy.deepcopy(a['A-PAN']);wrong['R800_pct']=47.39
        self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(wrong))
    def test_six_states_and_eight_unpaired_tg_rows(self):
        a=rows();master,_,_,report=v.build_tables(pd.DataFrame(a),v.issue_list())
        self.assertEqual(len(master),6);self.assertEqual(report['verified_exact_sample_states'],6);self.assertEqual(report['verified_exact_condition_records'],6)
        self.assertEqual(sum(not x.get('LOI_pct') for x in a),8)
        self.assertFalse(report['errors'])
        for x in a:
            if x.get('LOI_pct'):self.assertFalse(pairing.evidence_issues(x))
if __name__=='__main__':unittest.main()
