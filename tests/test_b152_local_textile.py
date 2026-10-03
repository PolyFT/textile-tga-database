"""Protect native specimen states, metrics and explicitly unresolved evidence."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b152/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261004_b152_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing;import validate_tg_loi as v
A='10.1016/j.porgcoat.2019.105323';B='10.1039/d3nr06604e';C='10.1002/adfm.202425093';D='10.1016/j.porgcoat.2016.03.020'
class TextileB152Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def row(self,d,s):return next(r for r in self.rows if r['DOI']==d and r['sample_state']==s)
 def reject(self,r,**changes):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**changes)))
 def test_six_states_and_conditions_not28facts(self):
  p=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(p['errors']);self.assertEqual((p['verified_exact_sample_states'],p['verified_exact_condition_records']),(6,6));self.assertEqual(len(self.rows),28)
 def test_twenty_two_held_facts_remain_excluded(self):
  x=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(x),22);self.assertTrue(all(pairing.evidence_issues(r)for r in x))
 def test_four_own_coated_pet_profiles(self):
  x=[r for r in self.rows if r['DOI']==A and r['pairing_status']=='verified_exact'];self.assertEqual([(r['T5_C'],r['Tmax1_C'],r['Tmax2_C'],r['R600_pct'],r['LOI_pct'])for r in x],[('265.5','290.2','427','8.9','21.4'),('263.1','287.5','390.6','12.1','24.3'),('238.6','281.7','385.2','13.8','26.2'),('178.2','244.3','381.3','16.6','27.5')]);self.reject(x[3],LOI_pct='26.8')
 def test_native_t5_is_not_undefined_onset(self):
  r=self.row(A,'S3-F initial coated PET fabric');self.assertFalse(r.get('Tonset_C'));self.reject(r,T5_C='',Tonset_C='178.2')
 def test_native_second_peak_not_renumbered_first(self):
  r=self.row(A,'S1-F initial coated PET fabric');self.assertEqual((r['Tmax1_C'],r['Tmax2_C']),('287.5','390.6'));self.reject(r,Tmax1_C='390.6')
 def test_char_at_peak_temperatures_not_r600(self):
  r=self.row(A,'S0-F initial coated PET fabric');self.assertEqual((r['residue_at_Tmax1_pct'],r['residue_at_Tmax2_pct'],r['source_CTmax1_temperature_C'],r['source_CTmax2_temperature_C'],r['R600_pct']),('92.8','36.1','290.2','427','8.9'));self.reject(r,R600_pct='36.1');self.reject(r,residue_at_Tmax1_pct='8.9')
 def test_wet_feed_including_water_not_final_coating_fraction(self):
  r=self.row(A,'S2-F initial coated PET fabric');self.assertEqual((r['source_FRC6_wetfeed_wt_pct'],r['source_water_wetfeed_wt_pct']),('6.05','64.54'));self.assertIn('wetoriginalcomponentfeedwt%includingwater',r['source_recipe_basis']);self.assertIn('notfinaldrycoatingorfabricfractions',r['source_recipe_basis'])
 def test_own_pet_matrix_and_cure_are_retained(self):
  r=self.row(A,'S3-F initial coated PET fabric');self.assertIn('106g/m2',r['material_form']);self.assertIn('about40gsmaddon',r['treatment_method']);self.assertIn('120C30scure',r['treatment_method']);self.assertIn('RTdesiccator24h',r['treatment_method'])
 def test_loi_repeats_and_dimensions_not_vbt_dimensions(self):
  r=self.row(A,'S0-F initial coated PET fabric');self.assertEqual((r['source_LOI_repeats'],r['source_LOI_dimensions_mm'],r['LOI_standard']),('5','150x58','GB/T5454-1997'));self.assertIn('mechanical-test20C65%RHnotassigned',r['source_LOI_temperature'])
 def test_tg_native_instrument_unknown_auxiliary_details(self):
  r=self.row(A,'S0-F initial coated PET fabric');self.assertIn('NativeDiamond5700',r['TGA_instrument']);self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['TG_start_C'],r['TG_end_C'],r['source_TG_mass_pan_flow_repeats']),('N2','10','30','600','Unreported'));self.reject(r,heating_rate_C_min='20')
 def test_pristine_pet_not_assigned_no_fr_coating_tg(self):
  r=self.row(A,'Pristine PET initial uncoated fabric');self.assertEqual(r['LOI_pct'],'20.1');self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS));self.assertIn('held_',r['pairing_status'])
 def test_washed_pet_has_no_tg_and_equivalence_not_lab_cycle_count(self):
  r=self.row(A,'S3-Fprime washed coated PET fabric');self.assertEqual(r['LOI_pct'],'26.8');self.assertIn('not5labcycles',r['washing_state']);self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS))
 def test_two_rsc_native_profiles_and_loi(self):
  x=[r for r in self.rows if r['DOI']==B and r['pairing_status']=='verified_exact'];self.assertEqual([(r['T5_C'],r['Tmax1_C'],r['R700_pct'],r['LOI_pct'])for r in x],[('368.11','430.11','8.43','32'),('317.97','371.69','19.41','26')]);self.reject(x[1],LOI_pct='32')
 def test_rsc_matrix_is_coplymerized_frpet_not_plain_pet(self):
  r=self.row(B,'FRPET initial flame-retardant PET fabric');self.assertIn('CEPPA-copolymerized',r['material_form']);self.assertIn('160g/m2',r['material_form']);self.assertIn('ref38unread',r['treatment_method'])
 def test_rsc_uncoated_control_not_given_app_or_mxene_recipe(self):
  r=self.row(B,'FRPET initial flame-retardant PET fabric');self.assertEqual(r['source_APP_bath'],'NotapplicabletouncoatedFRPET');self.assertIn('Notapplicable',r['source_A5M1_assembly']);self.assertIn('uncoated',r['treatment_state'])
 def test_rsc_a5m1_coating_not_am3_or_pm3(self):
  r=self.row(B,'FPP@A5-M1 initial hybrid-coated FRPET fabric');self.assertIn('5APP-PEIbilayers',r['composition']);self.assertIn('oneexterior',r['source_A5M1_assembly']);self.assertIn('drytemperatureunreported',r['source_A5M1_assembly']);self.reject(r,sample_state='FPP@AM-3 initial hybrid-coated FRPET fabric')
 def test_rsc_tg_mass_flow_and_program_explicit(self):
  r=self.row(B,'FPP@A5-M1 initial hybrid-coated FRPET fabric');self.assertEqual((r['source_TG_mass_mg'],r['source_TG_flow_mL_min'],r['source_TG_pan'],r['TG_start_C'],r['TG_end_C'],r['heating_rate_C_min']),('5-10','10','Unreported','25','700','10'));self.reject(r,atmosphere='air')
 def test_rsc_loi_standard_as_reported_four_layers_only_cone(self):
  r=self.row(B,'FRPET initial flame-retardant PET fabric');self.assertEqual(r['LOI_standard'],'GB/T5455-1997(asreported;notcorrected)');self.assertIn('coneFOURlayers35kWm2notLOIplies',r['source_LOI_form']);self.assertEqual(r['source_LOI_dimensions_mm'],'150x58')
 def test_three_rsc_tg_only_groups_not_assigned_other_loi(self):
  x=[r for r in self.rows if r['DOI']==B and r['pairing_status']!='verified_exact'];self.assertEqual(len(x),3);self.assertTrue(all(not r.get('LOI_pct')for r in x));self.assertEqual([r['R700_pct']for r in x],['6.99','14.29','10.07'])
 def test_afm_three_lois_and_uncertainties_not_approved(self):
  x=[r for r in self.rows if r['DOI']==C and r.get('LOI_pct')];self.assertEqual([(r['LOI_pct'],r['LOI_uncertainty_pct'])for r in x],[('19.5','0.3'),('20.3','0.2'),('28.1','0.4')]);self.assertTrue(all(not r.get('heating_rate_C_min')for r in x));self.assertTrue(all('Unreportedinmain' in r['source_TG_rate_program_mass_pan_flow']for r in x))
 def test_afm_residues_have_native_temperatures_not_tmax_or_r800(self):
  a=self.row(C,'CF initial cotton fabric');b=self.row(C,'CF-PIL-4 initial ionic-liquid grafted cotton fabric');self.assertEqual((a['residue_pct'],a['residue_temp_C'],b['residue_pct'],b['residue_temp_C']),('13','351','47.8','308'));self.assertTrue(all(not r.get(k)for r in [a,b]for k in ['T5_C','Tmax1_C','Tonset_C','R800_pct']))
 def test_afm_washed_retention_not_calculated_absolute_loi(self):
  r=self.row(C,'CF-PIL-4 after50washes retention only');self.assertIn('94.0%',r['source_raw_LOI_retention']);self.assertFalse(r.get('LOI_pct'));self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS));self.assertIn('no26.414calculated',r['source_raw_LOI_retention'])
 def test_seven_fabric_lois_not_six_bulk_film_tg(self):
  fabrics=[r for r in self.rows if r['DOI']==D and'bulk OWPU'not in r['sample_state']];films=[r for r in self.rows if r['DOI']==D and'bulk OWPU'in r['sample_state']];self.assertEqual((len(fabrics),len(films)),(7,6));self.assertEqual([r['LOI_pct']for r in fabrics],['14.6','15.6','18.2','20.8','21.6','21','21.2']);self.assertTrue(all(all(not r.get(k)for k in pairing.TG_FIELDS)for r in fabrics));self.assertTrue(all(r['pairing_status']=='held_bulk_polymer_film_not_textile'for r in films))
 def test_native_film_indices_and_nitrogen_not_argon_tgftir(self):
  r=self.row(D,'S0 bulk OWPU film outside textile scope');self.assertFalse(r.get('Tmax1_C'));self.assertEqual((r['Tmax2_C'],r['Tmax3_C'],r['R500_pct']),('284.3','411.2','1.2'));self.assertIn('separateTGFTIRMSargon40mLminnotaliased',r['source_gas_scope']);self.assertEqual((r['TG_end_C'],r['atmosphere']),('600','N2'))
 def test_forged_film_approval_is_rejected_by_textile_scope(self):
  r=dict(self.row(D,'S3 bulk OWPU film outside textile scope'),pairing_status='verified_exact');r['reviewed_measurement_fingerprint']=pairing.measurement_fingerprint(r);self.assertIn('reviewed_specimen_not_textile',pairing.evidence_issues(r))
 def test_fabric_loi_and_film_tg_form_mismatch_is_rejected(self):
  r=dict(self.row(A,'S0-F initial coated PET fabric'),material_form_TGA='Bulk polyurethane film');self.assertIn('specimen_form_mismatch',pairing.evidence_issues(r))
 def test_all_accepted_facts_have_native_source_locators(self):
  for r in self.rows:
   if r['pairing_status']=='verified_exact':self.assertIn('Own',r['TG_locator']);self.assertIn('Own',r['LOI_locator']);self.assertTrue(r['source_location']);self.assertFalse(pairing.evidence_issues(r))
if __name__=='__main__':unittest.main()
