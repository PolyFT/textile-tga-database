"""Protect source-specific gas, formulation, geometry and unresolved-LOI boundaries."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));import pairing as p;import validate_tg_loi as v
with(R/'data/incoming/verified_source_batch_20261006_b322_local_material.csv').open(newline='')as f:ROWS=list(csv.DictReader(f))
GOOD=[r for r in ROWS if r['pairing_status']=='verified_exact']
class SourceBoundaries(unittest.TestCase):
    def test_three_recipes_not_six_independent_samples(self):
        master,_,_,report=v.build_tables(pd.DataFrame(ROWS))
        self.assertFalse(report['errors']);self.assertEqual((len(master),report['verified_exact_sample_states']),(6,3))
        for label in ['PP_initial','IFR/PP_initial','0.5FA/IFR/PP_initial']:
            rows=[r for r in GOOD if r['sample_state']==label]
            self.assertEqual(len(rows),2);self.assertEqual({r['atmosphere']for r in rows},{'N2','air'})
            self.assertEqual(len({p.sample_state_id(r)for r in rows}),1)
            self.assertEqual(len({p.pair_key(r)for r in rows}),2)
    def test_exact_selected_FA_alias_not_other_loadings(self):
        for r in GOOD:
            if r['sample_state']=='0.5FA/IFR/PP_initial':
                self.assertEqual((r['FA_wt_pct'],r['LOI_pct'],r['TG_source_sample_label']),('0.5','33','FA/IFR/PP'))
                self.assertEqual((r['PP_wt_pct'],r['APP_wt_pct'],r['PER_wt_pct'],r['LigOH_wt_pct']),('70','17.7','7.1','4.7'))
                self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(dict(r,sample_state='0.3FA/IFR/PP_initial')))
    def test_threshold_peak_and_zero_residue_not_relabelled(self):
        for r in GOOD:
            self.assertFalse(r['Tonset_C']);self.assertFalse(r['T30_C']);self.assertFalse(r['T10_C'])
            self.assertEqual((r['residue_temp_C'],r['TG_end_C'],r['TG_start_C']),('800','800','50'))
            self.assertEqual(r['residue_pct'],r['R800_pct'])
            self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(dict(r,residue_temp_C='600')))
        pp=[r for r in GOOD if r['sample_state']=='PP_initial']
        for r in pp:self.assertEqual(r['R800_pct'],'0');self.assertFalse(r['Tmax2_C'])
        fr=next(r for r in GOOD if r['sample_state']=='IFR/PP_initial'and r['atmosphere']=='N2')
        self.assertEqual((fr['T5_C'],fr['Tmax1_C'],fr['Tmax2_C']),('338','270','503'))
    def test_own_LOI_width_not_UL94_and_control_history_unknown(self):
        for r in GOOD:
            self.assertEqual(r['LOI_specimen_geometry'],'130x6.5x3.2mm')
            self.assertEqual(r['LOI_standard'],'ASTMD2863-97');self.assertFalse(r['LOI_replicates'])
            self.assertEqual((r['TGA_mass_mg'],r['TGA_gas_flow_ml_min'],r['heating_rate_C_min']),('5-10','60','20'))
            self.assertFalse(r['TGA_pan']);self.assertFalse(r['TGA_replicates'])
            self.assertIn('specimen_form_mismatch',p.evidence_issues(dict(r,material_form_LOI='woven PP fabric')))
        pp=next(r for r in GOOD if r['sample_state']=='PP_initial')
        self.assertIn('control molding/mixing history not separately reported',pp['source_preparation'])
        self.assertNotIn('hotpress10MPa180C6min',pp['source_preparation'])
    def test_six_LOI_only_rows_cannot_borrow_optimum_TG(self):
        held=[r for r in ROWS if r['pairing_status']=='LOI_only_no_own_same_state_TG']
        self.assertEqual(len(held),6)
        for r in held:
            self.assertTrue(r['LOI_pct']);self.assertFalse(r['atmosphere']);self.assertFalse(r['TG_locator'])
            self.assertFalse(r['reviewed_measurement_fingerprint']);self.assertTrue(p.evidence_issues(r))
            self.assertTrue(all(not r.get(k)for k in p.TG_FIELDS))
        rounded=next(r for r in held if r['sample_state']=='0.1FA/IFR/PP_initial')
        self.assertEqual((rounded['APP_wt_pct'],rounded['PER_wt_pct']),('17.94','7.2'))
    def test_conflicting_PC_LOI_both_remain_unselected(self):
        held=[r for r in ROWS if r['DOI']=='10.1002/pc.25702']
        self.assertEqual(len(held),2)
        for r in held:
            self.assertFalse(r['LOI_pct']);self.assertFalse(r['reviewed_measurement_fingerprint'])
            self.assertNotEqual(r['source_LOI_table_pct'],r['source_LOI_conclusion_pct'])
            self.assertEqual(r['pairing_status'],'held_unresolved_LOI_assignment_conflict')
            self.assertEqual(r['residue_temp_C'],'1000');self.assertEqual(r['residue_pct'],r['R1000_pct'])
            self.assertIn('12wt%talc',r['composition']);self.assertTrue(p.evidence_issues(r))
        self.assertFalse(any('PB20'==r['source_sample_label']for r in ROWS))
    def test_unknown_SI_and_no_gas_rate_transfer(self):
        for r in GOOD:
            self.assertIn('noexternalfetch',r['supplement_review_status'])
            self.assertFalse(r.get('FA_SiO2_wt_pct'))
            self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(dict(r,heating_rate_C_min='10')))
            wrong='air'if r['atmosphere']=='N2'else'N2'
            self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(dict(r,atmosphere=wrong)))
if __name__=='__main__':unittest.main()
