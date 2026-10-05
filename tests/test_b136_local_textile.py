"""Protect textile identity, original metric definitions and excluded washing states."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b136/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261003_b136_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing,validate_tg_loi as v
A='10.1021/acssuschemeng.9b02474';B='10.1002/pat.3041';C='10.1016/j.reactfunctpolym.2018.03.005'
class TextileB136Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def source(self,d):return[r for r in self.rows if r['DOI']==d]
 def exact(self,d,s,g):return next(r for r in self.source(d)if r['sample_state']==s and r['atmosphere']==g and r['pairing_status']=='verified_exact')
 def reject(self,r,**kw):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**kw)))
 def test_sixstates_eightconditions_not_sixtyfacts(self):
  z=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(z['errors']);self.assertEqual((z['verified_exact_sample_states'],z['verified_exact_condition_records']),(6,8));self.assertEqual(len(self.rows),60)
 def test_fiftytwo_holds_no_canonical_tg(self):
  rr=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(rr),52);self.assertTrue(all(all(not r.get(k,'')for k in pairing.TG_FIELDS)for r in rr))
 def test_casein_only_control_and30_initial(self):
  rr=[r for r in self.source(A)if r['pairing_status']=='verified_exact'];self.assertEqual(len(rr),4);self.assertEqual({r['sample_state']for r in rr},{'ControlCotton','Casein30Cotton'});self.assertEqual({r['LOI_pct']for r in rr},{'18.2','39.5'})
 def test_casein_native_tonset_defined_t10(self):
  r=self.exact(A,'Casein30Cotton','N2');self.assertEqual(r['T10_C'],'259');self.assertFalse(r['Tonset_C']);self.assertFalse(r['T5_C']);self.assertIn('10percentweightloss',r['source_raw_Tonset_label']);self.reject(r,T10_C='',Tonset_C='259')
 def test_casein_gas_specific_values(self):
  n=self.exact(A,'ControlCotton','N2');a=self.exact(A,'ControlCotton','air');self.assertEqual((n['T10_C'],a['T10_C']),('335','325'));self.reject(n,atmosphere='air')
 def test_casein_air_second_decomposition_peak(self):
  r=self.exact(A,'ControlCotton','air');self.assertEqual((r['Tmax1_C'],r['Tmax2_C']),('341','494'));self.reject(r,Tmax1_C='494',Tmax2_C='341')
 def test_casein_char600_not_method700(self):
  r=self.exact(A,'Casein30Cotton','N2');self.assertEqual((r['R600_pct'],r['residue_temp_C'],r['TG_end_C']),('43.57','600','700'));self.assertFalse(r['R700_pct']);self.reject(r,residue_temp_C='700')
 def test_casein_air_control_residue_not_cone(self):
  r=self.exact(A,'ControlCotton','air');self.assertEqual(r['R600_pct'],'0.53');self.reject(r,R600_pct='3.6',residue_pct='3.6')
 def test_casein_wash_twenty_eight_states_excluded(self):
  rr=[r for r in self.source(A)if r['source_native_wash_count']];self.assertEqual(len(rr),28);self.assertTrue(all(not r['material_form_TGA']for r in rr));reported=[r for r in rr if r['LOI_pct']];self.assertEqual(len(reported),1);self.assertEqual((reported[0]['LOI_pct'],reported[0]['source_native_wash_count']),('26.7','40'));self.reject(self.exact(A,'Casein30Cotton','N2'),LOI_pct='26.7',washing_state='40nativeLCs')
 def test_casein_other_doses_not_curve_estimated(self):
  rr=[r for r in self.source(A)if r['pairing_status']=='held_other_dose_unannotated_LOI_without_own_TG'];self.assertEqual(len(rr),5);self.assertTrue(all(not r['LOI_pct']for r in rr))
 def test_casein_neat_fr_not_cotton_pair(self):
  r=next(r for r in self.source(A)if r['sample_state']=='NeatCaseinFR');self.assertNotEqual(r['pairing_status'],'verified_exact');self.assertFalse(r['LOI_pct']);self.assertEqual(r['source_raw_Tmax1_C'],'167')
 def test_pat_all_seven_identity_or_metric_holds(self):
  rr=self.source(B);self.assertEqual(len(rr),7);self.assertTrue(all(r['pairing_status']!='verified_exact'for r in rr));self.assertTrue(all(r['year']=='2013'for r in rr))
 def test_pat_control_labels_not_forced_equivalent(self):
  r=next(r for r in self.source(B)if r['sample_state']=='ControlPA66');self.assertEqual((r['source_raw_prose_first_loss_C'],r['source_raw_Table3_Tonset_C']),('360','386'));self.assertEqual((r['source_raw_prose_max_rate_C'],r['source_raw_Tinflection_C']),('440','450'));self.assertFalse(r['Tmax1_C']);self.assertFalse(r['Tonset_C'])
 def test_pat_wr_unknown_temperature_not700(self):
  r=next(r for r in self.source(B)if r['sample_state']=='HybridPA66'and not r['source_native_wash_count']and r['treatment_state']=='Initial own native group');self.assertEqual(r['source_raw_Wr_pct'],'9.14');self.assertFalse(r['residue_temp_C']);self.assertFalse(r['R700_pct']);self.assertIn('Unreported',r['source_raw_Wr_temperature'])
 def test_kss_nylon6_initial_four_air_only(self):
  rr=[r for r in self.source(C)if r['pairing_status']=='verified_exact'];self.assertEqual(len(rr),4);self.assertEqual({r['atmosphere']for r in rr},{'air'});self.assertTrue(all('nylon6'in r['composition']for r in rr));self.assertEqual({r['LOI_pct']for r in rr},{'24.7','29.4','29.6','30'})
 def test_kss_n2_curves_not_estimated(self):
  rr=[r for r in self.source(C)if r['pairing_status']=='held_N2_curve_only_exact_TG_metrics_unreported'];self.assertEqual(len(rr),4);self.assertTrue(all(r['atmosphere']=='N2'and not r['Tmax1_C']for r in rr))
 def test_kss_two_decomposition_peaks_not_melting(self):
  r=self.exact(C,'KSS5Nylon6','air');self.assertEqual((r['Tmax1_C'],r['Tmax2_C']),('435','536'));self.assertFalse(r['T5_C']);self.assertFalse(r['T10_C']);self.assertEqual(r['Tonset_C'],'390');self.reject(r,Tmax1_C='221')
 def test_kss_end468_not_char_temperature(self):
  r=self.exact(C,'ControlNylon6','air');self.assertEqual((r['source_Tend_C'],r['TG_end_C']),('468','600'));self.assertFalse(r['residue_temp_C']);self.assertFalse(r['R600_pct']);self.reject(r,residue_temp_C='468')
 def test_kss_fixed_and_washed_states_not_initial(self):
  rr=[r for r in self.source(C)if r['source_native_wash_count']];self.assertEqual(len(rr),4);self.assertEqual({r['LOI_pct']for r in rr},{'26.9','29.7','29.6','28.5'});self.assertTrue(all(not r['material_form_TGA']for r in rr));self.reject(self.exact(C,'KSS10Nylon6','air'),LOI_pct='28.5',washing_state='40nativecycles')
 def test_invalid_specimen_or_rate_rejected(self):
  r=self.exact(C,'KSS10Nylon6','air');self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='Neat KSS powder')));self.assertTrue(pairing.evidence_issues(dict(r,heating_rate_C_min='0')))
if __name__=='__main__':unittest.main()
