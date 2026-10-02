"""Reject treated-dose guesses, cross-wash joins and conflicting residual values."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b134/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261002_b134_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing,validate_tg_loi as v
A='10.1002/mame.202000624';B='10.1002/app.32319'
class TextileB134Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def source(self,d):return[r for r in self.rows if r['DOI']==d]
 def exact(self,d,s,g):return next(r for r in self.source(d)if r['sample_state']==s and r['atmosphere']==g and r['pairing_status']=='verified_exact')
 def reject(self,r,**kw):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**kw)))
 def test_fourstates_sevenconditions_not31facts(self):
  z=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(z['errors']);self.assertEqual((z['verified_exact_sample_states'],z['verified_exact_condition_records']),(4,7));self.assertEqual(len(self.rows),31)
 def test_24held_facts_without_chosen_tg(self):
  rr=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(rr),24);self.assertTrue(all(all(not r[k]for k in pairing.TG_FIELDS)for r in rr))
 def test_mame_only_three_initialgroups_paired(self):
  rr=[r for r in self.source(A)if r['pairing_status']=='verified_exact'];self.assertEqual(len(rr),6);self.assertEqual({r['sample_state']for r in rr},{'PristineCotton','TABLoadedCotton','TABPDACotton'})
 def test_ta_only_two_tgconditions_no_borrowed_loi(self):
  rr=[r for r in self.source(A)if r['sample_state']=='TALoadedCotton'];self.assertEqual(len(rr),2);self.assertTrue(all(not r['LOI_pct']and r['pairing_status']!='verified_exact'for r in rr));self.assertEqual({r['atmosphere']for r in rr},{'N2','air'})
 def test_mame_t5_not_t10_or_generic_onset(self):
  r=self.exact(A,'TABPDACotton','N2');self.assertEqual(r['T5_C'],'255');self.assertFalse(r['T10_C']);self.assertFalse(r['Tonset_C']);self.reject(r,T5_C='',T10_C='255')
 def test_mame_airandn2_not_crossed(self):
  r=self.exact(A,'TABPDACotton','N2');a=self.exact(A,'TABPDACotton','air');self.assertEqual((r['T5_C'],a['T5_C']),('255','306'));self.reject(r,atmosphere='air');self.assertEqual(a['Tmax2_C'],'488')
 def test_three_air_dtg_peaks_not_merged(self):
  r=self.exact(A,'TABLoadedCotton','air');self.assertEqual((r['Tmax1_C'],r['Tmax2_C'],r['Tmax3_C']),('310','457','551'));self.reject(r,Tmax1_C='551',Tmax3_C='310');self.assertFalse(self.exact(A,'PristineCotton','air')['Tmax2_C'])
 def test_mame_air_residue_conflicts_raw_only(self):
  rr=[r for r in self.source(A)if r['atmosphere']=='air'and r['pairing_status']=='verified_exact'];self.assertTrue(all(not r['R800_pct']and not r['residue_pct']and not r['residue_temp_C']for r in rr));r=self.exact(A,'TABPDACotton','air');self.assertEqual(r['source_raw_R800_pct'],'27.9');self.reject(r,R800_pct='27.9',residue_temp_C='800')
 def test_mame_n2_residue_not_cone_residue(self):
  r=self.exact(A,'TABPDACotton','N2');self.assertEqual((r['R800_pct'],r['residue_temp_C']),('48.9','800'));self.reject(r,R800_pct='28.8',residue_pct='28.8');self.reject(r,residue_temp_C='600')
 def test_mame_main20_bothgases_not_tgir_model(self):
  r=self.exact(A,'TABPDACotton','air');self.assertEqual((r['heating_rate_C_min'],r['TG_start_C'],r['TG_end_C']),('20','50','800'));self.assertIn('modelunreported',r['TGA_instrument']);self.assertIn('notmaininstrument',r['source_TG_mass_flow_pan']);self.reject(r,heating_rate_C_min='10')
 def test_mame_fifteen_washed_lois_no_washed_tg(self):
  rr=[r for r in self.source(A)if r['source_native_wash_count']];self.assertEqual(len(rr),15);self.assertEqual({r['source_native_wash_count']for r in rr},{'2','4','6','8','10'});self.assertTrue(all(not r['material_form_TGA']and r['pairing_status']!='verified_exact'for r in rr));self.reject(self.exact(A,'TABPDACotton','N2'),LOI_pct='24',washing_state='10nativeLCs;AATCC61-2006')
 def test_si403_unread_not_assumed_missing_measurements(self):
  self.assertTrue(all('HTTP403' in r['supplement_review_status']and'unread'in r['supplement_review_status']for r in self.source(A)))
 def test_app_only_own_control_onset390_paired(self):
  r=self.exact(B,'UntreatedPA66','air');self.assertEqual((r['LOI_pct'],r['Tonset_C']),('22.7','390'));self.assertFalse(r['T5_C']);self.assertFalse(r['T10_C']);self.assertFalse(r['Tmax1_C']);self.reject(r,Tonset_C='',T5_C='390')
 def test_app_no_computed_control426(self):
  r=self.exact(B,'UntreatedPA66','air');self.assertIn('do notcompute426',r['source_control_DTG_description']);self.reject(r,Tmax1_C='426')
 def test_app_hybrid456_held_unresolved_addon_not_exactpair(self):
  r=next(r for r in self.source(B)if r['sample_state']=='TEOAMAnPA66'and r['treatment_state']=='Initial own native group');self.assertEqual((r['LOI_pct'],r['source_TableIII_addon_pct'],r['source_raw_Tmax_C']),('29.1','6.6','456'));self.assertIn('loading_join_unresolved',r['pairing_status']);self.assertFalse(r['Tmax1_C']);self.assertFalse(r['R600_pct']);self.assertEqual(r['source_raw_residue_pct'],'13.1')
 def test_app_fourwashed_treated_states_held(self):
  rr=[r for r in self.source(B)if r['source_native_wash_count']];self.assertEqual(len(rr),4);self.assertEqual({r['LOI_pct']for r in rr},{'25.7','23.6','22.5','22'});self.assertTrue(all(not r['material_form_TGA']and r['pairing_status']!='verified_exact'for r in rr));self.assertTrue(all('Roomtemperature'in r['source_wash_method']for r in rr))
 def test_app_staticair10_not_assumed600_temperature_end(self):
  r=self.exact(B,'UntreatedPA66','air');self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['source_TG_mass_range_mg']),('air','10','3-5'));self.assertFalse(r['TG_end_C']);self.assertFalse(r['residue_temp_C']);self.assertIn('plot600notmethodendpoint',r['source_TG_temperature_range_pan_flow']);self.reject(r,atmosphere='N2')
 def test_invalid_specimen_form_and_rate_rejected(self):
  r=self.exact(A,'TABPDACotton','N2');self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='Neat borax powder')));self.assertTrue(pairing.evidence_issues(dict(r,heating_rate_C_min='0')))
if __name__=='__main__':unittest.main()
