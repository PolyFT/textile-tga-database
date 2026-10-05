"""Keep the source's ambiguous air cells out of canonical thresholds and peaks."""
import csv,json,sys,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'scripts'));import pairing as p
with(R/'data/incoming/verified_source_batch_20261006_b326_local_material.csv').open(newline='')as f:rows=list(csv.DictReader(f))
by={(r['sample_state'],r['atmosphere']):r for r in rows}
class SourceChecks(unittest.TestCase):
    def test_four_states_eight_conditions(self):
        self.assertEqual(len(rows),8);self.assertEqual(len({p.sample_state_id(r)for r in rows}),4)
        self.assertTrue(all(not p.evidence_issues(r)for r in rows))
    def test_no_air_header_repair(self):
        for r in rows:
            if r['atmosphere']=='air':
                self.assertEqual((r['T5_C'],r['Tmax1_C']),('',''))
                self.assertTrue(r['source_air_Tmax1_header_value_C']and r['source_air_T5_header_value_C'])
                self.assertIn('HeldTable2',r['source_air_contested_metric_disposition'])
        self.assertEqual((by['PET','air']['source_air_Tmax1_header_value_C'],by['PET','air']['source_air_T5_header_value_C']),('390','435'))
    def test_uncontested_air_second_peak_and_explicit_residue(self):
        self.assertEqual((by['PET','air']['Tmax2_C'],by['PET','air']['R700_pct']),('575','0.1'))
        self.assertEqual((by['P(ET-co-BP)15','air']['Tmax2_C'],by['P(ET-co-BP)15','air']['R700_pct']),('618','6.1'))
        self.assertTrue(all(r['residue_temp_C']=='700'for r in rows))
    def test_N2_T5_not_onset_or_DSC(self):
        r=by['PET','N2'];self.assertEqual((r['T5_C'],r['Tmax1_C'],r['R700_pct']),('392','436','13.5'))
        self.assertTrue(all(not r.get('Tonset_C')for r in rows))
    def test_native_molar_composition_not_mass_percent(self):
        r=by['P(ET-co-BP)10','N2'];self.assertEqual((r['BPDI_nominal_mol_pct'],r['BPDI_measured_NMR_mol_pct']),('10','9.3'))
        self.assertEqual(r['material_scope_class'],'fiber_forming_polymer')
        self.assertIn('Covalent',r['composition'])
    def test_methods_and_replicates_not_borrowed(self):
        self.assertTrue(all((r['heating_rate_C_min'],r['TG_start_C'],r['TG_end_C'],r['TGA_pan'])==('10','40','700','Al2O3')for r in rows))
        self.assertTrue(all(not r['TGA_gas_flow_mL_min']and not r['TGA_replicates']for r in rows))
        self.assertTrue(all(r['LOI_replicates']=='atleast5'and r['LOI_specimen_geometry']=='HaakMiniJetmoulded120x6.5x3.2mm'for r in rows))
        self.assertEqual((by['P(ET-co-BP)10','N2']['LOI_pct'],by['P(ET-co-BP)10','N2']['source_LOI_plusminus_pct']),('27.5','0.2'))
    def test_unreviewed_repair_or_state_change_rejected(self):
        for key,value in [('T5_C','390'),('Tmax1_C','435'),('heating_rate_C_min','1000'),('residue_temp_C','600'),('material_form_TGA','isolated BPDI monomer')]:
            with self.subTest(key=key):
                changed=dict(by['PET','air']);changed[key]=value
                self.assertTrue(p.evidence_issues(changed))
    def test_canonical_profile_duplicates_resolved(self):
        a=json.loads((R/'data/curation/source_review_manifest_20261006_b326.json').read_text());self.assertEqual((a['canonical_comparisons'],a['raw_paired_profile_hit_comparisons'],a['unresolved_approved_profile_hits'],a['raw_hit_presentations']),(76,0,0,23))
if __name__=='__main__':unittest.main()
