"""Protect sample-specific LOI conflicts, native metrics and treatment states."""
import csv,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if not(ROOT/'scripts/pairing.py').exists():ROOT=ROOT/'repo'
sys.path.insert(0,str(ROOT/'scripts'));import pairing
PUBLIC=ROOT/'data/incoming/verified_source_batch_20261004_b191_local_textile.csv'
PRIVATE=ROOT.parent/'work/staged-local-textile-b191/publication_proposed.csv'
class THPOCottonFacts(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with(PUBLIC if PUBLIC.exists()else PRIVATE).open(newline='')as f:cls.rows=list(csv.DictReader(f));cls.accepted=[r for r in cls.rows if r['pairing_status']=='verified_exact']
 def test_four_initial_samefabric_pairs(self):
  self.assertEqual(len(self.rows),11);self.assertEqual([r['source_sample_label']for r in self.accepted],['Untreated','C1','C2','C3'])
  for r in self.accepted:self.assertEqual(r['material_form_TGA'],r['material_form_LOI']);self.assertEqual(r['treatment_state'],'initial')
 def test_full_native_TG_LOI_profiles(self):
  self.assertEqual([tuple(r[k]for k in ['T5_C','Tmax1_C','R800_pct','LOI_pct'])for r in self.accepted],[('306','375','9.4','18'),('263','347','22.1','30'),('259','340','27.4','31'),('225','331','33.7','32')])
  for r in self.accepted:self.assertFalse(r.get('Tonset_C'));self.assertEqual(r['residue_temp_C'],'800')
 def test_PDMS_conflicting_LOI_wholepair_held(self):
  r=self.rows[3];self.assertEqual((r['LOI_pct'],r['source_abstract_conclusion_LOI_pct'],r['source_SI_S3_beforewashing_LOI_pct']),('25','27.0','27'));self.assertEqual(r['direct_numeric_use'],'no');self.assertEqual((r['T5_C'],r['Tmax1_C'],r['R800_pct']),('270','343','25.4'))
 def test_SI_and_wash_TG_not_borrowed(self):
  for r in self.rows[5:]:self.assertFalse(any(r.get(k)for k in pairing.TG_FIELDS));self.assertFalse(r.get('residue_temp_C'));self.assertEqual(r['direct_numeric_use'],'no')
  self.assertEqual([r['LOI_pct']for r in self.rows[-2:]],['22','23'])
 def test_stock_concentrations_distinctfrom_addon(self):
  r=self.accepted[-1];self.assertEqual((r['source_THPO_stock_wt_pct'],r['source_guanazole_stock_wt_pct'],r['source_weight_gain_wt_pct']),('4','4','15'));self.assertIn('notfinalcomposition',r['source_loading_basis'])
 def test_ordinary_instrument_geometry_unknowns(self):
  for r in self.accepted:self.assertEqual((r['TGA_instrument'],r['heating_rate_C_min'],r['atmosphere']),('TAQ5000','20','N2'));self.assertFalse(r['TG_start_C']);self.assertEqual(r['source_LOI_dimensions_mm'],'58x150')
 def test_binding_rejects_editedgas_char_or_wash_LOI(self):
  for r in self.accepted:
   self.assertFalse(pairing.evidence_issues(r))
   for k,v in [('LOI_pct','22'),('atmosphere','air'),('residue_temp_C','700')]:self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**{k:v})))
if __name__=='__main__':unittest.main()
