"""Protect native TG metrics, wash-state matching and unresolved source conflicts."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import pairing
import validate_tg_loi as v
class LocalCottonB113Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with(R/'data/incoming/verified_source_batch_20261002_b113_local_2020_cotton.csv').open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def source(self,suffix):return[r for r in self.rows if r['DOI'].endswith(suffix)]
 def test_gas_records_do_not_double_unique_samples(self):
  report=v.build_tables(pd.DataFrame(self.rows),v.issue_list())[3]
  self.assertEqual(report['errors'],[]);self.assertEqual((report['verified_exact_sample_states'],report['verified_exact_condition_records']),(4,8));self.assertEqual(len(self.rows),69)
 def test_agatmpa_t10_is_not_t5_or_onset(self):
  for r in self.source('03003-1'):
   if r['pairing_status']=='verified_exact':
    self.assertNotEqual(r['T10_C'],'');self.assertEqual(r.get('T5_C',''),'');self.assertEqual(r['Tonset_C'],'')
    self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,T10_C='',T5_C=r['T10_C'])))
 def test_agatmpa_other_doses_have_no_curve_numbers(self):
  rr=[r for r in self.source('03003-1')if r['pairing_status']=='held_exact_LOI_graphonly_TG_not_digitized'];self.assertEqual(len(rr),4)
  for r in rr:self.assertNotEqual(r['LOI_pct'],'');self.assertTrue(all(not r.get(k,'')for k in pairing.TG_FIELDS));self.assertEqual(r['reviewed_measurement_fingerprint'],'')
 def test_all_washed_exact_loi_excludes_initial_tg_transfer(self):
  rr=[r for r in self.rows if r['pairing_status']=='held_washed_exact_LOI_no_own_TG'];self.assertEqual(len(rr),32)
  for r in rr:self.assertNotEqual(r['LOI_pct'],'');self.assertTrue(all(not r.get(k,'')for k in pairing.TG_FIELDS));self.assertEqual(r['reviewed_measurement_fingerprint'],'')
 def test_amhpe_air_residues_keep_their_temperatures(self):
  r=next(r for r in self.source('03064-2')if r['sample_state']=='30% AMHPE-treated cotton'and r['atmosphere']=='air')
  self.assertEqual(r['R700_pct'],'16.4');self.assertEqual(r['R800_pct'],'2.0');self.assertEqual(r['residue_temp_C'],'800');self.assertEqual(r['residue_pct'],'2.0')
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,residue_temp_C='700')))
 def test_amhpe_secondary_peak_is_char_oxidation(self):
  r=next(r for r in self.source('03064-2')if r['sample_state']=='Control cotton'and r['atmosphere']=='air')
  self.assertEqual(r['Tmax2_C'],'470.8');self.assertEqual(r['source_Tonset2_C'],'443.1');self.assertIn('charoxidation',r['source_Tmax_label'])
 def test_pbn_conflicting_char_and_water_peak_stay_raw(self):
  r=next(r for r in self.source('03063-3')if r['sample_state']=='Control sample')
  self.assertEqual(r['source_Ta_max_C'],'79.8');self.assertEqual(r['source_R900_native_pct'],'19.06');self.assertEqual(r['Tmax1_C'],'');self.assertEqual(r['residue_pct'],'')
  self.assertTrue(all(x['pairing_status']!='verified_exact'for x in self.source('03063-3')))
 def test_pbn_approximate_control_loi_not_exact(self):
  r=next(r for r in self.source('03063-3')if r['sample_state']=='Control sample');self.assertEqual(r['LOI_pct'],'');self.assertEqual(r['source_control_LOI_approximate_pct'],'~19.0')
 def test_hydrophobic_control_reuse_is_not_another_verified_sample(self):
  rr=[r for r in self.source('03057-1')if r['sample_state']=='C1'];self.assertEqual(len(rr),2)
  for r in rr:self.assertEqual(r['source_crosspaper_control_reuse_DOI'],'10.1016/j.matchemphys.2020.123656');self.assertNotEqual(r['pairing_status'],'verified_exact');self.assertEqual(r['reviewed_measurement_fingerprint'],'')
 def test_hydrophobic_residue_has_no_invented_fixed_endpoint(self):
  rr=[r for r in self.source('03057-1')if r['atmosphere']];self.assertEqual(len(rr),8)
  for r in rr:self.assertEqual(r['source_TG_end_method_C'],'600');self.assertEqual(r['residue_temp_C'],'');self.assertEqual(r['R700_pct'],'');self.assertEqual(r['R800_pct'],'');self.assertNotEqual(r['source_residue_native_pct'],'')
if __name__=='__main__':unittest.main()
