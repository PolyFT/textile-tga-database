"""Guard initial RTM state, nitrogen-only method scope, and resin-matrix loading."""
import csv,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if not (ROOT/'scripts/pairing.py').exists():ROOT=Path(__file__).resolve().parent.parent/'repo'
sys.path.insert(0,str(ROOT/'scripts'));import pairing
def rows():
 p=ROOT/'data/incoming/verified_source_batch_20261005_b286_local_textile.csv'
 if not p.exists():p=Path(__file__).resolve().parent/'staged-local-textile-b286/publication_proposed.csv'
 with p.open(newline='') as f:return list(csv.DictReader(f))
class ContinuousWovenGFPA6SourceBoundaries(unittest.TestCase):
 def test_ordinary_initial_N2_does_not_borrow_Soxhlet_TGIR_conditions(self):
  valid=[r for r in rows() if r['direct_numeric_use']=='yes'];self.assertEqual(len(valid),4);self.assertEqual(len({r['sample_state'] for r in valid}),4)
  for r in valid:
   self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['TG_start_C'],r['TG_end_C']),('nitrogen','10','30','600'));self.assertFalse(r.get('TGA_mass_mg'));self.assertFalse(r.get('TGA_gas_flow_ml_min'));self.assertFalse(r.get('TGA_pan'));self.assertIn('not_Soxhlet_extracted',r['washing_state']);self.assertEqual(r['material_form_TGA'],r['material_form_LOI']);self.assertIn('25-800C',r['source_separate_TGIR_conditions'])
   self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,washing_state='acetone_Soxhlet_extracted_24h')))
 def test_air_and_pure_powder_remain_outside_approved_pairs(self):
  held=[r for r in rows() if r['direct_numeric_use']=='no'];self.assertEqual(len(held),6)
  for r in held:self.assertFalse(r.get('reviewed_measurement_fingerprint'))
  air=[r for r in held if r['pairing_status']=='scientific_hold'];self.assertEqual(len(air),4)
  for r in air:
   self.assertFalse(r['atmosphere']);self.assertFalse(r['heating_rate_C_min']);self.assertEqual((r['source_raw_table_atmosphere'],r['source_raw_figure_atmosphere']),('air','oxygen'))
   self.assertTrue(pairing.evidence_issues(dict(r,pairing_status='verified_exact',direct_numeric_use='yes',atmosphere='air',heating_rate_C_min='10')))
  powder=[r for r in held if r['source_sample_label']=='HPCTP'];self.assertEqual(len(powder),2)
  for r in powder:self.assertFalse(r['LOI_pct']);self.assertEqual(r['material_category'],'non_textile')
 def test_T5_real_R600_and_matrix_loadings_do_not_become_other_metrics(self):
  for r in [r for r in rows() if r['direct_numeric_use']=='yes']:
   self.assertTrue(r['T5_C']);self.assertFalse(r.get('Tonset_C'));self.assertFalse(r.get('T10_C'));self.assertEqual(r['residue_temp_C'],'600');self.assertEqual(r['residue_pct'],r['R600_pct']);self.assertIn('WITHINresinmatrix',r['source_HPCTP_loading_basis']);self.assertEqual(r['source_approximate_glass_wt_percent'],'67');self.assertFalse(r['source_reported_glass_wt_percent'])
   self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,T5_C='',Tonset_C=r['T5_C'])))
   self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,residue_temp_C='800')))
  c=next(r for r in rows() if r['source_sample_label']=='GF/PA6/0%HPCTP' and r['direct_numeric_use']=='yes');self.assertEqual((c['LOI_pct'],c['T5_C'],c['Tmax1_C'],c['Tmax2_C'],c['R600_pct']),('27.2','376','430','','67.1'))
if __name__=='__main__':unittest.main()
