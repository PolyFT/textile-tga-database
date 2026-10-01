"""Protect source residue conflicts, TG stages and unmatched durability states."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'scripts'))
import pairing
import validate_tg_loi as v

class APOSSCottonEvidenceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with(R/'data/incoming/verified_source_batch_20261001_b108_local_aposs.csv').open(newline='')as f:cls.rows=list(csv.DictReader(f))
  cls.approved=[r for r in cls.rows if r['pairing_status']=='verified_exact']
 def test_conditions_do_not_double_state_count(self):
  report=v.build_tables(pd.DataFrame(self.rows),v.issue_list())[3]
  self.assertEqual(report['errors'],[])
  self.assertEqual((report['verified_exact_sample_states'],report['verified_exact_condition_records']),(6,12))
 def test_conflicting_residue_stays_blank_with_other_tg(self):
  r=next(r for r in self.approved if r['sample_state']=='C3-PDMS-TiO2'and r['atmosphere']=='N2')
  self.assertEqual(r['source_R800_Table2_pct'],'33.6');self.assertEqual(r['source_R800_prose_p8_pct'],'33.7')
  for k in ['residue_pct','R800_pct','residue_temp_C']:self.assertEqual(r[k],'')
  self.assertEqual(r['T5_C'],'217');self.assertEqual(r['Tmax1_C'],'285.2')
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,residue_pct='33.6',residue_temp_C='800')))
 def test_air_second_stage_is_not_moisture(self):
  for r in self.approved:
   self.assertEqual(r.get('water_removal_peak_C',''),'')
   self.assertEqual(r.get('Tonset_C',''),'');self.assertEqual(r.get('T10_C',''),'')
   if r['atmosphere']=='N2':self.assertEqual(r['Tmax2_C'],'')
   else:self.assertNotEqual(r['Tmax2_C'],'')
 def test_t75_not_relabelled_as_t80(self):
  for r in self.approved:self.assertEqual(r.get('T80_C',''),'')
  r=next(r for r in self.approved if r['sample_state']=='C1'and r['atmosphere']=='N2')
  self.assertEqual(r['source_T75_C'],'632.6')
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,T80_C='632.6')))
 def test_loi_only_initial_and_washed_cannot_inherit_tg(self):
  held=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(held),3)
  self.assertEqual([(r['sample_state'],r['LOI_pct'])for r in held],[('Cotton-PDMS-TiO2','20'),('(C3)5','24'),('(C3-PDMS-TiO2)5','28')])
  for r in held:
   self.assertTrue(all(r.get(k,'')==''for k in pairing.TG_FIELDS));self.assertEqual(r['reviewed_measurement_fingerprint'],'')
 def test_wash_state_and_form_change_require_review(self):
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(self.approved[0],washing_state='5detergentwashes')))
  self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(self.approved[0],material_form_LOI='Cotton fibers')))
 def test_preparation_molarity_and_addon_are_distinct(self):
  for r in self.approved:self.assertEqual(r['source_combined_bath_concentration_resolved'],'')
  r=next(r for r in self.approved if r['sample_state']=='C1');self.assertEqual(r['source_Table1_APOSS_mol_L'],'0.067')
  self.assertIn('A-POSS1mmol',r['source_recipe_methods']);self.assertEqual(r['source_measured_weight_gain_pct_owf'],'5')
 def test_control_dash_and_missing_method_values_stay_missing(self):
  for r in self.approved:
   self.assertEqual(r['source_TG_mass_mg'],'');self.assertEqual(r['source_TG_flow'],'Unreported')
   self.assertEqual(r['source_TG_replicates'],'');self.assertEqual(r['source_LOI_replicates'],'')
   if r['sample_state']=='Pristine cotton':
    self.assertEqual(r['source_measured_weight_gain_pct_owf'],'');self.assertIn('pretreated control',r['source_recipe_methods'])
 def test_cone_residue_cannot_reuse_tg_review(self):
  r=next(r for r in self.approved if r['sample_state']=='C3-PDMS-TiO2'and r['atmosphere']=='air')
  self.assertEqual(r['R800_pct'],'16.2')
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,residue_pct='15.1',R800_pct='15.1')))

if __name__=='__main__':unittest.main()
