import csv
import io
import tempfile
import unittest
from pathlib import Path

import pandas as pd
from scripts.csv_ingest import read_source_csv, WRAPPER
from scripts import validate_tg_loi as v

HEADER = ['record_id', 'DOI', 'sample_state', 'atmosphere', 'heating_rate_C_min', 'Tmax1_C', 'LOI_pct']
ROW = ['TG1', '10.1234/example', 'A', 'N2', '10', '340', '25']


def contents(rows):
    out = io.StringIO()
    csv.writer(out, lineterminator='\n').writerows(rows)
    return out.getvalue()


class CsvImportTests(unittest.TestCase):
    def write(self, root, name, content):
        path = Path(root) / name
        path.write_text(content)
        return path

    def test_known_wrapper_is_recovered_without_rewriting_original(self):
        raw = WRAPPER + '\nTAB NAME: scatter_ready.csv>' + contents([HEADER, ROW])
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(tmp, 'scatter_ready.csv', raw)
            frame, meta, rejected = read_source_csv(path, tmp)
            self.assertEqual(path.read_text(), raw)
            self.assertEqual(frame.iloc[0].DOI, '10.1234/example')
            self.assertEqual(frame.iloc[0].source_row, 3)
            self.assertTrue(meta['wrapper_removed'])
            self.assertEqual(rejected, [])
            self.assertNotIsInstance(frame.index, pd.MultiIndex)
            master, candidates, _, _ = v.build_tables(frame)
            self.assertTrue(master.empty)
            self.assertEqual(len(candidates), 1)

    def test_short_and_long_records_retained_verbatim_in_quarantine(self):
        short = contents([ROW[:-2]])
        long = contents([ROW + ['extra']])
        raw = contents([HEADER, ROW]) + short + long
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(tmp, 'scatter_ready.csv', raw)
            frame, meta, rejected = read_source_csv(path, tmp)
            self.assertEqual(len(frame), 1)
            self.assertEqual(meta['quarantined_rows'], 2)
            self.assertEqual([r['source_row'] for r in rejected], [3, 4])
            self.assertEqual([r['raw_record'] for r in rejected], [short, long])
            self.assertEqual(path.read_text(), raw)

    def test_actual_wrapped_baseline_and_truncated_last_row(self):
        root = Path(__file__).resolve().parents[1]
        source = root / 'data/scatter_ready.csv'
        before = source.read_bytes()
        frame, meta, rejected = read_source_csv(source, root)
        self.assertEqual(len(frame), 570)
        self.assertEqual(meta['quarantined_rows'], 1)
        self.assertEqual(rejected[0]['expected_fields'], 47)
        self.assertEqual(rejected[0]['actual_fields'], 45)
        self.assertIn('CTG0362', rejected[0]['raw_record'])
        self.assertEqual(source.read_bytes(), before)
        self.assertIn('DOI', frame)
        self.assertGreater(pd.to_numeric(frame.Tmax1_C, errors='coerce').notna().sum(), 0)

    def test_legacy_aliases_are_explicit_and_original_columns_retained(self):
        head = ['DOI', 'sample', 'title', 'direct_numeric', 'material', 'Tmax1_C', 'LOI_pct']
        row = ['10.1234/x', 'A', 'Title', 'yes', 'cotton fabric', '340', '25']
        raw = WRAPPER + '\nTAB NAME: verified_web_batch_20260921.csv>' + contents([head, row])
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(tmp, 'verified_web_batch_20260921.csv', raw)
            frame, meta, rejected = read_source_csv(path, tmp)
            self.assertEqual(frame.iloc[0].sample_state, frame.iloc[0]['sample'])
            self.assertEqual(frame.iloc[0].direct_numeric_use, 'yes')
            self.assertNotIn('material_form', frame)
            self.assertEqual(meta['column_aliases']['sample'], 'sample_state')
            self.assertEqual(rejected, [])

    def test_single_column_or_missing_expected_schema_fails(self):
        for raw in ['wrong\n1,2,3\n', contents([['DOI', 'sample_state'], ['10.1/x', 'A']]), contents([HEADER[:-1], ROW[:-1]])]:
            with self.subTest(raw=raw), tempfile.TemporaryDirectory() as tmp:
                path = self.write(tmp, 'scatter_ready.csv', raw)
                with self.assertRaises(ValueError):
                    read_source_csv(path, tmp)

    def test_wrong_sheet_unknown_wrapper_duplicate_header_and_bad_quotes_fail(self):
        cases = [WRAPPER + '\nTAB NAME: other.csv>' + contents([HEADER, ROW]),
                 '<PARSED TEXT FOR SHEET: 2 / 2 TABS\n' + contents([HEADER, ROW]),
                 contents([HEADER + ['DOI'], ROW + ['10.1/a']]),
                 contents([HEADER]) + '"unterminated\n']
        for raw in cases:
            with self.subTest(raw=raw), tempfile.TemporaryDirectory() as tmp:
                path = self.write(tmp, 'scatter_ready.csv', raw)
                with self.assertRaises(ValueError):
                    read_source_csv(path, tmp)

    def test_crlf_quarantine_is_verbatim_and_unicode_separators_are_data(self):
        row = ROW.copy()
        row[2] = 'A\u2028B'
        raw = contents([HEADER, row, ROW[:-2]]).replace('\n', '\r\n')
        expected_short = contents([ROW[:-2]]).replace('\n', '\r\n')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'scatter_ready.csv'
            path.write_bytes(raw.encode())
            frame, _, rejected = read_source_csv(path, tmp)
            self.assertEqual(frame.iloc[0].sample_state, 'A\u2028B')
            self.assertEqual(rejected[0]['source_row'], 3)
            self.assertEqual(rejected[0]['raw_record'], expected_short)
            self.assertEqual(path.read_bytes(), raw.encode())

    def test_quarantine_output_preserves_crlf_and_rebuild_is_noop(self):
        raw_record = contents([ROW[:-2]]).replace('\n', '\r\n')
        frame = pd.DataFrame([{'raw_record': raw_record}])
        serialized = frame.to_csv(index=False)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'quarantine.csv'
            v.write_if_changed(path, serialized)
            stamp = path.stat().st_mtime_ns
            v.write_if_changed(path, serialized)
            self.assertEqual(path.stat().st_mtime_ns, stamp)
            with path.open(newline='') as handle:
                self.assertEqual(next(csv.DictReader(handle))['raw_record'], raw_record)

    def test_multiline_fields_keep_physical_source_row(self):
        first = ROW.copy()
        first[2] = 'A\nmultiline'
        raw = contents([HEADER, first, ROW])
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(tmp, 'scatter_ready.csv', raw)
            frame, _, rejected = read_source_csv(path, tmp)
            self.assertEqual(frame.source_row.tolist(), [2, 4])
            self.assertEqual(frame.iloc[0].sample_state, 'A\nmultiline')
            self.assertEqual(rejected, [])


if __name__ == '__main__':
    unittest.main()
