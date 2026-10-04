"""Source-specific guards for PCS and DSCFT cotton and excluded DES sample facts."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo' if private else P.parent
F=P/'staged-local-textile-b156/publication_proposed.csv' if private else R/'data/incoming/verified_source_batch_20261004_b156_local_textile.csv'
sys.path.insert(0,str(R/'scripts'))
import pairing
import validate_tg_loi as v
A='10.1007/s10570-021-04216-8';B='10.1007/s10570-021-04235-5';C='10.1007/s10570-022-04566-x'
class TextileB156Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='') as h:cls.rows=list(csv.DictReader(h))
 def pcs(self,label='FR3',gas='N2'):
  return next(r for r in self.rows if r['DOI']==C and r['pairing_status']=='verified_exact' and 'Own'+label+'initial' in r['sample_state'] and r['atmosphere']==gas)
 def dscft(self):return next(r for r in self.rows if r['DOI']==B and r['pairing_status']=='verified_exact')
 def reject(self,r,**changes):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**changes)))
 def test_five_states_nine_conditions_not34facts(self):
  p=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(p['errors']);self.assertEqual((p['verified_exact_sample_states'],p['verified_exact_condition_records']),(5,9));self.assertEqual(len(self.rows),34)
 def test_all25held_facts_excluded(self):
  rows=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual([sum(r['DOI']==d for r in rows) for d in [A,B,C]],[14,8,3]);self.assertTrue(all(pairing.evidence_issues(r) for r in rows))
 def test_pcs_nitrogen_native_profiles(self):
  for label,vals in [('Control',(269.2,349.4,3.1)),('FR1',(266.9,316.1,14.4)),('FR2',(262.6,314,24.7)),('FR3',(246.5,303.4,36.3))]:self.assertEqual(tuple(float(self.pcs(label)[k]) for k in ['T5_C','Tmax1_C','R700_pct']),vals)
 def test_pcs_air_native_profiles(self):
  for label,vals in [('Control',(244.5,305.3,1.2)),('FR1',(265.4,296.5,2.6)),('FR2',(256.5,295.1,6.3)),('FR3',(240.5,291.3,6.9))]:self.assertEqual(tuple(float(self.pcs(label,'air')[k]) for k in ['T5_C','Tmax1_C','R700_pct']),vals)
 def test_pcs_t5_not_onset_or_tmax_and_t10_unreported(self):
  r=self.pcs();self.assertFalse(r.get('T10_C'));self.assertFalse(r.get('Tonset_C'));self.reject(r,Tmax1_C='246.5');self.reject(r,Tonset_C='246.5');self.reject(r,T10_C='246.5')
 def test_gas_and_ramp_changes_require_review(self):
  for r in [self.pcs(),self.dscft()]:self.assertEqual(r['heating_rate_C_min'],'10');self.reject(r,atmosphere='air');self.reject(r,heating_rate_C_min='20')
 def test_residue_temperatures_not_cross_assigned(self):
  p=self.pcs();d=self.dscft();self.assertEqual((p['residue_temp_C'],d['residue_temp_C']),('700','800'));self.reject(p,residue_temp_C='800');self.reject(d,residue_temp_C='700')
 def test_pcs_plain_TG_methods_flow_not_from_TGIR(self):
  r=self.pcs();self.assertEqual((r['TG_start_C'],r['TG_end_C'],r['source_TG_flow_mL_min']),('40','700','20'));self.assertIn('independentlyspecified',r['source_TGIR_method'])
 def test_pcs_four_native_loi_values_and_uncertainty(self):
  for label,loi in [('Control','19'),('FR1','24.6'),('FR2','25.7'),('FR3','28.3')]:r=self.pcs(label);self.assertEqual((r['LOI_pct'],r['LOI_uncertainty_pct']),(loi,'0.2'));self.assertIn('SD/SE/repeatsunreported',r['source_LOI_uncertainty_definition'])
 def test_pcs_own_dimensions50_not58(self):
  r=self.pcs();self.assertEqual(r['source_LOI_dimensions_mm'],'150x50');self.assertEqual(r['LOI_standard'],'ASTMD2863-2000')
 def test_pcs_bath_dose_not_final_WG_fraction(self):
  for label,dose,wg in [('FR1','PCS5wtbath','11.3'),('FR2','PCS7.5wtbath','12.7'),('FR3','PCS10wtbath','14.1')]:r=self.pcs(label);self.assertIn(dose,r['composition']);self.assertEqual(r['source_weight_gain_wt_pct'],wg);self.assertIn('finalcomponentfractionsunknown',r['composition'])
 def test_pcs_control_not_assigned_fr_cure(self):
  self.assertIn('noPCS',self.pcs('Control')['composition']);self.assertIn('FRcureprotocolnotassigned',self.pcs('Control')['treatment_method']);self.assertIn('180C10min',self.pcs()['treatment_method']);self.assertIn('110g/m2',self.pcs()['material_form'])
 def test_pcs_acid_identity_and_WG_formula_conflicts_retained(self):
  r=self.pcs();self.assertIn('phosphorousacidvsPCSpreparationphosphoricacid',r['source_acid_identity_conflict']);self.assertIn('notassignoxidationstate',r['source_acid_identity_conflict']);self.assertIn('notrecomputed',r['source_weight_gain_formula_conflict'])
 def test_pcs_washed_loi_not_initial_tg(self):
  rows=[r for r in self.rows if r['DOI']==C and r['pairing_status']!='verified_exact'];self.assertEqual([r['LOI_pct'] for r in rows],['21','23','23.5']);self.assertTrue(all(not r.get('Tmax1_C') and not r.get('R700_pct') for r in rows));self.reject(self.pcs(),LOI_pct='23.5');self.reject(self.pcs(),washing_state='10LC')
 def test_pcs_native_washed_WG_conflict_retained(self):
  r=next(r for r in self.rows if r['DOI']==C and r['sample_state']=='FR1 after10launderingcycles');self.assertEqual(r['source_weight_gain_after10LC_pct'],'7.8');self.assertIn('versusbody7.5',r['source_washed_FR1_WG_conflict']);self.assertIn('equiv5cycles',r['washing_state'])
 def test_dscft_native_T5_T10_Tmax_DTG_residue(self):
  r=self.dscft();self.assertEqual(tuple(float(r[k]) for k in ['T5_C','T10_C','Tmax1_C','source_DTGmax_rate_pct_per_C','R800_pct']),(258,277,295,1.4,42.74));self.assertIn('notpercentpermin',r['source_DTG_rate_definition']);self.reject(r,Tmax1_C='258')
 def test_dscft_conflicting_start_unselected_known_rate_gas(self):
  r=self.dscft();self.assertFalse(r['TG_start_C']);self.assertIn('Methods35',r['source_TG_start_conflict']);self.assertIn('body40',r['source_TG_start_conflict']);self.assertEqual((r['heating_rate_C_min'],r['atmosphere'],r['TG_end_C']),('10','N2','800'));self.assertFalse(r['source_TG_flow_mL_min'])
 def test_dscft_only_selected300_not350_same_loi(self):
  r=self.dscft();self.assertIn('300gL',r['sample_state']);self.assertIn('finalchoice300gL',r['pairing_evidence']);other=next(x for x in self.rows if x['DOI']==B and x['sample_state']=='DSCFT350gL initial cotton fabric');self.assertEqual(other['LOI_pct'],'28.2');self.assertFalse(other['Tmax1_C']);self.assertNotEqual(other['pairing_status'],'verified_exact')
 def test_dscft_control_no_own_loi_cannot_borrow_intro18(self):
  r=next(r for r in self.rows if r['DOI']==B and r['sample_state']=='Untreated initial cotton fabric');self.assertFalse(r['LOI_pct']);self.assertEqual(r['Tmax1_C'],'368');self.assertIn('intro18generic',r['source_location']);self.assertIn('own_control_LOI_unreported',r['pairing_status'])
 def test_dscft_PBTCA_and_nativeinstrument_uncertainty(self):
  r=self.dscft();self.assertIn('PBTCAamountunreported',r['composition']);self.assertIn('identityconflictretained',r['TGA_instrument']);self.assertIn('weave/gsmunreported',r['material_form']);self.assertEqual(r['source_native_Table1_Weight_pct'],'15.48')
 def test_dscft_three_washedstates_no_own_tg(self):
  rows=[r for r in self.rows if r['DOI']==B and 'after' in r['sample_state']];self.assertEqual([r['LOI_pct'] for r in rows],['27.1','25.9','24.2']);self.assertTrue(all(not r['Tmax1_C'] for r in rows));self.assertTrue(all('duration/detergent/equivcyclesunreported' in r['washing_state'] for r in rows))
 def test_DES_weightloss220_not_residue_or_T40(self):
  rows=[r for r in self.rows if r['DOI']==A and r['source_reported_weight_loss_at220C_pct']];self.assertEqual([r['source_reported_weight_loss_at220C_pct'] for r in rows],['40','35']);self.assertTrue(all(not r.get(k) for r in rows for k in pairing.TG_FIELDS));self.assertTrue(all('notexactT40' in r['source_reported_weight_loss_qualifier'] for r in rows))
 def test_DES_thickness_replicates_loading_not_newpairs(self):
  rows=[r for r in self.rows if r['DOI']==A];self.assertTrue(all(r['pairing_status']!='verified_exact' for r in rows));self.assertEqual(len([r for r in rows if r['source_LOI_reported_replica_rows']=='5']),6);self.assertEqual([r['LOI_pct'] for r in rows if 'thickB' in r['sample_state']],['40.2','53.4']);self.assertTrue(any('Primary2-3minvsSI S1220s' in r['source_dip_time_conflict'] for r in rows))
 def test_DES_wash_weightloss_not_tg_residue(self):
  rows=[r for r in self.rows if r['DOI']==A and r['source_wash_weight_loss_pct_notTG']];self.assertEqual([r['source_wash_weight_loss_pct_notTG'] for r in rows],['64.88','27.78','55.09','19.69']);self.assertTrue(all(not r['Tmax1_C'] and not r.get('residue_pct') for r in rows))
 def test_conechar_near_TGchar_not_substituted(self):
  r=self.pcs('FR2');self.assertEqual(r['R700_pct'],'24.7');self.reject(r,R700_pct='24.6');self.reject(self.pcs('Control'),R700_pct='6');self.assertFalse(r.get('residue_at_Tmax1_pct'))
 def test_approved_values_and_identity_bound_to_review(self):
  rows=[r for r in self.rows if r['pairing_status']=='verified_exact'];self.assertEqual(len(rows),9)
  for r in rows:self.assertFalse(pairing.evidence_issues(r));self.reject(r,LOI_pct=str(float(r['LOI_pct'])+1));self.reject(r,sample_state='Remoldedpolymer-sheet')
if __name__=='__main__':unittest.main()
