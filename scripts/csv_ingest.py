"""Read source CSVs without letting export wrappers hide entire observation layers.

Only the exact, known single-sheet wrapper is removed. Original files are never
rewritten. Width-invalid records are retained verbatim in an import quarantine.
"""
from __future__ import annotations

import csv
import io
from pathlib import Path

import pandas as pd
try:
    from .pairing import TG_FIELDS
except ImportError:
    from pairing import TG_FIELDS

WRAPPER = '<PARSED TEXT FOR SHEET: 1 / 1 TABS'
LEGACY_ALIASES = {
    'verified_web_batch_20260921.csv': {
        'sample': 'sample_state', 'material': 'material_category',
        'treatment': 'treatment_state', 'direct_numeric': 'direct_numeric_use',
        'title': 'source_title',
    },
}
QUARANTINE_COLUMNS = ['source_file', 'source_row', 'reason_code', 'expected_fields', 'actual_fields', 'raw_record']


def read_source_csv(path, root):
    path, root = Path(path), Path(root)
    source = str(path.relative_to(root))
    with path.open(encoding='utf-8-sig', newline='') as handle:
        raw = handle.read()
    # Preserve CRLF/CR verbatim and do not treat Unicode separators inside
    # quoted cells as physical CSV record lines.
    lines = io.StringIO(raw, newline='').readlines()
    offset = 0
    wrapped = False
    if lines and lines[0].strip() == WRAPPER:
        prefix = 'TAB NAME: ' + path.name + '>'
        if len(lines) < 2 or not lines[1].startswith(prefix):
            raise ValueError(f'{source}: wrapper sheet name/header does not match the source file')
        raw = lines[1][len(prefix):] + ''.join(lines[2:])
        offset = 1
        wrapped = True
    elif lines and lines[0].startswith('<PARSED TEXT FOR SHEET:'):
        raise ValueError(f'{source}: unsupported export wrapper; review the source rather than guess')
    reader = csv.reader(io.StringIO(raw, newline=''), strict=True)
    try:
        columns = next(reader)
    except (StopIteration, csv.Error) as exc:
        raise ValueError(f'{source}: missing or invalid CSV header') from exc
    if len(columns) != len(set(columns)) or any(not col.strip() for col in columns):
        raise ValueError(f'{source}: duplicate/empty CSV header')
    aliases = LEGACY_ALIASES.get(path.name, {})
    effective = set(columns) | {target for origin, target in aliases.items() if origin in columns}
    required = {'DOI', 'sample_state'}
    if path.name == 'scatter_ready.csv':
        required |= {'LOI_pct', 'atmosphere', 'heating_rate_C_min', 'record_id'}
    if not required <= effective or not ({'LOI_pct'} | set(TG_FIELDS)) & effective:
        raise ValueError(f'{source}: unrecognized source schema; missing {sorted(required - effective)} or numerical columns')
    rows, source_rows, quarantine = [], [], []
    previous_line = reader.line_num + offset
    try:
        for row in reader:
            start_line = previous_line + 1
            end_line = reader.line_num + offset
            previous_line = end_line
            if not row:
                continue
            if len(row) != len(columns):
                quarantine.append({
                    'source_file': source, 'source_row': start_line,
                    'reason_code': 'csv_record_width_mismatch',
                    'expected_fields': len(columns), 'actual_fields': len(row),
                    'raw_record': ''.join(lines[start_line - 1:end_line]),
                })
                continue
            rows.append(row)
            source_rows.append(start_line)
    except csv.Error as exc:
        raise ValueError(f'{source}: malformed CSV quoting near line {reader.line_num + offset}; no rebuild published') from exc
    frame = pd.DataFrame(rows, columns=columns)
    applied = {}
    for origin, target in aliases.items():
        if origin in frame and target not in frame:
            frame[target] = frame[origin]  # Retain the original column alongside its documented alias.
            applied[origin] = target
    frame['source_file'] = source
    frame['source_row'] = source_rows
    metadata = {'source_file': source, 'accepted_rows': len(frame),
                'quarantined_rows': len(quarantine), 'wrapper_removed': wrapped,
                'column_aliases': applied}
    return frame, metadata, quarantine
