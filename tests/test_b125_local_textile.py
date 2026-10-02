"""Guard wash identity, conflicting metrics, acid lineage and gas-specific peaks."""
import csv, sys, unittest
from pathlib import Path
import pandas as pd
H=Path(__file__).resolve().parent; P=H.name=='work'; R=H.parent/'repo' if P else H.parent
F=H/'staged-local-textile-b125/publication_proposed.csv' if P else R/'data/incoming/verified_source_batch_20261002_b125_local_textile.csv'
sys.path.insert(0,str(R/'scripts')); import pairing, validate_tg_loi as v
DH='10.1002/app.32074'; CS='10.1016/j.carbpol.2017.02.084'
class TextileB125Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='') as f:cls.rows=list(csv.DictReader(f))
 def source(self,d):return [r for r in self.rows if r['DOI']==d]
 def row(self,d,s,gas=None):return next(r for r in self.source(d) if r['sample_state']==s and (gas is None or r['atmosphere']==gas))
 def rejected(self,r,**changes):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**changes)))
 def test_nine_independent_states_seventeen_conditions_not_twenty_nine_facts(self):
  z=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(z['errors']);self.assertEqual((z['verified_exact_sample_states'],z['verified_exact_condition_records']),(9,17));self.assertEqual(len(self.rows),29);self.assertEqual(sum(r['pairing_status']!='verified_exact' for r in self.rows),12)
 def test_dhdbp_only_trial6_after_one_wash_has_matching_tg(self):
  rr=[r for r in self.source(DH) if r['pairing_status']=='verified_exact'];self.assertEqual(len(rr),1);r=rr[0];self.assertEqual((r['source_trial'],r['source_native_washing_times'],r['LOI_pct'],r['LOI_uncertainty_pct']),('6','1','27.6','0.2'));self.rejected(r,LOI_pct='36.8',washing_state='Beforewashing')
 def test_dhdbp_table234_and_conclusion113_onset_conflict_blank(self):
  r=self.row(DH,'Trial6-PETcotton-after1wash');self.assertEqual((r['source_TableI_Ton_C'],r['source_conclusion_Ton_C']),('234','113'));self.assertFalse(r['Tonset_C']);self.rejected(r,Tonset_C='234');self.rejected(r,Tonset_C='113')
 def test_dhdbp_peak_precision_difference_preserved_without_canonical_choice(self):
  r=self.row(DH,'Trial6-PETcotton-after1wash');self.assertEqual((r['source_TableI_Tmax1_C'],r['source_TableI_Tmax2_C'],r['source_Fig5B_direct_peak1_C'],r['source_Fig5B_direct_peak2_C']),('274','413','274.3','413.6'));self.assertFalse(r['Tmax1_C']);self.assertFalse(r['Tmax2_C']);self.rejected(r,Tmax2_C='413.6')
 def test_dhdbp_three_fixed_temperature_retentions_are_one_tg_condition(self):
  r=self.row(DH,'Trial6-PETcotton-after1wash');self.assertEqual((r['source_weight_retention_385C_pct'],r['source_weight_retention_485C_pct'],r['residue_pct'],r['residue_temp_C'],r['TG_end_C']),('74.8','38.0','35.4','585','590'));self.rejected(r,residue_temp_C='590',char_temp_C='590');self.assertEqual(sum(r['pairing_status']=='verified_exact' for r in self.source(DH)),1)
 def test_dhdbp_addon_native_treated_mass_denominator_not_conventional_wg(self):
  r=self.row(DH,'Trial6-PETcotton-after1wash');self.assertEqual(r['source_native_addon_pct'],'20.6');self.assertTrue(r['source_native_addon_denominator'].startswith('wt,treatedfabricmass'));self.assertFalse(r.get('source_WG_pct'));self.assertFalse(r.get('additive_loading_wt_pct'));self.assertEqual((r['source_DHDBP_bath_wt_pct'],r['source_CA_bath_wt_pct'],r['source_NaH2PO2_bath_wt_pct']),('30','12','6'))
 def test_dhdbp_cross_table_wash1_is_corroboration_not_second_sample(self):
  r=self.row(DH,'Trial6-PETcotton-after1wash');self.assertEqual((r['source_TableIII_same_state_LOI_pct'],r['source_TableIII_same_state_LOI_uncertainty_pct']),('27.6','0.2'));self.assertEqual(sum(r['sample_state']=='Trial6-PETcotton-after1wash' for r in self.source(DH)),1)
 def test_dhdbp_unwashed_and_five_ten_wash_lois_do_not_borrow_tg(self):
  rr=[self.row(DH,f'Trial6-PETcotton-after{x}washes') for x in [0,5,10]];self.assertEqual([r['LOI_pct'] for r in rr],['36.8','25.6','25.1']);self.assertTrue(all(all(not r[k] for k in pairing.TG_FIELDS) for r in rr));self.assertTrue(all(r['pairing_status']!='verified_exact' for r in rr))
 def test_dhdbp_control_loi_and_tg_washing_lineage_not_assumed(self):
  a=self.row(DH,'Trial0-PETcotton-after1wash');b=self.row(DH,'UntreatedT-C-TGonly');self.assertEqual(a['LOI_pct'],'17.2');self.assertFalse(b['LOI_pct']);self.assertEqual(b['washing_state'],'Unreported');self.assertEqual(b['source_weight_retention_585C_pct'],'24.8');self.assertTrue(all(not r[k] for r in [a,b] for k in pairing.TG_FIELDS))
 def test_dhdbp_pure_compound_and_stage_losses_do_not_become_textile_char(self):
  r=self.row(DH,'PureDHDBP-nontextile-TGonly');self.assertFalse(r['LOI_pct']);self.assertNotEqual(r['pairing_status'],'verified_exact');r=self.row(DH,'Trial6-PETcotton-after1wash');self.assertEqual((r['source_stage_weight_loss1_pct'],r['source_stage_weight_loss2_pct'],r['char_pct']),('15','42.6','35.4'));self.rejected(r,char_pct='85',residue_pct='85')
 def test_cs_osa_eight_native_codes_have_sixteen_gas_records(self):
  rr=self.source(CS);self.assertEqual(len(rr),16);self.assertEqual(len({r['sample_state'] for r in rr}),8);self.assertEqual({r['atmosphere'] for r in rr},{'air','N2'});self.assertTrue(all(r['pairing_status']=='verified_exact' for r in rr))
 def test_cs_osa_scoured_and_acid_controls_have_distinct_own_metrics(self):
  a=self.row(CS,'SS-PA66-Control','N2');b=self.row(CS,'HT-PA66-Control','N2');self.assertEqual((a['LOI_pct'],a['T5_C'],a['residue_pct']),('19.5','382','2.3'));self.assertEqual((b['LOI_pct'],b['T5_C'],b['residue_pct']),('21.5','378','2.1'));self.assertEqual((a['source_pretreatment_HCl_M'],b['source_pretreatment_HCl_M']),('0','3'));self.rejected(b,LOI_pct='19.5');self.assertTrue(all(not r['source_HCl_time_min'] and not r['source_HCl_temperature_C'] for r in [a,b]))
 def test_cs_osa_equal_loi_does_not_merge_five_and_fifteen_quadralayers(self):
  a=self.row(CS,'SS-PA66-5 QL','N2');b=self.row(CS,'SS-PA66-15 QL','N2');self.assertEqual((a['LOI_pct'],b['LOI_pct']),('21.3','21.3'));self.assertNotEqual(a['source_QL'],b['source_QL']);self.assertNotEqual(a['T5_C'],b['T5_C']);z=v.build_tables(pd.DataFrame(self.source(CS)).fillna(''),v.issue_list())[3];self.assertEqual(z['verified_exact_sample_states'],8)
 def test_cs_osa_tminusfive_is_t5_not_generic_onset(self):
  r=self.row(CS,'HT-PA66-10 QL','air');self.assertEqual(r['T5_C'],'286');self.assertFalse(r['Tonset_C']);self.assertFalse(r['T10_C']);self.rejected(r,T5_C='',Tonset_C='286')
 def test_cs_osa_second_third_air_peaks_not_transferred_to_nitrogen(self):
  a=self.row(CS,'SS-PA66-5 QL','air');n=self.row(CS,'SS-PA66-5 QL','N2');self.assertEqual((a['Tmax1_C'],a['Tmax2_C'],a['Tmax3_C']),('396','440','590'));self.assertEqual(n['Tmax1_C'],'399');self.assertFalse(n['Tmax2_C']);self.assertFalse(n['Tmax3_C']);self.rejected(n,Tmax3_C='590');self.assertFalse(self.row(CS,'HT-PA66-Control','air')['Tmax3_C'])
 def test_cs_osa_rounded_group_averages_not_individual_r800(self):
  a=self.row(CS,'SS-PA66-10 QL','air');b=self.row(CS,'HT-PA66-10 QL','air');self.assertEqual((a['residue_pct'],b['residue_pct']),('4.2','5.6'));self.assertEqual(a['source_prose_rounded_group_average_air_char_pct'],'5');self.rejected(a,char_pct='5',residue_pct='5');self.assertEqual(self.row(CS,'HT-PA66-10 QL','N2')['residue_pct'],'11.4')
 def test_cs_osa_r800_not_assumed_method_range_and_tgir_flow_not_main_tg(self):
  rr=self.source(CS);self.assertTrue(all(r['residue_temp_C']=='800' and r['source_TGIR_N2_flow_mL_min']=='55' for r in rr));self.assertTrue(all(not r.get(k) for r in rr for k in ['TG_start_C','TG_end_C','TG_mass_mg','TG_flow_mL_min']));self.assertEqual(self.row(CS,'SS-PA66-10 QL','N2')['LOI_sample_dimensions_mm'],'150x58;thicknessunreported')
 def test_cs_osa_version_supplement_and_missing_bath_concentrations_preserved(self):
  rr=self.source(CS);self.assertTrue(all('acceptedmanuscript' in r['source_document_version'] and 'notfinaltypeset' in r['source_document_version'] for r in rr));self.assertTrue(all('TableS1' in r['TG_locator'] and 'wholeXML' in r['supplement_review_status'] for r in rr));self.assertTrue(all(not r[k] for r in rr for k in ['source_CS_bath_concentration','source_PA_bath_concentration','source_OSA_bath_concentration']));self.assertEqual(self.row(CS,'HT-PA66-5 QL','air')['source_bath_pH'],'5');self.assertEqual(self.row(CS,'SS-PA66-Control','air')['source_native_control_addon'],'dash');self.assertFalse(self.row(CS,'SS-PA66-Control','air')['source_addon_pct'])
if __name__=='__main__':unittest.main()
