"""Scope-only documentary admissions; scientific master rows stay unchanged."""
import copy,csv,hashlib,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'data/curation/archive/20261007/source_review_manifest_b483.json'
MASTER=ROOT/'data/tg_loi_master.csv'
def full_nonempty_hash(row):
    return hashlib.sha256(json.dumps({k:v for k,v in row.items()if v!=''},sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def literal_row_preserved(row,entry):
    return full_nonempty_hash(row)==entry['nonempty_original_row_sha256']
class LegacyScopeGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=json.loads(MANIFEST.read_text())
        cls.selected=cls.manifest['selected_existing_observations']
        cls.bindings=cls.manifest['scope_entries']
        with MASTER.open(newline='') as handle:cls.master=list(csv.DictReader(handle))
        cls.rows=[]
        for e in cls.selected:
            r=e['row'];matches=[x for x in cls.master if x['DOI'].casefold()==r['DOI'].casefold()and x['sample_state']==r['sample_state']and x['washing_state']==r['washing_state']and x['atmosphere']==r['atmosphere']and x['heating_rate_C_min']==r['heating_rate_C_min']]
            assert len(matches)==1
            cls.rows.append(matches[0])
    def sample(self,name,atmosphere=None):
        return next(e for e in self.selected if e['row']['sample_state']==name and(atmosphere is None or e['row']['atmosphere']==atmosphere))
    def test_real_default_archive_path(self):self.assertEqual(str(MANIFEST.relative_to(ROOT)),'data/curation/archive/20261007/source_review_manifest_b483.json')
    def test_all40_nonempty_old_fields_preserved(self):self.assertEqual(len(self.rows),40);self.assertTrue(all(literal_row_preserved(r,e)for r,e in zip(self.rows,self.selected)))
    def test_actual_treatment_mutation_rejected(self):
        r=copy.deepcopy(self.rows[-1]);r['treatment_method']=r.get('treatment_method','')+' fabricated';self.assertFalse(literal_row_preserved(r,self.selected[-1]))
    def test_unknown_nonempty_and_literal_zero_protected(self):
        r=copy.deepcopy(self.rows[-1]);r['unknown_scientific_field']='0';self.assertFalse(literal_row_preserved(r,self.selected[-1]))
    def test_added_blank_default_does_not_hide_science(self):
        r=copy.deepcopy(self.rows[-1]);r['new_empty_column']='';self.assertTrue(literal_row_preserved(r,self.selected[-1]));r['new_empty_column']='0';self.assertFalse(literal_row_preserved(r,self.selected[-1]))
    def test_scope20conditions12states_not20samples(self):
        a=[e for e in self.bindings if e['decision']=='admit_textile'];self.assertEqual(len(a),20);self.assertEqual(len({(e['source_identity'],e['sample_state_id'])for e in a}),12)
    def test_20holds_remain20_states(self):
        h=[e for e in self.bindings if e['decision']=='hold_scope'];self.assertEqual(len(h),20);self.assertEqual(len({(e['source_identity'],e['sample_state_id'])for e in h}),20)
    def test_newpairs_and_evidenceupgrades_zero(self):self.assertEqual(self.manifest['newpairs'],0);self.assertEqual(self.manifest['newTG'],0);self.assertEqual(self.manifest['evidence_upgrades'],0)
    def test_PVA_uncrosslinked_saltwash_gate(self):
        self.assertEqual(self.sample('PVA')['decision'],'hold_scope');self.assertEqual(self.sample('PVA/75CD')['decision'],'hold_scope');self.assertEqual(self.sample('PVA/75CD/HDI')['decision'],'admit_textile')
    def test_powder_aliquot_and_cone_hotpress_not_substituted(self):
        e=self.sample('PVA/75CD');self.assertEqual(e['decision'],'hold_scope');self.assertEqual(e['scope_class'],'textile_fibre')
        # Changing process evidence to a cone-only hotpress history is a real row change.
        i=self.selected.index(e);r=copy.deepcopy(self.rows[i]);r['source_preparation']='cone hotpressed100x100x4mm';self.assertFalse(literal_row_preserved(r,e))
    def test_PA66_only_actual15_25(self):
        e=[e for e in self.selected if e['row']['DOI'].endswith('106271')];self.assertEqual({x['row']['sample_state']for x in e},{'IP6_15PA66','IP6_25PA66'});self.assertEqual(len(e),4)
    def test_PA66_reverse_columns_literal(self):
        self.assertEqual(self.sample('IP6_25PA66','N2')['row']['T10_C'],'305.49');self.assertEqual(self.sample('IP6_15PA66','N2')['row']['T10_C'],'323.39')
        self.assertEqual(self.sample('IP6_25PA66','air')['row']['T10_C'],'303.48');self.assertEqual(self.sample('IP6_15PA66','air')['row']['T10_C'],'329.51')
    def test_T10_not_onset_or_T5(self):
        e=self.sample('IP6_25PA66','N2');self.assertEqual(e['row']['Tonset_C'],'');self.assertEqual(e['row']['T5_C'],'');self.assertNotEqual(e['row']['T10_C'],'')
    def test_SiPAN_actual_initial_labels_and_0WCs(self):
        e=[e for e in self.selected if e['row']['DOI'].endswith('2017.07.022')];self.assertEqual({x['row']['sample_state']for x in e},{'Si-PAN initial','Si-P-PAN initial'})
        self.assertEqual(self.sample('Si-PAN initial')['row']['LOI_pct'],'25.1');self.assertEqual(self.sample('Si-P-PAN initial')['row']['LOI_pct'],'30.3')
    def test_durability_LOI_not_initial_TG(self):
        e=self.sample('Si-PAN initial');i=self.selected.index(e);r=copy.deepcopy(self.rows[i]);r['washing_state']='one laundering cycle';r['LOI_pct']='23.4';self.assertFalse(literal_row_preserved(r,e))
    def test_T5_water_inclusive_lowvalue_not_peak(self):
        r=self.sample('Si-P-PAN initial','N2')['row'];self.assertEqual(r['T5_C'],'125');self.assertEqual(r['Tmax1_C'],'');self.assertEqual(r['Tonset_C'],'')
    def test_residue_temperatures_no_borrowing(self):
        self.assertEqual(self.sample('Si-P-PAN initial','N2')['row']['residue_temp_C'],'800');self.assertEqual(self.sample('IP6_15PA66','N2')['row']['residue_temp_C'],'800')
        self.assertEqual(self.sample('Print cloth, untreated','N2')['row']['residue_temp_C'],'500')
    def test_scope_classes_and_fingerprints_bound(self):
        self.assertEqual(sum(e['scope_class']=='textile_fibre'and e['decision']=='admit_textile'for e in self.bindings),1)
        self.assertEqual(sum(e['scope_class']=='textile_cloth'and e['decision']=='admit_textile'for e in self.bindings),19)
        self.assertTrue(all(e['measurement_fingerprint']==e['row']['reviewed_measurement_fingerprint']and e['scope_identity_sha256']for e in self.selected))
    def test_missing_local_body_not_complete_newreview(self):
        facts=[f for f in self.manifest['processed_source_queue_facts']if f.get('review_role')]
        self.assertEqual(len(facts),10);self.assertEqual(sum(f['source_original_navigation']=='bounded_current_original_not_recovered'for f in facts),5)
        self.assertTrue(all('not_new_full_source_review'in f['review_role']for f in facts))
    def test_queue_broad_count_not_scope_count(self):
        f=next(f for f in self.manifest['processed_source_queue_facts']if f['DOI']=='10.3390/polym12051078')
        self.assertEqual(f['existing_verified_unique_sample_states_literal'],'3');self.assertEqual(f['admitted_old_scope_states'],1);self.assertEqual(f['verified_unique_sample_states_update'],'preserve_existing_literal')
    def test_three_completed_zero_sources_preserve_holds(self):
        f=[x for x in self.manifest['processed_source_queue_facts']if x.get('source_review_complete')]
        self.assertEqual(len(f),3);self.assertTrue(all(x['new_pairs']==0 and x['candidate_unique_states']==0 for x in f))
        self.assertEqual(next(x for x in f if x['DOI']=='10.1002/vnl.21726')['wholeheld_states'],4)
    def test_prediction_is_scopeonly_with_wide_table_unchanged(self):
        self.assertEqual(self.manifest['private_prediction_only']['states'],888);self.assertEqual(self.manifest['private_prediction_only']['TG'],1099);self.assertEqual(self.manifest['old_master_field_changes'],0)
if __name__=='__main__':unittest.main()
