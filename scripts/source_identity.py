"""Reviewed identities for original, DOI-less sources. No identity is inferred.

DOI normalization and DOI-era keys remain the responsibility of pairing.py.
This registry describes public provenance, never document bytes or observations.
"""
from __future__ import annotations

import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit

REGISTRY = Path(__file__).resolve().parents[1] / 'data/curation/source_registry.json'
SCHEMA_VERSION = 1
PROVENANCE_FIELDS = (
    'stable_source_id', 'source_type', 'publication_identifier',
    'primary_document_version', 'primary_source_url', 'primary_document_sha256',
    'TG_locator', 'LOI_locator', 'conditions_locator',
)
ID_PATTERN = re.compile(r'[a-z][a-z0-9._-]*(?::[a-z0-9][a-z0-9._-]*)+')
SHA256_PATTERN = re.compile(r'[0-9a-f]{64}')


def text(value):
    return value.strip() if isinstance(value, str) else ''


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':')).encode()).hexdigest()


def identity_binding(entry):
    """Review must be regenerated after any identity/provenance/mapping change."""
    return digest({k: v for k, v in entry.items() if k != 'identity_review'})


def valid_url(value):
    if (not isinstance(value, str) or re.search(r'[\s\x00-\x1f\x7f]', value)
            or '\\' in value):
        return False
    try:
        parsed = urlsplit(value)
        port = parsed.port  # Access validates numeric syntax and the allowed port range.
        return (parsed.scheme == 'https' and bool(parsed.hostname)
                and not parsed.username and not parsed.password and not parsed.fragment
                and (port is None or port > 0))
    except ValueError:
        return False


@lru_cache(maxsize=8)
def _parse_registry(raw):
    registry = json.loads(raw)
    if (not isinstance(registry, dict) or registry.get('schema_version') != SCHEMA_VERSION
            or not isinstance(registry.get('sources'), list)
            or any(not isinstance(entry, dict) for entry in registry['sources'])):
        raise ValueError('Unsupported source registry schema; no rebuild published')
    return registry


def load_registry(path=None):
    path = Path(path) if path is not None else REGISTRY
    # Missing registry holds every non-DOI source; malformed registry stops a rebuild.
    return _parse_registry(path.read_bytes()) if path.exists() else {'schema_version': SCHEMA_VERSION, 'sources': []}


def registry_digest():
    return hashlib.sha256(REGISTRY.read_bytes()).hexdigest() if REGISTRY.exists() else ''


def entry_issues(entry):
    issues = []
    if not ID_PATTERN.fullmatch(text(entry.get('stable_source_id'))):
        issues.append('invalid_stable_source_id')
    if entry.get('source_type') != 'original_conference_proceedings':
        issues.append('unsupported_source_type')
    if not text(entry.get('publication_identifier')):
        issues.append('missing_publication_identifier')
    documents = entry.get('documents')
    if not isinstance(documents, list) or not documents:
        issues.append('missing_registered_documents')
    else:
        versions = []
        for document in documents:
            if not isinstance(document, dict):
                issues.append('invalid_registered_document')
                continue
            versions.append(text(document.get('version')))
            aliases = document.get('url_aliases', [])
            if (not versions[-1] or document.get('original_primary') is not True
                    or not valid_url(document.get('primary_source_url'))
                    or not SHA256_PATTERN.fullmatch(text(document.get('primary_document_sha256')))
                    or not isinstance(aliases, list) or any(not valid_url(url) for url in aliases)
                    or len(aliases) != len(set(aliases))):
                issues.append('invalid_registered_document')
        if len(versions) != len(set(versions)):
            issues.append('ambiguous_document_version')
    review = entry.get('identity_review', {})
    if (not isinstance(review, dict) or review.get('approved') is not True
            or not all(text(review.get(k)) for k in ['reviewer', 'reviewed_at', 'evidence'])
            or review.get('binding_sha256') != identity_binding(entry)):
        issues.append('source_identity_review_pending_or_stale')
    return issues


def _reuse_tokens(entry):
    tokens = {('publication', ' '.join(text(entry.get('publication_identifier')).casefold().split()))}
    documents = entry.get('documents', [])
    for document in documents if isinstance(documents, list) else []:
        if isinstance(document, dict):
            tokens.add(('hash', text(document.get('primary_document_sha256'))))
            tokens.add(('url', text(document.get('primary_source_url'))))
            aliases = document.get('url_aliases', [])
            if isinstance(aliases, list):
                tokens.update(('url', text(url)) for url in aliases)
    return {token for token in tokens if token[1]}


