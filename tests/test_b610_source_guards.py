"""B610 literal source bindings and source-specific scientific boundaries."""
import copy,csv,hashlib,json,unittest
from pathlib import Path
from scripts import pairing,textile_scope,reader_table
ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'data/curation/archive/20261007/source_review_manifest_b610.json'
def digest(row):
 return hashlib.sha256(json.dumps({k:v for k,v in row.items()if v!=''},sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
class B610SourceGuards(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=json.loads(MANIFEST.read_text());cls.rows=[]
  for name in cls.m['incoming_files']:
   with (ROOT/name).open(newline='')as f:cls.rows+=list(csv.DictReader(f))
  cls.by={pairing.pair_key(r):r for r in cls.rows}
 def subset(self,doi):return [r for r in self.rows if r['DOI']==doi]
 def test_01_all_provided_nonempty_literal_fields(self):
  self.assertEqual(len(self.rows),78)
  self.assertEqual(len(self.by),78)
  for r,fact in zip(self.rows,self.m['selected_source_facts']):self.assertEqual(digest(r),fact['nonempty_provided_row_sha256'])
 def test_02_unknown_field_changes_rejected(self):
  r=copy.deepcopy(self.rows[0]);before=digest(r);r['source_unknown_future_field']='0';self.assertNotEqual(digest(r),before)
 def test_03_literal_zero_preserved(self):
  r=next(r for r in self.rows if r.get('R800_pct')=='0');a=digest(r);r=copy.deepcopy(r);r['R800_pct']='';self.assertNotEqual(a,digest(r))
 def test_04_unique_states_not_conditions(self):
  self.assertEqual(len({pairing.sample_state_id(r)for r in self.rows}),25)
  self.assertEqual(len(self.m['scope_entries']),78)
 def test_05_all_measurement_scope_bindings(self):
  for r,e in zip(self.rows,self.m['scope_entries']):
   self.assertEqual(pairing.evidence_issues(r),[]);self.assertEqual(e['reviewed_measurement_fingerprint'],pairing.measurement_fingerprint(r));self.assertEqual(e['scope_identity_sha256'],textile_scope.scope_identity_sha256(r))
 def test_06_measurement_mutation_rejected(self):
  r=copy.deepcopy(self.rows[0]);r['LOI_pct']='999';self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(r))
 def test_07_scope_prep_mutation_rejected(self):
  r=copy.deepcopy(next(r for r in self.rows if r.get('material_scope_class')));r['source_preparation']+=' invented';self.assertNotEqual(pairing.material_scope_fingerprint(r),r['reviewed_material_scope_fingerprint'])
 def test_08_conflicting_R800_not_selected(self):
  r=next(r for r in self.subset('10.1002/app.48036')if r['sample_state']=='PP/rGO-APP/PER 30 wt %')
  for k in ['R800_pct','residue_pct','residue_temp_C']:self.assertEqual(r.get(k,''),'')
  text=json.dumps(r);self.assertIn('11.0',text);self.assertIn('10.0',text)
 def test_09_PP_control_not_neat_resin(self):
  r=next(r for r in self.subset('10.1002/app.48036')if r['sample_state']=='Pure PP');self.assertIn('98',r['composition']);self.assertIn('MAPP',r['composition'])
 def test_10_T1_not_T5_or_Tonset(self):
  for r in self.subset('10.1002/app.47129'):self.assertNotEqual(r.get('T1_C',''),'');self.assertEqual(r.get('T5_C',''),'');self.assertEqual(r.get('Tonset_C',''),'')
 def test_11_rate_amplitude_not_temperature(self):
  for r in self.subset('10.1002/app.47129'):
   out=reader_table.reading_row(r,{'scope_class':'fiber_forming_polymer_composite'});self.assertIn('原文峰值失重速率1=',out[20]);self.assertIn('未换算',out[20]);self.assertIn('% min/C',out[20]);self.assertNotIn('source_R1peak_raw=',out[13])
 def test_12_undefined_peaks_not_canonical(self):
  for r in self.subset('10.1002/app.47367'):self.assertEqual(r.get('Tmax1_C',''),'');self.assertEqual(r.get('Tmax2_C',''),'')
 def test_13_R800_coordinate_not_endpoint(self):
  for r in self.rows:
   if r.get('R800_pct','')!='':self.assertEqual(r.get('residue_temp_C'),'800');self.assertEqual(r.get('residue_pct'),r['R800_pct'])
 def test_14_RPET_multiramp_six_states(self):
  rs=self.subset('10.1002/app.37673');self.assertEqual(len(rs),48);self.assertEqual(len({pairing.sample_state_id(r)for r in rs}),6);self.assertEqual({r['heating_rate_C_min']for r in rs},{'2','5','10','20'})
 def test_15_exact_LOI_generic_prose_caveat(self):
  rs=self.subset('10.1002/app.37673');self.assertEqual({r['LOI_pct']for r in rs},{'23.2','20.3','21.1','22.4','19.4','20.5'});self.assertTrue(all('21' in json.dumps(r)and'23' in json.dumps(r)for r in rs))
 def test_16_particle_unit_not_guessed(self):
  for r in self.subset('10.1002/app.37673'):self.assertIn('1.8 mm',json.dumps(r));self.assertNotIn('1.8 μm',json.dumps(r))
 def test_17_PVA_conflicting_T5_blank(self):
  rs=[r for r in self.subset('10.1002/pen.25609')if r['atmosphere']=='N2'and r.get('source_T5_field_status')=='metric_held_table_body_conflict']
  self.assertEqual(len(rs),2)
  for r in rs:self.assertEqual(r.get('T5_C',''),'');self.assertIn('source_T5_conflicting_prose_C=',reader_table.reading_row(r,{'scope_class':'fiber_forming_polymer_composite'})[20])
 def test_18_PVA_R700_raw_not_selected(self):
  rs=[r for r in self.subset('10.1002/pen.25609')if r.get('source_R700_field_status')];self.assertEqual(len(rs),1)
  r=rs[0];self.assertEqual(r.get('R700_pct',''),'');self.assertEqual(r['source_raw_R700_table_pct'],'7.3');self.assertEqual(r['source_raw_R700_body_pct'],'9.5')
 def test_19_cotton_Tmax_raw_only(self):
  rs=[r for r in self.rows if r.get('source_Tmax_ambiguous_C','')];self.assertEqual(len(rs),4)
  for r in rs:self.assertEqual(r.get('Tmax1_C',''),'');self.assertEqual(r.get('Tmax2_C',''),'');self.assertIn(r['source_Tmax_ambiguous_C'],reader_table.reading_row(r,{'scope_class':'textile_cloth'})[20])
 def test_20_initial_wash_not_laundering(self):
  rs=[r for r in self.rows if r.get('source_Tmax_ambiguous_C','')];self.assertEqual(len({pairing.sample_state_id(r)for r in rs}),2);self.assertTrue(all('column0LC' in r['washing_state']or'0standardlaundrycycles' in r['washing_state']for r in rs))
 def test_21_TGIR_not_ordinaryTG(self):
  for r in self.rows:
   if r.get('source_Tmax_ambiguous_C',''):self.assertEqual(r['heating_rate_C_min'],'20');self.assertNotEqual(r.get('sample_mass_mg',''),'5')
 def test_22_phase_not_published(self):
  self.assertFalse(self.m['publication_approved']);self.assertEqual(self.m['published'],0);self.assertEqual(self.m['formal_baseline'],{'states':980,'TG':1213,'sources':196})
 def test_23_public_privacy(self):
  text=MANIFEST.read_text()
  for token in ['/Volumes/','/Users/','smb://']:self.assertNotIn(token,text)
if __name__=='__main__':unittest.main()
