"""Protect source-specific TG/LOI correspondence and conflicting additive evidence."""
import csv,json,sys,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'scripts'));import pairing as p
with(R/'data/incoming/verified_source_batch_20261006_b325_local_material.csv').open(newline='')as f:rows=list(csv.DictReader(f))
by={r['sample_state']:r for r in rows}
class SourceChecks(unittest.TestCase):
    def test_complete_inventory(self):
        self.assertEqual(set(by),{'PP'+str(i)for i in range(7)})
        self.assertEqual(len({p.sample_state_id(r)for r in rows}),7)
        self.assertTrue(all(not p.evidence_issues(r)for r in rows))
    def test_real_recipe_not_optimal_sentence(self):
        self.assertEqual((by['PP4']['PP_wt_pct'],by['PP4']['OS_MCAPP_wt_pct'],by['PP4']['PEIC_wt_pct']),('70','20','10'))
        self.assertEqual((by['PP4']['LOI_pct'],by['PP6']['LOI_pct']),('32.7','28.5'))
        self.assertIn('1:2',by['PP4']['limitations'])
    def test_distinct_adjacent_peak_temperatures(self):
        self.assertEqual((by['PP5']['Tmax1_C'],by['PP6']['Tmax1_C']),('367.3','367.2'))
    def test_no_additive_or_cone_residue(self):
        self.assertEqual(by['PP4']['R600_pct'],'19.7')
        self.assertTrue(all(r['residue_temp_C']=='600'and not r.get('R800_pct')for r in rows))
        self.assertTrue(all(not r.get('Tonset_C')and not r.get('T5_C')for r in rows))
    def test_normal_TG_not_TGIR(self):
        self.assertTrue(all((r['atmosphere'],r['heating_rate_C_min'],r['TG_start_C'],r['TG_end_C'])==('air','20','30','600')for r in rows))
        self.assertTrue(all(not r['TGA_mass_reported']and not r['TGA_pan']and not r['TGA_replicates']for r in rows))
        self.assertTrue(all(r['LOI_specimen_geometry']=='100x6.5x3mm'and not r['LOI_replicates']for r in rows))
    def test_changed_metric_or_state_rejected(self):
        for key,value in [('T10_C','333.5'),('Tmax1_C','381.3'),('residue_temp_C','800'),('heating_rate_C_min','40'),('material_form_TGA','isolated additive powder')]:
            with self.subTest(key=key):
                changed=dict(by['PP4']);changed[key]=value
                self.assertTrue(p.evidence_issues(changed))
    def test_no_full_profile_duplicates(self):
        a=json.loads((R/'data/curation/archive/source_review_manifest_20261006_b325.json').read_text())
        self.assertEqual((a['canonical_comparisons'],a['raw_paired_profile_hit_comparisons'],a['unresolved_approved_profile_hits']),(84,0,0))
        self.assertEqual(a['raw_hit_presentations'],5)
if __name__=='__main__':unittest.main()
