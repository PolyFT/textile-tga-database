"""Guard canonical controls, source loading bridges and two-atmosphere pairing."""
import csv,hashlib,json,unittest
from pathlib import Path
import pandas as pd
from scripts.pairing import evidence_issues,measurement_fingerprint
from scripts.validate_tg_loi import build_tables,numeric_errors
R=Path(__file__).resolve().parents[1];M=R/'data/curation/source_review_manifest_20260930_b52.json'
def files():return json.loads(M.read_text())['files']
def rows():
    data=[]
    for entry in files():
        with (R/entry['file']).open(newline='') as f:data.extend(csv.DictReader(f))
    return data
def sample(name):return {r['atmosphere']:r for r in rows() if r['sample_state']==name}
class Batch52(unittest.TestCase):
    def test_counts_and_review_binding(self):
        d=rows();self.assertEqual(len(d),6);self.assertEqual(len({(r['DOI'],r['sample_state'],r['washing_state']) for r in d}),3)
        for r in d:self.assertFalse(evidence_issues(r));self.assertEqual(measurement_fingerprint(r),r['reviewed_measurement_fingerprint'])
        self.assertIn('measurement_review_pending_or_stale',evidence_issues(dict(d[0],LOI_pct='99')))
        m,_,_,report=build_tables(pd.DataFrame(d));self.assertEqual(len(m),6);self.assertEqual(report['verified_exact_sample_states'],3);self.assertFalse(numeric_errors(pd.DataFrame(d)))
    def test_input_hashes(self):
        for entry in files():self.assertEqual(hashlib.sha256((R/entry['file']).read_bytes()).hexdigest(),entry['published_input_sha256'])
    def test_dd_exact_values(self):
        d=sample('DD');self.assertEqual(set(d),{'N2','air'})
        self.assertEqual(tuple(d['N2'][k] for k in ['T5_C','Tmax1_C','R700_pct','LOI_pct']),('259','292','31.8','28.3'))
        self.assertEqual(tuple(d['air'][k] for k in ['T5_C','Tmax1_C','Tmax2_C','R700_pct','LOI_pct']),('240','282','522','3.6','28.3'))
        self.assertTrue(all(r['gas_flow_mL_min']=='90' and r['heating_rate_C_min']=='20' and r['TG_end_C']=='750' for r in d.values()))
    def test_canonical_cotton_and_held_nitrogen_T5(self):
        d=sample('Cotton');self.assertFalse(d['N2']['T5_C']);self.assertEqual((d['N2']['Tmax1_C'],d['N2']['R700_pct'],d['N2']['residue_at_Tmax1_pct']),('380','10.2','42.2'))
        self.assertEqual(tuple(d['air'][k] for k in ['T5_C','Tmax1_C','Tmax2_C','R700_pct']),('312','352','466','1.3'))
        self.assertTrue(all(r['LOI_pct']=='18.6' for r in d.values()));self.assertEqual(d['N2']['shared_experiment_group'],'Cotton_nitrogen_TG_CEJ165778_PDS112025');self.assertFalse(d['air']['shared_experiment_group'])
    def test_no_second_po_cotton_admission(self):
        for p in (R/'data/incoming').glob('*.csv'):
            if '10.1016/j.polymdegradstab.2026.112025' not in p.read_text():continue
            with p.open(newline='') as f:
                for r in csv.DictReader(f):
                    if r.get('DOI')!='10.1016/j.polymdegradstab.2026.112025' or r.get('pairing_status')!='verified_exact':continue
                    self.assertNotIn(r.get('sample_state','').strip().lower(),{'cotton','pristine cotton','cotton (co)'})
                    self.assertNotEqual(tuple(float(r.get(k) or -1) for k in ['Tmax1_C','R700_pct']),(380.0,10.2))
    def test_source_addon_and_calculated_residues_not_normalized(self):
        d=sample('DD');self.assertTrue(all(r['source_add_on_reported_pct']=='17.1' and not r.get('add_on_pct') for r in d.values()))
        self.assertTrue(all(not r.get('source_calculated_silica_free_residue_pct') for r in rows()))
        self.assertNotIn('TD',{r['sample_state'] for r in rows()})
    def test_dopo_prose_completion_not_plot_estimation(self):
        d=sample('CO/DOPO-ETES');self.assertEqual(len(d),2)
        self.assertEqual(tuple(d['N2'][k] for k in ['T5_C','Tmax1_C','R800_pct','LOI_pct']),('320.4','360.5','18.8','23'))
        self.assertEqual(tuple(d['air'][k] for k in ['T5_C','Tmax1_C','Tmax2_C','R800_pct','LOI_pct']),('312.1','341.3','518.7','7.8','23'))
        self.assertTrue(all(r['heating_rate_C_min']=='20' and r['gas_flow_mL_min']=='90' and r['tga_start_temperature_C']=='40' and r['TG_end_C']=='800' for r in d.values()))
    def test_preparative_rinse_and_withheld_other_loadings(self):
        d=sample('CO/DOPO-ETES');self.assertTrue(all('no_durability_washes' in r['washing_state'] and r['legacy_sample_id']=='L031-S002' for r in d.values()))
        self.assertEqual({r['legacy_TG_record_id'] for r in d.values()},{'TG0196','TG0197'})
        self.assertEqual({r['sample_state'] for r in rows()},{'DD','Cotton','CO/DOPO-ETES'})
