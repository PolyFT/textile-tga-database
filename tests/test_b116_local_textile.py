"""Regression guards for original numerical conflicts and unpaired textile states."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
HERE=Path(__file__).resolve().parent
PRIVATE=HERE.name=='work'
R=HERE.parent/'repo'if PRIVATE else HERE.parent
INPUT=HERE/'staged-local-textile-b116/publication_proposed.csv'if PRIVATE else R/'data/incoming/verified_source_batch_20261002_b116_local_textile.csv'
sys.path.insert(0,str(R/'scripts'))
import pairing
import validate_tg_loi as v

class LocalTextileB116Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with INPUT.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def source(self,suffix):return[r for r in self.rows if r['DOI'].endswith(suffix)]
 def accepted(self,suffix):return[r for r in self.source(suffix)if r['pairing_status']=='verified_exact']
 def test_gas_conditions_never_multiply_sample_count(self):
  p=v.build_tables(pd.DataFrame(self.rows),v.issue_list())[3]
  self.assertEqual(p['errors'],[])
  self.assertEqual((p['verified_exact_sample_states'],p['verified_exact_condition_records']),(6,10))
  self.assertEqual((len(self.rows),sum(r['pairing_status']!='verified_exact'for r in self.rows)),(102,92))
 def test_vcfr_control_residue_conflict_stays_raw(self):
  r=self.accepted('03218-2')[0]
  self.assertEqual((r['source_R800_Table2_pct'],r['source_R800_prose_pct']),('14','13.6'))
  self.assertFalse(r['residue_pct']);self.assertFalse(r['R800_pct'])
  self.assertEqual((r['T5_C'],r['T50_C'],r['Tmax1_C'],r['heating_rate_C_min']),('294','339','338','15'))
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,R800_pct='14')))
 def test_washed_loi_is_never_matched_to_initial_tg(self):
  rr=[r for r in self.rows if float(r.get('source_washing_cycles')or 0)>0]
  self.assertEqual(len(rr),68)
  for r in rr:
   self.assertNotEqual(r['pairing_status'],'verified_exact')
   self.assertFalse(r['reviewed_measurement_fingerprint'])
   self.assertTrue(all(not r.get(k,'')for k in pairing.TG_FIELDS))
 def test_addtmpa_char_temperature_is_600_not_700(self):
  for r in self.accepted('02374-4'):
   self.assertEqual((r['residue_temp_C'],r['TG_end_C'],r['heating_rate_C_min'],r['source_TG_flow_mL_min']),('600','700','10','60'))
   self.assertTrue(r['R600_pct']);self.assertFalse(r['R700_pct']);self.assertTrue(r['T10_C']);self.assertFalse(r['T5_C']);self.assertFalse(r.get('Tonset_C',''))
   self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,residue_temp_C='700')))
 def test_addtmpa_second_air_peak_is_char_oxidation(self):
  r=next(r for r in self.accepted('02374-4')if r['sample_state']=='Control cotton'and r['atmosphere']=='air')
  self.assertEqual((r['Tmax1_C'],r['Tmax2_C'],r['R600_pct']),('355.0','472.5','0'))
  self.assertIn('charoxidation',r['source_Tmax_role'])
 def test_other_addtmpa_doses_do_not_borrow_30percent_tg(self):
  rr=[r for r in self.source('02374-4')if r['source_bath_concentration_pct']in['5','10','15','20','25']]
  self.assertEqual(len(rr),25)
  for r in rr:self.assertTrue(all(not r.get(k,'')for k in pairing.TG_FIELDS))
  five=next(r for r in rr if r['source_bath_concentration_pct']=='5'and not r['source_washing_cycles'])
  self.assertEqual(five['LOI_pct'],'30.3')
 def test_native_laundry_units_are_preserved(self):
  r=next(r for r in self.source('02374-4')if r['source_bath_concentration_pct']=='30'and r['source_washing_cycles']=='20')
  self.assertEqual(r['LOI_pct'],'29.11');self.assertIn('After20nativeLC',r['washing_state']);self.assertIn('oneLC=5home',r['washing_state'])
 def test_adgp_dose_and_endpoint_conflicts_preclude_pairs(self):
  rr=self.source('02751-z');self.assertEqual(len(rr),14);self.assertFalse(self.accepted('02751-z'))
  tg=[r for r in rr if r['source_R800_prose_pct']];self.assertEqual(len(tg),2)
  for r in tg:
   self.assertEqual((r['source_method_end_C'],r['source_residue_temperature_C']),('700','800'))
   self.assertFalse(r['LOI_pct']);self.assertTrue(all(not r.get(k,'')for k in pairing.TG_FIELDS))
 def test_b5_nitrogen_treated_residue_not_silently_resolved(self):
  r=next(r for r in self.accepted('02886-z')if r['source_bath_concentration_wtpct']=='40'and r['atmosphere']=='N2')
  self.assertEqual((r['source_R700_Table3_and_conclusion_pct'],r['source_R700_prose_pct']),('42.03','40.03'))
  self.assertFalse(r['R700_pct']);self.assertFalse(r['residue_pct']);self.assertFalse(r['residue_temp_C'])
  self.assertEqual((r['T10_C'],r['Tmax1_C'],r['LOI_pct']),('232.15','302.61','46.5'))
 def test_b5_other_doses_and_all_washes_lack_own_tg(self):
  rr=[r for r in self.source('02886-z')if r['pairing_status']!='verified_exact'];self.assertEqual(len(rr),17)
  self.assertEqual(sum(bool(r['LOI_pct'])for r in rr),17)
  for r in rr:self.assertTrue(all(not r.get(k,'')for k in pairing.TG_FIELDS))
 def test_ramie_vertical_burning_and_mcc_are_not_loi(self):
  rr=self.source('1408-y');self.assertEqual(len(rr),5)
  for r in rr:
   self.assertFalse(r['LOI_pct']);self.assertFalse(r['reviewed_measurement_fingerprint']);self.assertTrue(r['source_T5_Table1_C'])
   self.assertTrue(all(not r.get(k,'')for k in pairing.TG_FIELDS))
 def test_amhmpa_approximate_control_loi_and_undefined_tg_dose_held(self):
  rr=self.source('2018.05.085');self.assertEqual(len(rr),24);self.assertFalse(self.accepted('2018.05.085'))
  control=next(r for r in rr if r['source_LOI_reported'])
  self.assertEqual(control['source_LOI_reported'],'about16.0%');self.assertFalse(control['LOI_pct'])
  for r in rr:
   self.assertIn('AcceptedManuscript',r['source_document_version']);self.assertFalse(r['reviewed_measurement_fingerprint'])
   self.assertTrue(all(not r.get(k,'')for k in pairing.TG_FIELDS))
 def test_modified_evidence_fingerprints_reject_gas_form_and_rate_changes(self):
  for r in self.rows:
   if r['pairing_status']=='verified_exact':
    self.assertFalse(pairing.evidence_issues(r))
    for change in [dict(atmosphere='He'),dict(heating_rate_C_min='100')]:
     self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**change)))
    self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_LOI='bulk resin')))
 def test_public_facts_have_only_public_source_locations(self):
  for r in self.rows:
   for prefix in ['/'+'Volumes'+'/', '/'+'Users'+'/']:self.assertNotIn(prefix,' '.join(r.values()))
   self.assertTrue(r['source_url'].startswith('https://doi.org/'))

if __name__=='__main__':unittest.main()
