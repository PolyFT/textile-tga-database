"""Protect source definitions, conflicting values and original atmospheres in B857."""
import csv,json,unittest
from pathlib import Path
from scripts import pairing,reader_table
ROOT=Path(__file__).resolve().parents[1]
class TestB857SourceLimits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT/'data/incoming/verified_source_batch_20261007_b857_pp.csv').open(newline='') as f:cls.rows=list(csv.DictReader(f))
        cls.manifest=json.loads((ROOT/'data/curation/archive/20261007/source_review_manifest_b857.json').read_text())
    def group(self,doi):return [r for r in self.rows if r['DOI']==doi]
    def test_unknown_decomposition_peak_criteria_not_promoted(self):
        for doi in ['10.1002/app.47593','10.1002/app.49047','10.1002/app.30585','10.1002/app.39701','10.1002/pat.1958','10.1002/pc.21250','10.1002/app.34578']:
            rr=self.group(doi);self.assertTrue(rr,doi)
            for r in rr:self.assertEqual(r['Tmax1_C'],'',doi)
        for r in self.group('10.1002/pat.1958'):
            self.assertIn('not DTG',r['source_metric_limits'])
    def test_conflicting_residue_values_remain_unselected(self):
        conflicts=[r for r in self.group('10.1002/app.47593') if 'FRPP30' in r['source_sample_id'] or 'FRPP40' in r['source_sample_id']]
        self.assertEqual(len(conflicts),2)
        for r in conflicts:
            self.assertEqual(r['R700_pct'],'')
            self.assertTrue(r['source_R700_pct']);self.assertTrue(r['source_R700_prose_pct'])
        pp9=next(r for r in self.group('10.1002/app.41810') if r['sample_id']=='PP9')
        self.assertEqual(pp9['R500_pct'],'')
    def test_synthetic_air_original_and_unknown_composition_preserved(self):
        rr=[r for r in self.rows if r.get('source_original_atmosphere')=='synthetic air']
        self.assertEqual(len(rr),2)
        for r in rr:
            self.assertEqual(r['atmosphere'],'air')
            self.assertEqual(r['TG_atmosphere_composition'],'Source synthetic air; O2/N2 proportions not reported')
            self.assertIn('synthetic air',reader_table.reading_row(r,{'scope_class':r['material_scope_class']})[20])
    def test_approximate_residue_has_explicit_temperature_and_qualification(self):
        r=self.group('10.1002/app.34578')[0]
        self.assertEqual((r['R600_pct'],r['source_R600_qualifier']),('22','about'))
        self.assertIn('Abstract PDFp1',r['source_R600_definition_locator'])
        self.assertEqual(r['Tmax1_C'],'')
    def test_incomplete_conditions_and_shared_control_not_admitted(self):
        self.assertFalse(self.group('10.1002/app.48320'))
        self.assertFalse(self.group('10.1002/app.25178'))
        self.assertEqual({r['sample_id'] for r in self.group('10.1002/pc.21250')},{'PP-3','PP-7'})
        self.assertEqual((len(self.rows),len({pairing.sample_state_id(r) for r in self.rows}),len({pairing.pair_key(r) for r in self.rows})),(37,37,37))
        self.assertEqual(self.manifest['new_paired_sources'],13)
if __name__=='__main__':unittest.main()
