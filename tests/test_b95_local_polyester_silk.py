"""Regressions for original printed labels and held protocol/state conflicts."""
import csv
import sys
import unittest
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import pairing
import validate_tg_loi as v
class PolyesterSilkEvidence(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with(ROOT/'data/incoming/verified_source_batch_20261001_b95_local_polyester_silk.csv').open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def source(self,suffix):return [r for r in self.rows if r['DOI'].endswith(suffix)]
 def test_counts_exclude_all_held_facts(self):
  rep=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertEqual(rep['errors'],[])
  self.assertEqual((len(self.rows),rep['verified_exact_sample_states'],rep['verified_exact_condition_records']),(28,6,6))
  self.assertEqual(sum(r['pairing_status']!='verified_exact'for r in self.rows),22)
 def test_printed_pani_loi_crosswalk_and_endpoint(self):
  rr=self.source('20689');self.assertEqual(len(rr),4)
  expected={'PET':(19,.4),'PANI-g-PET':(28.7,6.9),'POAN-g-PET':(21.4,3.75),'POT-g-PET':(25.5,4.5)}
  for r in rr:
   self.assertEqual((float(r['LOI_pct']),float(r['R700_pct'])),expected[r['sample_state']])
   self.assertEqual(float(r['residue_temp_C']),700)
   self.assertEqual(r['source_Figure8_axis_native_label'],r['sample_state'].replace('PET','PEF'))
   self.assertEqual((r['atmosphere'],float(r['heating_rate_C_min'])),('nitrogen',10))
 def test_major_dtg_not_water_step_or_threshold(self):
  expected={'PET':(430,564),'PANI-g-PET':(438,598),'POAN-g-PET':(436,575),'POT-g-PET':(438,574)}
  for r in self.source('20689'):
   self.assertEqual((float(r['Tmax1_C']),float(r['Tmax2_C'])),expected[r['sample_state']])
   for k in ['Tonset_C','T5_C','T10_C']:self.assertEqual(r.get(k,''),'')
   self.assertEqual(r['source_TableIII_stage1_range_C'],'90-300')
   self.assertIn('noNH3dedopingprocedureassigned',r['limitations'])
 def test_four_existing_tg_only_rows_remain_and_are_completed_once(self):
  base=v.load_all();old=base.loc[base.DOI.astype(str).str.lower().eq('10.1002/app.20689')&base.LOI_pct.astype(str).eq('')]
  self.assertEqual(len(old),4)
  self.assertEqual(set(old.sample_state),{'PET','PANI-g-PET','POAN-g-PET','POT-g-PET'})
  with(ROOT/'data/curation/source_review_manifest_20261001_b95.json').open()as f:
   import json;summary=json.load(f)['summary']
  self.assertEqual((summary['new_source_inventory_states'],summary['newly_completed_pairs'],summary['existing_paired_states_evidence_upgraded']),(2,4,0))
 def test_hfpo_same_one_handwash_and_raw_ti(self):
  rr=self.source('2008.10.024');aa=[r for r in rr if r['pairing_status']=='verified_exact'];self.assertEqual(len(aa),2)
  r=next(r for r in aa if '1HW'in r['sample_state']);self.assertEqual((float(r['LOI_pct']),float(r['R600_pct'])),(27.7,41.2))
  self.assertEqual(r['washing_state'],'After1HW')
  for r in aa:
   self.assertEqual(r.get('Tonset_C',''),'');self.assertEqual(r.get('Tmax1_C',''),'');self.assertEqual(r.get('T5_C',''),'')
  for r in rr:
   if r['pairing_status']!='verified_exact':
    for k in pairing.TG_FIELDS:self.assertEqual(r.get(k,''),'')
 def test_dctbpp_compound_air_not_assigned_to_fabrics(self):
  rr=self.source('1497');self.assertEqual(len(rr),13)
  for r in rr:
   self.assertEqual(r.get('atmosphere',''),'');self.assertEqual(r.get('reviewed_measurement_fingerprint',''),'')
   self.assertNotEqual(r['pairing_status'],'verified_exact');self.assertEqual(r.get('residue_temp_C',''),'')
   self.assertEqual(r.get('R550_pct',''),'')
  controls=[r for r in rr if r['sample_state'].startswith('Untreated')];self.assertEqual(len(controls),2)
  self.assertEqual({float(r['source_Ru_footnote_pct'])for r in controls},{13.1,11})
  for r in controls:self.assertEqual(r['source_native_control_Rf_pct'],'0');self.assertEqual(r.get('residue_pct',''),'')
 def test_wool_source_conflicts_and_controls_stay_held(self):
  rr=self.source('01.007')+self.source('35353');self.assertEqual(len(rr),4)
  for r in rr:
   self.assertNotEqual(r['pairing_status'],'verified_exact');self.assertEqual(r.get('reviewed_measurement_fingerprint',''),'')
   self.assertEqual(r.get('R600_pct',''),'');self.assertEqual(r.get('residue_temp_C',''),'')
  r=next(r for r in self.source('01.007')if r['pairing_status']=='treated_formulation_source_conflict')
  self.assertEqual((r['source_table_treatment_temperature_C'],r['source_prose_treatment_temperature_C']),('92','95'))
  r=next(r for r in self.source('35353')if r['pairing_status']=='treated_formulation_source_conflict')
  self.assertEqual((r['source_table_acid'],r['source_regression_acid']),('Hydrochloricacid','Formicacid'))
  self.assertEqual(r.get('TGA_sample_mass_mg',''),'')
 def test_changed_measurement_or_wash_invalidates_approval(self):
  for r in [r for r in self.rows if r['pairing_status']=='verified_exact']:
   for k,val in [('LOI_pct',1),('heating_rate_C_min',99),('washing_state','After30HW')]:
    changed=dict(r,**{k:val});self.assertNotEqual(pairing.measurement_fingerprint(changed),r['reviewed_measurement_fingerprint']);self.assertTrue(pairing.evidence_issues(changed))
if __name__=='__main__':unittest.main()
