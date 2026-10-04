"""Protect native cotton table cells, metric definitions, add-on basis and method scope."""
import csv,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if not(ROOT/'scripts/pairing.py').exists():ROOT=ROOT/'repo'
sys.path.insert(0,str(ROOT/'scripts'));import pairing
PUBLIC=ROOT/'data/incoming/verified_source_batch_20261004_b183_local_textile.csv'
PRIVATE=ROOT.parent/'work/staged-local-textile-b183/publication_proposed.csv'
class SourceFacts(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with(PUBLIC if PUBLIC.exists()else PRIVATE).open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def test_onlyfive_initial_woven_formulations(self):
  self.assertEqual(len(self.rows),5);self.assertEqual(len({r['sample_state']for r in self.rows}),5);self.assertTrue(all(r['material_form_TGA']==r['material_form_LOI']=='woven cotton fabric'for r in self.rows))
 def test_entire_native_Tables4and5(self):
  fields=['source_sample_label','Tonset_C','Tmax1_C','residue_at_Tmax1_pct','Tmax2_C','residue_at_Tmax2_pct','R800_pct','LOI_pct']
  expected=[('CO(Nc)','312','328','48.4','463','4.5','1.6','19.0'),('CO/4Si-DOPO','307','325','56.4','510','14.4','5.7','19.5'),('CO/8Si-DOPO','303','323','58.3','','','10.0','20.5'),('CO/16Si-DOPO','297','319','61.4','','','12.5','21.5'),('CO/32Si-DOPO','289','312','63.6','','','15.2','23.5')]
  for row,facts in zip(self.rows,expected):
   with self.subTest(sample=facts[0]):self.assertEqual(tuple(row[k]for k in fields),facts)
 def test_three_undefined_second_peaks(self):self.assertEqual([r['source_sample_label']for r in self.rows if not r['Tmax2_C']],['CO/8Si-DOPO','CO/16Si-DOPO','CO/32Si-DOPO']);self.assertTrue(all(not r['residue_at_Tmax2_pct']for r in self.rows[2:]))
 def test_extrapolated_onset_is_not_T5(self):self.assertTrue(all(r['Tonset_C']and not r['T5_C']and not r['T10_C']and'extrapolated'in r['source_metric_definition']for r in self.rows))
 def test_dry_addon_distinct_from_sol_concentration(self):self.assertEqual([r['source_dry_solid_addon_pct']for r in self.rows],['0','2.6','5.1','14.1','28.2']);self.assertEqual([r['source_sol_concentration_pct']for r in self.rows],['0','4','8','16','32']);self.assertTrue(all('untreated drymass'in r['source_dry_solid_addon_basis']for r in self.rows))
 def test_ordinary_air10_mass1_n2(self):self.assertTrue(all((r['atmosphere'],r['heating_rate_C_min'],r['TG_start_C'],r['TG_end_C'],r['source_TGA_sample_mass_mg'],r['source_TGA_repetitions'])==('air','10','','800','1','2')for r in self.rows))
 def test_LOI_scope_not_vertical_or_cone(self):self.assertTrue(all(r['LOI_standard']=='ASTM D2863'and r['LOI_instrument']=='FIRE oxygen index apparatus'and'unreported'in r['source_LOI_dimensions_repetitions']and'vertical'in r['source_LOI_dimensions_repetitions']and'cone'in r['source_LOI_dimensions_repetitions']for r in self.rows))
 def test_peak_residues_distinct_from_R800(self):self.assertTrue(all(r['residue_temp_C']=='800'and r['residue_pct']==r['R800_pct']and r['residue_at_Tmax1_pct']!=r['R800_pct']for r in self.rows))
 def test_review_binding_rejects_false_massloss_definition(self):
  self.assertTrue(all(not pairing.evidence_issues(r)for r in self.rows));self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(self.rows[0],T5_C='312')))
if __name__=='__main__':unittest.main()
