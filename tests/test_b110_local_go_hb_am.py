"""Protect original residue conflicts, washer equivalents and unmatched states."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'scripts'))
import pairing
import validate_tg_loi as v

class GOHBCottonEvidenceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  path=R/'data/incoming/verified_source_batch_20261001_b110_local_go_hb.csv'
  with path.open(newline='')as f:cls.rows=list(csv.DictReader(f))
  cls.go=[r for r in cls.rows if r['DOI'].endswith('123656')];cls.hb=[r for r in cls.rows if r['DOI'].endswith('115648')];cls.am=[r for r in cls.rows if r['DOI'].endswith('03140-7')]
 def test_two_gases_do_not_add_sample_states(self):
  report=v.build_tables(pd.DataFrame(self.rows),v.issue_list())[3]
  self.assertEqual(report['errors'],[]);self.assertEqual((report['verified_exact_sample_states'],report['verified_exact_condition_records']),(12,15))
 def test_nitrogen_control_residue_conflict_stays_blank(self):
  r=next(r for r in self.go if r['sample_state']=='Pure cotton'and r['atmosphere']=='N2')
  self.assertEqual(r['source_R700_Table1_pct'],'7.4');self.assertEqual(r['source_R700_prose_p17_pct'],'7.3')
  for k in ['residue_pct','R700_pct','residue_temp_C']:self.assertEqual(r[k],'')
  self.assertEqual(r['T5_C'],'293.9');self.assertEqual(r['Tmax1_C'],'368.5')
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,residue_pct='7.4',residue_temp_C='700')))
 def test_air_control_is_not_other_formulation(self):
  r=next(r for r in self.go if r['sample_state']=='Pure cotton'and r['atmosphere']=='air')
  self.assertEqual(r['R700_pct'],'3.2')
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,residue_pct='3.4',R700_pct='3.4')))
 def test_low_air_mass_loss_is_not_tonset_or_water_peak(self):
  r=next(r for r in self.go if r['sample_state']=='GO-cotton/ZIF-8'and r['atmosphere']=='air')
  self.assertEqual(r['T5_C'],'142.3');self.assertEqual(r['T10_C'],'162.3')
  self.assertEqual(r.get('Tonset_C',''),'');self.assertEqual(r.get('water_removal_peak_C',''),'')
  self.assertIn('unnumbered',r['source_Tmax_label'])
 def test_hb_loi_only_states_never_borrow_initial_tg(self):
  held=[r for r in self.hb if r['pairing_status']!='verified_exact'];self.assertEqual(len(held),15)
  self.assertEqual(len([r for r in held if 'after' in r['sample_state']]),12)
  for r in held:self.assertTrue(all(r.get(k,'')==''for k in pairing.TG_FIELDS));self.assertEqual(r['reviewed_measurement_fingerprint'],'')
 def test_hb_water_and_intervals_not_dtg_peak_estimates(self):
  approved=[r for r in self.hb if r['pairing_status']=='verified_exact'];self.assertEqual(len(approved),2)
  for r in approved:
   for k in ['T5_C','T10_C','Tonset_C','Tmax1_C','Tmax2_C','water_removal_peak_C']:self.assertEqual(r.get(k,''),'')
   self.assertEqual(r['residue_temp_C'],'800');self.assertEqual(r['residue_pct'],r['R800_pct'])
   self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,Tonset_C='105')))
 def test_hb_oxidative_word_does_not_create_air_test(self):
  approved=[r for r in self.hb if r['pairing_status']=='verified_exact']
  for r in approved:
   self.assertEqual(r['atmosphere'],'N2');self.assertIn('inconsistent',r['source_TG_terminology_conflict'])
   self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,atmosphere='air')))
 def test_washer_home_equivalents_and_preparation_are_distinct(self):
  r=next(r for r in self.hb if r['sample_state']=='HBPOPN160g/L after50homeLCs')
  self.assertEqual(r['source_home_laundering_cycles'],'50');self.assertEqual(r['LOI_pct'],'29.3')
  self.assertIn('oneacceleratedcycle=5homeLCs',r['source_accelerated_wash_protocol']);self.assertEqual(r['source_measured_weight_gain_pct_owf'],'')
  initial=next(r for r in self.hb if r['sample_state']=='HBPOPN160g/L')
  self.assertEqual(initial['source_measured_weight_gain_pct_owf'],'28.1');self.assertEqual(initial['source_wet_pickup_pct'],'120');self.assertEqual(initial['source_bath_HBPOPN_g_L'],'160')
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(initial,washing_state=r['washing_state'])))
 def test_missing_mass_and_loi_size_not_borrowed_from_other_assay(self):
  for r in self.rows:
   self.assertEqual(r['source_TG_mass_mg'],'');self.assertEqual(r['source_LOI_replicates'],'')
  for r in self.hb:self.assertEqual(r['source_LOI_specimen_size_mm'],'')
  for r in self.go:self.assertNotIn('220g',r['material_form']);self.assertEqual(r['source_LOI_specimen_size_mm'],'150x58')
 def test_fabric_to_separate_fibers_needs_new_review(self):
  self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(self.go[0],material_form_LOI='Cotton fibers')))
 def test_publisher_preproof_not_author_preprint_or_final_vor(self):
  for r in self.go+self.hb:
   self.assertEqual(r['publication_type'],'journal_article');self.assertIn('not',r['source_document_version'].lower())
   self.assertIn('pre-proof',r['source_document_version'].lower())
 def test_am_direct_loi_labels_preserve_series_and_control(self):
  vals={r['sample_state']:float(r['LOI_pct'])for r in self.am}
  self.assertEqual(vals,{'Cotton':18.1,'C5/CS/APP':24.1,'C10/CS/APP':25.7,'C15/CS/APP':26.0,'C5/AM-CS/APP':25.6,'C10/AM-CS/APP':27.8,'C15/AM-CS/APP':31.5})
  r=next(r for r in self.am if r['sample_state']=='Cotton')
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,LOI_pct='18.4')))
 def test_am_nitrogen_tg_not_cone_char_or_air_photos(self):
  r=next(r for r in self.am if r['sample_state']=='Cotton')
  self.assertEqual(r['R800_pct'],'6.3');self.assertEqual(r['T5_C'],'346.5');self.assertEqual(r['Tmax1_C'],'396.3')
  self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,residue_pct='8.1',R800_pct='8.1')))
  for r in self.am:
   self.assertEqual(r['atmosphere'],'N2');self.assertEqual(r['heating_rate_C_min'],'10');self.assertEqual(r['residue_temp_C'],'800')
   self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,atmosphere='air')))
 def test_am_missing_assay_numbers_not_other_assay_repeats(self):
  for r in self.am:
   for k in ['TG_start_C','source_TG_mass_mg','source_TG_replicates','source_LOI_replicates','LOI_standard','source_LOI_uncertainty_pct','T10_C','Tmax2_C']:self.assertEqual(r.get(k,''),'')
   self.assertEqual(r['source_LOI_specimen_size_mm'],'150x58');self.assertIn('Ambient',r['source_TG_start'])
 def test_am_bath_bilayers_and_dry_addon_are_distinct(self):
  r=next(r for r in self.am if r['sample_state']=='C15/AM-CS/APP')
  self.assertEqual(r['source_bilayers'],'15');self.assertEqual(r['source_AM_native_wt_pct_CS'],'3.3');self.assertEqual(float(r['source_measured_weight_gain_pct_owf']),18.5)
  self.assertIn('CSsolution(1.0wt%)',r['source_AM_percent_basis']);self.assertIn('Na2CO3',r['source_preparation']);self.assertIn('notdurability',r['washing_state'])
 def test_am_publisher_journal_identity_and_form(self):
  for r in self.am:
   self.assertEqual(r['publication_type'],'journal_article');self.assertIn('ORIGINAL RESEARCH',r['source_document_version']);self.assertIn('150g/m2',r['material_form']);self.assertIn('Quanying',r['material_form'])

if __name__=='__main__':unittest.main()
