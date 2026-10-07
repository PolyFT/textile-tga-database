import csv,json,unittest
from pathlib import Path
from scripts import pairing

ROOT=Path(__file__).resolve().parents[1]
class B758SourceGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT/'data/incoming/verified_source_batch_20261007_b758_pa66_pa6.csv').open(newline='') as f:cls.rows=list(csv.DictReader(f))
        cls.manifest=json.loads((ROOT/'data/curation/archive/20261007/source_review_manifest_b758.json').read_text())
    def test_seventeen_source_states_and_conditions_not_pending_controls(self):
        self.assertEqual(len(self.rows),17)
        self.assertEqual(len({pairing.sample_state_id(r) for r in self.rows}),17)
        self.assertEqual(sum(r['DOI']=='10.1016/j.polymdegradstab.2020.109220' for r in self.rows),16)
        self.assertFalse(any(r['sample_name'] in {'S0','S2','AlPi7.5'} for r in self.rows))
    def test_conflicting_T5_not_repaired_and_usable_TG_retained(self):
        r=next(r for r in self.rows if r['sample_name']=='AlPiMPP10')
        self.assertEqual([r['source_original_T5_Table1_C'],r['source_original_T5_Table2_C']],['338','368'])
        self.assertEqual(r['T5_C'],'')
        self.assertEqual([r['Tmax1_C'],r['R500_pct']],['433','21.5'])
    def test_raw_residue_rate_and_assay_form_remain_distinct(self):
        for r in self.rows:
            self.assertFalse(r.get('R580_pct'))
            self.assertEqual(r['material_form_TGA'],r['material_form_LOI'])
            self.assertTrue(r['source_original_material_form_LOI'])
            self.assertIn('geometry unreported',r['material_form_TGA'])
            self.assertFalse(pairing.evidence_issues(r))
        r=next(r for r in self.rows if r['sample_name']=='S9')
        self.assertEqual([r['source_Rpeak_pct_per_min_raw'],r['Tmax1_C'],r['R800_pct']],['19.8','434.2','8.4'])
    def test_ordinary_gas_and_ramp_and_batch_counts(self):
        for r in self.rows:
            self.assertEqual(r['heating_rate_C_min'],'10')
            self.assertEqual(r['atmosphere'],'N2' if r['sample_name']=='S9' else 'air')
        self.assertEqual([self.manifest['selected_new_states'],self.manifest['selected_new_TG'],self.manifest['new_sources']],[29,29,4])
