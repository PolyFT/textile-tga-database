"""Prevent process aliases, calculated curves and combustion data from becoming TG pairs."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b148/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261004_b148_local_textile.csv'
sys.path.insert(0,str(R/'scripts'))
import pairing
import validate_tg_loi as v
A='10.1016/j.polymdegradstab.2010.04.023';B='10.1016/j.polymdegradstab.2010.04.005';C='10.1016/j.polymertesting.2019.03.015';D='10.1016/j.apsusc.2020.145265'
class TextileB148Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def row(self,d,s):return next(r for r in self.rows if r['DOI']==d and r['sample_state']==s)
 def reject(self,r,**changes):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**changes)))
 def test_eight_pairs_not_fortythree_facts(self):
  p=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(p['errors']);self.assertEqual((p['verified_exact_sample_states'],p['verified_exact_condition_records']),(8,8));self.assertEqual(len(self.rows),43)
 def test_thirtyfive_held_never_grade_a(self):
  held=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(held),35);self.assertTrue(all(pairing.evidence_issues(r)for r in held));self.assertTrue(all(r['review_disposition']=='held_outside_verified_target'for r in held))
 def test_pa_initial_dp_exact_not_middle_alias(self):
  r=self.row(A,'AM-g-nylon66 DP32.5 initial');self.assertEqual((r['source_DP_pct'],r['LOI_pct'],r['Tonset_C']),('32.5','26.2','374'));self.reject(r,sample_state='AM-g-nylon66 DP16.9 initial');self.reject(r,Tonset_C='412')
 def test_middle_dp16_6_and16_9_keep_separate_quantities(self):
  t=self.row(A,'AM-g-nylon66 DP16.6 TGonly');l=self.row(A,'AM-g-nylon66 DP16.9 initialLOIonly');self.assertEqual(t['Tonset_C'],'412');self.assertFalse(t['LOI_pct']);self.assertEqual(l['LOI_pct'],'22.7');self.assertTrue(all(not l.get(k)for k in pairing.TG_FIELDS));self.assertNotEqual(t['source_DP_pct'],l['source_DP_pct'])
 def test_pa_375_deamination_peak_not_water_or_higher_peak(self):
  r=self.row(A,'AM-g-nylon66 DP32.5 initial');self.assertEqual(r['Tmax1_C'],'375');self.assertIn('amide',r['source_peak_definition']);self.assertFalse(r.get('water_removal_peak_C'));self.reject(r,Tmax1_C='440')
 def test_pa_higher_peak_conflict_never_canonical(self):
  r=self.row(A,'AM-g-nylon66 DP32.5 initial');self.assertIn('440',r['source_raw_higher_peak_C']);self.assertIn('442',r['source_raw_higher_peak_C']);self.assertFalse(r.get('Tmax2_C'));self.reject(r,Tmax2_C='442')
 def test_pa_unknown_numeric_residue_not_estimated(self):
  r=self.row(A,'AM-g-nylon66 DP32.5 initial');self.assertFalse(r.get('R600_pct')or r.get('residue_pct'));self.assertIn('noexactnumber',r['source_raw_R600']);self.reject(r,R600_pct='20')
 def test_pa_six_washed_loi_without_tg(self):
  x=[r for r in self.rows if r['DOI']==A and r['pairing_status']=='held_washed_LOI_without_TG'];self.assertEqual(len(x),6);self.assertEqual([r['LOI_pct']for r in x],['22.2','21.4','20.9','25.5','24.0','22.9']);self.assertTrue(all(all(not r.get(k)for k in pairing.TG_FIELDS)for r in x));self.assertTrue(all('unreported' in r['washing_state']for r in x))
 def test_pa_control_loi_conflict_not_repaired(self):
  r=self.row(A,'Ungraftednylon66 control conflictingLOI');self.assertIn('19.8',r['source_raw_LOI']);self.assertIn('19.9',r['source_raw_LOI']);self.assertFalse(r['LOI_pct']);self.assertNotEqual(r['pairing_status'],'verified_exact')
 def test_pa_process_dp31_3_not_assigned_to32_5(self):
  r=self.row(A,'AM-g-nylon66 DP32.5 initial');self.assertIn('31.3',r['source_recipe_conflict']);self.assertIn('durationunassigned',r['source_recipe_conflict']);self.assertEqual(self.row(A,'Processscreen DP31.3 at20wtAM40min')['source_DP_pct'],'31.3')
 def test_pet_native_four_groups_and_650_residues(self):
  x=[r for r in self.rows if r['DOI']==B and r['pairing_status']=='verified_exact'];self.assertEqual([(r['LOI_pct'],r['R650_pct'])for r in x],[('22.9','6.0'),('17.4','0.3'),('26.0','3.9'),('25.9','15.7')]);self.reject(self.row(B,'PET-4 GMA-g-PET FR'),R650_pct='3.9',LOI_pct='26.0')
 def test_pet_graft_only_and_graft_fr_not_same_recipe(self):
  g=self.row(B,'PET-2 GMA-g-PET');f=self.row(B,'PET-4 GMA-g-PET FR');self.assertEqual((g['source_Gp_pct'],f['source_Gp_pct'],f['source_FR_addon_pct']),('28.4','22.5','5.6'));self.assertIn('denominatorunreported',f['source_Gp_definition']);self.reject(f,sample_state=g['sample_state'])
 def test_pet_dsc_temperatures_are_not_dtg_maxima(self):
  x=[r for r in self.rows if r['DOI']==B and r['pairing_status']=='verified_exact'];self.assertTrue(all(not r.get('Tmax1_C')for r in x));self.assertEqual(self.row(B,'PET-4 GMA-g-PET FR')['source_DSC_observation'],'Exothermal416/endothermal362C;DSCnotDTG');self.reject(x[0],Tmax1_C='530')
 def test_pet_approximate_control_onsets_remain_raw(self):
  r=self.row(B,'PET-1 untreated');self.assertFalse(r['Tonset_C']);self.assertIn('350',r['source_raw_control_onsets']);self.assertIn('486',r['source_raw_control_onsets']);self.reject(r,Tonset_C='350')
 def test_native_starts_are_not_t5_or_t10(self):
  for d,s,n in[(A,'AM-g-nylon66 DP32.5 initial','374'),(B,'PET-2 GMA-g-PET','290'),(B,'PET-3 FR-only','335'),(B,'PET-4 GMA-g-PET FR','318')]:
   r=self.row(d,s);self.assertEqual(r['Tonset_C'],n);self.assertFalse(r.get('T5_C')or r.get('T10_C'));self.assertIn('criterionunreported',r['source_Tonset_definition']);self.reject(r,Tonset_C='',T5_C=n)
 def test_pet_theoretical242_and2_67_not_measured(self):
  r=self.row(B,'Theoretical weighted TG curve4');self.assertEqual((r['source_theoretical_start_C'],r['source_theoretical_R650_pct']),('242','2.67'));self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS));self.assertFalse(r['LOI_pct']);self.assertNotEqual(r['pairing_status'],'verified_exact')
 def test_pet_unknown_program_not_borrowed_from_pa(self):
  r=self.row(B,'PET-4 GMA-g-PET FR');a=self.row(A,'AM-g-nylon66 DP32.5 initial');self.assertFalse(r.get('TG_start_C')or r.get('TG_end_C'));self.assertEqual((a['TG_start_C'],a['TG_end_C']),('100','650'));self.assertEqual((r['source_TG_mass_mg'],a['source_TG_mass_mg']),('2-3','3-5'));self.assertEqual(r['atmosphere'],'air');self.assertEqual(r['source_TG_atmosphere_mode'],'Staticairreported;notflowingair')
 def test_pbi_six_exact_tg_profiles_without_loi_crosswalk(self):
  x=[r for r in self.rows if r['DOI']==C and r['pairing_status']=='held_fiber_LOI_and_drawing_mapping_unresolved'];self.assertEqual(len(x),6);self.assertTrue(all(not r['LOI_pct']for r in x));self.assertEqual([(r['T5_C'],r['T10_C'],r['Tmax1_C'])for r in x],[('532','563','580'),('535','566','582'),('555','579','587'),('548','580','591'),('560','579','593'),('561','585','597')]);self.assertTrue(all(not r.get('residue_temp_C')for r in x))
 def test_pbi_loi54_not_assigned_using_conclusion_conflict(self):
  r=self.row(C,'PBIPI LOI unspecifiedformula_and_drawing');self.assertEqual(r['LOI_pct'],'54');self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS));self.assertIn('PI5',r['source_location']);self.assertIn('PI2conflict',r['source_location'])
 def test_aps_three_native_si_profiles_match_primary_loi(self):
  x=[r for r in self.rows if r['DOI']==D and r['pairing_status']=='verified_exact'];self.assertEqual([(r['T5_C'],r['T50_C'],r['Tmax1_C'],r['R500_pct'],r['LOI_pct'])for r in x],[('105.6','336.5','339.0','2.08','17.14'),('89.4','335.8','332.1','27.06','19.23'),('105.7','336.7','333.1','23.3','20.35')]);self.reject(x[1],LOI_pct='20.35')
 def test_aps_low_t5_includes_water_not_decomposition_onset(self):
  r=self.row(D,'Cotton NiOH2 superamphiphilic');self.assertEqual(r['T5_C'],'89.4');self.assertFalse(r['Tonset_C']);self.assertIn('earlywaterloss',r['source_T5_definition']);self.reject(r,T5_C='',Tonset_C='89.4')
 def test_aps_500_residue_includes_inorganic_not_600_calcination(self):
  r=self.row(D,'Cotton NiOH2 superamphiphilic');self.assertEqual((r['R500_pct'],r['residue_temp_C']),('27.06','500'));self.assertIn('inorganicNiO',r['source_residue_definition']);self.assertFalse(r.get('R600_pct')or r.get('char_pct'));self.reject(r,R500_pct='',R600_pct='27.06',residue_temp_C='600')
 def test_aps_own_loi_instrument_dimensions_repeats(self):
  r=self.row(D,'Cotton NiOH2 PFOA superamphiphobic');self.assertEqual((r['LOI_instrument'],r['source_LOI_dimensions_mm'],r['source_LOI_repeats'],r['source_LOI_temperature_C'],r['source_LOI_RH_pct']),('5801A,SuzhouVouch','140x50x0.3','3','23','55'));self.assertIn('versionunreported',r['LOI_standard'])
 def test_aps_twelve_variant_wash_facts_do_not_borrow_initial_tg(self):
  x=[r for r in self.rows if r['DOI']==D and r['pairing_status']!='verified_exact'];self.assertEqual(len(x),12);self.assertTrue(all(not r['LOI_pct']and all(not r.get(k)for k in pairing.TG_FIELDS)for r in x));self.assertEqual(sum(r['pairing_status'].startswith('held_washed')for r in x),6)
 def test_fiber_powder_gas_and_wash_state_mutations_rejected(self):
  r=self.row(D,'Cotton NiOH2 superamphiphilic');self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='NiOH2 powder')));self.reject(r,atmosphere='N2');self.reject(r,heating_rate_C_min='20');self.reject(r,washing_state='After2h700rpmwashing')
 def test_aps_surface_atom_fraction_not_bulk_mass_fraction(self):
  r=self.row(D,'Cotton NiOH2 PFOA superamphiphobic');self.assertIn('atompercentNOTbulk',r['source_XPS_definition']);self.assertIn('absoluteamountsunreported',r['source_hydrothermal_molar_ratio']);self.assertEqual(r['source_PFOA_M'],'0.02')
 def test_pet_table_dashes_remain_missing_not_zero(self):
  r=self.row(B,'PET-1 untreated');self.assertFalse(r['source_Gp_pct']or r['source_FR_addon_pct']);self.assertFalse(self.row(B,'PET-2 GMA-g-PET')['source_FR_addon_pct']);self.assertFalse(self.row(B,'PET-3 FR-only')['source_Gp_pct'])
if __name__=='__main__':unittest.main()
