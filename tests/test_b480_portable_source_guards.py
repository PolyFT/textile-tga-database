"""Source-specific B480 guards; passing is not independent source approval."""
import copy,csv,json,unittest
from pathlib import Path
import pairing,reader_table
ROOT=Path(__file__).resolve().parents[1]
INCOMING=ROOT/'data/incoming/verified_source_batch_20261007_b480_local_material.csv'
MANIFEST=ROOT/'data/curation/archive/20261007/source_review_manifest_b480.json'

def source_guard(row):
    """Keep the actual RCF evidence and reject interpolation from other assays."""
    checks={'DOI':'10.1039/d6ta00859c','sample_state':'RCF','LOI_pct':'18',
            'source_LOI_entry_raw':'approximately18%','R800_pct':'12.13',
            'residue_pct':'12.13','residue_temp_C':'800','atmosphere':'N2',
            'heating_rate_C_min':'10','gas_flow_mL_min':'50',
            'material_form_TGA':'regeneratedcellulose fibre',
            'material_form_LOI':'regeneratedcellulose fibre',
            'source_Tmax_ambiguous_C':'317.78','T5_C':'','T10_C':'','Tonset_C':'','Tmax1_C':''}
    return all(row.get(k,'')==z for k,z in checks.items()) and not pairing.evidence_issues(row)

