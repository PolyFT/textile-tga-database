"""Source-role boundaries for the B573 approved batch; default public paths only."""
import csv,json,copy,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
INCOMING=ROOT/'data/incoming/verified_source_batch_20261007_b573_local_material.csv'
MANIFEST=ROOT/'data/curation/archive/20261007/source_review_manifest_b573.json'

def source_violations(r):
    bad=[];doi=r.get('DOI');s=r.get('sample_state');gas=r.get('atmosphere')
    if r.get('material_form_TGA')!=r.get('material_form_LOI'):bad.append('different_material_parent')
    if r.get('numeric_evidence_type')!='tabulated':bad.append('numeric_evidence_role')
    if doi=='10.1021/acsami.2c14709':
        if r.get('T5_C') or r.get('Tonset_C'):bad.append('T10_not_T5_or_onset')
        if r.get('residue_temp_C')!='800':bad.append('explicit_residue_temperature')
        if gas=='N2' and r.get('Tmax2_C'):bad.append('no_air_second_peak_in_N2')
        if s=='CT-PHB2' and gas=='air' and (r.get('Tmax1_C') or r.get('source_Tmax_ambiguous_C')!='356.4' or r.get('source_Tmax_prose_conflict_C')!='365.4'):bad.append('unresolved_peak_conflict')
        if r.get('source_LOI_uncertainty_type')!='unreported; do not assign SD/SE or n':bad.append('unreported_LOI_statistic')
        if s=='CT-PHB2' and any(r.get(k) for k in ['source_PPA_POSS_bath_wt_pct','source_PPA_POSS_WG1_raw','source_hydrophobic_WG2_raw']):bad.append('no_CT_PPA_or_borrowed_WG')
    elif doi=='10.1021/acsami.2c21320':
        if any(r.get(k) for k in ['T5_C','Tonset_C','Tmax1_C','Tmax2_C']):bad.append('undefined_peak_or_wrong_loss_threshold')
        if not r.get('T10_C') or r.get('residue_temp_C')!='800':bad.append('independently_defined_T10_R800')
        if s not in {'pristine cotton fabric','Cot@PA','Cot@PA/TA-APTES'}:bad.append('Ag_branch_composition_hold')
    elif doi=='10.1016/j.carbpol.2013.04.025':
        if s!='Superhydrophobic cotton (S2)':bad.append('nonselected_pristine_or_intermediate')
        if r.get('residue_temp_C')!='750' or r.get('R750_pct')!='15.6':bad.append('terminal_residue_not_peak_residue')
    elif doi=='10.1002/app.49552':
        if s=='PP':bad.append('related_control_reuse_hold')
        if any(r.get(k) for k in ['residue_pct','residue_temp_C','residue_temperature_C','R600_pct','R700_pct']):bad.append('raw_W_unknown_temperature')
        if not r.get('source_raw_residue_pct'):bad.append('raw_W_must_be_retained')
        if 'Figure 8' not in r.get('TG_locator','') or 'Figure 5' in r.get('TG_locator',''):bad.append('TG_not_Fe_mapping')
    elif doi=='10.1002/app.48312':
        if s not in {'Sample 5','Sample 6','Sample 10','Sample 11'}:bad.append('LOI_only_or_pure_control_not_paired')
        if not r.get('R700_pct') or r.get('T10_C') or r.get('Tonset_C'):bad.append('defined_T5_R700_not_other_threshold')
    else:bad.append('outside_selected_sources')
    return bad

