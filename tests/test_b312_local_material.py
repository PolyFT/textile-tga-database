"""Source-derived boundaries for moulded PA1012 specimens, assay definitions and conflict holds."""
import csv,sys,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));import pairing as p;import validate_tg_loi as v
import pandas as pd
with(R/'data/incoming/verified_source_batch_20261005_b312_local_material.csv').open(newline='')as f:ROWS=list(csv.DictReader(f))
class PA1012ScientificBoundaries(unittest.TestCase):
 def test_exact_source_grid_and_two_conflict_holds(self):
  accepted=[r for r in ROWS if r['pairing_status']=='verified_exact'];master,_,_,report=v.build_tables(pd.DataFrame(ROWS));self.assertEqual((len(accepted),len(master),report['verified_exact_sample_states']),(3,3,3));self.assertEqual({r['source_sample_label']for r in accepted},{'PA1012','PA1012/H3PMo12O40','PA1012/PMo+Li-POSS'})
  holds=[r for r in ROWS if r['pairing_status']=='source_conflict_held'];self.assertEqual(len(holds),2);self.assertTrue(all(p.evidence_issues(r)for r in holds))
  li=next(r for r in holds if r['source_sample_label']=='PA1012/Li-Ph-POSS');self.assertIn('PA1010',li['source_raw_TableS1_recipe']);self.assertEqual(li['LOI_pct'],'25.1')
  hybrid=next(r for r in holds if r['source_sample_label']=='PA1012/PMo@Li-POSS');self.assertEqual((hybrid['LOI_pct'],hybrid['source_raw_LOI_abstract']),('26.3','26.2'));self.assertEqual(hybrid['LOI_uncertainty_pct'],'0.1')
 def test_threshold_and_TG_residue_cannot_be_relabelled(self):
  r=next(r for r in ROWS if r['source_sample_label']=='PA1012');self.assertEqual((r['T5_C'],r['Tmax1_C'],r['R800_pct']),('423','465','1.9'));self.assertFalse(r['Tonset_C']);self.assertFalse(r['T10_C'])
  for changed in [dict(T5_C='',Tonset_C='423'),dict(R800_pct='1.34'),dict(residue_temp_C='500')]:self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(dict(r,**changed)))
 def test_precursor_scope_does_not_mix_forms_or_postfire_state(self):
  for r in [r for r in ROWS if r['pairing_status']=='verified_exact']:
   self.assertEqual(r['material_form_TGA'],r['material_form_LOI']);self.assertIn('bulk',r['material_form_TGA']);self.assertFalse(p.evidence_issues(r));self.assertIn('specimen_form_mismatch',p.evidence_issues(dict(r,material_form_LOI='wet-spun PA1012 textile fibres')));self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(dict(r,washing_state='furnace500C5min')))
 def test_air_TGFTIR_and_DSC_metadata_are_not_ordinary_TG(self):
  for r in [r for r in ROWS if r['pairing_status']=='verified_exact']:
   self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['TG_start_C'],r['TG_end_C']),('N2','10','40','800'));self.assertFalse(r['TGA_gas_flow_ml_min']);self.assertFalse(r['TGA_mass_mg']);self.assertFalse(r['TGA_replicates']);self.assertFalse(r['LOI_replicates']);self.assertFalse(r['LOI_uncertainty_type']);self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(dict(r,atmosphere='air')))
 def test_changed_matrix_recipe_invalidates_material_review(self):
  r=next(r for r in ROWS if r['source_sample_label']=='PA1012/H3PMo12O40');self.assertEqual(r['material_scope_class'],'fiber_forming_polymer_composite');self.assertIn('material_scope_review_pending_or_stale',p.evidence_issues(dict(r,composition='PA1010/H3PMo12O40 alternate matrix')))
if __name__=='__main__':unittest.main()
