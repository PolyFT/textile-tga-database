"""Protect source-specific condition, metric and counting limits in B820."""
import csv, json, unittest
from pathlib import Path
from scripts import pairing, reader_table

ROOT=Path(__file__).resolve().parents[1]
INCOMING=ROOT/'data/incoming/verified_source_batch_20261007_b820_pp.csv'
MANIFEST=ROOT/'data/curation/archive/20261007/source_review_manifest_b820.json'

class TestB820SourceLimits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with INCOMING.open(newline='') as h:cls.rows=list(csv.DictReader(h))
        cls.manifest=json.loads(MANIFEST.read_text())
    def group(self,doi):return [r for r in self.rows if r['DOI']==doi]
    def test_sample_and_condition_counts(self):
        self.assertEqual((len(self.rows),len({pairing.sample_state_id(r) for r in self.rows})),(39,27))
        self.assertEqual(len({pairing.pair_key(r) for r in self.rows}),39)
        self.assertEqual(self.manifest['new_paired_sources'],8)
        for doi in ['10.1002/pat.4766','10.1002/pat.4996']:
            rr=self.group(doi);self.assertEqual((len(rr),len({pairing.sample_state_id(r) for r in rr})),(12,6))
            self.assertEqual({(r['atmosphere'],r['heating_rate_C_min']) for r in rr},{('N2','10'),('air','10')})
        self.assertFalse(self.group('10.1002/pat.4492'))
    def test_one_app30_primary_without_cross_source_tg(self):
        rr=[r for r in self.rows if r.get('source_cohort_alias_note')]
        self.assertEqual(len(rr),1)
        r=rr[0];self.assertEqual((r['DOI'],r['source_observation_key']),('10.1002/pc.20459','B772-6-068'))
        self.assertEqual((r['LOI_pct'],r['Tmax1_C'],r['Tmax2_C'],r['Tmax3_C']),('20','276','366','605'))
        self.assertFalse(self.group('10.1002/pat.1231'))
    def test_undefined_peaks_and_conflicting_onset_stay_raw(self):
        for r in self.group('10.1002/pat.4766'):
            self.assertEqual(r['Tmax1_C'],'');self.assertTrue(r['source_Tmax1_C'])
            self.assertIn(r['source_MLR_pct_per_min'],r['source_thermal_metric_annotation_note'])
        pure=next(r for r in self.group('10.1002/pat.3129') if r['sample_id']=='PP0')
        self.assertEqual(pure['T5_C'],'')
        self.assertIn('420',pure['source_thermal_metric_annotation_note'])
        self.assertIn('400',pure['source_thermal_metric_annotation_note'])
    def test_approximate_residue_qualifiers_stay_visible(self):
        rr=[r for r in self.rows if r.get('source_residue_observation_note')]
        self.assertEqual(len(rr),4)
        for r in rr:
            view=reader_table.reading_row(r,{'scope_class':r['material_scope_class']})
            self.assertIn(r['source_residue_observation_note'],view[20])
            self.assertIn('source_residue_qualifier=',r['source_residue_observation_note'])
        self.assertEqual(len({pairing.sample_state_id(r) for r in self.rows if r['material_scope_class']=='fiber_forming_polymer'}),2)

if __name__=='__main__':unittest.main()
