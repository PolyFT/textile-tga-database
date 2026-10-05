#!/usr/bin/env python3
"""Validate numeric ranges, retain review candidates, and build evidence-gated A pairs."""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import pandas as pd
try:
    from .pairing import (TG_FIELDS, clean, evidence_issues, measurement_fingerprint,
                         normalize_doi, normalize_label, normalized_atmosphere, material_scope_review_matches,
                         pair_key, reviewed_metadata, source_identity, source_group_key, sample_state_id)
except ImportError:
    from pairing import (TG_FIELDS, clean, evidence_issues, measurement_fingerprint,
                                normalize_doi, normalize_label, normalized_atmosphere, material_scope_review_matches,
                                pair_key, reviewed_metadata, source_identity, source_group_key, sample_state_id)

try:
    from .csv_ingest import read_source_csv, QUARANTINE_COLUMNS
except ImportError:
    from csv_ingest import read_source_csv, QUARANTINE_COLUMNS

try:
    from .source_identity import REGISTRY, SCHEMA_VERSION, load_registry, evidence_reuse_tokens
except ImportError:
    from source_identity import REGISTRY, SCHEMA_VERSION, load_registry, evidence_reuse_tokens

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
OUT_DIR = DATA / 'automation'
MASTER = DATA / 'tg_loi_master.csv'
REPORT = OUT_DIR / 'validation_report.json'
CANDIDATES = DATA / 'tg_loi_candidates.csv'
QUARANTINE = OUT_DIR / 'pairing_quarantine.csv'
IMPORT_QUARANTINE = OUT_DIR / 'source_import_quarantine.csv'
ISSUES = DATA / 'curation/known_pairing_issues.csv'
README = ROOT / 'README.md'
SNAPSHOT_START = '<!-- TG-LOI-SNAPSHOT:START -->'
SNAPSHOT_END = '<!-- TG-LOI-SNAPSHOT:END -->'
PUBLICATION_TYPES = ('journal_article', 'conference_proceedings', 'author_preprint')
PUBLICATION_TYPE_CATEGORIES = PUBLICATION_TYPES + ('unspecified', 'unrecognized', 'conflicting_metadata')


def num(values):
    return pd.to_numeric(values, errors='coerce')


def input_paths():
    return [DATA / 'scatter_ready.csv'] + sorted((DATA / 'incoming').glob('verified*.csv'))


def load_all():
    frames, imports, quarantine = [], [], []
    for path in input_paths():
        if not path.exists():
            continue
        frame, metadata, rejected = read_source_csv(path, ROOT)
        frames.append(frame)
        imports.append(metadata)
        quarantine.extend(rejected)
    result = pd.concat(frames, ignore_index=True, sort=False).fillna('') if frames else pd.DataFrame()
    result.attrs['source_imports'] = imports
    result.attrs['source_import_quarantine'] = quarantine
    return result


