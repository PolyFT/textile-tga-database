"""Protect printed residue temperatures, initial preparation and computed-LOI exclusions."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b160/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261004_b160_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing;import validate_tg_loi as v
A='10.1007/s10570-025-06440-y';B='10.1007/s10570-023-05226-4';C='10.1007/s10570-025-06683-9'
class TextileB160Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def subset(self,d):return[r for r in self.rows if r['DOI']==d]
 def find(self,d,s,gas=None):return next(r for r in self.subset(d)if r['sample_state']==s and(gas is None or r['atmosphere']==gas))
 def accepted(self):return[r for r in self.rows if r['pairing_status']=='verified_exact']
 def noTG(self,r):self.assertTrue(all(not r.get(k)for k in pairing.TG_FIELDS))
 def test_four_states_four_conditions_not43facts(self):
  p=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(p['errors']);self.assertEqual((p['verified_exact_sample_states'],p['verified_exact_condition_records']),(4,4));self.assertEqual(len(self.rows),43)
 def test_all39_holds_excluded(self):
  held=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(held),39);self.assertEqual([sum(r['DOI']==d for r in held)for d in[A,B,C]],[9,20,10]);self.assertTrue(all(pairing.evidence_issues(r)for r in held))
 def test_bound_fingerprints_reject_cross_state_or_numeric_change(self):
  for r in self.accepted():
   self.assertFalse(pairing.evidence_issues(r))
   for k,x in [('LOI_pct','99'),('residue_pct','77'),('sample_state','Otherdose'),('washing_state','after50LC'),('atmosphere','Ar'),('heating_rate_C_min','60')]:self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**{k:x})))
 def test_fabrics_not_independent_fibers(self):
  for r in self.accepted():self.assertEqual(r['material_form_TGA'],'cotton fabric');self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='cotton fiber')))
 def test_Banana_direct_remaining_mass_not_body_weightloss(self):
  for s,r400,r500 in [('FS1','0','0'),('FS6','40','26')]:
   r=self.find(A,'Banana_'+s+'_initial');self.assertEqual((r['R400_pct'],r['R500_pct']),(r400,r500));self.assertIn('NativeTables2/3/4',r['source_location']);self.assertIn('no100-minus-weightlossconversion',r['source_metric_rule'])
 def test_Banana_R500_not_end600(self):
  r=self.find(A,'Banana_FS6_initial');self.assertEqual((r['residue_pct'],r['residue_temp_C'],r['TG_end_C']),('26','500','600'));self.assertFalse(r.get('R600_pct'))
 def test_Banana_concentration_not_fabric_massloading(self):
  r=self.find(A,'Banana_FS6_initial');self.assertEqual(r['source_addon_pct'],'4.5');self.assertIn('200/300/400mLboiledto100mL',r['source_BPS_concentration_definition']);self.assertIn('notmasspercent/fabricloading',r['source_BPS_concentration_definition'])
 def test_Banana_generic330_and_water100_not_assigned_peaks(self):
  for s in ['FS1','FS6']:
   r=self.find(A,'Banana_'+s+'_initial');self.assertFalse(r.get('Tmax1_C'));self.assertFalse(r.get('T5_C'));self.assertFalse(r.get('T10_C'));self.assertIn('notassignedTmax',r['source_Tmax_hold'])
 def test_Banana_lowtemperature_remainingmass_aux_fields(self):
  r=self.find(A,'Banana_FS1_initial');self.assertEqual((r['source_remaining100_pct'],r['source_remaining250_pct'],r['source_remaining300_pct']),('90','86','83'));r=self.find(A,'Banana_FS6_initial');self.assertEqual(r['source_remaining100_pct'],'98');self.assertFalse(r.get('Tonset_C'))
 def test_Banana_otherfour_initial_LOI_no_borrowedTG(self):
  for s,loi in [('FS2','20.2'),('FS3','23.4'),('FS4','24.4'),('FS5','25.5')]:r=self.find(A,'Banana_'+s+'_initial');self.assertEqual(r['LOI_pct'],loi);self.noTG(r)
 def test_Banana_fivewashed_LOI_unknown_cyclecount(self):
  rows=[r for r in self.subset(A)if r['treatment_state']=='washed'];self.assertEqual([r['LOI_pct']for r in rows],['18.5','20.2','22.1','24.1','25'])
  for r in rows:self.noTG(r);self.assertIn('cyclecount_unreported',r['washing_state']);self.assertIn('ordinalscoresnotLCcount',r['source_wash_details'])
 def test_Banana_methods_own_conditioning_and_LOI_dimensions(self):
  r=self.find(A,'Banana_FS6_initial');self.assertEqual((r['TG_start_C'],r['heating_rate_C_min'],r['source_LOI_dimensions_mm']),('50','10','150x50'));self.assertIn('25C65pctRH',r['source_conditioning']);self.assertEqual(r['source_TG_mass_pan_flow_repeats'],'unreported')
 def test_own_source_control_LOIs_not_interchanged(self):
  self.assertEqual(self.find(A,'Banana_FS1_initial')['LOI_pct'],'18.3');self.assertEqual(self.find(B,'Proban_C0_initial','N2')['LOI_pct'],'17.2');self.assertNotEqual(self.find(A,'Banana_FS1_initial')['DOI'],self.find(B,'Proban_C0_initial','N2')['DOI'])
 def test_Proban_explicit_body_Tmax_R700(self):
  for s,tmax,res in [('C0','375','9.04'),('C40','321','34.67')]:
   r=self.find(B,'Proban_'+s+'_initial','N2');self.assertEqual((r['Tmax1_C'],r['R700_pct'],r['residue_temp_C']),(tmax,res,'700'));self.assertEqual(r['numeric_evidence_type'],'explicit_text');self.assertIn('OwnThermalperformanceanalyses',r['TG_locator']);self.assertFalse(r.get('T5_C'));self.assertFalse(r.get('Tonset_C'))
 def test_Proban_peroxide_is_own_initial_preparation(self):
  r=self.find(B,'Proban_C40_initial','N2');self.assertEqual(r['washing_state'],'initial_after_preparation_peroxide_rinse');self.assertIn('.01pctH2O290C60min',r['treatment_method']);self.assertIn('pH10.5-11',r['treatment_method']);self.assertIn('notextraagedstate',r['source_initial_peroxide_state']);r=self.find(B,'Proban_C0_initial','N2');self.assertIn('peroxideunassigned',r['treatment_method'])
 def test_Proban_WG_not_bath_weightpercent(self):
  r=self.find(B,'Proban_C40_initial','N2');self.assertEqual((r['source_weight_gain_wt_pct'],r['source_weight_gain_uncertainty_pct']),('28.5','0.2'));self.assertIn('bath20/30/40wt',r['treatment_method']);self.assertEqual(r['source_uncertainty_type'],'unreported')
 def test_Proban_two_air_curves_no_numeric_TG(self):
  rows=[r for r in self.subset(B)if r['atmosphere']=='air'];self.assertEqual(len(rows),2)
  for r in rows:self.noTG(r);self.assertIn('curve_only',r['pairing_status']);self.assertEqual((r['TG_start_C'],r['TG_end_C'],r['heating_rate_C_min']),('25','700','20'))
 def test_Proban_intermediate_and_otherdose_LOI_only(self):
  for s,loi in [('BGDETA-CF','17.3'),('C20','27'),('C30','29.4')]:r=self.find(B,'Proban_'+s+'_initial');self.noTG(r);self.assertEqual(r['LOI_pct'],loi)
 def test_Proban_all15washed_LOI_no_initialTG(self):
  rows=[r for r in self.subset(B)if r['treatment_state']=='washed'];self.assertEqual(len(rows),15)
  for r in rows:self.noTG(r);self.assertIn('NFPA2112-2012',r['washing_state']);self.assertIn('temp/time/detergentperLCunreported',r['source_wash_details'])
  self.assertEqual(self.find(B,'Proban_C40_after50LC')['LOI_pct'],'29.7');self.assertEqual(self.find(B,'Proban_C30_after50LC')['LOI_pct'],'28.8');self.assertEqual(self.find(B,'Proban_C20_after50LC')['LOI_pct'],'25.1')
 def test_Core_allten_computed_LOI_never_promoted(self):
  rows=self.subset(C);self.assertEqual(len(rows),10)
  for r in rows:self.assertIn('calculated_from_TGA_char',r['pairing_status']);self.assertEqual(r['direct_numeric_use'],'no');self.assertIn('derivedfromTGAcharyield',r['source_LOI_measurement_kind']);self.assertNotEqual(r['pairing_status'],'verified_exact');self.assertTrue(pairing.evidence_issues(r))
 def test_Core_air_peak_conflicts_raw_table_and_body_retained(self):
  r=self.find(C,'CoreShell_Neat_initial','air');self.assertEqual((r['Tmax1_C'],r['Tmax2_C']),('344.1','472.2'));self.assertIn('335/464',r['source_TG_table_body_conflicts']);r=self.find(C,'CoreShell_TA-PA-ZIF-8_initial','air');self.assertEqual((r['Tmax1_C'],r['Tmax2_C']),('270.13','506.5'));self.assertIn('240/528',r['source_TG_table_body_conflicts'])
 def test_Core_residue700_not_end800_or_LOI(self):
  r=self.find(C,'CoreShell_PA_initial','N2');self.assertEqual((r['R700_pct'],r['LOI_pct'],r['TG_end_C'],r['residue_temp_C']),('35.17','28.08','800','700'));r=self.find(C,'CoreShell_TA-PA_initial','N2');self.assertEqual((r['R700_pct'],r['LOI_pct']),('37.62','32.54'))
 def test_Core_separate_DSC_mass_pan_not_TG(self):
  r=self.find(C,'CoreShell_Neat_initial','N2');self.assertFalse(r['TG_start_C']);self.assertEqual(r['source_TG_start_raw_C'],'0');self.assertIn('outsidephysicalvalidationrange',r['source_TG_start_validity']);self.assertTrue(any('TG_start_C' in x for x in v.build_tables(pd.DataFrame([dict(r,TG_start_C='0')]).fillna(''),v.issue_list())[3]['errors']));self.assertIn('Native0-800C',r['source_TG_start_definition']);self.assertIn('DSC3-4mg/hermeticAlpan/N2notborrowed',r['source_TG_mass_pan_flow_repeats']);self.assertNotEqual(r['Tmax1_C'],'257.62');self.assertIn('enthalpynotTGmax',r['source_DSC_method'])
if __name__=='__main__':unittest.main(verbosity=2)
