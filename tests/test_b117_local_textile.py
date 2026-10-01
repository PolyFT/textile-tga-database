"""Guard chemistry states, author labels and raw non-pair textile evidence."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
HERE=Path(__file__).resolve().parent;PRIVATE=HERE.name=='work';R=HERE.parent/'repo'if PRIVATE else HERE.parent
INPUT=HERE/'staged-local-textile-b117/publication_proposed.csv'if PRIVATE else R/'data/incoming/verified_source_batch_20261002_b117_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing;import validate_tg_loi as v
class LocalTextileB117Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with INPUT.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def source(self,suffix):return[r for r in self.rows if r['DOI'].endswith(suffix)]
 def test_six_new_states_are_pairs(self):
  p=v.build_tables(pd.DataFrame(self.rows),v.issue_list())[3];self.assertFalse(p['errors']);self.assertEqual((p['verified_exact_sample_states'],p['verified_exact_condition_records']),(6,6));self.assertEqual((len(self.rows),sum(r['pairing_status']!='verified_exact'for r in self.rows)),(47,41))
 def test_chlorinated_state_never_borrows_unactivated_threshold_or_addon(self):
  rr=self.source('02373-5');r=next(r for r in rr if r['sample_state'].endswith('-Cl'));u=next(r for r in rr if r['sample_state'].endswith('30'))
  self.assertEqual((r['LOI_pct'],r['Tmax1_C'],r['R600_pct']),('28.5','336','34'));self.assertFalse(r.get('T5_C'));self.assertFalse(r['source_initial_addon_pct']);self.assertEqual((u['T5_C'],u['LOI_pct'],u['R600_pct']),('291','29.8','37'))
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,T5_C='291')))
 def test_t5_definition_does_not_become_generic_onset(self):
  rr=[r for r in self.source('02373-5')if r.get('T5_C')];self.assertEqual(len(rr),2)
  for r in rr:self.assertFalse(r.get('Tonset_C'));self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,T5_C='',Tonset_C=r['T5_C'])))
 def test_author_label_pei_has_own_loi_and_nitrogen(self):
  r=next(r for r in self.source('02373-5')if r['sample_state']=='Cotton-PEI');self.assertEqual((r['LOI_pct'],r['Tmax1_C'],r['atmosphere']),('18.7','380','N2'));self.assertFalse(r.get('R600_pct'));self.assertIn('notduplicate',r['source_numeric_collision_adjudication']);self.assertFalse(pairing.evidence_issues(r));self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,LOI_pct='20.7',atmosphere='air')))
 def test_other_pcqs_layers_do_not_borrow_thirty_layer_tg(self):
  rr=[r for r in self.source('02373-5')if r['source_native_layer_label']in ['10','20']];self.assertEqual(len(rr),2)
  for r in rr:self.assertNotEqual(r['pairing_status'],'verified_exact');self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS));self.assertFalse(r.get('reviewed_measurement_fingerprint'))
 def test_casein_variable_temperature_residues_and_bound_stay_raw(self):
  rr=[r for r in self.source('8826-y')if r.get('source_native_Tonset10percent_Table1_C')];self.assertEqual(len(rr),7);self.assertEqual(rr[0]['source_R800_Table1_reported'],'<1')
  for r in rr:self.assertFalse(r['LOI_pct']);self.assertTrue(r['source_residue_at_Tmax1_Table1_pct']);self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS));self.assertFalse(r.get('reviewed_measurement_fingerprint'))
 def test_casein_washed_aged_abraded_burn_char_is_never_tg_or_loi(self):
  rr=[r for r in self.source('8826-y')if r.get('source_durability_kind')];self.assertEqual(len(rr),15)
  for r in rr:self.assertTrue(r['source_HMV_burn_residue_pct']);self.assertFalse(r['LOI_pct']);self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS));self.assertNotEqual(r['pairing_status'],'verified_exact')
 def test_atp_own_loi_and_native_washes_have_no_tg(self):
  rr=self.source('02709-1');self.assertEqual(len(rr),6);self.assertEqual(sum(bool(r['source_washing_cycles'])for r in rr),3)
  for r in rr:self.assertTrue(r['LOI_pct']);self.assertEqual(r['LOI_sample_dimensions_mm'],'58x150');self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS));self.assertFalse(r.get('reviewed_measurement_fingerprint'));self.assertNotEqual(r['pairing_status'],'verified_exact')
 def test_reused_generation_two_and_shared_control_never_add_pairs(self):
  rr=[r for r in self.source('03744-7')if r['source_prior_reuse_DOI']];self.assertEqual(len(rr),2)
  for r in rr:self.assertEqual(r['source_prior_reuse_DOI'],'10.1016/j.carbpol.2019.115648');self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS));self.assertNotEqual(r['pairing_status'],'verified_exact')
  self.assertEqual(next(r for r in rr if r['native_sample_label']=='HBPOPN2')['source_R800_reported_pct'],'31.4')
 def test_new_generations_keep_t10_main_peak_and_eight_hundred_residue(self):
  rr=[r for r in self.source('03744-7')if r['pairing_status']=='verified_exact'];self.assertEqual(len(rr),2)
  self.assertEqual({(r['native_sample_label'],r['LOI_pct'],r['T10_C'],r['Tmax1_C'],r['R800_pct'])for r in rr},{('HBPOPN3','42.7','252','307','33.1'),('HBPOPN4','43','247','290','34.8')})
  for r in rr:self.assertFalse(r.get('Tonset_C'));self.assertFalse(r.get('T5_C'));self.assertFalse(r.get('R600_pct'));self.assertEqual(r['residue_temp_C'],'800');self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,T10_C='',Tonset_C=r['T10_C'])))
 def test_all_nine_native_washed_generations_are_loi_only(self):
  rr=[r for r in self.source('03744-7')if r['source_washing_cycles']];self.assertEqual(len(rr),9)
  for r in rr:self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS));self.assertNotEqual(r['pairing_status'],'verified_exact');self.assertIn('homeequivalenceunreported',r['source_wash_method'])
if __name__=='__main__':unittest.main()