class B573SourceGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with INCOMING.open(newline='') as f:cls.rows=list(csv.DictReader(f))
        cls.manifest=json.loads(MANIFEST.read_text())
    def row(self,doi,s,gas):return next(r for r in self.rows if r['DOI']==doi and r['sample_state']==s and r['atmosphere']==gas)
    def reject(self,row,field,value):
        changed=copy.deepcopy(row);changed[field]=value;self.assertTrue(source_violations(changed))
    def test_actual_source_roles(self):
        for r in self.rows:self.assertEqual(source_violations(r),[],(r['DOI'],r['sample_state'],r['atmosphere']))
    def test_conditions_are_not_extra_samples(self):
        self.assertEqual(len(self.rows),self.manifest['selected_TG'])
        self.assertEqual(len({r['sample_state_id'] for r in self.rows}),self.manifest['selected_states'])
        self.assertGreater(len(self.rows),len({r['sample_state_id'] for r in self.rows}))
    def test_two_related_controls_remain_held(self):
        self.assertNotIn(('10.1016/j.carbpol.2013.04.025','Pristine cotton'),{(r['DOI'],r['sample_state']) for r in self.rows})
        self.assertNotIn(('10.1002/app.49552','PP'),{(r['DOI'],r['sample_state']) for r in self.rows})
    def test_conflicting_air_peak_neither_version_selected(self):
        r=self.row('10.1021/acsami.2c14709','CT-PHB2','air')
        for value in ['356.4','365.4']:self.reject(r,'Tmax1_C',value)
    def test_conflict_original_values_cannot_be_erased(self):
        r=self.row('10.1021/acsami.2c14709','CT-PHB2','air');self.reject(r,'source_Tmax_ambiguous_C','')
    def test_no_threshold_relabeling(self):
        r=self.row('10.1021/acsami.2c14709','CTF1','air')
        for field in ['T5_C','Tonset_C']:self.reject(r,field,r['T10_C'])
    def test_nitrogen_cannot_borrow_air_second_peak(self):
        self.reject(self.row('10.1021/acsami.2c14709','CTF1','N2'),'Tmax2_C','494.5')
    def test_LOI_errors_not_invented_SD(self):
        self.reject(self.row('10.1021/acsami.2c14709','CTF1','air'),'source_LOI_uncertainty_type','SD n=3')
    def test_hydrophobic_control_no_bath_or_gain_borrow(self):
        r=self.row('10.1021/acsami.2c14709','CT-PHB2','air')
        for k,v in [('source_PPA_POSS_bath_wt_pct','10'),('source_hydrophobic_WG2_raw','10.1 ± 0.15')]:self.reject(r,k,v)
    def test_qualified_Table1_temperature_not_rate_peak(self):
        r=self.row('10.1021/acsami.2c21320','Cot@PA','air')
        self.assertEqual(r['source_raw_Table1_Tmax1_C'],'265');self.reject(r,'Tmax1_C','265')
    def test_Ag_dose_unknown_branch_not_admitted(self):
        self.reject(self.row('10.1021/acsami.2c21320','Cot@PA','air'),'sample_state','Cot@PA/TA-APTES/Ag/PFDT')
    def test_peak_residue_not_terminal_residue(self):
        r=self.row('10.1016/j.carbpol.2013.04.025','Superhydrophobic cotton (S2)','air')
        self.reject(r,'R750_pct',r['source_raw_Residuemax_pct'])
    def test_PP_unknown_W_temperature_stays_raw(self):
        r=self.row('10.1002/app.49552','PP/IFR','N2');self.reject(r,'R600_pct',r['source_raw_residue_pct']);self.reject(r,'residue_temp_C','600')
    def test_TG_locator_not_element_mapping(self):
        r=self.row('10.1002/app.49552','PP/IFR','N2');self.reject(r,'TG_locator',r['TG_locator'].replace('Figure 8','Figure 5'))
    def test_PP_LOI_only_design_run_cannot_borrow_TG(self):
        self.reject(self.row('10.1002/app.48312','Sample 5','air'),'sample_state','Sample 2')
    def test_common_material_not_equal_aliquot_geometry(self):
        for r in self.rows:
            if r['DOI'].startswith('10.1002/app.'):
                self.assertTrue(r['source_material_form_TGA_original']);self.assertTrue(r['source_material_form_LOI_original'])
                self.assertNotEqual(r['source_material_form_TGA_original'],r['source_material_form_LOI_original'])
                self.assertNotIn('cut from',r['material_form_TGA'])
    def test_public_paths_are_real_default_archive(self):
        self.assertEqual(MANIFEST.relative_to(ROOT).as_posix(),'data/curation/archive/20261007/source_review_manifest_b573.json')
        self.assertEqual(self.manifest['planned_incoming'],INCOMING.relative_to(ROOT).as_posix())

if __name__=='__main__':unittest.main()
