# Source verification progress — 2026-09-30

The reviewed dataset contains **239 unique DOI/sample/washing states**, **280 TG condition records**, and **50 papers**. The near-term target is 500 unique states; **261 remain**. The long-term target remains 2000.

## Batches

- b38: 60 reviewed states, represented by 67 TG conditions. Of these, 15 were genuinely new or newly completed pairs and 45 were existing states upgraded with source evidence
- b39: 81 additional reviewed states, represented by 97 TG conditions. Of these, 56 are new-source or newly completed pairs; 25 are existing states upgraded with source evidence or missing conditions
- b40: 21 additional reviewed states and 31 conditions, comprising 5 new alginate/aramid/PTFE laminate states and 16 existing states with verified source evidence
- b41: 59 additional reviewed states and 59 conditions from seven papers; all 59 were existing numeric sample states upgraded with primary-source evidence. There are zero genuinely new scientific states in this batch
- Cumulative: 76 new/newly completed paired states and 163 existing paired states with upgraded evidence
- Two new cotton candidates lack a reported TG heating rate and remain outside the verified layer

## Scientific safeguards

- All accepted observations have primary-source TG, LOI and method locators, exact specimen/wash-state mapping and fingerprint-bound review
- Original source CSVs remain intact. New extractions and supplementary values are in the b38/b39/b40/b41 incoming files
- Repeated TG atmospheres do not increase the sample-state target count
- Conflicting source values remain absent from clean fields, with the discrepancy preserved in source notes
- Cashmere/alginate source T1max is a water-removal peak. It is stored as water_removal_peak_C; T2–T4 retain original numbering
- TG method start temperatures and standard deviations are typed metadata, not decomposition-temperature metrics
- Unknown heating rates, LOI intervals, specimen-form mismatches and unproven sample aliases are not converted into exact pairs

## Continuation

The guarded legacy importer recovered 180 historical numerical candidates and quarantined one truncated row. These are not new scientific observations and are not automatically Grade A. With b42 the candidate layer has 669 numerical rows, while 239 unique sample states have the required source review.

 tracks per-paper outcomes;  records target accounting and the active publication owner. Check current main and any open data PR before starting a new write. Preserve the documented holds and use source-backed crosswalks rather than DOI-only or value-only matching.

The b40 source rows use fingerprint-bound inline review metadata supported by the existing validator. This avoids repeatedly rewriting an ever-growing review registry; changing a scientific value or condition invalidates the stored approval. Public branch-local materialization generates large derived tables without copying PDF/XML source caches into the repository.

## Legacy recovery checkpoint

Twenty-four complete legacy commercial rows (CTG0362–CTG0385) are staged in curation only: one repairs the truncated scatter record and 23 were absent from scatter. They already exist in the commercial source table, seven overlap incoming source/sample records, and none represents new scientific evidence or a Grade-A promotion. The original XLSX transfer failed twice with HTTP502; its available text also ends at CTG0386, so the remaining expected 45 commercial rows are unresolved. Do not invent that tail or append the recovery file without reconciliation.

## b41 source adjudication

- Seven papers add 59 evidence-reviewed states: commercial MLSE fabrics 27, meta-aramid/polyurea 6, microwave cotton 9, CPA-Al/PET 4, pea-protein cotton 4, sericin/PET 4, and lignin/rPET 5
- Nine MLSE post-soak pairs belong to one explicitly cross-referenced series in both LOI and TGA tables. Their numerical soak duration is withheld because one sentence says 30 s while methods/captions say 30 min; no typo correction is inferred
- Cotton control LOI 17 versus 19, air-ramp attribution, and synthetic-air versus nitrogen atmosphere conflicts remain excluded. TGA peaks are kept distinct from MCC temperatures, and original stage numbering is preserved
- The three earlier priority leads produced no new verified pairs: the NYCO paper reports no LOI; PET biodegradation rows carry a wrong DOI; the RSC full text could not be accessed. Their concrete holds are saved in the b41 curation report
- Full-text caches remain outside the public repository; only numerical facts, concise provenance, tests and review outcomes are published

## b41 publication checkpoint

PR #7 merged to  at 2026-09-30 15:53:45 UTC as . Exact-head validation of  passed in [run 36725147420](https://github.com/PolyFT/textile-tga-database/actions/runs/36725147420), including all 97 offline tests and snapshot consistency. Remote main was independently read back: 221 verified unique sample states, 254 conditions, 46 DOI, no validation errors. Snapshot SHA-256: .

The b41 single-writer lease is released. The per-paper source-review queue and its holds remain intact. Start the next publisher only after checking current main and any open data PR; no b42 rows are included in this checkpoint.

## b42 recovered publication batch

- Eighteen existing states receive source verification, represented by 26 TG conditions across four additional papers. This is an evidence upgrade, with zero genuinely new scientific states
- ACS Omega 2c02466: five states / ten conditions; defective later Table 5 headers remain unmapped. Only three explicit prose residues are retained
- IJMS 24021093: three states / six conditions; TGA conditions stay separate from TG-FTIR conditions, and unmatched washed states remain held
- e-Polymers 2020-0059: six states / six conditions; bath concentration differs from add-on, and unspecified uncertainty is not called SD
- Nanomaterials 12224048: four 50-laundering-cycle states / four conditions; actual LOI grid and TG table state mapping overrides transposed captions. Residue endpoint is 900 C. The stage-a moisture/solvent loss peak is stored as water_removal_peak_C, with stage-b decomposition numbering retained as Tmax2_C
- D1RA07410E remains excluded: bulk copolyester TG cannot be paired with separately spun-fiber LOI; five legacy numeric sets also mismatch the cited source

Recovered original extraction and independent QA artifacts were reused rather than repeating their source reviews. All 104 offline tests, compilation and the scientific validation gate pass locally. The branch must pass exact-head snapshot CI before merging. Its temporary branch-only materializer removes itself, and only numerical facts, concise provenance and tests are published. The b42 writer lease was released after verified publication on main.

## b42 publication checkpoint

PR #8 merged to `main` at 2026-09-30 16:25:52 UTC as `a1858b9f82d16fad95ff0c4afe79dbf68ed259f5`. Exact head `08e7798ebf80ef98c3126b8e2a6b4a3a56fe52a0` passed [run 36743487730, attempt 2](https://github.com/PolyFT/textile-tga-database/actions/runs/36743487730) after the normal workflow approval. All 104 offline tests, compilation, scientific validation and committed-snapshot consistency succeeded. Remote main independently confirms 239 unique reviewed sample states, 280 TG conditions, 50 DOI, and errors=[]. Snapshot SHA-256: `b4f1ffe0216bcf13f84e059c90e0b5da677e5acb59369ffc5f4fb8f5c3f1fa20`.

The temporary materializer has been removed. The b42 single-writer lease is released, and all source holds remain. Current main contains no b43 source rows. Next public-source preparation is read-only until a new publisher checks current main and open data PRs.
