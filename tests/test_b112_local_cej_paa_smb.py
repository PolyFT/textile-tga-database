"""Guard source/state attribution and unresolved original-paper metadata."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import pairing
import validate_tg_loi as v
class LocalCottonB112Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with(R/'data/incoming/verified_source_batch_20261001_b112_local_cej_paa_smb.csv').open(newline='')as f:cls.rows=list(csv.DictReader(f))
 @classmethod
 def source(cls,doi):return[r for r in cls.rows if r['DOI']==doi]
 def test_unique_wash_states_and_gas_conditions_are_distinct(self):
  report=v.build_tables(pd.DataFrame(self.rows),v.issue_list())[3]
  self.assertEqual(report['errors'],[]);self.assertEqual((report['verified_exact_sample_states'],report['verified_exact_condition_records']),(7,10));self.assertEqual(len(self.rows),76)
 def test_cej_intermediate_silver_doses_do_not_borrow_loi(self):
  rr=self.source('10.1016/j.cej.2019.05.012');h=[r for r in rr if 'held_intermediate'in r['pairing_status']];self.assertEqual(len(h),6)
  for r in h:self.assertEqual(r['LOI_pct'],'');self.assertEqual(r['reviewed_measurement_fingerprint'],'');self.assertNotEqual(r['T5_C'],'')
 def test_cej_air_second_peak_is_char_oxidation(self):
  r=next(r for r in self.source('10.1016/j.cej.2019.05.012')if r['sample_state']=='Pure cotton'and r['atmosphere']=='air')
  self.assertEqual(r['Tmax2_C'],'424.87');self.assertEqual(r['R800_pct'],'0.99');self.assertEqual(r.get('water_removal_peak_C',''),'')
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,Tmax2_C='')))
 def test_cej_regular_tg_mass_is_not_coupled_tgir_mass(self):
  r=next(r for r in self.rows if r['sample_state']=='Cotton-8BL-4AgNW'and r['atmosphere']=='N2')
  self.assertEqual(r['heating_rate_C_min'],'20');self.assertEqual(r['source_TG_flow_mL_min'],'50');self.assertEqual(r['source_TG_mass_mg'],'');self.assertIn('About8mg',r['source_TG_mass_reported'])
  self.assertEqual(r['T5_C'],'248.62');self.assertEqual(r.get('T10_C',''),'');self.assertEqual(r.get('Tonset_C',''),'')
 def test_cej_durability_emi_has_no_initial_tg_loi_transfer(self):
  h=[r for r in self.rows if 'held_durability_EMI'in r['pairing_status']];self.assertEqual(len(h),3)
  for r in h:self.assertEqual(r['LOI_pct'],'');self.assertTrue(all(not r.get(k,'')for k in pairing.TG_FIELDS))
 def test_paa_relative_improvement_does_not_create_absolute_control_char(self):
  rr=self.source('10.1016/j.carbpol.2018.10.113');h=[r for r in rr if r['pairing_status']!='verified_exact'];self.assertEqual(len(h),6)
  for r in h:self.assertNotEqual(r['LOI_pct'],'');self.assertEqual(r['residue_pct'],'');self.assertEqual(r['reviewed_measurement_fingerprint'],'')
 def test_paa_exact_residue_endpoint_and_feed_basis(self):
  r=next(r for r in self.rows if r['sample_state']=='PAA/1.0%ATP');self.assertEqual(r['R600_pct'],'19.56');self.assertEqual(r['LOI_pct'],'22.7');self.assertEqual(r['heating_rate_C_min'],'10');self.assertEqual(r['source_ATP_feed_pct'],'1');self.assertIn('feedratio',r['source_ATP_percent_basis'])
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,residue_temp_C='800')))
 def test_smb_washed_state_keeps_own_loi_and_r700(self):
  rr=self.source('10.1007/s10570-019-02371-7');a=[r for r in rr if r['pairing_status']=='verified_exact'];self.assertEqual(len(a),3)
  r=next(r for r in a if r['sample_state']=='SMB T.C/Washed');self.assertEqual(r['LOI_pct'],'23.6');self.assertEqual(r['R700_pct'],'18.4');self.assertEqual(r['atmosphere'],'air')
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,LOI_pct='28.5')))
 def test_smb_conflicting_peak_metadata_remains_raw(self):
  r=next(r for r in self.rows if r['sample_state']=='SMB T.C/Washed');self.assertEqual(r['Tmax1_C'],'');self.assertEqual(r['source_SI_Tmax_native_C'],'360.9');self.assertEqual(r['source_SI_MLR_native_pct'],'-5.0');self.assertEqual(r.get('residue_at_Tmax_pct',''),'')
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,Tmax1_C='360.9')))
 def test_smb_washing_loss_is_not_remaining_addon_or_cone_char(self):
  r=next(r for r in self.rows if r['sample_state']=='SMB T.C/Washed');self.assertEqual(r['source_washing_weight_loss_pct'],'9.4');self.assertEqual(r['source_initial_addon_pct_owf'],'18.6');self.assertIn('notremainingaddon',r['source_washing_weight_loss_basis'])
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,R700_pct='20.2',residue_pct='20.2')))
 def test_asgtmpa_conflicting_regular_conditions_not_repaired_by_tgir(self):
  rr=self.source('10.1007/s10570-018-02241-8');self.assertEqual(len(rr),33)
  for r in rr:self.assertNotEqual(r['pairing_status'],'verified_exact');self.assertEqual(r['reviewed_measurement_fingerprint'],'')
  pair=[r for r in rr if r['sample_state']=='30% ASGTMPA'];self.assertEqual({r['atmosphere']for r in pair},{'air','N2'})
  for r in pair:self.assertEqual(r['heating_rate_C_min'],'');self.assertEqual(r['source_regular_TG_heating_rate_native_K_min'],'20')
 def test_dctp_missing_tg_gas_not_borrowed_from_mcc(self):
  rr=self.source('10.1007/s12221-020-9442-6');self.assertEqual(len(rr),17)
  for r in rr:self.assertNotEqual(r['pairing_status'],'verified_exact');self.assertEqual(r['atmosphere'],'');self.assertEqual(r['reviewed_measurement_fingerprint'],'')
  r=next(r for r in rr if r['sample_state']=='D30+T5.4');self.assertEqual(r['Tmax1_C'],'286');self.assertEqual(r['R600_pct'],'40.6');self.assertEqual(r['LOI_pct'],'39')
  washed=[r for r in rr if 'after'in r['sample_state']];self.assertEqual(len(washed),4)
  for r in washed:self.assertTrue(all(not r.get(k,'')for k in pairing.TG_FIELDS))
if __name__=='__main__':unittest.main()
