"""Test original threshold definitions, old review transition, and treatment/form matching."""
import csv,hashlib,importlib.util,json,sys,unittest
from pathlib import Path
import pandas as pd
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));import pairing as p;import validate_tg_loi as v
def read(f):
    with f.open(newline='') as h:return list(csv.DictReader(h))
ROWS=read(R/'data/incoming/verified_source_batch_20261006_b321_local_material.csv')
WOOL=[r for r in read(R/'data/incoming/verified_source_batch_20261001_b74_local_cotton_wool.csv') if r['DOI']=='10.1016/j.polymdegradstab.2020.109101']
class ScientificBoundaries(unittest.TestCase):
    def test_five_new_states_with_exact_20kGy_not_10kGy(self):
        master,_,_,report=v.build_tables(pd.DataFrame(ROWS))
        self.assertFalse(report['errors']);self.assertEqual((len(master),report['verified_exact_sample_states']),(5,5))
        gamma=[r for r in ROWS if r['irradiation_dose_kGy']=='20'];self.assertEqual(len(gamma),1)
        self.assertEqual((gamma[0]['LOI_pct'],gamma[0]['T25_C'],gamma[0]['R600_pct']),('26','286','10.34'))
        self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(dict(gamma[0],sample_state='WF/WPP/NC/Hisil_10kGy')))
    def test_thresholds_review_bound_and_range_checked(self):
        for r in ROWS:
            self.assertFalse(r['T5_C']);self.assertFalse(r['T10_C']);self.assertFalse(r['Tonset_C']);self.assertFalse(r['Tmax1_C'])
            for key in ['T25_C','T75_C']:
                self.assertIn(key,p.TG_FIELDS)
                self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(dict(r,**{key:str(float(r[key])+1)})))
                self.assertTrue(any(key in x for x in v.numeric_errors(pd.DataFrame([dict(r,**{key:'1600'})]))))
    def test_own_LOI_not_linear_burning_replicates_or_geometry(self):
        for r in ROWS:
            self.assertEqual(r['LOI_standard'],'ISO4589-1984');self.assertFalse(r['LOI_specimen_geometry']);self.assertFalse(r['LOI_replicates'])
            self.assertFalse(r['TGA_mass_mg']);self.assertFalse(r['TGA_gas_flow_ml_min']);self.assertFalse(r['TGA_replicates'])
            self.assertEqual((r['TG_start_C'],r['TG_end_C'],r['atmosphere'],r['heating_rate_C_min']),('20','600','N2','10'))
            self.assertEqual(r['residue_temp_C'],'600');self.assertEqual(r['residue_pct'],r['R600_pct'])
    def test_recipe_phr_base_and_bulk_not_fabric(self):
        for r in ROWS:
            self.assertIn('MA2phr',r['composition']);self.assertIn('phrdenominatorWF/WPPbase,notWPPalone',r['composition'])
            self.assertIn('specimen_form_mismatch',p.evidence_issues(dict(r,material_form_LOI='woven PP fabric')))
        ath=next(r for r in ROWS if r['sample_state']=='WF/WPP/NC/ATH_unirradiated')
        self.assertEqual((ath['T25_C'],ath['T50_C'],ath['T75_C']),('282','331','335'))
    def test_wool_wash_and_gas_states_with_two_isothermal_holds(self):
        paired=[r for r in WOOL if r['pairing_status']=='verified_exact']
        self.assertEqual((len(paired),len({p.sample_state_id(r) for r in paired})),(6,3))
        for r in paired:
            self.assertFalse(p.evidence_issues(r))
            self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(dict(r,T75_C=str(float(r['T75_C'])+1))))
        held=[r for r in WOOL if 'Isothermal' in r['sample_state']]
        self.assertEqual(len(held),2)
        for r in held:
            self.assertEqual(r['pairing_status'],'TG_only_no_exact_same_state_LOI');self.assertFalse(r['LOI_pct']);self.assertTrue(p.evidence_issues(r))
        washed=[r for r in paired if 'after30wash' in r['sample_state']]
        self.assertEqual({r['LOI_pct'] for r in washed},{'29.6'})
        self.assertEqual({r['atmosphere']:r['T75_C'] for r in washed},{'nitrogen':'716','air':'566'})
    def test_B319_T30_review_bindings_remain_compatible(self):
        self.assertIn('T30_C',p.TG_FIELDS)
        for r in read(R/'data/incoming/verified_source_batch_20261006_b319_local_material.csv'):
            self.assertEqual(p.measurement_fingerprint(r),r['reviewed_measurement_fingerprint'])
            if r['pairing_status']=='verified_exact':self.assertFalse(p.evidence_issues(r))
if __name__=='__main__':unittest.main()
