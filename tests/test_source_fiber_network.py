"""Protect source-specific metric and independent-sample counting boundaries."""
import csv,unittest
from pathlib import Path
import pandas as pd
from scripts.pairing import measurement_fingerprint
from scripts.validate_tg_loi import build_tables
ROOT=Path(__file__).resolve().parents[1]
# Publication replaces this placeholder with the exact immutable input filename.
FILE=ROOT/'data/incoming/verified_source_batch_20261001_b71_fiber_network.csv'
def source_rows():
    with FILE.open(newline='') as handle:
        return list(csv.DictReader(handle))
class FiberNetworkSourceReview(unittest.TestCase):
    def test_moisture_stage_is_not_decomposition_onset_or_fixed_residue(self):
        rows=[r for r in source_rows() if r['DOI']=='10.3390/polym17172377']
        self.assertEqual(len(rows),5)
        self.assertEqual([float(r['T5_C']) for r in rows],[69.83,76.83,77.5,77.83,80.17])
        self.assertTrue(all(r.get('Tonset_C','')=='' for r in rows))
        self.assertTrue(all(r.get('R600_pct','')=='' and r['residue_temp_C']=='' for r in rows))
        altered=dict(rows[0],Tonset_C=rows[0]['T5_C'],R600_pct=rows[0]['residue_pct'],residue_temp_C='600')
        self.assertNotEqual(measurement_fingerprint(altered),rows[0]['reviewed_measurement_fingerprint'])
        master,_,_,_=build_tables(pd.DataFrame([altered]))
        self.assertTrue(master.empty)
    def test_two_atmospheres_do_not_double_count_three_laminates(self):
        rows=[r for r in source_rows() if r['DOI']=='10.3390/polym12102379']
        master,_,_,report=build_tables(pd.DataFrame(rows))
        self.assertEqual(report['verified_exact_sample_states'],3)
        self.assertEqual(report['verified_exact_condition_records'],6)
        self.assertEqual(set(master['atmosphere']),{'N2','air'})
        self.assertEqual({(r['sample_state'],r['atmosphere']):float(r['R800_pct']) for r in rows},{('GFRP','N2'):84,('GFRP','air'):71,('BFRP','N2'):84,('BFRP','air'):70,('CFRP','N2'):79,('CFRP','air'):27})
        self.assertTrue(all(r.get('T5_C','')=='' and r.get('Tonset_C','')=='' for r in rows))
        altered=dict(rows[0],T5_C=rows[0]['source_T2wt_pct_C'])
        self.assertNotEqual(measurement_fingerprint(altered),rows[0]['reviewed_measurement_fingerprint'])
    def test_nomex_repeated_splines_and_non_TG_gases_are_not_new_states(self):
        rows=[r for r in source_rows() if r['DOI']=='10.1007/s42765-022-00231-x']
        self.assertEqual(len(rows),1)
        row=rows[0]
        self.assertEqual(float(row['LOI_n']),6)
        self.assertEqual(float(row['LOI_pct']),28.39)
        self.assertEqual(float(row['T5_C']),376)
        self.assertEqual(row['atmosphere'],'air')
        self.assertTrue(all(row.get(field,'')=='' for field in ['Tonset_C','Tmax1_C','residue_pct','R800_pct']))
        altered=dict(row,atmosphere='argon')
        self.assertNotEqual(measurement_fingerprint(altered),row['reviewed_measurement_fingerprint'])
        master,_,_,report=build_tables(pd.DataFrame(source_rows()))
        self.assertEqual(report['verified_exact_sample_states'],9)
        self.assertEqual(report['verified_exact_condition_records'],12)
