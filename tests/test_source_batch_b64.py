"""Keep measured LOI statistics, onset stages and source identities intact."""
import csv,hashlib,json,unittest
from pathlib import Path
import pandas as pd
from scripts.pairing import evidence_issues,measurement_fingerprint
from scripts.validate_tg_loi import build_tables,numeric_errors
R=Path(__file__).resolve().parents[1];M=R/'data/curation/source_review_manifest_20260930_b64.json'
def rows(tag):
 f=next(x['file'] for x in json.loads(M.read_text())['files'] if x['file'].endswith('_'+tag+'.csv'));return list(csv.DictReader((R/f).open()))
class Batch64(unittest.TestCase):
 def test_fingerprints_and_input_hashes(self):
  for f in json.loads(M.read_text())['files']:
   self.assertEqual(hashlib.sha256((R/f['file']).read_bytes()).hexdigest(),f['published_input_sha256'])
   for r in csv.DictReader((R/f['file']).open()):self.assertFalse(evidence_issues(r));self.assertEqual(measurement_fingerprint(r),r['reviewed_measurement_fingerprint'])
 def test_cn3_exact_means_not_prose_rounding(self):
  self.assertEqual([(r['LOI_pct'],r['R600_pct']) for r in rows('cn3')],[('23.7','19'),('27.0','21'),('28.6','22'),('31.0','22'),('23.0','18'),('25.0','19'),('25.0','20'),('27.6','23')])
  self.assertEqual([r['LOI_standard_deviation'] for r in rows('cn3')],['0.76','0','1.19','0','0','0','0','0.55'])
 def test_ehp_mhp_exact_residues_and_uncertainty(self):
  self.assertEqual([(r['LOI_pct'],r['R600_pct']) for r in rows('ehp_mhp')],[('25.8','31'),('31.5','31'),('31.5','28'),('33.4','29'),('27.0','33'),('29.5','35'),('34.2','36'),('37.2','36')])
  r=rows('ehp_mhp')[3];self.assertEqual(r['sample_state'],'EHP-20');self.assertEqual(r['Tonset_C'],'158');self.assertEqual(r['additional_onset_C'],'');self.assertTrue(r['LOI_reported_plus_minus']);self.assertFalse(r.get('LOI_standard_deviation'))
 def test_cn_mono_exact_pairs(self):
  self.assertEqual([(r['LOI_pct'],r['Tonset_C'],r['R600_pct']) for r in rows('cn_mono')],[('30','244','30'),('32','242','29'),('34.2','240','33'),('40.2','240','35')])
 def test_no_mcc_or_threshold_substitution(self):
  for tag in ['cn3','ehp_mhp','cn_mono']:
   for r in rows(tag):
    for f in ['Tmax1_C','Tmax2_C','T5_C','T10_C']:self.assertFalse(r.get(f))
    self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['gas_flow_mL_min']),('nitrogen','10','60'));self.assertIn('initial',r['washing_state'])
 def test_thirty_seven_distinct_prepared_states(self):
  d=pd.DataFrame(rows('cn3')+rows('ehp_mhp')+rows('cn_mono')+rows('woolboron2026'));m,_,_,v=build_tables(d);self.assertEqual(len(m),37);self.assertEqual(v['verified_exact_sample_states'],37);self.assertFalse(numeric_errors(d))
 def test_derived_assay_metadata(self):
  m,_,_,_=build_tables(pd.DataFrame(rows('ehp_mhp')))
  for r in m.to_dict('records'):
   self.assertIn('not reported',r['TGA_specimen_preparation']);self.assertIn('13 x 6 cm',r['LOI_specimen_preparation']);self.assertTrue(r['LOI_reported_plus_minus'])
 def test_held_controls_and_reused_comparisons(self):
  h=json.loads((R/'data/curation/source_review_holds_20260930_b64.json').read_text());s=json.dumps(h);self.assertIn('10.1002/pat.2008',s);self.assertIn('CN-1',s);self.assertIn('10.4236/msa.2014.511079',s);self.assertIn('control',s.lower());self.assertIn('ramp',s)

 def test_wool_residue_temperature_and_preparation(self):
  d=rows('woolboron2026');self.assertEqual(len(d),17)
  self.assertEqual([(r['sample_state'],r['LOI_pct'],r['residue_pct']) for r in d],[('1A','24.7','4.67'),('1B','40.8','1.74'),('2A','44.9','10.15'),('2B','38.9','10'),('2C','37.3','15.28'),('3A','43.4','5.89'),('3B','47.1','3.15'),('3C','47.9','13.23'),('4A','53.3','7.72'),('4B','58.4','7.22'),('4C','57.1','13.67'),('5A','44.3','9.08'),('5B','47.4','6.77'),('5C','34.3','3.99'),('6A','48','5.03'),('6B','54.8','7.37'),('6C','59.8','11.28')])
  for r in d:
   self.assertEqual(r['residue_temp_C'],'810');self.assertEqual(r['heating_rate_C_min'],'20');self.assertFalse(r.get('R800_pct'));self.assertFalse(r.get('R600_pct'));self.assertFalse(r.get('add_on'));self.assertIn('before_five',r['washing_state'])
  by={r['sample_state']:r for r in d};self.assertEqual(by['3C']['source_preparation_method_number'],'1');self.assertEqual(by['4C']['source_preparation_method_number'],'2');self.assertEqual(by['3C']['boron_bath_concentration_wv_pct'],'5');self.assertEqual(by['4C']['boron_bath_concentration_wv_pct'],'5')
 def test_wool_derived_residue_and_stage_numbering(self):
  m,_,_,_=build_tables(pd.DataFrame(rows('woolboron2026')))
  for r in m.to_dict('records'):
   self.assertEqual(float(r['residue_temp_C']),810);self.assertGreater(float(r['Tmax1_C']),300);self.assertGreater(float(r['Tmax3_C']),600)
