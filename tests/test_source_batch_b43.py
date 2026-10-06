"""Source-bound safeguards for the four-paper b43 evidence upgrade."""
import csv
import hashlib
import json
import unittest
from pathlib import Path
from scripts.pairing import measurement_fingerprint, evidence_issues
ROOT = Path(__file__).resolve().parents[1]
def rows():
    result=[]
    for path in sorted((ROOT/'data/incoming').glob('verified_source_batch_20260930_b43_*.csv')):
        with path.open(newline='',encoding='utf-8') as handle:result.extend(csv.DictReader(handle))
    return result
class SourceBatchB43Tests(unittest.TestCase):
    def test_counting_and_existing_state_classification(self):
        data=rows();self.assertEqual(len(data),14)
        self.assertEqual(len({(r['DOI'].lower(),r['sample_state'],r['washing_state']) for r in data}),12)
        self.assertEqual(len({r['DOI'].lower() for r in data}),4)
        self.assertTrue(all(r['existing_state_status']=='existing_state_evidence_upgraded' for r in data))
    def test_row_fingerprints_and_source_locators(self):
        for r in rows():
            with self.subTest(doi=r['DOI'],sample=r['sample_state'],atmosphere=r['atmosphere']):
                self.assertEqual(measurement_fingerprint(r),r['reviewed_measurement_fingerprint'])
                self.assertFalse(evidence_issues(r))
                self.assertTrue(r['TG_locator'] and r['LOI_locator'] and r['conditions_locator'])
    def test_lyocell_does_not_borrow_TGIR_conditions(self):
        data=[r for r in rows() if r['DOI'].lower()=='10.1039/d1ra06573d']
        self.assertEqual(len(data),4)
        self.assertEqual({r['washing_state'] for r in data},{'0 laundering cycles'})
        self.assertEqual({r['heating_rate_C_min'] for r in data},{'10'})
        self.assertEqual({r['TG_start_C'] for r in data},{'40'})
        self.assertEqual({r['TG_end_C'] for r in data},{'800'})
        self.assertTrue(all(not r.get('gas_flow_mL_min') and not r.get('TGA_sample_mass_mg') for r in data))
    def test_pet2016_keeps_only_unambiguous_stage_metrics(self):
        data=[r for r in rows() if r['DOI']=='10.1177/1528083716648761']
        self.assertEqual({r['sample_state'] for r in data},{'PB','PC','PE'})
        self.assertTrue(all(not r.get('Tmax1_C') and not r.get('Tmax2_C') for r in data))
        pc=next(r for r in data if r['sample_state']=='PC')
        self.assertEqual(pc['Tonset_C'],'274');self.assertFalse(pc.get('residue_pct'))
        for r in data:
            if r['sample_state']!='PC':
                self.assertEqual(r['residue_pct'],'10');self.assertEqual(r['residue_temp_C'],'750')
                self.assertFalse(r.get('Tonset_C'))
    def test_pet2018_residue_has_no_inferred_fixed_temperature(self):
        data=[r for r in rows() if r['DOI']=='10.1177/1528083718798636']
        self.assertEqual({r['sample_state'] for r in data},{'PO2','PO3','PO4','PO5'})
        self.assertEqual([r['residue_pct'] for r in sorted(data,key=lambda r:r['sample_state'])],['28.7','34.8','32.0','31.2'])
        self.assertTrue(all(not r.get('residue_temp_C') and not r.get('R750_pct') and not r.get('Tmax1_C') for r in data))
    def test_pp_experimental_residues_exclude_conflicted_control(self):
        data=[r for r in rows() if r['DOI']=='10.1177/1528083720938158']
        self.assertEqual({r['sample_state'] for r in data},{'PP-1','PP-2','PP-3'})
        self.assertEqual([r['R700_pct'] for r in sorted(data,key=lambda r:r['sample_state'])],['15.9','17.6','17.9'])
        self.assertTrue(all(r.get('LOI_uncertainty_type','').lower()!='sd' for r in data))
    def test_manifest_hashes_bind_reviewed_files(self):
        manifest=json.loads((ROOT/'data/curation/archive/source_review_manifest_20260930_b43.json').read_text())
        for item in manifest['files']:
            path=ROOT/item['file'];self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),item['published_input_sha256'])
