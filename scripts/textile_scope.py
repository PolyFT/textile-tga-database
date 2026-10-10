"""Export original-evidence-admitted textiles from the evidence-reviewed broad master."""
import csv
import hashlib
import io
import json
from pathlib import Path

try:
    from . import pairing
except ImportError:
    import pairing

ROOT = Path(__file__).resolve().parents[1]
SCOPE_FIELDS = ['DOI', 'sample_state', 'washing_state', 'material_form_TGA',
                'material_form_LOI', 'composition', 'source_title', 'source_location',
                'TG_locator', 'LOI_locator', 'conditions_locator', 'pairing_evidence',
                'source_preparation', 'treatment_state', 'source_textile_scope_evidence',
                'source_textile_scope_status', 'material_scope_class',
                'source_material_scope_evidence', 'source_material_scope_locator',
                'reviewed_material_scope_fingerprint']
TEXTILE_CLASSES = {'textile_cloth', 'textile_yarn', 'textile_nonwoven', 'textile_fibre',
                   'textile_composite'}
MATERIAL_CLASSES = TEXTILE_CLASSES | pairing.MATERIAL_SCOPE_CLASSES
DECISIONS = {'admit_textile', 'exclude_non_textile', 'hold_scope'}


def scope_identity_sha256(row):
    payload = {field: row.get(field, '') for field in SCOPE_FIELDS}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':'),
                                    ensure_ascii=True).encode()).hexdigest()


def observation_key(row):
    return (pairing.source_identity(row), pairing.sample_state_id(row),
            row.get('reviewed_measurement_fingerprint', ''))


def classify(rows, registry):
    """No admission by title/form keywords; require the exact manual evidence binding."""
    if registry.get('schema_version') != 2 or registry.get('scope_identity_fields') != SCOPE_FIELDS:
        raise ValueError('Unsupported textile-scope registry schema or identity fields')
    entries = {}
    for entry in registry['entries']:
        key = tuple(entry[field] for field in
                    ['source_identity', 'sample_state_id', 'reviewed_measurement_fingerprint'])
        if key in entries:
            raise ValueError('Duplicate textile-scope observation binding')
        if entry.get('decision') not in DECISIONS:
            raise ValueError('Unknown textile-scope decision')
        for field in ['scope_identity_sha256', 'scope_class', 'scope_review_basis',
                      'scope_evidence', 'source_locator', 'scope_reviewed_by', 'scope_reviewed_at']:
            if not entry.get(field):
                raise ValueError('Missing textile-scope evidence: ' + field)
        if entry['decision'] == 'admit_textile' and entry['scope_class'] not in MATERIAL_CLASSES:
            raise ValueError('Non-textile class cannot be admitted')
        entries[key] = entry
    admitted, seen = [], set()
    state_classes = {}
    decisions, conditions, pending = {}, {key: 0 for key in DECISIONS}, []
    for row in rows:
        if pairing.evidence_issues(row):
            raise ValueError('Textile scope requires an evidence-reviewed master observation')
        key = observation_key(row)
        if key in seen:
            raise ValueError('Duplicate master observation')
        seen.add(key)
        entry = entries.get(key)
        if entry is None:
            pending.append(row)
            continue
        if scope_identity_sha256(row) != entry['scope_identity_sha256']:
            raise ValueError('Stale textile-scope material/state/documentary binding')
        decision = entry['decision']
        state = key[1]
        if state in decisions and decisions[state] != decision:
            raise ValueError('Conflicting textile-scope decisions across TG conditions')
        decisions[state] = decision
        conditions[decision] += 1
        if decision == 'admit_textile':
            scope_class = entry['scope_class']
            if state in state_classes and state_classes[state] != scope_class:
                raise ValueError('Conflicting material classes across TG conditions')
            state_classes[state] = scope_class
            admitted.append(row)
    if set(entries) - seen:
        raise ValueError('Stale textile-scope observation is absent from the reviewed master')
    state_decisions = {key: {state for state, value in decisions.items() if value == key}
                       for key in DECISIONS}
    all_states = {pairing.sample_state_id(row) for row in rows}
    pending_states = all_states - state_decisions['admit_textile'] - state_decisions['exclude_non_textile']
    report = {
        'scope_definition': 'Urban textiles, fibres, source-reviewed fabric/felt-reinforced textile composites, fibre-forming polymers and precursors; matched resin/film/bulk forms may qualify without textile-use prose.',
        'target_unique_sample_states': registry['target_unique_sample_states'],
        'verified_target_sample_states': len(state_decisions['admit_textile']),
        'verified_target_condition_records': len(admitted),
        'verified_target_sources': len({pairing.source_identity(row) for row in admitted}),
        'verified_sample_states_by_material_class': {name: sum(value == name for value in state_classes.values()) for name in sorted(MATERIAL_CLASSES)},
        'verified_condition_records_by_material_class': {name: sum(entries[observation_key(row)]['scope_class'] == name for row in admitted) for name in sorted(MATERIAL_CLASSES)},
        'legacy_counter_aliases': 'verified_textile_* retained as aliases for all admitted target materials; use the material-class breakdown to distinguish finished textiles, textile composites and precursors.',
        'verified_textile_sample_states': len(state_decisions['admit_textile']),
        'verified_textile_condition_records': len(admitted),
        'verified_textile_sources': len({pairing.source_identity(row) for row in admitted}),
        'remaining_to_target': max(0, registry['target_unique_sample_states'] - len(state_decisions['admit_textile'])),
        'excluded_non_textile_sample_states': len(state_decisions['exclude_non_textile']),
        'excluded_non_textile_condition_records': conditions['exclude_non_textile'],
        'pending_scope_sample_states': len(pending_states),
        'pending_scope_condition_records': len(pending) + conditions['hold_scope'],
        'scope_audit_complete': not pending and conditions['hold_scope'] == 0,
        'legacy_broad_sample_states': len(all_states),
        'legacy_broad_condition_records': len(rows),
        'counting_rule': registry['counting_rule'],
        'admission_basis': 'Exact manual scope evidence, material/state/documentary hash and reviewed measurement fingerprint. Pending scope contributes zero to the target.',
    }
    return admitted, report


def main():
    registry_path = ROOT / 'data/curation/textile_scope_registry.json'
    master_path = ROOT / 'data/tg_loi_master.csv'
    with master_path.open(newline='') as handle:
        reader = csv.DictReader(handle)
        columns, rows = reader.fieldnames, list(reader)
    registry = json.loads(registry_path.read_text())
    admitted, report = classify(rows, registry)
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=columns, lineterminator='\n')
    writer.writeheader()
    writer.writerows(admitted)
    output = buffer.getvalue().encode()
    report.update(input_master_sha256=hashlib.sha256(master_path.read_bytes()).hexdigest(),
                  scope_registry_sha256=hashlib.sha256(registry_path.read_bytes()).hexdigest(),
                  textile_master_sha256=hashlib.sha256(output).hexdigest())
    for path, data in [(ROOT / 'data/tg_loi_textile_master.csv', output),
                       (ROOT / 'data/automation/textile_scope_report.json',
                        (json.dumps(report, indent=2) + '\n').encode())]:
        if not path.exists() or path.read_bytes() != data:
            path.write_bytes(data)
    try:
        from .reader_table import export_reader_table
    except ImportError:
        from reader_table import export_reader_table
    export_reader_table(admitted, registry, report, ROOT)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
