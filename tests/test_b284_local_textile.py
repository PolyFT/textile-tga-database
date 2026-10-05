"""Protect source T3, sparse peak columns, and assay/form boundaries."""
import csv,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if not (ROOT/'scripts/pairing.py').exists():ROOT=Path(__file__).resolve().parent.parent/'repo'
sys.path.insert(0,str(ROOT/'scripts'));import pairing
def rows():
 p=ROOT/'data/incoming/verified_source_batch_20261005_b284_local_textile.csv'
 if not p.exists():p=Path(__file__).resolve().parent/'staged-local-textile-b284/publication_proposed.csv'
 with p.open(newline='') as f:return list(csv.DictReader(f))
class GlassPETAHPSourceBoundaries(unittest.TestCase):
 def test_T3_is_not_T5_T10_or_Tonset_and_peak_columns_are_not_shifted(self):
  valid=[r for r in rows() if r['direct_numeric_use']=='yes'];self.assertEqual(len(valid),8);self.assertEqual(len({r['sample_state'] for r in valid}),4)
  for r in valid:
   self.assertTrue(r['source_raw_T3_C']);self.assertTrue(all(not r.get(k) for k in ['T5_C','T10_C','Tonset_C']))
   for i in range(1,4):self.assertEqual(r.get('Tmax'+str(i)+'_C',''),r.get('source_raw_Tmax'+str(i)+'_C',''))
   for metric in ['T5_C','T10_C','Tonset_C']:self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**{metric:r['source_raw_T3_C']})))
  n=next(r for r in valid if r['source_sample_label']=='PET/GF' and r['atmosphere']=='nitrogen');self.assertEqual((n['Tmax1_C'],n['Tmax2_C'],n['Tmax3_C']),('','443',''))
  a=next(r for r in valid if r['source_sample_label']=='PET/GF' and r['atmosphere']=='air');self.assertEqual((a['Tmax1_C'],a['Tmax2_C'],a['Tmax3_C']),('','439','549'))
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(n,Tmax1_C='443',Tmax2_C='')))
 def test_ordinary_TG_is_distinct_from_TGIR_MCC_and_muffle_residue(self):
  for r in [r for r in rows() if r['direct_numeric_use']=='yes']:
   self.assertEqual((r['TGA_mass_mg'],r['TGA_gas_flow_ml_min'],r['TGA_pan'],r['heating_rate_C_min']),('5-10','60','open platinum pan','20'))
   self.assertEqual(r['residue_temp_C'],'650');self.assertEqual(r['residue_pct'],r['R650_pct']);self.assertFalse(r.get('TG_start_C'));self.assertEqual(r['material_form_TGA'],r['material_form_LOI']);self.assertIn('45mLmin',r['source_separate_TGIR_conditions'])
   self.assertEqual(r['LOI_uncertainty_pct'],'0.5');self.assertEqual(r['source_LOI_uncertainty_type'],'unreported');self.assertFalse(r.get('TGA_replicates'));self.assertFalse(r.get('LOI_replicates'))
   self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,residue_temp_C='700')))
   self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,LOI_uncertainty_pct='3')))
 def test_powder_endpoints_and_nominal_mixture_are_never_invented(self):
  held=[r for r in rows() if r['direct_numeric_use']=='no'];self.assertEqual(len(held),2)
  for r in held:self.assertFalse(r.get('LOI_pct'));self.assertFalse(r.get('reviewed_measurement_fingerprint'));self.assertFalse(r.get('heating_rate_C_min'));self.assertFalse(r.get('TGA_pan'))
  a=next(r for r in held if r['source_sample_label']=='AHP');self.assertEqual(a['source_raw_endpoint_unbound_residue_pct'],'74');self.assertFalse(a['residue_pct']);self.assertFalse(a['residue_temp_C'])
  mc=next(r for r in held if r['source_sample_label']=='MC');self.assertEqual((mc['R650_pct'],mc['residue_temp_C']),('1.2','650'))
  for r in [r for r in rows() if r['source_sample_label']=='PET/GF-AHP-MC']:
   self.assertEqual((r['source_reported_AHP_MC_total_wt_percent'],r['source_reported_AHP_MC_ratio']),('10','2:1'));self.assertFalse(r['source_reported_AHP_wt_percent']);self.assertFalse(r['source_reported_MC_wt_percent']);self.assertIn('Al(H2PO2)3',r['source_AHP_identity'])
if __name__=='__main__':unittest.main()
