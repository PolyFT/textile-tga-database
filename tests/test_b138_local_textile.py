"""Protect unclassified TG labels, washing conflicts and stacked textile identity."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b138/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261003_b138_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing,validate_tg_loi as v
A='10.1002/pat.6162';B='10.1016/j.carbpol.2014.11.007';C='10.1016/j.polymdegradstab.2009.02.009'
class TextileB138Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def source(self,d):return[r for r in self.rows if r['DOI']==d]
 def exact(self,d,s):return next(r for r in self.source(d)if r['sample_state']==s and r['pairing_status']=='verified_exact')
 def reject(self,r,**kw):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**kw)))
 def test_sixstates_sixconditions_not35facts(self):
  z=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(z['errors']);self.assertEqual((z['verified_exact_sample_states'],z['verified_exact_condition_records']),(6,6));self.assertEqual(len(self.rows),35)
 def test_twenty_nine_holds_no_canonical_tg(self):
  rr=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(rr),29);self.assertTrue(all(all(not r.get(k,'')for k in pairing.TG_FIELDS)for r in rr))
 def test_jute_four_composites_not_six_fabrics(self):
  rr=[r for r in self.source(A)if r['pairing_status']=='verified_exact'];self.assertEqual(len(rr),4);self.assertTrue(all('Film-stacked'in r['material_form']for r in rr));self.assertEqual({r['LOI_pct']for r in rr},{'20','35.5','23.5','34.1'})
 def test_jute_control_conflicting_labels_raw_only(self):
  r=self.exact(A,'PLA/F');self.assertFalse(r['T1_C']);self.assertFalse(r['Tmax1_C']);self.assertEqual((r['source_raw_Table5_Td1_pct_C'],r['source_raw_Table5_Tmax_C']),('292','373'));self.assertEqual(r['R700_pct'],'6.5');self.reject(r,T1_C='373')
 def test_jute_700char_not730programend(self):
  r=self.exact(A,'FRPLA/PC-F');self.assertEqual((r['R700_pct'],r['residue_temp_C'],r['TG_end_C']),('19.3','700','730'));self.reject(r,residue_temp_C='730')
 def test_jute_t1_native_not_t5_or_t10(self):
  r=self.exact(A,'FRPLA/F');self.assertEqual((r['T1_C'],r['Tmax1_C']),('281','370'));self.assertFalse(r['T5_C']);self.assertFalse(r['T10_C']);self.reject(r,T1_C='',T5_C='281')
 def test_jute_n2_not_air(self):
  r=self.exact(A,'PLA/PC-F');self.assertEqual(r['atmosphere'],'N2');self.reject(r,atmosphere='air')
 def test_jute_rate20_not_mlr1_3(self):
  r=self.exact(A,'FRPLA/PC-F');self.assertEqual((r['heating_rate_C_min'],r['source_raw_MLR_pct_per_C']),('20','1.3'));self.reject(r,heating_rate_C_min='1.3')
 def test_jute_composite_pan_not_borrowed_from_fabric(self):
  r=self.exact(A,'PLA/F');self.assertIn('Unreportedforcomposites',r['source_TG_pan_flow']);self.assertIn('notborrowedfiberalumina',r['source_TG_pan_flow']);self.assertEqual(r['source_TG_mass_mg'],'5-10');self.assertIn('maintainstackedstructure',r['source_TG_specimen_preparation'])
 def test_jute_free_fabric_tg_without_loi(self):
  rr=[r for r in self.source(A)if r['sample_state']in ['F','PC-F']];self.assertEqual(len(rr),2);self.assertTrue(all(not r['LOI_pct']and r['pairing_status']!='verified_exact'for r in rr));self.assertEqual({r['source_raw_Table2_R700_pct']for r in rr},{'15.3','22.9'})
 def test_chitosan_all20_held_and2015_volume(self):
  rr=self.source(B);self.assertEqual(len(rr),20);self.assertTrue(all(r['pairing_status']!='verified_exact'and r['year']=='2015'for r in rr))
 def test_chitosan_shp6_loi23_not_shp4_tg(self):
  r=next(r for r in self.source(B)if r['sample_state']=='ChitP6BTCA4SHP6Ti9');self.assertEqual(r['LOI_pct'],'23');self.assertEqual(r['source_SHP_wt_bath_pct'],'6');self.assertFalse(r['Tmax1_C']);q=next(r for r in self.source(B)if r['sample_state']=='ChitP6BTCA4SHP4Ti9');self.assertFalse(q['LOI_pct']);self.assertEqual(q['source_SHP_wt_bath_pct'],'4')
 def test_chitosan_weightloss_no_fixed_temp_char_conversion(self):
  r=next(r for r in self.source(B)if r['sample_state']=='ControlCotton');self.assertEqual(r['source_raw_weight_loss_pct'],'66.6');self.assertFalse(r['R600_pct']);self.assertFalse(r['residue_temp_C']);self.assertEqual(r['source_raw_weight_loss_temperature'],'Unreported')
 def test_depolymerized_chitosan_not_phosphate(self):
  rr=[r for r in self.source(B)if r['sample_state'].startswith('DepChit')];self.assertEqual(len(rr),2);self.assertTrue(all(not r['LOI_pct']and'without_own_LOI'in r['pairing_status']for r in rr))
 def test_chitosan_washing_count_conflict_not_selected(self):
  self.assertTrue(all('5cyclesversus10'in r['washing_state']for r in self.source(B)))
 def test_pa66_only_two_appi_initialgroups(self):
  rr=[r for r in self.source(C)if r['pairing_status']=='verified_exact'];self.assertEqual(len(rr),2);self.assertEqual({r['sample_state']for r in rr},{'IFR2PA66','IFR4PA66'});self.assertEqual({r['LOI_pct']for r in rr},{'27.5','27.9'})
 def test_pa66_750char24_not800_or_lowerbound13(self):
  r=self.exact(C,'IFR2PA66');self.assertEqual((r['R750_pct'],r['residue_temp_C'],r['TG_end_C']),('24','750','800'));self.assertFalse(r['R800_pct']);self.reject(r,residue_temp_C='800');self.reject(r,R750_pct='13',residue_pct='13')
 def test_pa66_firstwater120_not_max310(self):
  r=self.exact(C,'IFR4PA66');self.assertEqual(r['Tmax1_C'],'310');self.assertFalse(r['Tonset_C']);self.assertFalse(r['T5_C']);self.assertFalse(r['R750_pct']);self.assertIn('120',r['source_water_loss_interval_C']);self.reject(r,Tmax1_C='120')
 def test_pa66_appii_andcontrol_not_paired(self):
  rr=[r for r in self.source(C)if r['sample_state']in ['IFR5PA66','IFR6PA66','IFR7PA66','IFR8PA66']];self.assertEqual(len(rr),4);self.assertTrue(all(not r['Tmax1_C']and r['pairing_status']!='verified_exact'for r in rr));q=next(r for r in self.source(C)if r['sample_state']=='ControlPA66');self.assertFalse(q['LOI_pct']);self.assertEqual(q['source_raw_Tmax_C'],'410')
 def test_wrong_form_rate_or_gas_rejected(self):
  r=self.exact(C,'IFR4PA66');self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['source_TG_mass_mg']),('air','10','2-3'));self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_LOI='Cotton fabric')));self.assertTrue(pairing.evidence_issues(dict(r,heating_rate_C_min='0')));self.reject(r,atmosphere='N2')
if __name__=='__main__':unittest.main()
