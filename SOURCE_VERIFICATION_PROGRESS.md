# Source verification progress — 2026-09-30

Batch b38 establishes **60 source-reviewed unique DOI/sample/washing states** across **13 papers**, represented by **67 TG condition records**. The near-term target is 500 unique states; 440 remain. The long-term target is 2000.

- **15 genuinely new or newly completed sample-state pairs**: PA56 7; ZnO/MDPA cotton 4; phytic-acid/Cu cotton 2 missing LOIs; ATMP-CS C8.5 1; clay 2TL 1
- **45 existing sample states upgraded with source evidence**, rather than counted as new discoveries
- Original input measurements are preserved. New supplementary/verified readings are in `data/incoming/verified_source_batch_20260930_b38.csv`
- Approval is tied to individual measurement fingerprints in `data/curation/pair_reviews.csv`
- Four phytic-acid numeric/BL sample aliases were adjudicated from methods and column headers. Only the canonical BL states are admitted
- Source contradictions, missing ramps and specimen-form questions are held separately, including air versus oxygen, baseline versus washed LOI, and fabric versus powder

## Continuation

`data/curation/source_review_queue.csv` records per-paper outcomes and next steps. `source_verification_progress.json` gives machine-readable target accounting. Continue with matched primary-source table or explicit-text data and supplementary files; never use plot estimates, LOI ranges or repeated atmospheres to inflate the exact-pair count.

The guarded legacy importer now recovers 180 previously ignored historical numerical candidate rows and quarantines one truncated source row. These recovered rows are not new scientific evidence and are not automatically Grade A. With this batch, the validator reports 454 numerical candidates and 60 source-reviewed sample states.
