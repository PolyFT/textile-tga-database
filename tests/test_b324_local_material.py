"""Regressions for whole GFPA6T source tables, measurement definitions and form/state."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));import pairing as p;import validate_tg_loi as v
with(ROOT/'data/incoming/verified_source_batch_20261006_b324_local_material.csv').open(newline='')as f:ROWS=list(csv.DictReader(f))
class SourceBoundaries(unittest.TestCase):
 def test_nine_original_whole_material_states(self):
  master,_,_,report=v.build_tables(pd.DataFrame(ROWS));self.assertFalse(report['errors']);self.assertEqual((len(master),report['verified_exact_sample_states']),(9,9));self.assertEqual(sorted(float(r['LOI_pct'])for r in ROWS),[23.2,26.6,28.5,28.9,29.5,30.9,38.6,39.8,40.1])
 def test_T5_mass_loss_and_DTG_temperatures_review_bound(self):
  for r in ROWS:
   self.assertFalse(r.get('Tonset_C'));self.assertFalse(r.get('T10_C'))
   for k in ['T5_C','Tmax1_C']:
    self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(dict(r,**{k:str(float(r[k])+1)})));self.assertTrue(any(k in e for e in v.numeric_errors(pd.DataFrame([dict(r,**{k:'1600'})]))))
 def test_measured_residue_not_theory_or_cone(self):
  r=ROWS[0];self.assertEqual((r['R700_pct'],r['source_theoretical_R700_pct']),('35.3','35'))
  self.assertNotEqual(float(r['R700_pct']),36.7)
  for r in ROWS:
   self.assertEqual(r['residue_temp_C'],'700');self.assertEqual(r['R700_pct'],r['residue_pct']);self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(dict(r,residue_temp_C='600')))
 def test_unknown_replicates_not_cone_or_EDS_replication(self):
  for r in ROWS:
   self.assertFalse(r['TGA_replicates']);self.assertFalse(r['LOI_replicates']);self.assertIn('uncertaintytypeandreplicationnotdefined',r['source_TG_uncertainty_definition']);self.assertEqual((r['LOI_standard'],r['LOI_specimen_geometry']),('ASTMD2863-97','130.0x6.5x3.2mm'))
 def test_own_Q50_conditions_not_PyGC(self):
  for r in ROWS:
   self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['TG_start_C'],r['TG_end_C']),('N2','10','20','700'));self.assertEqual((r['TGA_gas_flow_mL_min'],r['TGA_pan']),('60','Al2O3'));self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(dict(r,atmosphere='helium',heating_rate_C_min='1000')))
 def test_glass_composite_bulk_and_whole_loading(self):
  for r in ROWS:
   self.assertEqual(r['source_base_glass_wt_pct'],'35');self.assertEqual(r['material_scope_class'],'fiber_forming_polymer_composite');self.assertIn('specimen_form_mismatch',p.evidence_issues(dict(r,material_form_LOI='woven glass fibre fabric')));self.assertIn('material_scope_review_pending_or_stale',p.evidence_issues(dict(r,composition='pure isolated glass fibres')))
 def test_atmosphere_is_condition_not_new_state(self):
  r=ROWS[0];other=dict(r,atmosphere='air');self.assertEqual(p.sample_state_id(r),p.sample_state_id(other));self.assertNotEqual(p.measurement_fingerprint(r),p.measurement_fingerprint(other));self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(other))
if __name__=='__main__':unittest.main()
