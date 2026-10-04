"""Keep conflicting control, additive powder and extra ramp conditions out of pairs."""
import csv
import unittest
from pathlib import Path

def load_rows():
    repo=Path(__file__).resolve().parents[1]
    path=repo/'data/incoming/verified_source_batch_20261005_b259_local_textile.csv'
    if not path.exists():path=Path(__file__).resolve().parent/'staged-local-textile-b259/publication_proposed.csv'
    with path.open(newline='')as f:return list(csv.DictReader(f))

class GlassPBTSourceEvidence(unittest.TestCase):
    def test_conflicting_LOI_control_not_counted(self):
        r=next(x for x in load_rows()if x['source_sample_label']=='GF30-PBT')
        self.assertEqual((r['LOI_pct'],r['source_LOI_alternate_prose_pct']),('20.0','22.0'))
        self.assertEqual(r['direct_numeric_use'],'no')
        self.assertIn('conflicting_source_LOI',r['pairing_status'])
        self.assertEqual(len([x for x in load_rows()if x['direct_numeric_use']=='yes']),4)
    def test_threshold_and_R700_not_onset_or_programme(self):
        for r in load_rows():
            if r['direct_numeric_use']!='yes':continue
            self.assertTrue(r['T5_C'])
            self.assertTrue(r['Tmax1_C'])
            self.assertFalse(r.get('Tonset_C'))
            self.assertFalse(r.get('T10_C'))
            self.assertEqual(r['residue_temp_C'],'700')
            self.assertEqual(r['R700_pct'],r['residue_pct'])
            self.assertFalse(r.get('R800_pct'))
            self.assertFalse(r.get('TG_end_C'))
    def test_powder_not_composite_and_one_ramp_per_state(self):
        rows=load_rows();powder=next(r for r in rows if r['source_sample_label']=='AP')
        self.assertEqual(powder['direct_numeric_use'],'no')
        self.assertFalse(powder['LOI_pct'])
        self.assertFalse(powder['material_form_LOI'])
        self.assertEqual(powder['R700_pct'],'74.4')
        paired=[r for r in rows if r['direct_numeric_use']=='yes']
        self.assertEqual(len({r['sample_state']for r in paired}),4)
        for r in paired:
            self.assertEqual((r['heating_rate_C_min'],r['atmosphere'],r['TGA_gas_flow_ml_min']),('10','nitrogen','60'))
            self.assertEqual(r['material_form_TGA'],r['material_form_LOI'])
            self.assertIn('matrixfractionnotexplicitlyreported,notcalculated',r['composition'])

if __name__=='__main__':unittest.main()
