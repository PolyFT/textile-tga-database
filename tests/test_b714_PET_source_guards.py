import copy
import csv
import json
import unittest
from pathlib import Path
from scripts import pairing, textile_scope

ROOT=Path(__file__).resolve().parents[1]

class PETSourceGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT/'data/incoming/verified_source_batch_20261007_b714_PET_material.csv').open(newline='') as f:
            cls.rows=list(csv.DictReader(f))
        cls.manifest=json.loads((ROOT/'data/curation/archive/20261007/source_review_manifest_b714.json').read_text())

    def test_conditions_not_independent_samples(self):
        self.assertEqual(len(self.rows),13)
        self.assertEqual(len({pairing.sample_state_id(r) for r in self.rows}),10)
        rr=[r for r in self.rows if r['DOI']=='10.1002/pat.4815']
        self.assertEqual(len(rr),6)
        self.assertEqual({r['atmosphere'] for r in rr},{'N2','air'})
        self.assertEqual(len({pairing.sample_state_id(r) for r in rr}),3)

    def test_ordinary_TG_does_not_borrow_TGFTIR(self):
        self.assertTrue(all(r['heating_rate_C_min']=='10' for r in self.rows))
        self.assertTrue(all(r['material_form_TGA']==r['material_form_LOI'] for r in self.rows))
        for r in self.rows:
            changed=copy.deepcopy(r);changed['heating_rate_C_min']='20'
            self.assertTrue(pairing.evidence_issues(changed))

    def test_source_residue_coordinates(self):
        for r in self.rows:
            t='600' if r['DOI']=='10.1002/pat.4815' else '800'
            self.assertEqual(r['residue_temp_C'],t)
            self.assertEqual(r['residue_pct'],r['R'+t+'_pct'])
            changed=copy.deepcopy(r);changed['residue_temp_C']='900'
            self.assertTrue(pairing.evidence_issues(changed))

    def test_source_T5_not_invented_Tonset(self):
        for r in self.rows:
            self.assertFalse(r['Tonset_C'])
            self.assertTrue(r['T5_C'])
            changed=copy.deepcopy(r);changed['Tonset_C']=r['T5_C']
            self.assertTrue(pairing.evidence_issues(changed))

    def test_same_recipe_review_binding(self):
        r=copy.deepcopy(self.rows[0]);r['composition']='PET/PDPSI=95/5wt%'
        self.assertTrue(pairing.evidence_issues(r))
        r=copy.deepcopy(self.rows[0]);r['TG_locator']='Table7 fabricated locator'
        registry=json.loads((ROOT/'data/curation/textile_scope_registry.json').read_text())
        registry['entries']=self.manifest['scope_entries']
        mutated=[r]+copy.deepcopy(self.rows[1:])
        with self.assertRaises(ValueError):textile_scope.classify(mutated,registry)

    def test_noH_and_denominator_source_limits(self):
        rr=[r for r in self.rows if r['DOI']=='10.1002/pat.5674']
        self.assertEqual(len(rr),4)
        self.assertEqual(sum(r['sample_name']=='PET/PZS600_noH' for r in rr),1)
        for r in rr:
            self.assertIn('0.95/0.05',r['source_recipe_limits'])
            self.assertIn('not silently normalized',r['source_recipe_limits'])

    def test_pure_controls_and_raw_peak_residue_not_imported(self):
        self.assertTrue(all(r['sample_name']!='PET' for r in self.rows))
        self.assertEqual((self.manifest['held_control_states'],self.manifest['held_control_TG']),(3,4))
        self.assertTrue(all(not r.get('residue_at_Tmax_pct','') for r in self.rows))
        self.assertEqual((self.manifest['old_scope_admissions'],self.manifest['old_evidence_upgrades']),(0,0))

    def test_source_snapshot_not_publication_claim(self):
        self.assertFalse(self.manifest['publication_approved'])
        self.assertEqual(self.manifest['published'],0)
        self.assertTrue(all(r['direct_numeric_use']=='yes' and r['schema_approved']=='1' for r in self.rows))

if __name__=='__main__':unittest.main()
