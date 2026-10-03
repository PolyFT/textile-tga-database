"""Protect metric definitions, excluded provenance, and primary-versus-SI observations."""
import csv
import sys
import unittest
from pathlib import Path

import pandas as pd

P = Path(__file__).resolve().parent
private = P.name == 'work'
R = P.parent / 'repo' if private else P.parent
F = P / 'staged-local-textile-b147/publication_proposed.csv' if private else R / 'data/incoming/verified_source_batch_20261003_b147_local_textile.csv'
A = '10.1016/j.eurpolymj.2020.109483'
B = '10.1016/j.ijbiomac.2020.04.075'
sys.path.insert(0, str(R / 'scripts'))
import pairing
import validate_tg_loi as v


class TextileB147Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with F.open(newline='') as f: cls.rows = list(csv.DictReader(f))

    def row(self, doi, sample, gas='N2'):
        return next(r for r in self.rows if r['DOI'] == doi and r['sample_state'] == sample and r.get('atmosphere') == gas)

    def reject(self, row, **changes):
        self.assertIn('measurement_review_pending_or_stale', pairing.evidence_issues(dict(row, **changes)))

    def test_nine_states_eighteen_conditions_not_fiftyone_facts(self):
        report = v.build_tables(pd.DataFrame(self.rows).fillna(''), v.issue_list())[3]
        self.assertFalse(report['errors'])
        self.assertEqual((report['verified_exact_sample_states'], report['verified_exact_condition_records']), (9,18))
        self.assertEqual(len(self.rows), 51)

    def test_thirtythree_held_facts_never_grade_a(self):
        held = [r for r in self.rows if r['pairing_status'] != 'verified_exact']
        self.assertEqual(len(held),33)
        self.assertTrue(all(pairing.evidence_issues(r) for r in held))
        self.assertTrue(all(r['review_disposition'] == 'held_outside_verified_target' for r in held))

    def test_exact_fabric_form_and_wash_identity_are_bound(self):
        r = self.row(B,'PA66-D')
        self.assertIn('woven fabric, 100 g/m2, Jiaxing',r['material_form_TGA'])
        self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='GO-L free powder')))
        self.reject(r,washing_state='After5durabilitycycles')

    def test_epj_shared_control_held_even_with_numeric_tg_and_loi(self):
        for gas in ['air','N2']:
            r = self.row(A,'PA66-Control',gas)
            self.assertEqual(r['LOI_pct'],'19.5')
            self.assertTrue(r['T5_C'] and r['R800_pct'])
            self.assertNotEqual(r['pairing_status'],'verified_exact')
            self.assertIn('same_state_review_pending',pairing.evidence_issues(r))
            self.assertIn('notproofindependentexperiment',r['source_control_provenance_limit'])

    def test_epj_dose_suffix_is_not_washing_count(self):
        r = self.row(A,'PA66-D-GPTMS-20W')
        self.assertEqual(r['source_bath_g_L'],'200')
        self.assertIn('initial0durabilitycycles',r['washing_state'])
        self.reject(r,sample_state='PA66-D-GPTMS-10W')

    def test_epj_air_and_nitrogen_columns_cannot_swap(self):
        r = self.row(A,'PA66-D-GPTMS-20W','air')
        self.assertEqual((r['T5_C'],r['Tmax1_C'],r['R800_pct']),('330','446','6.9'))
        self.reject(r,T5_C='327',Tmax1_C='458',R800_pct='8.2')

    def test_epj_800_residue_not_700(self):
        r = self.row(A,'PA66-D-APTES-20W')
        self.assertEqual((r['R800_pct'],r['residue_temp_C']),('9.2','800'))
        self.assertFalse(r.get('R700_pct'))
        self.reject(r,R800_pct='',R700_pct='9.2',residue_temp_C='700')

    def test_epj_t5_not_t10_or_undefined_onset(self):
        r = self.row(A,'PA66-D-APTES-20W')
        self.assertEqual(r['T5_C'],'368')
        self.assertFalse(r.get('T10_C') or r.get('Tonset_C'))
        self.reject(r,T5_C='',T10_C='368')

    def test_epj_only_air_second_dissociation_peak(self):
        a = self.row(A,'PA66-D-APTES-10W','air')
        n = self.row(A,'PA66-D-APTES-10W')
        self.assertEqual((a['Tmax1_C'],a['Tmax2_C']),('427','628'))
        self.assertFalse(n.get('Tmax2_C') or n.get('Tmax3_C'))
        self.reject(n,Tmax2_C='628')

    def test_epj_primary_control_table_prose_difference_not_repaired(self):
        r = self.row(A,'PA66-Control','air')
        self.assertEqual((r['Tmax1_C'],r['Tmax2_C']),('466','597'))
        self.assertIn('proseapprox464/589',r['limitations'])
        self.assertNotEqual(r['pairing_status'],'verified_exact')

    def test_epj_addon_not_bath_concentration(self):
        r = self.row(A,'PA66-D-GPTMS-20W')
        self.assertEqual((r['source_addon_pct'],r['source_bath_g_L']),('15.2','200'))
        self.assertIn('(W1-W)/W*100',r['source_addon_definition'])
        self.assertIn('NOTdryfabricmassfraction',r['composition'])

    def test_epj_unknown_main_conditions_and_unread_si_remain_explicit(self):
        r = self.row(A,'PA66-D-APTES-20W')
        self.assertTrue(r['source_TG_mass_pan_flow_start_end'].startswith('Unreported'))
        self.assertFalse(r.get('TG_end_C'))
        self.assertIn('TGIR55mLminNOTborrowed',r['source_TG_mass_pan_flow_start_end'])
        self.assertIn('SIunread',r['limitations'])

    def test_epj_fifteen_washed_vft_observations_no_tg_loi(self):
        rows = [r for r in self.rows if r['DOI']==A and r['pairing_status'].startswith('held_washed')]
        self.assertEqual(len(rows),15)
        self.assertTrue(all(not r.get('LOI_pct') and all(not r.get(k) for k in pairing.TG_FIELDS) for r in rows))
        self.assertEqual(next(r for r in rows if r['sample_state']=='PA66-D-APTES-20W after10nativewashingcycles')['source_native_UL94_rating'],'UL-94-V1')

    def test_biomac_t10_not_t5_or_onset(self):
        r = self.row(B,'PA66-D')
        self.assertEqual(r['T10_C'],'410')
        self.assertFalse(r.get('T5_C') or r.get('Tonset_C'))
        self.reject(r,T10_C='',T5_C='410')

    def test_biomac_native_air_peaks_not_extra_nitrogen_peaks(self):
        a = self.row(B,'PA66-A','air')
        n = self.row(B,'PA66-A')
        self.assertEqual((a['Tmax1_C'],a['Tmax2_C']),('463','575'))
        self.assertFalse(n.get('Tmax2_C') or n.get('Tmax3_C'))
        self.assertIn('generic3stepproseNOTthirdnumericpeak',n['source_TG_peak_definition'])
        self.reject(n,Tmax2_C='575')

    def test_biomac_700_residue_not_800_or_cone_char(self):
        r = self.row(B,'PA66-D')
        self.assertEqual((r['R700_pct'],r['residue_temp_C']),('7.4','700'))
        self.assertFalse(r.get('R800_pct'))
        self.reject(r,R700_pct='',R800_pct='7.4',residue_temp_C='800')
        self.reject(r,R700_pct='8.1')

    def test_biomac_plusminus_has_no_invented_sd_or_replicates(self):
        r = self.row(B,'PA66-D')
        self.assertEqual((r['source_LOI_plusminus'],r['source_residue_plusminus']),('1','0.3'))
        self.assertIn('SD/SE/range/repeatsunreported',r['source_uncertainty_definition'])
        self.assertEqual(r['source_LOI_repeats'],'Unreported')

    def test_biomac_control_primary20_not_si21(self):
        r = self.row(B,'PA66-N')
        self.assertEqual(r['LOI_pct'],'20')
        self.assertEqual(r['source_LOI_plusminus'],'1')
        self.assertIn('primaryTable4used',r['source_SI_conflict'])
        self.reject(r,LOI_pct='21')
        h = next(r for r in self.rows if r['pairing_status']=='held_SI_control_conflict_without_own_TG')
        self.assertEqual(h['LOI_pct'],'21')
        self.assertTrue(all(not h.get(k) for k in pairing.TG_FIELDS))

    def test_biomac_si_initial_addon_differences_preserved(self):
        c = self.row(B,'PA66-C')
        d = self.row(B,'PA66-D')
        self.assertEqual((c['source_reported_addon_pct'],c['source_SI_reported_addon_pct']),('4.0','3.6'))
        self.assertEqual((d['source_reported_addon_pct'],d['source_SI_reported_addon_pct']),('6.0','5.7'))
        self.assertIn('EqtextPDFp10unreadnotreconstructed',d['source_addon_definition'])

    def test_biomac_si_eleven_other_recipe_time_trials_do_not_borrow_tg(self):
        trials = [r for r in self.rows if r['pairing_status']=='held_SI_trial_LOI_without_own_TG']
        self.assertEqual(len(trials),11)
        self.assertTrue(all(r['LOI_pct'] and all(not r.get(k) for k in pairing.TG_FIELDS) for r in trials))
        self.assertEqual({r['source_impregnation_time'] for r in trials},{'12h','1h','30min','Unreported'})
        self.assertEqual(sum(r['source_application_method']=='LbL10BL' for r in trials),1)

    def test_biomac_four_washed_cone_facts_without_tg_loi(self):
        rows = [r for r in self.rows if r['DOI']==B and r['pairing_status'].startswith('held_washed')]
        self.assertEqual(len(rows),4)
        self.assertTrue(all(not r.get('LOI_pct') and all(not r.get(k) for k in pairing.TG_FIELDS) for r in rows))
        self.assertEqual([r['source_cone_pHRR_reduction_pct'] for r in rows],['13','15','12','17'])

    def test_biomac_preproof_not_final_year_or_vor(self):
        r = self.row(B,'PA66-A')
        self.assertFalse(r['year'])
        self.assertIn('Journal Pre-proof accepted2020-04-10',r['source_document_version'])
        self.assertIn('finalpublicationyearunknown',r['source_document_version'])

    def test_biomac_bath_not_synthesis_stock_or_final_composition(self):
        r = self.row(B,'PA66-D')
        self.assertEqual((r['source_GO_L_g_L'],r['source_GO_PA_g_L'],r['source_PA_g_L'],r['source_CS_g_L'],r['source_CA_g_L']),('0.5','','15','2.5','50'))
        self.assertIn('5mgmLGOplus3gligninfinal100mL',r['source_synthesis'])
        self.assertIn('NOTfinalfabricmassfractions',r['composition'])

    def test_biomac_native_control_recipe_dashes_not_numeric_zero(self):
        r = self.row(B,'PA66-N')
        self.assertTrue(all(not r[k] for k in ['source_GO_L_g_L','source_GO_PA_g_L','source_PA_g_L','source_CS_g_L','source_CA_g_L','source_reported_addon_pct']))
        self.assertEqual(self.row(A,'PA66-Control')['source_addon_pct'],'0')

    def test_biomac_own_instrument_dimensions_and_gas_rate_bound(self):
        r = self.row(B,'PA66-A')
        self.assertEqual((r['LOI_instrument'],r['source_LOI_dimensions_mm']),('JF-3,JiangningAnalyticalInstrumentFactoryNanjing','140x50'))
        self.assertEqual(self.row(A,'PA66-D-GPTMS-10W')['source_LOI_dimensions_mm'],'150x58')
        self.reject(r,atmosphere='air')
        self.reject(r,heating_rate_C_min='10')


if __name__ == '__main__': unittest.main()
