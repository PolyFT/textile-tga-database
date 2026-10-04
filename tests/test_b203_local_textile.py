"""Prevent cross-specimen TG joins, fire-tube peak substitution and conflict repair."""
import csv,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if not(ROOT/'scripts/pairing.py').exists():ROOT=ROOT/'repo'
sys.path.insert(0,str(ROOT/'scripts'));import pairing
def facts(b):
 p=ROOT/f'data/incoming/verified_source_batch_20261004_{b}_local_textile.csv'
 if not p.exists():p=ROOT.parent/f'work/staged-local-textile-{b}/publication_proposed.csv'
 with p.open(newline='')as f:return list(csv.DictReader(f))
class NativeTextileSpecimenAndStateEvidence(unittest.TestCase):
 def test_microsphere_TG_not_joined_to_fabric_LOI(self):
  self.assertTrue(all(r['pairing_status']=='scientific_hold'and 'specimen_form_mismatch'in pairing.evidence_issues(r)for r in facts('b202')))
 def test_neat_TG_conditions_not_assigned_fabrics(self):
  self.assertTrue(all(not any(r.get(k)for k in list(pairing.TG_FIELDS)+['atmosphere','heating_rate_C_min'])for r in facts('b202')))
 def test_sodium_prose_conflict_not_overwritten_by_final_state(self):
  a,b=facts('b202')[6:];self.assertFalse(a['LOI_pct']);self.assertEqual((a['source_LOI_Table2_pct'],a['source_LOI_prose_pct'],b['LOI_pct']),('22.2','22.1','22.1'));self.assertNotEqual(a['sample_state'],b['sample_state'])
 def test_fume_peak_and_undefined_start_not_TG_thresholds(self):
  r=facts('b203')[0];self.assertEqual((r['source_MFT_exhaust_Tmax_C'],r['Tmax1_C'],r['source_reported_rapid_decomposition_start_C']),('457','370','275'));self.assertFalse(r.get('T5_C'));self.assertFalse(r.get('Tonset_C'))
 def test_generic_CNT_dose_and_curve_only_stay_held(self):
  r=facts('b203');self.assertTrue(all(r[i]['pairing_status']=='scientific_hold'and not any(r[i].get(k)for k in pairing.TG_FIELDS)for i in [2,3,4,5]))
 def test_CNT1_LOI_conflict_not_resolved_by_choosing_table(self):
  r=facts('b203')[4];self.assertFalse(r['LOI_pct']);self.assertEqual((r['source_LOI_Table3_pct'],r['source_LOI_Discussion_pct']),('31.7','32.0'))
 def test_test_specific_loading_not_imputed_to_TG(self):
  r=facts('b203')[1];self.assertEqual((r['source_LOI_WG_pct'],r['source_MFT_WG_pct']),('12.2±1.1','13.4±1.2'));self.assertFalse(r.get('weight_gain_pct'))
 def test_roving_pair_binding_rejects_form_peak_and_wash_changes(self):
  r=facts('b203')[6];self.assertFalse(pairing.evidence_issues(r));self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='cotton fabric')))
  for k,v in [('Tmax1_C','190'),('LOI_pct','31.7'),('washing_state','washed')]:self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**{k:v})))
if __name__=='__main__':unittest.main()
