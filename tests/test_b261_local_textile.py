"""Protect the source-specific threshold, residue and atmosphere crosswalks."""
import csv
import unittest
from pathlib import Path

def load_rows():
    repo=Path(__file__).resolve().parents[1]
    path=repo/'data/incoming/verified_source_batch_20261005_b261_local_textile.csv'
    if not path.exists():path=Path(__file__).resolve().parent/'staged-local-textile-b261/publication_proposed.csv'
    with path.open(newline='')as f:return list(csv.DictReader(f))

class GlassPA6CrosswalkEvidence(unittest.TestCase):
    def test_source_onset_footnote_is_T5(self):
        for r in load_rows():
            if r['direct_numeric_use']!='yes':continue
            self.assertEqual(r['T5_C'],r['source_raw_Tonset_C'])
            self.assertIn('5percentweightloss',r['source_raw_Tonset_definition'])
            self.assertFalse(r.get('Tonset_C'))
            self.assertFalse(r.get('T10_C'))
    def test_normalized_and_cone_residues_do_not_replace_TG(self):
        rows=load_rows();r=next(x for x in rows if x['source_sample_label']=='GF–PA6/AP20'and x['atmosphere']=='nitrogen')
        self.assertEqual((r['source_normalized_residue_pct'],r['R700_pct'],r['residue_pct']),('7.8','51.2','51.2'))
        for r in rows:
            self.assertEqual(r['residue_temp_C'],'700')
            self.assertFalse(r.get('R800_pct'))
            self.assertEqual(r['R700_pct'],r['residue_pct'])
    def test_two_atmospheres_one_state_and_missing_peaks_stay_missing(self):
        rows=load_rows();valid=[r for r in rows if r['direct_numeric_use']=='yes']
        self.assertEqual(len(valid),10)
        states={r['sample_state']for r in valid};self.assertEqual(len(states),5)
        for state in states:
            tests=[r for r in valid if r['sample_state']==state]
            self.assertEqual({r['atmosphere']for r in tests},{'nitrogen','air'})
            self.assertEqual(len({r['LOI_pct']for r in tests}),1)
            for r in tests:self.assertEqual(r['material_form_TGA'],r['material_form_LOI'])
        for r in valid:
            if (r['source_sample_label']=='GF–PA6'and r['atmosphere']=='nitrogen')or(r['source_sample_label']!='GF–PA6'and r['atmosphere']=='air'):
                self.assertFalse(r['Tmax2_C'])
        powder=next(r for r in rows if r['source_sample_label']=='AP')
        self.assertEqual(powder['direct_numeric_use'],'no')
        self.assertFalse(powder['LOI_pct'])
        self.assertFalse(powder['material_form_LOI'])

if __name__=='__main__':unittest.main()
