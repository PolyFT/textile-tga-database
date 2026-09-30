import unittest

import pandas as pd

from scripts import pairing as p
from scripts import validate_tg_loi as v
from test_pairing_validation import approve, observation


class HeliumConditionTests(unittest.TestCase):
    def test_helium_symbol_and_name_identify_one_condition(self):
        self.assertEqual(p.pair_key(observation(atmosphere='He')),
                         p.pair_key(observation(atmosphere='helium')))
        self.assertEqual(p.measurement_fingerprint(observation(atmosphere='He')),
                         p.measurement_fingerprint(observation(atmosphere='Helium')))

    def test_reviewed_pure_helium_enters_master(self):
        master, _, _, report = v.build_tables(pd.DataFrame([approve(observation(atmosphere='He'))]))
        self.assertEqual(len(master), 1)
        self.assertEqual(report['verified_exact_sample_states'], 1)

    def test_distinct_gases_are_conditions_not_extra_samples(self):
        rows = [approve(observation(atmosphere=gas)) for gas in ['He', 'N2', 'air']]
        master, _, _, report = v.build_tables(pd.DataFrame(rows))
        self.assertEqual(len(master), 3)
        self.assertEqual(len(set(master.pair_key)), 3)
        self.assertEqual(report['verified_exact_sample_states'], 1)

    def test_changing_helium_to_nitrogen_invalidates_review(self):
        row = approve(observation(atmosphere='He'))
        row['atmosphere'] = 'N2'
        master, candidates, _, _ = v.build_tables(pd.DataFrame([row]))
        self.assertTrue(master.empty)
        self.assertIn('measurement_review_pending_or_stale', candidates.iloc[0].review_reasons)

    def test_helium_still_requires_source_review(self):
        master, _, _, _ = v.build_tables(pd.DataFrame([observation(atmosphere='He')]))
        self.assertTrue(master.empty)

    def test_unspecified_inert_or_helium_oxygen_mix_remains_pending(self):
        for gas in ['inert', 'He+O2', '79%He/21%O2', '']:
            with self.subTest(gas=gas):
                master, candidates, _, _ = v.build_tables(pd.DataFrame([approve(observation(atmosphere=gas))]))
                self.assertTrue(master.empty)
                self.assertIn('missing_or_unresolved_atmosphere', candidates.iloc[0].review_reasons)


if __name__ == '__main__':
    unittest.main()
