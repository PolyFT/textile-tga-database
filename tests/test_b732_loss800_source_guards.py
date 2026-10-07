"""Finite source-specific guards for reported PET mass loss, not residue."""
import copy
import csv
import json
import unittest
from pathlib import Path
from scripts import pairing, reader_table, textile_scope

ROOT = Path(__file__).resolve().parents[1]

class Loss800SourceGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT/'data/incoming/verified_source_batch_20261007_b732_loss800_material.csv').open(newline='') as f:
            cls.rows = list(csv.DictReader(f))
        cls.manifest = json.loads((ROOT/'data/curation/archive/20261007/source_review_manifest_b732.json').read_text())

    def test_original_table_values_and_physical_state_count(self):
        loi = ['24.0','26.5','29.5','30.5','31.0','36.0','32.5','33.0','29.0','29.5','23.5','30.5','25.5']
        loss = ['90.7','88.7','88.3','89.5','92.0','84.7','89.5','85.3','84.5','78.5','75.8','85.7','80.1']
        self.assertEqual([(r['Sample'],r['LOI'],r['source_weight_loss_800_pct']) for r in self.rows],
                         [('PT'+str(i),l,w) for i,(l,w) in enumerate(zip(loi,loss),1)])
        self.assertEqual(len({pairing.sample_state_id(r) for r in self.rows}),13)

    def test_mass_loss_never_becomes_reported_residue(self):
        for r in self.rows:
            self.assertFalse(r['R800_pct'])
            self.assertFalse(r.get('residue_pct',''))
            mutated = copy.deepcopy(r)
            mutated['R800_pct'] = str(100-float(r['source_weight_loss_800_pct']))
            self.assertTrue(pairing.evidence_issues(mutated))
            shown = reader_table.reading_row(r,{'scope_class':r['material_scope_class']})
            self.assertIn('原文800℃失重（%）='+r['source_weight_loss_800_pct'],shown[20])
            self.assertEqual(shown[10],'')

    def test_ambiguous_decomposition_temperatures_stay_raw(self):
        for r in self.rows:
            for field in ['T1_C','T5_C','T10_C','T50_C','Tonset_C','Tmax1_C','Tmax2_C']:
                self.assertFalse(r[field])
            changed = copy.deepcopy(r)
            changed['Tmax1_C'] = r['source_Tmax_ambiguous_C']
            self.assertTrue(pairing.evidence_issues(changed))

    def test_matched_mother_material_and_unknown_conditions(self):
        for r in self.rows:
            self.assertEqual(r['material_form_TGA'],r['material_form_LOI'])
            self.assertEqual((r['atmosphere'],r['heating_rate_C_min']),('N2','10'))
            self.assertFalse(r['source_TG_mass_mg'])
            self.assertFalse(r['source_TG_flow_mL_min'])
            changed = copy.deepcopy(r);changed['heating_rate_C_min']='20'
            self.assertTrue(pairing.evidence_issues(changed))

    def test_recipe_and_locator_cannot_inherit_review(self):
        r = copy.deepcopy(self.rows[0]);r['composition']='PET100wt%'
        self.assertTrue(pairing.evidence_issues(r))
        r = copy.deepcopy(self.rows[0]);r['TG_locator']='TableIII invented different page'
        registry={'entries':self.manifest['scope_entries']}
        with self.assertRaises(ValueError):textile_scope.classify([r]+self.rows[1:],registry)

    def test_source_identity_limits_and_negative_roles_preserved(self):
        self.assertTrue(all('Ref33' in r['source_limitations'] for r in self.rows))
        self.assertNotIn('PT',{r['Sample'] for r in self.rows})
        facts=self.manifest['processed_source_queue_facts']
        self.assertEqual(len(facts),6)
        self.assertEqual(sum(f['wholehold_states'] for f in facts),8)
        self.assertEqual(sum(f['TG_only_conditions'] for f in facts),39)
        self.assertFalse(self.manifest['publication_approved'])
        self.assertEqual(self.manifest['published'],0)

if __name__=='__main__':unittest.main()
