"""Keep TG/LOI reviews distinct from water, MCC, cone and washed observations."""
import csv
import sys
import unittest
from pathlib import Path
import pandas as pd
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'scripts'))
import pairing
import validate_tg_loi as v

class PEIHCCPFePEvidenceTests(unittest.TestCase):
 source_file=R/'data/incoming/verified_source_batch_20261001_b105_local_peihccp_fep.csv'
 @classmethod
 def setUpClass(cls):
  with cls.source_file.open(newline='') as f:cls.rows=list(csv.DictReader(f))
  cls.approved=[r for r in cls.rows if r['pairing_status']=='verified_exact']
 def test_gas_conditions_do_not_double_count_treated_samples(self):
  report=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3]
  self.assertEqual(report['errors'],[])
  self.assertEqual((report['verified_exact_sample_states'],report['verified_exact_condition_records']),(6,9))
 def test_control_reuse_excludes_both_gas_conditions(self):
  control=[r for r in self.rows if r['sample_state']=='Cotton']
  self.assertEqual(len(control),2)
  for r in control:
   self.assertEqual(r['pairing_status'],'cross_source_control_reuse_pending')
   self.assertEqual(r['source_control_comparator_DOI'],'10.1007/s10570-021-03874-y')
   self.assertEqual(r['reviewed_measurement_fingerprint'],'')
 def test_tg_only_pei_control_does_not_inherit_cotton_loi(self):
  row=next(r for r in self.rows if r['sample_state']=='Cotton-P10')
  self.assertEqual(row['LOI_pct'],'')
  self.assertEqual(row['pairing_status'],'held_TG_only_no_own_LOI')
  self.assertEqual(row['Tmax1_C'],'337')
 def test_wash_states_have_no_transferred_initial_tg_or_loi(self):
  washed=[r for r in self.rows if r['treatment_state']=='Afterdurabilitylaundering']
  self.assertEqual(len(washed),5)
  for row in washed:
   self.assertEqual(row['LOI_pct'],'')
   self.assertTrue(all(row.get(k,'')=='' for k in pairing.TG_FIELDS))
   self.assertEqual(row['reviewed_measurement_fingerprint'],'')
 def test_cone_residue_is_not_tg_residue(self):
  fep=[r for r in self.approved if r['DOI'].endswith('0003-4')]
  self.assertEqual([r['R800_pct'] for r in fep],['9.9','33.3','35.1'])
  for row in fep:self.assertEqual(row['residue_temp_C'],'800')
  washed=next(r for r in self.rows if r['sample_state']=='FeP/APP/PEI-4BL-10LCs')
  self.assertEqual(washed['source_CCT_char_pct'],'6.92')
  self.assertEqual(washed['residue_pct'],'')
 def test_air_curves_and_unreported_treated_thresholds_stay_blank(self):
  for row in self.rows:
   if row['DOI'].endswith('0003-4') and row['atmosphere']=='air':
    self.assertTrue(all(row.get(k,'')=='' for k in pairing.TG_FIELDS))
    self.assertNotEqual(row['pairing_status'],'verified_exact')
  for row in self.approved:
   if row['DOI'].endswith('0003-4'):
    self.assertEqual(row.get('T5_C',''),'')
    if row['sample_state']!='Uncoated':self.assertEqual(row['Tmax1_C'],'')
 def test_neat_scraped_polymer_is_not_a_textile_pair(self):
  row=next(r for r in self.rows if r['material_category']=='nontextile_component')
  self.assertEqual(row['LOI_pct'],'')
  self.assertEqual(row['R700_pct'],'66')
  self.assertEqual(row['material_form_LOI'],'')
  self.assertNotEqual(row['pairing_status'],'verified_exact')
 def test_regular_tg_methods_and_native_unusual_units_preserved(self):
  for row in self.approved:
   self.assertEqual(row['material_form_TGA'],row['material_form_LOI'])
   if row['DOI'].endswith('03047-3'):
    self.assertEqual(row['source_TG_mass_mg'],'10')
    self.assertEqual(row['heating_rate_C_min'],'10')
    self.assertIn('60mL/s',row['source_TG_flow'])
    self.assertEqual(row.get('source_TG_flow_mL_min',''),'')
    self.assertIn('preheat100C',row['limitations'])
   else:self.assertEqual(row['heating_rate_C_min'],'20')
 def test_substituting_mcc_temperature_invalidates_review(self):
  row=next(r for r in self.approved if r['sample_state']=='Cotton-P10H5')
  altered=dict(row,Tmax1_C='321.5')
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(altered))
 def test_substituting_cone_residue_invalidates_review(self):
  row=next(r for r in self.approved if r['sample_state']=='FeP/APP/PEI-4BL')
  altered=dict(row,residue_pct='18.80',R800_pct='18.80')
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(altered))
 def test_condition_change_cannot_reuse_numeric_review(self):
  row=self.approved[0]
  self.assertEqual(pairing.evidence_issues(row),[])
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(row,heating_rate_C_min='20')))
 def test_fiber_fabric_transfer_is_rejected(self):
  self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(self.approved[0],material_form_LOI='Cotton fibers')))

if __name__=='__main__':unittest.main()
