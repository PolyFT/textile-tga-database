"""Protect source ambiguities from erroneous future numeric admission."""
import csv,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if not(ROOT/'scripts/pairing.py').exists():ROOT=ROOT/'repo'
sys.path.insert(0,str(ROOT/'scripts'));import pairing
def facts(batch):
 p=ROOT/f'data/incoming/verified_source_batch_20261004_{batch}_local_textile.csv'
 if not p.exists():p=ROOT.parent/f'work/staged-local-textile-{batch}/publication_proposed.csv'
 with p.open(newline='')as f:return list(csv.DictReader(f))
class NativeSourceExclusions(unittest.TestCase):
 def test_water_peak_does_not_become_decomposition(self):
  r=facts('b199')[0];self.assertEqual(r['Tmax1_C'],'350.2');self.assertEqual(r['source_water_loss_Tmax1_C'],'50.6')
 def test_calculated_curve_is_not_a_measured_sample(self):
  r=facts('b199');c=r[3];self.assertEqual(c['R600_pct'],'13.8');self.assertEqual(c['source_calculated_not_measured_R600_pct'],'6.2');self.assertFalse(any(x['source_sample_label']=='Cotton-3b'for x in r))
 def test_missing_ramp_stays_excluded(self):
  self.assertTrue(all(not r['heating_rate_C_min']and r['pairing_status']=='scientific_hold'for r in facts('b199')))
 def test_three_LOIs_not_assigned_to_four_doses(self):
  self.assertEqual({r['source_HGM_coating_bath_pct']for r in facts('b200')[1:]},{'2','5','10','20'});self.assertTrue(all(not r['LOI_pct']and r['direct_numeric_use']=='no'for r in facts('b200')[1:]))
 def test_program_end_does_not_define_residue_temperature(self):
  r=facts('b200')[0];self.assertEqual(r['TG_end_C'],'700');self.assertEqual(r['source_unbound_residue_pct'],'0.77');self.assertFalse(r.get('R700_pct'));self.assertFalse(r.get('residue_temp_C'))
 def test_conflicting_onset_kept_raw(self):
  r=facts('b200')[0];self.assertEqual((r['source_native_Tonset_Table1_C'],r['source_native_Tonset_prose_C']),('307.4','283'));self.assertFalse(r.get('Tonset_C'))
 def test_control_pair_preserves_unambiguous_peak(self):
  r=facts('b200')[0];self.assertEqual((r['LOI_pct'],r['Tmax1_C'],r['atmosphere'],r['heating_rate_C_min']),('17','339.14','air','10'));self.assertFalse(pairing.evidence_issues(r))
 def test_binding_rejects_peak_LOI_or_wash_mutation(self):
  r=facts('b200')[0]
  for k,v in [('Tmax1_C','350.2'),('LOI_pct','21'),('washing_state','20_laundering_cycles')]:self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**{k:v})))
if __name__=='__main__':unittest.main()
