"""Original-source boundaries: paired states, residues, gas conditions and curve-only holds."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));import pairing as p;import validate_tg_loi as v
with(R/'data/incoming/verified_source_batch_20261005_b313_local_material.csv').open(newline='')as f:PA_ARAMID_ROWS=[r for r in csv.DictReader(f)if r['DOI']in ['10.1002/pc.23505','10.1021/acsami.3c16614']]
class MaterialScientificBoundaries(unittest.TestCase):
 def test_six_states_eleven_conditions_with_seven_held_fact_rows(self):
  master,_,_,r=v.build_tables(pd.DataFrame(PA_ARAMID_ROWS));self.assertFalse(r['errors']);self.assertEqual((r['verified_exact_sample_states'],len(master)),(6,11));self.assertEqual(len([x for x in PA_ARAMID_ROWS if x['direct_numeric_use']=='no']),7)
  for name,loi in [('GFPA','23.5'),('GFPA/CeHP5','24.5'),('GFPA/CeHP10','25'),('GFPA/CeHP15','25.5'),('GFPA/CeHP20','26.5')]:
   own=[x for x in PA_ARAMID_ROWS if x['source_sample_label']==name];self.assertEqual(len(own),2);self.assertEqual({x['atmosphere']for x in own},{'N2','air'});self.assertEqual({x['LOI_pct']for x in own},{loi});self.assertEqual({p.sample_state_id(x)for x in own},{p.sample_state_id(own[0])})
 def test_residue_temperature_conflict_remains_held_not_guessed(self):
  for x in [x for x in PA_ARAMID_ROWS if x['DOI']=='10.1002/pc.23505'and x['pairing_status']=='verified_exact']:
   if x['atmosphere']=='N2':self.assertFalse(x['residue_pct']);self.assertFalse(x['residue_temp_C']);self.assertFalse(x['R750_pct']);self.assertIn('conflict',x['source_held_metric']);self.assertEqual(x['source_raw_TG_residue_table_temperature_C'],'750');self.assertEqual(x['source_raw_N2_residue_body_temperature_C'],'800')
   else:self.assertEqual(x['residue_temp_C'],'750');self.assertEqual(x['R750_pct'],x['source_raw_TG_residue_pct']);self.assertFalse(x['R800_pct'])
   self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(dict(x,R800_pct=x['source_raw_TG_residue_pct'])))
 def test_threshold_and_missing_DTG_slots_do_not_shift(self):
  n=next(x for x in PA_ARAMID_ROWS if x['source_sample_label']=='GFPA'and x['atmosphere']=='N2');a=next(x for x in PA_ARAMID_ROWS if x['source_sample_label']=='GFPA'and x['atmosphere']=='air');self.assertEqual((n['T5_C'],n['Tmax1_C'],n['Tmax2_C']),('401','471',''));self.assertEqual((a['T5_C'],a['Tmax1_C'],a['Tmax2_C'],a['Tmax3_C']),('392','467','553',''));self.assertFalse(n['T10_C']);self.assertFalse(n['Tonset_C']);self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(dict(n,T5_C='',Tonset_C='401')))
 def test_whole_composite_forms_and_MCC_conditions_are_not_borrowed(self):
  for x in [x for x in PA_ARAMID_ROWS if x['DOI']=='10.1002/pc.23505'and x['pairing_status']=='verified_exact']:
   self.assertEqual(x['material_form_TGA'],x['material_form_LOI']);self.assertEqual(x['heating_rate_C_min'],'20');self.assertEqual(x['LOI_specimen_geometry'],'100x6.5x3.0mm3');self.assertTrue(all(not x[k]for k in ['TG_start_C','TG_end_C','TGA_mass_mg','TGA_gas_flow_ml_min','TGA_replicates','LOI_replicates']));self.assertIn('specimen_form_mismatch',p.evidence_issues(dict(x,material_form_LOI='wovenPA6fabric')))
 def test_aramid_explicit_text_control_and_curve_only_composites(self):
  x=next(x for x in PA_ARAMID_ROWS if x['source_sample_label']=='ANFs_paper');self.assertEqual((x['LOI_pct'],x['R800_pct'],x['residue_temp_C'],x['numeric_evidence_type']),('28.55','40.22','800','explicit_text'));self.assertTrue(all(not x[k]for k in ['T5_C','T10_C','Tonset_C','Tmax1_C']));self.assertFalse(p.evidence_issues(x))
  held=[x for x in PA_ARAMID_ROWS if x['pairing_status']=='TG_curve_only_held'];self.assertEqual(len(held),4);self.assertTrue(all(p.evidence_issues(x)for x in held));self.assertTrue(all(not x['R800_pct']for x in held))
  bf=next(x for x in PA_ARAMID_ROWS if x['source_sample_label']=='BF_pure');self.assertEqual(bf['source_raw_mass_loss_at800_pct'],'0.46');self.assertFalse(bf['R800_pct']);self.assertFalse(bf['LOI_pct']);self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(dict(x,washing_state='post300C60min')))


"""Source-specific EPDM/PP scientific boundaries and deliberate invalid mutations."""
import csv, sys, unittest
from pathlib import Path
import pandas as pd
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import pairing as p
import validate_tg_loi as v
with (R/'data/incoming/verified_source_batch_20261005_b313_local_material.csv').open(newline='') as f:EPDM_PP_ROWS=[r for r in csv.DictReader(f)if r['DOI']=='10.1002/app.50116']
class EPDMPolypropyleneBoundaries(unittest.TestCase):
 def test_nine_pairs_one_conflicted_control(self):
  master,_,_,report=v.build_tables(pd.DataFrame(EPDM_PP_ROWS));self.assertFalse(report['errors']);self.assertEqual((report['verified_exact_sample_states'],len(master)),(9,9));self.assertEqual(len([r for r in EPDM_PP_ROWS if r['direct_numeric_use']=='no']),1)
  control=next(r for r in EPDM_PP_ROWS if r['source_sample_label']=='TPE0');self.assertEqual((control['source_raw_LOI_Table1'],control['source_raw_LOI_body']),('25.7','25.5'));self.assertTrue(p.evidence_issues(dict(control,pairing_status='verified_exact',direct_numeric_use='yes',LOI_pct='25.6')))
 def test_residue600_cannot_shift_to_program_endpoint700(self):
  row=next(r for r in EPDM_PP_ROWS if r['source_sample_label']=='EG9');self.assertEqual((row['R600_pct'],row['residue_pct'],row['residue_temp_C'],row['TG_end_C']),('17.2','17.2','600','700'));self.assertFalse(row['R700_pct']);self.assertFalse(row['R800_pct']);self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(dict(row,R600_pct='',R700_pct='17.2',residue_temp_C='700')))
 def test_own_LOI_replicates_and_geometry_not_UL94(self):
  for row in EPDM_PP_ROWS:
   self.assertEqual((row['LOI_replicates'],row['LOI_specimen_geometry']),('5','120x6.5x3.2mm3'));self.assertFalse(row['TGA_replicates']);self.assertEqual(row['source_raw_TG_mass'],'around10mg');self.assertFalse(row['TGA_mass_mg']);self.assertFalse(row['TG_start_C']);self.assertEqual((row['atmosphere'],row['heating_rate_C_min']),('N2','10'))
 def test_T5_is_not_generic_onset_or_DMA_peak(self):
  row=next(r for r in EPDM_PP_ROWS if r['source_sample_label']=='ZB3');self.assertEqual((row['T5_C'],row['Tmax1_C']),('416.4','495.2'));self.assertFalse(row['Tonset_C']);self.assertFalse(row['T10_C']);self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(dict(row,T5_C='',Tonset_C='416.4')))
 def test_actual_whole_bulk_form_and_recipe_binding(self):
  row=next(r for r in EPDM_PP_ROWS if r['source_sample_label']=='OMMT6');self.assertEqual(row['material_form_TGA'],row['material_form_LOI']);self.assertIn('injection-moulded',row['material_form']);self.assertIn('literal',row['source_metric_limits'].lower());self.assertIn('specimen_form_mismatch',p.evidence_issues(dict(row,material_form_LOI='woven PP fabric')));self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(dict(row,washing_state='after_50washes')))
if __name__=='__main__':unittest.main()
