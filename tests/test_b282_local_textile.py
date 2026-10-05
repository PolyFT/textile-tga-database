"""Guard stock loading, defined thresholds, and excluded powder conflicts."""
import csv,unittest
from pathlib import Path
def rows():
 p=Path(__file__).resolve().parents[1]/'data/incoming/verified_source_batch_20261005_b282_local_textile.csv'
 if not p.exists():p=Path(__file__).resolve().parent/'staged-local-textile-b282/publication_proposed.csv'
 with p.open(newline='')as f:return list(csv.DictReader(f))
class GlassPETCeriumEvidence(unittest.TestCase):
 def test_stock_GF15_is_not_assigned_as_final_loading(self):
  valid=[r for r in rows()if r['direct_numeric_use']=='yes'];self.assertEqual(len(valid),8);self.assertEqual(len({r['sample_state']for r in valid}),4)
  for r in valid:
   self.assertEqual(r['source_input_PET_GF_stock_glass_wt_percent'],'15');self.assertFalse(r['source_reported_glass_wt_percent']);self.assertEqual(r['source_antioxidant_wt_percent'],'0.3');self.assertIn('notrenormalized',r['composition']);self.assertEqual(r['material_form_TGA'],r['material_form_LOI'])
 def test_defined_thresholds_and_real_R700_not_MCC_or_program_end(self):
  valid=[r for r in rows()if r['direct_numeric_use']=='yes']
  for r in valid:
   for k in ['T5_C','T10_C','T50_C']:self.assertTrue(r[k])
   self.assertFalse(r.get('Tonset_C'));self.assertEqual(r['residue_temp_C'],'700');self.assertEqual(r['TG_end_C'],'800');self.assertEqual(r['residue_pct'],r['R700_pct']);self.assertEqual(r['heating_rate_C_min'],'20');self.assertFalse(r.get('TGA_mass_mg'));self.assertFalse(r.get('TGA_gas_flow_ml_min'))
   if r['atmosphere']=='nitrogen':self.assertFalse(r.get('Tmax2_C'))
  c=next(r for r in valid if r['source_sample_label']=='PET'and r['atmosphere']=='air');self.assertEqual((c['T5_C'],c['T10_C'],c['T50_C'],c['Tmax1_C'],c['Tmax2_C'],c['R700_pct']),('388','401','442','439','560','16.0'))
 def test_powder_and_conflicting_R700_never_count_as_pairs(self):
  held=[r for r in rows()if r['direct_numeric_use']=='no'];self.assertEqual(len(held),2)
  for r in held:self.assertEqual(r['source_sample_label'],'CeHPP');self.assertFalse(r.get('LOI_pct'));self.assertFalse(r.get('reviewed_measurement_fingerprint'));self.assertEqual(r['pairing_status'],'pending_source_review')
  n=next(r for r in held if r['atmosphere']=='nitrogen');self.assertEqual((n['R700_pct'],n['source_raw_R700_prose_pct']),('72.6','71.9'))
if __name__=='__main__':unittest.main()
