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
| `T1_C`, `T5_C`, `T10_C`, `T20_C`, `T40_C`, `T50_C` | Temperatures at specified mass loss; `T1_C` is retained only when the source explicitly reports Td,1% |
| `Tonset_C` | Reported onset / initial decomposition temperature |
| `Tmax1_C`, `Tmax2_C`, `Tmax3_C` | DTG peak temperatures |
| `residue_at_Tmax_pct` | Residual mass reported at a single DTG peak / Tmax when explicitly tabulated |
| `residue_at_Tmax1_pct`, `residue_at_Tmax2_pct`, `residue_at_Tmax3_pct` | Residual mass corresponding to `Tmax1_C`, `Tmax2_C`, and `Tmax3_C` when a source reports multiple DTG peaks |
| `residue_temp_C` | Temperature corresponding to `residue_pct` |
| `residue_pct` | Residual mass |
| `R400_pct`, `R500_pct`, `R550_pct`, `R600_pct`, `R650_pct`, `R700_pct`, `R800_pct` | Residual mass at explicitly reported fixed temperatures; preserve the source temperature exactly |
| `LOI_pct` | Limiting oxygen index |
| `direct_numeric_use` | Whether source evidence currently supports direct numerical analysis |
| `DOI`, `source_url`, `source_location` | Provenance / audit trail |
| `limitations` | Known limitations or conflicts |

## Scatter-plot constraints

For quantitative plots, the default filter should be `direct_numeric_use == "是"` where applicable. Do not compare residue values measured at different terminal temperatures without either normalization or explicit faceting/encoding. Do not merge N2 and air as one condition.

## Extended staging fields

Incoming verified batches may also carry `T50_C` and `residue_at_Tmax_pct`. These fields should be preserved when regenerating the master scatter table. Do not substitute `residue_at_Tmax_pct` for terminal residue (`R500_pct`, `R600_pct`, `R700_pct`, `R800_pct`) because they are physically different quantities.

`T1_C` must not be silently re-labelled as `Tonset_C`; both may coexist when a source reports them separately.

`T40_C` is retained when a source explicitly reports the temperature at 40% mass loss; it must not be converted to or substituted for `T50_C`.

Fixed-temperature residue fields must never be shifted to the nearest existing bin. For example, a source value at 550 °C belongs in `R550_pct`, not `R500_pct` or `R600_pct`.

When multiple Tmax values are reported with a residual-mass value at each peak, preserve the pairing in numbered `residue_at_TmaxN_pct` fields rather than collapsing to one residue value.
