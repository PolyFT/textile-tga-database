import copy
import csv
import hashlib
import json
import unittest
from pathlib import Path
from scripts import pairing, reader_table

ROOT=Path(__file__).resolve().parents[1]

class PPSourceGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT/'data/incoming/verified_source_batch_20261007_b714_PP_material.csv').open(newline='') as f:
            cls.rows=list(csv.DictReader(f))
        cls.manifest=json.loads((ROOT/'data/curation/archive/20261007/source_review_manifest_b714.json').read_text())

    def test_selected_states_and_positive_sources(self):
        self.assertEqual(len(self.rows),8)
        self.assertEqual(len({pairing.sample_state_id(r) for r in self.rows}),8)
        self.assertEqual({r['DOI'] for r in self.rows},{'10.1002/app.34993','10.1002/app.36227'})
        self.assertEqual((self.manifest['selected_new_states'],self.manifest['selected_new_TG'],self.manifest['new_sources']),(18,21,5))

    def test_approximate_LOI_qualifier_is_visible(self):
        rr=[r for r in self.rows if r['source_LOI_qualifier']=='about']
        self.assertEqual([r['LOI_pct'] for r in rr],['21','21.5'])
        for r in rr:
            display=reader_table.reading_row(r,{'scope_class':r['material_scope_class']})
            self.assertIn('about',display[20]+' '+display[21])

    def test_original_R420_exact_coordinate_binding(self):
        coords=[dict(DOI=r['DOI'],sample_state=r['sample_state'],field='R420_pct',value=r['R420_pct']) for r in self.rows if r['R420_pct']]
        self.assertEqual([r['value'] for r in coords],['19','29','30','24'])
        encoded=lambda x:hashlib.sha256(json.dumps(x,ensure_ascii=True,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        self.assertEqual(coords,self.manifest['additional_original_R420_coordinates'])
        self.assertEqual(encoded(coords),self.manifest['original_R420_coordinate_sha256'])
        mutated=copy.deepcopy(coords);mutated[0]['value']='20'
        self.assertNotEqual(encoded(mutated),self.manifest['original_R420_coordinate_sha256'])

    def test_R420_is_not_claimed_to_be_helper_bound(self):
        self.assertNotIn('R420_pct',pairing.TG_FIELDS)
        r=next(r for r in self.rows if r['R420_pct']);mutated=copy.deepcopy(r);mutated['R420_pct']='99'
        self.assertEqual(pairing.measurement_fingerprint(r),pairing.measurement_fingerprint(mutated))
        self.assertIn('420℃: '+r['R420_pct']+'%',reader_table.reading_row(r,{'scope_class':r['material_scope_class']})[10])

    def test_R600_alias_and_source_undefined_peak(self):
        for r in self.rows:
            self.assertEqual((r['residue_pct'],r['residue_temp_C']),(r['R600_pct'],'600'))
            if r['DOI']=='10.1002/app.36227':self.assertFalse(r['Tmax1_C'])
        r=copy.deepcopy(self.rows[0]);r['residue_temp_C']='800'
        self.assertTrue(pairing.evidence_issues(r))

    def test_CNCA_identity_and_nominal_ratio_limits_visible(self):
        r=self.rows[0];self.assertIn('12.0g0.2mol',r['source_reagent_naming_discrepancy'])
        self.assertIn('12.0g0.2mol',reader_table.reading_row(r,{'scope_class':r['material_scope_class']})[20])
        self.assertIn('do not normalize',r['composition'])
        r=copy.deepcopy(r);r['composition']='normalized100% assumed pure reagent'
        self.assertTrue(pairing.evidence_issues(r))

    def test_held_and_calculated_views_not_promoted(self):
        self.assertEqual(self.manifest['excluded_PP_role_views'],dict(wholehold=6,LOI_only=11,TG_only=3,calculated=2))
        q=[r for r in self.manifest['processed_source_queue_facts'] if r['DOI']=='10.1002/app.38740']
        self.assertEqual(len(q),1)
        self.assertEqual((q[0]['verified_new_states'],q[0]['verified_new_TG']),(0,0))
        self.assertIn('31.4',q[0]['note']);self.assertIn('34',q[0]['note'])

if __name__=='__main__':unittest.main()
