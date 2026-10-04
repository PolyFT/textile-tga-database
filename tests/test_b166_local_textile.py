"""Guard native condition evidence, water-loss criteria and washed-state pairing."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b166/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261004_b166_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing;import validate_tg_loi as v
A='10.1007/s10570-024-05785-0';B='10.1007/s10570-024-06177-0';C='10.1007/s10570-025-06556-1'
class TextileB166Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def subset(self,doi):return[r for r in self.rows if r['DOI']==doi]
 def find(self,doi,sample,gas=None):return next(r for r in self.subset(doi)if r['sample_state']==sample and(gas is None or r['atmosphere']==gas))
 def accepted(self):return[r for r in self.rows if r['pairing_status']=='verified_exact']
 def noTG(self,r):self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS))
 def test_three_states_three_conditions_not23facts(self):
  p=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(p['errors']);self.assertEqual((p['verified_exact_sample_states'],p['verified_exact_condition_records']),(3,3));self.assertEqual(len(self.rows),23)
 def test_twenty_held_excluded(self):
  rows=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(rows),20);self.assertEqual([sum(r['DOI']==d for r in rows)for d in[A,B,C]],[8,3,9]);self.assertTrue(all(pairing.evidence_issues(r)for r in rows))
 def test_review_rejects_mutated_metric_condition_or_state(self):
  for r in self.accepted():
   self.assertFalse(pairing.evidence_issues(r))
   for k,value in [('LOI_pct','99'),('T5_C','300'),('Tmax1_C','555'),('R800_pct','77'),('atmosphere','oxygen'),('heating_rate_C_min','50'),('washing_state','50LC'),('sample_state','otherdose')]:self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**{k:value})))
 def test_fabric_not_fiber(self):
  for r in self.accepted():self.assertEqual(r['material_form_TGA'],'cotton fabric');self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='cotton fiber')))
 def test_acapoc_all_ordinary_ramps_unknown(self):
  for r in self.subset(A):self.assertFalse(r['heating_rate_C_min']);self.assertNotEqual(r['pairing_status'],'verified_exact')
 def test_acapoc_oxygen_air_conflict_retained(self):
  rows=[r for r in self.subset(A)if r['atmosphere']=='O2'];self.assertEqual(len(rows),2)
  for r in rows:self.assertIn('Table1O2versusFig6captionair',r['source_oxidizing_atmosphere_conflict']);self.assertIn('oxygen_air_conflict',r['pairing_status'])
 def test_acapoc_two_peaks_and_at_peak_mass_not_char(self):
  r=self.find(A,'ACAPOC_25_initial','N2');self.assertEqual(tuple(r[k]for k in['T5_C','Tmax1_C','Tmax2_C','R600_pct','source_at_peak_remaining_mass1_pct','source_at_peak_remaining_mass2_pct']),('263','279','321','42.3','89.3','66.8'));self.assertFalse(r.get('Tonset_C'));self.assertFalse(r['TG_end_C']);self.assertEqual(r['residue_temp_C'],'600')
 def test_acapoc_otherdose_no_curve_estimates(self):
  r=self.find(A,'ACAPOC_15_initial');self.assertFalse(r['LOI_pct']);self.noTG(r);self.assertIn('curveunreadnotestimated',r['source_LOI_limit']);r=self.find(A,'ACAPOC_20_initial');self.assertEqual(r['LOI_pct'],'44.1');self.noTG(r)
 def test_acapoc_washed_not_initial_TG(self):
  for dose,value in [('20','32.9'),('25','33.8')]:r=self.find(A,'ACAPOC_'+dose+'_after50LC');self.assertEqual(r['LOI_pct'],value);self.noTG(r);self.assertIn('reportedLCnotmultiplied',r['source_wash_details'])
 def test_acapoc_reagent_and_char_unit_conflicts_preserved(self):
  for r in self.subset(A):
   if r['atmosphere']:self.assertIn('POCl3',r['source_reagent_conflict']);self.assertIn('PCl3',r['source_reagent_conflict']);self.assertIn('Table3charlengthmmversusbodycm',r['source_VFT_conflict'])
 def test_durable_no_independent_LOI(self):
  self.assertEqual(len(self.subset(B)),3)
  for r in self.subset(B):self.assertFalse(r['LOI_pct']);self.assertIn('VFT/UPF/waterproofgradesarenotLOI',r['source_LOI_missing_scope']);self.assertNotEqual(r['pairing_status'],'verified_exact')
 def test_durable_T75_not_T50_or_T80(self):
  r=self.find(B,'Durable_Pristine_initial');self.assertEqual(r['source_T75_C'],'386.2');self.assertFalse(r.get('T50_C'));self.assertFalse(r.get('T80_C'));self.assertFalse(r.get('Tonset_C'))
 def test_durable_own_TG_not_computed_layer_or_muffle_char(self):
  for s,expected in [('Pristine',('214.7','399.8','11.5')),('FR',('137.5','294.4','35.1')),('SFR',('201.4','289.1','43.3'))]:r=self.find(B,'Durable_'+s+'_initial');self.assertEqual(tuple(r[k]for k in['T5_C','Tmax1_C','R700_pct']),expected);self.assertEqual((r['TG_start_C'],r['TG_end_C'],r['heating_rate_C_min']),('30','700','20'));self.assertIn('notdeductedlayerchar24.1/26.8ormuffle3Cmin',r['source_metric_definition'])
 def test_durable_increment_not_whole_fabric_loading(self):
  r=self.find(B,'Durable_SFR_initial');self.assertEqual((r['source_weight_gain_pct'],r['source_SFR_increment_pct']),('19.8','7.5'));self.assertIn('notrecalculated',r['source_SFR_increment_basis'])
 def test_multifunctional_accepted_own_native_numbers(self):
  for s,expected in [('Cotton',('249.6','403.2','12.0','18')),('PAP',('243.8','327.9','40.7','37.8')),('PAP-Fe_QAS',('235.9','332.8','36.3','37.5'))]:r=self.find(C,'Multifunctional_'+s+'_initial','N2');self.assertEqual(tuple(r[k]for k in['T5_C','Tmax1_C','R800_pct','LOI_pct']),expected);self.assertEqual(r['pairing_status'],'verified_exact')
 def test_multifunctional_N2_endpoint_unknown_not_R800(self):
  for r in self.accepted():self.assertFalse(r['TG_start_C']);self.assertFalse(r['TG_end_C']);self.assertEqual(r['residue_temp_C'],'800');self.assertIn('W800footnoteexplicitchar800notN2programend',r['source_metric_definition'])
 def test_multifunctional_air_rate_not_N2_rate(self):
  rows=[r for r in self.subset(C)if r['atmosphere']=='air'];self.assertEqual(len(rows),3)
  for r in rows:self.assertFalse(r['heating_rate_C_min']);self.assertEqual((r['TG_start_C'],r['TG_end_C']),('30','800'));self.assertEqual(r['pairing_status'],'held_air_TG_ramp_unreported');self.assertIn('cannotborrowN210',r['source_air_ramp_hold'])
 def test_multifunctional_air_native_equal_T5_Tmax_not_corrected(self):
  r=self.find(C,'Multifunctional_PAP-Fe_QAS_initial','air');self.assertEqual((r['T5_C'],r['Tmax1_C']),('282.9','282.9'));self.assertNotEqual(r['pairing_status'],'verified_exact')
 def test_multifunctional_DTG_units_water_T5_and_model_label(self):
  for r in self.accepted():self.assertIn('DTGmaxpctperCnotpctpermin',r['source_metric_definition']);self.assertFalse(r.get('Tonset_C'));self.assertIn('rawTG209(TAInstruments)',r['source_model_vendor_conflict']);self.assertEqual(r['heating_rate_C_min'],'10')
 def test_multifunctional_all_six_washed_LOIs_have_no_washed_TG(self):
  for s,values in [('PAP',{10:36.1,50:32.,80:28.8,100:25.1}),('PAP-Fe_QAS',{10:28.6,50:21.4})]:
   for cycle,value in values.items():r=self.find(C,'Multifunctional_'+s+'_after'+str(cycle)+'LC');self.assertEqual(float(r['LOI_pct']),value);self.noTG(r);self.assertIn('notmultiplied',r['source_wash_details']);self.assertIn('dashesunknownnotzero',r['source_wash_TG_limit'])
 def test_multifunctional_loading_stack_and_repeats_not_borrowed(self):
  r=self.find(C,'Multifunctional_PAP-Fe_QAS_initial','N2');self.assertEqual(r['source_weight_gain_pct'],'14');self.assertIn('charEDSnotfabricPloading',r['source_composition_limit']);self.assertIn('4stackedfabriclayers',r['source_other_test_exclusion']);self.assertIn('notLOIreplicates',r['source_LOI_repeats_uncertainty'])
 def test_public_facts_no_private_paths_or_contacts(self):
  for r in self.rows:self.assertRegex(r['evidence_reviewed_at'],r'^\d{4}-\d{2}-\d{2}$');self.assertFalse(any(('/'+'Volumes'+'/')in str(x)or('/'+'Users'+'/')in str(x)or('smb'+':'+chr(47)*2)in str(x)or'@163.com'in str(x)for x in r.values()))
if __name__=='__main__':unittest.main(verbosity=2)
