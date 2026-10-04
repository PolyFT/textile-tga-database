"""Keep native contradictions, water criteria, blend forms and dose joins explicit."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b159/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261004_b159_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing;import validate_tg_loi as v
A='10.1007/s10570-024-06218-8';B='10.1007/s10570-023-05506-z';C='10.1007/s10570-023-05265-x'
class TextileB159Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def subset(self,doi):return[r for r in self.rows if r['DOI']==doi]
 def find(self,doi,sample,gas=None):return next(r for r in self.subset(doi)if r['sample_state']==sample and(gas is None or r['atmosphere']==gas))
 def accepted(self):return[r for r in self.rows if r['pairing_status']=='verified_exact']
 def noTG(self,r):self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS))
 def test_four_states_five_conditions_not23facts(self):
  p=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(p['errors']);self.assertEqual((p['verified_exact_sample_states'],p['verified_exact_condition_records']),(4,5));self.assertEqual(len(self.rows),23)
 def test_eighteen_holds_excluded(self):
  held=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(held),18);self.assertEqual([sum(r['DOI']==d for r in held)for d in[A,B,C]],[5,5,8]);self.assertTrue(all(pairing.evidence_issues(r)for r in held))
 def test_review_fingerprints_bind_numbers_conditions_states(self):
  for r in self.accepted():
   self.assertFalse(pairing.evidence_issues(r))
   for k,x in [('LOI_pct','99'),('Tmax1_C','777'),('sample_state','Otherdose'),('washing_state','after20LC'),('atmosphere','Ar'),('heating_rate_C_min','60')]:self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**{k:x})))
 def test_own_fabric_not_standalone_fiber(self):
  for r in self.accepted():self.assertEqual(r['material_form_TGA'],'cotton fabric');self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='cotton fiber')))
 def test_Psyn_blend_not_purecotton(self):
  for r in self.subset(A):self.assertEqual(r['material_form'],'98% cotton/2% spandex twill fabric');self.assertIn('280gsm98cotton2spandex',r['composition']);self.assertNotEqual(r['pairing_status'],'verified_exact')
 def test_Psyn_both_Tmax_conflicts_retained(self):
  for sample,table,body in [('Control','338.61','336'),('P-syn1','326.57','314.81')]:
   r=self.find(A,'Psyn_'+sample+'_initial');self.assertEqual((r['Tmax1_C'],r['source_Tmax_body_C']),(table,body));self.assertIn('wholeTGconditionsheld',r['source_Tmax_conflict']);self.assertNotEqual(r['pairing_status'],'verified_exact')
 def test_Psyn_T10_not_T5_or_DSC_peak(self):
  r=self.find(A,'Psyn_Control_initial');self.assertEqual((r['T10_C'],r['R600_pct'],r['TG_end_C']),('280.38','0.73','600'));self.assertFalse(r['T5_C']);self.assertIn('notTGgasorDTGpeaks',r['source_DSC_method'])
 def test_Psyn_other_formulations_LOI_only(self):
  for k,loi in [('2','31.6'),('3','34.9'),('4','37.2')]:r=self.find(A,'Psyn_P-syn'+k+'_initial');self.noTG(r);self.assertEqual(r['LOI_pct'],loi)
 def test_Psyn_measured_WG_not15percent_FR_basis(self):
  r=self.find(A,'Psyn_P-syn1_initial');self.assertEqual(r['source_weight_gain_wt_pct'],'12.73');self.assertIn('15pctFRbasisunreported',r['treatment_method']);self.assertIn('molar1:1:2',r['treatment_method'])
 def test_TDB_samplelabels_not_WG_or_bath_weightfraction(self):
  for sample,bath,wg,loi in [('Cotton10','100','8.6','29.9'),('Cotton20','200','17.3','32.7'),('Cotton30','300','26.5','35.2')]:
   r=self.find(B,'TDBTZP_'+sample+'_initial','N2');self.assertEqual((r['source_bath_gL'],r['source_weight_gain_wt_pct'],r['LOI_pct']),(bath,wg,loi));self.assertIn('not10/20/30pctWG',r['source_name_WG_mapping'])
 def test_TDB_water_T5_preserved_not_promoted_onset(self):
  for sample,t5,t10 in [('Cotton20','121','202'),('Cotton30','117','277')]:
   r=self.find(B,'TDBTZP_'+sample+'_initial','N2');self.assertEqual((r['T5_C'],r['T10_C']),(t5,t10));self.assertFalse(r.get('Tonset_C'));self.assertIn('notdecompositiononset',r['source_T5_definition'])
 def test_TDB_four_N2_one_controlair_same_samplecount(self):
  rows=self.accepted();self.assertEqual(sum(r['atmosphere']=='N2'for r in rows),4);self.assertEqual(sum(r['atmosphere']=='air'for r in rows),1);self.assertEqual({r['sample_state']for r in rows if r['atmosphere']=='air'},{'TDBTZP_Control_initial'})
 def test_TDB_airCotton20_inversion_not_swapped(self):
  r=self.find(B,'TDBTZP_Cotton20_initial','air');self.assertEqual((r['T5_C'],r['T10_C']),('122','116'));self.assertIn('inversion',r['pairing_status']);self.assertNotEqual(r['pairing_status'],'verified_exact')
 def test_TDB_airCotton20_residuetemperature_conflict_held(self):
  r=self.find(B,'TDBTZP_Cotton20_initial','air');self.assertEqual((r['R750_pct'],r['residue_temp_C']),('10.9','750'));self.assertIn('at700bodyversusS2/conclusion750',r['source_air_conflicts']);self.assertNotEqual(r['pairing_status'],'verified_exact')
 def test_TDB_standalone750_not_TGIR800_flow(self):
  for r in self.accepted():self.assertEqual((r['TG_start_C'],r['TG_end_C'],r['heating_rate_C_min']),('35','750','10'));self.assertIn('50mLminnotborrowed',r['source_TG_mass_pan_flow_repeats']);self.assertIn('notstandaloneTG851endpoint',r['source_TGIR_method'])
 def test_TDB_air_raw_Rmax_header_unit_not_inferred(self):
  r=self.find(B,'TDBTZP_Control_initial','air');self.assertEqual((r['Tmax1_C'],r['Tmax2_C'],r['source_Rmax_raw_header_C']),('336','446','1.04'));self.assertFalse(r['source_DTGmax_pct_per_C']);self.assertIn('notinferredpercentperC',r['source_Rmax_unit_conflict'])
 def test_TDB_uncertainty_type_and_LOI_dimensions(self):
  r=self.find(B,'TDBTZP_Cotton30_initial','N2');self.assertEqual((r['LOI_uncertainty_pct'],r['source_weight_gain_uncertainty_pct'],r['source_LOI_dimensions_mm']),('0.3','0.3','150x59'));self.assertIn('type/SD/SE/repeats unreported',r['source_uncertainty_type'])
 def test_TDB_control_rinse_not_invented(self):
  r=self.find(B,'TDBTZP_Control_initial','air');self.assertEqual(r['washing_state'],'initial_unwashed_control_preparation_unreported');r=self.find(B,'TDBTZP_Cotton10_initial','N2');self.assertIn('postcurerinseunreported',r['treatment_method'])
 def test_TDB_allfour_washed_LOI_no_initialTG(self):
  rows=[r for r in self.subset(B)if r['treatment_state']=='washed'];self.assertEqual([r['LOI_pct']for r in rows],['31.4','28.6','27.5','27.2'])
  for r in rows:self.noTG(r);self.assertIn('protocol_unreported',r['washing_state']);self.assertIn('noAATCCborrowed',r['source_washing_protocol'])
 def test_BPNM_four_TG_without_own_absoluteLOI(self):
  rows=[r for r in self.subset(C)if r['R700_pct']];self.assertEqual(len(rows),4)
  for r in rows:self.assertFalse(r['LOI_pct']);self.assertIn('absolute_LOI',r['pairing_status']);self.assertEqual(r['TG_end_C'],'800');self.assertEqual(r['residue_temp_C'],'700')
 def test_BPNM_weight_at_peak_not_final_residue(self):
  r=self.find(C,'BPNM_450gL_initial','air');self.assertEqual((r['source_weight_at_Tmax1_pct'],r['source_weight_at_Tmax2_pct'],r['R700_pct']),('70.8','36.6','23.5'));self.assertIn('notfinalTGresidue',r['source_weight_at_peak_definition'])
 def test_BPNM_relative_LOI_not_computed_to_absolute(self):
  for dose,rel,wg in [('50','88','11.25'),('450','127.8','14.81')]:
   r=self.find(C,'BPNM_'+dose+'gL_relative_LOI_fact');self.assertFalse(r['LOI_pct']);self.noTG(r);self.assertEqual((r['source_relative_LOI_improvement_pct'],r['source_weight_gain_wt_pct']),(rel,wg));self.assertIn('do notcompute',r['source_LOI_join_hold'])
 def test_BPNM_40point1_ratio_not_assigned450dose(self):
  r=self.find(C,'BPNM_ratio1to4_doseunreported');self.assertEqual(r['LOI_pct'],'40.1');self.noTG(r);self.assertIn('bathdoseunreported',r['composition']);self.assertNotEqual(r['pairing_status'],'verified_exact')
 def test_BPNM_after30LC_no_ownwashedTG(self):
  r=self.find(C,'BPNM_after30LC_dosejoinunreported');self.assertEqual(r['LOI_pct'],'30.5');self.noTG(r);self.assertIn('detailsunreported',r['washing_state']);self.assertIn('option/temp/time',r['source_washing_protocol'])
if __name__=='__main__':unittest.main(verbosity=2)
