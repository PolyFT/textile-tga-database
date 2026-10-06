"""Original-source guards for the9 root-approved B466 conditions; no curve/assay substitution."""
import pathlib,json,csv,copy,unittest,sys,os
from decimal import Decimal as D
ROOT=pathlib.Path(os.environ.get('B466_REPO_ROOT',pathlib.Path(__file__).resolve().parents[1]))
sys.dont_write_bytecode=True;sys.path.insert(0,str(ROOT/'scripts'))
import pairing,textile_scope,reader_table
INCOMING=pathlib.Path(os.environ.get('B466_INCOMING',ROOT/'data/incoming/verified_source_batch_20261007_b466_local_material.csv'))
MANIFEST=pathlib.Path(os.environ.get('B466_MANIFEST',ROOT/'data/curation/archive/20261007/source_review_manifest_b466.json'))
with INCOMING.open(newline='')as f:rows=list(csv.DictReader(f))
manifest=json.loads(MANIFEST.read_text());held=manifest['held_source_facts'];witness=manifest['approved_source_facts']
def valid_source(r):
 found=[x for x in witness if (x['DOI'],x['sample_state'])==(r.get('DOI'),r.get('sample_state'))]
 return len(found)==1 and r==found[0] and not pairing.evidence_issues(r)
def select(name):return next(x for x in rows if x['sample_state']==name)
def residue_metrics(r):
 out={k:D(v)for k,v in r.items()if k.startswith('R')and k.endswith('_pct')and k[1:-4].isdigit()and v!=''}
 if r.get('residue_pct','')and r.get('residue_temp_C',''):
  key='R'+format(D(r['residue_temp_C']).normalize(),'f')+'_pct';value=D(r['residue_pct'])
  if key in out:assert out[key]==value,'conflictingresiduealiases'
  out[key]=value
 return out
class SourceTests(unittest.TestCase):
 def reject(self,name,**changes):
  x=copy.deepcopy(select(name));x.update(changes);x['reviewed_measurement_fingerprint']=pairing.measurement_fingerprint(x);x['reviewed_material_scope_fingerprint']=pairing.material_scope_fingerprint(x);self.assertFalse(valid_source(x))
 def test_positive9_complete_sourcewitness(self):
  for x in rows:self.assertTrue(valid_source(x))
 def test_B_interval_not_T5_Tonset_Tmax(self):
  for field in ['T5_C','Tonset_C','Tmax1_C']:self.reject('PP',**{field:'271.3'})
 def test_B_residue700_not800_programme(self):self.reject('PPAF1',residue_temp_C='800')
 def test_B_control_not_antioxidantfree(self):self.reject('PP',source_B225_w_w='0')
 def test_B_fibre_loading_not_final_PP_balance(self):self.reject('PPAF1',composition='PP94.5/AF5/B2250.5wt%')
 def test_B40_conflict_notforced_table_orabstract(self):
  h=next(x for x in held if x['sample_state']=='PPAF5');self.assertEqual((h['source_raw_R700_TableIV_pct'],h['source_raw_R700_abstract_pct']),('23.5','23.7'));self.assertEqual(h['residue_pct'],'');self.assertNotIn('PPAF5',[r['sample_state']for r in rows])
 def test_C_measured_not_theoretical(self):self.reject('RPUF-5',LOI_pct='27.7');self.reject('RPUF-6',LOI_pct='27.9')
 def test_C_T5_not_watercorrected_mainstage(self):self.reject('RPUF-6',T5_C='340')
 def test_C_residue700_not800_programme(self):self.reject('RPUF-3',residue_temp_C='800')
 def test_C_unmodifiedAF_notMAFrecipe(self):self.reject('RPUF-3',source_Table1_MAF='5',source_Table1_AF='')
 def test_C_nominal5not_computedPU95(self):self.reject('RPUF-3',composition='PU95/MAF5wt%')
 def test_C_purethermoset_not_citykeyword_scope(self):self.assertEqual({x['sample_state']for x in held if x['DOI'].endswith('2017.08.019')},{'RPUF-1','RPUF-2'})
 def test_C_MSD_MLR_not_TGmassloss(self):self.reject('RPUF-6',residue_pct='66.3',residue_temp_C='700')
 def test_C_fivepreparedgroups_notLOIn5(self):self.reject('RPUF-6',LOI_n='5')
 def test_C_source_stage1_not_promotedmainpeak(self):self.reject('RPUF-6',Tmax1_C='245')
 def test_C_rate_percent_perC_not_percentpermin(self):self.reject('RPUF-6',source_TG_stage_rate_unit='percent/min')
 def test_priorPP_scalar_equality_notbatchproof(self):
  note=manifest['prior_control_identity_note'];self.assertIn('control LOI18.0 and R600=0',note);self.assertIn('Physical batch relationship and prior B225 loading were not reported',note);self.assertIn('do not infer prior antioxidant absence or a distinct batch',note)
 def test_required_annotation_only_one_textcell(self):
  self.assertEqual(manifest['scientific_text_cells_changed'],1);r=select('PP');self.assertEqual(r['source_limitations'],manifest['prior_control_identity_note']);self.assertEqual(pairing.measurement_fingerprint(r),r['reviewed_measurement_fingerprint']);self.assertIn('Ref2',r['source_limitations']);self.assertIn('not reported',r['source_limitations'])
 def test_residue_aliases_are_one_temperature_bound_metric(self):
  self.assertEqual(residue_metrics({'R700_pct':'0','residue_pct':'0','residue_temp_C':'700'}),{'R700_pct':D('0')})
  self.assertFalse(residue_metrics({'R600_pct':'0','residue_pct':'0','residue_temp_C':'600'}).keys()&residue_metrics({'R700_pct':'0','residue_pct':'0','residue_temp_C':'700'}).keys())
  self.assertEqual(residue_metrics({'residue_pct':'0'}),{})
 def test_residue_alias_conflict_must_reject(self):
  with self.assertRaisesRegex(AssertionError,'conflictingresiduealiases'):residue_metrics({'R700_pct':'1','residue_pct':'0','residue_temp_C':'700'})
 def test_rootapproved_counts_and_negative_roles(self):
  self.assertEqual(len(rows),9);self.assertEqual(len(manifest['scope_entries']),9);self.assertEqual(manifest['sourceapproved_unique_states'],9);self.assertEqual(manifest['oldmain_evidence_upgrade'],0);self.assertEqual(manifest['oldmain_scope_upgrade'],0)
  facts=manifest['processed_source_queue_facts'];self.assertEqual(len(facts),6);self.assertEqual(sum(f['new_verified_pairs'] for f in facts),9);self.assertEqual(sum(f['new_verified_pairs']==0 for f in facts),4)
 def test_scope_identity_rejects_changed_form(self):
  r=dict(select('RPUF-3'),material_form_TGA='pure thermoset foam without AF');e=next(e for e in manifest['scope_entries']if e['sample_state_id']==pairing.sample_state_id(select('RPUF-3')));self.assertNotEqual(textile_scope.scope_identity_sha256(r),e['scope_identity_sha256'])
 def test_annotation_visible_in_unchanged_reader(self):
  r=select('PP');e=next(e for e in manifest['scope_entries']if e['sample_state_id']==pairing.sample_state_id(r));self.assertIn('source_limitations='+r['source_limitations'],reader_table.reading_row(r,e)[20]);self.assertEqual(reader_table.reading_row(r,e)[9],'')
if __name__=='__main__':unittest.main()
