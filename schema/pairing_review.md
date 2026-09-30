# Exact pairing review contract

## Layers and migration

- Original incoming and workbook CSVs are unchanged source records
- `tg_loi_candidates.csv` is a reproducible all-numeric-pair review view, preserving source file/row and original numbers
- `pairing_quarantine.csv` repeats flagged candidate records with machine-readable reasons. It is not deletion, numerical correction or adjudication of duplicate aliases
- `tg_loi_master.csv` contains only Grade-A observations with explicit, fingerprint-bound evidence review
- Empty Grade A after the initial migration means the new review registry has not yet been populated. It does not establish that historical observations are scientifically invalid

## Reviewing a candidate

Copy the candidate's DOI, sample_state, washing_state, atmosphere, heating_rate_C_min and measurement_fingerprint into `data/curation/pair_reviews.csv`. Use exactly one matching record. Re-read the relevant original tables/text/methods and provide:

- `pairing_status`: `verified_exact` only after checking that TGA and LOI concern the same formulation, physical form, treatment and washing state
- `pairing_evidence`: concrete explanation of the mapping, including original labels, same-form/state evidence, and table/text positions. A DOI-wide blanket approval is insufficient
- `material_form_TGA` and `material_form_LOI`: the actual specimen forms, using the same precise value only when equivalent; fiber and woven fabric are different
- `numeric_evidence_type`: `tabulated` or `explicit_text`. Graph estimates, inferred typo corrections, ranges and thresholds require separate review layers and cannot be promoted here
- `evidence_reviewed_by`: actual reviewer identity, never populated by the parser
- `evidence_reviewed_at`: review date
- `source_url` and `source_location`: retrievable source and exact table/figure/section/page references supporting numbers, methods, and mapping

The measurement fingerprint includes normalized observation identity, LOI, uncertainty, TG numerical values and residue temperature. A changed measurement, wash state, atmosphere or rate cannot reuse approval. Missing/duplicate registry matches do not grant new approval. Inline review metadata must carry the original `reviewed_measurement_fingerprint`; it becomes stale if values change.

Open records in `known_pairing_issues.csv` remain quarantined even if a review is supplied. Resolve an issue only after source evidence establishes the mapping/correction, retaining details and source provenance. For alias candidates, do not merge on matching numbers alone. For the PAN/PVA issue, chemistry matching does not establish identical physical form and a suspected typo is not an exact number.

## Identity and counting

Normalization casefolds Unicode and collapses whitespace, retains sample punctuation, normalizes DOI prefixes and numeric heating rate, and keeps wash state in every pair key. A+B, A-B and AB remain distinct. Missing wash state is unknown rather than assumed unwashed; an exact-state reviewer must resolve it in the evidence.

Report condition records, DOI count, sample-state combinations and per-variable plot counts separately. The provisional target uses verified DOI/sample/washing combinations, not repeated atmospheres/rates. This does not prove statistical independence: avoid pooled correlations and pseudoreplication, and cluster by source/sample where appropriate.

## Local verification

`python -m unittest discover -s tests -v` runs fixture-based hard-bug, cache, fingerprint, conservative-identity, quarantine and failure-safe rebuild regressions. `python scripts/validate_tg_loi.py` regenerates candidates, quarantine, master, JSON report and README snapshot in one pass. No raw source CSV is overwritten.
