"""Protect threshold identity, residue endpoint and condition/sample counting."""
import csv
import unittest
from pathlib import Path

def load_rows():
    repo=Path(__file__).resolve().parents[1]
    path=repo/'data/incoming/verified_source_batch_20261005_b252_local_textile.csv'
    if not path.exists():
        path=Path(__file__).resolve().parent/'staged-local-textile-b252/publication_proposed.csv'
    with path.open(newline='')as stream:return list(csv.DictReader(stream))

class GlassMatSourceEvidence(unittest.TestCase):
    def test_two_atmospheres_are_six_specimens(self):
        rows=[r for r in load_rows()if r['direct_numeric_use']=='yes']
        self.assertEqual(len(rows),12)
        self.assertEqual(len({r['sample_state']for r in rows}),6)
        for state in {r['sample_state']for r in rows}:
            own=[r for r in rows if r['sample_state']==state]
            self.assertEqual({r['atmosphere']for r in own},{'nitrogen','air'})
            self.assertEqual(len({r['LOI_pct']for r in own}),1)
            self.assertTrue(all(r['material_form_TGA']==r['material_form_LOI']for r in own))
    def test_T10_R600_not_relabelled(self):
        rows=[r for r in load_rows()if r['direct_numeric_use']=='yes']
        for r in rows:
            self.assertTrue(r['T10_C'])
            self.assertEqual(r['residue_temp_C'],'600')
            self.assertEqual(r['TG_end_C'],'800')
            self.assertEqual(r['R600_pct'],r['residue_pct'])
            for field in ['T5_C','Tonset_C','Tmax1_C','Tmax2_C','R800_pct']:
                self.assertFalse(r.get(field))
        by_key={(r['source_sample_label'],r['atmosphere']):r for r in rows}
        self.assertEqual(by_key['P-GF','nitrogen']['R600_pct'],'20')
        self.assertEqual(by_key['P-GF','air']['R600_pct'],'21')
        self.assertEqual(by_key['P-CaCO3-GF','nitrogen']['R600_pct'],'34')
    def test_identical_TG_does_not_merge_different_clay_preparations(self):
        rows=load_rows()
        own={r['source_sample_label']:r for r in rows if r.get('atmosphere')=='nitrogen'}
        a,b=own['P-30B-GF'],own['P-30B(MPS)-GF']
        self.assertEqual((a['T10_C'],a['R600_pct']),(b['T10_C'],b['R600_pct']))
        self.assertNotEqual(a['sample_state'],b['sample_state'])
        self.assertNotEqual(a['composition'],b['composition'])
        self.assertNotEqual(a['LOI_pct'],b['LOI_pct'])
        outside=[r for r in rows if r['source_sample_label']=='P']
        self.assertEqual(len(outside),1)
        self.assertEqual(outside[0]['direct_numeric_use'],'no')
        self.assertIn('outside_textile',outside[0]['pairing_status'])

if __name__=='__main__':unittest.main()