def write_if_changed(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        with path.open(encoding='utf-8', newline='') as handle:
            if handle.read() == text:
                return
    with path.open('w', encoding='utf-8', newline='') as handle:
        handle.write(text)


def issue_list():
    return pd.read_csv(ISSUES, dtype=str).fillna('').to_dict('records') if ISSUES.exists() else []


def known_issues(row, issues):
    result = []
    for issue in issues:
        if clean(issue.get('status')) != 'open':
            continue
        if not normalize_doi(issue.get('DOI')) and not clean(issue.get('stable_source_id')):
            continue  # A blank DOI is never a source-wide issue scope.
        if source_group_key(issue) != source_group_key(row):
            continue
        sample = issue.get('sample_state', '')
        if sample == '*' or normalize_label(sample) == normalize_label(row.get('sample_state')):
            result.append(issue['reason_code'])
    # Explicit source form disagreement is a substantive flag, unlike absent new metadata.
    forms = [normalize_label(row.get(k)) for k in ['material_form_TGA', 'material_form_LOI']]
    if all(forms) and forms[0] != forms[1]:
        result.append('specimen_form_mismatch')
    if 'form_caveat' in clean(row.get('direct_numeric_use')).lower():
        result.append('specimen_form_mismatch')
    return list(dict.fromkeys(result))


def numeric_errors(df):
    errors = []
    for col in [c for c in df if c.startswith('T') and c.endswith('_C')]:
        x = num(df[col])
        bad = x.notna() & (~x.between(20, 1500))
        if bad.any():
            errors.append(f'{col}: {int(bad.sum())} values outside 20–1500 °C')
    for col in [c for c in df if c.endswith('_pct') and
                (c == 'LOI_pct' or c.startswith('R') or 'residue' in c.lower())]:
        x = num(df[col])
        bad = x.notna() & (~x.between(0, 100))
        if bad.any():
            errors.append(f'{col}: {int(bad.sum())} values outside 0–100%')
    return errors


def publication_type_report(master, reviewed_rows):
    """Describe verified sources without changing scientific admission or identity.

    Inspect Grade-A candidate rows for each source before deduplication.
    Missing labels add no assertion; disagreeing nonempty labels are conflicts.
    """
    counts = {kind: {'sources': 0, 'sample_states': 0, 'condition_records': 0}
              for kind in PUBLICATION_TYPE_CATEGORIES}
    sources = {}
    for row in master.to_dict('records'):
        identity = source_identity(row)
        if identity not in sources:
            sources[identity] = {'types': set(), 'states': set(), 'conditions': set()}
        sources[identity]['states'].add(row['sample_state_id'])
        sources[identity]['conditions'].add(row['pair_key'])
    for row in reviewed_rows.to_dict('records'):
        source = sources.get(source_identity(row))
        if source is None:
            continue
        declared = normalize_label(row.get('publication_type'))
        if declared:
            source['types'].add(declared)
        if (not normalize_doi(row.get('DOI'))
                and clean(row.get('source_type')) == 'original_conference_proceedings'):
            source['types'].add('conference_proceedings')
    issues = []
    for identity, source in sorted(sources.items()):
        types = source['types']
        if not types:
            kind = 'unspecified'
        elif len(types) > 1:
            kind = 'conflicting_metadata'
        else:
            declared = next(iter(types))
            kind = declared if declared in PUBLICATION_TYPES else 'unrecognized'
        counts[kind]['sources'] += 1
        counts[kind]['sample_states'] += len(source['states'])
        counts[kind]['condition_records'] += len(source['conditions'])
        if kind in {'unrecognized', 'conflicting_metadata'}:
            issues.append({'source_identity': identity, 'category': kind,
                           'observed_types': sorted(types)})
    preprints = counts['author_preprint']
    return {
        'verified_publication_type_counts': counts,
        'verified_publication_type_metadata_issues': issues,
        'verified_author_preprint_sources': preprints['sources'],
        'verified_author_preprint_sample_states': preprints['sample_states'],
        'verified_author_preprint_condition_records': preprints['condition_records'],
        'publication_type_basis': 'Disjoint existing source identities; metadata from Grade-A candidate rows before deduplication. Pending and quarantined rows cannot classify verified sources. Missing-only types are unspecified; unknown labels are unrecognized; disagreeing nonempty labels are conflicting_metadata. Non-DOI original_conference_proceedings implies conference_proceedings. Author-preprint totals count only sources explicitly marked author_preprint without type conflicts; zero does not establish absence of legacy preprints. DOI presence and Grade A do not establish journal publication or peer review.',
    }


def build_tables(df, issues=None):
    load_registry()  # Fail before publishing if the registry file is malformed.
    df = df.copy().fillna('')
    for col in ['DOI', 'sample_state', 'washing_state', 'atmosphere', 'heating_rate_C_min', 'LOI_pct']:
        if col not in df:
            df[col] = ''
    loi = num(df.LOI_pct)
    tg = pd.Series(False, index=df.index)
    for col in TG_FIELDS:
        if col in df:
            tg |= num(df[col]).notna()
    atm = df.atmosphere.map(clean)
    rate = num(df.heating_rate_C_min)
    # Preserve the old completeness metric independently of the new evidence gate.
    legacy = loi.notna() & tg & df.sample_state.map(clean).ne('') & atm.ne('') & rate.notna()
    if 'direct_numeric_use' in df:
        legacy &= ~df.direct_numeric_use.str.lower().str.contains('tg-only|否|no', regex=True)
    legacy_df = df[legacy].copy()
    legacy_keys = legacy_df.apply(lambda r: '||'.join(clean(r.get(c)) for c in
        ['DOI', 'sample_state', 'washing_state', 'atmosphere', 'heating_rate_C_min']), axis=1)

    doi_evidence = set()
    for original in df[df.DOI.map(normalize_doi).ne('')].to_dict('records'):
        doi_evidence.update(evidence_reuse_tokens(original))
    candidates = df[loi.notna() & tg].copy()
    output = []
    for original in candidates.to_dict('records'):
        row = dict(original)
        row.update(reviewed_metadata(row))
        row['pair_key'] = pair_key(row)
        row['sample_state_id'] = sample_state_id(row)
        row['measurement_fingerprint'] = measurement_fingerprint(row)
        substantive = known_issues(row, issues or [])
        pending = evidence_issues(row)
        if (not normalize_doi(row.get('DOI'))
                and evidence_reuse_tokens(row, include_registered=True) & doi_evidence):
            pending.append('source_doi_reuse_review_required')
        # A complete fingerprint-bound source review can resolve legacy form
        # labels in another language; keep the original descriptive field.
        reviewed_form = normalize_label(row.get('material_form_TGA')) if not pending else ''
        if not normalize_label(row.get('sample_state')):
            pending.append('missing_sample_state')
        if normalized_atmosphere(row.get('atmosphere')) not in {'n2', 'air', 'o2', 'argon', 'helium'}:
            pending.append('missing_or_unresolved_atmosphere')
        rr = pd.to_numeric(row.get('heating_rate_C_min'), errors='coerce')
        if pd.isna(rr) or not 0 < rr < float('inf'):
            pending.append('missing_or_invalid_heating_rate')
        if clean(row.get('direct_numeric_use')).lower() not in {'yes', 'tg+loi', '是'}:
            pending.append('direct_numeric_use_review_pending')
        form = reviewed_form or normalize_label(row.get('material_form'))
        if (not re.search(r'fabric|textile|fiber|fibre|woven|knit|yarn', form)
                and not material_scope_review_matches(row)):
            pending.append('textile_form_review_pending')
        row['pair_quality'] = 'quarantine' if substantive else ('pending_review' if pending else 'A')
        row['review_reasons'] = ';'.join(dict.fromkeys(substantive + pending))
        row['field_complete'] = (
            clean(row.get('sample_state')) != '' and clean(row.get('atmosphere')) != '' and
            pd.notna(pd.to_numeric(row.get('heating_rate_C_min'), errors='coerce')))
        output.append(row)
    result = pd.DataFrame(output)
    if result.empty:
        result = candidates.assign(pair_key='', sample_state_id='', measurement_fingerprint='',
                                   pair_quality='', review_reasons='', field_complete=False)
    # Shared identity with disagreeing overlapping measurements is never silently keep-first.
    conflict_keys = []
    for key, group in result.groupby('pair_key', sort=False):
        if len(group) < 2:
            continue
        for field in ['LOI_pct'] + TG_FIELDS:
            if field in group and num(group[field]).dropna().nunique() > 1:
                conflict_keys.append(key)
                break
    for idx in result.index[result.pair_key.isin(conflict_keys)]:
        result.loc[idx, 'pair_quality'] = 'quarantine'
        result.loc[idx, 'review_reasons'] = ';'.join(filter(None, [result.loc[idx, 'review_reasons'], 'conflicting_measurements']))
    # Retain all input records in candidates/quarantine; deduplicate only the verified analysis view.
    master = result[result.pair_quality.eq('A')].drop_duplicates('pair_key', keep='first').copy()
    quarantine = result[result.pair_quality.eq('quarantine')].copy()
    eligible = result[result.field_complete & ~result.pair_quality.eq('quarantine')]
    doi_master = master[master.DOI.map(normalize_doi).ne('')]
    non_doi_master = master[master.DOI.map(normalize_doi).eq('')]
    report = {
        'report_version': 5,
        'source_identity_schema_version': SCHEMA_VERSION,
        'source_imports': df.attrs.get('source_imports', []),
        'malformed_source_rows_quarantined': len(df.attrs.get('source_import_quarantine', [])),
        'all_loaded_rows': int(len(df)),
        'legacy_field_complete_condition_records': int(legacy_keys.nunique()),
        'numeric_pair_candidate_rows': int(len(result)),
        'eligible_pending_condition_records': int(eligible[eligible.pair_quality.ne('A')].pair_key.nunique()),
        'quarantined_condition_records': int(quarantine.pair_key.nunique()),
        'quarantine_reason_counts': dict(Counter(reason for reasons in quarantine.review_reasons
                                                for reason in reasons.split(';')
                                                if reason in {'possible_sample_alias', 'specimen_form_mismatch', 'conflicting_measurements'})),
        'strict_tg_loi_pairs': int(len(master)),
        'verified_exact_condition_records': int(len(master)),
        'verified_exact_sample_states': int(master.sample_state_id.nunique()),
        'verified_exact_dois': int(doi_master.DOI.map(normalize_doi).nunique()),
        'verified_exact_sources': int(master.apply(source_identity, axis=1).nunique()) if len(master) else 0,
        'verified_non_doi_sources': int(non_doi_master.apply(source_identity, axis=1).nunique()) if len(non_doi_master) else 0,
        'verified_doi_condition_records': int(len(doi_master)),
        'verified_non_doi_condition_records': int(len(non_doi_master)),
        'verified_doi_sample_states': int(doi_master.sample_state_id.nunique()),
        'verified_non_doi_sample_states': int(non_doi_master.sample_state_id.nunique()),
        **publication_type_report(master, result[result.pair_quality.eq('A')]),
        'doi_target_basis': 'evidence-reviewed unique DOI/sample/washing states; multiple TG conditions do not add independent samples',
        'candidate_dois': int(result.DOI.map(normalize_doi).replace('', pd.NA).nunique()),
        'candidate_sample_states': int(result.sample_state_id.nunique()),
        'rows_with_numeric_loi': int(loi.notna().sum()),
        'rows_with_any_tg_numeric': int(tg.sum()),
        'rows_missing_atmosphere_among_pair_candidates': int((loi.notna() & tg & atm.eq('')).sum()),
        'rows_missing_heating_rate_among_pair_candidates': int((loi.notna() & tg & rate.isna()).sum()),
        'target_pairs': 2000,
        'target_basis': 'evidence-reviewed unique source/sample/washing states; multiple TG conditions do not add independent samples',
        'remaining_to_target': max(0, 2000 - int(master.sample_state_id.nunique())),
        'plot_ready_verified_counts': {field: int(num(master[field]).notna().sum()) if field in master else 0
                                       for field in ['Tmax1_C', 'T5_C', 'Tonset_C', 'R600_pct', 'R700_pct', 'R800_pct']},
        'grade_note': 'Missing review metadata means pending documentation, not scientifically invalid. Legacy count is field completeness only. Alias candidates are not automatically merged.',
        'errors': numeric_errors(df),
    }
    return master, result, quarantine, report


def snapshot_digest():
    paths = input_paths() + [REGISTRY, ROOT / 'scripts/source_identity.py', ISSUES, DATA / 'curation/pair_reviews.csv', ROOT / 'scripts/pairing.py', ROOT / 'scripts/validate_tg_loi.py', ROOT / 'scripts/csv_ingest.py']
    digest = hashlib.sha256()
    for path in sorted(paths):
        if path.exists():
            digest.update(str(path.relative_to(ROOT)).encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


def update_readme(report):
    if not README.exists():
        return
    publication_counts = report['verified_publication_type_counts']
    publication_summary = '; '.join(
        f"{kind}: **{publication_counts[kind]['sources']}**" for kind in PUBLICATION_TYPE_CATEGORIES)
    block = '\n'.join([
        SNAPSHOT_START,
        '## Current TG–LOI evidence snapshot', '',
        f"- Legacy field-complete condition records: **{report['legacy_field_complete_condition_records']}** (not a scientific Grade-A count)",
        f"- Numeric TG–LOI candidate rows: **{report['numeric_pair_candidate_rows']}**, across **{report['candidate_dois']} DOI**",
        f"- Field-complete, unflagged condition records awaiting evidence review: **{report['eligible_pending_condition_records']}**",
        f"- Quarantined condition records: **{report['quarantined_condition_records']}**; originals and reasons retained",
        f"- Malformed input CSV records quarantined separately: **{report['malformed_source_rows_quarantined']}**",
        f"- Evidence-reviewed exact Grade-A conditions / sample states: **{report['verified_exact_condition_records']} / {report['verified_exact_sample_states']}**",
        f"- DOI cohort: **{report['verified_exact_dois']} sources / {report['verified_doi_condition_records']} conditions / {report['verified_doi_sample_states']} states**",
        f"- Reviewed non-DOI cohort: **{report['verified_non_doi_sources']} sources / {report['verified_non_doi_condition_records']} conditions / {report['verified_non_doi_sample_states']} states**",
        f"- Overall reviewed sources: **{report['verified_exact_sources']}**; source identity schema **{report['source_identity_schema_version']}**",
        f"- Recorded publication types (disjoint Grade-A source identities): {publication_summary}",
        f"- Sources explicitly marked `author_preprint` (without conflicting type metadata): **{report['verified_author_preprint_sources']} sources / {report['verified_author_preprint_condition_records']} conditions / {report['verified_author_preprint_sample_states']} states**",
        f"- Target: 2000 verified sample states; remaining **{report['remaining_to_target']}**", '',
        'Publication types use explicit `publication_type` metadata on Grade-A candidate rows before deduplication; pending and quarantined rows cannot classify verified sources. Non-DOI `original_conference_proceedings` also identifies conference proceedings. Missing-only labels are `unspecified`; unknown labels are `unrecognized`; disagreeing nonempty labels are `conflicting_metadata`, excluded from the author-preprint subtotal. Blank labels do not contradict an explicit source-level type. DOI presence and Grade-A numerical review do not establish journal publication or peer review.',
        'Unspecified or unrecognized publication types do not invalidate accepted numerical evidence. Zero explicitly marked author-preprint sources does not establish that no legacy source is a preprint.',
        'New author-preprint rows should explicitly record `publication_type=author_preprint` and `source_version`. These reporting fields do not change source identities, fingerprints or the evidence gate.',
        'A missing new review field means pending documentation, not that a legacy measurement is wrong.',
        'Counts are generated together with `data/automation/validation_report.json`; do not edit by hand.',
        f"Snapshot SHA-256: `{report['snapshot_sha256']}`", SNAPSHOT_END])
    text = README.read_text(encoding='utf-8')
    if SNAPSHOT_START in text:
        text = re.sub(re.escape(SNAPSHOT_START) + r'.*?' + re.escape(SNAPSHOT_END), lambda _: block, text, flags=re.S)
    else:
        text = text.rstrip() + '\n\n' + block + '\n'
    write_if_changed(README, text)


def main():
    df = load_all()
    if df.empty:
        raise SystemExit('No input data found')
    master, candidates, quarantine, report = build_tables(df, issue_list())
    report['snapshot_sha256'] = snapshot_digest()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    # Validate before publishing any output. Bad input must not replace the last valid snapshot.
    if report['errors']:
        raise SystemExit(1)
    import_quarantine = pd.DataFrame(df.attrs.get('source_import_quarantine', []), columns=QUARANTINE_COLUMNS)
    for path, frame in [(MASTER, master), (CANDIDATES, candidates), (QUARANTINE, quarantine),
                        (IMPORT_QUARANTINE, import_quarantine)]:
        write_if_changed(path, frame.to_csv(index=False))
    write_if_changed(REPORT, json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    update_readme(report)


if __name__ == '__main__':
    main()
