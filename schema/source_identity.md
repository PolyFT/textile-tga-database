# Reviewed non-DOI primary sources (schema 1)

This opt-in extension supports original conference proceedings that have no DOI. It does not add observations. `data/curation/source_registry.json` starts with an empty `sources` array. Missing, rejected, ambiguous or stale reviews hold the observation outside Grade A.

## Publication registry

Keep DOI blank for a DOI-less publication. Never put a URL, proceedings identifier or synthetic token in the DOI column. Assign one lowercase, colon-namespaced `stable_source_id`, such as `proceedings:publisher.example:conference:year:paper-id`. It identifies a publication, not a sample, URL or document revision.

Each registry entry contains:

- `stable_source_id`
- `source_type`: exactly `original_conference_proceedings` in this narrow schema
- `publication_identifier`: the official paper identifier and complete citation (title, authors, year, venue and pages)
- `documents`: explicit document versions, each with a unique `version`, `original_primary: true`, an HTTPS `primary_source_url`, a lowercase 64-hex `primary_document_sha256`, and optional `url_aliases`
- `identity_review`: `approved: true` as a JSON boolean, actual `reviewer`, `reviewed_at`, substantive `evidence`, and `binding_sha256`

A reviewer must check that the URL is the original publisher or conference document, that the citation identifies it unambiguously, and that the SHA-256 describes the exact inspected bytes. Official origin is a human evidence finding, not something the URL syntax check can establish. Keep full texts outside this repository. The registry stores public citation, URL, hash and review metadata only.

`binding_sha256` is computed by `scripts.source_identity.identity_binding(entry)` over every entry field except `identity_review`, using sorted, compact, UTF-8 JSON. It is a deterministic change detector, not a digital signature. Changing any citation, document version, hash, URL, mirror or mapping requires another identity review. New versions must be explicit members of `documents`; an unknown version never inherits review.

## Observation and pairing review

A DOI-less source row must contain the following fields, and the matching row in `pair_reviews.csv` must copy all of them exactly:

- `stable_source_id`, `source_type`, `publication_identifier`
- `primary_document_version`, `primary_source_url`, `primary_document_sha256`
- `TG_locator`, `LOI_locator`, `conditions_locator`: precise original pages, table/text positions, sample labels and numeric columns or assay-method locations
- Existing `source_url` and `source_location`

`primary_source_url` remains the registered original URL. `source_url` may be the original URL or an explicitly registered mirror for those same document bytes. A mirror needs its own exact observation review if its source URL differs.

All existing sample/form/washing, TG atmosphere/ramp and numerical evidence gates still apply. The pair review must additionally set `source_review_approved` to the exact CSV string `true`, include `evidence_reviewed_at`, and carry the matching `measurement_fingerprint`. An inline approval cannot bypass this lookup, even if it supplies a freshly calculated fingerprint. Blank or false approval, missing review, duplicate review, mismatched review metadata, changed source provenance, changed locators and changed scientific values all remain held.

The non-DOI fingerprint includes the existing normalized measurements and condition key, every required provenance field, source URL/location and the registered identity binding. Existing DOI fingerprints, DOI state IDs and `normalized_pair_key(d, s, w, a, r)` are unchanged.

## Aliases and reuse holds

One publication's reviewed mirrors stay under one stable ID. Multiple conditions contribute condition records but only one source/sample/washing state. Exact duplicate pair keys are counted once, while conflicting overlapping measurements remain quarantined.

Reuse of a document hash, original or mirror URL, or normalized publication citation under another stable ID is held. If curators establish that an alternate ID is an alias, record an explicitly reviewed `alias_of` mapping. The alias remains held for deliberate migration; its canonical target remains usable. This implementation never guesses sample-label equivalence or changes a legacy DOI identity.

For a later DOI, an explicitly reviewed `doi_alias` mapping holds the old non-DOI entry. Any DOI row carrying that stable ID must match the mapping before admission. A collision between DOI and non-DOI input provenance also holds the non-DOI record until reviewed. This includes exact original/source/full-text/additional-full-text URLs, document hashes and stable IDs, including older DOI rows without the new provenance fields. For a non-DOI publication, the collision check includes every original URL, mirror URL and document hash in its reviewed registry entry, including versions not selected by that particular observation. These are conservative hold signals, not inferred equivalence. No automatic copying, reassignment of sample states, or migration is performed; adding the separately reviewed DOI observation is a later curation action.

Known issues use DOI for DOI sources and `stable_source_id` for DOI-less sources. A blank DOI with no stable ID is not a valid source-wide issue scope.

## Processing and reporting

The validator loads the registry before rebuilding and includes its bytes and implementation in the deterministic snapshot digest. Malformed registry JSON/schema fails before output publication; unapproved or invalid individual entries produce pending reasons. The normal source CSV import still requires the DOI column, whose values may now be blank under this reviewed path.

Grade-B grouping and master deduplication use row-based source identity. DOI-only network extraction skips DOI-less and synthetic-DOI rows and leaves them for manual review. A source registry change also invalidates extraction/review cache fingerprints.

Report version 4 keeps `verified_exact_dois` restricted to nonblank normalized DOI, and separately reports:

- `verified_exact_sources`, `verified_non_doi_sources`
- `verified_doi_condition_records`, `verified_non_doi_condition_records`
- `verified_doi_sample_states`, `verified_non_doi_sample_states`

Overall verified counts equal the disjoint DOI and non-DOI cohorts. `target_basis` uses reviewed source/sample/washing states; `doi_target_basis` retains the historical DOI-cohort definition. These state counts are not proof of statistically independent replicates.
