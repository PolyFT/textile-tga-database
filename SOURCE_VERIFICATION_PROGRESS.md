# Source verification progress — 2026-09-30

The reviewed dataset contains **141 unique DOI/sample/washing states**, **164 TG condition records**, and **34 papers**. The near-term target is 500 unique states; **359 remain**. The long-term target remains 2000.

## Batches

- b38: 60 reviewed states, represented by 67 TG conditions. Of these, 15 were genuinely new or newly completed pairs and 45 were existing states upgraded with source evidence
- b39: 81 additional reviewed states, represented by 97 TG conditions. Of these, 56 are new-source or newly completed pairs; 25 are existing states upgraded with source evidence or missing conditions
- Cumulative: 71 new/newly completed paired states and 70 existing paired states with upgraded evidence
- Two new cotton candidates lack a reported TG heating rate and remain outside the verified layer

## Scientific safeguards

- All accepted observations have primary-source TG, LOI and method locators, exact specimen/wash-state mapping and fingerprint-bound review
- Original source CSVs remain intact. New extractions and supplementary values are in the b38/b39 incoming files
- Repeated TG atmospheres do not increase the sample-state target count
- Conflicting source values remain absent from clean fields, with the discrepancy preserved in source notes
- Cashmere/alginate source T1max is a water-removal peak. It is stored as water_removal_peak_C; T2–T4 retain original numbering
- TG method start temperatures and standard deviations are typed metadata, not decomposition-temperature metrics
- Unknown heating rates, LOI intervals, specimen-form mismatches and unproven sample aliases are not converted into exact pairs

## Continuation

The guarded legacy importer recovered 180 historical numerical candidates and quarantined one truncated row. These are not new scientific observations and are not automatically Grade A. With b39 the candidate layer has 553 numerical rows, while only 141 unique sample states have the required source review.

`data/curation/source_review_queue.csv` tracks per-paper outcomes; `source_verification_progress.json` records target accounting and the active publication owner. Check current main and any open data PR before starting a new write. Preserve the documented holds and use source-backed crosswalks rather than DOI-only or value-only matching.
