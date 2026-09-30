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

ROOT = Path(__file__).resolve().parents[1]
REVIEWS = ROOT / 'data/curation/pair_reviews.csv'
TG_FIELDS = [
    'T1_C', 'T5_C', 'T10_C', 'T20_C', 'T40_C', 'T50_C', 'T80_C',
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
    return {'nitrogen': 'n2', 'n₂': 'n2', 'oxygen': 'o2', 'o₂': 'o2', 'ar': 'argon'}.get(value, value)


def normalized_pair_key(d, s, w, a, r):
    return '||'.join([normalize_doi(d), normalize_label(s), normalize_label(w),
                      normalized_atmosphere(a), normalized_rate(r)])


def pair_key(row):
    return normalized_pair_key(*(row.get(k, '') for k in
        ['DOI', 'sample_state', 'washing_state', 'atmosphere', 'heating_rate_C_min']))


def measurement_fingerprint(row):
    """A review cannot silently authorize changed numbers or measurement conditions."""
    measurements = {k: normalized_rate(row.get(k)) for k in
                    ['LOI_pct', 'LOI_uncertainty_pct', 'residue_temp_C'] + TG_FIELDS
                    if clean(row.get(k))}
    payload = {'pair_key': pair_key(row), 'measurements': measurements}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def reviewed_metadata(row, path=None):
    """Only accept one unambiguous, fingerprint-bound review for this observation."""
    path = Path(path) if path is not None else REVIEWS
    if not path.exists():
        return {}
    with path.open(newline='', encoding='utf-8') as handle:
        matches = [r for r in csv.DictReader(handle)
                   if pair_key(r) == pair_key(row)
                   and clean(r.get('measurement_fingerprint')) == measurement_fingerprint(row)]
    if len(matches) > 1:
        # An ambiguous registry must override any older inline approval.
        return {'pairing_status': 'ambiguous_review', 'reviewed_measurement_fingerprint': ''}
    if not matches:
        return {}
    # Blank/rejected review fields cannot inherit a stale inline approval. Keep
    # original source citations unless the reviewer explicitly supplies new ones.
    metadata = {k: clean(matches[0].get(k)) for k in REVIEW_FIELDS
                if k not in {'source_url', 'source_location'} or clean(matches[0].get(k))}
    metadata['reviewed_measurement_fingerprint'] = matches[0]['measurement_fingerprint']
    return metadata


def evidence_issues(row):
    """Missing documentation means pending review, never scientific invalidity."""
    reasons = []
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
    elif not re.search(r'\b(?:fabric|textile|fibers?|fibres?|yarn|nonwoven|woven|knitted)\b', tga):
        reasons.append('reviewed_specimen_not_textile')
    if clean(row.get('numeric_evidence_type')) not in {'tabulated', 'explicit_text'}:
        reasons.append('numeric_evidence_review_pending')
    return reasons
