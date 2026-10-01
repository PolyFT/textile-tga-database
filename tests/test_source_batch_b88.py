"""Guard assay-specific fiber preparation, thermal stages and legacy completion counts."""
import csv,hashlib,json,unittest
from pathlib import Path
from scripts.pairing import evidence_issues,measurement_fingerprint,pair_key,sample_state_id
ROOT=Path(__file__).resolve().parents[1]
def rows(tag):
    with (ROOT/f'data/incoming/verified_source_batch_20261001_b88_{tag}.csv').open(newline='') as f:return list(csv.DictReader(f))
class SourceBatchB88Tests(unittest.TestCase):
    def test_review_bound_inputs_count_seven_states_without_upgrading_old_pairs(self):
        m=json.loads((ROOT/'data/curation/source_review_manifest_20261001_b88.json').read_text());all_rows=[]
        for source in m['files']:
            p=ROOT/source['file'];self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),source['published_input_sha256'])
            with p.open(newline='') as f:data=list(csv.DictReader(f))
            for r in data:self.assertEqual(r['reviewed_measurement_fingerprint'],measurement_fingerprint(r));self.assertFalse(evidence_issues(r))
            all_rows+=data
        self.assertEqual(len(all_rows),7);self.assertEqual(len({sample_state_id(r) for r in all_rows}),7);self.assertEqual(len({pair_key(r) for r in all_rows}),7)
        self.assertEqual(m['summary']['new_source_measurement_states'],5);self.assertEqual(m['summary']['newly_completed_pairs'],2)
        self.assertEqual(m['summary']['existing_paired_states_evidence_upgraded'],0)
        source=next(x for x in m['files'] if x['DOI']=='10.1177/1528083703034627')
        self.assertEqual(source['classification'],'newly_completed_legacy_TG_only_pairs');self.assertEqual(source['legacy_TG_records'],['CTG0060','CTG0068'])
    def test_pe_explicit_residue_temperature_survives_endpoint_conflict(self):
        data=rows('pe_inline2022');self.assertEqual(len(data),3)
        self.assertEqual({(float(r['LOI_pct']),float(r['T10_C']),float(r['residue_pct'])) for r in data},{(21.2,452,0.1),(21.5,447,1.9),(21.5,443,3.0)})
        for r in data:
            self.assertFalse(r.get('TG_end_C',''));self.assertEqual(float(r['residue_temp_C']),600)
            self.assertIn(r['atmosphere'],{'N2','nitrogen'});self.assertIn('800',r['limitations']);self.assertIn('600',r['limitations'])
    def test_fluorochemical_controls_keep_onset_and_exclude_undefined_peaks(self):
        data=rows('fluorochem2003');self.assertEqual(len(data),2)
        self.assertEqual({(float(r['LOI_pct']),float(r['Tonset_C'])) for r in data},{(28,414.76),(29.8,264.03)})
        for r in data:
            self.assertFalse(r.get('Tmax1_C',''));self.assertFalse(r.get('Tmax2_C',''));self.assertFalse(r.get('residue_pct',''))
            self.assertEqual(r['DOI'],'10.1177/1528083703034627');self.assertEqual(float(r['heating_rate_C_min']),20)
    def test_pa6_char_oxidation_peak_is_not_reindexed_as_initial_decomposition(self):
        data=rows('pa6wg2017');self.assertEqual(len(data),2)
        self.assertEqual({(float(r['LOI_pct']),float(r['Tmax2_C'])) for r in data},{(24.2,540.9),(27.5,549.1)})
        for r in data:
            self.assertFalse(r.get('Tmax1_C',''));self.assertFalse(r.get('residue_pct',''));self.assertEqual(r['atmosphere'],'air')
            self.assertEqual(float(r['heating_rate_C_min']),20)
        treated=next(r for r in data if float(r['LOI_pct'])==27.5)
        self.assertIn('5 g/dm³ Pretepon G',treated['washing_state']);self.assertIn('60 °C for 30 min',treated['washing_state']);self.assertIn('fiber',treated['limitations'].lower())
    def test_public_holds_omit_private_paths(self):
        text=(ROOT/'data/curation/source_review_holds_20261001_b88.json').read_text()
        for marker in ['/workspace/','/tmp/','new-textile-cache/','new-textile-prep/','/root/']:self.assertNotIn(marker,text)
if __name__=='__main__':unittest.main()
