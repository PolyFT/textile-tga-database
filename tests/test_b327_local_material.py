"""Protect the ambiguous recipe and independent original test conditions."""
import csv,json,sys,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'scripts')); import pairing as p
with(R/'data/incoming/verified_source_batch_20261006_b327_local_material.csv').open(newline='')as f: rows=list(csv.DictReader(f))
by={r['sample_state']:r for r in rows}; good=[r for r in rows if r['pairing_status']=='verified_exact']
def scientific_issues(row):
    issues=list(p.evidence_issues(row))
    # Source-specific auxiliary recipe columns must also match the reviewed source.
    source_recipe={'PP':('100','0','0','0'),'25APP':('65','10','0','25'),'5CB20APP':('65','10','5','20'),'7CB18APP':('65','10','7','18')}
    expected=source_recipe.get(row['sample_state'])
    if expected is not None and tuple(row[k]for k in ['PP_wt_pct','PPMA_wt_pct','CB_wt_pct','APP_wt_pct'])!=expected:
        issues.append('source_recipe_auxiliary_columns_mismatch')
    return issues
class SourceChecks(unittest.TestCase):
    def test_three_reviewed_and_two_held(self):
        self.assertEqual((len(rows),len(good),len({p.sample_state_id(r)for r in good})),(5,3,3))
        self.assertTrue(all(not scientific_issues(r)for r in good))
        self.assertEqual(json.loads((R/'data/curation/archive/source_review_manifest_20261006_b327.json').read_text())['source_guard_count'],45)
    def test_no_recipe_repair(self):
        r=by['3CB23APP_recipe_unresolved']; self.assertIn('held_recipe',r['pairing_status'])
        self.assertTrue(all(not r[k]for k in ['PP_wt_pct','PPMA_wt_pct','CB_wt_pct','APP_wt_pct','reviewed_measurement_fingerprint']))
        changed=dict(r,pairing_status='verified_exact',sample_state='3CB22APP'); self.assertTrue(p.evidence_issues(changed))
    def test_rounded_control_reuse_remains_held(self):
        r=by['PP']; self.assertIn('held_control',r['pairing_status'])
        self.assertEqual(r['reviewed_measurement_fingerprint'],'')
        self.assertTrue(p.evidence_issues(dict(r,pairing_status='verified_exact')))
        a=json.loads((R/'data/curation/archive/source_review_manifest_20261006_b327.json').read_text())['source_family_control_amendment']
        self.assertTrue(a['integer_rounding_compatible'])
        self.assertFalse(a['exact_paired_duplicate_proven'])
        self.assertEqual((a['new_pairs_retained'],a['old_scope_states_retained']),(3,100))
    def test_whole_composite_not_free_maleic_anhydride(self):
        r=by['7CB18APP']; self.assertEqual(tuple(r[k]for k in ['PP_wt_pct','PPMA_wt_pct','CB_wt_pct','APP_wt_pct']),('65','10','7','18'))
        self.assertIn('graftcontent0.8',r['composition']); self.assertEqual(by['PP']['PPMA_wt_pct'],'0')
    def test_two_peaks_and_explicit_residue_not_cone(self):
        r=by['7CB18APP']; self.assertEqual(tuple(r[k]for k in ['T5_C','T10_C','Tmax1_C','Tmax2_C','R700_pct']),('339.1','362.8','458.8','597.5','8.4'))
        self.assertEqual(tuple(by['PP'][k]for k in ['T5_C','T10_C','Tmax1_C','Tmax2_C','R700_pct']),('275.8','281.5','320.1','','0.0'))
        self.assertTrue(all(r['residue_temp_C']=='700'and not r.get('Tonset_C')for r in rows))
    def test_no_char_replicates_or_UL94_geometry_borrowed(self):
        self.assertTrue(all(tuple(r[k]for k in ['atmosphere','heating_rate_C_min','TG_start_C','TG_end_C','LOI_specimen_geometry'])==('air','10','25','700','130x6.5x3.2mm')for r in rows))
        self.assertTrue(all(not r[k]for r in rows for k in ['TGA_mass_reported','TGA_pan','TGA_gas_flow_mL_min','TGA_replicates','LOI_replicates']))
        self.assertEqual((by['PP']['source_LOI_plusminus_pct'],by['25APP']['source_LOI_plusminus_pct']),('0.1','0.2'))
    def test_unreviewed_state_and_metric_changes_rejected(self):
        for key,value in [('T5_C','339.2'),('Tmax2_C','600'),('heating_rate_C_min','20'),('residue_temp_C','600'),('material_form_TGA','isolated carbon black'),('APP_wt_pct','22')]:
            with self.subTest(key=key):
                changed=dict(by['7CB18APP']); changed[key]=value; self.assertTrue(scientific_issues(changed))
    def test_partial_coincidences_not_complete_duplicates(self):
        a=json.loads((R/'data/curation/archive/source_review_manifest_20261006_b327.json').read_text())
        self.assertEqual((a['canonical_comparisons'],a['LOI_plus_R700_only_hit_groups'],a['complete_paired_profile_duplicates'],a['unresolved_approved_profile_hits']),(63,1,0,0))
        self.assertEqual(a['raw_hit_presentations'],39)
if __name__=='__main__': unittest.main()
