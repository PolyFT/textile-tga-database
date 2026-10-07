"""Source-specific limits for the B790 polyamide batch; no inferred TG coordinates."""
import csv,json,unittest
from pathlib import Path
from scripts import pairing,reader_table
ROOT=Path(__file__).resolve().parents[1]
INCOMING=ROOT/'data/incoming/verified_source_batch_20261007_b790_polyamides.csv'
MANIFEST=ROOT/'data/curation/archive/20261007/source_review_manifest_b790.json'
class TestB790SourceLimits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with INCOMING.open(newline='') as stream:cls.rows=list(csv.DictReader(stream))
        cls.manifest=json.loads(MANIFEST.read_text())
    def group(self,doi):return [r for r in self.rows if r['DOI']==doi]
    def test_source_specific_conditions_not_borrowed(self):
        expected={'10.1002/app.42932':('N2','15',3),'10.1002/pat.4206':('air','15',4),'10.1002/pat.5003':('N2','10',4),'10.1007/s13233-017-5081-1':('N2','10',3),'10.1007/s10965-020-02229-8':('N2','10',5),'10.1016/j.polymdegradstab.2017.09.003':('air','20',6)}
        self.assertEqual(len(self.rows),25)
        self.assertEqual(len({pairing.sample_state_id(r) for r in self.rows}),25)
        for doi,(gas,rate,n) in expected.items():
            rr=self.group(doi);self.assertEqual(len(rr),n)
            self.assertEqual({(r['atmosphere'],r['heating_rate_C_min']) for r in rr},{(gas,rate)})
        self.assertEqual(self.manifest['new_sources'],6)
        self.assertEqual(self.manifest['incoming_files'],[str(INCOMING.relative_to(ROOT))])
    def test_residue_conflict_and_unknown_temperature_stay_raw(self):
        rr=self.group('10.1002/app.42932')
        s3=next(r for r in rr if r['sample_state'].startswith('S3;'))
        s4=next(r for r in rr if r['sample_state'].startswith('S4;'))
        for r in (s3,s4):
            self.assertEqual(r['residue_pct'],'');self.assertEqual(r['residue_temp_C'],'')
            view=reader_table.reading_row(r,{'scope_class':r['material_scope_class']})
            self.assertIn(r['source_residue_observation_note'],view[20])
            self.assertEqual(view[10],'')
        self.assertIn('4.8',s3['source_residue_observation_note']);self.assertIn('4.9',s3['source_residue_observation_note'])
        self.assertIn('10.7',s4['source_residue_observation_note'])
        self.assertTrue(all(not r.get('residue_temp_C') for r in self.group('10.1002/pat.5003')))
    def test_undefined_peak_and_relative_loss_not_promoted(self):
        for doi in ('10.1002/pat.4206','10.1002/pat.5003','10.1007/s13233-017-5081-1'):
            self.assertTrue(all(not r.get('Tmax1_C') and not r.get('Tmax2_C') for r in self.group(doi)))
        apba=next(r for r in self.group('10.1016/j.polymdegradstab.2017.09.003') if r['sample_state'].startswith('PA6/APBA12;'))
        self.assertEqual(apba['T5_C'],'')
        self.assertIn('371.2',apba['source_thermal_metric_annotation_note']);self.assertIn('15.8',apba['source_thermal_metric_annotation_note'])
        self.assertNotIn('381.2',apba['source_thermal_metric_annotation_note'])
        mh20=next(r for r in self.group('10.1007/s10965-020-02229-8') if r['sample_state'].startswith('PA6/MCA-MH-20;'))
        self.assertEqual(mh20['residue_pct'],'')
        self.assertIn('10.2',mh20['source_thermal_metric_annotation_note']);self.assertIn('4.1',mh20['source_thermal_metric_annotation_note'])
    def test_control_authority_and_literal_details(self):
        self.assertFalse(any(r['sample_state'].startswith('PA6;') for r in self.group('10.1002/pat.5003')))
        pure=next(r for r in self.group('10.1007/s10965-020-02229-8') if r['sample_state'].startswith('PA6;'))
        self.assertEqual((pure['T5_C'],pure['Tmax1_C'],pure['residue_pct'],pure['residue_temp_C']),('412.3','470.5','0.1','800'))
        self.assertIn('Table1',pure['pairing_evidence'])
        self.assertIn('0.13',pure['source_thermal_metric_annotation_note'])
        self.assertIn('Exact TG geometry is unknown',pure['pairing_evidence'])
        for r in self.rows:
            view=reader_table.reading_row(r,{'scope_class':r['material_scope_class']})
            if r.get('source_LOI_entry_raw'):self.assertIn(r['source_LOI_entry_raw'],view[21])
            if r.get('gas_flow_mL_min'):self.assertEqual(r['gas_flow_mL_min'],view[22])
        trial=dict(pure,source_unapproved_peak_C='999')
        self.assertNotIn('source_unapproved_peak_C',reader_table.reading_row(trial,{'scope_class':pure['material_scope_class']})[20])
if __name__=='__main__':unittest.main()
