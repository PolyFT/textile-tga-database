"""Protect temperature definitions and unresolved specimen/LOI mappings."""
import csv
import sys
import unittest
from pathlib import Path
import pandas as pd

R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / 'scripts'))
import pairing
import validate_tg_loi as v

class LocalCottonB114Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (R / 'data/incoming/verified_source_batch_20261002_b114_local_aphompa_ctsgp_aspbh.csv').open(newline='') as f:
            cls.rows = list(csv.DictReader(f))

    def source(self, suffix):
        return [r for r in self.rows if r['DOI'].endswith(suffix)]

    def test_distinct_states_are_not_repeated_gas_records(self):
        report = v.build_tables(pd.DataFrame(self.rows), v.issue_list())[3]
        self.assertEqual(report['errors'], [])
        self.assertEqual((report['verified_exact_sample_states'], report['verified_exact_condition_records']), (5, 8))
        self.assertEqual(len(self.rows), 57)

    def test_aphompa_residue_coordinates_keep_exact_temperatures(self):
        rr = [r for r in self.source('03387-0') if r['pairing_status'] == 'verified_exact']
        self.assertEqual(len(rr), 2)
        for r in rr:
            self.assertEqual(r['residue_temp_C'], '600')
            self.assertIn('measurement_review_pending_or_stale', pairing.evidence_issues(dict(r, residue_temp_C='601')))
        control = next(r for r in rr if r['sample_state'] == 'Control cotton')
        self.assertEqual((control['R600_pct'], control['source_R601_pct']), ('11.9', '11.6'))
        treated = next(r for r in rr if r['sample_state'] != 'Control cotton')
        self.assertEqual((treated['R600_pct'], treated['source_R602_pct']), ('45.4', '45.4'))

    def test_aphompa_stage_boundaries_are_not_thresholds_or_peaks(self):
        for r in self.source('03387-0'):
            if r['pairing_status'] == 'verified_exact':
                self.assertTrue(all(not r.get(k, '') for k in ['Tonset_C', 'Tmax1_C', 'T5_C', 'T10_C']))
                self.assertIn('measurement_review_pending_or_stale', pairing.evidence_issues(dict(r, Tmax1_C='390')))

    def test_aphompa_air_ramp_is_not_borrowed_from_nitrogen(self):
        rr = [r for r in self.source('03387-0') if r['atmosphere'] == 'air']
        self.assertEqual(len(rr), 2)
        for r in rr:
            self.assertEqual(r['heating_rate_C_min'], '')
            self.assertEqual(r['pairing_status'], 'held_air_TG_heating_rate_unreported')
            self.assertEqual(r['reviewed_measurement_fingerprint'], '')

    def test_washed_loi_never_borrows_initial_tg(self):
        rr = [r for r in self.rows if r['pairing_status'] == 'held_washed_exact_LOI_no_own_TG']
        self.assertEqual(len(rr), 16)
        for r in rr:
            self.assertNotEqual(r['LOI_pct'], '')
            self.assertTrue(all(not r.get(k, '') for k in pairing.TG_FIELDS))
            self.assertEqual(r['reviewed_measurement_fingerprint'], '')

    def test_gbap_dose_and_wash_mapping_stay_unresolved(self):
        rr = self.source('03417-x')
        self.assertEqual(len(rr), 19)
        self.assertTrue(all(r['pairing_status'] != 'verified_exact' for r in rr))
        tg = [r for r in rr if r['pairing_status'] == 'held_TG_dose_or_control_LOI_wash_mapping_unresolved']
        self.assertEqual(len(tg), 2)
        for r in tg:
            self.assertEqual(r['LOI_pct'], '')
            self.assertEqual(r['reviewed_measurement_fingerprint'], '')

    def test_gbap_early_moisture_peaks_are_not_decomposition_peaks(self):
        rr = [r for r in self.source('03417-x') if r['source_Ta_max_C']]
        self.assertEqual({r['source_Ta_max_C'] for r in rr}, {'84.3', '96.5'})
        for r in rr:
            self.assertEqual(r['Tmax1_C'], '')
            self.assertEqual(r['Tonset_C'], '')
            self.assertIn('unresolved', r['source_DTGrate_units'])

    def test_ctsgp_discordant_initial_lois_have_no_approval(self):
        rr = [r for r in self.source('03469-z') if r['source_LOI_Table1_pct']]
        self.assertEqual(len(rr), 2)
        for r in rr:
            self.assertEqual((r['source_LOI_Table1_pct'], r['source_LOI_Table4_0wash_pct']), ('29.0', '28.8'))
            self.assertEqual(r['LOI_pct'], '')
            self.assertNotEqual(r['pairing_status'], 'verified_exact')

    def test_ctsgp_dyed_control_is_not_undyed_control(self):
        rr = [r for r in self.source('03469-z') if r['pairing_status'] == 'held_dyed_exact_LOI_no_own_TG']
        self.assertEqual(len(rr), 4)
        dyed = next(r for r in rr if r['source_bath_CTSGP_g_L'] == '0')
        self.assertEqual(dyed['LOI_pct'], '18.4')
        for r in rr:
            self.assertTrue(all(not r.get(k, '') for k in pairing.TG_FIELDS))

    def test_ctsgp_mass_at_peak_is_not_terminal_char(self):
        rr = [r for r in self.source('03469-z') if r['pairing_status'] == 'verified_exact']
        for r in rr:
            self.assertEqual(r['residue_temp_C'], '700')
            self.assertNotEqual(r['residue_at_Tmax_pct'], r['residue_pct'])
            self.assertIn('measurement_review_pending_or_stale', pairing.evidence_issues(dict(r, residue_pct=r['residue_at_Tmax_pct'])))

    def test_aspbh_air_control_char_is_blank_under_conflict(self):
        r = next(r for r in self.source('03488-w') if r['sample_state'] == 'Untreated cotton' and r['atmosphere'] == 'air')
        self.assertEqual(r['Tmax1_C'], '344')
        self.assertEqual(r['residue_pct'], '')
        self.assertEqual(r['R800_pct'], '')
        self.assertIn('measurement_review_pending_or_stale', pairing.evidence_issues(dict(r, residue_pct='0', residue_temp_C='800')))
        self.assertIn('no alias inferred', r['source_sparse_Tmax344_coincidence'])

    def test_aspbh_treated_nitrogen_has_no_estimated_peaks(self):
        r = next(r for r in self.source('03488-w') if r['sample_state'] == '350g/L ASPBH-treated cotton' and r['atmosphere'] == 'N2')
        self.assertEqual(r['R800_pct'], '42.9')
        self.assertTrue(all(not r.get(k, '') for k in ['Tonset_C', 'Tmax1_C', 'Tmax2_C']))
        self.assertIn('not exact peak', r['source_decomposition_intervals_C'])
        self.assertIn('unresolved', r['source_amine_identity_conflict'])
        self.assertIn('unreported', r['source_PBTCA_native'])

if __name__ == '__main__':
    unittest.main()
