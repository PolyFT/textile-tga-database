"""Factual checks for five source-verified cotton TG–LOI records."""
import argparse,csv,json,copy,unittest
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--payload',type=Path,required=True);parser.add_argument('--scope',type=Path,required=True);args,rest=parser.parse_known_args()
else:
 args=argparse.Namespace(payload=ROOT/'data/incoming/verified_source_batch_20261006_b420_local_material.csv',scope=ROOT/'data/curation/textile_scope_registry.json');rest=[]
with args.payload.open(newline='') as f:records=list(csv.DictReader(f))
bindings=json.loads(args.scope.read_text())
if isinstance(bindings,dict):
 fps={r['reviewed_measurement_fingerprint']for r in records};bindings=[e for e in bindings['entries']if e['reviewed_measurement_fingerprint']in fps]
def source_valid(rs):
 vals=[('F0','18.6','5.9','339.3'),('F1','24.6','12.0',''),('F2','26.3','20.7',''),('F3','28.5','22.5',''),('F4','27.4','25.3','')]
 return len(rs)==5 and all((r['native_sample_label'],r['LOI_pct'],r['R600_pct'],r['Tmax1_C'])==v and r['atmosphere']=='air'and r['heating_rate_C_min']=='10'and r['residue_temp_C']=='600'and all(not r[k]for k in ['T5_C','T10_C','Tonset_C','R700_pct','R800_pct','Tmax2_C'])for r,v in zip(rs,vals))
class SourceTests(unittest.TestCase):
 def test_source_numbers_and_five_states_exact(self):
  self.assertTrue(source_valid(records));self.assertEqual(len({(r['DOI'],r['sample_state'])for r in records}),5);self.assertEqual({r['DOI']for r in records},{'10.1007/s10570-019-02431-y'})
 def test_real_numeric_mutation_rejected(self):
  bad=copy.deepcopy(records);bad[0]['LOI_pct']='19';self.assertFalse(source_valid(bad))
 def test_rawinitial_unreported_criterion_not_T5_Tonset(self):
  self.assertEqual(records[0]['source_raw_initial_decomposition_temperature_C'],'294.1');self.assertIn('criterion unreported',records[0]['source_raw_initial_temperature_definition'])
  for k in ['T5_C','Tonset_C']:
   bad=copy.deepcopy(records);bad[0][k]='294.1';self.assertFalse(source_valid(bad))
 def test_DTGrate_only_control_not_MCC(self):
  self.assertIn('maximum rate of degradation',records[0]['source_Tmax_definition']);self.assertTrue(all(not r['Tmax1_C']for r in records[1:]));self.assertTrue(all('HEATRELEASE MCC' in r['limitations']for r in records))
 def test_400C_weightloss_not_residue(self):
  bad=copy.deepcopy(records);bad[3]['R600_pct']='37';self.assertFalse(source_valid(bad));self.assertEqual(records[0]['source_weight_loss_at400_pct'],'55.2')
 def test_ordinary_air_method_and_preparedfabric(self):
  self.assertTrue(all(r['gas_flow_mL_min']=='50'and r['material_form_TGA']==r['material_form_LOI']=='cotton fabric'for r in records));self.assertTrue(all('initial prepared' in r['washing_state']for r in records))
 def test_control_history_not_functionalization_borrow(self):self.assertIn('subsequent drying/functionalization notreported forcontrol',records[0]['source_preparation'])
 def test_unknown_final_fraction_and_uncertainty_preserved(self):
  self.assertTrue(all(not r['LOI_replicates']and r['LOI_uncertainty_type']=='unreported'for r in records));self.assertTrue(all('retained' in r['composition'].lower()and 'unknown' in r['composition'].lower()for r in records))
 def test_audit_chain_is_primary_peer_root(self):
  self.assertTrue(all(r['review_disposition']=='source_verified' and all(x in r['evidence_reviewed_by'] for x in ['b412','b417','b418']) for r in records))
 def test_all_five_scope_bindings(self):
  self.assertEqual(len(bindings),5);self.assertEqual(Counter(e['reviewed_measurement_fingerprint']for e in bindings),Counter(r['reviewed_measurement_fingerprint']for r in records));self.assertTrue(all(e['decision']=='admit_textile'and e['scope_class']=='textile_cloth' for e in bindings))
 def test_private_paths_excluded(self):
  prefixes=['/'+'Users/','/'+'Volumes/','smb:'+chr(47)*2,'file:'+chr(47)*2];self.assertFalse(any(p in json.dumps(records+bindings,ensure_ascii=False)for p in prefixes));self.assertTrue(any(p in ('/'+'Users/'+'example/source.pdf')for p in prefixes))
if __name__=='__main__':unittest.main(argv=['test_b420_portable_source_guards']+rest)
