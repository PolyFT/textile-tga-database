"""Protect reported LOI/DTG/residue identity and initial fiber-containing state."""
import csv
import unittest
from pathlib import Path

def load_rows():
    repo=Path(__file__).resolve().parents[1]
    path=repo/'data/incoming/verified_source_batch_20261005_b254_local_textile.csv'
    if not path.exists():path=Path(__file__).resolve().parent/'staged-local-textile-b254/publication_proposed.csv'
    with path.open(newline='')as f:return list(csv.DictReader(f))

class AramidFoamSourceEvidence(unittest.TestCase):
    def test_actual_LOI_not_relative_increase(self):
        rows=[r for r in load_rows()if r['direct_numeric_use']=='yes']
        self.assertEqual(len(rows),4)
        self.assertEqual({r['LOI_pct']for r in rows},{'22.5','23.0','25.8','24.3'})
        for r in rows:
            self.assertNotEqual(r['LOI_pct'],r['source_LOI_relative_increase_pct'])
            self.assertFalse(r.get('LOI_replicates'))
            self.assertIn('Methods n10 versus',r['source_LOI_replicate_qualification'])
    def test_TG_residue_not_muffle_and_early_loss_not_single_stage(self):
        for r in load_rows():
            if r['direct_numeric_use']!='yes':continue
            self.assertEqual(r['residue_temp_C'],'800')
            self.assertEqual(r['residue_pct'],r['R800_pct'])
            self.assertNotEqual(r['R800_pct'],r['source_muffle_350C_10min_air_residual_char_pct'])
            self.assertFalse(r.get('source_TG_mass_loss_25_250_C_pct'))
            for k in ['T5_C','T10_C','Tonset_C','R600_pct','R700_pct']:self.assertFalse(r.get(k))
        t=next(r for r in load_rows()if r['source_sample_label']=='T–RPUF')
        self.assertEqual(t['Tmax2_C'],'549.66')
        self.assertNotEqual(t['Tmax2_C'],'630')
        self.assertIn('100.01percent',t['source_metric_limits'])
    def test_fiber_network_initial_state_and_unreported_loading(self):
        rows=load_rows();paired=[r for r in rows if r['direct_numeric_use']=='yes']
        self.assertEqual(len({r['sample_state']for r in paired}),4)
        for r in paired:
            self.assertEqual(r['material_form_TGA'],r['material_form_LOI'])
            self.assertIn('fiber network',r['material_form_TGA'])
            self.assertEqual(r['washing_state'],'initial_unlaundered')
            self.assertIn('finalfiberwtfractionandMDImassunreported',r['composition'])
        t=next(r for r in paired if r['source_sample_label']=='T–RPUF')
        self.assertFalse(t['source_ANF_bath_wt_percent'])
        outside=[r for r in rows if r['source_sample_label']=='RPUF']
        self.assertEqual(len(outside),1)
        self.assertEqual(outside[0]['direct_numeric_use'],'no')
        self.assertIn('outside_textile',outside[0]['pairing_status'])

if __name__=='__main__':unittest.main()
