"""Conservative identity and explicit, observation-scoped evidence review.

Matching labels is useful extraction evidence, not proof of identical specimens.
No review fields are inferred from filenames, prose, or numerical completeness.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import unicodedata
from pathlib import Path

try:
    from .source_identity import (PROVENANCE_FIELDS, load_registry, registered_source,
                                  source_gate_issues, provenance_payload, digest, registry_digest)
except ImportError:
    from source_identity import (PROVENANCE_FIELDS, load_registry, registered_source,
                                 source_gate_issues, provenance_payload, digest, registry_digest)

ROOT = Path(__file__).resolve().parents[1]
REVIEWS = ROOT / 'data/curation/pair_reviews.csv'
TG_FIELDS = [
    'T1_C', 'T5_C', 'T10_C', 'T20_C', 'T25_C', 'T30_C', 'T40_C', 'T50_C', 'T75_C', 'T80_C',
    'Tonset_C', 'Tmax1_C', 'Tmax2_C', 'Tmax3_C', 'Tmax4_C',
    'R400_pct', 'R500_pct', 'R550_pct', 'R600_pct', 'R650_pct',
    'R700_pct', 'R750_pct', 'R800_pct', 'residue_pct',
    'residue_at_Tmax_pct', 'residue_at_Tmax1_pct',
    'residue_at_Tmax2_pct', 'residue_at_Tmax3_pct',
]
REVIEW_FIELDS = [
    'pairing_status', 'pairing_evidence', 'material_form_TGA',
    'material_form_LOI', 'numeric_evidence_type', 'evidence_reviewed_by',
    'evidence_reviewed_at', 'source_url', 'source_location',
]


def clean(value):
    if value is None:
        return ''
    text = str(value).strip()
    return '' if text.lower() in {'nan', 'none', '<na>'} else text


def normalize_label(value):
    # Preserve punctuation: A+B, AB and A-B can be different formulations.
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', clean(value))).casefold()


def normalize_doi(value):
    value = normalize_label(value)
    return re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)', '', value).rstrip(' .;,')


def is_network_doi(value):
    return bool(re.fullmatch(r'10\.\d{4,9}/\S+', normalize_doi(value)))


def number(value):
    try:
        result = float(clean(value))
        return result if math.isfinite(result) else None
    except (TypeError, ValueError):
        return None


def normalized_rate(value):
    value_num = number(value)
    return format(value_num, '.12g') if value_num is not None else clean(value)


def normalized_atmosphere(value):
    value = normalize_label(value)
    return {'nitrogen': 'n2', 'n₂': 'n2', 'oxygen': 'o2', 'o₂': 'o2', 'ar': 'argon', 'he': 'helium'}.get(value, value)


def normalized_pair_key(d, s, w, a, r):
    return '||'.join([normalize_doi(d), normalize_label(s), normalize_label(w),
                      normalized_atmosphere(a), normalized_rate(r)])


def source_identity(row):
    """Legacy DOI token, or a registry-approved, namespaced publication token."""
    doi = normalize_doi(row.get('DOI'))
    if doi:
        return doi
    entry, issues = registered_source(row.get('stable_source_id'))
    return 'source:' + entry['stable_source_id'] if entry and not issues else ''


def source_group_key(row):
    """Keep unapproved sources apart without granting them a verified identity."""
    identity = source_identity(row)
    if identity:
        return identity
    stable_id = clean(row.get('stable_source_id'))
    if stable_id:
        return 'pending-source:' + stable_id
    provenance = {field: clean(row.get(field)) for field in
                  ['primary_source_url', 'source_url', 'source_title', 'title', 'source_file']}
    return 'unidentified-source:' + digest(provenance)


def pair_key(row):
    return '||'.join([source_group_key(row), normalize_label(row.get('sample_state')),
                      normalize_label(row.get('washing_state')),
                      normalized_atmosphere(row.get('atmosphere')),
                      normalized_rate(row.get('heating_rate_C_min'))])


def sample_state_id(row):
    return hashlib.sha256('||'.join([source_group_key(row),
        normalize_label(row.get('sample_state')), normalize_label(row.get('washing_state'))]
        ).encode()).hexdigest()[:20]


# Explicitly expanded by the user: fibre-forming polymers and precursors may be
# tested as resin, film or bulk specimens without a claimed textile application.
# Shared specimen form and all ordinary numeric/source review gates still apply.
MATERIAL_SCOPE_CLASSES = {'fiber_forming_polymer', 'textile_precursor_material',
                          'fiber_forming_polymer_composite'}
MATERIAL_SCOPE_FIELDS = ['DOI', 'sample_state', 'washing_state', 'composition',
                         'material_form_TGA', 'material_form_LOI', 'source_title',
                         'source_location', 'source_preparation', 'treatment_state',
                         'material_scope_class', 'source_material_scope_evidence',
                         'source_material_scope_locator']


def material_scope_fingerprint(row):
    payload = {field: clean(row.get(field)) for field in MATERIAL_SCOPE_FIELDS}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def material_scope_review_matches(row):
    return (clean(row.get('material_scope_class')) in MATERIAL_SCOPE_CLASSES
            and all(clean(row.get(field)) for field in
                    ['source_material_scope_evidence', 'source_material_scope_locator',
                     'material_scope_reviewed_by', 'material_scope_reviewed_at'])
            and clean(row.get('reviewed_material_scope_fingerprint')) == material_scope_fingerprint(row))


def measurement_fingerprint(row):
    """A review cannot silently authorize changed numbers or measurement conditions."""
    measurements = {k: normalized_rate(row.get(k)) for k in
                    ['LOI_pct', 'LOI_uncertainty_pct', 'residue_temp_C'] + TG_FIELDS
                    if clean(row.get(k))}
    payload = {'pair_key': pair_key(row), 'measurements': measurements}
    if not normalize_doi(row.get('DOI')):
        payload['source_provenance'] = provenance_payload(row)
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def matching_reviews(row, path=None):
    path = Path(path) if path is not None else REVIEWS
    if not path.exists():
        return []
    key, fingerprint = pair_key(row), measurement_fingerprint(row)
    with path.open(newline='', encoding='utf-8') as handle:
        return [r for r in csv.DictReader(handle)
                if pair_key(r) == key and clean(r.get('measurement_fingerprint')) == fingerprint
                and (normalize_doi(row.get('DOI')) or
                     all(clean(r.get(k)) == clean(row.get(k)) for k in
                         (*PROVENANCE_FIELDS, 'source_url', 'source_location')))]


def non_doi_review_issues(row, path=None, check_metadata=True):
    """Inline flags never replace the explicit non-DOI registry review."""
    issues = source_gate_issues(row)
    matches = matching_reviews(row, path)
    if (len(matches) != 1 or clean(matches[0].get('source_review_approved')) != 'true'
            or clean(matches[0].get('pairing_status')) != 'verified_exact'
            or not all(clean(matches[0].get(k)) for k in
                       ['evidence_reviewed_by', 'evidence_reviewed_at'])):
        issues.append('non_doi_registry_review_pending_or_stale')
    elif check_metadata and any(clean(row.get(k)) != clean(matches[0].get(k)) for k in REVIEW_FIELDS):
        issues.append('non_doi_review_metadata_mismatch')
    return issues


def reviewed_metadata(row, path=None):
    """Only accept one unambiguous, fingerprint-bound review for this observation."""
    non_doi = not normalize_doi(row.get('DOI'))
    matches = matching_reviews(row, path)
    if non_doi and non_doi_review_issues(row, path, check_metadata=False):
        return {'pairing_status': 'pending_source_review', 'reviewed_measurement_fingerprint': ''}
    if len(matches) > 1:
        return {'pairing_status': 'ambiguous_review', 'reviewed_measurement_fingerprint': ''}
    if not matches:
        return {}
    metadata = {k: clean(matches[0].get(k)) for k in REVIEW_FIELDS
                if k not in {'source_url', 'source_location'} or clean(matches[0].get(k))}
    metadata['reviewed_measurement_fingerprint'] = matches[0]['measurement_fingerprint']
    return metadata


def evidence_issues(row):
    """Missing documentation means pending review, never scientific invalidity."""
    doi = normalize_doi(row.get('DOI'))
    reasons = non_doi_review_issues(row) if not doi else []
    if doi and not is_network_doi(doi):
        reasons.append('invalid_doi')
    if doi and clean(row.get('stable_source_id')):
        entry, identity_issues = registered_source(row.get('stable_source_id'))
        unresolved = [issue for issue in identity_issues if issue != 'source_alias_migration_required']
        if (not entry or unresolved or normalize_doi(entry.get('doi_alias')) != doi
                or clean(entry.get('alias_of'))):
            reasons.append('source_doi_mapping_review_required')
    if clean(row.get('reviewed_measurement_fingerprint')) != measurement_fingerprint(row):
        reasons.append('measurement_review_pending_or_stale')
    if clean(row.get('pairing_status')) != 'verified_exact':
        reasons.append('same_state_review_pending')
    for field in ['pairing_evidence', 'evidence_reviewed_by', 'source_url', 'source_location']:
        if not clean(row.get(field)):
            reasons.append('missing_' + field)
    tga, loi = (normalize_label(row.get(k)) for k in ['material_form_TGA', 'material_form_LOI'])
    if not tga or not loi:
        reasons.append('specimen_forms_review_pending')
    elif tga != loi:
        reasons.append('specimen_form_mismatch')
    elif (not re.search(r'\b(?:fabric|textile|fibers?|fibres?|yarn|nonwoven|woven|knitted)\b', tga)
          and not material_scope_review_matches(row)):
        reasons.append('reviewed_specimen_not_textile')
    if clean(row.get('material_scope_class')) and not material_scope_review_matches(row):
        reasons.append('material_scope_review_pending_or_stale')
    if clean(row.get('numeric_evidence_type')) not in {'tabulated', 'explicit_text'}:
        reasons.append('numeric_evidence_review_pending')
    return reasons
