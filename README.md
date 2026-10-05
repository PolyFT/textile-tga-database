# Textile TGA Database

Research database for textile thermal-response / thermogravimetric data, with LOI as a principal fire-performance label.

## Historical imported workbook snapshot (2026-09-21)

- Literature TG records: 209
- Commercial / branded / city-use textile TG records: 430
- Unified scatter-ready rows: 639
- Rows with LOI: 242
- Rows with both Tmax1 and LOI: 122
- Rows with both residue and LOI: 98

Snapshot source: `纺织品文献基准数据_持续扩展_430条TG_20260921.xlsx`.

## Data organization

`data/literature_tg.csv`  
Original literature TG record layer.

`data/commercial_tg.csv`  
Commercial/branded/city-use textile TG layer.

`data/scatter_ready.csv`  
Normalized analysis table for paper figures. Literature and commercial records are kept distinguishable by `dataset_type`.

`data/candidate_pool.csv` and `data/priority_download.csv`  
Discovery / extraction queue. These are not treated as confirmed numerical observations until verified.

Other CSVs preserve sample, source, product, LOI, procurement and source-index layers from the workbook.

## Figure policy

The paper-facing analysis should use scatter plots rather than treating every row as directly comparable. Always stratify or filter by:
- atmosphere,
- heating rate,
- material category / form,
- literature vs commercial source,
- evidence / numerical usability.

Recommended first analyses:
1. `Tmax1_C` vs `LOI_pct`
2. `residue_pct` vs `LOI_pct`, with residue temperature controlled
3. `Tonset_C` vs `LOI_pct`
4. Within-category / within-condition subsets rather than pooled correlations

Do not pool N2 and air measurements without explicit labeling or stratification.

## Update rule

CSV is the source of truth. Each new batch should:
1. add/verify sources,
2. append sample-state rows,
3. append TG/LOI observations,
4. run the evidence-gated rebuild for candidates, quarantine and strict master,
5. commit with a batch-specific message.

PDFs are not stored here unless redistribution is clearly permitted; use DOI/URL and source-location fields for provenance.

## Collection progress — 2026-09-21

Baseline normalized snapshot: 639 TG observations.

Incoming verified staging now extends through **B20260921-205**, for **205 additional observations**. These are a mixture of:
- exact TGA–LOI paired observations,
- TG-only observations retained when LOI is absent or not reliably measurable,
- condition-partial observations whose numerical TGA/LOI values are explicit but one TGA condition field is missing,
- commercial / application-relevant textile records kept distinct from laboratory-only systems.

Recent high-value additions include commercial furnishing fabrics, mattress ticking with commercial flame retardants, automotive-interior PET, PA6,6 technical textiles, wool, silk, lyocell, PAN, polypropylene nonwoven, and multiple PET/cotton blend constructions.

Paper-facing scatter plots should use only rows with exact sample-state matching between TGA and LOI, then stratify by atmosphere, heating rate, material class and evidence level. TG-only rows remain useful for the thermal-response landscape but are not used as TGA–LOI correlation points.

Additional candidate queues contain PA6/PA66/PET/viscose/lyocell/cuprammonium/Nylon56 sources that remain outside the main paired layer until TGA conditions and exact sample-state mapping are resolved.

## TG–LOI processing and evidence review

Discovery is configured hourly at minute 17 UTC and processing at `*/10` UTC.
GitHub scheduling can be delayed; configured cadence is not a throughput guarantee.

Data flow:

1. OpenAlex and open-source discovery write `data/automation/candidate_extractions.csv`
2. Extraction and the Grade-B condition pass retain numeric matches and source evidence in `data/automation/auto_extracted.csv`, `review_queue.csv`, and `b_review_resolved.csv`
3. Original `data/scatter_ready.csv` and `data/incoming/verified*.csv` remain source records. A `verified` filename is not itself scientific verification
4. Validation writes all numeric pairing candidates to `data/tg_loi_candidates.csv`; known form conflicts, unresolved aliases, and conflicting duplicate values also appear in `data/automation/pairing_quarantine.csv`
5. Only individually evidence-reviewed exact observations enter `data/tg_loi_master.csv` as Grade A

