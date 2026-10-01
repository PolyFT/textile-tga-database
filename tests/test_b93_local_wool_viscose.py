"""Protect native metric identity, missing endpoints and held sample crosswalks."""
import csv
import sys
import unittest
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import pairing
import validate_tg_loi as v
class WoolViscoseEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with(ROOT/'data/incoming/verified_source_batch_20261001_b93_local_wool_viscose.csv').open(newline='')as f:cls.rows=list(csv.DictReader(f))
    def source(self,suffix):return [r for r in self.rows if r['DOI'].endswith(suffix)]
    def test_counts_exclude_held_facts(self):
        rep=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3]
        self.assertEqual(rep['errors'],[])
        self.assertEqual((len(self.rows),rep['verified_exact_sample_states'],rep['verified_exact_condition_records']),(38,11,11))
        self.assertEqual(sum(r['pairing_status']!='verified_exact'for r in self.rows),27)
    def test_wool_static_air_dta_and_unknown_char_endpoint(self):
        rr=self.source('02839-0');self.assertEqual(len(rr),8)
        self.assertEqual([float(r['LOI_pct'])for r in rr],[24,27,28,27.5,31,33.5,32.5,31])
        self.assertEqual([float(r['residue_pct'])for r in rr],[.8,2.4,3.3,4.4,8.3,9.5,5.1,6])
        for r in rr:
            self.assertEqual((r['atmosphere'],r['atmosphere_mode']),('air','static air'))
            self.assertEqual(float(r['heating_rate_C_min']),10)
            self.assertGreater(float(r['source_DTA_second_exotherm_K']),700)
            for k in ['Tmax1_C','residue_temp_C','R600_pct','TG_end_C']:self.assertEqual(r.get(k,''),'')
    def test_wool_native_identity_and_recipe_conflicts_preserved(self):
        for r in self.source('02839-0'):
            self.assertEqual(r['source_native_PII'],'S0040-6031(96)02839-0')
            self.assertEqual((r['source_cover_header_year'],r['source_other_headers_and_copyright_year']),('1995','1996'))
        r=self.source('02839-0')[2]
        self.assertEqual(r['source_native_complex_formula'],'(NH4)3Cl[Ca(H2PO4)4]')
        self.assertEqual(r['source_bath_concentration_range_mol_L'],'0.06-0.10')
    def test_viscose_dsc_not_tg_peak_and_runend_not_char_endpoint(self):
        rr=[r for r in self.source('24217')if r['pairing_status']=='verified_exact']
        self.assertEqual(len(rr),2)
        for r in rr:
            self.assertEqual((r['atmosphere'],float(r['heating_rate_C_min'])),('nitrogen',20))
            self.assertEqual(float(r['TG_end_C']),500)
            self.assertEqual(r['source_TableIII_TGA_column_labels'],'StageI/StageI;proseStageIwater/StageIIdecomposition')
            for k in ['Tmax1_C','T5_C','Tonset_C','residue_temp_C','R500_pct']:self.assertEqual(r.get(k,''),'')
        self.assertEqual([float(r['residue_pct'])for r in rr],[11.61,27.65])
    def test_viscose_loi_only_fibers_have_no_assigned_tg(self):
        rr=[r for r in self.source('24217')if r['pairing_status']!='verified_exact']
        self.assertEqual({r['sample_state']for r in rr},{'Fiber2','Fiber3','Fiber5'})
        for r in rr:
            for k in pairing.TG_FIELDS:self.assertEqual(r.get(k,''),'')
            self.assertEqual(r.get('reviewed_measurement_fingerprint',''),'')
    def test_dpamp_exact_control_and_generic_grafting_hold(self):
        rr=self.source('0970-6');aa=[r for r in rr if r['pairing_status']=='verified_exact']
        self.assertEqual(len(aa),1);r=aa[0]
        self.assertEqual((float(r['LOI_pct']),float(r['R800_pct']),float(r['residue_temp_C'])),(17.1,12.7,800))
        self.assertEqual(float(r['source_Tmax_approximate_C']),335)
        self.assertEqual(r['Tmax1_C'],'')
        for r in rr:
            if 'genericunmappedGP'in r['sample_state']:
                self.assertEqual(r['LOI_pct'],'');self.assertEqual(r.get('reviewed_measurement_fingerprint',''),'')
            if r['grafting_pct']:
                self.assertEqual(r['Tmax1_C'],'');self.assertEqual(r['residue_pct'],'')
        air=next(r for r in rr if r['sample_state'].startswith('Control')and r['atmosphere']=='air')
        self.assertEqual(air['residue_pct'],'')
    def test_coating_ramp_and_latex_form_remain_held(self):
        rr=self.source('0954-0');self.assertEqual(len(rr),17)
        for r in rr:self.assertNotEqual(r['pairing_status'],'verified_exact')
        tg=[r for r in rr if r['residue_temp_C']=='480'];self.assertEqual(len(tg),8)
        for r in tg:
            self.assertEqual(r['heating_rate_C_min'],'')
            self.assertEqual(float(r['residue_temp_C']),480)
            self.assertEqual(r.get('reviewed_measurement_fingerprint',''),'')
    def test_changed_metric_or_washing_invalidates_review(self):
        r=next(r for r in self.rows if r['pairing_status']=='verified_exact')
        for field,val in [('LOI_pct',1),('residue_temp_C',800),('heating_rate_C_min',99),('washing_state','after30LCs')]:
            changed=dict(r,**{field:val});self.assertNotEqual(pairing.measurement_fingerprint(changed),r['reviewed_measurement_fingerprint'])
            self.assertTrue(pairing.evidence_issues(changed))
if __name__=='__main__':unittest.main()
