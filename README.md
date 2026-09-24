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

Baseline normalized snapshot: 639 TG observations.

Incoming verified staging now extends through **B20260921-205**, for **205 additional observations**. These are a mixture of:
- exact TGA–LOI paired observations,
- TG-only observations retained when LOI is absent or not reliably measurable,
- condition-partial observations whose numerical TGA/LOI values are explicit but one TGA condition field is missing,
- commercial / application-relevant textile records kept distinct from laboratory-only systems.

Recent high-value additions include commercial furnishing fabrics, mattress ticking with commercial flame retardants, automotive-interior PET, PA6,6 technical textiles, wool, silk, lyocell, PAN, polypropylene nonwoven, and multiple PET/cotton blend constructions.

Paper-facing scatter plots should use only rows with exact sample-state matching between TGA and LOI, then stratify by atmosphere, heating rate, material class and evidence level. TG-only rows remain useful for the thermal-response landscape but are not used as TGA–LOI correlation points.

Additional candidate queues contain PA6/PA66/PET/viscose/lyocell/cuprammonium/Nylon56 sources that remain outside the main paired layer until TGA conditions and exact sample-state mapping are resolved.

## Closed-loop automation

The repository now runs a conservative end-to-end TG-LOI pipeline automatically.

Schedule: `TG-LOI closed-loop harvest` runs hourly at minute 17 (UTC). Each cycle advances 8 stateful OpenAlex query pages, collects up to 200 new reviewable literature candidates, and performs full-text/sample-level extraction on at most 25 previously unprocessed candidates.

Data flow:

```
OpenAlex / open full text / supplementary evidence
        ↓
data/automation/candidate_extractions.csv
        ↓
scripts/extract_tg_loi.py
        ↓
data/automation/auto_extracted.csv
        ├── Grade A → data/incoming/verified_auto_YYYYMMDD.csv
        └── Grade B/C → data/automation/review_queue.csv
        ↓
scripts/validate_tg_loi.py
        ↓
data/tg_loi_master.csv
```

Automatic Grade A promotion is intentionally strict. A row is promoted only when:
- the LOI and TG tables contain an exact normalized match for the same sample state;
- LOI is an exact numeric value, not a range or inferred midpoint;
- at least one supported TG numeric field is explicitly tabulated;
- TGA atmosphere and heating rate are unambiguous;
- the source is a textile/fabric/fiber/yarn system rather than a plaque, film, resin, composite or paper state;
- the normalized DOI + sample state + atmosphere + heating-rate key is not already present in the strict master table.

Grade B retains useful numerical pairings with incomplete/ambiguous conditions. Grade C retains non-pairable candidates or sources whose structured tables cannot be safely parsed. Neither B nor C is automatically used for paper-facing scatter plots.

The workflow fast-forwards to the current `main` branch before processing and skips stale commits if `main` advances during a run. This prevents automated state files and master-table rebuilds from creating merge/rebase conflicts.

Current strict paired count: **183** (validation report: 2026-09-24; target 2000).

