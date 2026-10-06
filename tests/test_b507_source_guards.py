import copy,csv,json,unittest,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
M=json.loads((ROOT/'data/curation/archive/20261007/source_review_manifest_b507.json').read_text())
raw=M['raw_scientific_views'];pub=M['selected_scientific_rows']
A='10.1039/c4ra09243k';B='10.1039/c6ra15542a';C='10.1002/pat.5605'
def one(doi,label):return next(x for x in raw if x['DOI']==doi and x['sample_state']==label)
def allowed(r):return r['source_numeric_role']=='candidate' and r['pairing_status']=='verified_exact'
def exact(a,b):return all(a.get(k,'')==b.get(k,'') for k in set(a)|set(b))
class SourceRisks(unittest.TestCase):
 def test_01_all_states_partition(self):
  self.assertEqual(len(raw),22);self.assertEqual(sum(x['source_numeric_role']=='candidate' for x in raw),12);self.assertEqual(sum(x['source_numeric_role']=='wholehold' for x in raw),6)
 def test_02_no_formal_count(self):
  self.assertEqual(M['rootapproved'],0);self.assertEqual(M['published'],0);self.assertFalse(M['full_private_reuse_approved'])
 def test_03_PP_neat_is_explicit_zero_recipe(self):
  r=one(A,'PP');self.assertIn('explicitly includes0wt%PP',r['pairing_evidence']);self.assertEqual(r['LOI_pct'],'18.0');self.assertEqual(r['T5_C'],'271')
 def test_04_PP_all_six(self):
  self.assertEqual([r['LOI_pct'] for r in raw if r['DOI']==A and r['source_numeric_role']=='candidate'],['18.0','19.7','22.0','25.1','18.9','19.8'])
 def test_05_PA_active_basis_unknown(self):
  r=one(A,'PP/20PA');self.assertIn('50wt%aqueous',r['composition']);self.assertIn('active/drybasis',r['source_recipe_limits']);self.assertNotIn('PP80/',r['composition'])
 def test_06_air_numeric_not_genericN2(self):
  self.assertTrue(all(x['atmosphere']=='air' for x in raw if x['DOI']==A));self.assertEqual(len([r for r in pub if r['DOI']==A]),6)
 def test_07_DSC_flow_not_TG(self):
  r=one(A,'PP');self.assertEqual(r['gas_flow_mL_min'],'');self.assertEqual(r['heating_rate_C_min'],'20');self.assertIn('DSC60mLmin notordinaryTG',r['source_TG_unknowns'])
 def test_08_PP_Tmax_raw(self):
  r=one(A,'PP/20PEI');self.assertEqual(r['source_Tmax_ambiguous_C'],'392');self.assertEqual(r['Tmax1_C'],'');self.assertIn('without explicit maximum-rate',r['source_Tmax_definition'])
 def test_09_fixed600_not500muffle(self):
  r=one(A,'PP/20PEC');self.assertEqual((r['R600_pct'],r['residue_temp_C']),('11','600'));self.assertNotIn('R500_pct',r)
 def test_10_ingredient_noLOI(self):
  self.assertTrue(all(one(A,n)['source_numeric_role']=='TG_only' and not one(A,n)['LOI_pct'] for n in ['PEI','PA','PEC']))
 def test_11_PEC_ingredientwash_not_finished(self):
  r=one(A,'PP/20PEC');self.assertIn('Ingredientneutral',r['source_preparation_scope_note']);self.assertIn('no durability wash',r['washing_state'].replace('no durability wash assigned','no durability wash'))
 def test_12_LDHdosebasis_hold(self):
  rs=[r for r in raw if r['DOI']==B and r['sample_state']!='PP'];self.assertEqual(len(rs),5);self.assertTrue(all(not allowed(r) for r in rs));self.assertTrue(all('cannot choose denominator' in r['pairing_evidence'] for r in rs))
 def test_13_LDHcontrol_history_hold(self):
  r=one(B,'PP');self.assertFalse(allowed(r));self.assertIn('notexplicit',r['pairing_evidence'])
 def test_14_LDH_50_is_massloss(self):
  r=one(B,'PP-LDH5-ZrP15');self.assertEqual(r['T50_C'],'470');self.assertEqual(r['T5_C'],'');self.assertEqual(r['Tmax1_C'],'479')
 def test_15_LDH_W_not_R600(self):
  r=one(B,'PP-ZrP20');self.assertEqual(r['source_raw_residue_pct'],'12.86');self.assertEqual(r['R600_pct'],'');self.assertEqual(r['residue_temp_C'],'');self.assertIn('after combustion',r['source_residue_definition'])
 def test_16_LDH_LOIaboutfive_not_exact_stats(self):
  r=one(B,'PP');self.assertEqual(r['source_LOI_n_reported'],'about five');self.assertEqual(r['LOI_uncertainty_pct'],'');self.assertEqual(r['gas_flow_mL_min'],'20')
 def test_17_PBT_all_injectionstates(self):
  rs=[r for r in pub if r['DOI']==C];self.assertEqual(len(rs),6);self.assertEqual([r['LOI_pct'] for r in rs],['27.6','27.1','27.2','27.5','28.1','29.0']);self.assertEqual([r['source_injection_time_s'] for r in rs],['1','2','3','5','1','1'])
 def test_18_PBT_commonfinal_history(self):
  r=one(C,'PBT/20 wt% IFR-2 s');self.assertIn('only common final extrude/dry/inject series',r['pairing_evidence']);self.assertIn('aliquot geometry/cutting unreported',r['pairing_evidence']);self.assertEqual(r['material_form_TGA'],r['material_form_LOI'])
 def test_19_PBT_T5_DSC_and_rawpeak(self):
  r=one(C,'PBT/20 wt% IFR-2 s');self.assertEqual(r['T5_C'],'349');self.assertEqual(r['source_Tmax_ambiguous_C'],'396');self.assertEqual(r['Tmax1_C'],'');self.assertNotEqual(r['T5_C'],'230.5')
 def test_20_PBT_unknownRtemperature(self):
  r=one(C,'PBT/30 wt% IFR-1 s');self.assertEqual(r['source_raw_residue_pct'],'19');self.assertEqual(r['R800_pct'],'');self.assertEqual(r['residue_temp_C'],'');self.assertEqual(r['TG_end_C'],'800')
 def test_21_PBT_TGmass_not_XRDmechanical(self):
  r=one(C,'PBT/20 wt% IFR-1 s');self.assertEqual((r['source_TG_mass_mg'],r['gas_flow_mL_min'],r['source_LOI_sample_dimensions_mm']),('5.5','100','125x7x3'));self.assertNotEqual(r['source_TG_mass_mg'],'10')
 def test_22_PBT_neat_onlyLOI(self):
  r=one(C,'PBT');self.assertEqual(r['source_numeric_role'],'LOI_only');self.assertEqual(r['LOI_pct'],'21.5');self.assertEqual(r['T5_C'],'');self.assertEqual(r['atmosphere'],'')
 def test_23_unknown_recipe_not_normalized(self):
  r=one(C,'PBT/30 wt% IFR-1 s');self.assertIn('amountsunreported',r['composition']);self.assertIn('no inferPBTremainder',r['composition'])
 def test_24_real_field_mutation_rejected(self):
  r=pub[0];bad=copy.deepcopy(r);bad['treatment_method']='LOI-only injection branch';self.assertFalse(exact(r,bad));bad=copy.deepcopy(r);bad['unknown_extension']='0';self.assertFalse(exact(r,bad))
 def test_25_sourcefacts_are_own(self):
  self.assertTrue(all(r['source_numeric_role']=='candidate' for r in pub));self.assertEqual(len({r['DOI'] for r in pub}),2);self.assertTrue(all(r['LOI_uncertainty_pct']=='' for r in pub))
 def test_26_same_conditions_no_extra_state(self):
  keys={(r['DOI'],r['sample_state'],r['washing_state']) for r in pub};self.assertEqual(len(keys),12);self.assertEqual(len(M['scope_entries']),12)
 def test_27_public_privacy(self):
  t=json.dumps(M);self.assertNotIn('/Volumes/',t);self.assertNotIn('/Users/',t);self.assertNotIn('smb://',t)
 def test_28_current_measurement_gate_rejects_changed_value(self):
  sys.path.insert(0,str(ROOT/'scripts'));import pairing
  bad=copy.deepcopy(pub[0]);bad['T5_C']='999';self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(bad))
 def test_29_current_scope_gate_rejects_changed_parent(self):
  sys.path.insert(0,str(ROOT/'scripts'));import pairing,textile_scope
  r=pub[0];bad=copy.deepcopy(r);bad['material_form_TGA']='unmolded ingredient powder';self.assertNotEqual(textile_scope.scope_identity_sha256(r),textile_scope.scope_identity_sha256(bad));self.assertIn('specimen_form_mismatch',pairing.evidence_issues(bad))
 def test_30_complete_rowprotects_definition(self):
  r=pub[-1];bad=copy.deepcopy(r);bad['source_residue_definition']='Assume800Cfromprogram';self.assertFalse(exact(r,bad));self.assertEqual(bad['reviewed_measurement_fingerprint'],r['reviewed_measurement_fingerprint'])
if __name__=='__main__':unittest.main()
