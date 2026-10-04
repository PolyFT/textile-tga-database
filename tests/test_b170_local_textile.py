"""Guard nylon atmosphere/program conflicts, ramie criteria and PCz source ambiguity."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b170/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261004_b170_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing;import validate_tg_loi as v
A='10.1007/s10570-024-06263-3';B='10.1007/s10570-024-06147-6';C='10.1007/s12221-023-00442-y'
class TextileB170Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def subset(self,d):return[r for r in self.rows if r['DOI']==d]
 def find(self,d,s,gas=None):return next(r for r in self.subset(d)if r['sample_state']==s and(gas is None or r['atmosphere']==gas))
 def accepted(self):return[r for r in self.rows if r['pairing_status']=='verified_exact']
 def noTG(self,r):self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS))
 def test_six_states_six_records_not26facts(self):
  p=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(p['errors']);self.assertEqual((p['verified_exact_sample_states'],p['verified_exact_condition_records']),(6,6));self.assertEqual(len(self.rows),26)
 def test_twenty_held_excluded(self):
  rr=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(rr),20);self.assertEqual([sum(r['DOI']==d for r in rr)for d in[A,B,C]],[7,4,9]);self.assertTrue(all(pairing.evidence_issues(r)for r in rr))
 def test_measurement_or_sample_state_changes_invalidate_review(self):
  for r in self.accepted():
   self.assertFalse(pairing.evidence_issues(r))
   for k,z in [('LOI_pct','99'),('Tmax1_C','555'),('residue_pct','77'),('residue_temp_C','500'),('heating_rate_C_min','20'),('atmosphere','air'),('washing_state','washed'),('sample_state','othercoating')]:self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**{k:z})))
 def test_fabric_not_fiber_or_bulk_polymer(self):
  for r in self.accepted():self.assertEqual(r['material_form_TGA'],r['material_form_LOI']);self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='fiber')))
 def test_ramie_three_native_T5_Tmax_R800_profiles(self):
  for sample,e in [('RF',('286.66','358.83','9.72','19.5')),('G2',('260.66','350.16','16.95','27.9')),('G3',('246.16','342.29','30.34','30.2'))]:r=self.find(B,'RAMIE_'+sample+'_initial');self.assertEqual(tuple(r[k]for k in['T5_C','Tmax1_C','R800_pct','LOI_pct']),e);self.assertEqual(r['pairing_status'],'verified_exact')
 def test_ramie_onset_word_with_five_percent_definition_not_Tonset(self):
  for r in self.subset(B):self.assertFalse(r.get('Tonset_C'))
  self.assertIn('OwnT5explicit5pctmassloss',self.find(B,'RAMIE_G3_initial')['source_metric_definition'])
 def test_ramie_ordinary_N2_program_and_raw_vendor(self):
  for r in self.subset(B):
   if r['atmosphere']:self.assertEqual(tuple(r[k]for k in['atmosphere','heating_rate_C_min','TG_start_C','TG_end_C','source_TGA_sample_mass_mg']),('N2','10','30','800','5-10'));self.assertIn('source labels Nicolet',r['TGA_instrument']);self.assertIn('notcorrectedtoothermanufacturer',r['source_TGA_vendor_limit'])
 def test_ramie_coating_labels_measured_WG_not_bilayer_counts(self):
  for sample,wg in [('G2','20.41'),('G3','31.57')]:r=self.find(B,'RAMIE_'+sample+'_initial');self.assertEqual(r['source_weight_gain_pct'],wg);self.assertIn('exactbilayercountunreported',r['source_coating_count_limit'])
 def test_ramie_recipe_wash_and_PSP_identity_not_guessed(self):
  r=self.find(B,'RAMIE_G3_initial');self.assertIn('PSPexpandedchemicalidentityunreportedinmethods',r['treatment_method']);self.assertIn('washwiththissolutionasreported(notassumedDI)',r['treatment_method'])
 def test_ramie_DTG_rate_not_converted_to_per_minute(self):
  r=self.find(B,'RAMIE_G3_initial');self.assertEqual(r['source_DTG_Rmax_pct_per_C'],'1.22');self.assertIn('nativepctperCnotpctpermin',r['source_metric_definition'])
 def test_ramie_conechar_not_TGchar(self):
  r=self.find(B,'RAMIE_G3_initial');self.assertEqual(r['R800_pct'],'30.34');self.assertIn('conechar3.04/23.38/28.75notTG',r['source_ancillary_burning_limit'])
 def test_ramie_G1_curve_caption_not_borrowed_G2_TG(self):
  r=self.find(B,'RAMIE_G1_initial');self.assertEqual((r['LOI_pct'],r['source_weight_gain_pct']),('24.2','9.38'));self.noTG(r)
 def test_ramie_three_washed_LOIs_no_initial_TG(self):
  for lc,loi,wg in [(1,'29.3','27.25'),(2,'28.6','24.31'),(6,'26.4','17.75')]:r=self.find(B,f'RAMIE_G3_after{lc}LC');self.assertEqual((r['LOI_pct'],r['source_weight_gain_pct']),(loi,wg));self.noTG(r)
 def test_nylon_three_own_N2_profiles(self):
  for sample,e in [('Untreated',('417.9','467.9','3.472','24')),('PA4',('326','377.7','27.09','38.5')),('TAPA4',('317.9','375','28.78','39'))]:r=self.find(C,'NYLON_'+sample+'_initial','N2');self.assertEqual(tuple(r[k]for k in['T10_C','Tmax1_C','R700_pct','LOI_pct']),e);self.assertEqual(r['pairing_status'],'verified_exact');self.assertFalse(r['Tmax2_C'])
 def test_nylon_Tminus10_not_T5_or_Tonset(self):
  for r in self.subset(C):self.assertFalse(r.get('T5_C'));self.assertFalse(r.get('Tonset_C'))
 def test_nylon_own_ordinary_program_and_gas_flow(self):
  for r in self.subset(C):
   if r['atmosphere']:self.assertEqual(tuple(r[k]for k in['TG_start_C','TG_end_C','heating_rate_C_min','source_TGA_gas_flow_ml_min']),('30','700','10','20'))
 def test_nylon_air_Tmax2_above_program_entire_records_held(self):
  for sample,tm in [('PA4','776'),('TAPA4','782')]:r=self.find(C,'NYLON_'+sample+'_initial','air');self.assertEqual(r['Tmax2_C'],tm);self.assertGreater(float(r['Tmax2_C']),float(r['TG_end_C']));self.assertEqual(r['pairing_status'],'held_air_Tmax2_above_reported_program_end');self.assertTrue(pairing.evidence_issues(r))
 def test_nylon_air_control_raw_bad_cell_not_corrected(self):
  r=self.find(C,'NYLON_Untreated_initial','air');self.assertEqual(r['source_raw_Tmax1'],'471,.9');self.assertFalse(r['Tmax1_C']);self.assertEqual(r['pairing_status'],'held_air_unparsed_native_Tmax1');self.assertEqual(r['R700_pct'],'2.77');self.assertTrue(pairing.evidence_issues(r))
 def test_nylon_N2_conditions_separate_from_held_air(self):
  self.assertEqual(len([r for r in self.subset(C)if r['pairing_status']=='verified_exact']),3);self.assertEqual({r['atmosphere']for r in self.subset(C)if r['pairing_status']=='verified_exact'},{'N2'})
 def test_nylon_Oxford_type_and_loading_not_inferred(self):
  r=self.find(C,'NYLON_TAPA4_initial','N2');self.assertIn('nylontype6/66/purityunreported',r['treatment_method']);self.assertEqual(r['source_weight_gain_pct'],'85.8');self.assertIn('60-70pickup',r['treatment_method'])
 def test_nylon_other_two_cycle_samples_no_four_cycle_TG(self):
  for s,loi in [('PA2','27.5'),('TAPA2','29')]:r=self.find(C,'NYLON_'+s+'_initial');self.assertEqual(r['LOI_pct'],loi);self.noTG(r)
 def test_nylon_four_washed_LOIs_not_initial_records(self):
  for s,loi in [('PA2','24.5'),('PA4','26.5'),('TAPA2','25.7'),('TAPA4','29')]:r=self.find(C,'NYLON_'+s+'_after4wash');self.assertEqual(r['LOI_pct'],loi);self.noTG(r);self.assertIn('reported4timesnotmultiplied',r['source_wash_details'])
 def test_nylon_CCT_PET_caption_not_TG_form_or_char(self):
  r=self.find(C,'NYLON_TAPA4_initial','N2');self.assertEqual(r['material_form'],'nylon fabric');self.assertEqual(r['R700_pct'],'28.78');self.assertIn('cone22.60notTG28.78',r['source_ancillary_CCT_caption'])
 def test_PCZ_all_seven_facts_held(self):
  self.assertEqual(len(self.subset(A)),7);self.assertTrue(all(r['pairing_status']!='verified_exact'for r in self.subset(A)))
 def test_PCZ_source_program_conflict_not_borrowed_DSC_program(self):
  r=self.find(A,'PCZ_P@PCz_initial');self.assertEqual((r['TG_end_C'],r['Tmax1_C']),('700','534'));self.assertIn('actualprogramunresolved',r['source_method_body_end_conflict']);self.assertIn('DSCroomtemp80020Cminisaseparatemethod',r['source_method_body_end_conflict'])
 def test_PCZ_DSC_peaks_onsets_and_weightloss_not_canonical_TG(self):
  for r in self.subset(A):self.assertFalse(r.get('Tonset_C'));self.assertFalse(r.get('T5_C'));self.assertFalse(r.get('residue_pct'));self.assertFalse(r.get('R800_pct'))
  self.assertIn('notinferredresidue9.8/46.31',self.find(A,'PCZ_Control_initial')['source_metric_definition'])
 def test_PCZ_reported_LOI_mean_not_replaced_or_three_formulations(self):
  r=self.find(A,'PCZ_P@PCz_initial');self.assertEqual(r['LOI_pct'],'40.4');self.assertEqual(r['source_LOI_replicate_values'],'[42.1, 40.2, 40.9]');self.assertIn('41.0667;meanmethodunreported,no correction',r['source_LOI_mean_limit'])
 def test_PCZ_addon_basis_not_corrected(self):
  self.assertIn('reported28.68notcorrected',self.find(A,'PCZ_P@PCz_initial')['source_addon_limit'])
 def test_PCZ_binder_and_washed_states_no_initial_TG(self):
  for name,loi in [('PCZ_P@PCz_binder_initial','39.8'),('PCZ_P@PCz_after10wash','29.2'),('PCZ_P@PCz_binder_after10wash','37.5')]:r=self.find(A,name);self.assertEqual(r['LOI_pct'],loi);self.noTG(r)
 def test_public_facts_no_private_paths_or_contacts(self):
  for r in self.rows:self.assertFalse(any(('/'+'Volumes'+'/')in str(x)or('/'+'Users'+'/')in str(x)or('smb'+':'+chr(47)*2)in str(x)or'@ictmumbai'in str(x)for x in r.values()))
if __name__=='__main__':unittest.main(verbosity=2)
