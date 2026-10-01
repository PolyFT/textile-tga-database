"""Protect original-source conflicts, state matching and metric definitions."""
import copy,csv,sys,unittest
from pathlib import Path
import pandas as pd
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import pairing
import validate_tg_loi as v
FILE=R/'data/incoming/verified_source_batch_20261001_b74_local_cotton_wool.csv'
def rows(suffix=None):
    with FILE.open(newline='') as f:a=list(csv.DictReader(f))
    return [r for r in a if suffix is None or r['DOI'].endswith(suffix)]
class OriginalSourceBoundaries(unittest.TestCase):
    def test_ttpbd_control_and_bath_addon_are_not_guessed(self):
        a=rows('2020.109312');control=[r for r in a if r['sample_state']=='Control cotton']
        self.assertEqual(len(control),2)
        for r in control:self.assertFalse(r['LOI_pct']);self.assertEqual(float(r['source_LOI_native_pct']),28.5)
        n=next(r for r in control if r['atmosphere']=='nitrogen');self.assertFalse(n['residue_at_Tmax_pct'])
        t=next(r for r in a if r['sample_state']=='Cotton-TTPBD-20');self.assertEqual(float(t['TTPBD_bath_wt_pct']),20);self.assertEqual(float(t['weight_gain_pct']),13.2)
        wrong=copy.deepcopy(t);wrong['washing_state']='30wash'
        self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(wrong))
    def test_wool_washing_and_thresholds(self):
        a=rows('2020.109101');washed=[r for r in a if r['sample_state']=='WS20B5 after30wash']
        self.assertEqual(len(washed),2)
        for r in washed:
            self.assertEqual(float(r['LOI_pct']),29.6);self.assertEqual(float(r['LOI_uncertainty_pct']),.54);self.assertIn('30 wash',r['washing_state']);self.assertFalse(r['Tmax1_C']);self.assertFalse(r['Tonset_C'])
        n=next(r for r in washed if r['atmosphere']=='nitrogen');self.assertEqual(float(n['T25_C']),298);self.assertEqual(float(n['T50_C']),358);self.assertEqual(float(n['T75_C']),716)
        for r in a:
            if 'Isothermal' in r['sample_state']:self.assertFalse(r['LOI_pct']);self.assertIn('250C',r['washing_state'])
        wrong=copy.deepcopy(n);wrong['LOI_pct']=36
        self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(wrong))
    def test_dtctng_treated_series_not_mapped_to_optimized_addon(self):
        a=rows('2015.07.003');paired=[r for r in a if r['LOI_pct']]
        self.assertEqual(len(paired),1);self.assertEqual(paired[0]['sample_state'],'Untreated');self.assertEqual(float(paired[0]['LOI_pct']),18.8)
        self.assertEqual(float(paired[0]['Tonset_C']),297);self.assertFalse(paired[0]['T5_C'])
        self.assertEqual(sum(not r['LOI_pct'] for r in a),5)
    def test_atepahp_residue_temperature_not_peak(self):
        a=rows('2019.04.024');self.assertEqual(len(a),2)
        n=next(r for r in a if r['atmosphere']=='nitrogen');air=next(r for r in a if r['atmosphere']=='air')
        self.assertEqual(float(n['R700_pct']),7);self.assertEqual(float(air['residue_pct']),28.76);self.assertEqual(float(air['residue_temp_C']),372)
        for r in a:self.assertFalse(r['Tmax1_C']);self.assertFalse(r['Tonset_C']);self.assertEqual(r['numeric_evidence_type'],'explicit_text')
        self.assertFalse(air['R700_pct'])
    def test_csls_atmospheres_moisture_and_source_conflicts(self):
        a=rows('2020.109302');t=next(r for r in a if r['sample_state']=='CS/LS/cotton-25.2 wt%' and r['atmosphere']=='nitrogen');air=next(r for r in a if r['sample_state']==t['sample_state'] and r['atmosphere']=='air')
        self.assertEqual(float(t['heating_rate_C_min']),20);self.assertEqual(float(t['TG_gas_flow_mL_min']),25);self.assertEqual(float(air['heating_rate_C_min']),10);self.assertEqual(float(air['TG_gas_flow_mL_min']),30)
        self.assertEqual(float(t['T5_C']),89);self.assertFalse(t['Tonset_C']);self.assertEqual(float(t['source_Rmax1_pct_min']),8);self.assertEqual(float(t['Tmax1_C']),340)
        n=next(r for r in a if r['sample_state']=='Cotton' and r['atmosphere']=='nitrogen');self.assertFalse(n['R700_pct']);self.assertEqual(float(n['source_R700_table_pct']),13);self.assertEqual(float(n['source_R700_prose_pct']),12.5)
        for r in a:
            if r['sample_state']=='LS/cotton-17.1 wt%':self.assertFalse(r['LOI_pct']);self.assertEqual(float(r['source_LOI_table_abstract_pct']),24.7);self.assertEqual(float(r['source_LOI_prose_conflict_pct']),26)
        wrong=copy.deepcopy(t);wrong['heating_rate_C_min']=10
        self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(wrong))
    def test_count_unique_states_once_across_atmospheres(self):
        a=rows();_,_,_,p=v.build_tables(pd.DataFrame(a),v.issue_list())
        self.assertFalse(p['errors']);self.assertEqual(p['verified_exact_sample_states'],11);self.assertEqual(p['verified_exact_condition_records'],21);self.assertEqual(sum(not r['LOI_pct'] for r in a),11)
        for r in a:
            if r['LOI_pct']:self.assertFalse(pairing.evidence_issues(r))
if __name__=='__main__':unittest.main()
