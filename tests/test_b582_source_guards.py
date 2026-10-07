"""Source-bound guards for the three app33113 modified PP sheets."""
import copy
import csv
import json
import unittest
from pathlib import Path

from scripts import pairing

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'data/curation/archive/20261007/source_review_manifest_b582.json'
INCOMING = ROOT / 'data/incoming/verified_source_batch_20261007_b582_local_material.csv'


def check_source_record(row, approved):
    """A changed source quantity or omitted original limitation needs a new review."""
    expected = {r['sample_state']: r for r in approved}
    if row.get('sample_state') not in expected:
        raise ValueError('Unapproved formulation')
    source = expected[row['sample_state']]
    fields = pairing.TG_FIELDS + [
        'LOI_pct', 'composition', 'atmosphere', 'heating_rate_C_min',
        'source_T5_definition', 'source_Tmax_definition', 'source_residue_definition',
        'source_reported_Tonset_C', 'source_LOI_assignment_note',
        'source_TG_mass_mg', 'source_TG_mass_qualifier', 'source_TG_flow_mL_min',
        'source_TG_method', 'source_preparation', 'source_limitations']
    if any(row.get(k, '') != source.get(k, '') for k in fields):
        raise ValueError('Source value or qualification changed')
    if pairing.evidence_issues(row):
        raise ValueError('Missing or stale evidence binding')


class B582SourceGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST.read_text())
        cls.approved = cls.manifest['selected_source_facts']
        cls.rows = list(csv.DictReader(INCOMING.open(newline='')))

    def altered(self, index, field, value):
        row = copy.deepcopy(self.rows[index])
        row[field] = value
        with self.assertRaises(ValueError):
            check_source_record(row, self.approved)

    def test_three_source_rows(self):
        self.assertEqual(len(self.rows), 3)
        for row in self.rows:
            check_source_record(row, self.approved)

    def test_onset_cannot_replace_five_percent_loss(self):
        self.altered(0, 'Tonset_C', '301')

    def test_ten_percent_not_reported(self):
        self.altered(0, 'T10_C', '301')

    def test_loi_cannot_borrow_other_clay_dose(self):
        self.altered(1, 'LOI_pct', '36')

    def test_vmt_assignment_keeps_explicit_delta_and_plateau(self):
        note = self.rows[1]['source_LOI_assignment_note']
        self.assertIn('delta15/base18', note)
        self.assertIn('1-3wt% plateau', note)
        self.altered(1, 'source_LOI_assignment_note', 'Read from unlabelled curve')

    def test_second_dtg_peak_not_other_assay_temperature(self):
        self.altered(0, 'Tmax2_C', '700')

    def test_residue_is_at_reported_temperature(self):
        self.altered(0, 'R600_pct', self.rows[0]['R800_pct'])

    def test_ca_mass_is_not_exact_mass(self):
        self.altered(0, 'source_TG_mass_qualifier', '')

    def test_unknown_flow_not_borrowed(self):
        self.altered(0, 'source_TG_flow_mL_min', '50')

    def test_base_pp_fraction_not_inferred(self):
        self.altered(0, 'composition', 'PP60wt%; APP/PER30wt%; PP-g-MAH10wt%')

    def test_control_and_other_source_stay_outside_selected(self):
        self.altered(0, 'sample_state', 'Pure PP')
        self.assertNotIn('10.1002/app.34428', {r['DOI'] for r in self.rows})

    def test_residue_erratum_keeps_phosphate_and_clay_distinct(self):
        self.assertIn('phosphate', self.rows[0]['source_residue_definition'])
        self.assertNotIn('clay-containing', self.rows[0]['source_residue_definition'])
        self.altered(0, 'source_residue_definition', 'Pure carbon from clay-containing material')


if __name__ == '__main__':
    unittest.main()
