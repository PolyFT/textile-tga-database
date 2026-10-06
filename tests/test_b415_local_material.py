"""Portable factual checks for the eight source-approved B415 records.

Run with --payload and --scope. The repository publisher supplies the paths.
No literature text or private paths are needed.
"""
import argparse,csv,json,copy,unittest,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--payload',type=Path,required=True);parser.add_argument('--scope',type=Path,required=True);args,rest=parser.parse_known_args()
else:args=argparse.Namespace(payload=ROOT/'data/incoming/verified_source_batch_20261006_b415_local_material.csv',scope=ROOT/'data/curation/textile_scope_registry.json');rest=[]
records=list(csv.DictReader(args.payload.open(newline='')));bindings=json.loads(args.scope.read_text())
if isinstance(bindings,dict):
 fingerprints={r['reviewed_measurement_fingerprint']for r in records};bindings=[e for e in bindings['entries']if e['reviewed_measurement_fingerprint']in fingerprints]
A='10.1021/acsomega.9b00346';B='10.1021/am200940z';C='10.1016/j.compositesa.2021.106423';D='10.1002/app.49027'
def row(d,s):return next(r for r in records if r['DOI']==d and r['native_sample_label']==s)
def expected_source_fields(r):
 if r['DOI']==D:
  expected={'PA6-1':['34','375','442','625'],'PA6-2':['31','379','443','614'],'PA6-3':['30','380','449','605'],'PA6-4':['33','375','453','618'],'PA6-5':['32','377','452','583']}
  return [r[k]for k in ['LOI_pct','T5_C','Tmax1_C','Tmax2_C']]==expected[r['native_sample_label']]
 if r['DOI']==B:return [r[k]for k in ['LOI_pct','T5_C','residue_pct','residue_temp_C']]==['31','318.8','12.3','700']
 return [r[k]for k in ['LOI_pct','residue_pct','residue_temp_C']]==({'PA6-PSA20%':['27','13.8','700'],'PA6-POSC20%':['32','13.4','700']}[r['native_sample_label']])
class ScientificTests(unittest.TestCase):
 def test_eight_states_not_peak_or_gas_count(self):
  self.assertEqual(len(records),8);self.assertEqual(len({(r['DOI'],r['sample_state'])for r in records}),8);self.assertEqual(Counter(r['DOI']for r in records),{D:5,B:1,C:2})
 def test_own_numeric_tables_exact(self):self.assertTrue(all(expected_source_fields(r)for r in records))
 def test_real_LOI_mutation_rejected(self):
  r=copy.deepcopy(row(B,'EVA2'));r['LOI_pct']='30.5';self.assertFalse(expected_source_fields(r))
 def test_all_app_residue800_held_not_700(self):
  for r in records:
   if r['DOI']==D:self.assertEqual(r['TG_end_C'],'700');self.assertEqual(r['source_raw_residue_temp_C'],'800');self.assertTrue(r['source_raw_residue_pct']);self.assertTrue(all(not r[k]for k in ['R700_pct','R800_pct','residue_pct','residue_temp_C']))
 def test_rate_defined_two_app_decomposition_peaks(self):
  for r in records:
   if r['DOI']==D:self.assertIn('maximum decomposition rate',r['source_Tmax_definition']);self.assertEqual(r['atmosphere'],'air');self.assertEqual(r['heating_rate_C_min'],'20')
 def test_corrected_method_page(self):
  for r in records:
   if r['DOI']==D:self.assertIn('PDFp4',r['conditions_locator']);self.assertIn('p4§2.4 rate20',r['TG_locator']);self.assertIn('p3–4',r['LOI_locator'])
 def test_unknown_FR_basis_not_PA80(self):
  for r in records:
   if r['DOI']==C:self.assertIn('20wt%',r['composition']);self.assertIn('not further specified',r['composition']);self.assertNotIn('PA680',r['composition'])
 def test_EVA_unmapped_weightloss_Tmax_retained(self):
  r=row(B,'EVA2');self.assertEqual([r['source_Tmax_ambiguous_C'],r['source_Tmax2_ambiguous_C']],['351.4','477.9']);self.assertFalse(r['Tmax1_C']);self.assertFalse(r['Tmax2_C'])
 def test_unknown_n_not_borrowed_contactangle(self):self.assertTrue(all(not r['LOI_replicates']and r['LOI_uncertainty_type']=='unreported'for r in records))
 def test_ordinary_N2_conditions_not_TGIR(self):
  for r in records:
   if r['DOI']==C:self.assertEqual(r['atmosphere'],'N2');self.assertEqual(r['heating_rate_C_min'],'10')
 def test_no_unverified_control_washed_or_lowdose(self):
  self.assertTrue(all(r['washing_state']=='initial prepared material'for r in records));self.assertNotIn(A,{r['DOI']for r in records});self.assertNotIn('EVA0',{r['native_sample_label']for r in records});self.assertNotIn('EVA4',{r['native_sample_label']for r in records});self.assertNotIn('PA6',{r['native_sample_label']for r in records})
 def test_T5_not_Tonset(self):self.assertTrue(all(not r['Tonset_C']and not r['T10_C']for r in records))
 def test_no_Cone_or_XPS_value_as_residue(self):self.assertEqual(row(B,'EVA2')['residue_pct'],'12.3');self.assertNotEqual(row(C,'PA6-PSA20%')['residue_pct'],'15.4')
 def test_scope_bindings_match_provided_fingerprints(self):
  self.assertEqual(len(bindings),8);self.assertEqual(Counter(e['reviewed_measurement_fingerprint']for e in bindings),Counter(r['reviewed_measurement_fingerprint']for r in records));self.assertTrue(all(e['decision']=='admit_textile'for e in bindings))
 def test_public_payload_without_private_paths(self):
  prefixes=['/'+'Users/','/'+'Volumes/','smb:'+chr(47)*2,'file:'+chr(47)*2];body=json.dumps(records+bindings,ensure_ascii=False);self.assertFalse(any(prefix in body for prefix in prefixes));self.assertTrue(any(prefix in ('/'+'Users/'+'example/source.pdf')for prefix in prefixes))
if __name__=='__main__':unittest.main(argv=['test_b415_scientific_guards']+rest)
