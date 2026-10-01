"""Regressions for source-native metrics, dose holds and unmatched washing states."""
import csv
import sys
import unittest
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import pairing
import validate_tg_loi as v

class CottonSourceEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with(ROOT/'data/incoming/verified_source_batch_20261001_b89_local_cotton.csv').open(newline='')as h:
            cls.rows=list(csv.DictReader(h))

    def source(self,suffix):
        return [r for r in self.rows if r['DOI'].endswith(suffix)]

    def test_counts_exclude_all_unpaired_facts(self):
        rep=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3]
        self.assertEqual(rep['errors'],[])
        self.assertEqual(len(self.rows),28)
        self.assertEqual(rep['verified_exact_sample_states'],6)
        self.assertEqual(rep['verified_exact_condition_records'],8)
        self.assertEqual(sum(r['pairing_status']!='verified_exact'for r in self.rows),20)

    def test_amop_t10_not_onset_stage_or_gas_peak(self):
        for r in self.source('03041-9'):
            self.assertEqual(r.get('T5_C',''),'')
            self.assertEqual(r['Tonset_C'],'')
            self.assertEqual(r['Tmax1_C'],'')
            self.assertEqual(r.get('TGA_sample_mass_mg',''),'')
        initial=[r for r in self.source('03041-9')if r['pairing_status']=='verified_exact'and r['atmosphere']=='nitrogen']
        self.assertEqual({float(r['T10_C'])for r in initial},{310,289})

    def test_amop_residue720_not_run_end800(self):
        accepted=[r for r in self.source('03041-9')if r['pairing_status']=='verified_exact']
        self.assertEqual({float(r['residue_pct'])for r in accepted},{9,33,.14})
        for r in accepted:
            self.assertEqual(float(r['residue_temp_C']),720)
            self.assertEqual(float(r['TG_end_C']),800)
            self.assertEqual(r.get('R800_pct',''),'')
        treated=next(r for r in accepted if r['sample_state'].startswith('15%'))
        self.assertEqual(float(treated['source_residue_at325C_pct']),53)
        self.assertEqual(float(treated['AMOP_bath_pct']),15)
        self.assertEqual(treated['AMOP_bath_percentage_basis'],'Unspecified')

    def test_amop_generic_air_approximation_is_unapproved(self):
        r=next(r for r in self.source('03041-9')if 'generic air'in r['sample_state'])
        self.assertEqual(r['LOI_pct'],'')
        self.assertEqual(r['residue_pct'],'')
        self.assertEqual(r['residue_temp_C'],'')
        self.assertEqual(r['source_residue_qualifier'],'about')
        self.assertEqual(float(r['source_residue_approximate_at760C_pct']),6)
        self.assertEqual(r['reviewed_measurement_fingerprint'],'')

    def test_apctsi_native750_and_generic_dose_hold(self):
        tg=[r for r in self.source('04127-8')if r['R750_pct']]
        self.assertEqual(len(tg),4)
        for r in tg:
            self.assertEqual(float(r['residue_temp_C']),750)
            self.assertEqual(float(r['TG_end_C']),800)
            self.assertEqual(r.get('R800_pct',''),'')
            self.assertEqual(r.get('T5_C',''),'')
            self.assertEqual(r.get('TGA_gas_flow_mL_min',''),'')
            if 'generic'in r['sample_state']:
                self.assertEqual(r['LOI_pct'],'')
                self.assertEqual(r['pairing_status'],'treated_formulation_crosswalk_unresolved')
                self.assertEqual(r['reviewed_measurement_fingerprint'],'')
            else:self.assertEqual(float(r['LOI_pct']),18)

    def test_all_washed_and_loi_only_states_remain_unpaired(self):
        held=[r for r in self.rows if r['pairing_status']!='verified_exact']
        washed=[r for r in held if r['treatment_state'].startswith('After')]
        self.assertEqual(len(washed),5)
        self.assertEqual({float(r['LOI_pct'])for r in washed},{19.5,27.8,26.5,25.8,25.3})
        for r in washed:
            self.assertEqual(r['reviewed_measurement_fingerprint'],'')
            for k in pairing.TG_FIELDS:self.assertEqual(r.get(k,''),'')

    def test_paa_zno_conflict_does_not_assign_peak_or_loi(self):
        rr=self.source('02948-2')
        r=next(r for r in rr if 'generic'in r['sample_state'])
        self.assertEqual(r['LOI_pct'],'')
        self.assertEqual(r['Tmax1_C'],'')
        self.assertEqual(float(r['source_Tmax_conflicting_prose_first_C']),336)
        self.assertEqual(float(r['source_Tmax_conflicting_prose_second_C']),348)
        self.assertEqual(float(r['R600_pct']),23.36)
        self.assertEqual(r['reviewed_measurement_fingerprint'],'')
        exact=[r for r in rr if r['pairing_status']=='verified_exact']
        self.assertEqual({float(r['LOI_pct'])for r in exact},{18.5,18.3,23.1})
        self.assertEqual({float(r['Tmax1_C'])for r in exact if r['Tmax1_C']},{360,366})
        r=next(r for r in exact if r['sample_state']=='PAA/BF-ATP')
        self.assertEqual((float(r['R600_pct']),float(r['residue_temp_C'])),(22.96,600))

    def test_changed_measurement_or_washing_requires_new_review(self):
        r=next(r for r in self.rows if r['pairing_status']=='verified_exact')
        for field,value in [('LOI_pct',1),('residue_temp_C',800),('heating_rate_C_min',99),('washing_state','after30LCs')]:
            changed=dict(r,**{field:value})
            self.assertNotEqual(pairing.measurement_fingerprint(changed),r['reviewed_measurement_fingerprint'])
            self.assertTrue(pairing.evidence_issues(changed))

if __name__=='__main__':unittest.main()
