"""Keep common sample identity distinct from assay geometry and unsupported fields."""
import csv,hashlib,json,unittest
from pathlib import Path
import pandas as pd
from scripts.pairing import evidence_issues,measurement_fingerprint
from scripts.validate_tg_loi import build_tables,numeric_errors
R=Path(__file__).resolve().parents[1];M=R/'data/curation/source_review_manifest_20260930_b59.json'
def rows(tag):
 f=next(x['file'] for x in json.loads(M.read_text())['files'] if tag in x['file']);return list(csv.DictReader((R/f).open()))
class Batch59(unittest.TestCase):
 def test_fingerprints(self):
  for tag,n in [('mof3',3),('fibers1972',19)]:
   d=rows(tag);self.assertEqual(len(d),n)
   for r in d:self.assertFalse(evidence_issues(r));self.assertEqual(measurement_fingerprint(r),r['reviewed_measurement_fingerprint'])
   self.assertIn('measurement_review_pending_or_stale',evidence_issues(dict(d[0],LOI_pct='99')))
 def test_1972_exact_nineteen_pairs(self):
  expected=[('PET','22','3.8'),('Polypropylene','20','3.3'),('Nylon-6','20','1.5'),('Nylon-6.6','21','8.8'),('MXD-6','23','17.0'),('Nomex','30','21.4'),('Kynol','35','30.0'),('Krehalon','50','4.5'),('Teviron','35','6.0'),('Cordelan','30','0.3'),('Kanekalon','26','34.5'),('Exlan','17','58.5'),('Chinon','18','48.5'),('Silk','23','9.0'),('Wool','24','12.8'),('Cotton','18','2.0'),('Flame-retardant Cotton','35','11.0'),('Rayon','19','0.4'),('Acetate','17','3.0')]
  self.assertEqual([(r['sample_state'],r['LOI_pct'],r['R600_pct']) for r in rows('fibers1972')],expected)
 def test_1972_unknown_tg_geometry_preserved(self):
  for r in rows('fibers1972'):
   self.assertEqual(r['TGA_specimen_preparation'],'not reported');self.assertEqual(r['LOI_specimen_preparation'],'woven or knitted fabric; 150-200 g/m2; construction unspecified by row')
   self.assertEqual(r['TGA_form_source_description'],'commercial fibers; TG specimen geometry unspecified');self.assertEqual(r['LOI_form_source_description'],'woven or knitted fabric')
   self.assertIn('identical assay geometry is not asserted',r['pairing_evidence']);self.assertEqual(r['material_form_TGA'],r['material_form_LOI'])
 def test_1972_no_flashpoint_or_dta_substitution(self):
  for r in rows('fibers1972'):
   self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['TGA_sample_mass_reported']),('air','15','5.0 mg'))
   for f in ['Tonset_C','Tmax1_C','T5_C','gas_flow_mL_min','LOI_sample_dimensions_mm']:self.assertFalse(r.get(f))
   self.assertNotIn(r['sample_state'],['Carbon Fiber','Glass'])
 def test_mof_exact_fields(self):
  self.assertEqual([(r['sample_state'],r['T5_C'],r['Tmax1_C'],r['R800_pct'],r['LOI_pct']) for r in rows('mof3')],[('Control cotton','299.1','368.4','8.28','17.2'),('Cotton/UiO-66','','355.3','10.34','18.4'),('Cotton/UiO-66/2St-PZS','282.0','309.7','25.34','24.8')])
 def test_mof_conventional_tg_distinguished(self):
  for r in rows('mof3'):
   self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['TGA_sample_mass_reported']),('nitrogen','10','8 mg'))
   self.assertIn('Mettler-Toledo',r['TGA_instrument'])
   for f in ['gas_flow_mL_min','TG_end_C','Rmax_pct_min','add_on_pct']:self.assertFalse(r.get(f))
   self.assertNotIn('20',r['washing_state'])
 def test_derived_keeps_metadata(self):
  d=pd.DataFrame(rows('mof3')+rows('fibers1972'));m,_,_,v=build_tables(d);self.assertEqual(len(m),22);self.assertEqual(v['verified_exact_sample_states'],22);self.assertFalse(numeric_errors(d))
  for r in m.to_dict('records'):
   if r['DOI']=='10.2115/fiber.28.9_359':self.assertEqual(r['TGA_specimen_preparation'],'not reported');self.assertIn('woven or knitted',r['LOI_specimen_preparation'])
 def test_source_hashes_and_holds(self):
  for f in json.loads(M.read_text())['files']:self.assertEqual(hashlib.sha256((R/f['file']).read_bytes()).hexdigest(),f['published_input_sha256'])
  h=json.loads((R/'data/curation/source_review_holds_20260930_b59.json').read_text());self.assertEqual(len(h),10);s=json.dumps(h);self.assertIn('Kanekalon',s);self.assertIn('PZS treatment bath',s);self.assertIn('Carbon Fiber and Glass',s)
