import csv
import re
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import reader_table as reader
import textile_scope as scope


REPORT = {'verified_target_sample_states': 1, 'verified_target_condition_records': 1, 'verified_target_sources': 1, 'target_unique_sample_states': 3000}

def payload(body):
    match = re.search(r'<script id="dataset" type="application/json">(.*?)</script>', body.decode(), flags=re.S)
    return json.loads(match.group(1))


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

    def test_source_T70_retains_original_field_and_definition(self):
        row = dict(T30_C='289.8', T50_C='334.8', source_T70_C='472.3',
                   source_T70_definition='temperature at 70% mass loss',
                   source_T75_C='999', Tmax1_C='')
        display = dict(zip(reader.HEADERS, reader.reading_row(
            row, {'scope_class': 'fiber_forming_polymer_composite'})))
        self.assertEqual(display['其他TG温度（℃）'],
                         'T30_C=289.8; T50_C=334.8; source_T70_C=472.3')
        self.assertIn('source_T70_definition=temperature at 70% mass loss',
                      display['限制与不确定性'])
        self.assertEqual(display['Tmax1 (℃)'], '')
        self.assertNotIn('999', str(display))

    def test_ambiguous_source_temperature_is_a_note_not_a_peak(self):
        for raw in ['514', '517', '550']:
            row = dict(source_Tmax_ambiguous_C=raw, source_Tmax_C='999',
                       source_Tmax_definition='maximum label; DTG rate definition unresolved',
                       Tmax1_C='')
            display = dict(zip(reader.HEADERS, reader.reading_row(
                row, {'scope_class': 'fiber_forming_polymer_composite'})))
            self.assertIn('source_Tmax_ambiguous_C=' + raw,
                          display['限制与不确定性'])
            self.assertEqual(display['Tmax1 (℃)'], '')
            self.assertEqual(display['其他TG温度（℃）'], '')
            self.assertNotIn('999', str(display))

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

    def test_original_tg_errors_and_undefined_statistics_are_preserved(self):
        row = dict(T5_C='385', Tmax1_C='410', R700_pct='8.0',
                   source_R700_plusminus_pct='1.2', source_T5_plusminus_C='6.3',
                   source_TGA_unknowns='R700 is measured temperature, not inferred scan end',
                   source_metric_limits='LOI repeat count does not establish TG repeats',
                   source_Tmax_plusminus_C='2.9', source_TG_uncertainty_definition='uncertainty not defined',
                   source_uncertainty_definition='not identified as SD',
                   source_LOI_uncertainty_definition='plus/minus, statistic unspecified',
                   source_LOI_reported_plusminus_pct='0.4', TGA_replicates='3')
        display = reader.reading_row(row, {'scope_class': 'textile_cloth'})
        self.assertEqual(display[6], '385')
        self.assertEqual(display[9], '410')
        self.assertEqual(display[10], '700℃: 8.0%')
        for key in ['source_R700_plusminus_pct', 'source_T5_plusminus_C', 'source_Tmax_plusminus_C',
                    'source_TG_uncertainty_definition', 'source_uncertainty_definition', 'TGA_replicates',
                    'source_TGA_unknowns', 'source_metric_limits']:
            self.assertIn(f'{key}={row[key]}', display[20])
        for key in ['source_LOI_uncertainty_definition', 'source_LOI_reported_plusminus_pct']:
            self.assertIn(f'{key}={row[key]}', display[21])

    def test_html_payload_preserves_source_text_and_unicode(self):
        row = dict(sample_state='Cotton,"A"\n洗涤 </script><img src=x onerror=alert(1)>', DOI='10.1234/中文', LOI_pct='18.0',
                   source_location='p. 3; Table 2', source_title='Title, with comma',
                   atmosphere='N2', heating_rate_C_min='10', washing_state='50 cycles')
        key = scope.observation_key(row)
        entry = dict(zip(['source_identity', 'sample_state_id', 'reviewed_measurement_fingerprint'], key),
                     scope_class='textile_cloth')
        body = reader.page_bytes([row], {'entries': [entry]}, REPORT)
        parsed = payload(body)['rows']
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0][0], row['sample_state'])
        self.assertEqual(parsed[0][15], row['DOI'])
        self.assertEqual(parsed[0][11], 'N2')
        self.assertEqual(parsed[0][12], '10')
        self.assertEqual(parsed[0][18], row['source_location'])
        self.assertNotIn(b'</script><img', body)
        self.assertEqual(body, reader.page_bytes([row], {'entries': [entry]}, REPORT))

    def test_every_reading_record_matches_accepted_master(self):
        with (ROOT / 'data/tg_loi_textile_master.csv').open(newline='') as handle:
            source = list(csv.DictReader(handle))
        registry = json.loads((ROOT / 'data/curation/textile_scope_registry.json').read_text())
        entries = {tuple(entry[key] for key in ['source_identity', 'sample_state_id',
                   'reviewed_measurement_fingerprint']): entry for entry in registry['entries']}
        report = json.loads((ROOT / 'data/automation/textile_scope_report.json').read_text())
        body = reader.page_bytes(source, registry, report)
        public = payload((ROOT / 'index.html').read_bytes())
        expected = [reader.reading_row(row, entries[scope.observation_key(row)]) for row in source]
        self.assertEqual(public['rows'], expected)
        self.assertEqual((ROOT / 'index.html').read_bytes(), body)
        self.assertEqual(len({row[-2] for row in public['rows']}), len({row['sample_state_id'] for row in source}))
        for raw, row in zip(source, public['rows']):
            self.assertEqual(row[5:10], [raw.get(key, '') for key in ['LOI_pct', 'T5_C', 'T10_C', 'Tonset_C', 'Tmax1_C']])
            self.assertEqual(row[11:13], [raw.get(key, '') for key in ['atmosphere', 'heating_rate_C_min']])

    def test_missing_documentary_binding_is_not_silently_exported(self):
        with self.assertRaises(KeyError):
            reader.page_bytes([{'sample_state': 'Unreviewed', 'LOI_pct': '30'}], {'entries': []}, REPORT)

    def test_no_duplicate_page_records_or_stale_front_page(self):
        rows = payload((ROOT / 'index.html').read_bytes())['rows']
        self.assertEqual(len(rows), len({row[24] for row in rows}))
        report = json.loads((ROOT / 'data/automation/textile_scope_report.json').read_text())
        text = (ROOT / 'README.md').read_text()
        self.assertIn(f'**{report["verified_target_sample_states"]}**', text)
        self.assertIn(f'**{report["verified_target_condition_records"]}**', text)
        self.assertIn(f'**{report["target_unique_sample_states"]}**', text)


