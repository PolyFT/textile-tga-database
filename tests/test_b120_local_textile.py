"""Protect dose mapping, native DTG order and unresolved residue description."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
H=Path(__file__).resolve().parent;P=H.name=='work';R=H.parent/'repo'if P else H.parent
F=H/'staged-local-textile-b120/publication_proposed.csv'if P else R/'data/incoming/verified_source_batch_20261002_b120_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing,validate_tg_loi as v
class PNSiB120Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def test_batch_counts_distinct_states_and_gas_conditions(self):
  q=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(q['errors']);self.assertEqual((q['verified_exact_sample_states'],q['verified_exact_condition_records']),(4,7));self.assertEqual(len(self.rows),41)
 def test_control_is_not_catalyst_only_cotton(self):
  c=next(r for r in self.rows if r['sample_state']=='CO');ca=next(r for r in self.rows if r['sample_state']=='CO-FR(0)');self.assertEqual((c['LOI_pct'],ca['LOI_pct']),('18.4','22.5'));self.assertEqual((c['source_NaH2PO2_bath_g_L'],ca['source_NaH2PO2_bath_g_L']),('0','50'));self.assertTrue(all(not ca.get(k)for k in pairing.TG_FIELDS));self.assertFalse(pairing.evidence_issues(c))
 def test_native_t5_is_not_generic_onset(self):
  r=next(r for r in self.rows if r['sample_state']=='CO');self.assertEqual(r['T5_C'],'309.8');self.assertFalse(r.get('Tonset_C'));self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,T5_C='',Tonset_C='309.8')))
 def test_sole_dtg_peak_keeps_native_table_column(self):
  r=next(r for r in self.rows if r['sample_state']=='CO');self.assertEqual(r['Tmax2_C'],'361.8');self.assertFalse(r['Tmax1_C']);self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,Tmax1_C='139.2')))
 def test_control_residue_description_conflict_remains_raw(self):
  r=next(r for r in self.rows if r['sample_state']=='CO');self.assertEqual(r['source_R700_reported_pct'],'15.9');self.assertFalse(r['R700_pct']);self.assertFalse(r['residue_pct']);self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,R700_pct='15.9',residue_temp_C='700')))
 def test_duplicate_native_label_keeps_distinct_reported_dose(self):
  rr=[r for r in self.rows if r['native_sample_label']=='CO-FR(100)'];self.assertEqual(len(rr),2);self.assertEqual({r['source_FR_bath_g_L']for r in rr},{'100','200'});self.assertEqual({r['LOI_pct']for r in rr},{'29.9','31'});self.assertTrue(all(r['pairing_status']!='verified_exact'for r in rr))
 def test_generic_tg_never_becomes_150g_per_litre_pair(self):
  r=next(r for r in self.rows if r['sample_state']=='FR-treated-unspecified-dose');self.assertEqual((r['source_T5_reported_C'],r['source_R700_reported_pct']),('248.5','37.9'));self.assertFalse(r['LOI_pct']);self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS));self.assertFalse(r['source_FR_bath_g_L'])
 def test_neat_flame_retardant_has_no_textile_loi(self):
  r=next(r for r in self.rows if r['sample_state']=='FR-isolated-solid');self.assertEqual(r['source_R700_reported_pct'],'41.9');self.assertFalse(r['LOI_pct']);self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS));self.assertFalse(r['material_form_LOI'])
 def test_cydp_30percent_conflicting_loi_stays_unpaired(self):
  rr=[r for r in self.rows if r['DOI']=='10.1007/s10570-019-02608-5'and r['sample_state']=='Cotton-FR30percent'];self.assertEqual(len(rr),2)
  for r in rr:self.assertEqual((r['source_LOI_Table3_pct'],r['source_LOI_abstract_pct']),('52.0','52.9'));self.assertFalse(r['LOI_pct']);self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS));self.assertNotEqual(r['pairing_status'],'verified_exact')
 def test_cydp_control_t5_t10_and_native_tmax_remain_distinct(self):
  r=next(r for r in self.rows if r['DOI']=='10.1007/s10570-019-02608-5'and r['sample_state']=='Control-cotton'and r['atmosphere']=='air');self.assertEqual((r['T5_C'],r['T10_C'],r['Tmax1_C']),('283.5','318.1','298.2'));self.assertFalse(r['Tonset_C']);self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,Tmax1_C='398.2')))
 def test_cydp_nitrogen_has_no_borrowed_air_temperatures(self):
  r=next(r for r in self.rows if r['DOI']=='10.1007/s10570-019-02608-5'and r['pairing_status']=='verified_exact'and r['atmosphere']=='N2');self.assertEqual((r['char_pct'],r['char_temp_C'],r['heating_rate_C_min']),('8.5','700','20'));self.assertFalse(r['T5_C']);self.assertFalse(r['T10_C']);self.assertFalse(r['Tmax1_C']);self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,T5_C='283.5')))
 def test_cydp_gas_identity_and_zero_air_residue(self):
  rr=[r for r in self.rows if r['DOI']=='10.1007/s10570-019-02608-5'and r['pairing_status']=='verified_exact'];self.assertEqual({r['atmosphere']:float(r['char_pct'])for r in rr},{'air':0,'N2':8.5});self.assertTrue(all(not pairing.evidence_issues(r)for r in rr))
 def test_cydp_wash50_conflict_retains_both_original_values(self):
  r=next(r for r in self.rows if r['sample_state']=='Cotton-FR30percent-LC50');self.assertEqual((r['source_LOI_Table3_pct'],r['source_LOI_abstract_pct']),('27.9','27.2'));self.assertFalse(r['LOI_pct']);self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS))
 def test_cydp_washed_records_do_not_borrow_initial_tg(self):
  rr=[r for r in self.rows if r['DOI']=='10.1007/s10570-019-02608-5'and r.get('source_native_LC')];self.assertEqual(len(rr),15);self.assertEqual({r['source_native_LC']for r in rr},{'10','20','30','40','50'});self.assertTrue(all(r['pairing_status']!='verified_exact'and all(not r.get(k)for k in pairing.TG_FIELDS)for r in rr))
 def test_cited_literature_comparison_samples_not_new_own_states(self):
  rr=[r for r in self.rows if r['DOI']=='10.1007/s10570-019-02608-5'];self.assertFalse(any(r['sample_state']in['5BL','10BL','15BL','COT-PSi5.4','COT-PSi9.4','COT-PSi18.7']for r in rr))
 def test_dtsp_air_residue_is_not_nitrogen_peak_or_cone_residue(self):
  r=next(r for r in self.rows if r['DOI']=='10.1007/s10570-019-02465-2'and r['sample_state']=='Cotton-DTSP-30'and r['atmosphere']=='air');self.assertEqual((r['char_pct'],r['char_temp_C']),('17.5','800'));self.assertFalse(r['T5_C']);self.assertFalse(r['Tmax1_C']);self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,char_pct='17.97',residue_pct='17.97')))
 def test_dtsp_nitrogen_native_t5_not_onset_and_peak_residue_not_final(self):
  r=next(r for r in self.rows if r['DOI']=='10.1007/s10570-019-02465-2'and r['sample_state']=='Cotton-DTSP-30'and r['atmosphere']=='N2');self.assertEqual((r['T5_C'],r['Tmax1_C'],r['char_pct'],r['source_residue_at_Tmax_pct']),('269','315','40','75.2'));self.assertFalse(r['Tonset_C']);self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,char_pct='75.2',residue_pct='75.2')))
 def test_dtsp_bath_loading_and_fabric_weight_gain_differ(self):
  rr=[r for r in self.rows if r['DOI']=='10.1007/s10570-019-02465-2'and r['sample_state']=='Cotton-DTSP-30'];self.assertEqual(len(rr),2);self.assertTrue(all(r['source_DTSP_bath_wt_pct']=='30'and r['source_WG_pct']=='16'for r in rr))
 def test_dtsp_preparation_rinse_is_not_durability_wash(self):
  rr=[r for r in self.rows if r['DOI']=='10.1007/s10570-019-02465-2'and r['pairing_status']=='verified_exact'];self.assertEqual(len(rr),4);self.assertTrue(all('0durabilitycycles'in r['washing_state']for r in rr));held=[r for r in self.rows if r['DOI']=='10.1007/s10570-019-02465-2'and r['source_native_LC']in['5','10','15','20']];self.assertEqual(len(held),4);self.assertTrue(all(all(not r.get(k)for k in pairing.TG_FIELDS)for r in held))
 def test_all_held_facts_stay_outside_approved_pair_target(self):
  rr=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(rr),34);self.assertTrue(all(r['review_disposition']=='held_outside_verified_target'and all(not r.get(k)for k in pairing.TG_FIELDS)for r in rr))
if __name__=='__main__':unittest.main()