class B480SourceGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with INCOMING.open(newline='') as handle:
            cls.rows=list(csv.DictReader(handle))
        cls.manifest=json.loads(MANIFEST.read_text())
        assert len(cls.rows)==1
        cls.r=cls.rows[0]
        cls.facts={r['DOI']:r for r in cls.manifest['processed_source_queue_facts']}

    def changed(self,**fields):
        r=copy.deepcopy(self.r);r.update(fields);return r

    def test_default_repository_archive_path(self):
        self.assertEqual(str(MANIFEST.relative_to(ROOT)),self.manifest['public_archive_path'])
        self.assertEqual(str(INCOMING.relative_to(ROOT)),self.manifest['public_incoming_path'])

    def test_root_source_approval_preserves_original_pending_stage(self):
        self.assertTrue(source_guard(self.r))
        self.assertEqual((self.manifest['sourceapproved'],self.manifest['rootapproved'],self.manifest['published']),(1,1,0))
        for key in ['sourceapproved','rootapproved','published']:self.assertEqual(self.manifest['primary_snapshot'][key],0)
        self.assertTrue(self.manifest['root_source_approval_sha256'])
        self.assertTrue(self.manifest['primary_all_scientific_numeric_form_state_preparation_locator_fields_preserved'])

    def test_approximate_loi_preserved(self):
        self.assertFalse(source_guard(self.changed(source_LOI_entry_raw='18.0% exact')))
        row=reader_table.reading_row(self.r,{'scope_class':'textile_fibre'})
        self.assertIn('approximately18%',row[21])

    def test_peak_not_defined_rate_remains_raw(self):
        for field in ['T5_C','T10_C','Tonset_C','Tmax1_C']:
            self.assertFalse(source_guard(self.changed(**{field:'317.78'})))
        row=reader_table.reading_row(self.r,{'scope_class':'textile_fibre'})
        self.assertEqual(row[6:10],['','','',''])
        self.assertIn('source_Tmax_ambiguous_C=317.78',row[20])

    def test_explicit_residue_temperature(self):
        self.assertFalse(source_guard(self.changed(residue_temp_C='700',R800_pct='')))
        self.assertIn('800℃: 12.13%',reader_table.reading_row(self.r,{'scope_class':'textile_fibre'})[10])

    def test_caf_residue_not_at_rcf_or_program_end(self):
        self.assertFalse(source_guard(self.changed(sample_state='CAF-1',residue_pct='24.68',R800_pct='24.68')))
        r={'source_raw_residue_pct':'24.68','source_residue_temperature_status':'unreported',
           'TG_end_C':'800','sample_state':'CAF-1'}
        row=reader_table.reading_row(r,{'scope_class':'textile_fibre'})
        self.assertEqual(row[10],'');self.assertIn('24.68',row[20])

    def test_group_caf_loi_not_individual(self):
        self.assertFalse(source_guard(self.changed(sample_state='CAF-3',LOI_pct='32')))
        self.assertEqual(self.facts['10.1039/d6ta00859c']['nonnumeric_initial_contexts'],3)

    def test_relative_washing_retention_not_absolute_loi(self):
        self.assertFalse(source_guard(self.changed(sample_state='CAF-3;30washingcycles',LOI_pct='90')))
        self.assertEqual(self.facts['10.1039/d6ta00859c']['nonnumeric_washed_relative_retention_contexts'],3)

    def test_pcfc_flow_and_rate_not_ordinary_tg(self):
        self.assertFalse(source_guard(self.changed(heating_rate_C_min='60',gas_flow_mL_min='80')))
        self.assertFalse(source_guard(self.changed(atmosphere='air')))

    def test_fibre_to_fabric_or_bulk_not_inherited(self):
        for form in ['woven fabric','bulk moulded cellulose','polyurethane elastomer']:
            self.assertFalse(source_guard(self.changed(material_form_TGA=form)))

    def test_ep_bulk_tg_not_gfep_loi(self):
        fact=self.facts['10.1002/pc.25172']
        self.assertEqual((fact['LOI_only_conditions'],fact['TG_only_numeric_conditions']),(5,2))
        self.assertIn('glassfabric epoxy LOI',fact['scientific_decision'])
        self.assertIn('unreinforced epoxy TG',fact['scientific_decision'])

    def test_mcc_tp_not_tg_tmax(self):
        for tp in ['395','430','425','452']:
            self.assertFalse(source_guard(self.changed(DOI='10.1002/pc.25172',Tmax1_C=tp)))
        self.assertIn('MCC Table2 Tp not ordinary TG',self.facts['10.1002/pc.25172']['scientific_decision'])

    def test_cpu_missing_rate_cannot_pass(self):
        self.assertFalse(source_guard(self.changed(DOI='10.1039/d5ta04322k',sample_state='Control1',
                                                  LOI_pct='20.4',T5_C='272.1',heating_rate_C_min='')))
        self.assertEqual(self.facts['10.1039/d5ta04322k']['wholeheld_states'],3)

    def test_cpu_unknown_char_temp_or_cct_not_tg(self):
        for char in ['6.68','11.2']:
            self.assertFalse(source_guard(self.changed(DOI='10.1039/d5ta04322k',sample_state='CPU5',
                                                      LOI_pct='27.8',R800_pct=char)))

    def test_unknown_source_temperature_not_whitelisted(self):
        row=reader_table.reading_row(self.changed(source_initial_C='999',source_unqualified_temperature_C='998'),{'scope_class':'textile_fibre'})
        self.assertNotIn('999',row[20]);self.assertNotIn('998',row[20])

    def test_no_guessed_error_or_final_retained_dope_fraction(self):
        self.assertEqual(self.r.get('LOI_uncertainty_pct',''),'')
        self.assertIn('nominal4wt%',self.r['composition'])
        self.assertIn('Wording of24g mixture/component basis ambiguous',self.r['source_preparation'])

    def test_caf_traction_not_assigned_to_rcf(self):
        self.assertIn('Drawratio1.6 androller8rpm are described inCAF',self.r['source_preparation'])
        self.assertIn('not assigned as RCF settings',self.r['source_preparation'])

    def test_zero_sources_not_proposed_pairs(self):
        for doi in ['10.1002/pc.25172','10.1039/d5ta04322k']:
            self.assertEqual(self.facts[doi]['candidate_unique_states'],0)
        self.assertEqual(self.manifest['raw_view_counts']['total'],24)
        self.assertEqual(self.manifest['proposed_new_unique_states'],1)

    def test_public_files_contain_no_local_path_or_fulltext(self):
        text=INCOMING.read_text()+MANIFEST.read_text()
        for prefix in ['/'+'Volumes/','/'+'Users/','smb'+':','file'+':']:
            self.assertNotIn(prefix,text)

if __name__=='__main__':unittest.main()
