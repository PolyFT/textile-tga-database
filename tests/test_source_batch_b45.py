"""Protect source-specific TG method, peak and laundering-state assignments."""
import csv
import hashlib
import json
import unittest
from pathlib import Path

import pandas as pd
from scripts.pairing import evidence_issues, measurement_fingerprint
from scripts.validate_tg_loi import build_tables

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'data/incoming/verified_source_batch_20261001_b45.csv'


def rows():
    with INPUT.open(newline='', encoding='utf-8') as handle:
        return list(csv.DictReader(handle))


class SourceBatchB45Tests(unittest.TestCase):
    def test_counting_and_fingerprint_binding(self):
        data = rows()
        self.assertEqual(len(data), 9)
        self.assertEqual(len({(r['DOI'], r['sample_state'], r['washing_state']) for r in data}), 8)
        for row in data:
            self.assertFalse(evidence_issues(row))
            self.assertEqual(row['reviewed_measurement_fingerprint'], measurement_fingerprint(row))
        changed = dict(data[0], LOI_pct='31')
        self.assertIn('measurement_review_pending_or_stale', evidence_issues(changed))

    def test_proban_wash_states_and_TG_not_MCC(self):
        data = [r for r in rows() if r['DOI'] == '10.3390/ma15155373']
        self.assertEqual({r['sample_state'] for r in data}, {'UNW', '46_10x', '47_10x', '48_10x', '49_10x'})
        self.assertTrue(all(r['washing_state'] and r['residue_temp_C'] == '850' for r in data))
        self.assertEqual({float(r['Tmax1_C']) for r in data}, {340.04, 342.89, 340.00, 340.76, 333.35})
        self.assertEqual({float(r['residue_pct']) for r in data}, {11.206, 7.287, 9.549, 9.485, 14.932})
        self.assertFalse(any(r.get('R700_pct') or r.get('R800_pct') for r in data))

    def test_conflicted_proban_onset_is_withheld(self):
        unw = next(r for r in rows() if r['sample_state'] == 'UNW')
        self.assertEqual(unw['Tonset_C'], '')
        holds = json.loads((ROOT/'data/curation/archive/source_review_holds_20261001_b45.json').read_text())
        conflict = next(h for h in holds if h.get('sample_state') == 'UNW')
        self.assertEqual(set(conflict['source_values'].values()), {321.1, 321.61})

    def test_PET_route_and_stage_assignments(self):
        data = {r['sample_state']: r for r in rows() if r['DOI'] == '10.3390/polym12040774'}
        pure, modified = data['PET std'], data['PET + 0.50% C15A']
        self.assertEqual((pure['Tmax1_C'], pure['Tmax2_C']), ('448.3', '569.7'))
        self.assertEqual((modified['Tmax1_C'], modified['Tmax2_C']), ('261.1', '456.3'))
        self.assertIn('not moisture', modified['Tmax1_assignment'])
        self.assertTrue(all(r['gas_flow_mL_min'] == '50' and r['TG_end_C'] == '750' for r in data.values()))

    def test_wool_control_and_atmosphere_count(self):
        data = [r for r in rows() if r['DOI'] == '10.3390/polym13234111']
        self.assertEqual({r['sample_state'] for r in data}, {'Control'})
        self.assertEqual({r['atmosphere'] for r in data}, {'air', 'N2'})
        self.assertTrue(all(r['LOI_pct'] == '24' and r['heating_rate_C_min'] == '10' for r in data))
        self.assertTrue(all('pretreated' in r['treatment_state'] for r in data))
        self.assertTrue(all(not r.get('gas_flow_mL_min') for r in data))

    def test_missing_conditions_stay_outside_verified_target(self):
        with (ROOT/'data/curation/archive/source_review_condition_partial_20261001_b45.csv').open(newline='') as handle:
            data = list(csv.DictReader(handle))
        self.assertEqual(len(data), 5)
        self.assertTrue(all(not r['atmosphere'] for r in data))
        master, _, _, report = build_tables(pd.DataFrame(data))
        self.assertTrue(master.empty)
        self.assertEqual(report['verified_exact_sample_states'], 0)
        cotton = next(r for r in data if r['DOI'] == '10.1039/D5RA00402K')
        self.assertFalse(cotton.get('Tmax1_C') or cotton.get('Tmax2_C'))

    def test_manifest_hashes(self):
        manifest = json.loads((ROOT/'data/curation/archive/source_review_manifest_20261001_b45.json').read_text())
        for item in manifest['files']:
            self.assertEqual(hashlib.sha256((ROOT/item['file']).read_bytes()).hexdigest(), item['published_input_sha256'])
