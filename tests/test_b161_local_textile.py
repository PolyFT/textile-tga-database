"""Protect ordinary TG conditions, exact durability states and native mass-loss criteria."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b161/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261004_b161_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing;import validate_tg_loi as v
A='10.1007/s10570-025-06460-8';B='10.1007/s10570-024-05979-6';C='10.1007/s10570-023-05125-8'
class TextileB161Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as handle:cls.rows=list(csv.DictReader(handle))
 def subset(self,doi):return[r for r in self.rows if r['DOI']==doi]
 def find(self,doi,sample,gas=None):return next(r for r in self.subset(doi)if r['sample_state']==sample and(gas is None or r['atmosphere']==gas))
 def accepted(self):return[r for r in self.rows if r['pairing_status']=='verified_exact']
 def noTG(self,row):self.assertTrue(all(not row.get(k)for k in pairing.TG_FIELDS))
 def test_four_states_four_conditions_not38facts(self):
  report=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(report['errors']);self.assertEqual((report['verified_exact_sample_states'],report['verified_exact_condition_records']),(4,4));self.assertEqual(len(self.rows),38)
 def test_all34_holds_excluded(self):
  held=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(held),34);self.assertEqual([sum(r['DOI']==doi for r in held)for doi in[A,B,C]],[3,22,9]);self.assertTrue(all(pairing.evidence_issues(r)for r in held))
 def test_bound_fingerprints_reject_measurement_and_state_changes(self):
  for r in self.accepted():
   self.assertFalse(pairing.evidence_issues(r))
   for key,value in [('LOI_pct','99'),('R750_pct','77'),('sample_state','otherdose'),('washing_state','30LC_water'),('atmosphere','air'),('heating_rate_C_min','50')]:self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**{key:value})))
 def test_fabric_cannot_be_joined_to_a_fiber(self):
  for r in self.accepted():self.assertEqual(r['material_form_TGA'],'cotton fabric');self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='cotton fiber')))
 def test_UV_ordinary_ramp_not_borrowed_TGIR(self):
  for sample in ['Pristine','Cotton_CCPD_HMP']:
   r=self.find(A,'UV_'+sample+'_initial');self.assertFalse(r['heating_rate_C_min']);self.assertEqual(r['atmosphere'],'N2');self.assertEqual((r['TG_start_C'],r['TG_end_C']),('50','800'));self.assertIn('ordinaryramp/model',r['source_TG_method_limit']);self.assertIn('notborrowed',r['source_TG_method_limit']);self.assertIn('ramp_unreported',r['pairing_status'])
 def test_UV_two_decomposition_peaks_retained_not_TGIR_gas_peaks(self):
  r=self.find(A,'UV_Cotton_CCPD_HMP_initial');self.assertEqual((r['T5_C'],r['Tmax1_C'],r['Tmax2_C'],r['R800_pct']),('211.2','256.4','349.68','37.44'));r=self.find(A,'UV_Pristine_initial');self.assertEqual((r['T5_C'],r['Tmax1_C'],r['R800_pct']),('279.6','359.2','16.73'));self.assertFalse(r['Tmax2_C'])
 def test_UV_bulk_cure10min_not_fabric_duration(self):
  r=self.find(A,'UV_Cotton_CCPD_HMP_initial');self.assertIn('SI10minUVisbulk',r['source_UV_time_limit']);self.assertIn('fabricUVduration/irradianceunreported',r['source_UV_time_limit']);self.assertEqual(r['source_addon_pct'],'22.5');self.assertIn('notfinalcoatingfraction',r['treatment_method'])
 def test_UV_bulk_TG_and_weightloss_not_char(self):
  self.assertFalse(any('Bulk' in r['sample_state']for r in self.subset(A)));r=self.find(A,'UV_Cotton_CCPD_HMP_initial');self.assertIn('stageweightloss37.49/16.52notchar',r['source_bulk_TG_exclusion']);self.assertEqual(r['residue_temp_C'],'800');self.assertNotEqual(r['R800_pct'],'34.13')
 def test_UV_preparation_rinse_not_three_durability_cycles(self):
  r=self.find(A,'UV_Cotton_CCPD_HMP_initial');self.assertEqual(r['washing_state'],'initial_after_preparation_ethanol_water_rinse');r=self.find(A,'UV_Cotton_CCPD_HMP_after3watercycles');self.noTG(r);self.assertEqual((r['LOI_pct'],r['source_LOI_uncertainty_pct']),('23.5','0.3'));self.assertIn('threewatercycles1h',r['source_wash_details'])
 def test_PEI_four_N2_native_profiles_joined_to_own_LOI(self):
  expected={'Cotton':('303.9','385.5','14.5','18'),'Al':('105.2','327.4','30.4','32.5'),'Fe':('234.4','346.2','31.7','28.5'),'FeAl':('227.9','295.3','34.5','35')}
  for sample,values in expected.items():
   r=self.find(B,'PEIPA_'+sample+'_initial','N2');self.assertEqual(tuple(r[k]for k in['T5_C','Tmax1_C','R750_pct','LOI_pct']),values);self.assertEqual(r['pairing_status'],'verified_exact')
 def test_PEI_air_vs_oxygen_conflict_holds_all_four_conditions(self):
  air=[r for r in self.subset(B)if r['atmosphere']=='air'];self.assertEqual(len(air),4)
  for r in air:self.assertIn('air_vs_oxygen',r['pairing_status']);self.assertIn('MethodsN2andOXYGEN',r['source_TG_method_conflict']);self.assertTrue(pairing.evidence_issues(r))
  self.assertEqual(self.find(B,'PEIPA_Cotton_initial','air')['R750_pct'],'0.5');self.assertEqual(self.find(B,'PEIPA_FeAl_initial','air')['R750_pct'],'27.5')
 def test_PEI_T75_not_canonical_T50_T80(self):
  r=self.find(B,'PEIPA_Cotton_initial','N2');self.assertEqual(r['source_T75_C'],'412.1');r=self.find(B,'PEIPA_Cotton_initial','air');self.assertEqual(r['source_T75_C'],'401.9')
  for r in self.subset(B):self.assertFalse(r.get('T50_C'));self.assertFalse(r.get('T80_C'));self.assertFalse(r.get('T75_C'))
  for sample in['Al','Fe','FeAl']:
   r=self.find(B,'PEIPA_'+sample+'_initial','N2');self.assertFalse(r['source_T75_C']);self.assertEqual(r['source_T75_raw'],'/')
 def test_PEI_early_T5_not_decomposition_onset(self):
  r=self.find(B,'PEIPA_Al_initial','N2');self.assertEqual(r['T5_C'],'105.2');self.assertFalse(r.get('Tonset_C'));self.assertIn('notassignedTonset',r['source_T5_definition']);self.assertEqual(self.find(B,'PEIPA_Al_initial','air')['T5_C'],'99.4')
 def test_PEI_standalone_ramp_endpoint_not_TGIR(self):
  for r in self.accepted():self.assertEqual((r['TG_start_C'],r['TG_end_C'],r['heating_rate_C_min'],r['residue_temp_C']),('40','750','10','750'));self.assertIn('40-70050Cmin',r['source_TGIR_exclusion']);self.assertIn('secondsnotTGtemperature',r['source_TGIR_exclusion'])
 def test_PEI_uncertain_recipe_and_control_state_not_invented(self):
  r=self.find(B,'PEIPA_FeAl_initial','N2');self.assertIn('combinedbathbasisunresolved',r['source_recipe_limit']);self.assertIn('totalcyclesnotassumed',r['source_recipe_limit']);r=self.find(B,'PEIPA_Cotton_initial','N2');self.assertEqual(r['washing_state'],'initial_unwashed_control_preparation_unreported');self.assertIn('preciseNaOHpretreatmentunreported',r['treatment_method'])
 def test_PEI_repeats_and_standard_deviation_not_exact_three(self):
  r=self.find(B,'PEIPA_FeAl_initial','N2');self.assertEqual(r['source_LOI_uncertainty_pct'],'0.5');self.assertIn('standard_deviation',r['source_uncertainty_type']);self.assertIn('atleast3',r['source_repeats']);self.assertIn('exactnunknown',r['source_repeats']);self.assertEqual(r['source_LOI_dimensions_mm'],'150x56')
 def test_PEI_all14_water_soap_poststates_NO_initialTG(self):
  rows=[r for r in self.subset(B)if r['treatment_state']=='washed'];self.assertEqual(len(rows),14)
  for r in rows:self.noTG(r);self.assertIn('FZT73023',r['washing_state']);self.assertIn('washedwaterorsoapstates',r['source_exact_state_hold'])
  self.assertEqual(self.find(B,'PEIPA_FeAl_water_30LC')['LOI_pct'],'32.5');self.assertEqual(self.find(B,'PEIPA_FeAl_soap_20LC')['LOI_pct'],'28.3');self.assertEqual(self.find(B,'PEIPA_FeAl_soap_30LC')['LOI_pct'],'25.4')
 def test_PEI_water_nonmonotonic_native_value_not_corrected(self):
  r=self.find(B,'PEIPA_FeAl_water_2LC');self.assertEqual((r['LOI_pct'],r['source_LOI_uncertainty_pct']),('24.8','0.2'));self.assertIn('notcorrectedto34.8',r['source_nonmonotonic_raw']);self.assertEqual(self.find(B,'PEIPA_FeAl_water_4LC')['LOI_pct'],'34.5')
 def test_PEI_all_four_UV_poststates_NO_initialTG(self):
  rows=[r for r in self.subset(B)if r['treatment_state']=='UV_aged'];self.assertEqual(len(rows),4)
  for r in rows:self.noTG(r);self.assertEqual(r['LOI_pct'],'35');self.assertIn('wavelength/intensityunreported',r['source_UV_details'])
 def test_Glow_all9_LOI_only_native_values(self):
  expected={'Blank':'17','SP1':'39','SP2':'40','SP3':'42','SP4':'42','SC1':'51','SC2':'52','SC3':'54','SC4':'55'}
  self.assertEqual(len(self.subset(C)),9)
  for sample,loi in expected.items():r=self.find(C,'Glow_'+sample+'_initial');self.assertEqual(r['LOI_pct'],loi);self.noTG(r);self.assertFalse(r['atmosphere']);self.assertFalse(r['heating_rate_C_min']);self.assertIn('LOI_only',r['pairing_status'])
 def test_Glow_printing_spray_and_pigment_feed_not_merged(self):
  r=self.find(C,'Glow_SP4_initial');self.assertEqual(r['source_pigment_feed_pct'],'15');self.assertIn('160C4minfix',r['treatment_method']);self.assertIn('hotwater_tap_rinse',r['washing_state']);r=self.find(C,'Glow_SC4_initial');self.assertIn('Decoseal2540',r['treatment_method']);self.assertIn('rinse_unreported',r['washing_state']);self.assertIn('notfinalfabricmassfraction',r['source_feed_definition'])
 def test_Glow_charwidth_and_partial_table_scope_retained(self):
  for r in self.subset(C):self.assertIn('Charwidth17/18mm',r['source_char_definition']);self.assertFalse(r['source_LOI_uncertainty_pct']);self.assertIn('sevennontargettablesunread',r['source_TG_absence_scope']);self.assertIn('notglobalTGabsenceclaim',r['source_TG_absence_scope'])
 def test_public_facts_no_private_paths_and_dates_valid(self):
  for r in self.rows:
   self.assertRegex(r['evidence_reviewed_at'],r'^\d{4}-\d{2}-\d{2}$')
   self.assertFalse(any(('/'+'Volumes'+'/')in str(x)or('/'+'Users'+'/')in str(x)or('smb'+':'+chr(47)*2)in str(x)for x in r.values()))
if __name__=='__main__':unittest.main(verbosity=2)