### Source import safeguards

The validator recognizes only the exact existing single-sheet export wrapper, validates the expected column schema, and records wrapper/alias recovery in the JSON report. The original source files are unchanged. Width-invalid records are retained verbatim in `data/automation/source_import_quarantine.csv` and excluded from numeric analysis; unknown wrappers and invalid schemas fail the rebuild. Recovered historical rows are not new literature discoveries and are not automatically Grade A.

### Grade-A admission

Matching labels and complete numerical fields are necessary but insufficient. A reviewer must document the exact same material formulation, physical form, treatment and washing state for the TGA and LOI observations, exact numeric evidence, and concrete source/table/method locations. The same normalized DOI/sample/washing/atmosphere/rate key and measurement fingerprint bind the review to the observation. Changes to measurements require another review.

Record reviews in `data/curation/pair_reviews.csv`; see `schema/pairing_review.md`. No review is fabricated during migration. Missing newly introduced metadata means **pending documentation**, not a conclusion that legacy data are wrong. Known concerns are listed separately in `data/curation/known_pairing_issues.csv`, with both aliases retained until source mapping is resolved. Shared sample labels preserve punctuation; physical-form, washing-state and sample-alias equivalence is never guessed.

The 2000-pair target is reported as reviewed source/sample/washing-state combinations, separately from measurement-condition counts. DOI and reviewed non-DOI source, condition and state counts are reported separately. It is a provisional reporting definition for review, not a claim that every such combination is an independent experimental replicate. All plots must still stratify atmosphere, heating rate, material form and residue temperature and account for clustering by paper/sample.

Original proceedings without DOI may use the empty-by-default [reviewed source registry](schema/source_identity.md). This route requires an explicitly approved publication identity, original document hash/URL, exact TG/LOI/method locators and a registry-bound pair review. Existing DOI identities and fingerprints are unchanged. Alias or later-DOI migrations remain held for explicit curation.

### Retry and discovery behavior

- Extraction v6 retries unavailable/partially parsed sources after capped exponential cooldown, with reason, attempts and next retry recorded. A successfully parsed source with no exact sample match waits for input/parser changes
- Grade-B review caches input/evidence/version fingerprints and separates missing conditions, source failures, non-textile exclusions and pending exact-state evidence. Unchanged settled items are not fetched every run
- A new review-registry entry invalidates review/extraction caches. Failed or unchanged runs do not rewrite unchanged outputs merely to change timestamps
- Discovery suppresses only works already in its extraction queue, not every DOI mentioned elsewhere in the repository. Use `python scripts/harvest_tg_loi.py --refresh-existing --max-new 25` for a bounded, deliberate evidence refresh of queued works encountered by the current cursor
- Supplementary/PDF evidence can be discovered but is **not yet an end-to-end exact-pair extraction route**. This repair does not add PDF digitization, external-model calls, paid APIs or automatic inference from curves

### Checks and safe publication

Run locally with the existing dependencies:

```sh
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m compileall -q scripts tests
python scripts/validate_tg_loi.py
```

The plotting helper defaults to the evidence-reviewed master, requires a single TG-condition stratum, and refuses empty output. For intentional legacy exploration, pass `--csv data/tg_loi_candidates.csv --exploratory`; its figure is visibly labeled and can include quarantined records. Matplotlib remains an optional pre-existing plotting dependency.

Tests use local fixtures and mocked requests. A passing test suite is not a claim of successful live publisher access or scientific re-review of every paper. Rebuilds fail before replacing outputs when input ranges are invalid or an input CSV is unreadable. Validation and README counts use the same deterministic snapshot. Actions retain the single-writer/latest-main guard and use `queue: max` so up to 100 pending discovery/processing/rebuild runs are kept instead of replacing one another.

<!-- TG-LOI-SNAPSHOT:START -->
## Current TG–LOI evidence snapshot

