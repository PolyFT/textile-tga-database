"""Protect 2%-loss semantics, assay identity, and conflicting/partial holds."""
import csv,unittest
from pathlib import Path
def load_rows():
 repo=Path(__file__).resolve().parents[1];p=repo/'data/incoming/verified_source_batch_20261005_b272_local_textile.csv'
 if not p.exists():p=Path(__file__).resolve().parent/'staged-local-textile-b272/publication_proposed.csv'
 with p.open(newline='')as f:return list(csv.DictReader(f))
class GlassPA66DPOHEvidence(unittest.TestCase):
 def test_two_percent_loss_not_canonical_threshold_or_peak(self):
  rows=load_rows();raw={r['source_sample_label']:r.get('source_raw_Td2_C')for r in rows if r.get('source_raw_Td2_C')}
  self.assertEqual(raw,{'PA':'367','16%A/PA':'363','16%D/PA':'361','8%D/8%A/PA':'345','DPOH':'385'})
  for r in rows:
   for k in ['T1_C','T5_C','T10_C','Tonset_C','Tmax1_C','Tmax2_C']:self.assertFalse(r.get(k))
 def test_whole_glass_control_and_TG_residue_not_cone_residue(self):
  valid=[r for r in load_rows()if r['direct_numeric_use']=='yes']
  self.assertEqual({r['source_sample_label']:(r['LOI_pct'],r['R700_pct'])for r in valid},{'PA':('23.6','29.1'),'16%A/PA':('34.2','30.4'),'16%D/PA':('28.5','30.1')})
  for r in valid:
   self.assertEqual(r['source_reported_glass_wt_percent'],'30');self.assertEqual(r['material_form_TGA'],r['material_form_LOI'])
   self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['residue_temp_C']),('nitrogen','20','700'))
   self.assertEqual(r['R700_pct'],r['residue_pct']);self.assertFalse(r.get('TGA_mass_mg'));self.assertFalse(r.get('TGA_gas_flow_ml_min'))
 def test_internal_LOI_conflict_and_missing_assays_remain_held(self):
  rows=load_rows();self.assertEqual(len(rows),11);held=[r for r in rows if r['direct_numeric_use']=='no'];self.assertEqual(len(held),8)
  by={r['source_sample_label']:r for r in held}
  self.assertIn('33.6',by['8%D/8%A/PA']['source_hold_reason']);self.assertEqual(by['8%D/8%A/PA']['LOI_pct'],'33.9')
  self.assertFalse(by['DPOH'].get('LOI_pct'));self.assertEqual(sum(bool(r.get('LOI_pct'))and not r.get('R700_pct')for r in held),6)
  for r in held:self.assertEqual(r['pairing_status'],'pending_source_review');self.assertFalse(r.get('reviewed_measurement_fingerprint'))
if __name__=='__main__':unittest.main()
