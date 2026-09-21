# `scatter_ready.csv` schema

Each row is one TG observation mapped to its material/sample state. If a numeric LOI exists for the same state, it is attached to that row.

Core analytical fields:

| Field | Meaning |
|---|---|
| `record_id` | Stable TG record identifier |
| `dataset_type` | `literature` or `commercial` |
| `material_category` | Cotton, polyester, aramid, blends, etc. |
| `material_form` | Fabric, fiber, yarn, etc. |
| `sample_state` | Original sample / product state |
| `treatment_state` | Untreated, FR treated, washed, coated, etc. |
| `atmosphere` | N2, air, synthetic air, O2/air, etc. |
| `heating_rate_C_min` | TGA heating rate |
| `T5_C`, `T10_C`, `T20_C` | Temperatures at specified mass loss |
| `Tonset_C` | Reported onset / initial decomposition temperature |
| `Tmax1_C`, `Tmax2_C`, `Tmax3_C` | DTG peak temperatures |
| `residue_temp_C` | Temperature corresponding to `residue_pct` |
| `residue_pct` | Residual mass |
| `LOI_pct` | Limiting oxygen index |
| `direct_numeric_use` | Whether source evidence currently supports direct numerical analysis |
| `DOI`, `source_url`, `source_location` | Provenance / audit trail |
| `limitations` | Known limitations or conflicts |

## Scatter-plot constraints

For quantitative plots, the default filter should be `direct_numeric_use == "是"` where applicable. Do not compare residue values measured at different terminal temperatures without either normalization or explicit faceting/encoding. Do not merge N2 and air as one condition.