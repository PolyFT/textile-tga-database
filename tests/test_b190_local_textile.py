"""Keep explicit fiber/yarn form differences and washed records outside Grade A."""
import csv,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if not(ROOT/'scripts/pairing.py').exists():ROOT=ROOT/'repo'
sys.path.insert(0,str(ROOT/'scripts'));import pairing
PUBLIC=ROOT/'data/incoming/verified_source_batch_20261004_b190_local_textile.csv'
PRIVATE=ROOT.parent/'work/staged-local-textile-b190/publication_proposed.csv'
class FiberYarnHolds(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with(PUBLIC if PUBLIC.exists()else PRIVATE).open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def test_all_seven_are_held(self):
  self.assertEqual(len(self.rows),7)
  for r in self.rows:self.assertEqual(r['pairing_status'],'scientific_hold');self.assertEqual(r['direct_numeric_use'],'no')
 def test_actual_LOI_spun_yarn_differentfrom_TG_fiber(self):
  for r in self.rows:
   self.assertNotEqual(r['material_form_TGA'],r['material_form_LOI']);self.assertIn('120twists',r['source_LOI_assembly']);self.assertIn('0.9g',r['source_LOI_assembly'])
 def test_native_initial_table_profiles_not_additive_or_theoreticalchar(self):
  self.assertEqual([tuple(r[k]for k in ['T5_C','Tmax1_C','R700_pct','LOI_pct'])for r in self.rows[:3]],[('230.4','376.2','3.0','18.2'),('135.2','394.5','3.2','18.2'),('213.3','360.6','19.0','27.1')]);self.assertEqual(self.rows[2]['residue_temp_C'],'700')
 def test_wash_TG_not_borrowed(self):
  self.assertEqual([r['LOI_pct']for r in self.rows[3:]],['26.8','26.5','24.7','23.9'])
  for r in self.rows[3:]:self.assertFalse(any(r.get(k)for k in pairing.TG_FIELDS));self.assertFalse(r.get('residue_temp_C'))
 def test_even_fingerprinted_formmismatch_cannot_be_approved(self):
  r=dict(self.rows[0],pairing_status='verified_exact',direct_numeric_use='yes',pairing_evidence='Same formulation and initial state, but native TG fiber versus spun yarn LOI assembly.')
  r['reviewed_measurement_fingerprint']=pairing.measurement_fingerprint(r);self.assertIn('specimen_form_mismatch',pairing.evidence_issues(r))
if __name__=='__main__':unittest.main()
