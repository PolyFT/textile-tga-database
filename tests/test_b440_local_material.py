"""Source-specific guards: DOI 10.1002/adfm.202410940, PDF pp5-6/10."""
import argparse
import copy
import csv
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / 'data/incoming/verified_source_batch_20261006_b440_local_material.csv'
MANIFEST = ROOT / 'data/curation/archive/20261006/source_review_manifest_b440.json'


def source_supported(row):
    # Approximate prose T5 is valid; MCC and program endpoints are separate assays.
    required = {'DOI': '10.1002/adfm.202410940', 'native_sample_label': 'M-T/ANF',
                'LOI_pct': '47.7', 'T5_C': '453', 'source_T5_qualifier': 'Approximately',
                'atmosphere': 'air', 'heating_rate_C_min': '10'}
    if any(row.get(k, '') != v for k, v in required.items()):
        return False
    if any(row.get(k, '') for k in ['T10_C', 'Tonset_C', 'Tmax1_C', 'Tmax2_C',
            'residue_pct', 'residue_temp_C', 'R600_pct', 'R700_pct', 'R800_pct', 'R900_pct']):
        return False
    definition = row.get('source_T5_definition', '')
    if '5%massloss' not in definition or 'approximately453' not in definition:
        return False
    if row.get('numeric_evidence_type') != 'explicit_text':
        return False
    if row.get('material_form_TGA') != 'aramid nanofiber composite aerogel fibers' or row.get('material_form_LOI') != row.get('material_form_TGA'):
        return False
    if row.get('sample_state') != 'M-T/ANF; initial prepared material':
        return False
    for key in ['source_preparation', 'treatment_method']:
        text = row.get(key, '')
        if 'Composite M-T sol:16gMTES+2.1gTEOS' not in text or 'Composite freeze-dryingduration/temperatureunreported; bulk silica24h notborrowed' not in text:
            return False
    return 'individualfinalSiO2/ANFfractionsunreported' in row.get('composition', '')


class AramidScientificGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with PAYLOAD.open(newline='') as stream:
            cls.rows = list(csv.DictReader(stream))
        cls.manifest = json.loads(MANIFEST.read_text())
        # Bind the inherited single-source guards to this source within the combined bundle.
        cls.rows = [r for r in cls.rows if r['DOI'] == '10.1002/adfm.202410940']
        cls.manifest['scope_entries'] = [e for e in cls.manifest['scope_entries'] if e['source_identity'] == '10.1002/adfm.202410940']
        cls.manifest['processed_source_queue_facts'] = [f for f in cls.manifest['processed_source_queue_facts'] if f['source_review_chain']['primary'] in ['B419', 'B424']]
        cls.row = cls.rows[0]

    def test_original_single_approximate_T5_and_LOI_pair(self):
        self.assertEqual(len(self.rows), 1)
        self.assertTrue(source_supported(self.row))

    def test_approximately_is_not_exact_or_curve_digitisation(self):
        for key, value in [('source_T5_qualifier', ''), ('numeric_evidence_type', 'curve_estimate')]:
            row = copy.deepcopy(self.row); row[key] = value
            self.assertFalse(source_supported(row))

    def test_5percent_definition_not_onset(self):
        row = copy.deepcopy(self.row); row['source_T5_definition'] = 'approximately453C initial temperature; criterion unknown'
        self.assertFalse(source_supported(row))
        row = copy.deepcopy(self.row); row['Tonset_C'] = '453'
        self.assertFalse(source_supported(row))

    def test_MCC_578_and_686_are_not_TG_rate_peaks(self):
        for value in ['578', '686']:
            row = copy.deepcopy(self.row); row['Tmax1_C'] = value
            self.assertFalse(source_supported(row))

    def test_MCC_60p4_and_program900_not_temperature_bound_TG_residue(self):
        row = copy.deepcopy(self.row); row.update(residue_pct='60.4', residue_temp_C='900', R900_pct='60.4')
        self.assertFalse(source_supported(row))
        self.assertEqual(self.row['TG_end_C'], '900')
        self.assertEqual(self.row['residue_pct'], '')

    def test_air10_not_MCC_rate_or_other_assay_N2(self):
        for key, value in [('atmosphere', 'N2'), ('heating_rate_C_min', '1')]:
            row = copy.deepcopy(self.row); row[key] = value
            self.assertFalse(source_supported(row))

    def test_fibre_and_initial_state_not_cloth_or_calcined(self):
        for key, value in [('material_form_TGA', 'fabric'), ('sample_state', 'M-T/ANF; calcined900C1h')]:
            row = copy.deepcopy(self.row); row[key] = value
            self.assertFalse(source_supported(row))

    def test_fibre_sol16_2p1_not_bulk1p6_p21(self):
        row = copy.deepcopy(self.row)
        for key in ['source_preparation', 'treatment_method']:
            row[key] = row[key].replace('16gMTES+2.1gTEOS', '1.6gMTES+0.21gTEOS')
        self.assertFalse(source_supported(row))

    def test_composite_freeze_time_unknown_not_bulk24h(self):
        row = copy.deepcopy(self.row)
        row['source_preparation'] = row['source_preparation'].replace('Composite freeze-dryingduration/temperatureunreported; bulk silica24h notborrowed', 'Composite freeze-dry24h')
        self.assertFalse(source_supported(row))

    def test_group_fraction64_not_individual_sample_composition(self):
        row = copy.deepcopy(self.row); row['composition'] = 'M-T/ANF; retainedSiO2=64wt%'
        self.assertFalse(source_supported(row))

    def test_neat_ANF26p9_or_cited_Kevlar29_not_same_pair(self):
        for value in ['26.9', '29']:
            row = copy.deepcopy(self.row); row.update(LOI_pct=value, native_sample_label='ANF')
            self.assertFalse(source_supported(row))

    def test_source_locations_and_source_document_identity_retained(self):
        self.assertIn('PDFp5', self.row['TG_locator'])
        self.assertIn('PDFp6', self.row['LOI_locator'])
        self.assertIn('PDFp10', self.row['conditions_locator'])
        self.assertEqual(self.row['source_document_sha256'], 'c291ca05f5ec49af0bb8f4cab9e98f24d8c7873f3b67f4aa3d0e2ae418ed62b8')
        self.assertEqual(self.row['source_url'], 'https://doi.org/10.1002/adfm.202410940')

    def test_scope_one_fibre_binding_not_inline_class(self):
        self.assertEqual(self.row['material_scope_class'], '')
        entries = self.manifest['scope_entries']; self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['scope_class'], 'textile_fibre')
        self.assertEqual(entries[0]['decision'], 'admit_textile')

    def test_queue_eight_unique_sources_only_one_new_pair(self):
        facts = self.manifest['processed_source_queue_facts']
        self.assertEqual(len(facts), 8); self.assertEqual(len({r['DOI'] for r in facts}), 8)
        self.assertEqual(sum(r['new_sample_states'] for r in facts), 1)
        self.assertEqual(sum(r['new_TG_records'] for r in facts), 1)
        self.assertEqual(self.manifest['peer_second_count'], 0)

    def test_only_three_audit_fields_superseded(self):
        self.assertEqual({p['field'] for p in self.manifest['audit_metadata_patches']}, {'evidence_reviewed_by', 'material_scope_reviewed_by', 'review_disposition'})
        self.assertTrue(self.manifest['scientific_fields_unchanged'])




def PAN_source_supported(row):
    label = row.get('native_sample_label', '')
    original = {
        'Virgin PAN;untreated fabric': ('18.5', '280', 'around', '58'),
        'DEAEP;as-prepared rinsed fabric': ('22', '235', 'Unqualified reported onset', '61'),
        'DEAMP;as-prepared rinsed fabric': ('22.5', '240', 'Unqualified reported onset', '65'),
        'DMAMP;as-prepared rinsed fabric': ('24.5', '245', 'Unqualified reported onset', '65')}
    if row.get('DOI') != '10.1016/j.surfcoat.2004.11.030' or label not in original:
        return False
    loi, initial, qualifier, residual = original[label]
    fields = {'LOI_pct': loi, 'source_raw_initial_decomposition_C': initial,
              'source_raw_initial_decomposition_qualifier': qualifier,
              'residue_pct': residual, 'residue_temp_C': '650', 'R650_pct': residual,
              'atmosphere': 'argon', 'heating_rate_C_min': '10'}
    if any(row.get(k, '') != value for k, value in fields.items()):
        return False
    if any(row.get(k, '') for k in ['T5_C', 'T10_C', 'Tonset_C', 'Tmax1_C', 'Tmax2_C']):
        return False
    if row.get('source_residue_qualifier') != 'about for treated61/65%;source comparison58% forvirgin unqualified':
        return False
    if label.startswith('Virgin'):
        return row.get('washing_state') == 'Virgin untreated;no coatingprocess inherited' and row.get('source_preparation') == 'Ownvirgin untreated wovenPAN;grafting/plasma/rinse not borrowed'
    composition = row.get('composition', '')
    return all(token in composition for token in ['200g/L monomer bath', '5%(w/w)BAPO', '20%(w/w)EGDA']) and row.get('washing_state') == 'Soxhletethanol/water+RT2d;before accelerated laundering'


class PANScientificGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with PAYLOAD.open(newline='') as stream:
            cls.rows = [r for r in csv.DictReader(stream) if r['DOI'] == '10.1016/j.surfcoat.2004.11.030']
        cls.manifest = json.loads(MANIFEST.read_text())

    def test_four_original_initial_state_PAN_pairs(self):
        self.assertEqual(len(self.rows), 4)
        self.assertTrue(all(PAN_source_supported(r) for r in self.rows))

    def test_raw_initial_values_cannot_fill_threshold_or_rate_peak(self):
        for row in self.rows:
            for key in ['T5_C', 'T10_C', 'Tonset_C', 'Tmax1_C']:
                altered = copy.deepcopy(row); altered[key] = row['source_raw_initial_decomposition_C']
                self.assertFalse(PAN_source_supported(altered))
        altered = copy.deepcopy(self.rows[0]); altered['source_raw_initial_decomposition_qualifier'] = 'exact'
        self.assertFalse(PAN_source_supported(altered))

    def test_R650_about_qualifier_and_control58_precision_retained(self):
        for row in self.rows:
            altered = copy.deepcopy(row); altered['residue_temp_C'] = '800'
            self.assertFalse(PAN_source_supported(altered))
            altered = copy.deepcopy(row); altered['source_residue_qualifier'] = ''
            self.assertFalse(PAN_source_supported(altered))
        self.assertEqual(self.rows[0]['R650_pct'], '58')
        self.assertIn('58% forvirgin unqualified', self.rows[0]['source_residue_qualifier'])

    def test_200gL20EGDA_cannot_borrow_300gL_or10EGDA(self):
        for token, replacement in [('200g/L monomer bath', '300g/L monomer bath'), ('20%(w/w)EGDA', '10%(w/w)EGDA')]:
            row = copy.deepcopy(self.rows[1]); row['composition'] = row['composition'].replace(token, replacement)
            self.assertFalse(PAN_source_supported(row))

    def test_4hour_laundered_LOI_cannot_pair_initial_TG(self):
        row = copy.deepcopy(self.rows[1]); row['washing_state'] = 'after accelerated laundering4h'
        self.assertFalse(PAN_source_supported(row))

    def test_DEMEP_conflict_not_approved_or_aliased_to_DEAEP(self):
        for loi in ['22', '21.5']:
            row = copy.deepcopy(self.rows[1]); row.update(native_sample_label='DEMEP;as-prepared rinsed fabric', LOI_pct=loi)
            self.assertFalse(PAN_source_supported(row))
        fact = next(f for f in self.manifest['processed_source_queue_facts'] if f['DOI'] == '10.1016/j.surfcoat.2004.11.030')
        self.assertIn('DEMEP', fact['scientific_decision'])
        self.assertIn('22 versus', fact['scientific_decision'])
        self.assertIn('21.5 unresolved', fact['scientific_decision'])

    def test_virgin_control_not_inherit_grafting_plasma_process(self):
        row = copy.deepcopy(self.rows[0]); row['source_preparation'] = self.rows[1]['source_preparation']
        self.assertFalse(PAN_source_supported(row))

    def test_twelve_sources_five_new_and_PET_assays_separate(self):
        facts = self.manifest['processed_source_queue_facts']; counts = self.manifest['source_counts']
        self.assertEqual(len(facts), 12)
        self.assertEqual(len({f['DOI'] for f in facts}), 12)
        self.assertEqual(sum(f['candidate_unique_states'] for f in facts), 5)
        self.assertEqual(sum(f['candidate_TG_records'] for f in facts), 5)
        self.assertEqual(counts['original_series_physical_observations'], 75)
        self.assertEqual(counts['selected_conditions'], 5)
        self.assertEqual(counts['nonadmitted_conditions'], 70)
        self.assertEqual(counts['PET_separate_assays'], 18)
        self.assertEqual(counts['PET_correspondence_views'], 13)
        self.assertEqual(counts['PET_added_series_conditions'], 0)
        self.assertEqual(next(f['candidate_unique_states'] for f in facts if f['DOI'] == '10.1007/s12221-011-0166-5'), 0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--payload', type=Path, default=PAYLOAD)
    parser.add_argument('--manifest', type=Path, default=MANIFEST)
    args, rest = parser.parse_known_args()
    PAYLOAD, MANIFEST = args.payload, args.manifest
    unittest.main(argv=[sys.argv[0], *rest], verbosity=2)
