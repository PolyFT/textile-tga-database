"""Protect native onset, residue endpoint and same-state textile measurements."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b162/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261004_b162_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing;import validate_tg_loi as v
A='10.1007/s10570-025-06614-8';B='10.1007/s10570-025-06393-2';C='10.1007/s10570-023-05528-7'
class TextileB162Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as handle:cls.rows=list(csv.DictReader(handle))
 def subset(self,doi):return[r for r in self.rows if r['DOI']==doi]
 def find(self,doi,sample,gas=None):return next(r for r in self.subset(doi)if r['sample_state']==sample and(gas is None or r['atmosphere']==gas))
 def accepted(self):return[r for r in self.rows if r['pairing_status']=='verified_exact']
 def noTG(self,row):self.assertTrue(all(not row.get(k)for k in pairing.TG_FIELDS))
 def test_two_states_four_conditions_not21facts(self):
  p=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(p['errors']);self.assertEqual((p['verified_exact_sample_states'],p['verified_exact_condition_records']),(2,4));self.assertEqual(len(self.rows),21)
 def test_all17held_excluded(self):
  held=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(held),17);self.assertEqual([sum(r['DOI']==d for r in held)for d in[A,B,C]],[8,6,3]);self.assertTrue(all(pairing.evidence_issues(r)for r in held))
 def test_measurement_fingerprints_reject_cross_state_or_numeric_changes(self):
  for r in self.accepted():
   self.assertFalse(pairing.evidence_issues(r))
   for k,value in [('LOI_pct','99'),('Tonset_C','333'),('R700_pct','77'),('atmosphere','Ar'),('heating_rate_C_min','10'),('washing_state','50LC'),('sample_state','Otherdose')]:self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**{k:value})))
 def test_fabric_not_fiber(self):
  for r in self.accepted():self.assertEqual(r['material_form_TGA'],'cotton fabric');self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='cotton fiber')))
 def test_DTMHS_all8_ordinary_ramps_unknown_not_TGIR(self):
  self.assertEqual(len(self.subset(A)),8)
  for r in self.subset(A):self.assertFalse(r['heating_rate_C_min']);self.assertFalse(r.get('TG_start_C'));self.assertFalse(r.get('TG_end_C'));self.assertIn('ordinary_TG_ramp_unreported',r['pairing_status']);self.assertIn('notborrowedforordinaryTG',r['source_TGIR_method'])
 def test_DTMHS_rate_percent_per_minute_not_per_degree(self):
  r=self.find(A,'DTMHS_Cotton_initial','N2');self.assertEqual(r['source_Rmax_pct_per_min'],'25.3');self.assertIn('norampconversion',r['source_DTG_rate_definition']);r=self.find(A,'DTMHS_DTMHS_AP_initial','air');self.assertEqual((r['source_Rmax1_pct_per_min'],r['source_Rmax2_pct_per_min']),('7.7','2.1'))
 def test_DTMHS_T5_T10_two_air_peaks_remain_distinct(self):
  r=self.find(A,'DTMHS_AP_initial','air');self.assertEqual((r['T5_C'],r['T10_C'],r['Tmax1_C'],r['Tmax2_C'],r['R700_pct']),('217','240','288','499','4'));self.assertFalse(r.get('Tonset_C'));r=self.find(A,'DTMHS_DTMHS_initial','N2');self.assertEqual((r['T5_C'],r['T10_C'],r['Tmax1_C'],r['R700_pct']),('252','295','358','18.7'))
 def test_DTMHS_own_LOI_weightgain_not_feed_or_conechar(self):
  r=self.find(A,'DTMHS_DTMHS_AP_initial','N2');self.assertEqual((r['LOI_pct'],r['source_weight_gain_pct'],r['R700_pct']),('31.4','10.69','39.9'));self.assertIn('Table5conechar',r['source_MCC_cone_exclusion']);self.assertIn('notTGTable1',r['source_MCC_cone_exclusion']);self.assertEqual(self.find(A,'DTMHS_DTMHS_initial','N2')['LOI_pct'],'18.9')
 def test_Multilayer_four_residues_no_inferred_800C_endpoint(self):
  for sample,value in [('COT','10.4'),('PMT6','15.8'),('PHT6','13.7'),('PMTPHT3','23.7')]:
   r=self.find(B,'Multilayer_'+sample+'_initial');self.assertEqual(r['residue_pct'],value);self.assertFalse(r.get('residue_temp_C'));self.assertFalse(r.get('R800_pct'));self.assertEqual(r['TG_end_C'],'800');self.assertIn('notassigned800C',r['source_TG_residue_raw_definition']);self.assertIn('temperature_unreported',r['pairing_status'])
 def test_Multilayer_water_peak_and_approx369_not_exact_Tmax(self):
  r=self.find(B,'Multilayer_COT_initial');self.assertEqual(r['source_Tmax_approx_raw_C'],'369');self.assertFalse(r.get('Tmax1_C'));self.assertFalse(r.get('T5_C'));self.assertIn('notexactmaximumrate',r['source_Tmax_approx_limit']);self.assertIn('firstwater~100',r['source_TG_endpoint_hold'])
 def test_Multilayer_MCC_temperature_not_TG(self):
  for r in self.subset(B):self.assertFalse(r.get('Tmax1_C'))
  r=self.find(B,'Multilayer_PMTPHT3_initial');self.assertIn('MCC369/377.5',r['source_MCC_exclusion']);self.assertIn('notDTGmaximum',r['source_MCC_exclusion']);self.assertEqual((r['heating_rate_C_min'],r['TG_start_C'],r['TG_end_C']),('10','30','800'))
 def test_Multilayer_five_finishing_cycles_not_washing(self):
  r=self.find(B,'Multilayer_PMTPHT5_initial');self.noTG(r);self.assertEqual((r['LOI_pct'],r['source_weight_gain_pct']),('33.5','50.8'));self.assertIn('notwashingcycles',r['source_cycle_definition'])
 def test_Multilayer_24_hours_not_24_cycles_or_initialTG(self):
  r=self.find(B,'Multilayer_PMTPHT3_after24hourwaterwash');self.noTG(r);self.assertEqual(r['LOI_pct'],'26.6');self.assertIn('24hour_neutralwater30C',r['washing_state']);self.assertIn('not24launderingcycles',r['source_wash_time_definition'])
 def test_HPDPP_native_Tonset_not_T5_T10(self):
  expected={('Control','N2'):('322.9','353.9','0'),('FRC40','N2'):('260.2','300.8','33.39'),('Control','air'):('310.3','355.4','0'),('FRC40','air'):('262.4','294.1','10.78')}
  for (sample,gas),values in expected.items():
   r=self.find(C,'HPDPP_'+sample+'_initial',gas);self.assertEqual(tuple(r[k]for k in['Tonset_C','Tmax1_C','R700_pct']),values);self.assertFalse(r.get('T5_C'));self.assertFalse(r.get('T10_C'));self.assertIn('TonsetnotT5/T10',r['source_metric_definition'])
 def test_HPDPP_original_approx_LOI_qualifier_not_curve_estimate(self):
  for gas in ['N2','air']:
   r=self.find(C,'HPDPP_Control_initial',gas);self.assertEqual(r['LOI_pct'],'17.7');self.assertIn('approximately17.7',r['source_LOI_numeric_qualifier']);self.assertIn('notcurveestimate',r['source_LOI_numeric_qualifier']);self.assertEqual(self.find(C,'HPDPP_FRC40_initial',gas)['LOI_pct'],'41.3')
 def test_HPDPP_explicit_control_pretreatment_not_treated_state(self):
  r=self.find(C,'HPDPP_Control_initial','N2');self.assertIn('20pctNaOH5min',r['washing_state']);self.assertIn('2pctaceticacid',r['washing_state']);self.assertIn('HPDPPunassigned',r['treatment_method']);r=self.find(C,'HPDPP_FRC40_initial','N2');self.assertIn('runningwater_rinse120Cdry',r['washing_state']);self.assertEqual((r['source_bath_HPDP_pct'],r['source_weight_gain_pct']),('40','17.37'))
 def test_HPDPP_standalone_methods_and_R700_not_cone(self):
  for r in self.accepted():self.assertEqual((r['TG_start_C'],r['TG_end_C'],r['heating_rate_C_min'],r['residue_temp_C']),('40','700','20','700'));self.assertEqual(r['TGA_instrument'],'Pyris1 PerkinElmer');self.assertIn('ordinaryPyris1N2/airmethodexplicit',r['source_TGIR_exclusion']);self.assertIn('notcone2.5/9.5',r['source_residue_definition'])
 def test_HPDPP_all_three_washed_LOI_NO_initialTG_or_5xLC(self):
  for sample,cycle,loi in [('FRC40',50,'29.7'),('FRC30',30,'26.5'),('FRC20',30,'26.1')]:
   r=self.find(C,'HPDPP_'+sample+'_after'+str(cycle)+'LC');self.noTG(r);self.assertEqual(r['LOI_pct'],loi);self.assertIn('AATCC61-2013_3A',r['washing_state']);self.assertIn('notmultipliedbyfive',r['source_cycle_definition'])
 def test_public_facts_no_privatepaths_valid_review_dates(self):
  for r in self.rows:self.assertRegex(r['evidence_reviewed_at'],r'^\d{4}-\d{2}-\d{2}$');self.assertFalse(any(('/'+'Volumes'+'/')in str(x)or('/'+'Users'+'/')in str(x)or('smb'+':'+chr(47)*2)in str(x)for x in r.values()))
if __name__=='__main__':unittest.main(verbosity=2)
