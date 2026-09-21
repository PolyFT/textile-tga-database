# Textile TGA Database

Private research database for textile thermal-response / thermogravimetric data, with LOI as a principal fire-performance label.

## Current snapshot

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
4. regenerate `scatter_ready.csv`,
5. commit with a batch-specific message.

PDFs are not stored here unless redistribution is clearly permitted; use DOI/URL and source-location fields for provenance.

## Collection progress — 2026-09-21

New web-verified staging added after the 639-row workbook snapshot:

- Batch 1: 17 observations (some condition fields still require full-text completion)
- Batch 2: 24 paired TGA–LOI observations with explicit numerical evidence
- Batch 3: 14 paired TGA–LOI observations with explicit numerical evidence
- New candidate queue: 5 PA6/PA66/polyester sources awaiting full TGA extraction

For paper-facing scatter plots, batches 2–3 are currently the highest-confidence increment because sample state, TGA condition and matching LOI are explicitly resolved. The staging files retain T50 and residue-at-Tmax fields even where the current master scatter schema does not yet expose them.
