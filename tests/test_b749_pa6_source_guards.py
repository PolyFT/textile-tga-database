import csv
import json
from pathlib import Path
import unittest

from scripts import pairing

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT/'data/incoming/verified_source_batch_20261007_b749_pa6_material.csv'
MANIFEST = ROOT/'data/curation/archive/20261007/source_review_manifest_b749.json'


class PA6SourceGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with INPUT.open(newline='') as file:
            cls.rows = list(csv.DictReader(file))
        cls.manifest = json.loads(MANIFEST.read_text())

    def test_app46559_original_tables_II_III(self):
        rows = [row for row in self.rows if row['DOI'] == '10.1002/app.46559']
        self.assertEqual([[row[key] for key in ['LOI_pct','T5_C','T10_C','Tmax1_C','R700_pct']] for row in rows], [
            ['23.0','411.4','424.7','473.2','1.04'],
            ['28.0','384.8','407.8','444.2','4.45'],
            ['29.8','385.1','407.8','447.9','7.65'],
            ['31.2','385.1','404.4','447.2','7.80'],
            ['35.5','385.3','404.8','447.8','10.94'],
            ['35.5','385.5','407.8','449.3','13.49']])
        self.assertTrue(all(row['atmosphere']=='N2' and row['heating_rate_C_min']=='20' for row in rows))
        self.assertTrue(all(row['source_T5_definition']=='5 wt% mass loss' and row['source_Tmax_definition']=='temperature of maximum mass loss rate' for row in rows))

    def test_pc23008_original_LOI_and_explicit_R600(self):
        rows = [row for row in self.rows if row['DOI'] == '10.1002/pc.23008']
        self.assertEqual([[row[key] for key in ['LOI_pct','R600_pct','source_raw_Ti_C']] for row in rows], [
            ['24.2','1.01','416.6'],['24.9','1.08','419.0'],['30.9','1.71','414.0'],
            ['31.1','1.82','421.6'],['31.5','2.33','408.3'],['31.7','2.52','416.6']])
        for row in rows:
            self.assertEqual([key for key in pairing.TG_FIELDS if row.get(key)], ['R600_pct'])
            self.assertEqual(row['atmosphere'],'air')
            self.assertEqual(row['heating_rate_C_min'],'10')
            self.assertNotIn('injection',row['material_form_TGA'])
            self.assertIn('unknown',row['material_form_TGA'])

    def test_twelve_state_identity_and_source_bindings(self):
        self.assertEqual(len(self.rows),12)
        self.assertEqual(len({pairing.sample_state_id(row) for row in self.rows}),12)
        self.assertEqual(len({pairing.pair_key(row) for row in self.rows}),12)
        for row in self.rows:
            self.assertEqual(pairing.evidence_issues(row),[])
            self.assertEqual(row['direct_numeric_use'],'yes')
            self.assertEqual(row['reviewed_measurement_fingerprint'],pairing.measurement_fingerprint(row))

    def test_no_PA66_missing_conditions_or_held_source_promoted(self):
        self.assertEqual({row['DOI'] for row in self.rows},{'10.1002/app.46559','10.1002/pc.23008'})
        facts = self.manifest['processed_source_queue_facts']
        self.assertEqual(len(facts),12)
        self.assertEqual(sum(fact['source_pair_approved_states'] for fact in facts),12)
        PA66 = next(fact for fact in facts if fact['DOI']=='10.1016/j.polymdegradstab.2015.03.018')
        self.assertEqual(PA66['source_pair_approved_states'],0)

    def test_six_negative_sources_and_TG_only_weight_loss_remain_zero(self):
        facts = [fact for fact in self.manifest['processed_source_queue_facts'] if fact.get('root_negative_review_complete')]
        self.assertEqual(len(facts),6)
        self.assertTrue(all(fact['source_pair_approved_states']==0 for fact in facts))
        PET = next(fact for fact in facts if fact['DOI']=='10.1039/c6ra05213d')['additional_TG_only_fact']
        self.assertEqual(PET['source_weight_loss_650_pct'],'99')
        self.assertEqual([PET['new_states'],PET['new_TG_conditions']],[0,0])
        self.assertNotIn('R650_pct',PET)


if __name__ == '__main__':
    unittest.main()
