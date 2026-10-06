import csv,copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import pairing as p,textile_scope as scope
with(ROOT/'data/incoming/verified_source_batch_20261006_b406_local_material.csv').open(newline='')as f:ROWS=list(csv.DictReader(f))
DELTA=json.loads((ROOT/'data/curation/archive/20261006/source_review_manifest_b406.json').read_text())['scope_delta']
A='10.1021/acsapm.4c03632';B='10.1021/acsapm.3c01598'
class B406ScientificBoundaries(unittest.TestCase):
 def test_ten_states_thirteen_TG_not_gas_inflated(self):
  self.assertEqual(len(ROWS),13);self.assertEqual(len({p.sample_state_id(r)for r in ROWS}),10);self.assertEqual({r['DOI']for r in ROWS},{A,B,'10.1021/acsami.5b10287','10.1021/acsami.7b06250'})
 def test_PA12_exact_native_printed_LOI_values(self):
  self.assertEqual({r['native_sample_label']:r['LOI_pct']for r in ROWS if r['DOI']==B},{'PA12':'20.6','PA12/M':'24.5','PA12/HK':'23.5','PA12/MHK':'25.7'})
  for r in ROWS:
   if r['DOI']==B:self.assertIn('exactnativetextlabels',r['LOI_locator']);self.assertIn('notcurveread',r['LOI_locator'])
 def test_PA12_ordinary_TG_not_TGIR_rate(self):
  for r in ROWS:
   if r['DOI']==B:self.assertEqual(r['heating_rate_C_min'],'10');self.assertEqual(r['atmosphere'],'N2');self.assertIn('sintered',r['material_form_TGA'])
 def test_PA12_source_defined_Tmax_and_R700_not_scanend800(self):
  expected={'PA12':('476.98','0.82'),'PA12/M':('472.18','2.07'),'PA12/HK':('479.16','1.08'),'PA12/MHK':('478.64','1.75')}
  for r in ROWS:
   if r['DOI']==B:self.assertEqual((r['Tmax1_C'],r['R700_pct']),expected[r['native_sample_label']]);self.assertEqual(r['residue_temp_C'],'700');self.assertIn('maximumweightlossrate',r['source_Tmax_definition']);self.assertEqual(r.get('R800_pct',''),'')
 def test_PA6_only_three_absolute_own_LOI_not_UL94_or_neat(self):
  self.assertEqual({r['native_sample_label']:r['LOI_pct']for r in ROWS if r['DOI']==A},{'PA6/10ADP':'24.6','PA6/10ADP/3PDBD':'28.4','PA6/13PDBD':'23.7'})
  self.assertFalse(any(r['native_sample_label']in {'PA6','PA6/13ADP','IsolatedPDBD'}for r in ROWS))
 def test_PA6_undefined_maximum_labels_remain_raw(self):
  for r in ROWS:
   if r['DOI']==A:
    self.assertEqual(r['Tmax1_C'],'');self.assertTrue(r['source_Tmax_ambiguous_C']);self.assertTrue(r['T5_C']);bad=copy.deepcopy(r);bad['Tmax1_C']=r['source_Tmax_ambiguous_C'];self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(bad))
 def test_PA6_only_explicit_ternary_air_R800(self):
  for r in ROWS:
   if r['DOI']==A:
    explicit=r['native_sample_label']=='PA6/10ADP/3PDBD'and r['atmosphere']=='air';self.assertEqual(r['R800_pct'],'6.5'if explicit else'');self.assertEqual(r['residue_temp_C'],'800'if explicit else'')
    if not explicit:
     bad=copy.deepcopy(r);bad['R800_pct']=r['source_raw_residue_pct'];self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(bad))
 def test_PDBD_powder_not_cast_composite_TG(self):
  bad=copy.deepcopy(ROWS[0]);bad['material_form_TGA']='isolated dried PDBD powder';self.assertIn('specimen_form_mismatch',p.evidence_issues(bad))
 def test_no_unproved_recipe_normalization(self):
  bad=copy.deepcopy(ROWS[-1]);bad['composition']='UNPROVEN98wt%PA12/2wt%filler final retained fraction';self.assertIn('material_scope_review_pending_or_stale',p.evidence_issues(bad))
 def test_unknown_PA12_LOI_protocol_and_repeats_stay_missing(self):
  for r in ROWS:
   if r['DOI']==B:
    for k in ['LOI_standard','LOI_specimen_geometry','LOI_instrument','LOI_replicates','source_TGA_replicates','LOI_uncertainty_pct']:self.assertEqual(r[k],'')
 def test_13_scope_bindings_exact_and_number_mutation_rejected(self):
  self.assertEqual(len(DELTA),13)
  for r in ROWS:
   d=next(d for d in DELTA if (d['source_identity'],d['sample_state_id'],d['reviewed_measurement_fingerprint'])==scope.observation_key(r));self.assertEqual(d['scope_identity_sha256'],scope.scope_identity_sha256(r));self.assertFalse(p.evidence_issues(r))
  bad=copy.deepcopy(ROWS[-1]);bad['LOI_pct']='99';self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(bad))
 def test_only_sourceapproved_payload_no_private_path(self):
  self.assertFalse(any(r['DOI']in {'10.1021/acsapm.4c00340','10.1021/acsapm.5c04297','10.1021/acsapm.5c03272','10.1021/acsapm.5c04605'}for r in ROWS))
  self.assertNotRegex(json.dumps(ROWS),'|'.join('/'+name+'/' for name in ['Users','Volumes'])+'|'+':'.join(['smb','//'])+'|'+':'.join(['file','//']))

 def test_HTN_only_experimental_hybrid1_not_neat_or_calculated(self):
  rs=[r for r in ROWS if r['DOI']=='10.1021/acsami.5b10287'];self.assertEqual(len(rs),1);r=rs[0];self.assertEqual(r['native_sample_label'],'HTN/15%BM@Al-PPi-1');self.assertEqual((r['LOI_pct'],r['T5_C'],r['Tmax1_C'],r['R700_pct']),('28.0','383','471','15.7'));self.assertIn('expnotcal',r['TG_locator']);self.assertIn('85wt%',r['composition'])
 def test_PA11_only_S3S7_N2_no_air_or_prior_control_promotion(self):
  rs=[r for r in ROWS if r['DOI']=='10.1021/acsami.7b06250'];self.assertEqual({r['native_sample_label']for r in rs},{'S3','S7'});self.assertEqual({r['atmosphere']for r in rs},{'N2'});self.assertEqual({r['native_sample_label']:r['R700_pct']for r in rs},{'S3':'9.6','S7':'21.5'})
 def test_PA11_initial_raw_temperatures_not_T5_T10_Tonset(self):
  for r in ROWS:
   if r['DOI']=='10.1021/acsami.7b06250':
    for k in ['T5_C','T10_C','Tonset_C','Tmax1_C']:self.assertEqual(r.get(k,''),'')
    self.assertIn(r['source_initial_decomposition_C'],{'267.5','327.2'});self.assertIn('criterionunreported',r['source_initial_definition']);bad=copy.deepcopy(r);bad['Tonset_C']=r['source_initial_decomposition_C'];self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(bad))
 def test_PA11_original_plusminus_not_defined_SD_or_UL94_replicates(self):
  for r in ROWS:
   if r['DOI']=='10.1021/acsami.7b06250':self.assertEqual(r['LOI_uncertainty_type'],'plusminus_statistical_definition_unreported');self.assertEqual(r['source_LOI_n'],'unreported');self.assertEqual(r.get('LOI_replicates',''),'');self.assertEqual(r.get('LOI_specimen_geometry',''),'')
if __name__=='__main__':unittest.main(verbosity=2)
