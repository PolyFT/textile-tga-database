import csv
import unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from pairing import sample_state_id, evidence_issues, measurement_fingerprint

class B98PreparedTextilePairs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows={p.stem.split('_b98_',1)[1]:list(csv.DictReader(p.open())) for p in ROOT.glob('data/incoming/verified_source_batch_20261001_b98_*.csv')}
    def test_unique_states_and_review_binding(self):
        rows=[r for rs in self.rows.values() for r in rs]
        self.assertEqual((len(rows),len({sample_state_id(r) for r in rows})),(22,22))
        for r in rows:
            self.assertFalse(evidence_issues(r))
            self.assertEqual(r['reviewed_measurement_fingerprint'],measurement_fingerprint(r))
    def test_carbon_sandwich_initial_states_and_named_peaks(self):
        rows={r['source_sample_label']:r for r in self.rows['carbon_foam2019']}
        self.assertEqual(set(rows),{'Carbon/epoxy laminate','Foam core sandwich composite'})
        self.assertEqual(rows['Carbon/epoxy laminate']['Tmax1_C'],'385')
        s=rows['Foam core sandwich composite']
        self.assertEqual((s['LOI_pct'],s['Tmax1_C'],s['Tmax2_C']),('24.5','271','380'))
        for r in rows.values():
            self.assertFalse(r.get('residue_pct'))
            self.assertIn('room-temperature',r['sample_state'])
    def test_natural_laminates_initial_only_with_wool_conflict_held(self):
        rows={r['source_sample_label']:r for r in self.rows['natural_laminates2021']}
        self.assertEqual(set(rows),{'Jute/PP','Jute/PLA','Sisal/PP','Sisal/PLA','Wool/PP'})
        self.assertFalse(rows['Wool/PP']['T50_C'])
        self.assertEqual((rows['Wool/PP']['R500_pct'],rows['Wool/PP']['LOI_pct']),('10.0','20.7'))
        for r in rows.values():
            self.assertIn('unaged',r['sample_state'])
            self.assertEqual(r['atmosphere'],'air')
    def test_mpd_thpc_generic_residue_and_preprint_are_explicit(self):
        rows={r['source_sample_label']:r for r in self.rows['mpd_thpc2024']}
        self.assertEqual(set(rows),{'COT','PMT-6','PHT-6','PMT/PHT-3'})
        for r in rows.values():
            self.assertEqual(r['publication_type'],'author_preprint')
            self.assertEqual(r['related_version_doi'],'10.1007/s10570-025-06393-2')
            self.assertTrue(r['residue_pct'])
            self.assertFalse(r['residue_temp_C'])
            self.assertFalse(r.get('R800_pct'))
            self.assertEqual(r['TG_end_C'],'800')
            self.assertEqual(r['LOI_replicates'],'3')
        self.assertIn('2 wt% aqueous NaOH',rows['COT']['treatment_method'])
    def test_flax_conflicting_residue_and_unpaired_loadings_excluded(self):
        rows={r['source_sample_label']:r for r in self.rows['flax_mhch2026']}
        self.assertEqual(set(rows),{'S1','S4','S6'})
        self.assertFalse(rows['S6']['R600_pct'])
        self.assertEqual(rows['S6']['source_conflicting_R600_pct'],'9.23')
        self.assertEqual(rows['S6']['Tmax1_C'],'394.74')
        self.assertEqual(rows['S4']['R600_pct'],'10.96')
    def test_earlier_loi_only_labels_are_reuse_excluded(self):
        issues=list(csv.DictReader((ROOT/'data/curation/known_pairing_issues.csv').open()))
        labels={r['sample_state'] for r in issues if r['DOI']=='10.1016/j.compositesb.2018.09.013' and r['status']=='open'}
        self.assertTrue({'Jute/PP','Jute/PLA','Sisal/PP','Sisal/PLA'}<=labels)
    def test_bamboo_kenaf_pure_oxygen_and_measured_uncertainty(self):
        rows=self.rows['bamboo_kenaf2020']
        self.assertEqual(len(rows),4)
        self.assertEqual({r['LOI_pct'] for r in rows},{'19.80','22.92','22.94','27.71'})
        self.assertEqual({r['R800_pct'] for r in rows},{'0.52','1.54','1.43','1.92'})
        for r in rows:
            self.assertEqual(r['atmosphere'],'O2')
            self.assertEqual(r['LOI_uncertainty_type'],'standard deviation')
            self.assertTrue(r['LOI_sd'])
    def test_chance_only_readable_dtg_pairs_and_no_residue_inference(self):
        rows={r['source_sample_label']:r for r in self.rows['chance1981']}
        self.assertEqual(set(rows),{'Ia','Ib','Ic','Control'})
        self.assertEqual((rows['Ia']['Tmax1_C'],rows['Ia']['Tmax2_C'],rows['Ia']['LOI_pct']),('185','260','34.0'))
        self.assertEqual((rows['Control']['Tmax1_C'],rows['Control']['LOI_pct']),('349','18.5'))
        for r in rows.values():
            self.assertFalse(r.get('residue_pct'))
            self.assertFalse(r.get('R600_pct'))
            self.assertFalse(r.get('TG_end_C'))
    def test_public_holds_have_no_private_paths(self):
        text=(ROOT/'data/curation/source_review_holds_20261001_b98.json').read_text()
        for marker in ['/workspace/','/tmp/','new-textile-cache/','new-textile-prep/']:
            self.assertNotIn(marker,text)

if __name__=='__main__': unittest.main()
