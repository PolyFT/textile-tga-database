"""Guard source-defined specimen states, threshold definitions and reuse exclusions."""
import csv
import hashlib
import json
import unittest
from pathlib import Path
from scripts.pairing import evidence_issues,measurement_fingerprint,pair_key,sample_state_id
from scripts.validate_tg_loi import known_issues
ROOT=Path(__file__).resolve().parents[1]
def rows(tag):
    with (ROOT/f'data/incoming/verified_source_batch_20261001_b84_{tag}.csv').open(newline='') as f:
        return list(csv.DictReader(f))
class SourceBatchB84Tests(unittest.TestCase):
    def test_exact_inputs_remain_review_bound_and_counted_by_state(self):
        manifest=json.loads((ROOT/'data/curation/archive/source_review_manifest_20261001_b84.json').read_text())
        all_rows=[]
        for source in manifest['files']:
            path=ROOT/source['file']
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),source['published_input_sha256'])
            with path.open(newline='') as f: data=list(csv.DictReader(f))
            self.assertEqual(len(data),source['conditions'])
            self.assertEqual(len({sample_state_id(r) for r in data}),source['states'])
            for row in data:
                self.assertEqual(row['reviewed_measurement_fingerprint'],measurement_fingerprint(row))
                self.assertFalse(evidence_issues(row))
            all_rows.extend(data)
        self.assertEqual(len(all_rows),9)
        self.assertEqual(len({pair_key(r) for r in all_rows}),9)
        self.assertEqual(len({sample_state_id(r) for r in all_rows}),6)
    def test_pi_ommt_keeps_membrane_form_and_excludes_undefined_peaks(self):
        data=rows('pi_ommt2018')
        self.assertEqual({float(r['LOI_pct']) for r in data},{29.2,30.4})
        for row in data:
            self.assertIn('nonwoven',row['material_form'])
            self.assertIn('film sample',row['source_material_form_LOI_raw'])
            self.assertFalse(row['Tmax1_C'])
            self.assertTrue(row['source_Tdmax_C'])
            self.assertEqual(float(row['residue_temp_C']),800)
    def test_anpp_initial_wool_is_two_states_at_four_conditions(self):
        data=rows('anpp_wool2023')
        self.assertEqual(len(data),4)
        self.assertEqual(len({sample_state_id(r) for r in data}),2)
        self.assertEqual({float(r['LOI_pct']) for r in data},{24.0,37.8})
        for row in data:
            self.assertEqual(float(row['residue_temp_C']),600)
            self.assertIn('white-text header artifact',row['limitations'])
            self.assertIn('Cut and crushed',row['source_material_form_TGA_raw'])
        self.assertEqual({float(r['R600_pct']) for r in data},{28.25,6.14,37.24,30.47})
    def test_dbd_control_retains_native_air_peak_numbering(self):
        data=rows('dbd_wool2021')
        self.assertEqual(len(data),2)
        self.assertEqual(len({sample_state_id(r) for r in data}),1)
        self.assertTrue(all(float(r['LOI_pct'])==25.7 for r in data))
        air=next(r for r in data if r['atmosphere']=='air')
        self.assertEqual(float(air['Tmax1_C']),79)
        self.assertEqual(float(air['Tmax2_C']),286)
        self.assertEqual(float(air['source_Tmax3_C']),513)
    def test_appcabt_source_onset_is_defined_as_five_percent_loss(self):
        data=rows('appcabt_cotton2014')
        self.assertEqual(len(data),1)
        row=data[0]
        self.assertEqual(float(row['T5_C']),235.4)
        self.assertFalse(row['Tonset_C'])
        self.assertFalse(row['Tmax1_C'])
        self.assertEqual(float(row['source_Tmax1_C']),323.3)
        self.assertEqual(float(row['source_Tmax2_C']),500.7)
        self.assertEqual(float(row['R600_pct']),33.1)
        self.assertEqual(float(row['LOI_pct']),27.9)
    def test_later_appcabt_control_reuse_hold_is_sample_scoped(self):
        with (ROOT/'data/curation/known_pairing_issues.csv').open(newline='') as f: issues=list(csv.DictReader(f))
        self.assertIn('possible_sample_alias',known_issues({'DOI':'10.1007/s11814-014-0095-2','sample_state':'CFs'},issues))
        self.assertNotIn('possible_sample_alias',known_issues(rows('appcabt_cotton2014')[0],issues))
    def test_public_holds_omit_private_cache_paths(self):
        text=(ROOT/'data/curation/archive/source_review_holds_20261001_b84.json').read_text()
        for marker in ['/workspace/','/tmp/','new-textile-cache/','new-textile-prep/','/root/']:
            self.assertNotIn(marker,text)
if __name__=='__main__':
    unittest.main()
