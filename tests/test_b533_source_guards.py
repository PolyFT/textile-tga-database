import csv,json,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INCOMING=ROOT/'data/incoming/verified_source_batch_20261007_b533_local_material.csv'
MANIFEST=ROOT/'data/curation/archive/20261007/source_review_manifest_b533.json'
def rows():
    with INCOMING.open(newline='') as f:return list(csv.DictReader(f))
def key(r):return (r['DOI'],r['sample_state'],r['atmosphere'])
PLA='10.1016/j.compositesb.2019.107069'
PVA='10.1016/j.polymdegradstab.2014.02.020'
PAN='10.1016/j.polymdegradstab.2010.09.008'
def source_issues(r):
    issues=[];d=r['DOI'];n=r['sample_state'];gas=r['atmosphere']
    if d==PAN:issues.append('LOI_only_pressed_parent_TG_unknown')
    if d==PVA and gas=='air':
        if n in ['PVA0','PVA15'] and r.get('T5_C'):issues.append('conflicting_air_T5')
        if n in ['PVA5','PVA10']:
            expected={'PVA5':'275.2','PVA10':'253.1'}[n]
            if r.get('T5_C')!=expected or r.get('source_raw_T5_C')!=expected or 'weight loss5wt%' not in r.get('source_T5_definition',''):issues.append('middle_T5_omitted_changed_or_undefined')
    if d==PVA and n=='PVA15' and gas=='N2' and any(r.get(k) for k in ['R700_pct','residue_pct']):issues.append('conflicting_N2_PVA15_residue')
    if d==PLA and n!='PLA' and any(r.get(k) for k in ['R700_pct','residue_pct','residue_temp_C']):issues.append('unbound_residue_temperature')
    if r.get('Tonset_C'):issues.append('no_independent_Tonset_definition')
    if r.get('T10_C'):issues.append('no_own_T10_report')
    if r['heating_rate_C_min']!='20':issues.append('other_assay_rate_borrowed')
    if r.get('material_form_TGA')!=r.get('material_form_LOI'):issues.append('forms_not_bridged')
    if d==PVA and any(r.get('Tmax1_C')==v for v in ['343','441','442']):issues.append('MCC_peak_not_TG')
    if d==PVA and ('+/-' in r.get('source_preparation','') or '±' in r.get('source_preparation','')):issues.append('native_preparation_sign_unresolved')
    return issues
class SourceGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=rows();cls.by={key(r):r for r in cls.rows};cls.manifest=json.loads(MANIFEST.read_text())
    def test_default_paths_real_archive(self):
        self.assertTrue(MANIFEST.is_file());self.assertEqual(MANIFEST.relative_to(ROOT).parts[:3],('data','curation','archive'))
    def test_exact_condition_and_state_counts(self):
        self.assertEqual(len(self.rows),16);self.assertEqual(len({(r['DOI'],r['sample_state']) for r in self.rows}),12)
    def test_primary_not_root_or_main(self):
        self.assertEqual(self.manifest['counts']['rootapproved'],0);self.assertEqual(self.manifest['counts']['published'],0)
    def test_all_selected_source_constraints(self):
        self.assertTrue(all(not source_issues(r) for r in self.rows))
    def test_pan_coldpress_unknown_rejected(self):
        r=dict(self.rows[0],DOI=PAN);self.assertIn('LOI_only_pressed_parent_TG_unknown',source_issues(r))
    def test_air_T5_conflict_not_selected(self):
        r=dict(self.by[PVA,'PVA0','air'],T5_C='307.6');self.assertIn('conflicting_air_T5',source_issues(r))
    def test_nitrogen_residue_conflict_not_selected(self):
        r=dict(self.by[PVA,'PVA15','N2'],R700_pct='19.4');self.assertIn('conflicting_N2_PVA15_residue',source_issues(r))
    def test_unknown_temp_not_program_end(self):
        r=dict(self.by[PLA,'TPLA','N2'],R700_pct='7.1');self.assertIn('unbound_residue_temperature',source_issues(r))
    def test_zero_is_reported_purePLA(self):
        r=self.by[PLA,'PLA','N2'];self.assertEqual((r['R700_pct'],r['residue_temp_C']),('0','700'))
    def test_no_correcting_char_1point2(self):
        r=self.by[PLA,'PLA/APP20','N2'];self.assertEqual(r['source_raw_residue_pct'],'1.2');self.assertEqual(r.get('R700_pct',''),'')
    def test_mcc_peak_not_TG(self):
        r=dict(self.by[PVA,'PVA5','N2'],Tmax1_C='441');self.assertIn('MCC_peak_not_TG',source_issues(r))
    def test_FTIR_or_DSC_rate_not_TG(self):
        r=dict(self.by[PVA,'PVA5','N2'],heating_rate_C_min='10');self.assertIn('other_assay_rate_borrowed',source_issues(r))
    def test_no_onset_threshold_inference(self):
        r=dict(self.rows[0],Tonset_C=self.rows[0]['T5_C']);self.assertIn('no_independent_Tonset_definition',source_issues(r))
    def test_no_unreported_T10(self):
        r=dict(self.rows[0],T10_C='350');self.assertIn('no_own_T10_report',source_issues(r))
    def test_same_form_required(self):
        r=dict(self.rows[0],material_form_TGA='unprocessed powder');self.assertIn('forms_not_bridged',source_issues(r))
    def test_recipe_basis_not_reconstructed(self):
        r=self.by[PLA,'TPLA/APP20','N2'];self.assertIn('80:20',r['composition']);self.assertIn('0.01wt%',r['composition']);self.assertNotIn('64:16:20',r['composition'])
    def test_water_and_MCC_defined_separately(self):
        r=self.by[PVA,'PVA0','N2'];self.assertIn('not100-180C',r['Tmax1_assignment']);self.assertIn('maximum weight loss rate',r['source_Tmax_definition'])
    def test_LOI_repeats_not_error(self):
        r=self.by[PLA,'PLA','N2'];self.assertEqual(r['source_LOI_n_reported'],'5');self.assertEqual(r.get('LOI_uncertainty_pct',''),'')
    def test_pending_metrics_do_not_erase_uncontested_TG(self):
        a=self.by[PVA,'PVA15','air'];n=self.by[PVA,'PVA15','N2'];self.assertEqual(a['T5_C'],'');self.assertEqual(a['Tmax1_C'],'294.3');self.assertEqual(n['R700_pct'],'');self.assertEqual(n['T5_C'],'250.9')
    def test_two_gases_do_not_make_eight_PVA_states(self):
        self.assertEqual(len({r['sample_state'] for r in self.rows if r['DOI']==PVA}),4)
    def test_preparation_control_glyph_not_plusminus(self):
        r=self.by[PVA,'PVA0','air'];self.assertIn('U+0003',r['source_preparation']);self.assertIn('sign unresolved',r['source_preparation'])
        wrong=dict(r,source_preparation='PVA DP1788+/-50 film0.5+/-0.1mm');self.assertIn('native_preparation_sign_unresolved',source_issues(wrong))
    def test_two_uncontested_middle_T5_preserved(self):
        for name,value in [('PVA5','275.2'),('PVA10','253.1')]:
            r=self.by[PVA,name,'air'];self.assertEqual((r['T5_C'],r['source_raw_T5_C']),(value,value))
    def test_middle_T5_omission_is_not_safe_substitute(self):
        r=dict(self.by[PVA,'PVA5','air'],T5_C='');self.assertIn('middle_T5_omitted_changed_or_undefined',source_issues(r))
    def test_middle_T5_wrong_value_rejected(self):
        r=dict(self.by[PVA,'PVA10','air'],T5_C='293');self.assertIn('middle_T5_omitted_changed_or_undefined',source_issues(r))
    def test_middle_T5_wrong_definition_rejected(self):
        r=dict(self.by[PVA,'PVA5','air'],source_T5_definition='onset inferred from curve');self.assertIn('middle_T5_omitted_changed_or_undefined',source_issues(r))
if __name__=='__main__':unittest.main()
