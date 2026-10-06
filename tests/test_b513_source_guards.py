import copy,json,pathlib,unittest
ROOT=pathlib.Path(__file__).resolve().parent
MANIFEST=ROOT/'data/curation/archive/20261007/source_review_manifest_b513.json'
if not MANIFEST.exists():MANIFEST=ROOT.parent/'data/curation/archive/20261007/source_review_manifest_b513.json'
M=json.loads(MANIFEST.read_text()); P=M['selected_scientific_rows']; A='10.1002/app.47298';B='10.1002/app.49188';C='10.1002/pat.4218'
def admissible(r):
 if r['DOI']==A:return False
 if r['DOI']==B:return r['sample_state']!='PA6' and r.get('source_numeric_role')=='candidate' and r.get('heating_rate_C_min')=='10' and r.get('atmosphere') in ['N2','air'] and bool(r.get('T5_C')) and r.get('material_form_TGA')==r.get('material_form_LOI')=='common injection-molded PA6 composite test material' and 'then injectionmolded' in r.get('pairing_evidence','')
 return r['sample_state']=='S2' and r.get('source_numeric_role')=='candidate' and r.get('LOI_pct')=='28.5' and r.get('T5_C')=='383.6' and r.get('R800_pct')=='4.9' and r.get('residue_temp_C')=='800' and r.get('heating_rate_C_min')=='10' and r.get('atmosphere')=='N2'
class SourceGuards(unittest.TestCase):
 def test_candidate_partition(self):self.assertEqual((len(P),len({(r['DOI'],r['sample_state']) for r in P})),(13,7))
 def test_both_gases_not_new_states(self):self.assertEqual((len([r for r in P if r['DOI']==B]),len({r['sample_state'] for r in P if r['DOI']==B})),(12,6))
 def test_all_selected_support(self):self.assertTrue(all(admissible(r) for r in P))
 def test_a_t_unknown_reject(self):
  r=copy.deepcopy(P[0]);r['DOI']=A;self.assertFalse(admissible(r))
 def test_b_purecontrol_reject(self):
  r=copy.deepcopy(P[0]);r['sample_state']='PA6';self.assertFalse(admissible(r))
 def test_b_TGIR20_cannot_supply(self):
  r=copy.deepcopy(P[0]);r['heating_rate_C_min']='20';self.assertFalse(admissible(r))
 def test_b_powder_loi_form_reject(self):
  r=copy.deepcopy(P[0]);r['material_form_TGA']='extruded pellet unknownthermalhistory';self.assertFalse(admissible(r))
 def test_b_no_parentprocessing_reject(self):
  r=copy.deepcopy(P[0]);r['pairing_evidence']='Onlydimensions';self.assertFalse(admissible(r))
 def test_b_unknownordinarygas_reject(self):
  r=copy.deepcopy(P[0]);r['atmosphere']='';self.assertFalse(admissible(r))
 def test_b_t5_not_onset_or_peak(self):self.assertTrue(all(r['T5_C'] and not r['Tonset_C'] and not r['Tmax1_C'] for r in P if r['DOI']==B))
 def test_b_unknown_residual_temperature_not700(self):self.assertTrue(all(not r['residue_temp_C'] and not r['R700_pct'] and not r['residue_pct'] and r['source_raw_residue_pct'] for r in P if r['DOI']==B))
 def test_b_duplicate_headers_not_duplicate_states(self):self.assertEqual({r['sample_state'] for r in P if r.get('source_Table3_column_header')=='PA6/H-FR1'},{'PA6/H-FR1','PA6/H-FR2','PA6/H-FR3'})
 def test_b_mapping_prose_anchor(self):self.assertTrue(all('body' in r['source_Table3_mapping_basis'] for r in P if r.get('source_Table3_column_header')=='PA6/H-FR1'))
 def test_c_same_s2_unique(self):self.assertEqual(len([r for r in P if r['DOI']==C]),1)
 def test_c_pure_conflict_notselected(self):
  r=copy.deepcopy(P[-1]);r['sample_state']='S0';self.assertFalse(admissible(r))
 def test_c_s9_conflict_notselected(self):
  r=copy.deepcopy(P[-1]);r['sample_state']='S9';self.assertFalse(admissible(r))
 def test_c_s15_loi_cannot_borrow_s9tg(self):
  r=copy.deepcopy(P[-1]);r['sample_state']='S15';r['LOI_pct']='30.8';self.assertFalse(admissible(r))
 def test_c_defined_tinitial_maps5loss(self):self.assertEqual((P[-1]['T5_C'],P[-1]['Tonset_C'],P[-1]['Tmax1_C']),('383.6','','433.6'))
 def test_c_explicit_r800_not_cone600(self):
  r=copy.deepcopy(P[-1]);r['residue_temp_C']='600';self.assertFalse(admissible(r))
 def test_c_sourced_signed_rate_not_temperature(self):self.assertEqual((P[-1]['source_Rpeak_pct_per_min'],P[-1]['source_Rpeak_magnitude_pct_per_min']),('−20.7','20.7'))
 def test_c_rate_unit_not_perC(self):self.assertIn('%/min',P[-1]['source_Rpeak_definition'])
 def test_no_uncertainty_borrowed(self):self.assertTrue(all(not r['LOI_uncertainty_pct'] and not r['source_LOI_n_reported'] for r in P))
 def test_all_scope_composite(self):self.assertEqual({r['material_scope_class'] for r in P},{'fiber_forming_polymer_composite'})
 def test_scope_observations_count(self):self.assertEqual(len(M['scope_entries']),13)
 def test_no_formal_or_reuse_approval(self):self.assertEqual((M['rootapproved'],M['published'],M['full_private_reuse_approved']),(0,0,False))
 def test_public_privacy(self):self.assertFalse(any(t in json.dumps(M) for t in ['/Volumes/','/Users/','smb://','University Of British Columbia']))
 def test_no_rawpeak_mapping_by_name(self):self.assertTrue(all(not r['Tmax1_C'] and r['source_Tmax_ambiguous_C'] for r in P if r['DOI']==B))
 def test_unknown_zero_none_literal(self):
  r=copy.deepcopy(P[-1]);r['unknown_field']='0';self.assertNotEqual(r,P[-1]);r['unknown_field']='None';self.assertNotEqual(r,P[-1])
if __name__=='__main__':unittest.main()
