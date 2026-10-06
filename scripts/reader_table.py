"""Deterministic, single-sheet reading view of the admitted TG–LOI master."""
import csv
import io
import re
from pathlib import Path

try:
    from .textile_scope import observation_key
except ImportError:
    from textile_scope import observation_key

HEADERS = ['样品', '材料分类', '材料形态', '组成', '处理／洗涤状态', 'LOI (%)',
           'T5 (℃)', 'T10 (℃)', 'Tonset (℃)', 'Tmax1 (℃)',
           '残余质量（温度:质量%）', 'TG气氛', '升温速率 (℃/min)', '其他TG温度（℃）',
           '制备与处理', 'DOI／来源编号', '文献标题', 'TG页码／表／图', 'LOI页码／表／图',
           '条件证据位置', '限制与不确定性', 'LOI补充（原文）', '气体流量 (mL/min)',
           '样品状态ID', '测试记录ID']
CLASS_NAMES = {'textile_cloth': '织物', 'textile_yarn': '纱线',
               'textile_nonwoven': '非织造布', 'textile_fibre': '纤维',
               'fiber_forming_polymer': '可制纤聚合物',
               'textile_precursor_material': '纺织前驱材料',
               'fiber_forming_polymer_composite': '可制纤聚合物复合材料'}


def value(row, key):
    return row.get(key, '')


def labelled(row, fields):
    return '; '.join(f'{key}={row[key]}' for key in fields if row.get(key, '') != '')


def distinct_values(row, fields):
    return '\n'.join(dict.fromkeys(row[key] for key in fields if row.get(key, '')))


def reading_row(row, entry):
    """Display exact field names; never infer a temperature or rename a peak."""
    other = sorted(key for key in row if re.fullmatch(r'T\d+_C|Tmax[234]_C', key)
                   and key not in {'T5_C', 'T10_C'})
    residual = []
    for key in sorted((key for key in row if re.fullmatch(r'R\d+_pct', key)),
                      key=lambda key: int(key[1:-4])):
        if row[key] != '':
            residual.append(f'{key[1:-4]}℃: {row[key]}%')
    if row.get('residue_pct', '') != '':
        temperature = row.get('residue_temp_C', '')
        residual.append(f'{temperature + "℃" if temperature else "温度未报告"}: {row["residue_pct"]}%')
    for suffix in ['', '1', '2', '3']:
        key = f'residue_at_Tmax{suffix}_pct'
        if row.get(key, '') != '':
            residual.append(f'Tmax{suffix}: {row[key]}%')
    return [value(row, 'sample_state'), CLASS_NAMES.get(entry['scope_class'], entry['scope_class']),
            value(row, 'material_form_TGA'), value(row, 'composition'),
            labelled(row, ['treatment_state', 'washing_state']), value(row, 'LOI_pct'),
            value(row, 'T5_C'), value(row, 'T10_C'), value(row, 'Tonset_C'), value(row, 'Tmax1_C'),
            '; '.join(residual), value(row, 'atmosphere'), value(row, 'heating_rate_C_min'),
            labelled(row, other), distinct_values(row, ['source_preparation', 'treatment_method',
                           'TGA_specimen_preparation', 'LOI_specimen_preparation']),
            row.get('DOI') or row.get('stable_source_id', ''),
            row.get('source_title') or row.get('title', ''),
            row.get('TG_locator') or row.get('TG_source_location') or row.get('source_location', ''),
            row.get('LOI_locator') or row.get('LOI_source_location') or row.get('source_location', ''),
            row.get('conditions_locator') or row.get('conditions_source_location') or row.get('source_location', ''),
            distinct_values(row, ['limitations', 'uncertainty_notes', 'verification_notes',
                                 'onset_definition', 'source_T5_definition', 'source_Tmax_label',
                                 'Tmax1_assignment', 'Tmax2_assignment', 'Tmax3_assignment',
                                 'peak_assignment_note', 'source_residue_phase',
                                 'source_residue_temperature_definition', 'source_TG_scan_range_reported',
                                 'source_Tmax_definition', 'source_Tmax1_definition',
                                 'source_Tmax2_definition', 'source_residue_definition']),
            labelled(row, ['LOI_uncertainty_pct', 'LOI_uncertainty_type', 'LOI_statistic',
                           'LOI_reported_plus_minus', 'LOI_uncertainty_description', 'LOI_n',
                           'LOI_original', 'source_LOI_entry_raw', 'source_LOI_value_raw',
                           'LOI_standard_deviation', 'LOI_replicates', 'LOI_n_reported',
                           'source_LOI_plusminus_pct', 'error_definition', 'source_LOI_error_definition']),
            value(row, 'gas_flow_mL_min'), value(row, 'sample_state_id'), value(row, 'pair_key')]


def csv_bytes(rows, registry):
    entries = {tuple(entry[key] for key in ['source_identity', 'sample_state_id',
               'reviewed_measurement_fingerprint']): entry for entry in registry['entries']}
    buffer = io.StringIO(newline='')
    writer = csv.writer(buffer, lineterminator='\n')
    writer.writerow(HEADERS)
    for row in rows:
        writer.writerow(reading_row(row, entries[observation_key(row)]))
    return buffer.getvalue().encode('utf-8')


def export_reader_table(rows, registry, report, root):
    root = Path(root)
    path = root / 'TG_LOI.csv'
    body = csv_bytes(rows, registry)
    if not path.exists() or path.read_bytes() != body:
        path.write_bytes(body)
    start, end = '<!-- MATERIAL-TABLE-SNAPSHOT:START -->', '<!-- MATERIAL-TABLE-SNAPSHOT:END -->'
    path = root / 'README.md'
    if path.exists() and start in path.read_text():
        block = (f'{start}\n\n已核验并去重的有效样品：**{report["verified_target_sample_states"]}**；'
                 f'TG 测试记录：**{report["verified_target_condition_records"]}**；'
                 f'文献来源：**{report["verified_target_sources"]}**。'
                 f'目标 **{report["target_unique_sample_states"]}** 个样品，'
                 f'尚需 **{report["remaining_to_target"]}** 个。\n\n{end}')
        old = path.read_text()
        new = re.sub(re.escape(start) + '.*?' + re.escape(end), lambda _: block, old, flags=re.S)
        if old != new:
            path.write_text(new)