def show(row):
    return dict(zip(reader.HEADERS, reader.reading_row(row, {'scope_class': 'textile_fibre'})))

class ReaderOriginalMethodTests(unittest.TestCase):
    def test_undefined_initial_temperature_retains_source_value_and_approximation(self):
        for value, qualifier in [('267.5', ''), ('327.2', 'around')]:
            row = dict(source_initial_decomposition_C=value,
                       source_initial_decomposition_qualifier=qualifier,
                       source_initial_definition='loss percent/extrapolation criterion unreported; not T5/T10/Tonset')
            d = show(row)
            self.assertIn('source_initial_decomposition_C=' + value, d['限制与不确定性'])
            if qualifier:
                self.assertIn('source_initial_decomposition_qualifier=around', d['限制与不确定性'])
            self.assertIn(row['source_initial_definition'], d['限制与不确定性'])
            for key in ['T5 (℃)', 'T10 (℃)', 'Tonset (℃)', 'Tmax1 (℃)', '其他TG温度（℃）']:
                self.assertEqual(d[key], '')
            self.assertEqual(row['source_initial_decomposition_C'], value)

    def test_unreviewed_initial_field_is_not_added_to_display_whitelist(self):
        d = show(dict(source_initial_C='999', source_initial_decomposition_C='267.5',
                      source_initial_definition='criterion unreported'))
        self.assertIn('source_initial_decomposition_C=267.5', d['限制与不确定性'])
        self.assertNotIn('999', str(d))

    def test_unknown_temperature_raw_residue_is_qualified_note_only(self):
        d = show(dict(source_raw_residue_pct='1.3',
                      source_residue_temperature_status='Original Table3 temperature unreported; program endpoint is not a binding',
                      TG_end_C='800', source_residue_pct='999'))
        self.assertIn('source_raw_residue_pct=1.3', d['限制与不确定性'])
        self.assertIn('source_residue_temperature_status=Original Table3 temperature unreported', d['限制与不确定性'])
        self.assertEqual(d['残余质量（温度:质量%）'], '')
        self.assertEqual(d['其他TG温度（℃）'], '')
        self.assertNotIn('999', d['限制与不确定性'])

    def test_raw_maximum_label_is_not_a_defined_rate_peak(self):
        for value in ['464.2', '387.0', '380.1', '381.4', '457.6', '461.8']:
            d = show(dict(source_raw_Tmax_C=value, source_Tmax_definition='maximum weight loss temperature; rate criterion unreported', source_Tmax_C='999'))
            self.assertIn('source_raw_Tmax_C=' + value, d['限制与不确定性'])
            self.assertEqual(d['Tmax1 (℃)'], '')
            self.assertEqual(d['其他TG温度（℃）'], '')
            self.assertNotIn('999', str(d))

    def test_conflicted_raw_T70_keeps_two_definitions(self):
        for value in ['442', '466']:
            d = show(dict(source_raw_T70_C=value, source_T70_definition='Methods 70% versus table footnote 10% mass loss; conflict'))
            self.assertIn('source_raw_T70_C=' + value, d['限制与不确定性'])
            self.assertIn('Methods 70% versus table footnote 10%', d['限制与不确定性'])
            self.assertEqual(d['其他TG温度（℃）'], '')
            self.assertEqual(d['T10 (℃)'], '')

    def test_raw_MF_method_retains_approximation_without_filling_canonical_fields(self):
        row = dict(source_TG_flow_mL_min='40', source_TG_mass_mg='6', source_TG_mass_qualifier='About', source_TG_pan='Alumina')
        d = show(row)
        for k,v in row.items(): self.assertIn(k+'='+v, d['限制与不确定性'])
        self.assertEqual(d['气体流量 (mL/min)'], '')
        self.assertEqual(row['source_TG_mass_qualifier'], 'About')

    def test_maximum_mass_loss_rate_and_unit_do_not_become_Tmax(self):
        d = show(dict(max_mass_loss_rate='153.7', rate_unit='%/min', Tmax1_C='294.19'))
        self.assertIn('max_mass_loss_rate=153.7', d['限制与不确定性'])
        self.assertIn('rate_unit=%/min', d['限制与不确定性'])
        self.assertEqual(d['Tmax1 (℃)'], '294.19')
        self.assertNotIn('153.7', d['其他TG温度（℃）'])

    def test_LOI_geometry_and_method_do_not_become_TG_replicates(self):
        row = dict(source_LOI_dimensions_mm='50x6x3', LOI_specimen_geometry='110x55mm', LOI_standard='GB/T5454-1994', LOI_instrument='JF-3', LOI_replicates='9')
        d = show(row)
        for k,v in row.items(): self.assertIn(k+'='+v, d['LOI补充（原文）'])
        self.assertNotIn('LOI_replicates=9', d['限制与不确定性'])

    def test_preparation_context_note_labels_excluded_method_background(self):
        actual = 'PEI6% then PA6% only; one cycle; no LAP/CH'
        background = 'LAP8g+CH0.8g; other study branches'
        note = '本行不采用LAP/CH；其他分支背景不是本行处理'
        d = show(dict(treatment_method=actual, source_preparation=background, source_preparation_scope_note=note))
        self.assertTrue(d['制备与处理'].startswith(actual))
        self.assertIn('文献其他分支的方法背景', d['制备与处理'])
        self.assertIn(background, d['制备与处理'])
        self.assertIn(note, d['制备与处理'])
        self.assertIn(note, d['限制与不确定性'])


