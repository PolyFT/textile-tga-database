import csv
import io
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import reader_table as reader
import textile_scope as scope


class ReaderTableTests(unittest.TestCase):
    def test_no_temperature_guessing_or_zero_loss(self):
        row = dict(sample_state='A', LOI_pct='18.0', T5_C='250', T10_C='300',
                   Tonset_C='320', Tmax1_C='350', T30_C='330', Tmax2_C='410',
                   R700_pct='0', residue_pct='7.7', TG_end_C='800',
                   source_Tmax_C='550', source_residue_pct='99')
        display = dict(zip(reader.HEADERS, reader.reading_row(row, {'scope_class': 'textile_cloth'})))
        self.assertEqual(display['LOI (%)'], '18.0')
        self.assertEqual(display['T5 (℃)'], '250')
        self.assertEqual(display['T10 (℃)'], '300')
        self.assertEqual(display['Tonset (℃)'], '320')
        self.assertEqual(display['Tmax1 (℃)'], '350')
        self.assertEqual(display['残余质量（温度:质量%）'], '700℃: 0%; 温度未报告: 7.7%')
        self.assertEqual(display['其他TG温度（℃）'], 'T30_C=330; Tmax2_C=410')
        self.assertNotIn('550', str(display))
        self.assertNotIn('800℃', str(display))

    def test_source_peak_and_residual_definitions_are_preserved(self):
        row = dict(source_Tmax_label='unnumbered Tmax', Tmax2_assignment='PET char oxidation',
                   source_residue_phase='SiO2/Al2O3 solid residue, not pure char',
                   source_residue_temperature_definition='stage end at 497 C',
                   source_TG_scan_range_reported='30–100 C reported; unresolved contradiction',
                   source_T5_definition='5% mass loss includes moisture',
                   source_Tmax2_definition='second peak is oxidative conversion',
                   source_residue_definition='residual mass; not carbon yield')
        display = reader.reading_row(row, {'scope_class': 'textile_cloth'})
        for note in row.values():
            self.assertIn(note, display[20])

    def test_loi_error_definition_and_replicates_are_not_guessed(self):
        row = dict(LOI_pct='27', LOI_standard_deviation='0.2', LOI_replicates='5',
                   LOI_n_reported='5', source_LOI_plusminus_pct='0.3',
                   error_definition='plus/minus reported without statistical definition',
                   source_LOI_error_definition='raw scatter, not standard deviation',
                   source_LOI_entry_raw='about 27')
        display = reader.reading_row(row, {'scope_class': 'textile_cloth'})
        self.assertEqual(display[5], '27')
        for key, note in row.items():
            if key != 'LOI_pct':
                self.assertIn(f'{key}={note}', display[21])

    def test_csv_quoting_preserves_source_text_and_unicode(self):
        row = dict(sample_state='Cotton,"A"\n洗涤', DOI='10.1234/中文', LOI_pct='18.0',
                   source_location='p. 3; Table 2', source_title='Title, with comma',
                   atmosphere='N2', heating_rate_C_min='10', washing_state='50 cycles')
        key = scope.observation_key(row)
        entry = dict(zip(['source_identity', 'sample_state_id', 'reviewed_measurement_fingerprint'], key),
                     scope_class='textile_cloth')
        body = reader.csv_bytes([row], {'entries': [entry]})
        parsed = list(csv.DictReader(io.StringIO(body.decode('utf-8'), newline='')))
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]['样品'], row['sample_state'])
        self.assertEqual(parsed[0]['DOI／来源编号'], row['DOI'])
        self.assertEqual(parsed[0]['TG气氛'], 'N2')
        self.assertEqual(parsed[0]['升温速率 (℃/min)'], '10')
        self.assertEqual(parsed[0]['LOI页码／表／图'], row['source_location'])
        self.assertEqual(body, reader.csv_bytes([row], {'entries': [entry]}))

    def test_every_reading_record_matches_accepted_master(self):
        with (ROOT / 'data/tg_loi_textile_master.csv').open(newline='') as handle:
            source = list(csv.DictReader(handle))
        registry = json.loads((ROOT / 'data/curation/textile_scope_registry.json').read_text())
        entries = {tuple(entry[key] for key in ['source_identity', 'sample_state_id',
                   'reviewed_measurement_fingerprint']): entry for entry in registry['entries']}
        body = reader.csv_bytes(source, registry)
        with (ROOT / 'TG_LOI.csv').open(newline='') as handle:
            public = list(csv.reader(handle))
        expected = [reader.HEADERS] + [reader.reading_row(row, entries[scope.observation_key(row)]) for row in source]
        self.assertEqual(public, expected)
        self.assertEqual((ROOT / 'TG_LOI.csv').read_bytes(), body)
        self.assertEqual(len({row[-2] for row in public[1:]}), len({row['sample_state_id'] for row in source}))
        for raw, row in zip(source, public[1:]):
            self.assertEqual(row[5:10], [raw.get(key, '') for key in ['LOI_pct', 'T5_C', 'T10_C', 'Tonset_C', 'Tmax1_C']])
            self.assertEqual(row[11:13], [raw.get(key, '') for key in ['atmosphere', 'heating_rate_C_min']])

    def test_missing_documentary_binding_is_not_silently_exported(self):
        with self.assertRaises(KeyError):
            reader.csv_bytes([{'sample_state': 'Unreviewed', 'LOI_pct': '30'}], {'entries': []})

    def test_no_duplicate_csv_records_or_stale_front_page(self):
        with (ROOT / 'TG_LOI.csv').open(newline='') as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), len({row['测试记录ID'] for row in rows}))
        report = json.loads((ROOT / 'data/automation/textile_scope_report.json').read_text())
        text = (ROOT / 'README.md').read_text()
        self.assertIn(f'**{report["verified_target_sample_states"]}**', text)
        self.assertIn(f'**{report["verified_target_condition_records"]}**', text)
        self.assertIn(f'**{report["target_unique_sample_states"]}**', text)


if __name__ == '__main__':
    unittest.main()
