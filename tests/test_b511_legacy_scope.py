"""Keep scope-only admissions separate from new measurements and unresolved controls."""
import copy
import csv
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import pairing
import textile_scope


def nonempty_hash(row):
    payload = {key: value for key, value in row.items() if value != ''}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=True,
                                    separators=(',', ':')).encode()).hexdigest()


class LegacyScopeGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = ROOT / 'data/curation/archive/20261007/source_review_manifest_b511.json'
        cls.manifest = json.loads(path.read_text())
        cls.observations = cls.manifest['legacy_scope_observations']
        with (ROOT / 'data/tg_loi_master.csv').open(newline='') as handle:
            cls.master = list(csv.DictReader(handle))
        cls.by_key = {pairing.pair_key(row): row for row in cls.master}
        cls.registry = json.loads((ROOT / 'data/curation/textile_scope_registry.json').read_text())

    def test_all36_existing_observations_preserve_every_nonempty_field(self):
        self.assertEqual(len(self.observations), 36)
        for entry in self.observations:
            row = self.by_key[entry['pair_key']]
            self.assertEqual(nonempty_hash(row), entry['nonempty_original_row_sha256'])

    def test_unknown_field_and_literal_zero_cannot_escape_guard(self):
        entry = self.observations[-1]
        row = copy.deepcopy(self.by_key[entry['pair_key']])
        row['unknown_measurement'] = '0'
        self.assertNotEqual(nonempty_hash(row), entry['nonempty_original_row_sha256'])
        row['unknown_measurement'] = ''
        self.assertEqual(nonempty_hash(row), entry['nonempty_original_row_sha256'])

    def test_15_conditions_are_only13_physical_states(self):
        selected = [entry for entry in self.observations if entry['decision'] == 'admit_textile']
        self.assertEqual(len(selected), 15)
        self.assertEqual(len({pairing.sample_state_id(self.by_key[entry['pair_key']])
                              for entry in selected}), 13)
        self.assertEqual(sum(entry['scope_class'] == 'textile_fibre' for entry in selected), 5)

    def test_21_held_conditions_remain14_states(self):
        held = [entry for entry in self.observations if entry['decision'] == 'hold_scope']
        self.assertEqual(len(held), 21)
        self.assertEqual(len({pairing.sample_state_id(self.by_key[entry['pair_key']])
                              for entry in held}), 14)
        admitted, _ = textile_scope.classify(self.master, self.registry)
        keys = {pairing.pair_key(row) for row in admitted}
        self.assertFalse(keys & {entry['pair_key'] for entry in held})

    def test_conflicting_cotton_controls_are_whole_held(self):
        controls = [entry for entry in self.observations
                    if entry['sample_state'] in {'Cotton initial cotton fabric',
                                                'SiDOPO_CO_initial_14day_networkformation'}]
        self.assertEqual(len(controls), 3)
        self.assertTrue(all(entry['decision'] == 'hold_scope' for entry in controls))

    def test_alginate_residue_is800_not_cone_residue(self):
        entries = [entry for entry in self.observations
                   if entry['DOI'] == '10.1007/s12221-013-0767-2']
        expected = {'Alginic_acid_fiber_initial': '22.7', '1Alg-Zn_initial': '25.0',
                    '2Alg-Zn_initial': '24.8', '3Alg-Zn_initial': '26.0',
                    '4Alg-Zn_initial': '28.7'}
        self.assertEqual(len(entries), 5)
        for entry in entries:
            row = self.by_key[entry['pair_key']]
            self.assertEqual((row['residue_temp_C'], row['R800_pct']),
                             ('800', expected[entry['sample_state']]))
            self.assertEqual(entry['scope_class'], 'textile_fibre')

    def test_changed_state_cannot_inherit_scope_approval(self):
        entry = next(entry for entry in self.observations if entry['decision'] == 'admit_textile')
        changed = copy.deepcopy(self.master)
        row = next(row for row in changed if pairing.pair_key(row) == entry['pair_key'])
        row['washing_state'] = 'five post-treatment laundering cycles'
        with self.assertRaises(ValueError):
            textile_scope.classify(changed, self.registry)


if __name__ == '__main__':
    unittest.main()
