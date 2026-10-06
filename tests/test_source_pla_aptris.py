"""Protect nonwoven identity and the reported versus calculated residue boundary."""
import csv,json,unittest
from pathlib import Path
import pandas as pd
from scripts.pairing import measurement_fingerprint
from scripts.validate_tg_loi import build_tables

ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/'data/incoming/verified_source_batch_20261001_b68_pla_aptris.csv'

class PLAAPTris(unittest.TestCase):
    def test_only_exact_own_loi_and_complete_nitrogen_conditions_enter_master(self):
        with FILE.open(newline='') as f:
            rows=list(csv.DictReader(f))
        master,_,_,report=build_tables(pd.DataFrame(rows))
        self.assertEqual(report['verified_exact_sample_states'],2)
        self.assertEqual(report['verified_exact_condition_records'],2)
        self.assertEqual(set(zip(master['sample_state'],master['LOI_pct'].astype(float))),{('PLA',18.3),('PLA/25%APTris',30.0)})
        self.assertEqual(set(master['atmosphere']),{'N2'})
        self.assertEqual(set(master['material_form']),{'PLA nonwoven fabric'})
        for r in rows:
            if r['atmosphere']=='air':
                self.assertEqual(r['heating_rate_C_min'],'')
                self.assertEqual(r['TG_sample_mass_mg'],'')
                self.assertEqual(r['TGA_instrument'],'')
                self.assertNotEqual(r['pairing_status'],'verified_exact')
            if r['sample_state'] not in {'PLA','PLA/25%APTris'}:
                self.assertEqual(r['LOI_pct'],'')

    def test_experimental_residues_survive_and_altered_calculated_values_stale_review(self):
        with FILE.open(newline='') as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),10)
        exact=[r for r in rows if r['pairing_status']=='verified_exact']
        self.assertEqual([(r['T10_C'],r['T50_C'],r['Tmax1_C'],r['R800_pct']) for r in exact],[('366.5','389.2','393.8','1.7'),('289.8','387.3','391.6','12.3')])
        for r in exact:
            self.assertEqual(r['residue_temp_C'],'800')
            self.assertEqual(r['reviewed_measurement_fingerprint'],measurement_fingerprint(r))
        altered=dict(exact[1],R800_pct='8.7')
        self.assertNotEqual(altered['reviewed_measurement_fingerprint'],measurement_fingerprint(altered))
        master,_,_,_=build_tables(pd.DataFrame([altered]))
        self.assertTrue(master.empty)
        holds=json.loads((ROOT/'data/curation/archive/source_review_holds_20261001_b68.json').read_text())
        self.assertTrue(any(h['DOI']=='10.3390/ma12193095' and 'thermallybonded' in h['disposition'] for h in holds))
