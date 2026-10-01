"""Protect atmosphere, washing, onset conflicts and unavailable supplement boundaries."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
H=Path(__file__).resolve().parent;P=H.name=='work';R=H.parent/'repo'if P else H.parent
F=H/'staged-local-textile-b119/publication_proposed.csv'if P else R/'data/incoming/verified_source_batch_20261002_b119_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing,validate_tg_loi as v
PH='10.1007/s10570-016-0928-8';UV='10.1007/s12221-017-7628-3';PA='10.1016/j.porgcoat.2020.105640'
class B119TextileTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def select(self,doi,sample,gas=None):return next(r for r in self.rows if r['DOI']==doi and r['sample_state']==sample and(gas is None or r.get('atmosphere')==gas))
 def test_four_states_not_eight_independent_pairs(self):
  q=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(q['errors']);self.assertEqual((q['verified_exact_sample_states'],q['verified_exact_condition_records']),(4,8));self.assertEqual(len(self.rows),46)
 def test_eight_original_gas_specific_vectors(self):
  expected={'Untreated':{'N2':('359','377','','6.6'),'air':('','384','556','1.1')},'5BL':{'N2':('329','355','','29.9'),'air':('334','360','555','10.4')},'10BL':{'N2':('317','351','','33.4'),'air':('314','356','537','16.6')},'20BL':{'N2':('309','344','','38.6'),'air':('311','332','','23.5')}}
  for sample,gs in expected.items():
   for gas,x in gs.items():
    r=self.select(PH,sample,gas);self.assertEqual(tuple(r.get(k,'')for k in ['Tonset_C','Tmax1_C','Tmax2_C','R600_pct']),x);self.assertFalse(pairing.evidence_issues(r));self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,atmosphere='air'if gas=='N2'else'N2')))
 def test_air_control_conflicting_onset_is_not_arbitrarily_resolved(self):
  r=self.select(PH,'Untreated','air');self.assertEqual((r['source_Tonset_Table1_reported_C'],r['source_Tonset_prose_reported_C']),('360','358'));self.assertFalse(r['Tonset_C']);self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,Tonset_C='360')))
 def test_generic_onset_is_not_five_percent_loss(self):
  r=self.select(PH,'5BL','N2');self.assertEqual(r['Tonset_C'],'329');self.assertFalse(r.get('T5_C'));self.assertFalse(r.get('T10_C'));self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,Tonset_C='',T5_C='329')))
 def test_variable_peak_residue_and_flame_char_are_not_tg600(self):
  r=self.select(PH,'20BL','N2');self.assertEqual((r['source_residue_at_Tmax_reported_pct'],r['R600_pct'],r['residue_temp_C']),('70.1','38.6','600'));self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,R600_pct='98.4',residue_pct='98.4')));self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,R600_pct='70.1',residue_pct='70.1')))
 def test_mcc_flow_and_rate_are_not_tg(self):
  for r in [r for r in self.rows if r['DOI']==PH]:self.assertEqual(r['heating_rate_C_min'],'10');self.assertEqual((r['source_TG_start_C'],r['TG_end_C']),('50','600'));self.assertFalse(r['source_TG_flow_mL_min']);self.assertFalse(r['LOI_sample_dimensions_mm']);self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,heating_rate_C_min='60')))
 def test_uv_six_missing_atmospheres_stay_held(self):
  rr=[r for r in self.rows if r['DOI']==UV and r['pairing_status']=='held_TG_atmosphere_unreported'];self.assertEqual(len(rr),6)
  for r in rr:self.assertEqual(r['source_TG_heating_rate_C_min'],'20');self.assertFalse(r['source_TG_atmosphere']);self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS));self.assertFalse(r.get('reviewed_measurement_fingerprint'))
 def test_uv_fourteen_washed_states_do_not_borrow_initial_tg(self):
  rr=[r for r in self.rows if r['DOI']==UV and r['source_washing_cycles']];self.assertEqual(len(rr),14)
  for r in rr:self.assertEqual(r['pairing_status'],'held_washed_LOI_no_own_TG');self.assertFalse(r.get('source_R600_reported_pct'));self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS))
 def test_crosslinker_loi_conflicts_remain_raw_and_unpaired(self):
  for sample,val in [('VPA20_AAm40_MBAAm','34'),('VPA20_AAm40_TAHT','36')]:
   r=next(r for r in self.rows if r['sample_state']==sample and not r['source_washing_cycles']);self.assertFalse(r['LOI_pct']);self.assertEqual((r['source_LOI_Table3_reported_pct'],r['source_LOI_prose_reported_pct']),('43',val));self.assertEqual(r['pairing_status'],'held_crosslinker_LOI_conflict_no_own_TG')
 def test_cited_unread_si_does_not_become_approved_complete_review(self):
  rr=[r for r in self.rows if r['DOI']==PA];self.assertEqual(len(rr),12)
  for r in rr:self.assertEqual(r['pairing_status'],'held_cited_official_SI_unreviewed');self.assertEqual(r['source_TG_heating_rate_C_min'],'20');self.assertFalse(r.get('source_TG_flow_mL_min'));self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS));self.assertFalse(r.get('reviewed_measurement_fingerprint'))
  r=next(r for r in rr if r['sample_state']=='PA6.6-g-AA-5BL'and r['source_TG_atmosphere']=='air');self.assertEqual((r['source_R700_reported_pct'],r['LOI_pct']),('4.73','23'))
if __name__=='__main__':unittest.main()
