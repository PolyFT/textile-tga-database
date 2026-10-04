"""Reject fiber/composite and assay mixing in short ramie composites."""
import csv,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/'data/incoming/verified_source_batch_20261005_b239_local_textile.csv'
if not FILE.exists():FILE=Path(__file__).resolve().parent/'staged-local-textile-b239/publication_proposed.csv'
class RamieCompositeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with FILE.open()as f:cls.rows=list(csv.DictReader(f))
    def test_fiber_TG_and_neat_resin_do_not_become_composite_pairs(self):
        paired=[r for r in self.rows if r['pairing_status']=='verified_exact'];self.assertEqual({r['source_sample_label']for r in paired},{'PP/RF','PP/FR-RF'})
        for r in self.rows:
            if r['source_sample_label'] in ['RF','FR','FR-RF']:self.assertFalse(r['LOI_pct']);self.assertEqual(r['direct_numeric_use'],'no')
            if r['source_sample_label']=='PP':self.assertEqual(r['pairing_status'],'outside_textile_neat_resin_comparator');self.assertEqual(r['direct_numeric_use'],'no')
    def test_zero_TG_residue_and_phr_are_not_cone_residue_or_wtpercent(self):
        a=next(r for r in self.rows if r['source_sample_label']=='PP/RF');b=next(r for r in self.rows if r['source_sample_label']=='PP/FR-RF')
        self.assertEqual((a['R500_pct'],a['R600_pct'],a['R700_pct']),('0','0','0'));self.assertEqual((b['R500_pct'],b['R600_pct'],b['R700_pct']),('14.0','13.1','12.6'))
        for r in [a,b]:self.assertIn('40phr',r['composition']);self.assertIn('not40wtpercent',r['source_composite_preparation']);self.assertEqual(r['residue_temp_C'],'700');self.assertFalse(r.get('T10_C'));self.assertFalse(r.get('Tonset_C'))
if __name__=='__main__':unittest.main()
