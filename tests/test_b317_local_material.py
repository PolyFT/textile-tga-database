"""Prevent borrowed assays, shifted merged gas columns and invented experimental conditions."""
import csv,json,sys,unittest
from pathlib import Path
import pandas as pd
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));import pairing as p;import validate_tg_loi as v
with(R/'data/incoming/verified_source_batch_20261006_b317_local_material.csv').open(newline='')as f:ROWS=list(csv.DictReader(f))
def get(doi,name,gas):return next(r for r in ROWS if r['DOI']==doi and r['source_sample_label']==name and r['atmosphere']==gas)
LD='10.1002/app.50317';PV='10.1002/vnl.22070'
class LDPEPVABoundaries(unittest.TestCase):
 def test_eleven_states_seventeen_records_seven_held(self):
  master,_,_,report=v.build_tables(pd.DataFrame(ROWS));self.assertFalse(report['errors']);self.assertEqual((report['verified_exact_sample_states'],len(master)),(11,17));self.assertEqual(len([r for r in ROWS if r['direct_numeric_use']=='no']),7)
 def test_two_residues_same_experiment_and_900_not_800(self):
  r=get(LD,'LDPE10','air');self.assertEqual((r['R600_pct'],r['R900_pct'],r['residue_pct'],r['residue_temp_C']),('29.68','27.89','27.89','900'));self.assertFalse(r['R800_pct']);self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(dict(r,residue_temp_C='800',R800_pct='27.89')))
 def test_LDPE15_POE_recipe_cannot_borrow_same_LOI_LDPE10_TG(self):
  r=get(LD,'LDPE15','air');self.assertEqual((r['LOI_pct'],json.loads(r['source_raw_recipe_Table1'])['POE']),('25.4','4'));self.assertFalse(r['Tmax1_C']);self.assertFalse(r['TG_locator']);self.assertTrue(p.evidence_issues(dict(r,pairing_status='verified_exact',direct_numeric_use='yes',Tmax1_C='490.2',T5_C='438')))
 def test_uncertainty_replicates_and_geometry_not_borrowed(self):
  for r in ROWS:
   self.assertFalse(r['TGA_replicates']);self.assertFalse(r['LOI_replicates']);self.assertFalse(r['TGA_mass_mg']);self.assertFalse(r['LOI_uncertainty_type'])
   if r['DOI']==LD:self.assertEqual((r['LOI_specimen_geometry'],r['LOI_standard']),('125x13x2.2mm','ASTM2863-97'));self.assertTrue(r['LOI_uncertainty_pct'])
   else:self.assertFalse(r['LOI_specimen_geometry']);self.assertFalse(r['LOI_standard']);self.assertFalse(r['TG_start_C']);self.assertFalse(r['TG_end_C'])
 def test_PVA_merged_headers_and_third_peak_slots(self):
  a=get(PV,'PVA','N2');b=get(PV,'PVA','air');self.assertEqual((a['T5_C'],a['T10_C'],a['T50_C'],a['Tmax1_C'],a['Tmax2_C'],a['Tmax3_C']),('233','269','321','318','433',''));self.assertEqual((b['T5_C'],b['T10_C'],b['T50_C'],b['Tmax1_C'],b['Tmax2_C'],b['Tmax3_C']),('147','259','360','317','419','485'));self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(dict(a,Tmax3_C='485')))
 def test_PVA_thresholds_water_DSC_PCFC_not_decomposition_onset(self):
  r=get(PV,'PVA','air');self.assertFalse(r['Tonset_C']);self.assertEqual(r['source_DSC_Tg_C'],'74');self.assertIn('adsorbedwater',r['source_metric_limits']);self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(dict(r,T5_C='',Tonset_C='147')));self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(dict(r,Tmax1_C='312')))
 def test_700_explicit_residue_not_component_800_or_program_endpoint(self):
  for r in [r for r in ROWS if r['DOI']==PV]:
   self.assertEqual(r['residue_temp_C'],'700');self.assertEqual(r['residue_pct'],r['R700_pct']);self.assertFalse(r['R800_pct']);self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(dict(r,R700_pct='',R800_pct=r['residue_pct'],residue_temp_C='800')))
 def test_actual_form_and_PZH4_only_preparation_example(self):
  for r in [r for r in ROWS if r['DOI']==PV]:
   self.assertEqual(r['year'],'2024');self.assertEqual(r['source_index_year'],'2023');self.assertEqual(bool(r['source_preparation_example']),r['source_sample_label']=='PZH4');self.assertIn('specimen_form_mismatch',p.evidence_issues(dict(r,material_form_LOI='woven PVA textile')));self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(dict(r,washing_state='after_50_laundering_cycles')))
if __name__=='__main__':unittest.main()
