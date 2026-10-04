"""Reject dose joins, assay substitution and edited peak-bound TG metrics."""
import csv,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if not(ROOT/'scripts/pairing.py').exists():ROOT=ROOT/'repo'
sys.path.insert(0,str(ROOT/'scripts'));import pairing
PUBLIC=ROOT/'data/incoming/verified_source_batch_20261004_b196_local_textile.csv'
PRIVATE=ROOT.parent/'work/staged-local-textile-b196/publication_proposed.csv'
class PhotoATRPCottonFacts(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with(PUBLIC if PUBLIC.exists()else PRIVATE).open(newline='')as f:cls.rows=list(csv.DictReader(f));cls.accepted=[r for r in cls.rows if r['pairing_status']=='verified_exact']
 def test_one_control_state_two_test_gases(self):
  self.assertEqual(len(self.accepted),2);self.assertEqual({r['sample_state']for r in self.accepted},{'Neat fabric_initial'});self.assertEqual([r['atmosphere']for r in self.accepted],['air','N2'])
 def test_different_graft_loads_are_not_joined(self):
  for r in self.rows:
   if r['source_sample_label']in ['Fabric-Br','Cg15','Cg65']:self.assertFalse(r['LOI_pct']);self.assertEqual(r['direct_numeric_use'],'no')
  r=self.rows[-1];self.assertEqual((r['source_sample_label'],r['LOI_pct'],r['source_grafting_percentage'],r['source_light_intensity_mW_cm2']),('Cg41','30','40.8','9'));self.assertFalse(any(r.get(k)for k in pairing.TG_FIELDS))
 def test_peakbound_and_endpoint_residue_are_separate(self):
  r=self.accepted[0];self.assertEqual((r['Tmax2_C'],r['residue_at_Tmax2_pct'],r['R600_pct'],r['R800_pct']),('468','11.1','4.4','4.8'));self.assertEqual(r['residue_temp_C'],'800');self.assertIn('causeunreported',r['source_endpoint_anomaly'])
 def test_moisture_and_T10_are_not_T5_or_onset(self):
  self.assertEqual([r['T10_C']for r in self.accepted],['311','326'])
  for r in self.rows:self.assertFalse(r.get('T5_C'));self.assertFalse(r.get('Tonset_C'))
  self.assertFalse(self.accepted[1]['Tmax2_C']);self.assertFalse(self.accepted[1]['residue_at_Tmax2_pct'])
 def test_TG_is_not_MCC_protocol(self):
  for r in self.accepted:self.assertEqual((r['heating_rate_C_min'],r['TG_start_C'],r['TG_end_C'],r['gas_flow_mL_min']),('10','25','800','80'));self.assertEqual(r['LOI_replicates'],'3');self.assertEqual(r['source_LOI_dimensions_mm'],'140x52')
 def test_binding_rejects_gas_wash_and_peak_metric_changes(self):
  for r in self.accepted:
   self.assertFalse(pairing.evidence_issues(r))
   for k,v in [('LOI_pct','30'),('T10_C','257'),('washing_state','one_durability_wash'),('atmosphere','oxygen')]:self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**{k:v})))
if __name__=='__main__':unittest.main()
