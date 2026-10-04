"""Protect initial cotton measurements and exclude lower-bound changed states."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b174/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261004_b174_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing;import validate_tg_loi as v
class TextileB174Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def accepted(self):return[r for r in self.rows if r['pairing_status']=='verified_exact']
 def held(self):return[r for r in self.rows if r['pairing_status']!='verified_exact']
 def test_three_states_three_conditions_not_seven_pairs(self):q=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(q['errors']);self.assertEqual((len(self.rows),q['verified_exact_sample_states'],q['verified_exact_condition_records']),(7,3,3))
 def test_three_unique_own_initial_fabric_states(self):self.assertEqual({r['sample_state']for r in self.accepted()},{'SFC_Cotton_initial','SFC_FC_initial','SFC_SFC_initial'});self.assertTrue(all(r['washing_state']=='initial'for r in self.accepted()))
 def test_accepted_evidence_is_valid(self):self.assertTrue(all(not pairing.evidence_issues(r)for r in self.accepted()))
 def test_method_and_state_mutations_require_new_review(self):
  for r in self.accepted():
   for k,z in[('LOI_pct','99'),('Tmax1_C','555'),('residue_temp_C','700'),('heating_rate_C_min','10'),('washing_state','washed'),('sample_state','anotherrecipe')]:self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**{k:z})))
 def test_fiber_cannot_replace_fabric(self):
  for r in self.accepted():self.assertEqual(r['material_form_TGA'],r['material_form_LOI']);self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='fiber')))
 def test_native_SI_LOI_peak_and_residue(self):
  for r,e in zip(self.accepted(),[('18.2','380','19.5'),('31.1','326','44.5'),('30','319','34.8')]):self.assertEqual(tuple(r[k]for k in['LOI_pct','Tmax1_C','R600_pct']),e)
 def test_initial_decomposition_criterion_unknown_not_T5_T10_Tonset(self):self.assertEqual([r['source_initial_decomposition_temp_C']for r in self.accepted()],['305','253','253']);self.assertTrue(all(not r.get(k)for r in self.accepted()for k in['T5_C','T10_C','Tonset_C']))
 def test_ordinary_N2_ramp_and_explicit_residue_temperature(self):self.assertTrue(all(tuple(r[k]for k in['atmosphere','heating_rate_C_min','TG_start_C','TG_end_C','residue_temp_C'])==('N2','20','30','600','600')for r in self.accepted()))
 def test_VFT_char_and_surface_elements_not_TG_or_loading(self):self.assertTrue(all('VFTremainingmass.5/37.8/27.6notTGR60019.5/44.5/34.8'in r['source_ancillary_limit']for r in self.accepted()))
 def test_distinct_APP_and_sprayed_recipes(self):rr=self.accepted();self.assertEqual(len({r['treatment_method']for r in rr}),3);self.assertIn('APP50gL',rr[1]['treatment_method']);self.assertIn('FOCS.4g/ECA1.6g',rr[2]['treatment_method'])
 def test_unknown_flow_repeats_not_invented(self):self.assertTrue(all(r['source_TGA_flow_repetitions']=='unreported'for r in self.accepted()))
 def test_LOI_dimensions_and_repeats_not_VFT_or_contactangle(self):self.assertTrue(all('unreported;VFT78x300mm and contactangle3repetitions not LOI'in r['source_LOI_dimensions_repetitions']for r in self.accepted()))
 def test_reported_uncertainty_not_assumed_SD(self):self.assertEqual([r['LOI_uncertainty_pct']for r in self.accepted()],['','.4','.2']);self.assertTrue(all(r['LOI_uncertainty_type']=='unreported;notassumedSD'for r in self.accepted()))
 def test_issue_year_not_DOI_online_year(self):self.assertTrue(all(r['year']=='2022'and'online2021/11/13'in r['source_document_version']for r in self.rows))
 def test_four_changed_states_remain_excluded(self):self.assertEqual(len(self.held()),4);self.assertTrue(all(pairing.evidence_issues(r)for r in self.held()))
 def test_changed_states_have_no_own_TG(self):self.assertTrue(all(not r.get(k)for r in self.held()for k in pairing.TG_FIELDS))
 def test_LOI_bound29_is_not_measured29(self):self.assertTrue(all(not r['LOI_pct']and r['LOI_lower_bound_pct']=='29'and r['LOI_lower_bound_relation']=='strictly greater than as reported'and r['direct_numeric_use']=='no'for r in self.held()))
 def test_ultrasonic_minutes_not_laundering_cycles(self):self.assertTrue(any('conclusion says60cyclesbutmethods/results60min'in r['treatment_method']for r in self.held()))
 def test_age_abrasion_and_wash_are_separate_states(self):self.assertEqual({r['sample_state']for r in self.held()},{'SFC_SFC_after400abrasioncycles','SFC_SFC_after60minultrasonicwash','SFC_SFC_after60minUV','SFC_SFC_after60min180C'})
 def test_public_facts_have_no_private_locations(self):
  for r in self.rows:self.assertFalse(any(p in z for z in r.values()for p in['/'+'Users/','/'+'Volumes/','file'+':','smb'+':']))
if __name__=='__main__':unittest.main()
