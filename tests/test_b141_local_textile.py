"""Prevent dose, gas, residue-temperature and historical metric reinterpretation."""
import csv,sys,unittest
from decimal import Decimal
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b141/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261003_b141_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing,validate_tg_loi as v
A='10.1016/j.carbpol.2018.08.078';B='10.1002/app.1972.070160716'
class TextileB141Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def exact(self,s='Cotton-AHEDPA30 reportedLC0',gas='N2'):return next(r for r in self.rows if r['DOI']==A and r['sample_state']==s and r.get('atmosphere')==gas and r['pairing_status']=='verified_exact')
 def reject(self,r,**kw):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**kw)))
 def test_two_states_four_gas_tests_not_thirtynine_facts(self):
  z=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(z['errors']);self.assertEqual((z['verified_exact_sample_states'],z['verified_exact_condition_records']),(2,4));self.assertEqual(len(self.rows),39)
 def test_thirtyfive_holds_no_canonical_tg(self):
  rr=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(rr),35);self.assertTrue(all(all(not r[k]for k in pairing.TG_FIELDS)for r in rr))
 def test_native_tonset_not_t5_or_t10(self):
  r=self.exact();self.assertEqual(r['Tonset_C'],'201.2');self.assertFalse(r['T5_C']);self.assertFalse(r['T10_C']);self.reject(r,Tonset_C='',T5_C='201.2')
 def test_air_nitrogen_columns_cannot_swap(self):
  r=self.exact(gas='air');self.assertEqual((r['Tonset_C'],r['Tmax1_C'],r['R600_pct']),('223.6','302.8','14.9'));self.reject(r,Tonset_C='201.2',Tmax1_C='299.0',R600_pct='44.4')
 def test_control_air_second_peak_is_char_oxidation(self):
  r=self.exact('Cotton-Control initial','air');self.assertEqual((r['source_Tonset2_C'],r['Tmax2_C']),('443.5','467.6'));self.assertFalse(self.exact('Cotton-Control initial')['Tmax2_C']);self.reject(self.exact('Cotton-Control initial'),Tmax2_C='467.6')
 def test_treated_air_dashes_not_zero_peaks(self):
  r=self.exact(gas='air');self.assertFalse(r['Tmax2_C']);self.assertFalse(r['source_Tonset2_C']);self.reject(r,Tmax2_C='0')
 def test_air_r600_r800_not_interchangeable(self):
  r=self.exact(gas='air');self.assertEqual((r['R600_pct'],r['R800_pct'],r['residue_temp_C']),('14.9','0.5','800'));self.reject(r,R800_pct='14.9',residue_temp_C='600')
 def test_zero_control_air_residue_is_measured_value(self):
  r=self.exact('Cotton-Control initial','air');self.assertEqual(r['R800_pct'],'0');self.assertEqual(r['R600_pct'],'0.6');self.assertFalse(pairing.evidence_issues(r));self.reject(r,R800_pct='0.6')
 def test_nitrogen_residue_at600_not800(self):
  r=self.exact();self.assertEqual((r['R600_pct'],r['residue_temp_C']),('44.4','600'));self.assertFalse(r['R800_pct']);self.reject(r,residue_temp_C='800')
 def test_main_40_to800_not_tgir_40_to600(self):
  r=self.exact();self.assertEqual((r['TG_start_C'],r['TG_end_C']),('40','800'));self.assertIn('TGIR8mg40-600Cnotborrowed',r['source_TG_mass_pan_flow']);self.assertEqual(r['heating_rate_C_min'],'20');self.reject(r,heating_rate_C_min='10')
 def test_initial_process_rinse_not_laundering(self):
  r=self.exact();self.assertIn('runningwaterrinse80Cdry',r['treatment_method']);self.assertIn('Initial0durabilitycycles',r['washing_state']);self.reject(r,washing_state='After50durabilitylaunders')
 def test_dose30_not_other_concentration(self):
  r=self.exact();self.assertEqual((r['LOI_pct'],r['source_initial_WG_pct']),('41.5','20.11'));self.reject(r,LOI_pct='42.6');self.assertIn('basisunknownnotfinalmassfraction',r['composition'])
 def test_twentythree_other_dose_washed_states_unpaired(self):
  rr=[r for r in self.rows if r['pairing_status']=='held_LOI_without_own_matching_dose_or_washed_TG'];self.assertEqual(len(rr),23);self.assertTrue(all(not r['Tmax1_C']and not r['R600_pct']for r in rr));self.assertEqual(sum(r['source_reported_LCs']=='0'for r in rr),3)
 def test_washed_weightgain_does_not_create_duplicate_samples(self):
  rr=[r for r in self.rows if r['DOI']==A and r['sample_state']=='Cotton-AHEDPA30 reportedLC50'];self.assertEqual(len(rr),1);self.assertEqual((rr[0]['LOI_pct'],rr[0]['source_WG_after50LC_pct']),('26.2','9.59'));self.assertFalse(rr[0]['R600_pct'])
 def test_neat_additive_tg_not_cotton_loi(self):
  rr=[r for r in self.rows if r['sample_state']=='NeatAHEDPA'];self.assertEqual(len(rr),2);self.assertTrue(all(not r['LOI_pct']and not r['Tmax1_C']for r in rr));self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(self.exact(),material_form_TGA='NeatAHEDPApowder')))
 def test_accepted_manuscript_not_final_year(self):
  r=self.exact();self.assertFalse(r['year']);self.assertIn('accepted2018-08-19',r['source_document_version']);self.assertIn('finalVORnotreviewed',r['source_document_version'])
 def test_si_identity_not_absent_title_authors(self):
  r=self.exact();self.assertIn('SInotitleauthorsnotclaimedmatched',r['source_SI_identity']);self.assertIn('S0144861718309871',r['supplement_source_url']);self.assertIn('SupplementaryTableS1',r['TG_locator'])
 def test_historical_halfvolatile_not_assumed_t50(self):
  rr=[r for r in self.rows if r['DOI']==B];self.assertEqual(len(rr),10);self.assertTrue(all(not r['T50_C']and 'massbasis' in r['source_native_metric_limit']for r in rr));self.assertEqual(next(r for r in rr if r['sample_state']=='Control initial')['source_half_volatilization_C'],'334')
 def test_historical_oxygen_fraction_exact_unit_conversion_only(self):
  rr=[r for r in self.rows if r['DOI']==B];self.assertTrue(all(Decimal(r['LOI_pct'])==Decimal(r['source_LOI_native_fraction'])*100 for r in rr));self.assertEqual(next(r for r in rr if r['sample_state']=='Control after5launder')['LOI_pct'],'18.2')
 def test_historical_tg_not_dsc_or_repaired_precursor(self):
  rr=[r for r in self.rows if r['DOI']==B];self.assertTrue(all('DuPont950N25C/min' in r['source_TG_method']and 'notDSC40C/min' in r['source_TG_method']and not r['residue_temp_C']for r in rr));cc=[r for r in rr if r['sample_state'].startswith('THPCcyanamide')];self.assertEqual(len(cc),2);self.assertTrue(all('phosphoniumhydroxideconflict' in r['source_chemical_limit']for r in cc))
if __name__=='__main__':unittest.main()
