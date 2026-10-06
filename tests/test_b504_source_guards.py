import json,csv,copy,unittest,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT / 'data/curation/archive/20261007/source_review_manifest_b504.json'
manifest=json.loads(MANIFEST.read_text())
raw=manifest["raw_scientific_views"];pub=manifest["selected_scientific_rows"]
def one(doi,label,gas=None):return next(r for r in raw if r['DOI'].endswith(doi) and r['sample_state']==label and (gas is None or r['atmosphere']==gas))
def sameprovided(a,b):
 return all(a.get(k,'')==v for k,v in b.items())
def token(t,v):return bool(re.search(r'(?<![a-z0-9])'+re.escape(t)+r'(?![a-z0-9])',v,re.I))
class AfterSourceTests(unittest.TestCase):
 def test_neatPBT_PTFE_unknown(self):
  r=one('c5ra18829f','PBT');self.assertIn('PTFE applicability to control unreported',r['composition']);self.assertIn('nor explicitly label PTFE in pure PBT',r['source_preparation'])
 def test_PTFE_dose_not_total100(self):
  r=one('c5ra18829f','PBT/CPPA15%');self.assertIn('not normalized',r['composition']);self.assertIn('no infer composition sum100',r['source_recipe_limits'])
 def test_PBT20_conflict_wholeheld(self):
  r=one('c5ra18829f','PBT/CPPA20%');self.assertEqual((r['LOI_pct'],r['source_LOI_alternative_pct']),('26.2','26.8'));self.assertEqual(r['source_numeric_role'],'wholeheld');self.assertNotIn(r,pub)
 def test_PBT_exact_onset5(self):
  r=one('c5ra18829f','PBT/CPPA15%');self.assertEqual(r['T5_C'],'365');self.assertEqual(r['Tonset_C'],'');self.assertIn('weightloss is5%',r['source_T5_definition'])
 def test_PBT_measured_calc_not_substitute(self):
  r=one('c5ra18829f','PBT/CPPA25%');self.assertEqual(r['R700_pct'],'16');self.assertEqual(r['source_calculated_R700_pct'],'12');v=one('c5ra18829f','Calculated PBT/CPPA25%');self.assertEqual(v['R700_pct'],'')
 def test_PBT_two_weightloss_stages_not_residue_or_rates(self):
  r=one('c5ra18829f','PBT');self.assertEqual((r['source_TG_stage1_weight_loss_pct'],r['source_TG_stage2_weight_loss_pct']),('51','93.6'));self.assertIn('not residualmass or masslossrate',r['source_TG_stage_weight_loss_definition'])
 def test_PBT_TG_not_MCC(self):
  r=one('c5ra18829f','PBT');self.assertEqual((r['gas_flow_mL_min'],r['heating_rate_C_min']),('50','10'));bad=copy.deepcopy(r);bad['gas_flow_mL_min']='80';bad['heating_rate_C_min']='60';self.assertFalse(sameprovided(bad,r))
 def test_PP_common_hotpressonly_filled(self):
  r=one('c7ra09868e','PP/25 wt% DPPIP','N2');self.assertIn('Generic2.4 filledPPblend',r['pairing_evidence']);self.assertIn('purePP control preparation not explicitly',r['source_preparation'])
 def test_PP_two_gases_one_scopeidentity(self):
  x=[r for r in pub if r['DOI'].endswith('c7ra09868e')];self.assertEqual(len(x),2);scope=manifest['scope_entries'];ss=[e for e in scope if e['source_identity'].endswith('c7ra09868e')];self.assertEqual(len({e['sample_state_id'] for e in ss}),1);self.assertEqual(len({e['reviewed_measurement_fingerprint'] for e in ss}),2)
 def test_PP_neatcontrol_hold(self):
  for gas in ['N2','air']:self.assertEqual(one('c7ra09868e','Neat PP',gas)['source_numeric_role'],'wholeheld')
 def test_PP_wash_no_initialTG(self):
  r=one('c7ra09868e','PP/25 wt% DPPIP after water');self.assertEqual(r['LOI_pct'],'26.9');self.assertEqual(r['T5_C'],'');self.assertEqual(r['R700_pct'],'');self.assertEqual(r['source_numeric_role'],'LOIonly')
 def test_PP_unknown_Tmax_notcanonical(self):
  r=one('c7ra09868e','PP/25 wt% DPPIP','N2');self.assertEqual(r['Tmax1_C'],'');self.assertEqual(r['source_Tmax_ambiguous_C'],'404.6');self.assertEqual(r['source_Tmax2_ambiguous_C'],'451.0')
 def test_PP_residue_context700_notcone(self):
  r=one('c7ra09868e','PP/25 wt% DPPIP','air');self.assertEqual(r['R700_pct'],'0.1');self.assertEqual(r['residue_temp_C'],'700');self.assertIn('no substitute coneTable5',r['source_residue_definition'])
 def test_PA6_six_unassigned_processing(self):
  rs=[r for r in raw if r['DOI'].endswith('c6ra28293h')];self.assertEqual(len(rs),6);self.assertTrue(all(r['source_numeric_role']=='wholeheld' and 'TGpostformingparentunreported' not in r['source_preparation'] for r in rs));self.assertTrue(all('OrdinaryTG post-forming parent is not identified' in r['source_preparation'] for r in rs))
 def test_PA6_original_secondstage_onset_not5(self):
  for r in [r for r in raw if r['DOI'].endswith('c6ra28293h')]:self.assertEqual(r['T5_C'],'');self.assertEqual(r['T10_C'],'');self.assertIn('Tonset2',r['source_Tonset_definition']);self.assertIn('criterion not quantified',r['source_Tonset_definition'])
 def test_PA6_singlemax_originalcolumn2(self):
  r=one('c6ra28293h','PA6');self.assertEqual(r['Tmax1_C'],'');self.assertEqual(r['Tmax2_C'],'454.1')
 def test_PA6_droplet_replicates_notLOI(self):
  r=one('c6ra28293h','PA6');self.assertIn('droplet',r['source_LOI_definition'].lower());self.assertIn('not',r['source_LOI_definition'].lower())
 def test_literal_zero_none_allfield_protection(self):
  r=pub[0];bad=copy.deepcopy(r);bad['source_preparation']='None';self.assertFalse(sameprovided(bad,r));bad=copy.deepcopy(r);bad['source_TG_unknowns']='0';self.assertFalse(sameprovided(bad,r));self.assertTrue(sameprovided(r,copy.deepcopy(r)));bad=copy.deepcopy(r);bad['treatment_method']='changed heating history';self.assertFalse(sameprovided(bad,r));bad=copy.deepcopy(r);bad['source_preparation_scope_note']='assign separate MCC to TG';self.assertFalse(sameprovided(bad,r))
 def test_coverage_seven_notfive(self):
  p=manifest['profile_coverage_review'];self.assertEqual(p['actual_private_CSV_inputs'],7);self.assertEqual(p['comparators'],2297);self.assertEqual(len(p['coverage_description_metadata_patch_ledger']),2)
 def test_tokens_not_deposition_or_default30s(self):
  self.assertFalse(token('DEP','independent deposition'));self.assertFalse(token('T30S','default30s'));self.assertTrue(token('T30S','PP-T30S Lanzhou'));self.assertTrue(token('DEP','PA6/MCA/DEP-3'))
 def test_partition_individual_rowsets(self):
  p=manifest['condition_review'];self.assertEqual(len(p['condition_audit']),25);self.assertEqual(len({r['independent_condition_index'] for r in p['condition_audit']}),25);self.assertTrue(p['provided5andall_roleviews_exact_to_raw'])
 def test_source_temperature_no_inorganic_purechar_inference(self):
  self.assertTrue(all(r.get('residue_temp_C','') in ['','700'] for r in raw));self.assertTrue(all(r.get('R800_pct','')=='' for r in raw))
 def test_no_original_phase_rewrite(self):
  self.assertEqual(manifest['inherited_before_matrix_sha256'],'0c276131fac4a318d92cccc9ee10c36d456d56ea0888944e2397ab7cbd81d351');self.assertFalse(manifest['inherited_before_primary_payload_read'])
if __name__=='__main__':unittest.main()
