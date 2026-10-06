"""Source-specific pending-candidate checks. No root approval or numeric inference."""
import copy,csv,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
INCOMING=ROOT/'data/incoming/verified_source_batch_20261006_b454_local_material.csv'
MANIFEST=ROOT/'data/curation/archive/20261006/source_review_manifest_b454.json'
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'scripts'))
import pairing as p
import reader_table as reader

def source_corresponds(row,rows):
 found=[x for x in rows if (x['DOI'],x['sample_state'],x['heating_rate_C_min'])==(row.get('DOI'),row.get('sample_state'),row.get('heating_rate_C_min'))]
 if len(found)!=1:return False
 expected=found[0]
 return all(row.get(k,'')==v for k,v in expected.items()) and not p.evidence_issues(row)
class SourceGuards(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.rows=list(csv.DictReader(INCOMING.open(newline='')));cls.manifest=json.loads(MANIFEST.read_text())
 def select(self,suffix,**values):return next(r for r in self.rows if r['DOI'].endswith(suffix)and all(r.get(k)==v for k,v in values.items()))
 def reject(self,r,**changes):
  q=copy.deepcopy(r);q.update(changes);q['reviewed_measurement_fingerprint']=p.measurement_fingerprint(q);q['reviewed_material_scope_fingerprint']=p.material_scope_fingerprint(q);self.assertFalse(source_corresponds(q,self.rows))
 def test_real_default_incoming_and_archive_paths(self):
  self.assertTrue(INCOMING.is_file());self.assertTrue(MANIFEST.is_file());self.assertEqual(self.manifest['public_incoming'],str(INCOMING.relative_to(ROOT)));self.assertEqual(self.manifest['public_archive_manifest'],str(MANIFEST.relative_to(ROOT)))
 def test_all44_exact_approved_conditions(self):
  self.assertEqual(len(self.rows),44)
  for r in self.rows:self.assertTrue(source_corresponds(r,self.rows))
 def test_states_not_condition_count(self):
  self.assertEqual(len({p.sample_state_id(r)for r in self.rows}),32);self.assertEqual(len({r['DOI']for r in self.rows}),6)
 def test_root_sourceapproval_not_publication(self):
  self.assertEqual(self.manifest['rootapproved'],32);self.assertEqual(self.manifest['sourceapproved'],32);self.assertEqual(self.manifest['published'],0);self.assertEqual(self.manifest['root_source_approval']['approved_TG_conditions'],44)
 def test_PP_undefined_start_raw_not_threshold(self):
  r=self.select('2005.05.023',source_raw_starting_degradation_temperature_C='259');self.assertFalse(r['T5_C']);self.assertFalse(r['Tonset_C']);self.reject(r,T5_C='259');self.reject(r,Tonset_C='259');self.assertIn('criterionunreported',r['source_raw_starting_degradation_definition'])
 def test_PP_raw_start_visible_only_notes(self):
  r=self.select('2005.05.023',source_raw_starting_degradation_temperature_C='259');d=reader.reading_row(r,{'scope_class':r['material_scope_class']});self.assertIn('source_raw_starting_degradation_temperature_C=259',d[20]);self.assertEqual(d[6],'')
 def test_PP_source_error_about_not_sd(self):
  for r in self.rows:
   if r['DOI'].endswith('2005.05.023'):self.assertEqual(r['source_LOI_technique_error_pct'],'about0.5');self.assertIn('G0.5',r['source_LOI_error_definition']);self.assertFalse(r['LOI_replicates']);self.assertFalse(r['LOI_uncertainty_pct'])
 def test_PBT2percent_not_T5_or_T10(self):
  for r in self.rows:
   if r['DOI'].endswith('2009.04.014'):
    self.assertFalse(r['T5_C']);self.assertFalse(r['T10_C']);self.assertFalse(r['Tonset_C']);self.reject(r,T5_C=r['source_raw_T2pct_C'])
 def test_PBT_K_conversion_not1000C(self):
  for r in self.rows:
   if r['DOI'].endswith('2009.04.014'):
    self.assertEqual(r['source_residue_temperature_K'],'1000');self.assertEqual(r['residue_temp_C'],'726.85');self.reject(r,residue_temp_C='1000')
 def test_PBT_uncertainty_magnitude_and_sign_preserved(self):
  for r in self.rows:
   if r['DOI'].endswith('2009.04.014'):
    self.assertEqual(r['LOI_uncertainty_pct'],'1');self.assertEqual(r['source_LOI_error_raw'],'/C6 1');self.assertEqual(r['source_LOI_error_sign_status'],'native_glyph_unresolved');self.assertIn('source error magnitude',r['LOI_uncertainty_type']);self.assertEqual(r['source_mass_error_wt_pct'],'1');self.assertEqual(r['source_temperature_error_K'],'2');self.assertIn('/C6 2K',r['source_TG_error_raw']);d=reader.reading_row(r,{'scope_class':r['material_scope_class']});self.assertNotIn('±',d[20]+d[21])
 def test_aging_recipe_state_not_age_cross_pair(self):
  r=self.select('24253',source_aging_time_days='0');self.reject(r,LOI_pct='23.5');self.reject(r,source_aging_time_days='20')
 def test_four_rates_four_DBDPE_states(self):
  rows=[r for r in self.rows if r['DOI'].endswith('24720')];self.assertEqual(len(rows),16);self.assertEqual(len({p.sample_state_id(r)for r in rows}),4);self.assertEqual({r['heating_rate_C_min']for r in rows},{'10','20','30','40'})
 def test_20_40day_no_DBDPE_selected_TG(self):self.assertEqual({r['source_aging_time_days']for r in self.rows if r['DOI'].endswith('24720')},{'0','10','30','50'})
 def test_ten_day_conflict_only_residue_held(self):
  r=self.select('24720',source_aging_time_days='10',heating_rate_C_min='10');self.assertEqual((r['source_raw_residue_table_pct'],r['source_raw_residue_prose_pct']),('22.4','24.4'));self.assertEqual((r['residue_pct'],r['residue_temp_C'],r['R650_pct']),('','',''));self.assertTrue(r['T5_C']);self.assertTrue(r['Tmax1_C']);self.assertTrue(r['Tmax2_C']);self.reject(r,residue_pct='22.4',residue_temp_C='650');self.reject(r,residue_pct='24.4',residue_temp_C='650')
 def test_other_rates_cannot_borrow10rate_threshold_residue(self):
  for r in self.rows:
   if r['DOI'].endswith('24720')and r['heating_rate_C_min']!='10':self.assertEqual((r['T5_C'],r['residue_pct']),('',''));self.reject(r,T5_C='357.1')
 def test_R650_not700_program_end(self):
  r=self.select('24720',source_aging_time_days='0',heating_rate_C_min='10');self.assertEqual(r['residue_temp_C'],'650');self.assertEqual(r['TG_end_C'],'700');self.reject(r,residue_temp_C='700')
 def test_inorganic_residue_not_pure_carbon(self):
  for r in self.rows:
   if r['DOI'].endswith('24253')or r['DOI'].endswith('24720'):self.assertIn('notpure',r['source_residue_definition']);self.assertIn('LGF',r['composition'])
 def test_massloss_stage_not_residue_or_peak(self):
  r=self.select('24253',source_aging_time_days='0');self.assertEqual(r['source_raw_stage_mass_loss_pct'],'69');self.assertEqual(r['source_raw_degradation_stage_end_C'],'529.0');self.reject(r,residue_pct='31',residue_temp_C='529');self.reject(r,Tmax2_C='529')
 def test_DBDPE_first_peak_not_PP_or_massloss_rate(self):
  r=self.select('24720',source_aging_time_days='0',heating_rate_C_min='10');self.assertIn('DBDPE',r['Tmax1_assignment']);self.assertIn('PP',r['Tmax2_assignment']);self.reject(r,Tmax1_C=r['source_raw_Tp1_mass_loss_rate_pct_min']);self.reject(r,Tmax1_C='165.0')
 def test_preinjection_or_fibre_form_not_borrowed(self):
  r=self.select('24253',source_aging_time_days='0');self.reject(r,material_form_TGA='preinjectionpellets');self.reject(r,material_form_LOI='glassfibre')
 def test_unknown_raw_temperature_field_not_generalized(self):
  r=self.select('2005.05.023',source_raw_starting_degradation_temperature_C='259');q=dict(r,source_raw_starting_degradation_C='999',source_raw_T3pct_K='998');notes=reader.reading_row(q,{'scope_class':q['material_scope_class']})[20];self.assertNotIn('999',notes);self.assertNotIn('998',notes)
 def test_wood_zero_source_not_selected_and_sign_unknown(self):
  self.assertNotIn('10.1039/c5ra08292g',{r['DOI']for r in self.rows});fact=next(x for x in self.manifest['processed_source_queue_facts']if x['DOI']=='10.1039/c5ra08292g');self.assertEqual(fact['candidate_unique_states'],0);self.assertIn('unresolved',fact['raw_rate_sign_status'])
 def test_sisal_own_tables_not_reference_donor(self):
  rs=[r for r in self.rows if r['DOI'].endswith('2013.08.012')];self.assertEqual(len(rs),6)
  for r in rs:self.assertIn('ownTables2/3',r['pairing_evidence']);self.assertIn('Table3 PDFp12',r['TG_locator'])
 def test_sisal_T5_T50_definition_not_Tonset_or_DTg(self):
  r=self.select('2013.08.012',sample_state='PP');self.assertEqual((r['T5_C'],r['T50_C']),('408','458'));self.assertFalse(r['Tonset_C']);self.assertFalse(r['Tmax1_C']);self.assertIn('5%weightloss',r['source_T5_definition']);self.assertIn('50%weightloss',r['source_T50_definition']);self.reject(r,Tonset_C='408');self.reject(r,Tmax1_C='458')
 def test_sisal_zero_R600_not700_program_end(self):
  r=self.select('2013.08.012',sample_state='PP');self.assertEqual((r['R600_pct'],r['residue_pct'],r['residue_temp_C']),('0','0','600'));self.assertEqual(r['TG_end_C'],'700');self.reject(r,residue_temp_C='700')
 def test_purePP_preparation_does_not_take_sisal_branch(self):
  r=self.select('2013.08.012',sample_state='PP');self.assertIn('purePP hasno sisalfibre',r['source_preparation']);self.assertIn('otherbranch background',r['source_preparation']);self.reject(r,source_preparation=r['source_preparation']+' purePP sisaldried60Covernight')
 def test_sisal_phr_is_not_normalized_wtpercent(self):
  r=self.select('2013.08.012',sample_state='PP/30sisal/40Mg');self.assertIn('phr relativePP100',r['composition']);self.reject(r,composition='PP58.82/sisal17.65/Mg23.53wt%')
 def test_source_LOI_less19_unselected_not_replaced19(self):
  self.assertNotIn('PP/30sisal',{r['sample_state']for r in self.rows if r['DOI'].endswith('2013.08.012')});r=self.select('2013.08.012',sample_state='PP');self.reject(r,sample_state='PP/30sisal',LOI_pct='19')
 def test_administrative_rootapproved_only_original22rows(self):
  selected=[r for r in self.rows if r.get('rootapproved')];self.assertEqual(len(selected),22);self.assertEqual({r['rootapproved']for r in selected},{'1'});self.assertEqual({r['DOI']for r in selected},{'10.1002/pc.24253','10.1002/pc.24720'})
 def test_existing_archive_subdirectory_no_rootarchive(self):
  self.assertEqual(str(MANIFEST.relative_to(ROOT)),'data/curation/archive/20261006/source_review_manifest_b454.json');self.assertFalse((ROOT/'archive').exists())
if __name__=='__main__':unittest.main()
