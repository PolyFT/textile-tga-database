"""Scientific regressions for newly guarded source facts, including invalid substitutions."""
import copy,csv,json,sys,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];S=R/'data/incoming'
sys.path.insert(0,str(R/'scripts'));import pairing as p
with(S/'verified_source_batch_20261006_b329_local_material.csv').open(newline='')as f:ROWS=list(csv.DictReader(f))
D15='10.1016/j.compscitech.2015.03.013';D12='10.1016/j.polymdegradstab.2012.01.031'
def select(doi,sample,gas='air'):return next(r for r in ROWS if(r['DOI'],r['sample_state'],r['atmosphere'])==(doi,sample,gas))
def native_constraints(row):
 if row.get('residue_pct')or row.get('residue_temp_C')or any(row.get(k)for k in ['R600_pct','R700_pct']):return False
 if row['DOI']==D15:
  if row.get('T10_C')or row.get('Tonset_C')or row['TG_end_C']or row['TG_start_C']:return False
  if row['LOI_replicates']!='5'or row['TGA_replicates']:return False
  if row['sample_state']=='PP':return not row['PPMA_wt_pct']
  return row['PPMA_wt_pct']=='10'
 return row['sample_state']=='PPCB10'and row['LOI_pct']=='27'and row['TG_end_C']=='600'and not row['TG_start_C']and not row['LOI_replicates']and not row['PPMA_wt_pct']
class SourceFacts(unittest.TestCase):
 def test_two_gases_one_state(self):
  subset=[r for r in ROWS if r['DOI']==D12];self.assertEqual(len(subset),2);self.assertEqual(len({p.sample_state_id(r)for r in subset}),1);self.assertEqual({r['atmosphere']for r in subset},{'air','nitrogen'})
 def test_exact_table_profiles(self):
  expected={'PP':('250','325','18.2'),'3CF':('263','320','19.9'),'5CB':('299','398','24.6'),'3CF5CB':('307','404','25.7'),'8CF':('265','341','20.2')}
  for s,t in expected.items():r=select(D15,s);self.assertEqual(tuple(r[k]for k in ['T5_C','Tmax1_C','LOI_pct']),t)
  r=select(D12,'PPCB10','nitrogen');self.assertEqual(tuple(r[k]for k in ['T5_C','T10_C','Tmax1_C']),('446','453','473'))
  r=select(D12,'PPCB10');self.assertEqual(tuple(r[k]for k in ['T5_C','T10_C','Tmax1_C','Tmax2_C']),('345','364','414','596'))
 def test_cone_residue_must_not_enter_TG(self):
  for r in ROWS:self.assertTrue(native_constraints(r));bad=copy.deepcopy(r);bad.update(residue_pct='11.54',residue_temp_C='600');self.assertFalse(native_constraints(bad))
 def test_T5_cannot_be_T10_or_Tonset(self):
  r=select(D15,'3CF');self.assertEqual(r['T5_C'],'263')
  for key in ['T10_C','Tonset_C']:
   bad=copy.deepcopy(r);bad[key]=bad.pop('T5_C');self.assertFalse(native_constraints(bad))
 def test_replication_and_endpoint_not_borrowed(self):
  for r in ROWS:
   bad=copy.deepcopy(r);bad['LOI_replicates']='3';self.assertFalse(native_constraints(bad))
  bad=copy.deepcopy(select(D15,'5CB'));bad['TG_end_C']='600';self.assertFalse(native_constraints(bad))
  bad=copy.deepcopy(select(D12,'PPCB10'));bad['TG_start_C']='25';self.assertFalse(native_constraints(bad))
 def test_neat_and_noadditive_PPMA_not_assigned(self):
  for r in [select(D15,'PP'),select(D12,'PPCB10')]:
   bad=copy.deepcopy(r);bad['PPMA_wt_pct']='10';self.assertFalse(native_constraints(bad))
  self.assertEqual(select(D15,'5CB')['PPMA_wt_pct'],'10');self.assertEqual(select(D15,'5CB')['PP_wt_pct'],'')
 def test_curve_only_and_TG_only_not_counted(self):
  held=json.loads((R/'data/curation/source_review_manifest_20261006_b329.json').read_text());self.assertEqual(len(held['LOI_curve_only_2012']),5);self.assertEqual(len(held['TG_only_2015']),2);self.assertEqual({r['sample_state']for r in ROWS if r['DOI']==D12},{'PPCB10'});self.assertFalse({'1CF5CB','5CF5CB'}&{r['sample_state']for r in ROWS})
 def test_source_state_binding_rejects_mutation(self):
  for r in ROWS:
   self.assertFalse(p.evidence_issues(r));bad=copy.deepcopy(r);bad['material_form_LOI']='washed woven textile';self.assertTrue(p.evidence_issues(bad));bad=copy.deepcopy(r);bad['T5_C']=str(float(r['T5_C'])+1);self.assertTrue(p.evidence_issues(bad))
if __name__=='__main__':unittest.main(verbosity=2)