class ReaderResidueDisplayTests(unittest.TestCase):
    def test_actual_PA11_same_residue_aliases_display_once(self):
        row=dict(R700_pct='9.6',residue_pct='9.6',residue_temp_C='700')
        original=dict(row)
        self.assertEqual(show(row)['残余质量（温度:质量%）'], '700℃: 9.6%')
        self.assertEqual(row, original)

    def test_different_temperature_and_peak_zero_residues_remain_distinct(self):
        row=dict(R700_pct='0',R800_pct='0',residue_pct='0',residue_temp_C='700',
                 residue_at_Tmax1_pct='0')
        self.assertEqual(show(row)['残余质量（温度:质量%）'],
                         '700℃: 0%; 800℃: 0%; Tmax1: 0%')



class ReaderCottonInitialRawTests(unittest.TestCase):
    def test_real_F0_initial_temperature_keeps_original_value_not_Tonset(self):
        row = dict(sample_state='F0', LOI_pct='18.6', Tmax1_C='339.3',
                   source_raw_initial_decomposition_temperature_C='294.1',
                   source_raw_initial_temperature_definition='starts to decompose; criterion unreported; held raw')
        before = row.copy()
        d = show(row)
        self.assertIn('source_raw_initial_decomposition_temperature_C=294.1', d['限制与不确定性'])
        self.assertIn(row['source_raw_initial_temperature_definition'], d['限制与不确定性'])
        self.assertTrue(all(d[k] == '' for k in ['T5 (℃)', 'T10 (℃)', 'Tonset (℃)']))
        self.assertEqual(d['Tmax1 (℃)'], '339.3')
        self.assertEqual(row, before)

    def test_unapproved_raw_initial_aliases_are_not_generic_peaks(self):
        row = dict(source_raw_initial_C='999', source_initial_temperature_C='998',
                   source_raw_initial_decomposition_temperature_C='294.1',
                   source_raw_initial_temperature_definition='criterion unreported')
        d = show(row)
        self.assertNotIn('999', str(d))
        self.assertNotIn('998', str(d))
        self.assertTrue(all(d[k] == '' for k in ['T5 (℃)', 'T10 (℃)', 'Tonset (℃)', 'Tmax1 (℃)']))

if __name__ == '__main__':
    unittest.main()
