import csv,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class B689SourceGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT/'data/incoming/verified_source_batch_20261007_b689_PP_material.csv').open(newline='') as f:cls.rows=list(csv.DictReader(f))
        cls.manifest=json.loads((ROOT/'data/curation/archive/20261007/source_review_manifest_b689.json').read_text())
    def test_unqualified_peak_not_max_rate(self):
        for r in self.rows:self.assertFalse(any(r.get(k,'') for k in ['Tmax_C','Tmax1_C','Tmax2_C','Tonset_C']))
    def test_pure_PP_conflict_and_dashes_not_zero(self):
        r=self.rows[0];self.assertEqual(r['sample_name'],'PP');self.assertEqual([r[k] for k in ['source_raw_R450_TableV_pct','source_raw_R450_prose_pct','source_raw_R600_TableV_pct','source_raw_R700_TableV_pct']],['3.1','3.0','—','—'])
        self.assertTrue(all(not r[k] for k in ['R450_pct','R600_pct','R700_pct','residue_pct','residue_temp_C']))
    def test_defined_residues_keep_each_coordinate(self):
        expected=[('11.7','4.3','1.1'),('25.1','7.5','5.4'),('32.8','10.3','7.8'),('24.1','7.8','6.0')]
        for r,values in zip(self.rows[1:5],expected):self.assertEqual(tuple(r[k] for k in ['R450_pct','R600_pct','R700_pct']),values);self.assertEqual(r['residue_temp_C'],'700');self.assertEqual(r['residue_pct'],values[2])
    def test_TableII_recipe_not_silently_normalized(self):
        r=self.rows[1];self.assertEqual(r['composition'],'TableII PP/IFR/MAP/Z/CNT(wt%)=75/25.0/—/—/—;IFR APP/DPER ratio2:1, APP MHS-treated except explicit-r untreated branches; not normalized');self.assertIn('totals100.5',r['source_recipe_limits'])
    def test_ordinary_TG_not_TGFTIR_or_invented_endpoint(self):
        r=self.rows[-1];self.assertEqual([r[k] for k in ['sample_name','LOI_pct','T5_C','atmosphere','heating_rate_C_min']],['PPc/20IFR/1ZB','31.2','230.5','air','5']);self.assertEqual(r['residue_pct'],r['residue_temp_C']);self.assertFalse(r['residue_pct']);self.assertFalse(r.get('R800_pct',''))
    def test_literal_geometries_preserved_with_mother_material(self):
        for r in self.rows:self.assertTrue(r['source_original_material_form_TGA']);self.assertTrue(r['source_original_material_form_LOI']);self.assertEqual(r['material_form_TGA'],r['material_form_LOI'])
    def test_old_scope_is_separate_from_new_and_upgrade(self):
        m=self.manifest;self.assertEqual((m['selected_new_states'],m['selected_new_TG'],m['old_scope_admissions'],m['old_evidence_upgrades']),(6,6,5,0));old=[e for e in m['scope_entries'] if e['source_identity']=='10.3390/ma13235492'];self.assertEqual(len(old),5);self.assertTrue(all(e['scope_class']=='textile_cloth' and e['decision']=='admit_textile' for e in old))
    def test_prior_unresolved_processing_and_laminate_holds(self):
        held=[e for e in self.manifest['scope_entries'] if e['decision']=='hold_scope'];self.assertEqual(len(held),24);self.assertEqual(sum(e['source_identity']=='10.2115/fiber.28.9_359' for e in held),19);self.assertEqual(sum(e['source_identity']=='10.3144/expresspolymlett.2024.58' for e in held),5)
    def test_pyrolysis_no_own_LOI_and_processing_gaps_excluded(self):
        facts=self.manifest['processed_source_queue_facts'];negative=[q for q in facts if not q['verified_new_states']];self.assertEqual(len(negative),7);self.assertTrue(all(q['verified_new_TG']==0 for q in negative));self.assertTrue(all(r['DOI'] in ['10.1002/app.42875','10.1002/app.51016'] for r in self.rows))
if __name__=='__main__':unittest.main()
