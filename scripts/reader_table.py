"""Deterministic, single-page reading view of the admitted TG–LOI master."""
import json
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
    return '; '.join(f'{key}={row[key]}' for key in dict.fromkeys(fields) if row.get(key, '') != '')


def distinct_values(row, fields):
    return '\n'.join(dict.fromkeys(row[key] for key in dict.fromkeys(fields) if row.get(key, '')))


def reading_row(row, entry):
    """Display exact field names; never infer a temperature or rename a peak."""
    error_fields = sorted(key for key in row if re.search(
        r'uncert|plusminus|error|statistic|replicat|deviation|repeats', key, re.I))
    note_fields = sorted(key for key in row if re.search(
        r'unknown|ambiguous|limit|note|definition|assign', key, re.I)
        or key in {'source_residue_phase', 'source_TG_scan_range_reported', 'source_Tmax_label',
                   'source_raw_Tmax_C', 'source_raw_T70_C', 'source_raw_residue_pct',
                   'source_initial_decomposition_C', 'source_initial_decomposition_qualifier',
                   'source_residue_temperature_status', 'source_TG_flow_mL_min',
                   'source_TG_mass_mg', 'source_TG_mass_qualifier', 'source_TG_pan',
                   'max_mass_loss_rate', 'rate_unit', 'source_LOI_dimensions_mm',
                   'LOI_specimen_geometry', 'LOI_standard', 'LOI_instrument'})
    tg_notes = [key for key in note_fields + error_fields if 'LOI' not in key]
    loi_notes = [key for key in note_fields + error_fields if 'LOI' in key]
    other = sorted(key for key in row if (re.fullmatch(r'T\d+_C|Tmax[234]_C', key)
                   or key == 'source_T70_C')
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
    if row.get('source_preparation_scope_note'):
        preparation = distinct_values(row, ['treatment_method', 'TGA_specimen_preparation',
                                             'LOI_specimen_preparation'])
        preparation += '\n' + row['source_preparation_scope_note']
        if row.get('source_preparation'):
            preparation += '\n文献其他分支的方法背景：' + row['source_preparation']
    else:
        preparation = distinct_values(row, ['source_preparation', 'treatment_method',
                                             'TGA_specimen_preparation', 'LOI_specimen_preparation'])
    return [value(row, 'sample_state'), CLASS_NAMES.get(entry['scope_class'], entry['scope_class']),
            value(row, 'material_form_TGA'), value(row, 'composition'),
            labelled(row, ['treatment_state', 'washing_state']), value(row, 'LOI_pct'),
            value(row, 'T5_C'), value(row, 'T10_C'), value(row, 'Tonset_C'), value(row, 'Tmax1_C'),
            '; '.join(dict.fromkeys(residual)), value(row, 'atmosphere'), value(row, 'heating_rate_C_min'),
            labelled(row, other), preparation,
            row.get('DOI') or row.get('stable_source_id', ''),
            row.get('source_title') or row.get('title', ''),
            row.get('TG_locator') or row.get('TG_source_location') or row.get('source_location', ''),
            row.get('LOI_locator') or row.get('LOI_source_location') or row.get('source_location', ''),
            row.get('conditions_locator') or row.get('conditions_source_location') or row.get('source_location', ''),
            labelled(row, tg_notes),
            labelled(row, ['LOI_uncertainty_pct', 'LOI_uncertainty_type', 'LOI_statistic',
                           'LOI_reported_plus_minus', 'LOI_uncertainty_description', 'LOI_n',
                           'LOI_original', 'source_LOI_entry_raw', 'source_LOI_value_raw',
                           'LOI_standard_deviation', 'LOI_replicates', 'LOI_n_reported',
                           'source_LOI_plusminus_pct', 'error_definition', 'source_LOI_error_definition'] + loi_notes),
            value(row, 'gas_flow_mL_min'), value(row, 'sample_state_id'), value(row, 'pair_key')]


def page_bytes(rows, registry, report):
    entries = {tuple(entry[key] for key in ['source_identity', 'sample_state_id',
               'reviewed_measurement_fingerprint']): entry for entry in registry['entries']}
    payload = {'headers': HEADERS,
               'rows': [reading_row(row, entries[observation_key(row)]) for row in rows],
               'meta': {'samples': report['verified_target_sample_states'],
                        'records': report['verified_target_condition_records'],
                        'sources': report['verified_target_sources'],
                        'target': report['target_unique_sample_states']}}
    encoded = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    template = (Path(__file__).parent / 'reader_page.html').read_text()
    return template.replace('__DATASET__', encoded).encode('utf-8')


def export_reader_table(rows, registry, report, root):
    root = Path(root)
    path = root / 'index.html'
    body = page_bytes(rows, registry, report)
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