def registered_source(stable_id, registry=None):
    """Return one reviewed identity, or explicit reasons to hold it."""
    stable_id = text(stable_id)
    if not stable_id:
        return None, ['missing_stable_source_id']
    if not ID_PATTERN.fullmatch(stable_id):
        return None, ['invalid_stable_source_id']
    registry = load_registry() if registry is None else registry
    matches = [entry for entry in registry['sources'] if entry.get('stable_source_id') == stable_id]
    if len(matches) != 1:
        return None, ['unregistered_stable_source_id' if not matches else 'ambiguous_stable_source_id']
    entry = matches[0]
    issues = entry_issues(entry)
    # Mappings record a curation hold; this schema never changes legacy DOI keys
    # or silently asserts identical sample states across separately assigned IDs.
    if text(entry.get('alias_of')) or text(entry.get('doi_alias')):
        issues.append('source_alias_migration_required')
    own_tokens = _reuse_tokens(entry)
    for other in registry['sources']:
        if other is entry:
            continue
        # A reviewed alias is held itself, while its explicit canonical target
        # remains usable. An unreviewed claim cannot disable this reuse guard.
        if (other.get('alias_of') == stable_id and not entry_issues(other)):
            continue
        if own_tokens & _reuse_tokens(other):
            issues.append('source_identity_reuse_pending')
            break
    return entry, list(dict.fromkeys(issues))


def source_gate_issues(row, registry=None):
    """Bind a DOI-less observation to exactly one reviewed document version."""
    entry, issues = registered_source(row.get('stable_source_id'), registry)
    if entry is None:
        return issues
    issues = list(issues)
    for field in PROVENANCE_FIELDS:
        if not text(row.get(field)):
            issues.append('missing_' + field)
    for field in ['source_type', 'publication_identifier']:
        if text(row.get(field)) != text(entry.get(field)):
            issues.append('registered_' + field + '_mismatch')
    documents = entry.get('documents', [])
    documents = documents if isinstance(documents, list) else []
    matching = [d for d in documents if isinstance(d, dict)
                and d.get('version') == text(row.get('primary_document_version'))]
    if len(matching) != 1:
        issues.append('unregistered_document_version')
    else:
        document = matching[0]
        if row.get('primary_source_url') != document.get('primary_source_url'):
            issues.append('registered_primary_source_url_mismatch')
        if row.get('primary_document_sha256') != document.get('primary_document_sha256'):
            issues.append('registered_document_sha256_mismatch')
        aliases = document.get('url_aliases', [])
        allowed_urls = [document.get('primary_source_url')] + (aliases if isinstance(aliases, list) else [])
        if row.get('source_url') not in allowed_urls:
            issues.append('unregistered_evidence_source_url')
    if not SHA256_PATTERN.fullmatch(text(row.get('primary_document_sha256'))):
        issues.append('invalid_primary_document_sha256')
    return list(dict.fromkeys(issues))


def provenance_payload(row):
    entry, _ = registered_source(row.get('stable_source_id'))
    return {'fields': {field: text(row.get(field)) for field in PROVENANCE_FIELDS},
            'source_url': text(row.get('source_url')),
            'source_location': text(row.get('source_location')),
            'registered_identity_binding': identity_binding(entry) if entry else ''}


def evidence_reuse_tokens(row, *, include_registered=False):
    """Conservative signals for a DOI/non-DOI collision, never an equivalence."""
    tokens = {('id', text(row.get('stable_source_id'))),
              ('hash', text(row.get('primary_document_sha256')))}
    tokens.update(('url', text(row.get(field))) for field in
                  ['primary_source_url', 'source_url', 'fulltext_url', 'additional_fulltext_url'])
    if include_registered:
        entry, issues = registered_source(row.get('stable_source_id'))
        if entry and not issues:
            # Reuse concerns the entire reviewed publication, including other
            # versions/mirrors, not only the document selected by this row.
            tokens.update(_reuse_tokens(entry))
    return {token for token in tokens if token[1]}
