"""Protect literal textile evidence and sample-specific source conflicts."""
import csv, sys, unittest
from pathlib import Path
import pandas as pd
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'scripts'))
import pairing
import validate_tg_loi as v

class PolyesterNativeEvidenceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with(R/'data/incoming/verified_source_batch_20261001_b99_local_polyester_native.csv').open(newline='') as h:cls.rows=list(csv.DictReader(h))
  cls.pom=[r for r in cls.rows if r['DOI']=='10.1007/s12221-019-9189-0'];cls.flex=[r for r in cls.rows if r['DOI']=='10.1002/app.46414'];cls.paps=[r for r in cls.rows if r['DOI']=='10.1016/j.polymer.2021.123761']
 def test_only_four_initial_textile_pairs_count(self):
  report=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3]
  self.assertEqual(report['errors'],[]);self.assertEqual(report['verified_exact_sample_states'],4);self.assertEqual(report['verified_exact_condition_records'],4);self.assertEqual(len(self.rows),22)
 def test_explicit_loi_labels_not_curve_estimation(self):
  r={r['sample_state']:r for r in self.pom}
  self.assertEqual([r[k]['LOI_pct'] for k in ['FEP1','FEP2','FEP3','FEP4','FEP5']],['19.5','25.1','26.2','25.5','25.3'])
  self.assertTrue(all('printednumericlabels' in r[k]['LOI_locator'] for k in ['FEP2','FEP3','FEP4','FEP5']))
 def test_control_powder_legend_conflict_stays_unapproved(self):
  held=[r for r in self.pom if r['sample_state'] in ['FEP1','FEP0powder']]
  self.assertEqual(len(held),2)
  for r in held:self.assertNotEqual(r['pairing_status'],'verified_exact');self.assertEqual(r['reviewed_measurement_fingerprint'],'')
  self.assertEqual(held[0].get('Tmax1_C',''),'');self.assertEqual(held[0]['source_TG_prose_decomposition_peak_C'],'415')
 def test_unknown_residue_temperature_and_dsc_peaks_not_inferred(self):
  r={r['sample_state']:r for r in self.pom}
  self.assertEqual(r['FEP2']['residue_pct'],'26.85');self.assertEqual(r['FEP2']['residue_temp_C'],'');self.assertEqual(r['FEP2']['TG_end_C'],'750')
  for k,value in [('FEP3','28.1'),('FEP4','19.5'),('FEP5','18.0')]:self.assertEqual(r[k]['residue_pct'],value);self.assertEqual(r[k]['residue_temp_C'],'750')
  self.assertTrue(all(r[k].get('Tmax1_C','')=='' and r[k].get('T5_C','')=='' for k in ['FEP2','FEP3','FEP4','FEP5']))
 def test_extraction_weights_not_fabric_addon_and_wash_not_durability(self):
  r={r['sample_state']:r for r in self.pom}
  self.assertEqual([r[k]['source_PRP_extract_g'] for k in ['FEP3','FEP4','FEP5']],['2','4','7'])
  self.assertTrue(all(r[k].get('add_on_pct','')=='' and 'no durabilitylaundering' in r[k]['washing_state'] for k in ['FEP2','FEP3','FEP4','FEP5']))
  self.assertIn('85C20min',r['FEP3']['treatment_method']);self.assertIn('110C10min',r['FEP3']['treatment_method'])
 def test_unreviewed_supporting_information_and_washed_loi_stay_held(self):
  for r in self.flex:self.assertNotEqual(r['pairing_status'],'verified_exact');self.assertEqual(r['reviewed_measurement_fingerprint'],'')
  washed=next(r for r in self.flex if '45 washes' in r['sample_state']);self.assertEqual(washed['LOI_pct'],'31.0');self.assertEqual(washed['Tonset_C'],'');self.assertEqual(washed['residue_pct'],'')
  initial=[r for r in self.flex if '45 washes' not in r['sample_state']]
  self.assertEqual([r['source_signed_DTGmax_pct_min'] for r in initial],['-26.1','-17.8','-17.7','-17.4','-16.5','-16.1'])
  self.assertTrue(all(r['residue_temp_C']=='' and r.get('Tmax2_C','')=='' for r in initial))
 def test_paps_comparator_holds_and_separate_cone_residues(self):
  for r in self.paps:self.assertNotEqual(r['pairing_status'],'verified_exact');self.assertEqual(r['reviewed_measurement_fingerprint'],'')
  r=next(r for r in self.paps if r['sample_state']=='8%PAPS-DOPA' and r['atmosphere']=='N2')
  self.assertEqual(r['residue_pct'],'18');self.assertEqual(r['residue_temp_C'],'700');self.assertEqual(r['source_Table2_cone_residue_pct'],'7.5');self.assertEqual(r['LOI_standard'],'')
 def test_same_state_review_is_bound_to_numerical_values(self):
  accepted=[r for r in self.rows if r['pairing_status']=='verified_exact'];self.assertEqual(len(accepted),4)
  for r in accepted:self.assertEqual(pairing.evidence_issues(r),[]);self.assertEqual(r['material_form_TGA'],r['material_form_LOI'])
  changed=dict(accepted[0],LOI_pct='26.8');self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(changed))

if __name__=='__main__':unittest.main()
