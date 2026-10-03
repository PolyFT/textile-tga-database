"""Source-specific guards against false textile TG/LOI correspondence."""
import csv
import sys
import unittest
from pathlib import Path

import pandas as pd

P = Path(__file__).resolve().parent
private = P.name == 'work'
R = P.parent / 'repo' if private else P.parent
F = P / 'staged-local-textile-b154/publication_proposed.csv' if private else R / 'data/incoming/verified_source_batch_20261004_b154_local_textile.csv'
sys.path.insert(0, str(R / 'scripts'))
import pairing
import validate_tg_loi as v

A = '10.1007/s10570-022-04829-7'
B = '10.1007/s10570-023-05051-9'
C = '10.1007/s10570-022-04929-4'

class TextileB154Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with F.open(newline='') as f:
            cls.rows = list(csv.DictReader(f))

    def row(self, doi, label, gas='N2'):
        return next(r for r in self.rows if r['DOI'] == doi and r['sample_state'] == label + ' initial cotton fabric' and r['atmosphere'] == gas)

    def reject(self, row, **changes):
        self.assertIn('measurement_review_pending_or_stale', pairing.evidence_issues(dict(row, **changes)))

    def test_nine_states_fourteen_conditions_not31_facts(self):
        p = v.build_tables(pd.DataFrame(self.rows).fillna(''), v.issue_list())[3]
        self.assertFalse(p['errors'])
        self.assertEqual((p['verified_exact_sample_states'], p['verified_exact_condition_records']), (9, 14))
        self.assertEqual(len(self.rows), 31)

    def test_seventeen_held_facts_excluded(self):
        held = [r for r in self.rows if r['pairing_status'] != 'verified_exact']
        self.assertEqual(len(held), 17)
        self.assertTrue(all(pairing.evidence_issues(r) for r in held))
        self.assertEqual([sum(r['DOI'] == d for r in held) for d in [A,B,C]], [6,7,4])

    def test_ta_pa_pdms_five_native_nitrogen_profiles(self):
        for label, values in [('Cotton',(319,390,18)),('TA-1% PA-PDMS',(314,352,24)),('TA-2% PA-PDMS',(307,346,26)),('TA-4% PA-PDMS',(285,319,36)),('TA-8% PA-PDMS',(251,279,46))]:
            r = self.row(B,label)
            self.assertEqual(tuple(float(r[k]) for k in ['T5_C','Tmax1_C','R800_pct']), values)

    def test_ta_pa_pdms_three_native_air_profiles(self):
        for label, values in [('Cotton',(340,468,0)),('TA-2% PA-PDMS',(295,498,7)),('TA-8% PA-PDMS',(265,498,10.5))]:
            r = self.row(B,label,'air')
            self.assertEqual(tuple(float(r[k]) for k in ['Tmax1_C','Tmax2_C','R800_pct']), values)
            self.assertFalse(r['T5_C'])

    def test_npdbdpa_four_native_nitrogen_profiles(self):
        for label, values in [('Cot0',(307,327,361,13.92)),('Cot5',(283,297,315,34.48)),('Cot10',(278,292,312,36.02)),('Cot15',(261,287,309,37.36))]:
            r = self.row(C,label)
            self.assertEqual(tuple(float(r[k]) for k in ['T5_C','T10_C','Tmax1_C','R750_pct']), values)

    def test_npdbdpa_two_native_air_profiles(self):
        for label, values in [('Cot0',(250,306,336,446,1.02)),('Cot15',(156,271,303,484,7.34))]:
            r = self.row(C,label,'air')
            self.assertEqual(tuple(float(r[k]) for k in ['T5_C','T10_C','Tmax1_C','Tmax2_C','R750_pct']), values)

    def test_residue_endpoints_not_cross_assigned(self):
        b = self.row(B,'TA-8% PA-PDMS'); c = self.row(C,'Cot15')
        self.assertEqual((b['residue_temp_C'],c['residue_temp_C']),('800','750'))
        self.reject(b,residue_temp_C='750'); self.reject(c,residue_temp_C='800')

    def test_gas_and_ramp_changes_require_review(self):
        for d,label in [(B,'TA-4% PA-PDMS'),(C,'Cot10')]:
            r = self.row(d,label); self.assertEqual(r['heating_rate_C_min'],'10')
            self.reject(r,atmosphere='air'); self.reject(r,heating_rate_C_min='20')

    def test_t5_t10_not_onset_or_decomposition_peak(self):
        r = self.row(C,'Cot15','air')
        self.assertEqual((r['T5_C'],r['T10_C'],r['Tmax1_C']),('156','271','303'))
        self.assertFalse(r.get('Tonset_C'))
        self.reject(r,T5_C='',Tonset_C='156'); self.reject(r,Tmax1_C='156')

    def test_waterloss_not_inserted_as_decomposition_peak(self):
        r = self.row(C,'Cot0'); self.assertEqual(r['Tmax1_C'],'361')
        self.reject(r,Tmax1_C='70')

    def test_air_second_peak_not_first_peak(self):
        r = self.row(C,'Cot15','air')
        self.assertEqual((r['Tmax1_C'],r['Tmax2_C']),('303','484'))
        self.reject(r,Tmax1_C='484',Tmax2_C='303')

    def test_dtg_rates_remain_percent_per_degree(self):
        r = self.row(B,'Cotton'); c = self.row(C,'Cot0','air')
        self.assertEqual(r['source_DTGmax1_rate_pct_per_C'],'1.7')
        self.assertEqual((c['source_DTGmax1_rate_pct_per_C'],c['source_DTGmax2_rate_pct_per_C']),('1.04','0.34'))
        self.assertIn('notpercentpermin',r['source_DTG_rate_definition'])

    def test_native_air_zero_residue_is_valid_not_missing(self):
        r = self.row(B,'Cotton','air')
        self.assertEqual((r['R800_pct'],r['residue_pct']),('0','0'))
        self.assertFalse(pairing.evidence_issues(r))

    def test_tg_start_not_inferred_for_air_source_b(self):
        r = self.row(B,'Cotton','air')
        self.assertFalse(r['TG_start_C']); self.assertEqual(r['TG_end_C'],'800')
        self.assertIn('Unreported',r['source_air_TG_start'])
        self.assertEqual(self.row(B,'Cotton')['TG_start_C'],'30')

    def test_tgir_flow_and_range_not_plain_tg(self):
        r = self.row(C,'Cot15'); b = self.row(B,'TA-8% PA-PDMS')
        self.assertEqual((r['TG_start_C'],r['TG_end_C']),('35','750'))
        self.assertIn('35-800',r['source_TGIR_method'])
        self.assertIn('40-800',b['source_TGIR_method'])
        self.assertTrue(all(not x.get('source_TG_flow_mL_min') for x in [r,b]))

    def test_native_loi_dimensions_59_not_normalized58(self):
        r = self.row(C,'Cot15'); b = self.row(B,'TA-8% PA-PDMS')
        self.assertEqual((r['source_LOI_dimensions_mm'],b['source_LOI_dimensions_mm']),('150x59','150x58'))

    def test_control_loi_native_table19_body18_conflict_retained(self):
        r = self.row(B,'Cotton')
        self.assertEqual(r['LOI_pct'],'19')
        self.assertIn('body18',r['source_control_LOI_discrepancy'])
        self.reject(r,LOI_pct='18')

    def test_loi_uncertainty_type_not_guessed(self):
        for d,label,loi,unc in [(B,'TA-4% PA-PDMS','24','0.2'),(C,'Cot15','41.3','0.3')]:
            r = self.row(d,label)
            self.assertEqual((r['LOI_pct'],r['LOI_uncertainty_pct']),(loi,unc))
            self.assertIn('SD/SE',r['source_LOI_uncertainty_definition'])

    def test_material_density_and_recipe_not_cross_assigned(self):
        b = self.row(B,'TA-8% PA-PDMS'); c = self.row(C,'Cot15')
        self.assertIn('120g/m2',b['material_form']); self.assertIn('122g/m2',c['material_form'])
        self.assertIn('PDMS',b['treatment_method']); self.assertIn('N-PDBDPA',c['treatment_method'])
        self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(b,material_form_TGA=c['material_form_TGA'])))

    def test_initial_weight_gain_is_not_bath_concentration(self):
        b = self.row(B,'TA-8% PA-PDMS'); c = self.row(C,'Cot15')
        self.assertEqual((b['source_weight_gain_wt_pct'],c['source_weight_gain_wt_pct']),('19.38','14.13'))
        self.assertIn('basisunreported',b['composition']); self.assertIn('15wtbath',c['composition'])

    def test_control_composition_has_no_fr_and_each_dose_is_individual(self):
        for d,label in [(B,'Cotton'),(C,'Cot0')]:
            self.assertIn('noFR',self.row(d,label)['composition'])
        for label,dose in [('TA-1% PA-PDMS','PA1%bath'),('TA-2% PA-PDMS','PA2%bath'),('TA-4% PA-PDMS','PA4%bath'),('TA-8% PA-PDMS','PA8%bath')]:
            self.assertIn(dose,self.row(B,label)['composition'])
        for label,dose in [('Cot5','N-PDBDPA5wtbath'),('Cot10','N-PDBDPA10wtbath'),('Cot15','N-PDBDPA15wtbath')]:
            self.assertIn(dose,self.row(C,label)['composition'])

    def test_source_c_cure_and_control_remain_distinct(self):
        r = self.row(C,'Cot15'); control = self.row(C,'Cot0')
        self.assertIn('65C40min',r['treatment_method']); self.assertIn('180C20min',r['treatment_method'])
        self.assertIn('FRcureprotocolnotassigned',control['treatment_method'])

    def test_official_correction_is_sem_only(self):
        r = self.row(B,'TA-8% PA-PDMS')
        self.assertIn('05077-z',r['source_correction']); self.assertIn('Fig2a/bSEM',r['source_correction'])

    def test_seven_source_b_washed_lois_no_own_tg(self):
        held = [r for r in self.rows if r['DOI']==B and r['pairing_status']!='verified_exact']
        self.assertEqual([r['LOI_pct'] for r in held],['21','20.9','20.7','22.6','22.3','21.9','21'])
        self.assertTrue(all(not r.get(k) for r in held for k in pairing.TG_FIELDS))
        self.assertTrue(all(not r['LOI_uncertainty_pct'] for r in held))

    def test_washed_thirty_source_c_table31_8_not_body31_1(self):
        r = next(r for r in self.rows if r['DOI']==C and 'after30' in r['sample_state'])
        self.assertEqual((r['LOI_pct'],r['LOI_uncertainty_pct']),('31.8','0.1'))
        self.assertIn('body31.1',r['source_washed_30_LOI_conflict'])
        self.assertFalse(r['Tmax1_C'])

    def test_wash_cycles_equivalent_not_laboratory_repeats(self):
        held = [r for r in self.rows if r['DOI'] in [B,C] and r['pairing_status']!='verified_exact']
        self.assertEqual(len(held),11)
        self.assertTrue(all('equiv5cycles' in r['washing_state'] for r in held))
        self.assertTrue(any('10rubberballs' in r['washing_state'] for r in held if r['DOI']==C))

    def test_washed_cannot_replace_initial_state(self):
        r = self.row(C,'Cot15'); self.reject(r,LOI_pct='27.5'); self.reject(r,washing_state='50launderingcycles')
        self.assertEqual(self.row(B,'TA-8% PA-PDMS')['LOI_pct'],'32')

    def test_cone_residue_not_tg_residue(self):
        b = self.row(B,'TA-8% PA-PDMS'); c = self.row(C,'Cot15')
        self.reject(b,R800_pct='12.1'); self.reject(c,R750_pct='12.88')

    def test_ambiguous_cds_app_program_stays_held(self):
        held = [r for r in self.rows if r['DOI']==A]
        self.assertTrue(all(r['pairing_status']!='verified_exact' for r in held))
        initials = [r for r in held if 'initial' in r['sample_state']]
        self.assertTrue(all(not r['heating_rate_C_min'] for r in initials))
        self.assertTrue(all('laterramp/holdsambiguous' in r['source_reported_TG_program'] for r in initials))

    def test_ambiguous_char_and_undefined_onset_not_invented(self):
        r = self.row(A,'CP-C2'); self.assertEqual(r['Tmax1_C'],'423.21')
        self.assertFalse(r['R600_pct']); self.assertFalse(r.get('Tonset_C'))
        self.assertEqual(r['source_reported_undefined_Tonest_C'],'212.12')
        self.assertIn('notinferabsolute/deltachar',r['source_CPC2_R600_conflict'])

    def test_all_accepted_metrics_bound_to_same_textile_state(self):
        accepted = [r for r in self.rows if r['pairing_status']=='verified_exact']
        self.assertTrue(all(r['numeric_evidence_type']=='tabulated' for r in accepted))
        self.assertTrue(all(not pairing.evidence_issues(r) for r in accepted))
        for r in accepted:
            self.reject(r,LOI_pct=str(float(r['LOI_pct'])+1))
            self.reject(r,sample_state='Remoldedpolymer-sheet')

if __name__ == '__main__':
    unittest.main()
