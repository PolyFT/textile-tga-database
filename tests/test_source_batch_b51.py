"""Protect source-native fields, conditioning and explicit-text pairing in b51."""
import csv,hashlib,json,unittest
from pathlib import Path
import pandas as pd
from scripts.pairing import measurement_fingerprint,evidence_issues
from scripts.validate_tg_loi import build_tables,numeric_errors
R=Path(__file__).resolve().parents[1];M=R/'data/curation/archive/source_review_manifest_20260930_b51.json'
def files():return json.loads(M.read_text())['files']
def rows():
    result=[]
    for entry in files():
        with (R/entry['file']).open(newline='') as f:result.extend(csv.DictReader(f))
    return result
class Batch51(unittest.TestCase):
    def test_counts_and_bound_reviews(self):
        data=rows();self.assertEqual(len(data),3)
        for r in data:self.assertFalse(evidence_issues(r));self.assertEqual(measurement_fingerprint(r),r['reviewed_measurement_fingerprint'])
        self.assertIn('measurement_review_pending_or_stale',evidence_issues(dict(data[0],LOI_pct='100')))
        master,_,_,report=build_tables(pd.DataFrame(data));self.assertEqual(len(master),3);self.assertEqual(report['verified_exact_sample_states'],3);self.assertFalse(numeric_errors(pd.DataFrame(data)))
    def test_input_hashes(self):
        for e in files():self.assertEqual(hashlib.sha256((R/e['file']).read_bytes()).hexdigest(),e['published_input_sha256'])
    def test_po_radical_same_state_values(self):
        d={r['sample_state']:r for r in rows() if '112025' in r['DOI']};self.assertEqual(set(d),{'TD','TD220'})
        self.assertEqual({(s,r['LOI_pct'],r['T5_C'],r['Tmax1_C'],r['R700_pct'],r['residue_at_Tmax1_pct']) for s,r in d.items()},{('TD','29.2','252','308','38.2','70.1'),('TD220','26.6','278','314','36.6','69.4')})
        self.assertTrue(all(r['atmosphere']=='N2' and r['heating_rate_C_min']=='20' and r['gas_flow_mL_min']=='90' and r['TG_end_C']=='800' and not r['R800_pct'] for r in d.values()))
    def test_po_radical_conditioning_not_specimen_pretreatment(self):
        d={r['sample_state']:r for r in rows() if '112025' in r['DOI']}
        self.assertTrue(all('100 C hold for 5 min' in r['TG_preconditioning'] for r in d.values()))
        self.assertNotIn('additional cure 220 C',d['TD']['treatment_method']);self.assertIn('additional cure 220 C for 5 min',d['TD220']['treatment_method'])
        self.assertEqual(d['TD']['source_add_on_reported_pct'],'19.2');self.assertEqual(d['TD220']['source_add_on_reported_pct'],'12.6');self.assertTrue(all(not r.get('add_on_pct') for r in d.values()))
    def test_lyocell_explicit_prose_and_tg_ir_separation(self):
        r=next(r for r in rows() if '2145405' in r['DOI'])
        self.assertEqual((r['T5_C'],r['Tmax1_C'],r['R800_pct'],r['LOI_pct']),('71','266','12.51','54'))
        self.assertEqual((r['atmosphere'],r['heating_rate_C_min'],r['tga_start_temperature_C'],r['TG_end_C']),('air','10','30','800'))
        self.assertFalse(r['gas_flow_mL_min']);self.assertFalse(r['TGA_sample_mass_reported']);self.assertEqual(r['numeric_evidence_type'],'explicit_text');self.assertIn('no_durability_washes',r['washing_state'])
    def test_held_sources_not_admitted(self):
        accepted={r['DOI'] for r in rows()};self.assertEqual(accepted,{'10.1016/j.polymdegradstab.2026.112025','10.1080/15440478.2022.2145405'})
        h=json.loads((R/'data/curation/archive/source_review_holds_20260930_b51.json').read_text());held={r['DOI'] for r in h}
        self.assertTrue({'10.1016/j.eurpolymj.2024.112804','10.1016/j.porgcoat.2022.107018','10.1016/j.mtla.2026.102691'} <= held)
    def test_shared_td_tg_group_has_one_canonical_admission(self):
        td=next(r for r in rows() if r['sample_state']=='TD')
        self.assertEqual(td['related_source_doi'],'10.1016/j.cej.2025.165778')
        self.assertEqual(td['shared_experiment_group'],'TD_nitrogen_TG_CEJ165778_PDS112025')
        self.assertIn('LOI experimental independence is not established',td['cross_paper_reuse_note'])
        # Guard the explicit cross-paper scientific signature even if a future
        # author label differs; unreviewed provenance-only rows are permitted.
        for path in (R/'data/incoming').glob('*.csv'):
            if '10.1016/j.cej.2025.165778' not in path.read_text():continue
            with path.open(newline='') as f:
                for row in csv.DictReader(f):
                    if row.get('DOI','').lower()!='10.1016/j.cej.2025.165778' or row.get('pairing_status')!='verified_exact':continue
                    signature=tuple(float(row.get(k) or -1) for k in ['T5_C','Tmax1_C','R700_pct'])
                    self.assertNotEqual(signature,(252.0,308.0,38.2),'CEJ TD duplicates canonical PO TD TG state')
