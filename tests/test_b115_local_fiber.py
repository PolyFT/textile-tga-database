"""Protect same-form/wash/ramp matching and distinct TG temperature definitions."""
import csv
import sys
import unittest
from pathlib import Path
import pandas as pd

HERE=Path(__file__).resolve().parent
PRIVATE=HERE.name=='work'
R=HERE.parent/'repo' if PRIVATE else HERE.parent
INPUT=HERE/'staged-local-fiber-b115/publication_proposed.csv' if PRIVATE else R/'data/incoming/verified_source_batch_20261002_b115_local_fiber.csv'
sys.path.insert(0,str(R/'scripts'))
import pairing
import validate_tg_loi as v

class LocalFiberB115Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with INPUT.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def source(self,suffix):return [r for r in self.rows if r['DOI'].endswith(suffix)]
 def accepted(self,suffix):return [r for r in self.source(suffix) if r['pairing_status']=='verified_exact']
 def test_gases_do_not_multiply_independent_states(self):
  report=v.build_tables(pd.DataFrame(self.rows),v.issue_list())[3]
  self.assertEqual(report['errors'],[])
  self.assertEqual((report['verified_exact_sample_states'],report['verified_exact_condition_records']),(9,11))
  self.assertEqual(len(self.rows),69)
  self.assertEqual(sum(r['pairing_status']!='verified_exact' for r in self.rows),58)
 def test_silk_kelvin_conversion_is_not_rounded_to_r700(self):
  r=self.accepted('178929')[0]
  self.assertEqual((r['T10_C'],r['T50_C'],r['residue_temp_C']),('282.85','361.85','699.85'))
  self.assertEqual((r['source_T10_K'],r['source_T50_K'],r['source_residue_temperature_K']),('556','635','973'))
  self.assertFalse(r.get('R700_pct',''))
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,residue_temp_C='700')))
 def test_silk_lower_bound_is_not_an_exact_loi(self):
  rr=[r for r in self.source('178929') if r['pairing_status']!='verified_exact']
  self.assertEqual(len(rr),7)
  for r in rr:
   self.assertEqual(r['LOI_pct'],'')
   self.assertEqual(r['reviewed_measurement_fingerprint'],'')
   self.assertIn('>27.4',r['source_LOI_reported'])
 def test_lyocell_initial_loi_disagreement_is_held(self):
  rr=[r for r in self.source('03975-8') if r['source_LOI_abstract_pct']]
  self.assertEqual(len(rr),2)
  for r in rr:
   self.assertEqual((r['source_LOI_abstract_pct'],r['source_LOI_Table1_pct']),('44.6','40.6'))
   self.assertFalse(r['LOI_pct'])
   self.assertFalse(r['reviewed_measurement_fingerprint'])
 def test_lyocell_graphic_abstract_residue_is_not_silently_chosen(self):
  r=next(r for r in self.accepted('03975-8') if r['sample_state']=='Control lyocell fabric' and r['atmosphere']=='N2')
  self.assertEqual((r['source_R800_Table3_pct'],r['source_R800_graphical_abstract_pct']),('13.6','13.32'))
  self.assertFalse(r.get('R800_pct',''));self.assertFalse(r['residue_pct'])
  self.assertEqual(r['T10_C'],'313.1')
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,R800_pct='13.6')))
 def test_lyocell_discordant_source_peaks_remain_raw(self):
  for r in self.source('03975-8'):
   self.assertFalse(r.get('Tmax1_C',''))
   if r['source_Tmax_Table3_C']:self.assertIn('unresolved',r['source_Tmax_conflict'])
 def test_lyocell_native30lc_is_not_renamed150lc(self):
  rr=[r for r in self.accepted('03975-8') if r['source_washing_cycles']]
  self.assertEqual(len(rr),2)
  for r in rr:
   self.assertEqual((r['source_washing_cycles'],r['LOI_pct']),('30','31.3'))
   self.assertIn('After30 native',r['washing_state'])
   self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,washing_state='After150cycles')))
 def test_polyester_dta_and_unknown_residue_temperature_remain_raw(self):
  rr=self.accepted('1849-7');self.assertEqual(len(rr),4)
  for r in rr:
   self.assertFalse(r.get('Tmax1_C',''));self.assertFalse(r['residue_pct']);self.assertFalse(r['residue_temp_C'])
   self.assertTrue(r['source_Tdmax_Table2_C']);self.assertTrue(r['source_residual_Table2_wtpct'])
   self.assertIn('DTA(uV)',r['source_peak_measurement_conflict'])
   self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,residue_pct=r['source_residual_Table2_wtpct'],residue_temp_C='500')))
 def test_polyester_addon_denominator_is_treated_mass(self):
  for r in self.source('1849-7'):
   self.assertIn('(Wt-Wo)/Wt',r['source_addon_denominator'])
   self.assertIn('4to99',r['source_addon_prose_conflict'])
 def test_wool_moisture_peak_never_becomes_decomposition_peak(self):
  for r in self.accepted('7244-2'):
   self.assertEqual(r['source_Tmax1_moisture_C'],'64');self.assertFalse(r.get('Tmax1_C',''));self.assertFalse(r['Tonset_C'])
   self.assertTrue(r['Tmax2_C']);self.assertTrue(r['Tmax3_C'])
   self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,Tmax1_C='64')))
 def test_wool_wash_columns_have_no_loi_or_tg(self):
  rr=[r for r in self.source('7244-2') if r['source_washing_cycles']]
  self.assertEqual(len(rr),2)
  for r in rr:
   self.assertFalse(r['LOI_pct']);self.assertFalse(r['reviewed_measurement_fingerprint'])
   self.assertTrue(all(not r.get(k,'')for k in pairing.TG_FIELDS))
 def test_ag_lyocell_never_borrows_a_heating_rate(self):
  rr=self.source('04000-8');self.assertEqual(len(rr),19)
  self.assertTrue(all(r['pairing_status']!='verified_exact' for r in rr))
  tg=[r for r in rr if r['source_T5_Table1_C']];self.assertEqual(len(tg),6)
  for r in tg:
   self.assertFalse(r['heating_rate_C_min']);self.assertFalse(r['reviewed_measurement_fingerprint'])
   self.assertTrue(all(not r.get(k,'')for k in pairing.TG_FIELDS))
 def test_eadp_fiber_and_fabric_are_not_approved_as_same_form(self):
  rr=self.source('2005-y');self.assertEqual(len(rr),12)
  self.assertTrue(all(r['pairing_status']!='verified_exact' for r in rr))
  tg=[r for r in rr if r['source_T5_C']];self.assertEqual(len(tg),4)
  for r in tg:
   self.assertNotEqual(r['material_form_TGA'],r['material_form_LOI'])
   self.assertFalse(r['LOI_pct']);self.assertFalse(r['reviewed_measurement_fingerprint'])
   self.assertEqual(r['source_residue_temp_C'],'800' if r['atmosphere']=='N2' else '700')
 def test_source_review_facts_never_publish_private_paths(self):
  for r in self.rows:
   s=' '.join(r.values())
   for prefix in ['/'+'Volumes'+'/', '/'+'Users'+'/']:self.assertNotIn(prefix,s)
   self.assertTrue(r['source_url'].startswith('https://doi.org/'))

if __name__=='__main__':unittest.main()
