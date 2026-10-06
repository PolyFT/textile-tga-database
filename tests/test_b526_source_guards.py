import copy, json, pathlib, unittest

ROOT = pathlib.Path(__file__).resolve().parent
MANIFEST = ROOT.parent / 'data/curation/archive/20261007/source_review_manifest_b526.json'
M = json.loads(MANIFEST.read_text())
P = M['selected_scientific_rows']; RAW = M['raw_observations']
A, B, C = '10.1002/app.43370', '10.1002/pat.4920', '10.1002/app.50015'
KEY = lambda r: (r['DOI'], r['sample_state'], r['atmosphere'], r['heating_rate_C_min'])
PROVIDED = {KEY(r):r for r in P}
def accepted(r):
    original=PROVIDED.get(KEY(r))
    return original is not None and r == original
def one(doi,label):
    return next(r for r in RAW if r['DOI']==doi and r['sample_state']==label)

class SourceGuards(unittest.TestCase):
    def test_all_selected_exact_source_fields(self):self.assertTrue(all(accepted(r) for r in P))
    def test_partition_conditions_not_samples(self):
        self.assertEqual((len(P),len({(r['DOI'],r['sample_state']) for r in P})),(5,5))
        self.assertEqual(sum(r['source_numeric_role']=='wholehold' for r in RAW),13)
    def test_A_two_gases_not_eight_states(self):
        r=[r for r in RAW if r['DOI']==A and r['source_numeric_role']=='wholehold'];self.assertEqual((len(r),len({x['sample_state'] for x in r})),(8,4))
    def test_A_powderbar_history_no_admit(self):self.assertFalse(any(r['DOI']==A for r in P))
    def test_A_loss10_not_peak_or_water_relabel(self):
        r=one(A,'PA11');self.assertEqual((r['T10_C'],r['T50_C'],r['Tmax1_C']),('403.0','430.3',''))
    def test_A_actual500_not800_terminal(self):
        r=one(A,'PA11/AlPi20');self.assertEqual((r['residue_temp_C'],r['R500_pct'],r['R800_pct']),('500','2.4',''))
    def test_A_air_actual650(self):
        r=next(r for r in RAW if r['DOI']==A and r['sample_state']=='PA11/AlPi15/SA-LDH5' and r['atmosphere']=='air');self.assertEqual((r['residue_temp_C'],r['R650_pct']),('650','21.2'))
    def test_A_uncertainty_glyph_not_plusminus(self):
        r=one(A,'PA11');self.assertEqual((r['LOI_uncertainty_pct'],r['source_LOI_original_cell']),('','23.0 6 0.2'))
    def test_B_only_uniquely_mapped20(self):self.assertEqual([r['sample_state'] for r in P if r['DOI']==B],['PA6/MCN-20%'])
    def test_B_onset_not_T5_or_T10(self):
        r=one(B,'PA6/MCN-20%');self.assertEqual((r['source_raw_Tonset_C'],r['T5_C'],r['T10_C'],r['Tonset_C']),('372.4','','',''))
    def test_B_maximum_decomposition_not_ratepeak(self):
        r=one(B,'PA6/MCN-20%');self.assertEqual((r['source_Tmax_ambiguous_C'],r['Tmax1_C']),('452.4',''))
    def test_B_residue800_explicit_body(self):
        r=one(B,'PA6/MCN-20%');self.assertEqual((r['R800_pct'],r['residue_temp_C']),('12.1','800'))
    def test_B_zero_unknown_temperature_not800(self):
        r=one(B,'PA6/g-C3N4-10%');self.assertEqual((r['source_raw_residue_pct'],r['source_raw_residue_temp_C'],r['R800_pct']),('0','',''))
    def test_B_10percent_ratio_not_selected_by_order(self):
        r=one(B,'PA6/MCN-10%;TGgC3N4MgOratiounknown');self.assertEqual((r['LOI_pct'],r['source_raw_Tonset_C'],r['source_raw_residue_pct']),('','378.4','3.1'));self.assertFalse(accepted(r))
    def test_B_DSCmelting_not_TGpeak(self):
        r=one(B,'PA6/MCN-20%');self.assertEqual((r['source_DSC_Tm_C'],r['Tmax1_C']),('229.1',''))
    def test_B_TGIRmass_not_ordinarymass(self):self.assertEqual(one(B,'PA6/MCN-20%')['source_TG_mass_mg'],'4')
    def test_B_preparationwater_not_durabilitywash(self):
        r=one(B,'PA6/MCN-20%');self.assertIn('boilingwaterextract',r['treatment_method']);self.assertEqual(r['washing_state'],'no durabilitywash assigned')
    def test_B_purecontrol_processing_not_borrowed(self):self.assertFalse(accepted(one(B,'PA6')))
    def test_C_hotpress_motherstate_required(self):
        r=copy.deepcopy(next(r for r in P if r['DOI']==C));r['material_form_TGA']='unmoldedextrudedpellet';self.assertFalse(accepted(r))
    def test_C_preserve_actual_T5_and_R700(self):
        r=one(C,'PA6/3%DOPO-MWCNTs');self.assertEqual((r['T5_C'],r['R700_pct'],r['residue_temp_C'],r['R800_pct']),('402.7','6.9','700',''))
    def test_C_FTIRpoint_not_original_T5(self):
        r=copy.deepcopy(next(r for r in P if r['sample_state']=='PA6/3%DOPO-MWCNTs'));r['T5_C']='400';self.assertFalse(accepted(r))
    def test_C_Tmax_unknown_no_canonicalpeak(self):self.assertTrue(all(not r['Tmax1_C'] and r['source_Tmax_ambiguous_C'] for r in P if r['DOI']==C))
    def test_C_nonTG_Table5_not_TGvalues(self):
        r=one(C,'PA6/3%DOPO');self.assertIn('Table4',r['TG_locator']);self.assertEqual(r['T5_C'],'392.4')
    def test_C_purecontrol_held(self):self.assertFalse(accepted(one(C,'PA6')))
    def test_C_unmeasured_loading_no_TGborrow(self):
        r=one(C,'PA6/2%DOPO-MWCNTs');self.assertEqual((r['LOI_pct'],r['T5_C'],r['R700_pct']),('24.5','',''));self.assertFalse(accepted(r))
    def test_powder_additives_no_LOIborrow(self):self.assertTrue(all(not r['LOI_pct'] for r in RAW if r['source_numeric_role']=='TG_only'))
    def test_unknown_TGgas_rejected(self):
        r=copy.deepcopy(P[0]);r['atmosphere']='';self.assertFalse(accepted(r))
    def test_TGIR_condition_cannotreplace_ordinaryTG(self):
        r=copy.deepcopy(P[0]);r['TG_end_C']='600';self.assertFalse(accepted(r))
    def test_fullfield_treatment_and_literal0_None_protected(self):
        for k,v in [('treatment_method','LOIonlyinjection'),('unknown_field','0'),('unknown_field','None')]:
            r=copy.deepcopy(P[0]);r[k]=v;self.assertFalse(accepted(r))
    def test_scope_class_and_bindings(self):
        self.assertEqual({r['scope_class'] for r in M['scope_entries']},{'fiber_forming_polymer_composite'});self.assertEqual(len(M['scope_entries']),5)
    def test_no_root_or_fullreuse_or_public_approval(self):self.assertEqual((M['rootapproved'],M['published'],M['full_private_reuse_approved']),(0,0,False))
    def test_public_privacy(self):self.assertFalse(any(x in json.dumps(M) for x in ['/Volumes/','/Users/','smb://','Downloaded from','University Of British Columbia']))

if __name__=='__main__':unittest.main()