- Legacy field-complete condition records: **2189** (not a scientific Grade-A count)
- Numeric TG–LOI candidate rows: **2507**, across **483 DOI**
- Field-complete, unflagged condition records awaiting evidence review: **379**
- Quarantined condition records: **34**; originals and reasons retained
- Malformed input CSV records quarantined separately: **1**
- Evidence-reviewed exact Grade-A conditions / sample states: **1866 / 1467**
- DOI cohort: **414 sources / 1858 conditions / 1459 states**
- Reviewed non-DOI cohort: **2 sources / 8 conditions / 8 states**
- Overall reviewed sources: **416**; source identity schema **1**
- Recorded publication types (disjoint Grade-A source identities): journal_article: **271**; conference_proceedings: **5**; author_preprint: **8**; unspecified: **132**; unrecognized: **0**; conflicting_metadata: **0**
- Sources explicitly marked `author_preprint` (without conflicting type metadata): **8 sources / 33 conditions / 23 states**
- Target: 2000 verified sample states; remaining **533**

Publication types use explicit `publication_type` metadata on Grade-A candidate rows before deduplication; pending and quarantined rows cannot classify verified sources. Non-DOI `original_conference_proceedings` also identifies conference proceedings. Missing-only labels are `unspecified`; unknown labels are `unrecognized`; disagreeing nonempty labels are `conflicting_metadata`, excluded from the author-preprint subtotal. Blank labels do not contradict an explicit source-level type. DOI presence and Grade-A numerical review do not establish journal publication or peer review.
Unspecified or unrecognized publication types do not invalidate accepted numerical evidence. Zero explicitly marked author-preprint sources does not establish that no legacy source is a preprint.
New author-preprint rows should explicitly record `publication_type=author_preprint` and `source_version`. These reporting fields do not change source identities, fingerprints or the evidence gate.
A missing new review field means pending documentation, not that a legacy measurement is wrong.
Counts are generated together with `data/automation/validation_report.json`; do not edit by hand.
Snapshot SHA-256: `486ff7c53635a9a1ba7a5269fc003ab1ccf1c94905721f660e95314473fa71a6`
<!-- TG-LOI-SNAPSHOT:END -->



### Urban textiles and fibre-forming material target

The active target is **3000 original-source-verified,deduplicated sample states** for urban textiles,fibres,fibre-forming polymers and precursors. PET,aramid and other eligible fibre-forming materials may be tested as resin,film or bulk specimens without a textile-use statement. Record the actual whole specimen form;TG andLOI still require the same formulation,form,treatment andwashing state. Fibre/polymer-containing composites are classified separately and are never relabeled as finished fabrics. Ordinary city-use plastics are not automatically admitted.

Use [the target-material master](data/tg_loi_textile_master.csv) and [scope report](data/automation/textile_scope_report.json):**183 states /219 TG records**,comprising**143 cloth states /171 TG**,**29 fibre states /29 TG**,**1 PA1012 polymer state /1 TG**,and**10 PET/PA1012 polymer-composite states /18 TG**. Another**1284 broad reviewed states await scope review** and contributezero to this incremental target count. The broader master preserves historical facts;its total and historical2000-state benchmark are not this target. Former paper exclusions remain pending expanded eligibility review. Earlier textile-only scope reports are historical.

After the ordinary evidence-gated rebuild,run `python scripts/textile_scope.py`. [Scope decisions](data/curation/textile_scope_registry.json) require documentary material evidence and are bound to both the reviewed measurement fingerprint and material,composition,preparation,washing and source-locator identity. Raw resin/film/bulk forms require an explicit fibre-forming material class,evidence locator,reviewer,date and matching material-scope fingerprint. Missing or changed bindings fail;keywords alone cannot admit records. Different atmospheres or ramps count as conditions of one sample state. Scope adjudication reusing prior reviewed facts is distinct from new pairs and original-source evidence upgrades.

Source acquisition for this project uses the existing read-only local literature library:CSV/index discovery followed by native PDF text or parsed HTML/body/table reading and available supplementary materials. No online literature supplementation or page-image reading. Originals remain unchanged;all full-text caches,processing scripts and resumable checkpoints stay outside the library and public repository. Public outputs contain fact data,necessary code,validation and DOI/page/table/figure locators,without full text,private material or local paths.
