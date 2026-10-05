"""Protect own TG thresholds, field review binding and separate bulk/cone/DSC specimens."""
import csv,json,sys,unittest
from pathlib import Path
import pandas as pd
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));import pairing as p;import validate_tg_loi as v
with(R/'data/incoming/verified_source_batch_20261006_b319_local_material.csv').open(newline='')as f:ROWS=list(csv.DictReader(f))
def get(n):return next(r for r in ROWS if r['source_sample_label']==n)
class PPPA6Boundaries(unittest.TestCase):
 def test_five_paired_one_EG10_LOI_hold(self):
  master,_,_,report=v.build_tables(pd.DataFrame(ROWS));self.assertFalse(report['errors']);self.assertEqual((report['verified_exact_sample_states'],len(master)),(5,5));r=get('PP/PA6/EG10');self.assertEqual(r['LOI_pct'],'25.7');self.assertFalse(r['TG_locator']);self.assertFalse(r['T10_C']);self.assertTrue(p.evidence_issues(dict(r,pairing_status='verified_exact',direct_numeric_use='yes',Tmax1_C='481.7',R600_pct='9.9')))
  legacy=dict(get('PP/PA6/EG10'));legacy.pop('T30_C');self.assertTrue(all(not legacy.get(k,'') for k in p.TG_FIELDS));self.assertFalse(all(not dict(legacy,T30_C='470.1').get(k,'') for k in p.TG_FIELDS))
 def test_T30_review_binding_and_numeric_range(self):
  r=get('PP/PA6');self.assertIn('T30_C',p.TG_FIELDS);self.assertEqual((r['T10_C'],r['T30_C'],r['T50_C']),('454.1','470.1','478.2'));self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(dict(r,T30_C='471.1')));self.assertTrue(any('T30_C'in x for x in v.numeric_errors(pd.DataFrame([dict(r,T30_C='1600')]))))
 def test_T10_T30_T50_not_T5_or_onset(self):
  for r in ROWS:self.assertFalse(r['T5_C']);self.assertFalse(r['Tonset_C'])
  r=get('PP/PA6/nEG15');self.assertEqual((r['T10_C'],r['T30_C'],r['T50_C'],r['Tmax1_C']),('418.1','454.4','469.7','477.8'));self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(dict(r,T10_C='',Tonset_C='418.1')))
 def test_TG_R600_not_end700_or_cone_residue(self):
  r=get('PP/PA6/nEG15');self.assertEqual((r['R600_pct'],r['residue_temp_C'],r['TG_end_C']),('11.5','600','700'));self.assertFalse(r['R700_pct']);self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(dict(r,R600_pct='30.5',residue_pct='30.5')));self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(dict(r,R600_pct='',R700_pct='11.5',residue_temp_C='700')))
 def test_own_LOI_dimensions_not_UL94_cone_or_mechanical_replication(self):
  for r in ROWS:
   self.assertEqual((r['LOI_standard'],r['LOI_specimen_geometry']),('ASTMD2863-2013','120x6.5x3.2mm3'));self.assertFalse(r['TGA_mass_mg']);self.assertFalse(r['TGA_gas_flow_ml_min']);self.assertFalse(r['TGA_replicates']);self.assertFalse(r['LOI_replicates']);self.assertFalse(r['conditioning']);self.assertEqual((r['TG_start_C'],r['TG_end_C'],r['atmosphere'],r['heating_rate_C_min']),('20','700','N2','10'))
 def test_bulk_form_recipe_and_nEG_nominal_mass_not_silica(self):
  r=get('PP/PA6/nEG10');self.assertEqual(json.loads(r['source_raw_recipe_Table1'])['nEG_mass_pct'],'10');self.assertIn('unreported',r['composition']);self.assertIn('specimen_form_mismatch',p.evidence_issues(dict(r,material_form_LOI='woven PA6 fabric')));self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(dict(r,washing_state='after_50_cycles')))
if __name__=='__main__':unittest.main()
