"""Protect original TG endpoint/atmosphere/assay and washed-state distinctions."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'scripts'))
import pairing
import validate_tg_loi as v

class GCNCottonEvidenceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  path=R/'data/incoming/verified_source_batch_20261001_b107_local_gcn_rgo.csv'
  with path.open(newline='')as f:cls.rows=list(csv.DictReader(f))
  cls.approved=[r for r in cls.rows if r['pairing_status']=='verified_exact' and r['DOI'].endswith('05877-3')]
  cls.rgo=[r for r in cls.rows if r['DOI'].endswith('03356-7')]
 def test_gas_conditions_count_five_states(self):
  report=v.build_tables(pd.DataFrame(self.rows),v.issue_list())[3]
  self.assertEqual(report['errors'],[])
  self.assertEqual((report['verified_exact_sample_states'],report['verified_exact_condition_records']),(8,13))
 def test_argon_is_not_nitrogen(self):
  self.assertEqual({r['atmosphere']for r in self.approved},{'air','Ar'})
  ar=next(r for r in self.approved if r['atmosphere']=='Ar')
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(ar,atmosphere='N2')))
 def test_residue_temperature_is_700_despite_800_run_end(self):
  for r in self.approved:
   self.assertEqual(r['residue_temp_C'],'700');self.assertEqual(r['TG_end_C'],'800')
   self.assertEqual(r['R700_pct'],r['residue_pct'])
   self.assertEqual(r.get('R800_pct',''),'')
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(self.approved[0],residue_temp_C='800')))
 def test_washed_loi_never_inherits_initial_tg(self):
  washed=[r for r in self.rows if r['pairing_status']!='verified_exact' and r['DOI'].endswith('05877-3')]
  self.assertEqual(len(washed),6)
  self.assertEqual([r['LOI_pct']for r in washed],['29.6','29.1','28.5','28.6','28.6','28.5'])
  for r in washed:
   self.assertTrue(all(r.get(k,'')==''for k in pairing.TG_FIELDS))
   self.assertEqual(r['reviewed_measurement_fingerprint'],'')
   self.assertEqual(r['source_measured_weight_gain_pct_owf'],'')
 def test_early_t5_not_tonset_or_t10(self):
  r=next(r for r in self.approved if r['sample_state']=='(P/G)4BL' and r['atmosphere']=='air')
  self.assertEqual(r['T5_C'],'158.5');self.assertEqual(r['Tmax1_C'],'259.0')
  self.assertEqual(r.get('T10_C',''),'');self.assertEqual(r.get('Tonset_C',''),'')
 def test_mcc_temperature_cannot_reuse_tg_review(self):
  r=next(r for r in self.approved if r['sample_state']=='(P/G+P/PA)4+4')
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,Tmax1_C='310.2')))
 def test_missing_tg_mass_flow_and_loi_repeats_stay_unreported(self):
  for r in self.approved:
   self.assertEqual(r['source_TG_mass_mg'],'');self.assertEqual(r['source_TG_flow'],'Unreported')
   self.assertEqual(r['source_LOI_replicates'],'');self.assertEqual(r['source_LOI_uncertainty_pct'],'')
 def test_whole_fabric_does_not_transfer_to_separate_fibers(self):
  self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(self.approved[0],material_form_LOI='Cotton fibers')))
 def test_uncoated_add_on_and_layer_dashes_are_not_measured_zeros(self):
  for r in self.approved:
   if r['sample_state']=='Uncoated':
    for key in ['source_measured_weight_gain_pct_owf','source_weight_gain_uncertainty_pct','source_PEI_GCN_bilayers','source_PEI_PA_bilayers']:
     self.assertEqual(r[key],'')
 def test_wash_state_change_invalidates_fingerprint(self):
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(self.approved[0],washing_state='30 water washes')))
 def test_rgo_second_stage_peaks_and_rounded_residues(self):
  accepted=[r for r in self.rgo if r['pairing_status']=='verified_exact']
  self.assertEqual(len(accepted),3)
  self.assertEqual([r['Tmax2_C']for r in accepted],['296.7','287.4','290.9'])
  self.assertEqual([r['R600_pct']for r in accepted],['24.8','29.9','32.7'])
  for r in accepted:
   self.assertEqual(r.get('Tmax1_C',''),'');self.assertEqual(r.get('T5_C',''),'')
   self.assertEqual(r['source_APP_dip_minutes_resolved'],'')
   self.assertEqual(r['source_APP_dip_minutes_methods'],'10');self.assertEqual(r['source_APP_dip_minutes_table1'],'1')
 def test_rgo_control_loi_conflict_stays_outside_verified(self):
  r=next(r for r in self.rgo if r['sample_state']=='Pristine cotton fabric')
  self.assertEqual(r['LOI_pct'],'');self.assertEqual(r['source_LOI_abstract_pct'],'18.0')
  self.assertEqual(r['source_LOI_prose_pct'],'18.2');self.assertEqual(r['reviewed_measurement_fingerprint'],'')
 def test_rgo_washed_vft_is_neither_initial_loi_nor_cone_tg(self):
  washed=[r for r in self.rgo if r['sample_state'].startswith('Washed-')]
  self.assertEqual(len(washed),4)
  for r in washed:
   self.assertEqual(r['LOI_pct'],'');self.assertTrue(all(r.get(k,'')==''for k in pairing.TG_FIELDS))
   self.assertEqual(r['reviewed_measurement_fingerprint'],'')
   self.assertEqual(r['source_measured_weight_gain_pct_owf'],'');self.assertEqual(r['source_TG_mass_mg'],'')

if __name__=='__main__':unittest.main()
