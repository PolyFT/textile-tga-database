"""Protect original stage numbering, metric-specific holds and same-state pairing."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'scripts'))
import pairing
import validate_tg_loi as v

class CottonSiloxaneEvidenceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with(R/'data/incoming/verified_source_batch_20261001_b101_local_cotton_siloxane.csv').open(newline='')as h:cls.rows=list(csv.DictReader(h))
  cls.pn=[r for r in cls.rows if r['DOI']=='10.1007/s12221-018-7874-z']
  cls.gn=[r for r in cls.rows if r['DOI']=='10.1007/s12221-019-9008-7']
  cls.cyclic=[r for r in cls.rows if r['DOI']=='10.1002/app.47280']
  cls.pre=[r for r in cls.rows if r['DOI']=='10.1007/s10570-019-02327-x']
 def test_four_approved_states_and_conditions_only(self):
  rep=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3]
  self.assertEqual(rep['errors'],[])
  self.assertEqual((rep['verified_exact_sample_states'],rep['verified_exact_condition_records']),(4,4))
  self.assertEqual(len(self.rows),37)
 def test_residue_conflict_is_not_selected_or_averaged(self):
  r=next(r for r in self.pn if '350g/L'in r['sample_state'])
  self.assertEqual(r['pairing_status'],'verified_exact')
  self.assertEqual((r['source_R800_table_pct'],r['source_R800_prose_pct']),('14.76','14.67'))
  for k in ['residue_pct','R800_pct','residue_temp_C']:self.assertEqual(r[k],'')
  self.assertEqual((r['Tonset_C'],r['Tmax1_C'],r['Tmax2_C']),('203.44','204.95','333.78'))
 def test_source_control_stage_two_peak_is_not_shifted(self):
  r=next(r for r in self.pn if r['sample_state']=='Pure cotton fabric')
  self.assertEqual(r['Tmax1_C'],'')
  self.assertEqual(r['Tmax2_C'],'381.16')
  self.assertEqual((r['residue_pct'],r['residue_temp_C']),('6.59','800'))
 def test_lower_bath_states_do_not_inherit_optimized_tg(self):
  loionly=[r for r in self.pn+self.gn if r['pairing_status']=='LOI_only_no_matching_TG']
  self.assertEqual(len(loionly),7)
  for r in loionly:
   self.assertTrue(all(r.get(k,'')==''for k in pairing.TG_FIELDS))
   self.assertEqual(r['reviewed_measurement_fingerprint'],'')
 def test_washed_states_do_not_inherit_initial_tg(self):
  washed=[r for r in self.rows if r['pairing_status']=='LOI_only_washed_no_matching_TG']
  self.assertEqual(len(washed),12)
  for r in washed:self.assertTrue(all(r.get(k,'')==''for k in pairing.TG_FIELDS));self.assertEqual(r['reviewed_measurement_fingerprint'],'')
 def test_air_methods_and_second_onsets_remain_distinct(self):
  r=next(r for r in self.gn if r['pairing_status']=='verified_exact'and'250g/L'in r['sample_state'])
  self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['source_TG_flow_mL_min']),('air','10','20'))
  self.assertEqual((r['Tonset_C'],r['source_Tonset_stage2_C']),('241','330'))
  self.assertEqual((r['Tmax1_C'],r['Tmax2_C'],r['R800_pct']),('281','535','29.0'))
  self.assertEqual(r.get('T5_C',''),'');self.assertEqual(r.get('T10_C',''),'')
  self.assertNotIn('122g/m2',r['material_form_TGA'])
 def test_supporting_information_and_pre_metric_holds_remain_excluded(self):
  for r in self.cyclic+self.pre:self.assertNotEqual(r['pairing_status'],'verified_exact');self.assertEqual(r['reviewed_measurement_fingerprint'],'')
  control=next(r for r in self.pre if r['sample_state']=='Control cotton'and r['source_TG_program']=='air_dynamic')
  self.assertEqual((control['LOI_pct'],control['source_LOI_other_printed_control_pct']),('18.5','18'))
  n2=next(r for r in self.pre if r['sample_state']=='PRE400g/L cotton'and r['source_TG_program']=='N2_dynamic')
  self.assertEqual(n2['heating_rate_C_min'],'')
  self.assertEqual(n2['source_Fig4_mass_remaining_temperature_pairs'],'216C92%;283C73%;331C42%;383C37%')
  self.assertTrue(all(n2.get(k,'')==''for k in pairing.TG_FIELDS))
 def test_same_state_review_fingerprint_rejects_changed_measurement(self):
  approved=[r for r in self.rows if r['pairing_status']=='verified_exact']
  for r in approved:self.assertEqual(pairing.evidence_issues(r),[]);self.assertEqual(r['material_form_TGA'],r['material_form_LOI'])
  r=dict(approved[0],LOI_pct='19.5');self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(r))

if __name__=='__main__':unittest.main()
