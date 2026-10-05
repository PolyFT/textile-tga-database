"""Protect independent PET-cloth pairs from conflicting or misidentified auxiliary metrics."""
import csv,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));import pairing
with(ROOT/'data/incoming/verified_source_batch_20261005_b309_local_textile.csv').open(newline='')as f:DATA=list(csv.DictReader(f))
class PETSourceBoundaries(unittest.TestCase):
 def test_conflicting_AAm_residue_cannot_enter_fixed_temperature_fields(self):
  r=next(x for x in DATA if x['source_sample_label']=='PET-g-AAm')
  self.assertEqual((r['source_raw_Table1_R600'],r['source_body_R600']),('1.7','3.34'))
  for k in ['residue_pct','residue_temp_C','R600_pct']:self.assertFalse(r[k])
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,R600_pct='1.7')))
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,residue_pct='3.34',residue_temp_C='600')))
 def test_peak_step_and_threshold_identities_remain_distinct(self):
  for r in DATA:
   steps=json.loads(r['source_raw_Table2_Ti_Tm_Tf'])
   self.assertEqual([r['Tmax'+str(i+1)+'_C']for i in range(len(steps))],[x[1]for x in steps])
   for k in ['T5_C','T10_C','Tonset_C']:self.assertFalse(r[k])
   self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,T10_C=steps[0][0])))
  r=next(x for x in DATA if x['source_sample_label']=='PET-g-AAc')
  self.assertEqual((r['source_raw_AAc_body_initial_C'],json.loads(r['source_raw_Table2_Ti_Tm_Tf'])[0][0]),('242','194'))
  self.assertEqual(r['Tmax1_C'],'280')
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,Tmax1_C='160')))
 def test_complete_stage_metrics_keep_moisture_and_nonclosing_source_values_raw(self):
  data={r['source_sample_label']:json.loads(r['source_raw_Table1_stage_metrics'])for r in DATA}
  self.assertEqual([len(data[k])for k in ['PET','PET-g-AAc','PET-g-AAm','PET-g-DMVP']],[2,5,3,3])
  self.assertEqual(data['PET-g-AAc'][0]['temperature_range_C'],'50-160')
  self.assertEqual((data['PET-g-DMVP'][1]['mass_loss_pct'],data['PET-g-DMVP'][1]['end_residue_pct']),('63.02','27.6'))
  r=next(x for x in DATA if x['source_sample_label']=='PET-g-DMVP')
  self.assertTrue(r['source_step_mass_balance_flag']);self.assertEqual(r['R600_pct'],'3.95')
 def test_knit_preparation_and_unknown_methods_are_preserved(self):
  self.assertEqual(len({pairing.sample_state_id(r)for r in DATA}),4)
  for r in DATA:
   self.assertFalse(pairing.evidence_issues(r));self.assertEqual(r['material_form_TGA'],r['material_form_LOI'])
   self.assertEqual(r['atmosphere'],'air')
   for k in ['LOI_standard','LOI_replicates','TGA_mass_mg','TGA_pan','TGA_gas_flow_ml_min']:self.assertFalse(r[k])
   self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='isolated PET fibers')))
   self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,washing_state='washed20cycles')))
if __name__=='__main__':unittest.main()
