"""B641 public literal evidence bindings and scientific exclusion boundaries."""
import copy,csv,hashlib,json,unittest
from pathlib import Path
from scripts import pairing,textile_scope,reader_table
ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'data/curation/archive/20261007/source_review_manifest_b641.json'
def digest(row):
    return hashlib.sha256(json.dumps({k:v for k,v in row.items() if v!=''},sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
class B641SourceGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=json.loads(MANIFEST.read_text());cls.allrows=[]
        for name in cls.m['incoming_files']:
            with (ROOT/name).open(newline='') as f:cls.allrows+=list(csv.DictReader(f))
        cls.rows=[r for r in cls.allrows if r['direct_numeric_use']=='yes']
        cls.pending=[r for r in cls.allrows if r['direct_numeric_use']!='yes']
    def subset(self,doi):return [r for r in self.rows if r['DOI']==doi]
    def test_literal_full_rows_and_unknown_field_mutation(self):
        self.assertEqual(len(self.allrows),46);self.assertEqual(len(self.rows),36)
        facts={f['nonempty_provided_row_sha256'] for f in self.m['selected_source_facts']+self.m['condition_pending_source_facts']}
        self.assertEqual({digest(r) for r in self.allrows},facts)
        r=copy.deepcopy(self.rows[0]);before=digest(r);r['source_future_field']='0';self.assertNotEqual(before,digest(r))
    def test_states_not_gas_conditions(self):
        self.assertEqual(len({pairing.sample_state_id(r) for r in self.rows}),18)
        self.assertEqual(len({pairing.pair_key(r) for r in self.rows}),36)
        self.assertEqual(len({r['DOI'] for r in self.rows}),4)
    def test_required_unknown_conditions_remain_pending(self):
        self.assertEqual(len(self.pending),10)
        self.assertEqual(len({pairing.sample_state_id(r) for r in self.pending}),7)
        for r in self.pending:
            self.assertEqual(r.get('heating_rate_C_min',''),'')
            self.assertEqual(r['direct_numeric_use'],'pending_missing_required_test_conditions')
            self.assertIn('pending_required_test_conditions',r['review_disposition'])
        admitted={e['sample_state_id'] for e in self.m['scope_entries']}
        self.assertFalse(admitted & {pairing.sample_state_id(r) for r in self.pending})
    def test_measurement_and_scope_mutations_stale(self):
        for r,e in zip(self.rows,self.m['scope_entries']):
            self.assertEqual(pairing.evidence_issues(r),[])
            self.assertEqual(e['scope_identity_sha256'],textile_scope.scope_identity_sha256(r))
            self.assertEqual(e['reviewed_measurement_fingerprint'],pairing.measurement_fingerprint(r))
            self.assertFalse(e['proposal_only']);self.assertEqual(r['direct_numeric_use'],'yes')
        r=copy.deepcopy(self.rows[0]);r['LOI_pct']='999';self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(r))
        r=copy.deepcopy(self.rows[0]);r['material_form_TGA']+=' invented';self.assertNotEqual(pairing.material_scope_fingerprint(r),r['reviewed_material_scope_fingerprint'])
    def test_reuse_held_pure_and_uncompat_PP_absent(self):
        rs=self.subset('10.1021/am8001204');self.assertEqual(len(rs),2)
        self.assertEqual({r['sample_name'] for r in rs},{'C-PP/20% PDBPP'})
        n2=next(r for r in rs if r['atmosphere']=='N2');air=next(r for r in rs if r['atmosphere']=='air')
        self.assertEqual(n2.get('T5_C',''),'');self.assertEqual(n2.get('Tmax1_C',''),'')
        self.assertEqual(n2['source_T5_relative_increase_C'],'about6');self.assertEqual(n2['source_Tmax_relative_increase_C'],'about24')
        self.assertEqual(air['T5_C'],'296');self.assertEqual(air['Tmax1_C'],'480')
    def test_source_recipe_wholeholds_absent(self):
        self.assertNotIn('PP-1',{r['sample_name'] for r in self.subset('10.1016/j.polymdegradstab.2019.05.003')})
        self.assertNotIn('FRWPU-3',{r['sample_name'] for r in self.subset('10.1002/app.48444')})
        self.assertNotIn('PP',{r['sample_name'] for r in self.subset('10.1021/acsapm.2c00146')})
    def test_undefined_WPU_threshold_and_peaks_stay_raw(self):
        for r in self.subset('10.1002/app.48444'):
            self.assertEqual(r.get('T5_C',''),'');self.assertEqual(r.get('Tmax1_C',''),'');self.assertEqual(r.get('Tmax2_C',''),'')
            self.assertNotEqual(r['source_raw_Td5_C'],'');self.assertNotEqual(r['source_raw_Tmax1_C'],'')
            self.assertIn(r['source_raw_Td5_C'],reader_table.reading_row(r,{'scope_class':r['material_scope_class']})[20])
    def test_LOI_uncertainty_glyph_not_invented(self):
        for r in self.subset('10.1002/app.48444'):
            self.assertIn('unresolved',r['LOI_uncertainty_type']);self.assertNotIn('±',r['LOI_uncertainty_type']);self.assertNotEqual(r['source_LOI_error_raw'],'')
    def test_PP_undefined_ordered_peak_not_canonical(self):
        for r in self.subset('10.1016/j.polymdegradstab.2019.05.003'):
            self.assertEqual(r.get('Tmax1_C',''),'');self.assertNotEqual(r['source_raw_Table3_Tmax_C'],'')
    def test_residue_temperature_and_literal_zero(self):
        for r in self.rows:
            for temp in ['600','800']:
                if r.get('R'+temp+'_pct','')!='':
                    self.assertEqual(r['residue_temp_C'],temp);self.assertEqual(r['residue_pct'],r['R'+temp+'_pct'])
        r=copy.deepcopy(next(r for r in self.rows if r.get('R800_pct')=='0'));before=digest(r);r['R800_pct']='';self.assertNotEqual(before,digest(r))
    def test_preparation_reader_does_not_create_branch(self):
        for r,e in zip(self.rows,self.m['scope_entries']):
            out=reader_table.reading_row(r,e);self.assertNotIn('其他分支',out[14])
            if r.get('treatment_method'):self.assertEqual(out[14].count(r['treatment_method']),1)
            self.assertFalse(r.get('source_schema_authority_note'))
    def test_negative_sources_are_queue_facts_only(self):
        negatives=[f for f in self.m['processed_source_queue_facts'] if f['negative_only']]
        self.assertEqual(len(negatives),3)
        for f in negatives:self.assertEqual(f['source_supported_states'],0);self.assertEqual(self.subset(f['DOI']),[])
    def test_public_privacy_and_historical_stage(self):
        for text in [MANIFEST.read_text()]+[(ROOT/n).read_text() for n in self.m['incoming_files']]:
            for forbidden in ['/Volumes/','/Users/','smb://']:self.assertNotIn(forbidden,text)
        self.assertFalse(self.m['publication_approved']);self.assertEqual(self.m['published'],0)
        self.assertEqual(self.m['formal_baseline'],{'states':1005,'TG':1291,'sources':202})
if __name__=='__main__':unittest.main()
