"""Protect threshold/rate units and unreported program/condition boundaries."""
import csv,unittest
from pathlib import Path
def load_rows():
 repo=Path(__file__).resolve().parents[1];p=repo/'data/incoming/verified_source_batch_20261005_b262_local_textile.csv'
 if not p.exists():p=Path(__file__).resolve().parent/'staged-local-textile-b262/publication_proposed.csv'
 with p.open(newline='')as f:return list(csv.DictReader(f))
class GlassPA6AlkylphosphinateEvidence(unittest.TestCase):
 def test_raw_onset_is_threshold_and_rate_is_not_temperature(self):
  r=next(x for x in load_rows()if x['source_sample_label']=='PA6/30%GF')
  self.assertEqual((r['T5_C'],r['Tmax1_C'],r['source_peak_weight_loss_rate_pct_min']),('411','472','27'))
  for r in load_rows():
   self.assertEqual(r['T5_C'],r['source_raw_Tonset_C']);self.assertFalse(r.get('Tonset_C'));self.assertFalse(r.get('Tmax2_C'))
 def test_residue_endpoint_does_not_fill_program_or_molding_unknowns(self):
  for r in load_rows():
   self.assertEqual(r['residue_temp_C'],'700');self.assertEqual(r['R700_pct'],r['residue_pct'])
   for k in ['TG_start_C','TG_end_C','TGA_mass_mg','LOI_replicates']:self.assertFalse(r.get(k))
   self.assertIn('Moldingtemperature/pressure/timeunreported',r['source_preparation'])
 def test_mentioned_air_and_kinetics_curves_are_not_extra_records(self):
  rows=load_rows();self.assertEqual(len(rows),4);self.assertEqual(len({r['sample_state']for r in rows}),4)
  for r in rows:
   self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['TGA_gas_flow_ml_min']),('nitrogen','20','100'))
   self.assertEqual(r['material_form_TGA'],r['material_form_LOI']);self.assertIn('notcalculated',r['composition'])
if __name__=='__main__':unittest.main()
