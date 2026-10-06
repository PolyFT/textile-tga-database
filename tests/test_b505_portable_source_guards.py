import copy,csv,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.dont_write_bytecode=True;sys.path.insert(0,str(ROOT/'scripts'));import pairing as p
INCOMING=ROOT/'data/incoming/verified_source_batch_20261007_b505_local_textiles.csv'
MANIFEST=ROOT/'data/curation/archive/20261007/source_review_manifest_b505.json'
class SourceGuards(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.rows=list(csv.DictReader(INCOMING.open()));c.by={r['sample_state']:r for r in c.rows};c.man=json.loads(MANIFEST.read_text())
 def test_01_real_default_archive_path(self):
  self.assertTrue(MANIFEST.is_file());self.assertEqual(MANIFEST.relative_to(ROOT).as_posix(),'data/curation/archive/20261007/source_review_manifest_b505.json');self.assertEqual(len(self.rows),7)
 def test_02_source_only_approval_not_publication(self):
  self.assertEqual((self.man['sourceapproved_unique_states'],self.man['sourceapproved_TG_conditions'],self.man['published']),(7,7,0));self.assertIn('pending',self.man['publication_blocking_complete_reuse'].lower())
 def test_03_CS_PA_not_selected(self):self.assertNotIn('CS-PA-DFS',self.by)
 def test_04_two_R800_supported_without_group_T10(self):
  for name,val in [('CS-PA@TiO2-DFS','27'),('Janus-DFS','29')]:
   r=self.by[name];self.assertEqual((r['R800_pct'],r['residue_temp_C']),(val,'800'));self.assertFalse(r['T10_C'])
 def test_05_original_group_raw_not_erased(self):
  for name in ['CS-PA@TiO2-DFS','Janus-DFS']:
   r=self.by[name];self.assertIn('277 ± 0.57',r['source_T10_group_values_raw']);self.assertIn('276 ± 1.52',r['source_T10_group_values_raw']);self.assertIn('277 ± 2.51',r['source_T10_group_values_raw']);self.assertIn('no confirmed sample-specific assignment',r['source_T10_entry_raw'])
 def test_06_group_assignment_cannot_inherit_existing_measurement_review(self):
  r=copy.deepcopy(self.by['Janus-DFS']);r['T10_C']='277';self.assertNotEqual(p.measurement_fingerprint(r),r['reviewed_measurement_fingerprint'])
 def test_07_pure_DFS_abstract_not_ratio_inference(self):
  r=self.by['pure DFS'];self.assertEqual((r['LOI_pct'],r['source_LOI_uncertainty_magnitude_pct']),('19.03','1.25'));self.assertIn('PDFp1abstract pureDFS19.03',r['LOI_locator'])
 def test_08_pure_T10_explicit_not_T5_or_onset(self):
  r=self.by['pure DFS'];self.assertEqual((r['T10_C'],r['source_T10_uncertainty_magnitude_C']),('344','2.64'));self.assertFalse(r['T5_C']);self.assertFalse(r['Tonset_C'])
 def test_09_actual_modified_LOI_mapping(self):
  for name,x in [('CS-PA@TiO2-DFS','35.3'),('Janus-DFS','35')]:self.assertEqual(self.by[name]['LOI_pct'],x)
 def test_10_Rmax_amplitude_unit_exact(self):
  for name,amp in [('control cotton','2.30'),('cotton-LP','1.01'),('cotton-APP','1.23'),('cotton-APP/LP','1.16')]:
   r=self.by[name];self.assertEqual(r['source_Rmax_pct_per_C'],amp);self.assertIn('(%/°C)',r['source_Rmax_definition']);self.assertIn('Table3',r['TG_locator'])
 def test_11_Rmax_cannot_become_Tmax(self):
  r=copy.deepcopy(self.by['control cotton']);r['Tmax1_C']=r['source_Rmax_pct_per_C'];self.assertNotEqual(p.measurement_fingerprint(r),r['reviewed_measurement_fingerprint']);self.assertEqual(self.by['control cotton']['Tmax1_C'],'420.1')
 def test_12_ordinary_not_TGIR_rate(self):
  r=self.by['cotton-LP'];self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['gas_flow_mL_min']),('N2','10','60'));z=copy.deepcopy(r);z['heating_rate_C_min']='20';self.assertNotEqual(p.measurement_fingerprint(z),r['reviewed_measurement_fingerprint'])
 def test_13_afterwashing_not_initial(self):
  self.assertTrue(all('wash' not in r['sample_state'].lower() and 'abrasion' not in r['sample_state'].lower() for r in self.rows));r=copy.deepcopy(self.by['Janus-DFS']);old=p.sample_state_id(r);r['washing_state']='five successive washes';self.assertNotEqual(old,p.sample_state_id(r))
 def test_14_LP_only_not_APP_cure(self):
  r=self.by['cotton-LP'];self.assertIn('Do not assign APP175C curing',r['treatment_method']);self.assertIn('不得',r['source_preparation_scope_note']);self.assertIn('17',r['source_weight_gain_pct'])
 def test_15_PDMS_only_Janus(self):
  self.assertIn('PDMS/hexane/curingagent10:30:1mass',self.by['Janus-DFS']['treatment_method']);self.assertIn('no PDMS spray/cure assigned',self.by['CS-PA@TiO2-DFS']['treatment_method'])
 def test_16_substrate_yarn_ratio_not_fabricwtpercent(self):
  r=self.by['Janus-DFS'];self.assertIn('2:1 yarnliftingratio',r['composition']);self.assertIn('actualdryfabric massfractionsunreported',r['composition'])
 def test_17_missing_Springer_rate_stays_unselected(self):
  self.assertFalse(any('03833' in r['DOI'] for r in self.rows));fact=next(f for f in self.man['processed_source_queue_facts']if '03833' in f['DOI']);self.assertEqual(fact['sourceapproved_new_pairs'],0);self.assertEqual(fact['counts']['wholeheld'],5)
 def test_18_correct_negative_source_locators(self):
  fact=next(f for f in self.man['processed_source_queue_facts']if '03833' in f['DOI']);text=';'.join(fact['source_locations']);self.assertIn('p11Thermal',text);self.assertIn('p14Table2',text);self.assertIn('p15Flammability',text);self.assertNotIn('p10Thermal',text)
 def test_19_all7_exact_review_bindings(self):
  self.assertTrue(all(p.measurement_fingerprint(r)==r['reviewed_measurement_fingerprint']for r in self.rows));self.assertEqual(len({p.sample_state_id(r)for r in self.rows}),7)
 def test_20_public_privacy_and_preparation_scope(self):
  text=json.dumps(self.man,ensure_ascii=False);self.assertFalse(any(x in text for x in ['/Volumes/','/Users/','smb://']));self.assertTrue(all(r['treatment_method'] and r['source_preparation_scope_note']for r in self.rows))
if __name__=='__main__':unittest.main(verbosity=2)
