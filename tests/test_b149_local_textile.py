"""Protect scientific sample mapping, source-native thresholds and publication exclusions."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b149/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261004_b149_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing;import validate_tg_loi as v
A='10.1016/j.porgcoat.2020.105835';B='10.1016/j.porgcoat.2021.106296';C='10.1016/j.porgcoat.2017.07.022';D='10.1016/j.surfcoat.2006.05.002'
class TextileB149Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def row(self,d,s,gas=None):return next(r for r in self.rows if r['DOI']==d and r['sample_state']==s and(gas is None or r['atmosphere']==gas))
 def reject(self,r,**changes):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**changes)))
 def test_fourteen_states_twenty_conditions_not117facts(self):
  p=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(p['errors']);self.assertEqual((p['verified_exact_sample_states'],p['verified_exact_condition_records']),(14,20));self.assertEqual(len(self.rows),117)
 def test_97held_facts_excluded(self):
  x=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(x),97);self.assertTrue(all(pairing.evidence_issues(r)for r in x));self.assertTrue(all(r['review_disposition']=='held_outside_verified_target'for r in x))
 def test_pa66_exact_spi5_tu10_not_tu15(self):
  r=self.row(A,'PA66 SPI5 TU10 initial');self.assertEqual((r['source_SPI_bath_wt_pct'],r['source_thiourea_bath_wt_pct'],r['source_addon_pct'],r['LOI_pct']),('5','10','9.1','25.5'));self.reject(r,sample_state='PA66 TU15 initial TGonly');self.reject(r,T5_C='191')
 def test_tu15_tg_never_borrows_tu10_loi(self):
  r=self.row(A,'PA66 TU15 initial TGonly');self.assertEqual((r['source_thiourea_bath_wt_pct'],r['T5_C'],r['Tmax2_C']),('15','191','407'));self.assertFalse(r['LOI_pct']);self.assertNotEqual(r['pairing_status'],'verified_exact')
 def test_pa66_toneset_percent_fields_are_thresholds(self):
  r=self.row(A,'PA66 SPI5 TU10 initial');self.assertEqual((r['T5_C'],r['T50_C']),('244','415'));self.assertFalse(r['Tonset_C']);self.reject(r,T5_C='',Tonset_C='244');self.reject(r,T50_C='',T10_C='415')
 def test_first_tu_peak_below_t5_not_auto_corrected(self):
  r=self.row(A,'PA66 SPI5 TU10 initial');self.assertEqual((r['Tmax1_C'],r['T5_C'],r['Tmax2_C']),('206','244','413'));self.assertLess(float(r['Tmax1_C']),float(r['T5_C']));self.reject(r,Tmax1_C='246')
 def test_pa66_control_table_profile(self):
  r=self.row(A,'PA66 control initial');self.assertEqual((r['T5_C'],r['T50_C'],r['Tmax1_C'],r['R700_pct'],r['LOI_pct']),('354','393','403','2.8','20.5'));self.assertFalse(r['Tmax2_C']);self.assertIn('403literaturecitationcontext',r['limitations'])
 def test_neat_additive_tg_not_fabric(self):
  x=[r for r in self.rows if r['DOI']==A and r['pairing_status']=='held_neat_additive_not_fabric_pair'];self.assertEqual(len(x),2);self.assertTrue(all(not r['LOI_pct']for r in x));r=self.row(A,'PA66 SPI5 TU10 initial');self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='Neat SPI powder')))
 def test_spi_only5_not_spi15_photos_or_neat_tg(self):
  r=self.row(A,'PA66 SPI5 only LOI');self.assertEqual(r['LOI_pct'],'20.7');self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS));self.assertNotEqual(r['pairing_status'],'verified_exact')
 def test_pa66_si_unread_and_loi_uncertainty_not_replicates(self):
  r=self.row(A,'PA66 SPI5 TU10 initial');self.assertIn('unread',r['supplement_review_status']);self.assertIn('cone3repsnotborrowed',r['source_LOI_repeats']);self.assertIn('definitionunreported',r['source_LOI_uncertainty_definition']);self.assertEqual(r['source_LOI_dimensions'],'15x6cm2')
 def test_pet_gases_count_once_per_sample(self):
  x=[r for r in self.rows if r['DOI']==B and r['pairing_status']=='verified_exact'];self.assertEqual(len(x),8);self.assertEqual(len({r['sample_state']for r in x}),4);self.assertEqual({r['heating_rate_C_min']for r in x},{'20'})
 def test_pet_native_n2_profile_sequence(self):
  names=['PET pristine','PDMS-SiO2@PET','APP@PET','APP@SiO2-PDA@Ag PET'];x=[self.row(B,s+' initial','N2')for s in names];self.assertEqual([(r['T5_C'],r['Tmax1_C'],r['R700_pct'])for r in x],[('394','434','18.4'),('398','435','19.5'),('348','424','22.6'),('386','440','26.3')]);self.assertTrue(all(not r['Tmax2_C']for r in x))
 def test_pet_native_air_oxidation_second_peak(self):
  r=self.row(B,'APP@SiO2-PDA@Ag PET initial','air');self.assertEqual((r['T5_C'],r['Tmax1_C'],r['Tmax2_C'],r['R700_pct']),('365','435','576','11.2'));self.reject(r,Tmax2_C='440');self.reject(r,atmosphere='N2')
 def test_pet_pristine_loi_not_derived_from_abstract_delta(self):
  r=self.row(B,'PET pristine initial','N2');self.assertEqual(r['LOI_pct'],'19.4');self.assertIn('9.5',r['source_raw_abstract_delta']);self.assertIn('9.6',r['source_raw_abstract_delta']);self.reject(r,LOI_pct='19.5')
 def test_pet_four_washed_loi_have_no_tg(self):
  x=[r for r in self.rows if r['DOI']==B and r['pairing_status']=='held_washed_LOI_without_TG'];self.assertEqual([r['LOI_pct']for r in x],['19.3','23.1','21','28.4']);self.assertTrue(all(all(not r.get(k)for k in pairing.TG_FIELDS)for r in x));self.reject(self.row(B,'PET pristine initial','N2'),washing_state='After10nativeISOwashcycles')
 def test_pet_ag_free_and20wash_antibacterial_not_pairs(self):
  x=[r for r in self.rows if r['DOI']==B and r['pairing_status']=='held_antibacterial_only_unpaired'];self.assertEqual(len(x),2);self.assertTrue(all(not r['LOI_pct']and all(not r.get(k)for k in pairing.TG_FIELDS)for r in x))
 def test_pet_pan_mass_flow_and_partial_recipes_not_guessed(self):
  r=self.row(B,'APP@PET initial','N2');self.assertEqual(r['source_TG_pan'],'Alumina');self.assertEqual(r['source_TG_mass_flow'],'Unreported');self.assertIn('partialmodifierrecipesunreported',r['treatment_method']);self.assertIn('controlalkalipretreatmentunassigned',r['treatment_method'])
 def test_pet_residue_inorganic_not_pure_carbon(self):
  r=self.row(B,'PDMS-SiO2@PET initial','N2');self.assertEqual(r['residue_temp_C'],'700');self.assertIn('inorganicsSiO2',r['source_residue_definition']);self.assertFalse(r.get('char_pct'));self.reject(r,R700_pct='',R800_pct='19.5',residue_temp_C='800')
 def test_pan_reused_control_both_gases_held(self):
  x=[r for r in self.rows if r['DOI']==C and r['sample_state']=='PAN control initial'];self.assertEqual(len(x),2);self.assertTrue(all(r['pairing_status']=='held_crosssource_control_independence_unproven'for r in x));self.assertEqual(self.row(C,'PAN control initial','N2')['R800_pct'],'43.53');self.assertTrue(all('APS2017.09.155' in r['limitations']for r in x))
 def test_pan_sipn_loi_conflict_not_majority_voted(self):
  x=[r for r in self.rows if r['DOI']==C and r['sample_state']=='Si-P-N-PAN initial'];self.assertEqual(len(x),2);self.assertTrue(all(not r['LOI_pct']for r in x));self.assertTrue(all('42.1' in r['source_raw_LOI']and'34.1' in r['source_raw_LOI']for r in x));self.assertTrue(all(r['pairing_status']=='held_conflicting_initial_LOI'for r in x))
 def test_pan_n2_global_peak_not_chronological_index(self):
  r=self.row(C,'Si-P-PAN initial','N2');self.assertEqual((r['source_native_global_Tmax_C'],r['source_raw_intermediate_peak_C']),('413','324'));self.assertFalse(r['Tmax1_C']or r['Tmax2_C']);self.reject(r,Tmax1_C='413')
 def test_pan_air_native_second_index_is_oxidation(self):
  r=self.row(C,'Si-P-PAN initial','air');self.assertEqual((r['Tmax1_C'],r['Tmax2_C']),('152','652'));self.assertFalse(r.get('Tmax3_C'));self.assertIn('notrelabelledthird',r['source_peak_definition']);self.reject(r,Tmax2_C='',Tmax3_C='652')
 def test_pan_low_t5_not_tg_tonset_or_dsc_onset(self):
  r=self.row(C,'Si-P-PAN initial','N2');self.assertEqual(r['T5_C'],'125');self.assertFalse(r['Tonset_C']);self.assertIn('water/ethanol',r['source_T5_definition']);self.reject(r,T5_C='',Tonset_C='125');self.reject(r,Tonset_C='279')
 def test_pan_twelve_washed_states_not_commercial_equivalents(self):
  x=[r for r in self.rows if r['DOI']==C and r['pairing_status']=='held_washed_LOI_without_TG'];self.assertEqual(len(x),12);self.assertTrue(all(all(not r.get(k)for k in pairing.TG_FIELDS)for r in x));self.assertTrue(all('notextrasamples' in r['washing_state']for r in x))
 def test_pan123_8_addon_is_weightgain(self):
  r=self.row(C,'Si-P-N-PAN initial','N2');self.assertEqual(r['source_addon_pct'],'123.8');self.assertIn('notcomponentfraction',r['source_addon_definition']);self.assertIn('basisunclear',r['source_PA_basis'])
 def test_cotton_six_selected_table3_graftings(self):
  x=[r for r in self.rows if r['DOI']==D and r['pairing_status']=='verified_exact'];self.assertEqual([(r['LOI_pct'],r['Tonset_C'])for r in x],[('19','320'),('26','240'),('23','250'),('26','245'),('27.5','232'),('29.5','223')]);self.assertEqual({r['atmosphere']for r in x},{'Ar'});self.assertEqual({r['heating_rate_C_min']for r in x},{'10'})
 def test_cotton_1060_residue_never_changed_to650(self):
  x=[r for r in self.rows if r['DOI']==D and r['pairing_status']=='verified_exact'];self.assertTrue(all(r['TG_end_C']=='650'and r['source_raw_char_temp_C']=='1060'for r in x));self.assertTrue(all(not r.get('residue_pct')and not r.get('R650_pct')and not r.get('residue_temp_C')for r in x));self.reject(x[1],R650_pct='16.3',residue_temp_C='650');self.assertEqual(sum(r['pairing_status']=='held_residue_temperature_method_conflict'for r in self.rows),6)
 def test_cotton_onsets_not_t5_thresholds(self):
  r=self.row(D,'DEAEPN cotton120 initial Table3');self.assertEqual((r['source_monomer_bath_g_L'],r['source_EGDA_wt_pct'],r['source_grafting_pct'],r['Tonset_C']),('200','10','32.4','232'));self.assertFalse(r.get('T5_C')or r.get('T10_C'));self.reject(r,Tonset_C='',T5_C='232')
 def test_cotton_different_initial_graft_loading_held(self):
  x=[r for r in self.rows if r['DOI']==D and r['pairing_status']=='held_initial_graftloading_unmapped_TG'];self.assertEqual(len(x),6);self.assertTrue(all(all(not r.get(k)for k in pairing.TG_FIELDS)for r in x));r=self.row(D,'DEAEP cotton120 initial Table3');self.assertEqual(r['source_grafting_pct'],'28.6');self.assertEqual(self.row(D,'DEAEP cotton120 Table4 initial G30.6')['source_grafting_pct'],'30.6')
 def test_cotton_washed_and210gsm_unpaired(self):
  a=[r for r in self.rows if r['DOI']==D and r['pairing_status']=='held_washed_LOI_without_TG'];b=[r for r in self.rows if r['DOI']==D and r['pairing_status']=='held_cotton210_without_own_TG'];self.assertEqual((len(a),len(b)),(8,6));self.assertTrue(all(all(not r.get(k)for k in pairing.TG_FIELDS)for r in a+b));self.reject(self.row(D,'DEAEP cotton120 initial Table3'),washing_state='AfterMcSherryboil4h')
 def test_cotton_historic_pan_and_neat_films_not_new_pairs(self):
  a=[r for r in self.rows if r['DOI']==D and r['pairing_status']=='held_historic_comparator_not_new_pair'];b=[r for r in self.rows if r['DOI']==D and r['pairing_status']=='held_neat_polymer_not_fabric_pair'];self.assertEqual((len(a),len(b)),(4,6));self.assertTrue(all(all(not r.get(k)for k in pairing.TG_FIELDS)for r in a+b))
 def test_plasma_flow_not_tg_flow_or_loi_uncertainty(self):
  r=self.row(D,'DEAEP cotton120 initial Table3');self.assertIn('plasma125sccmnotTGflow',r['source_TG_pan_flow']);self.assertIn('notstatisticalsampleuncertainty',r['source_LOI_readout']);self.assertFalse(r.get('source_LOI_plusminus'));self.reject(r,atmosphere='N2');self.reject(r,heating_rate_C_min='20')
if __name__=='__main__':unittest.main()
