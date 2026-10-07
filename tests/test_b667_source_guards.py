"""B667 source evidence bindings and exclusions survive normal ingestion."""
import copy,csv,hashlib,json,unittest
from pathlib import Path
from scripts import pairing,textile_scope,reader_table
ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'data/curation/archive/20261007/source_review_manifest_b667.json'
def digest(r):
    return hashlib.sha256(json.dumps({k:v for k,v in r.items() if v!=''},sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
class B667SourceGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=json.loads(MANIFEST.read_text());cls.allrows=[]
        for name in cls.m['incoming_files']:
            with (ROOT/name).open(newline='') as f:cls.allrows+=list(csv.DictReader(f))
        cls.rows=[r for r in cls.allrows if r['direct_numeric_use']=='yes']
        cls.pending=[r for r in cls.allrows if r['direct_numeric_use']!='yes']
    def subset(self,doi):return [r for r in self.rows if r['DOI']==doi]
    def test_full_source_rows_including_literal_zero(self):
        self.assertEqual(len(self.allrows),28)
        self.assertEqual({digest(r) for r in self.allrows},{f['nonempty_provided_row_sha256'] for f in self.m['selected_source_facts']})
        r=copy.deepcopy(next(r for r in self.rows if r.get('R800_pct')=='0'));before=digest(r)
        r['R800_pct']='';self.assertNotEqual(before,digest(r))
        r['future_unknown_field']='0';self.assertNotEqual(before,digest(r))
    def test_states_are_not_gas_record_counts(self):
        self.assertEqual(len(self.rows),24)
        self.assertEqual(len({pairing.sample_state_id(r) for r in self.rows}),16)
        self.assertEqual(len({pairing.pair_key(r) for r in self.rows}),24)
        self.assertEqual(len({r['DOI'] for r in self.rows}),4)
    def test_condition_conflict_and_prior_reuse_remain_pending(self):
        self.assertEqual(len(self.pending),4)
        cond=[r for r in self.pending if r['DOI']=='10.1002/pen.21153']
        self.assertEqual(len(cond),3)
        self.assertTrue(all(r['heating_rate_C_min']=='' and r['direct_numeric_use']=='pending_missing_required_test_conditions' for r in cond))
        reused=[r for r in self.pending if r['DOI']=='10.1002/pat.1484']
        self.assertEqual([r['sample_name'] for r in reused],['9'])
        self.assertEqual(reused[0]['direct_numeric_use'],'pending_cross_source_reuse_review')
        admitted={e['sample_state_id'] for e in self.m['scope_entries']}
        self.assertFalse(admitted & {pairing.sample_state_id(r) for r in self.pending})
    def test_scope_and_measurement_changes_require_review(self):
        for r,e in zip(self.rows,self.m['scope_entries']):
            self.assertEqual(pairing.evidence_issues(r),[])
            self.assertEqual(e['scope_identity_sha256'],textile_scope.scope_identity_sha256(r))
            self.assertEqual(e['reviewed_measurement_fingerprint'],pairing.measurement_fingerprint(r))
            self.assertFalse(e['proposal_only'])
        r=copy.deepcopy(self.rows[0]);r['LOI_pct']='999'
        self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(r))
        r=copy.deepcopy(self.rows[0]);r['material_form_TGA']+=' changed'
        self.assertNotEqual(pairing.material_scope_fingerprint(r),r['reviewed_material_scope_fingerprint'])
    def test_PA6_five_percent_threshold_and_real_zero(self):
        rs=self.subset('10.1002/app.46039');self.assertEqual(len(rs),6)
        for r in rs:
            self.assertNotEqual(r['T5_C'],'');self.assertNotEqual(r['T50_C'],'')
            self.assertEqual(r.get('Tonset_C',''),'');self.assertEqual(r['residue_temp_C'],'800')
        pure=next(r for r in rs if r['sample_name']=='PA6')
        self.assertEqual((pure['LOI_pct'],pure['T5_C'],pure['T50_C'],pure['R800_pct']),('23.5','392','444','0'))
    def test_undefined_initial_temperature_stays_raw(self):
        rs=self.subset('10.1002/pat.1484');self.assertEqual({r['sample_name'] for r in rs},{'1','3'})
        for r in rs:
            self.assertEqual(r.get('T5_C',''),'');self.assertEqual(r.get('Tonset_C',''),'')
            self.assertNotEqual(r['Tmax1_C'],'');self.assertNotEqual(r['Tmax2_C'],'')
    def test_original_peak_ordinals_and_residue_temperatures(self):
        rs=self.subset('10.1002/app.45491');self.assertEqual(len(rs),8)
        self.assertNotIn('SP1',{r['sample_name'] for r in rs})
        for r in rs:
            self.assertEqual(r.get('Tmax2_C',''),'');self.assertEqual(r.get('R800_pct',''),'')
        r=next(r for r in rs if r['sample_name']=='SP4' and r['atmosphere']=='air')
        self.assertEqual((r['Tmax1_C'],r['Tmax3_C'],r['R500_pct'],r['R700_pct']),('326','292','13.5','3.0'))
    def test_residue_at_DTG_peak_is_not_end_of_program(self):
        rs=self.subset('10.1002/app.48308');self.assertEqual(len(rs),8)
        self.assertEqual({r['sample_name'] for r in rs},{'S-1','S-3','S-5','S-9'})
        for r in rs:
            self.assertEqual(r['residue_temp_C'],r['Tmax1_C']);self.assertEqual(r.get('R800_pct',''),'')
            self.assertNotEqual(r['residue_pct'],'')
        r=next(r for r in rs if r['sample_name']=='S-1' and r['atmosphere']=='N2')
        self.assertEqual((r['residue_pct'],r['residue_temp_C']),('35.3','463'))
    def test_calculated_LOI_and_unassigned_processing_not_admitted(self):
        self.assertEqual(self.subset('10.1002/app.49525'),[])
        self.assertEqual(self.subset('10.1002/app.49813'),[])
        for r in self.rows:
            self.assertFalse(r.get('source_schema_authority_note'))
            self.assertNotIn('其他分支',reader_table.reading_row(r,{'scope_class':r['material_scope_class']})[14])
    def test_public_evidence_and_historical_stage(self):
        for text in [MANIFEST.read_text()]+[(ROOT/n).read_text() for n in self.m['incoming_files']]:
            for forbidden in ['/Volumes/','/Users/','smb://']:self.assertNotIn(forbidden,text)
        self.assertFalse(self.m['publication_approved']);self.assertEqual(self.m['published'],0)
        self.assertEqual(self.m['formal_closed_baseline'],{'states':1023,'TG':1327,'sources':206})
if __name__=='__main__':unittest.main()
