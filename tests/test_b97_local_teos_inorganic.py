"""Protect source-native thresholds, TG/muffle scope, gas counts and exact-state holds."""
import csv
import sys
import unittest
from pathlib import Path
import pandas as pd
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'scripts'))
import pairing
import validate_tg_loi as v

class LocalSolGelOriginalTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with(R/'data/incoming/verified_source_batch_20261001_b97_local_teos_inorganic.csv').open(newline='')as h:cls.rows=list(csv.DictReader(h))
  cls.teos=[r for r in cls.rows if r['DOI']=='10.1002/app.32954'];cls.oxide=[r for r in cls.rows if r['DOI']=='10.1016/j.carbpol.2011.10.032']
 def test_two_atmospheres_are_conditions_not_extra_samples(self):
  report=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3]
  self.assertEqual(report['errors'],[]);self.assertEqual(report['verified_exact_sample_states'],20);self.assertEqual(report['verified_exact_condition_records'],36);self.assertEqual(len(self.rows),37)
 def test_exact_nitrogen_residues_and_native_component_positions(self):
  values=[14,25,24,24,17,37,32,32,10,25,33,31,13,34,30,32];rows=[r for r in self.teos if r['atmosphere']=='nitrogen']
  self.assertEqual([float(r['R700_pct'])for r in rows],values)
  pet=next(r for r in rows if r['sample_state']=='PET');self.assertEqual(pet['source_T1_star_C'],'');self.assertEqual(pet['source_T2_star_C'],'440');self.assertEqual(pet['Tmax1_C'],'440');self.assertEqual(pet['Tmax2_C'],'')
 def test_air_third_component_is_not_an_onset_or_extra_sample(self):
  rows=[r for r in self.teos if r['atmosphere']=='air'];self.assertEqual([float(r['R700_pct'])for r in rows],[1,14,18,23,1,24,24,18,1,19,24,15,1,16,16,18])
  cot=next(r for r in rows if r['sample_state']=='COT');self.assertEqual(cot['source_T2_star_C'],'');self.assertEqual(cot['source_T3_star_C'],'501');self.assertEqual(cot['Tmax2_C'],'501');self.assertTrue(all(r.get('Tonset_C','')==''and r.get('T5_C','')==''for r in rows))
 def test_loi_table_rows_repeat_across_gases_without_estimation(self):
  expected=[21,22,22,22,20,22,22,22,22,23,23,23,21,22,22,22]
  for gas in ['air','nitrogen']:
   self.assertEqual([float(r['LOI_pct'])for r in self.teos if r['atmosphere']==gas],expected)
  self.assertTrue(all(r['LOI_standard']=='ISO4589-2;editionunknown'for r in self.teos))
 def test_five_percent_threshold_and_residue_endpoint_are_literal(self):
  self.assertEqual([float(r['T5_C'])for r in self.oxide],[316,315,293,284,296]);self.assertTrue(all(r.get('Tonset_C','')==''for r in self.oxide));self.assertEqual([float(r['residue_pct'])for r in self.oxide],[0,10,9,7,9]);self.assertTrue(all(r['residue_temp_C']=='750'and r['TG_end_C']=='800'for r in self.oxide))
 def test_muffle_and_vertical_residues_are_not_tg_measurements(self):
  self.assertEqual([float(r['source_muffle_residue1100C_pct'])for r in self.oxide],[0,5,4,4,4]);self.assertEqual([float(r['source_Table3_verticalburn_residue_pct'])for r in self.oxide],[10,30,31,21,32]);self.assertTrue(all(r.get('R800_pct','')==''and r.get('R1100_pct','')==''and r['source_muffle_duration_h']=='1'for r in self.oxide))
 def test_silica_heat_and_wash_scope_hold_never_receives_approval(self):
  si=next(r for r in self.oxide if r['sample_state']=='SiCO');self.assertIn('80C15h',si['treatment_method']);self.assertIn('100C30min',si['treatment_method']);self.assertIn('60C1h',si['treatment_method']);self.assertEqual(si['review_disposition'],'held_outside_verified_target');self.assertEqual(si.get('reviewed_measurement_fingerprint',''),'');self.assertNotEqual(si['pairing_status'],'verified_exact')
 def test_same_fabric_and_measurement_change_invalidates_approval(self):
  approved=[r for r in self.rows if r['pairing_status']=='verified_exact'];self.assertEqual(len(approved),36)
  for r in approved:self.assertEqual(r['material_form_TGA'],r['material_form_LOI']);self.assertEqual(pairing.evidence_issues(r),[])
  changed=dict(approved[0],LOI_pct='22.5');self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(changed));changed=dict(approved[0],atmosphere='air');self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(changed))

if __name__=='__main__':unittest.main()
