"""Protect native T5, missing TG evidence and original-source numerical conflicts."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b163/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261004_b163_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing;import validate_tg_loi as v
A='10.1007/s12221-023-00408-0';B='10.1007/s13726-024-01287-9';C='10.1007/s10570-023-05512-1'
class TextileB163Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as handle:cls.rows=list(csv.DictReader(handle))
 def subset(self,doi):return[r for r in self.rows if r['DOI']==doi]
 def find(self,doi,sample,gas=None):return next(r for r in self.subset(doi)if r['sample_state']==sample and(gas is None or r['atmosphere']==gas))
 def accepted(self):return[r for r in self.rows if r['pairing_status']=='verified_exact']
 def noTG(self,row):self.assertTrue(all(not row.get(k)for k in pairing.TG_FIELDS))
 def test_two_states_two_conditions_not60facts(self):
  p=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(p['errors']);self.assertEqual((p['verified_exact_sample_states'],p['verified_exact_condition_records']),(2,2));self.assertEqual(len(self.rows),60)
 def test_all58held_excluded(self):
  held=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(held),58);self.assertEqual([sum(r['DOI']==d for r in held)for d in[A,B,C]],[10,27,21]);self.assertTrue(all(pairing.evidence_issues(r)for r in held))
 def test_fingerprints_reject_changes_to_numbers_and_states(self):
  for r in self.accepted():
   self.assertFalse(pairing.evidence_issues(r))
   for k,value in [('LOI_pct','99'),('T5_C','300'),('Tmax2_C','555'),('R600_pct','77'),('atmosphere','N2'),('heating_rate_C_min','20'),('washing_state','50LC'),('sample_state','otherdose')]:self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**{k:value})))
 def test_fabric_not_fiber(self):
  for r in self.accepted():self.assertEqual(r['material_form_TGA'],'cotton fabric');self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='cotton fiber')))
 def test_CDPST_native_T5_not_Tonset_despite_body_wording(self):
  for sample,value in [('CF','233.7'),('20','186.6')]:
   r=self.find(A,'CDPST_'+sample+'_initial');self.assertEqual(r['T5_C'],value);self.assertFalse(r.get('Tonset_C'));self.assertFalse(r.get('T10_C'));self.assertIn('T5=5pctmassloss',r['source_metric_definition']);self.assertIn('notTonset',r['source_metric_definition'])
 def test_CDPST_two_reported_decomposition_peaks_not_water(self):
  r=self.find(A,'CDPST_CF_initial');self.assertEqual((r['Tmax1_C'],r['Tmax2_C']),('302.4','380.5'));r=self.find(A,'CDPST_20_initial');self.assertEqual((r['Tmax1_C'],r['Tmax2_C']),('315.6','528.7'));self.assertIn('notwaterunder100',r['pairing_evidence'])
 def test_CDPST_R600_not_program_end_or_bulkFR(self):
  for sample,value in [('CF','8.7'),('20','24.6')]:
   r=self.find(A,'CDPST_'+sample+'_initial');self.assertEqual((r['R600_pct'],r['residue_temp_C']),(value,'600'));self.assertFalse(r.get('TG_start_C'));self.assertFalse(r.get('TG_end_C'));self.assertIn('not600Cprogramend',r['source_residue_definition']);self.assertNotEqual(r['R600_pct'],'46.5')
 def test_CDPST_qualitative_negligible_not_zero(self):
  r=self.find(A,'CDPST_CF_initial');self.assertEqual(r['R600_pct'],'8.7');self.assertIn('bodyCFnegligiblecharqualitativekept',r['source_residue_definition']);self.assertIn('notassumed0',r['source_residue_definition'])
 def test_CDPST_methods_known_gas_ramp_and_LOI_dimensions(self):
  for r in self.accepted():self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['TGA_instrument'],r['LOI_standard'],r['source_LOI_dimensions_mm']),('air','10','NETZSCH TG209F3','GB/T5454-1997','58x150'));self.assertEqual(r['source_repeats_mass_pan_flow'],'unreported')
 def test_CDPST_otherfour_dose_LOI_NO_borrowedTG(self):
  for dose,loi in [('10','23.7'),('15','26.5'),('25','29.6'),('30','31.1')]:r=self.find(A,'CDPST_'+dose+'_initial');self.noTG(r);self.assertEqual(r['LOI_pct'],loi)
 def test_CDPST_all_six_washed_states_NO_initialTG(self):
  expected=[('10','28.6'),('20','28'),('30','27.5'),('40','26.8'),('50','26.3'),('60','25.3')]
  for cycle,loi in expected:r=self.find(A,'CDPST_20_after'+cycle+'LC');self.noTG(r);self.assertEqual(r['LOI_pct'],loi);self.assertIn('notmultipliedbyfive',r['source_LC_definition'])
  self.assertEqual(len([r for r in self.subset(A)if r['treatment_state']=='washed']),6);self.assertFalse(any('after0LC'in r['sample_state']for r in self.subset(A)))
 def test_CDPST_control_pretreatment_not_assumed_from_treated_method(self):
  r=self.find(A,'CDPST_CF_initial');self.assertEqual(r['washing_state'],'initial_unwashed_control_preparation_unreported');self.assertIn('exactcontrolCFapplicationnotseparatelyreported',r['source_control_cleaning_scope'])
 def test_AHEDPA_all27_LOI_facts_no_numericTG(self):
  self.assertEqual(len(self.subset(B)),27)
  for r in self.subset(B):self.noTG(r);self.assertNotEqual(r['pairing_status'],'verified_exact')
 def test_AHEDPA_all_initial_own_LOIs_not_intro_or_prior_papers(self):
  for sample,value in [('Control','18.4'),('10','34.4'),('20','38.2'),('30','40.3'),('40','41.7')]:r=self.find(B,'AHEDPA_'+sample+'_initial');self.assertEqual(r['LOI_pct'],value)
 def test_AHEDPA_Table2_all_twenty_washed_LOIs(self):
  rows=[r for r in self.subset(B)if '_Table2'in r['sample_state']];self.assertEqual(len(rows),20)
  for r in rows:self.noTG(r);self.assertIn('No2A',r['washing_state'])
  self.assertEqual(self.find(B,'AHEDPA_20_after6LC_Table2')['LOI_pct'],'27.8');self.assertEqual(self.find(B,'AHEDPA_40_after10LC_Table2')['LOI_pct'],'28.2');self.assertEqual(self.find(B,'AHEDPA_30_after10LC_Table2')['LOI_pct'],'26.2')
 def test_AHEDPA_body_cycle_conflicts_not_5x_mapping(self):
  for sample,loi in [('20_after30LC','27.8'),('40_after50LC','28.2')]:
   r=self.find(B,'AHEDPA_'+sample+'_bodyconflict');self.assertEqual(r['LOI_pct'],loi);self.noTG(r);self.assertIn('noinferred5xmapping',r['source_LC_definition']);self.assertIn('withoutsourceequivalenceproof',r['source_cycle_conflicts'])
 def test_AHEDPA_recipe_and_grafting_conflicts_not_corrected(self):
  r=self.find(B,'AHEDPA_10_initial');self.assertEqual(r['source_Dgr_pct'],'11.21');self.assertIn('vsTable3/body10.21',r['source_recipe_conflicts']);self.assertIn('Methods15pctDCDA',r['source_recipe_conflicts']);self.assertIn('optimized/conclusion40pct',r['source_recipe_conflicts']);self.assertIn('140C150min',r['treatment_method']);self.assertIn('Table1optimization150C1h',r['treatment_method'])
 def test_DETAPAP_all_initial_conditions_held_for_LOI_conflict(self):
  for sample,table,body in [('Control','18.2','18.0'),('36','49.5','49.7')]:
   for gas in ['N2','air']:
    r=self.find(C,'DETAPAP_'+sample+'_initial',gas);self.assertEqual((r['LOI_pct'],r['source_LOI_body_raw']),(table,body));self.assertIn('conflict',r['pairing_status']);self.assertIn('WholeinitialN2/airconditionsheld',r['source_LOI_conflicts']);self.assertTrue(pairing.evidence_issues(r))
 def test_DETAPAP_N2_TG_native_R600_not_700_programend(self):
  r=self.find(C,'DETAPAP_Control_initial','N2');self.assertEqual((r['Tmax1_C'],r['R600_pct'],r['source_DTG_pct_per_C']),('375','9.72','2.47'));r=self.find(C,'DETAPAP_36_initial','N2');self.assertEqual((r['R600_pct'],r['residue_temp_C'],r['TG_end_C']),('42.8','600','700'));self.assertFalse(r.get('Tmax1_C'))
 def test_DETAPAP_air_curve_only_not_estimated_zero_residue(self):
  for sample in ['Control','36']:
   r=self.find(C,'DETAPAP_'+sample+'_initial','air');self.noTG(r);self.assertIn('curveonly',r['pairing_status']);self.assertFalse(r['source_DTG_pct_per_C'])
 def test_DETAPAP_T8_unreported_not_T5_T10(self):
  for sample in ['Control','36']:
   r=self.find(C,'DETAPAP_'+sample+'_initial','N2');self.assertEqual(r['source_T8_criterion_massloss_pct'],'8');self.assertFalse(r.get('T5_C'));self.assertFalse(r.get('T10_C'));self.assertFalse(r.get('T8_C'));self.assertIn('nocanonicalT5/T10created',r['source_T8_value_hold'])
 def test_DETAPAP_otherdose_initial_and_all15_washed_NO_initialTG(self):
  for dose,loi in [('12','43.3'),('24','48.9')]:r=self.find(C,'DETAPAP_'+dose+'_initial');self.noTG(r);self.assertEqual(r['LOI_pct'],loi)
  rows=[r for r in self.subset(C)if r['treatment_state']=='washed'];self.assertEqual(len(rows),15)
  for r in rows:self.noTG(r);self.assertIn('notmultipliedbyfive',r['source_LC_definition'])
 def test_DETAPAP_Table4_uncertainty_difference_not_new_state(self):
  r=self.find(C,'DETAPAP_24_initial');self.assertEqual((r['source_LOI_uncertainty_pct'],r['source_Table4_own24_LOI_uncertainty_pct']),('0.1','0.3'));r=self.find(C,'DETAPAP_24_after50LC');self.assertEqual((r['LOI_pct'],r['source_LOI_uncertainty_pct'],r['source_Table4_own24_LOI_uncertainty_pct']),('41.3','0.2','0.3'));self.assertFalse(any('DETA-P_prior'in r['sample_state']for r in self.subset(C)))
 def test_DETAPAP_SI_no_T8_or_LOI_correction(self):
  r=self.find(C,'DETAPAP_Control_initial','N2');self.assertIn('zeroSItables',r['source_SI_review']);self.assertIn('noordinaryTG/LOIconflictcorrection/numericT8',r['source_SI_review']);self.assertIn('Embeddedimagesunread',r['source_SI_review'])
 def test_public_facts_no_privatepaths_and_valid_review_dates(self):
  for r in self.rows:self.assertRegex(r['evidence_reviewed_at'],r'^\d{4}-\d{2}-\d{2}$');self.assertFalse(any(('/'+'Volumes'+'/')in str(x)or('/'+'Users'+'/')in str(x)or('smb'+':'+chr(47)*2)in str(x)for x in r.values()))
if __name__=='__main__':unittest.main(verbosity=2)
