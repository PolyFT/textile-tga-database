"""Guard percentage-loss definition, real residue, and source-label ambiguity."""
import csv,unittest
from pathlib import Path
def load_rows():
 repo=Path(__file__).resolve().parents[1];p=repo/'data/incoming/verified_source_batch_20261005_b276_local_textile.csv'
 if not p.exists():p=Path(__file__).resolve().parent/'staged-local-textile-b276/publication_proposed.csv'
 with p.open(newline='')as f:return list(csv.DictReader(f))
class LongGlassPA6ClayEvidence(unittest.TestCase):
 def test_author_onset_definition_is_T10_not_T5(self):
  valid=[r for r in load_rows()if r['direct_numeric_use']=='yes'];self.assertEqual(len(valid),6)
  for r in valid:
   self.assertEqual(r['T10_C'],r['source_raw_Tonset_C']);self.assertFalse(r.get('T5_C'));self.assertFalse(r.get('Tonset_C'));self.assertFalse(r.get('Tmax2_C'))
   self.assertIn('10percentweightloss',r['source_raw_Tonset_definition'])
 def test_real_whole_R800_not_calculated_char_or_component_powder(self):
  by={r['source_sample_label']:r for r in load_rows()};self.assertEqual(by['LGFPA6/OP15/OMMT5']['R800_pct'],'27.3')
  self.assertEqual(by['LGFPA6/OP15/MMT5']['R800_pct'],'28.2')
  for r in load_rows():
   if r['direct_numeric_use']=='yes':
    self.assertEqual(r['residue_pct'],r['R800_pct']);self.assertEqual(r['residue_temp_C'],'800');self.assertEqual(r['source_reported_glass_wt_percent'],'15')
    self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['TGA_mass_mg']),('nitrogen','20','about10'))
  for k in ['OP','MMT','OMMT']:self.assertEqual(by[k]['TGA_mass_mg'],'about5');self.assertEqual(by[k]['direct_numeric_use'],'no');self.assertFalse(by[k].get('LOI_pct'))
 def test_OMMT5_TG_and_OMMT6_LOI_are_not_silently_matched(self):
  rows=load_rows();self.assertEqual(len(rows),11);held=[r for r in rows if r['direct_numeric_use']=='no'];self.assertEqual(len(held),5)
  r=next(r for r in held if r['source_sample_label']=='LGFPA6/OMMT5');self.assertEqual(r['source_LOI_label'],'LGFPA6/OMMT6')
  self.assertEqual(r['LOI_pct'],'24.2');self.assertEqual(r['pairing_status'],'pending_source_review');self.assertFalse(r.get('reviewed_measurement_fingerprint'))
  r=next(r for r in held if r['source_sample_label']=='PA6');self.assertEqual(r['source_reported_glass_wt_percent'],'0')
if __name__=='__main__':unittest.main()
