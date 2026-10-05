"""Negative checks for missing states, residual temperatures and DSC/TG boundaries."""
import csv,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));import pairing
DOIS={'b307':'10.1016/j.compositesb.2015.03.061','b308':'10.1007/s12221-014-2495-7'}
def rows(batch):
    with(ROOT/'data/incoming/verified_source_batch_20261005_b307_b308_local_textile.csv').open(newline='')as f:return [r for r in csv.DictReader(f)if r['DOI']==DOIS[batch]]
class CottonSourceBoundaries(unittest.TestCase):
    def test_MMT2and4_have_LOI_but_no_borrowed_TG(self):
        data=rows('b307');held=[r for r in data if r['pairing_status']!='verified_exact']
        self.assertEqual(len(held),2)
        for r in held:
            self.assertTrue(r['LOI_pct'])
            for key in ['T5_C','Tmax1_C','residue_pct','residue_temp_C']:self.assertFalse(r[key])
            self.assertFalse(r.get('reviewed_measurement_fingerprint'))
            self.assertTrue(pairing.evidence_issues(r))
        for r in data:
            if r['pairing_status']=='verified_exact':
                self.assertEqual(r['residue_temp_C'],'590')
                self.assertFalse(r['R600_pct'])
                self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,residue_temp_C='600')))
    def test_air_TG_does_not_use_DSC_N2_peaks_mass_or_flow(self):
        data=rows('b308');self.assertEqual(len(data),10)
        for r in data:
            self.assertEqual(r['atmosphere'],'air')
            self.assertEqual(r['source_TGA_atmosphere'],'static air atmosphere')
            for key in ['TGA_gas_flow_ml_min','TGA_mass_mg','TGA_pan','TGA_replicates']:self.assertFalse(r[key])
            self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,atmosphere='nitrogen')))
            self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,T10_C='',Tonset_C=r['T10_C'])))
        control=next(r for r in data if r['source_sample_label']=='CF')
        self.assertEqual((control['Tmax1_C'],control['Tmax2_C']),('330','470'))
        self.assertEqual(control['source_raw_unbound_control_residue_pct'],'0.3')
        self.assertFalse(control['residue_pct']);self.assertFalse(control['residue_temp_C'])
        self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(control,Tmax1_C='361')))
    def test_initial_cloth_identity_is_bound_for_both_sources(self):
        for batch,number in [('b307',5),('b308',10)]:
            data=[r for r in rows(batch)if r['pairing_status']=='verified_exact']
            self.assertEqual(len({pairing.sample_state_id(r)for r in data}),number)
            for r in data:
                self.assertFalse(pairing.evidence_issues(r))
                self.assertEqual(r['material_form_TGA'],r['material_form_LOI'])
                self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='isolated cotton fibers')))
                self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,washing_state='washed_20cycles')))
if __name__=='__main__':unittest.main()
