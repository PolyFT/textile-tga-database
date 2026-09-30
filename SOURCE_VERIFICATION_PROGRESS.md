# Source verification progress — 2026-09-30

The reviewed dataset contains **501 unique DOI/sample/washing states**, **577 TG condition records**, and **117 papers**. The near-term target is 500 unique states; **0 remain**. The long-term target remains 2000.

## Batches

- b38: 60 reviewed states, represented by 67 TG conditions. Of these, 15 were genuinely new or newly completed pairs and 45 were existing states upgraded with source evidence
- b39: 81 additional reviewed states, represented by 97 TG conditions. Of these, 56 are new-source or newly completed pairs; 25 are existing states upgraded with source evidence or missing conditions
- b40: 21 additional reviewed states and 31 conditions, comprising 5 new alginate/aramid/PTFE laminate states and 16 existing states with verified source evidence
- b41: 59 additional reviewed states and 59 conditions from seven papers; all 59 were existing numeric sample states upgraded with primary-source evidence. There are zero genuinely new scientific states in this batch
- Cumulative: 300 new/newly completed paired states and 201 existing paired states with upgraded evidence
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

The guarded legacy importer recovered 180 historical numerical candidates and quarantined one truncated row. These are not new scientific observations and are not automatically Grade A. With b46 the candidate layer has 720 numerical rows, while 285 unique sample states have the required source review.

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

## b43 source adjudication

Twelve existing sample states gain primary-source review across four papers, represented by fourteen conditions. There are zero genuinely new scientific states. Two lyocell states each have air and nitrogen TG, three PET 2016 states retain only unambiguous TG metrics, four PET 2018 states retain generic terminal residues, and three PP states retain experimental T5/Tmax/R700. The batch uses fingerprint-bound approvals and a source-review manifest with per-file hashes.

Five whole pairs remain held: PET 2016 PA/PD abstract conflicts and PF washing ambiguity, PET 2018 PO1 residue conflict, and PP control LOI 18.1 versus18.2. The PAN paper retains four fiber-TG versus woven-fabric-LOI holds. Source Peak headings are not promoted to DTG Tmax; moisture and coating evaporation are kept separate. PET 2018 method endpoint750C is not assigned as the residue measurement temperature. All111 offline tests, compilation and scientific validation pass locally; exact-head CI and snapshot consistency are required before merging. The b43 writer lease is released after verified main publication.

The next read-only source preparation contains proposed cotton, nylon and wool pairs. No b44 rows are included in the b43 counts, and the next publisher must check current main and open PRs before claiming a writer lease.

## b43 publication checkpoint and source handoff

PR #10 merged to main at2026-09-30 16:48:52 UTC as `78a1fd32807d536bf149f1155bd71c5bb7ecf623`. Exact head `9af52582a221945d2cf2cd034ede85220b28c351` passed [run36746787846](https://github.com/PolyFT/textile-tga-database/actions/runs/36746787846), including all111 tests, compilation, scientific validation and committed-snapshot consistency. Remote main confirms251 unique verified states,294 conditions,54DOI and errors=[]. Snapshot SHA-256:`6636b7d4c35a2bf8854d60bfad1bf0484ddcc1a6d85e0a92effac5bc541580c4`.

The b43 writer lease is released. PR #9, a separate overlapping preparation on codex/source-review-b43, was withdrawn without merging; its stated remaining scope includes wool and other candidates. Check current main and open PRs and coordinate source scope before a new claim. No identity or execution environment is inferred for that preparation.

Separately,21 proposed pairs from five source reviews are staged but not imported or counted:13 existing TG-only cotton states completed from explicit printed LOI labels, plus eight new-to-measurement nylon/wool/cotton states. The per-source list and count categories are in source_verification_progress.json. Existing public and local-library preparation must reconcile those sources before publication; main remains251.

## b44 newly completed and new-source pairs

Twenty-one reviewed sample states add twenty-one conditions from five papers. Thirteen prior TG-only cotton states are newly completed using exact printed Figure8 LOI labels; these are not new TG experiments. Eight states have no prior measurement records: four from wholly new DOIs and four from existing metadata-only leads. This batch adds zero evidence-only upgrades of already paired states.

- Scientific Reports71071: original Figure8 labels and Tables2/3 supply13 initial/10-wash cotton pairs. Unmatched mercerized control and other washing/treatment states remain held. DTG and PCFC metrics stay separate; S10M252C retains its early-modifier caveat
- PK2018: three nylon fabric/wash states; exact TG prose and Table3LOI. Terminal residues are not recast as R600
- BUCT2016: PA66 and GMA-PA66 fabric pairs; DOPO39.0/39.3 descriptor conflict remains held
- BRIAC wool: ungrafted fabric only; grafted7.9% TG is not assigned the6%/8.1% LOI
- DMPP cotton: EB/PDC35%-bath states only; generic literature controlLOI and unmatched bath concentrations remain held. Independent publisher-PDF text verification succeeded; PDF pixel verification and a downloadable source hash were unavailable and are not claimed

All119 offline tests, compilation and scientific validation pass locally. Per-file hashes and observation fingerprints bind the source reviews. The temporary branch-only materializer must remove itself, and final exact-head CI must pass before merging. No copyrighted full texts, private metadata-library materials or source caches are published. The b44 writer lease is released following verified main publication.

## b44 publication checkpoint

PR #11 merged at2026-09-30 17:01:58 UTC as `7e8416bd10e4b7a203149d4430a6ef442dff2d60`. Exact head `3485305e8ab727c90669ff39c8326832c280bbf3` passed [run36748303574](https://github.com/PolyFT/textile-tga-database/actions/runs/36748303574), including119 tests, compilation, scientific validation and snapshot consistency. Main independently confirms272 unique verified states,315 conditions,59 DOI and errors=[]. Snapshot SHA-256:`7a6861539e3a6f260ed5d0253f9bc1ea4038110171b8ddcb8c87ddf5f06e41a5`.

The b44 single-writer lease is released and all five previously staged papers are now included. Next source preparation is not included in these counts: three guanidine-cotton states passed source review while five remain held for LOI contradictions; two PAA/MMT cotton states have four supported conditions while six concentration-mismatched states remain held; two further DOI sources are being screened. Recheck current main/open PRs and coordinate per-source ownership before another publication claim.


## b45 Proban, PET fiber and wool source review

Eight additional reviewed states are represented by nine TG conditions. Four are newly completed existing states: three Proban washing protocols gain exact TG annotations and the previously TG-only wool control gains explicit LOI. Four existing numeric pairs gain source evidence: Proban UNW/49_10x and two PET fiber states. There are zero new source-inventory sample states. Repeated wool atmospheres and Proban warp/weft LOI are not additional target samples.

- Proban: Table 7 supplies LOI32 for all five states; Figures1/3/5/7/9 contain exact printed TG/dTG analyzer numbers. Table8 is MCC and is excluded. UNW onset321.1 versus321.61 is held; unambiguous peak/residue facts remain accepted. Residue temperature is850C, not700/800C.
- PET/C15A: two Table1 fiber states match explicit primary DTG maxima. The coupled TG-FTIR condition is air50mL/min,20C/min,to750C; conventional TG air60mL/min,to700C is separate. First modifier decomposition, PET decomposition, later char oxidation and Gram-Schmidt gas maxima remain distinct. Preparation bath ramp is not TG ramp.
- Wool: control is oxidatively pretreated woven wool, not raw wool. ControlLOI24 matches Table2 nitrogen/air TG. W100LOI44/44.6 and graph-only W20/W60 remain held; DSC flow/ramp do not supply TG conditions.
- Heliyon: four explicit R600/LOI facts remain outside the verified layer because TG atmosphere and specimen preparation state are unresolved. SEM nitrogen is not a TG condition.
- AEDTMP cotton: initial25FR-1LOI42.6/R80038 remains held for missing TG atmosphere. The100C event is crystal-water loss and260C is approximate. Direct publisher-linked SI returned404; complete SI review is not claimed. Post-wash LOI is not assigned to initial TG.

Original source rows are retained. The source-state crosswalk resolves historical missing wash states; the manifest binds public numerical input hashes and measurement fingerprints. Full texts, original figure images and local source paths remain outside the public repository. The b45 publisher owns the active lease; exact-head tests and snapshot CI are required before merge.

All126 offline tests, compilation and scientific validation pass locally, with280 unique states,324 conditions,62DOI and errors=[]. Final exact-head GitHub checks and snapshot consistency remain required before merge.

## b45 publication checkpoint

PR #12 merged at 2026-09-30 17:15:35 UTC as `ad19fbfefef30cf27427b16a9b07359b849280a4`. Exact head `e2ac9ea3c13bc50feba5ec737f87f487da3884e6` passed [run 36749901610](https://github.com/PolyFT/textile-tga-database/actions/runs/36749901610), including all126 tests, compilation, scientific validation and snapshot consistency. Remote main independently confirms280 verified states,324 conditions,62DOI and errors=[]. Snapshot SHA-256:`c2234a08ca3c271c44fbb70b826a4051fc096bfc9026415715627a5f9389a94c`.

The b45 single-writer lease is released. Separate pending source preparation is preserved and is not included in the280 count. Local metadata-library root remains unresolved; do not assume a path or write any library files. Other unreviewed public-source evidence work can continue after checking current source ownership.

## b46 guanidine and cotton/MMT source review

Five new-source sample states add seven TG conditions from two papers. This batch adds no evidence-only upgrades of existing pairs. Three guanidine-cotton formulations pass exact initial-state LOI/onset/R400/R600 review; five other table rows remain held because their LOI values conflict with applicable prose bounds. Neither a majority vote nor table priority is used to infer corrections. Publisher PDF text was independently verified; unavailable pixel QA is disclosed.

The PAA/MMT paper contributes only COT and COT/MMT2% under nitrogen and air, sharing two measured LOI observations across four TG conditions. Table3's10%-loss onset is T10, not generic Tonset. The exactR800 zero for air COT is retained. Six PAA-bearing states remain held for concentration mismatches between TG and LOI; original supplementary native text adds no crosswalk, and incomplete supplementary image rendering is disclosed.

All132 offline tests, compilation and scientific validation pass locally. Fingerprint-bound approvals and per-file hashes preserve the independent source review. The branch-only materializer must remove itself and exact-head CI must pass before merge. The b46 publisher released its lease after verified main publication.

Two further cotton source assessments produced zero exact-condition pairs: SAGE1528083709347122 lacks a TG heating rate and has one formulation conflict; Donghua2024.0382 lacks exact same-state TG numbers and has formulation-unit/order ambiguities. DOI-less thesis values are not assigned a related journal DOI. The2011.08.014 primary full text remains unretrieved; the2012 kinetics follow-on is not a substitute. These holds are not target samples.

## b46 publication checkpoint

PR #13 merged at2026-09-30 17:26:36 UTC as `016e4251f3455e4be5af37d31aa4501f1082eafb`. Exact head `6910435f07316e1d7d8c39a85f7ab82a6933d77b` passed [run36751208066](https://github.com/PolyFT/textile-tga-database/actions/runs/36751208066), including all132 offline tests, compilation, scientific validation and committed-snapshot consistency. Remote main independently confirms285 unique verified states,331 conditions,64 DOI and errors=[]. Snapshot SHA-256:`f1668a8b7557cc17f5bc61b45e58495804e81cabc2aad45f7457cc13fe8ca191`.

The temporary materializer is removed and b46 writer lease is released. Every independently reviewed ready pair in the previously announced b42–b46 preparations is now included. Remaining condition-partial, LOI-only, identifier-held or inaccessible-source preparations remain excluded; none is an uncounted verified pair. The near-term goal is not yet met:215 further unique verified states are required to reach500. Continue from current source ownership and the per-paper queue rather than repeating completed or held reviews without new evidence.


## b47 heavy cotton, PET and official blend-coating SI

Nine existing numerical pairs gain complete same-state evidence and become eligible for the reviewed master, represented by nine TG conditions. This batch discovers zero new verified source-inventory states and completes zero formerly unpaired states. Three genuinely new cotton candidates from 8b00822 remain held for TG atmosphere attribution and do not increase the target.

- Heavy cotton back-coatings: five Table5 LOI/R500 pairs; air100mL/min,20C/min from author-manuscript p7. Initial360g/m2 cotton remains separate from light cotton, soaked states, neat chemicals and furnace-held chars. Fyrol51/250 lacks experimental TG and stays held.
- ATMP/chitosan blend coating: official SI TableS3 experimental PEC21.5/Fabric3 TG matches TableS5 zero-cycle LOI28.5+/-0.5. N2,10C/min and residue700C are explicit. The main paper is inaccessible, so review remains SI-only; five other TG states await primary LOI. Fiber ratios, statistical meaning of the LOI uncertainty, gas flow and scan endpoint are not inferred. Washed LOI and calculated TG are excluded.
- PET/NDFR: explicit Section3.4 LOI matches Table6 AZ1/AZ2/AZ10 TG at N2,10C/min. Complete published primary author-copy text was readable; original PDF pixels were unavailable. AZ2 T80 conflict471/472C and AZ10 oven-duration conflict20/30min remain absent from clean fields. Early coating volatilization is not polymer onset; Table7 DSC is excluded.
- New smart cotton: Table1 contains three exact TG/LOI tuples, but methods mention both N2 and air without assigning the table to either. These facts are condition-partial only. The full ramie paper reports no TG; two Cellulose leads expose only public previews.

Manifest, sample-state crosswalk, field-level holds and the source queue preserve recovery positions. Public files contain facts and concise provenance only. Metadata library selection remains pending; no library file has been changed. Latest-main b46 additions and other preparation are preserved. Exact-head tests and snapshot CI are required before merge.

## b47 publication checkpoint

[PR #14](https://github.com/PolyFT/textile-tga-database/pull/14) merged as `3d422bf40f07f48e425dfb6f31f015e30b578462` after [validation run 36753896559](https://github.com/PolyFT/textile-tga-database/actions/runs/36753896559) passed on exact head `eba30ce384c372bda8da5b79debd9244f5bcc227`: 138 tests, Python compilation, scientific validation and committed-snapshot consistency. Refreshed main confirms 294 verified unique states, 340 conditions and 67 DOI; errors are empty. Snapshot: `532e5d04b212b0d261e33c098d83f85ab4eab8bf7c5745e256c7d09fde59751a`. B47 adds nine evidence upgrades and no newly completed or new-source pairs. Its single-writer lease is released; next publication must refresh main, PRs, source queue and lease. Local metadata directory selection remains unresolved; no library file has been changed.


## b48 source review

Twenty-two additional reviewed sample states contribute twenty-three TG conditions from six papers. Twenty-one are new measurement states: five from wholly uncatalogued DOIs and sixteen from metadata-only leads. One existing untreated-silk pair gains source evidence in two atmospheres. No second sample is counted for its repeated LOI.

- Silk: scoured untreated fabric only; exact Table2 TG and TableS1 LOI24.4. Initial and washed treated LOI conflicts remain held
- Carrageenan/agar/alginate: three fiber states; author-printed R700 values and Table1 LOI. Original prose precision is retained; no reviewer digitization, cone specimen substitution or gas-peak substitution
- Silica/CaHP/chitosan cotton: two states; source onset means10% mass loss. The incompatible95%-loss endset is omitted
- Phosphazene cotton: seven initial states from separate conventional and supercritical deposition series. Generic residues stay unassigned to a temperature. Method start0C is metadata. Control onset,12%LOI and uncertain washing branches remain held
- Coconut-shell cotton: S2–S4 only. The official correction establishes the600C method endpoint. S1/S5/S6 LOI and S2 residue-temperature conflicts remain excluded
- Casein cotton: six exact Table1/Table3 labels share initial TG/LOI states. Conflicting preparation temperatures, pressures, bath loadings and two add-ons are withheld. Dual source onsets stay separate and MCC results are excluded

Per-file hashes and observation fingerprints bind independent reviews. The source PDFs, supplements, images and private preparation files remain outside the public repository. The branch-only materializer must remove itself, and all final exact-head tests and snapshot checks must pass before merge. The b48 publisher released the lease after verified main publication.

## b48 publication checkpoint

PR #15 merged at 2026-09-30 18:04:39 UTC as `7aa9b901ab5eb55974452efa1adbb96f6645d85b`. Exact head `50598535f86f89410ca9e9335ae555a027209981` passed [run 36755790556](https://github.com/PolyFT/textile-tga-database/actions/runs/36755790556), including all 147 offline tests, compilation, scientific validation and committed-snapshot consistency. Remote main independently confirms 316 reviewed unique sample states, 363 conditions, 73 DOI and errors=[]. Snapshot SHA-256: `38727b97c9054832516cc52e9b353057f1ced418b905a2afaba2eb67eefaa205`.

All accepted b48 drafts are now published, and the temporary materializer is removed. The b48 single-writer lease is released. No held source, conflicting value, repeated atmosphere or earlier overlapping b47 draft is an uncounted verified sample. The near-term target still requires 184 more unique reviewed states. Continue from the source queue and current ownership rather than repeating completed reviews.


## b49 original printed LOI labels and new PET/cotton control

Ten states are represented by ten TG conditions: nine existing phytate numerical pairs gain source evidence, and one new polyester/cotton control is a genuinely new source-inventory pair. No formerly single-sided state is newly completed. Eight incomplete or mismatched state facts stay outside the target. B48's22 states and23 conditions are preserved.

- Phytate CO/CO-PET/PET: original publisher Figure14 p16 prints all nine LOI numbers directly; no curve digitization is needed. Table4 p13, Figures11/14 and methods match initial substrate/coating states; complete official SI contains FTIR/Py-GC-MS and adds no exact pairs. N2,90mL/min,20K/min; scan40-800C with5/10min holds. R700 and the masses at DTG maxima remain separate from endpoint800C. TG-only predrying is not assigned to LOI. Old b37/scatter inputs are retained. The former graph-only source hold is resolved by original printed labels, and the queue entry is updated rather than duplicated.
- New80/20 PET/cotton control: Section3.3 gives T5=324.8C and R700=10.3%; Table2 gives LOI17. N2,50mL/min,10C/min,30-700C; ethanol preparation clean is distinct from durability washing. Five treated states remain held; PDA14.3%residue is preserved without silently assigning its temperature, and approximate/curve-only TG is excluded.
- Triazolium hydrogels: full main and official SI inspected. Neat-salt TG and neat-hydrogel residue do not pair with fabric LOI; TG-FTIR atmosphere and30wt%sample-label contradictions remain held.
- Grafted cotton has own TG but no own LOI; reactive-printing fabrics have own LOI and MCC but no TG. Background/reference values and MCC temperatures are not reused. The flax main text has own TG/PCFC/vertical burn only; SI review remains pending, so its source screening remains incomplete.

Manifest, factual-input hash, fingerprints, partial records, source-state crosswalk and holds preserve restart positions. Full source files and local paths remain outside the public repository; the metadata library remains untouched. B49 owns the single-writer lease; exact-head tests and committed-snapshot CI are required before merging.

All154 offline tests, compilation and scientific validation passed locally:326 unique verified states,373 TG conditions,75 DOI and errors=[]. Snapshot SHA-256:`9b1271024101e1ce753f27c60ef1a5afc5c56179c37b18ab315309525b8eb94a`. Final exact-head GitHub validation and committed-snapshot consistency remain required before merging.


## b49 publication checkpoint

PR #16 merged at2026-09-30 18:30:07 UTC as `bc59ccbff999365fb5b0a472bc95fd2174580a2a`. Exact head `87d3063cf8d5751d24d6cb74f0279651875a9721` passed [run36758833528](https://github.com/PolyFT/textile-tga-database/actions/runs/36758833528):154 offline tests, compilation, scientific validation and committed-snapshot consistency. Remote main independently confirms326 unique reviewed states,373 TG conditions,75 DOI and errors=[]. Snapshot SHA-256:`9b1271024101e1ce753f27c60ef1a5afc5c56179c37b18ab315309525b8eb94a`.

The b49 single-writer lease is released. This batch added one new source-inventory pair and upgraded nine previously numeric paired states; eight condition-partial records remain excluded. The near-term target still requires175 further unique states to exceed500. Local metadata-library path confirmation remains pending and the library remains untouched. Preserve source holds and verify current main/PRs/lease before the next publisher.


## b50 microwave-casein and PTCO source review

Seven additional states contribute ten TG conditions from two papers: four wholly new microwave-treated CUD cotton states, and three existing separate TG/LOI PTCO states newly completed in two atmospheres. Repeated atmospheres do not increase the sample-state count. The original full author/publisher text was independently reviewed; PDF pixel verification is not claimed.

- CUD-11 add-on and second onset conflict with prose and remain omitted; CUD-9 bath composition is inconsistent and is not imported
- The microwave control's identical TG/LOI triplet and fabric conditions in a related casein paper raise possible reuse; it is excluded from admission and the count increment
- Source-native dual onsets remain separate from T5/T10/Tmax; MCC results are not TG
- PTCO Tables 1-3 and conventional TG methods support six observations. Original peak numbering and the missing N2 control first peak are preserved. PPOA add-on is disputed and omitted. Coupled TG-FTIR peaks and its different gas flow are not substituted
- Acidic/alkaline casein has TG but no numerical LOI; the older PET/casein lead lacks retrieved original full text; the phosphorus/sulfur comparison lacks verified ramp and complete table recovery
- SLS/PET remains held because the TG method says N2 while Figure 6 says air, alongside residue/T10 inconsistencies

Only numerical facts, concise source locators, explicit holds and regression tests are published. Observation fingerprints bind reviewed values. Final exact-head tests and snapshot consistency are required before merge, and the active single-writer lease remains until main publication is verified.

All 161 offline tests, compilation and the scientific validation gate pass locally. The regenerated snapshot contains 333 unique states, 383 conditions and 77 DOI, with errors=[] and SHA-256 `69150e3861faf4caebf0e314364e96a680080a72b86792c8f02401c1a76129b4`. These are branch results pending exact-head CI and verified main publication.


## b50 publication checkpoint

PR [#17](https://github.com/PolyFT/textile-tga-database/pull/17) merged at 2026-09-30 18:41:33 UTC as `0351518f0978c37a1e6713649b3e613c803e8734`. Final head `e71fd76131ac8cdb772d27d51b84dca92f3885ed` passed [exact-head validation](https://github.com/PolyFT/textile-tga-database/actions/runs/36760145268): all 161 tests, compilation, scientific validation and committed-snapshot consistency. Fresh main independently confirms 333 unique states, 383 TG conditions, 77 DOI and errors=[]. Snapshot SHA-256: `69150e3861faf4caebf0e314364e96a680080a72b86792c8f02401c1a76129b4`.

This batch adds four new source states and newly completes three existing separate TG/LOI states; it adds zero evidence-only upgrades. The possible repeated microwave control stays excluded. All source holds remain; the branch-only materializer was removed. The b50 lease is released after verified main readback. There are 167 states remaining to 500 (168 to exceed 500). Recheck the latest main, open PRs, lease and per-paper queue before further publication.


## b51 remaining legacy source review

Three existing numerical pairs receive source evidence, adding three verified states and three conditions from two papers. This batch adds zero new scientific measurement states. Independent final-byte reviews checked original published text; PDF pixel QA is not claimed.

- TD and TD220 cotton use the same explicit specimen labels in Tables 1 and 2. The 220 C specimen pretreatment is distinct from the TG-only 100 C moisture-removal hold. R700 is not the 800 C scan endpoint, and residues at Tmax are separate observations. Source-native add-on metadata is not silently renormalized
- Initial COP-treated lyocell/cotton is supported by exact TG/LOI prose and air-atmosphere method. Chemical naming inconsistencies, unmatched washed results and control literature LOI remain excluded. Nitrogen TG-IR settings do not replace conventional air TG conditions
- Wool, taurine/NYCO, DOPO-APTES/PET, keratin/alginate cotton and guar-gum/polyborate cotton remain held for unavailable original conditions/fulltext or unresolved mapping. Repeated atmosphere rows or possibly aliased legacy labels are not new samples

Source fingerprints, input hashes, concise evidence locations and explicit holds are published. Fulltext caches and private preparation remain outside the repository. Exact-head tests and snapshot consistency must pass before merge; the active publisher retains the lease until main is verified.

All 168 offline tests, compilation and scientific validation pass locally. Branch snapshot: 336 unique states, 386 TG conditions, 79 DOI, errors=[]; SHA-256 `2a31d9db2d3595768fb224c166c08c348156c39c2dc3bcc8d91773dc2af1968f`. Exact-head CI and main readback remain required.

Cross-paper provenance: the PO-paper TD nitrogen TG row matches CEJ165778 Table2 exactly. It is kept as one canonical target record in shared experiment group `TD_nitrogen_TG_CEJ165778_PDS112025`; a second CEJ TD admission is excluded. TG reuse does not by itself establish that the LOI experiment was repeated or reused.


## b51 publication checkpoint

PR [#18](https://github.com/PolyFT/textile-tga-database/pull/18) merged at 2026-09-30 19:01:46 UTC as `8764282e2514e92863235407fa0218f84eb10e25`. Final head `99800914b05d1a26a76bad3122483ad55f876061` passed [exact-head validation](https://github.com/PolyFT/textile-tga-database/actions/runs/36762640587), including all 168 tests, compilation, scientific validation and committed-snapshot consistency. Fresh main independently confirms 336 unique states, 386 TG conditions, 79 DOI and errors=[]. Snapshot SHA-256: `2a31d9db2d3595768fb224c166c08c348156c39c2dc3bcc8d91773dc2af1968f`.

This batch adds three existing-pair evidence upgrades and zero new scientific measurement states. Shared TD TG is counted once; the matching CEJ TD state is blocked from a second admission. The temporary materializer is removed and the b51 single-writer lease is released after main readback. There are 164 states remaining to 500, or 165 to exceed 500. Source drafts awaiting review are not included in these counts.


## b52 canonical cotton and DOPO-ETES completion

Three additional states contribute six conditions from two papers. One is a new DD source state. One newly completed CEJ Cotton pair uses shared nitrogen TG and is not a new independent TG experiment. One prior TG-only DOPO-ETES state is completed by exact author-printed LOI. Repeated atmospheres do not increase the state count.

- CEJ DD uses the explicit high-loading LOI and Table1 specimen-selection bridge to Table2. Lower-loading DD is not substituted
- CEJ Cotton is the sole canonical control with measured LOI18.6. Disputed nitrogen T5 is omitted, while other unambiguous TG metrics remain. Future duplicate PO Cotton admission is blocked; PO TD remains the single canonical TD state
- Source add-on convention, nominal concentrations, residue endpoints and residues at DTG peaks retain their original meanings. Calculated silica-subtracted char is excluded
- DOPO-ETES cotton at approximately27% loading uses exact LOI23 from prose and Table1 TG. Other coating LOI is only approximate, and35%-loading or washed LOI lacks matched TG. No graph point is digitized

Independent final-byte reviews checked relevant CEJ final-publication text and visually checked the DOPO-ETES source table and exact LOI prose. Source files and private preparation remain outside the repository. Exact-head CI, scientific gates and snapshot consistency are required before merge; the publication lease remains active until main is verified.

All 176 offline tests, compilation and scientific validation pass locally. Branch snapshot: 339 states, 392 TG conditions, 81 DOI, errors=[]; SHA-256 `51dd4090f505930acc2553bcff487263f5433e2131d54e82b0ab3b70f6ef2ea5`. These remain branch results until exact-head CI and main readback.

Additional source screen: ACS cyclophosphazene2c01257 remains held after full official SI review. Its TableS1 is MCC and its printed temperatures belong to evolved-gas FTIR discussion. An original main-paper source with conventional TG values and exact specimen/LOI mapping is still needed; no pair is admitted.


## b52 publication checkpoint

PR [#19](https://github.com/PolyFT/textile-tga-database/pull/19) merged at 2026-09-30 19:20:03 UTC as `bb2d05cac110e79a749ae1802c95451a1eff4319`. Final head `946d984f413599fce25678bbaa93a071bc8be523` passed [exact-head validation](https://github.com/PolyFT/textile-tga-database/actions/runs/36764792509), including all 176 tests, compilation, scientific validation and committed-snapshot consistency. Fresh main independently confirms 339 unique states, 392 TG conditions, 81 DOI and errors=[]. Snapshot SHA-256: `51dd4090f505930acc2553bcff487263f5433e2131d54e82b0ab3b70f6ef2ea5`.

This batch adds one DD source state and completes two pairs: canonical CEJ Cotton using shared nitrogen TG, and prior TG-only DOPO-ETES cotton. It adds no evidence-only upgrades. Together with b51, this raises main from 333 to 339 states. Shared experimental references are counted once. All accepted source drafts are published, the temporary materializer is removed, and the b52 single-writer lease is released. There are 161 states remaining to 500, or 162 to exceed 500. The cyclophosphazene source remains blocked on original main-paper TG and specimen-mapping evidence; its official SI does not resolve that gap.

 
## b53 new PVA fibers and cotton-backed artificial leather

Four genuinely new source-inventory pairs contribute four TG conditions from two papers. Existing-pair evidence upgrades and newly completed legacy pairs are both zero. Thirty-five partial facts and sixteen additional source screens contribute zero target samples. B52 canonical shared-control safeguards remain intact. Reaching 500 requires 157 more states; strictly exceeding 500 requires 158.

- PVA, PVA/75CD and PVA/75CD/HDI: original Table 2 p8 and complete official SI Table S2 p1 match the final wet-spun fibers. TG uses air, 10 C/min, ending at 600 C. T10, author DTG peak loss, T90 and W550 remain distinct. W550 is neither final 600 C residue nor cone residue. PVA/HDI has exact LOI but lacks matching TG and remains held. Processing clean is distinct from durability laundering; hot pressing is specified for cone calorimetry only. Unreported gas flow, LOI dimensions and uncertainty statistic remain unspecified.
- Cotton-backed HS1 artificial leather with 20 phr org. P: Section 3.1 p6 reports individual generic TG residue 5.9 +/- 0.1%, and Table 4 p11 reports LOI 24.2. Figure 2 identifies the same initial whole laminate. Synthetic air is normalized to air with the original gas retained: 20 mL/min, 10 K/min, 25-600 C. The numeric residue statement lacks an explicit temperature; residue_temp_C remains blank and no R600 is inferred. The existing evidence gate accepts this exact same-state generic TG metric; fixed-temperature residue comparisons exclude it. Complete official SI contains mechanical data and cone-burned film images only.
- APP 13.4 +/- 0.8% and Phos 9.6 +/- 0.5% are chemical-class statistics, not individual representative values. Nineteen other Table 4 textile LOI states remain held. Films, other HS polymers, HALS/bentonite and specimens aged 4.5 years are not cross-paired.
- Additional screens preserve coating/fabric, pellet/meltblown and film/fiber mismatches; flax fabric laminate TG is curve-only. CAB-PL has conflicting LOI 33 in the abstract versus 34 in Table 1/results. MCC, DSC, vertical-fire and background LOI values do not produce TG-LOI pairs. Flax Table 4 percentages in parentheses are coefficients of variation. Unread SI remains explicitly identified in holds.

Input hashes, fingerprint-bound reviews, partial facts and per-source holds preserve the restart position. Full texts and local paths stay outside the public repository. The unconfirmed metadata library remains untouched.

PR [#20](https://github.com/PolyFT/textile-tga-database/pull/20) merged at 2026-09-30 19:38:52 UTC as `b51bcc53297de4696efb523d20d7d9f969283300`. Exact head `8697b046feb1e5c2ce67bccd7f48938e13306718` passed [CI run 36766840839](https://github.com/PolyFT/textile-tga-database/actions/runs/36766840839): all 176 tests, compilation, scientific validation and committed-snapshot consistency. Independent main readback confirms 343 unique sample states, 396 TG conditions, 83 DOI and errors=[]. Snapshot SHA-256: `84541c07f64e9ecfe5bb890da1abcf185dd0da6b991ad04f7e114fbb5a4e80fd`. The b53 writer lease is released through the conditional progress checkpoint after this publication record.


## b54 PAN fiber amination and zinc series

Eleven genuinely new sample states and eleven nitrogen TG conditions are recovered from one original paper. The complete original/A-1/A-2/A-4/A-6/A-8 and B-1/B-2/B-4/B-6/B-8 series uses exact measured LOI and700C residue, with10C/min heating. Independent review checked original methods, preparation, ordered residue lists and publisher Figure5/8 pixels.

TG powders aliquots of the already-spun fibers while LOI braids the same prepared fibers. Canonical material identity and both assay-specific preparations are preserved separately; identical specimen geometry is not claimed. Preparation rinsing is distinct from durability washing. Approximate DTG peaks, DSC temperatures, MCC outputs, evolved-gas peaks and calculated Zn-subtracted residue are excluded. Fulltext files remain private. Six additional source screens retain their concrete holds or no-LOI exclusions.

The input requires exact-head CI and snapshot validation before merging. The writer lease remains active until postmerge verification.


## b54 publication checkpoint

PR #21 merged as `f36272553b91fba3a4760e76629602ab9597eed5`. Exact head `c76d419ca69bbb98d57ad52eb8768fb316b3697f` passed [validation run 36768474390](https://github.com/PolyFT/textile-tga-database/actions/runs/36768474390), including182offline tests, compilation, scientific range/evidence gates and committed-snapshot consistency. Independent main readback confirms354unique states,407conditions,84DOI,errors=[]. Snapshot SHA256: `c40c3682c2b94795005c71a8a71d45a581f11400022bb838cf4e63a4913b78ad`.

All three postmerge checks succeeded: validation36768603488, rebuild36768603414 and processing36768603423. The temporary branch materializer has removed itself, and the writer lease is released. Eleven newly sourced states have been admitted; no repeated conditions inflate that count. Preserve raw assay-specific preparations and all source holds on continuation.


## b55 GEL/AMP and silica cotton coatings

Four genuinely new treated sample states add four nitrogen TG conditions from one original paper. Tables 3 and 4 provide exact T10, Tmax, R700 and LOI values at 10 C/min. State-specific preparation recipes are retained; the source only attributes NaOH pretreatment to LBL specimens. LOI uncertainties are retained without inferring a statistical type.

The 10BL-only state remains held for conflicting LOI values (25.3 versus 25.6) and weight gains (41.4 versus 41.3). SiO2-only weight gain is withheld because 28.3 and 28.2 conflict. The untreated control remains held for possible cross-paper reuse pending provenance resolution. Post-wash LOI states lack matching TG. Independent review used the clear original final-publication tabular text; unavailable PDF pixel review is not claimed. Full texts remain private.

The b55 writer lease is released after exact-head CI, merge and postmerge verification succeeded.

## b55 publication checkpoint

PR #22 merged as `871a900970b8b4f3cc71bdbe23bb638b28c4286c`. Exact head `e9a282ef693ba42b96f7e8a7cd3a12d5320f16d9` passed [run 36770703742](https://github.com/PolyFT/textile-tga-database/actions/runs/36770703742), including 187 tests, compilation, scientific validation and snapshot consistency. Main confirms 358 unique reviewed states, 411 TG conditions and 85 DOI, with no validation errors. Snapshot SHA-256: `4644de7ccc93bdc71fba23e3f9d1c51c975a2c1e64688e7dd9f20f1ec1623520`.

All three postmerge validation, rebuild and processing checks succeeded. The temporary materializer is absent and the single-writer lease is released. Further private source drafts are not included in these counts. Refresh main and source ownership before publishing another batch.


## b56 chitosan-based cotton coatings

Three genuinely new treated cotton states add three nitrogen TG conditions from the original final article. Tables 2 and 5 provide exact LOI, T10, Tmax and residue at 750 C; conditions are 10 C/min and 30 mL/min. Independent review confirmed preparation and original tables. No PDF pixel review is claimed.

The possible reused control remains held, as do seven initial LOI-only states and all unmatched post-wash states. Source-native weight gains are retained separately because the source equation reverses control/coated definitions; normalized add-on is absent. Bracketed delta LOI is not uncertainty. Original full texts remain private.

The b56 writer lease is released after exact-head CI and postmerge verification.

## b56 publication checkpoint

PR #23 merged as `d3ab1a6633405db17ab43e8a4147e746dceb69fe`. Exact head `fcc11a22e30b4d85bfb94cf66f674e58945f6bcd` passed [run 36771653669](https://github.com/PolyFT/textile-tga-database/actions/runs/36771653669), including 192 tests, compilation, scientific validation and snapshot consistency. Main confirms 361 unique states, 414 conditions and 86 DOI, with no validation errors. Snapshot SHA-256: `63f21f9fcc5a5475d38fd185c1c61b0900a1d46658d08455423803e4893346fe`.

All three postmerge checks passed. The temporary materializer is absent and the single-writer lease is released. Subsequent private source drafts are not included in these counts.


## b57 supercritical CO2 cotton finishing

Six genuinely new pdp/pdpt cotton states add six nitrogen TG conditions. Table 2 R600 values and section 3.4 ordered LOI values map exactly by flame retardant and fabric add-on. Methods specify 10 C/min; preparation and LOI conditioning are retained. Independent original-text review passed. The accessed original-text URL is preserved; unavailable publisher PDF bytes and no pixel review are disclosed.

The untreated control has only generic LOI and conflicting residue prose, so it remains excluded. ASTM edition conflict is retained without correction. The introduction mentions air, but methods and numerical results support nitrogen only. Source-native multi-stage onsets are not relabeled as DTG maxima. Full texts remain private.

The b57 writer lease is released after exact-head CI and postmerge verification.

## b57 publication checkpoint

PR #24 merged as `81bf6b9ad6032d22ca9a7adc8d0a361c075484c9`. Exact head `f948109093f096ee5ce61851c58babf8b1ed9073` passed [run 36772553803](https://github.com/PolyFT/textile-tga-database/actions/runs/36772553803), including 196 tests, compilation, scientific validation and snapshot consistency. Main confirms 367 unique states, 420 conditions and 87 DOI, with no validation errors. Snapshot SHA-256: `30bdd20dbdf3208a34691264990f61605b6cf7334bf02ece855b1d2bf101d8f3`.

All three postmerge checks passed. The temporary materializer is absent and the single-writer lease is released. A related 2012 conference poster repeats the six TG/add-on observations but gives LOI at different add-ons; it does not provide six additional pairs or override the 2017 exact same-state LOIs. Subsequent private source drafts are not included in these counts.


## b58 flax and glass fabric laminate source review

Six genuinely new sample states add six TG conditions from two primary sources; zero existing-pair evidence upgrades. Eighteen incomplete/source-conflicted facts stay outside the verified layer. The strict greater-than-500 milestone needs 128 further verified states.

- Flax/VE and5/10wt%MH: original Table2 provides same-laminate LOI and tangent-defined Tonset, not T5/T10. N2/10Cmin is explicit. All14 officialS1 worksheets inspected. Generic residues have no numerical temperature; method800C and supplied curves ending near600C remain separate, with noR600/R800. The source reports ASTM D2893 for LOI; its identifier is inconsistent with the oxygen-index standard and is preserved as reported without a compliance claim. Resin-preheat duration is unresolved; tensile-only optimization specimens are not additional pairs.
- Glass-fabric epoxy control/6%graphene/6%DDMDOPO: Table1 reports exactLOI and DTG peaks for final slab pieces in pureHe. Source30Kmin/27mLminNTP/30-580C retained. Complete3-page officialSI contains microscopy, flame IR and VBB photographs, no extra pairs. Helium support preserves distinct gas conditions and source/fingerprint gates. HeO2 approximate peaks, ambiguous9%char basis, VBB mass loss and model kinetics are excluded.
- Complete FNF officialSI adds12 exactTG conditions for six felt-plate states, but HTG1 ramp is unreported and air methods incomplete. SeparateTG-FTIR20Cmin is not borrowed. FNF5 LOI28.2 versus28.8 remains held. Carbon-fabric epoxy Table7 TG facts and controlLOI26 remain held because the source gas composition conflicts; four additive LOIs are unlabelled bars and optimizedLOI39 has no matching TG. Six further main-text screens give zero pairs; no unreviewed-SI exclusion is claimed.

Input hashes, measurement fingerprints, source holds and per-paper queue save restart positions. The metadata library remains untouched and its fulltext root awaits confirmation. No source PDFs, HTML, XML, workbooks or private paths are published. Exact-head tests, scientific validation and snapshot CI are required before merge.

All205 offline tests, compilation and the scientific gate pass locally; snapshot SHA-256 `60ab7edad74e3d9b47abba27f3352fdd41445b4e2869a9d45a14da91eb0fb7c1`. PR #25 passed exact-head CI and merged; the publication checkpoint follows.


## b58 publication checkpoint

[PR #25](https://github.com/PolyFT/textile-tga-database/pull/25) merged at2026-09-30T20:36:50Z as `f39fceef21e0034a8ef3e9b76f5b93cbe227507f`. Exact head `7717019b65658900b56b55710eebdf37745344bb` passed [validation36773704691](https://github.com/PolyFT/textile-tga-database/actions/runs/36773704691):205 tests, compilation, scientific gate and committed-snapshot consistency. Main was independently read back:373 unique verified states,426 TG conditions,89 DOI, errors=[]. Snapshot SHA-256:`60ab7edad74e3d9b47abba27f3352fdd41445b4e2869a9d45a14da91eb0fb7c1`.

Six new pairs and zero evidence-only upgrades are published;18 partial facts and all source holds remain excluded. Do not repeat either completed source without new evidence. The live single-writer lease is recorded in source_verification_progress.json; refresh main, open PRs and source queue before another claim. The metadata library remains untouched and its fulltext root still awaits confirmation.


## b59 commercial textile inventory and MOF cotton

Twenty-two genuinely new sample states add twenty-two TG conditions from two original papers. Nineteen commercial textile materials use original Tables 3/4 at 15 C/min in air. The shared sample inventory and exact trade/material labels provide the identity bridge. TG specimen preparation is unreported, while LOI explicitly uses woven or knitted fabrics at 150-200 g/m2. These limitations and both assay-specific descriptions are preserved. Powdered flash-point specimens, ignition tests and DTA peaks are not TG data. Carbon and glass have no numeric LOI and remain excluded.

Three MOF cotton states use official SI Table S2 and exact main-text LOI, under nitrogen at 10 C/min. Holds retain air-ramp attribution, one-immersion LOI, conflicting UiO-only T5, PZS bath quantity, Rmax, percentage calculations and washed-state labels. Preparation and generic control identity are retained without inventing control pretreatment.

Independent exact-hash original-source review passed. Fulltext and SI files remain private. The b59 writer lease is released after exact-head CI, merge and postmerge verification.

## b59 publication checkpoint

PR #26 merged as `ea00abe1f3a9b3d3047fcefc9eda12ac2a2e6563`. Exact head `1d1532c3ff3cac1e1627e23d9129a81f823ee877` passed [run 36774577791](https://github.com/PolyFT/textile-tga-database/actions/runs/36774577791), including 213 tests, compilation, scientific validation and snapshot consistency. Main confirms 395 unique states, 448 conditions and 91 DOI, with no validation errors. Snapshot SHA-256: `a4c0447dedfb7b6081d1cb69bfdfd9e592a869466947737d757b4d9103baf473`.

All six postmerge and lease-release validation, rebuild and processing checks passed. The temporary materializer is absent and the single-writer lease is released. Prior helium support and source holds remain intact. Subsequent private drafts are not included in these counts; refresh main and source ownership before another publisher.

## b60 aramid/epoxy and glass/BMI source review

Four genuinely new laminate sample states add eight TG conditions from two primary sources; zero existing-pair evidence upgrades. Four elevated-temperature LOI observations are retained separately and add zero independent samples. The strict greater-than-500 milestone needs 102 further verified states.

- Aramid/epoxy: three plain-weave PFJ09 fabric laminates with0/2/5wt%EAD relative to epoxy. Complete officialTableS1 pairs exactLOI with T5, matrix/fiber DTG peaks and explicitly700C residue. N2/90mLmin/10Cmin/30-700C methods and final-laminate fabrication reviewed. PureEP/AF have no matchedLOI; DMAglass transitions, PCFCheat peaks, cone residues and unreported washing are not substituted.
- Glass/BMI: one20ply woven laminate, fiber volume60%, measured at five TG heating rates. Table1 exactTo/Tf/Tp inspected; Table5 ambient20CLOI47.8 inspected. N2/50mLmin/40-1000C. To has no percentage-loss definition and is notT5/T10; Tf is not a residue or scan endpoint. Four50/100/150/220CLOIs are assay observations, not aging states. Approximate60%char excluded; sourceMLRp unit/normalization remains unresolved andunconverted. No SI is listed.
- PlasmaPA66 uses TGA-derived thiourea add-on and curve-only decomposition data, not exact TGmetrics. Sorbitol/isosorbide cotton has ownTG/ISO15025/cone but only citedLOI. Deep-eutectic epoxy thermal data are matrix-resin measurements, not final glass-fabric laminateTG. These three main-text screens contribute zero pairs; SI review is not claimed.

Input hashes, measurement fingerprints and per-paper holds save restart positions. The metadata library remains untouched and its fulltext root awaits confirmation. Source PDFs, XML and supplements stay outside the public repository. PR #27 passed exact-head tests, scientific validation and committed-snapshot CI; publication details follow.

All216 offline tests, compilation and scientific validation pass; errors=[]. All448 prior condition fingerprints are unchanged. Snapshot SHA-256:`cd30817085dfc30aefafb5c8f6be7171a84d98c3647d3709d163632097fa1b07`. PR #27 passed exact-head CI and merged.


## b60 publication checkpoint

[PR #27](https://github.com/PolyFT/textile-tga-database/pull/27) merged at2026-09-30T20:55:17Z as `d00c8fef8d4b09d70b1d77ef66bf69337bbd6c65`. Exact updated head `650f88421f5d0277f8b337bfcd6c787636866c99` passed [validation36775860963](https://github.com/PolyFT/textile-tga-database/actions/runs/36775860963):216 tests, compilation, scientific gate and committed-snapshot consistency. The b59 publication checkpoint and unrelated literature harvest were preserved during conflict resolution. Main independently confirms399 unique verified states,456 TG conditions,93 DOI and errors=[]. Snapshot SHA-256:`cd30817085dfc30aefafb5c8f6be7171a84d98c3647d3709d163632097fa1b07`.

Four genuinely new pairs, eight TG conditions and zero evidence-only upgrades are published. Four additional hot-LOI observations remain separately recorded, not additional states. All three postmerge checks passed. Do not repeat these completed sources without new evidence. Refresh the live lease in source_verification_progress.json, main, open PRs and the source queue before another publisher. The metadata library remains untouched; its fulltext root still awaits confirmation.


## b61 FYR/NMA cotton and DMMEPN silk

Thirteen genuinely new sample states add twenty-four TG conditions from two original papers. Eleven cotton states have exact Table 1 LOI and Tables 2/3 nitrogen Tmax/R600 at 10 and 20 C/min. Multiple ramps count as one state. The 100 C prehold for 20 min and the final ramp are recorded separately. NMA-4 LOI21.4 versus21.5 remains held; DTA peaks and source To/Tf are not substituted for DTG or percentage-loss metrics.

Two initial DMMEPN silk states use Tables I/II and the explicit Figure 4 treated-state bridge. Modifier and silk DTG stages remain distinct; Td11 is not T10, and incineration residues are not TG. The normalized add-on discrepancy and unmatched loading/wash states remain held. Independent original indexed-text review passed; unavailable PDF pixel review is disclosed.

Complete main and official SI review of research.0910 found precursor TG and gas spectra, without matched numerical textile TG; it remains excluded. Source fulltexts remain private. All 224 tests, compilation, scientific validation and exact-head snapshot CI passed. PR #28 merged; all three postmerge checks passed and the writer lease was released.


## b61 publication checkpoint

[PR #28](https://github.com/PolyFT/textile-tga-database/pull/28) merged as `e9c712fb5e8b835fd2e8701dac5ba4d75bcf957a`. Exact head `c0297963e2061a232b0ebcb1f6d8dd2924560d97` passed [validation 36776768369](https://github.com/PolyFT/textile-tga-database/actions/runs/36776768369), including 224 tests, compilation, scientific validation and committed-snapshot consistency. Main independently confirms 412 unique states, 480 TG conditions, 95 DOI and errors=[]. Thirteen genuinely new states add 24 conditions; repeated cotton heating ramps add no independent states. Snapshot SHA-256: `6e4520922b7352512b277729a5589c9e72f69ada01ff914ec964a3d73a96f4f5`.

Postmerge validation, processing and rebuild runs 36777382809, 36777382841 and 36777382968 passed. The writer lease was released through compare-and-swap. Refresh the live progress JSON, main, queue and open PRs before another publication. Source fulltexts remain private.


## b62 ramie-fabric epoxy laminate source review

Four genuinely new independent samples add four TG conditions from one original paper; zero evidence-only upgrades. Original Table1 p4, Table3 p10 and complete official two-page supplement reviewed. All four final twelve-ply ramie-fabric laminates have same-row exact T10, explicitly800C char and LOI. TG is N2/25mLmin/20Cmin/25-800C; neither TG-IR10Cmin nor DSC ramps are substituted. Decimal Table3 temperatures take precedence over rounded discussion.

Rmax has unresolved column/unit meaning and remains unconverted, never guessed as Tmax. Exact formulation masses remain as reported; inconsistent FPDpercentage/resin-content statements are flagged without inferring whole-laminate loadings. LOI thickness is unreported and is not borrowed from the vertical flame test. Preparation rinses are not durability wash states. SI contains FPD NMR and solubility figures, no extra material tests.

ED22 glass-laminate LOI cannot yet be assigned across its two curing systems/thicknesses. Ground plant-fiber phenolic slabs await scope clarification. CNF/PANI aerogel original SI and exactTG facts remain pending. These three holds add zero verified samples. Source caches stay outside the public repository and the metadata library stays untouched. Strictly exceeding500 requires85 more verified independent samples after this batch. Exact-head tests, scientific validation and committed-snapshot CI must pass before merge; independent main readback precedes lease release.


## b63 SIAM coaxial wet-spun aramid sensing fiber review

One genuinely new independent fiber sample adds one TG condition; zero existing-pair evidence upgrades. Original main and complete official supplement reviewed. Section4 p18 explicitly reports ownLOI41.5%; Section3.3 p9 reports56.12wt%genericTGresidue. OriginalFigure3 p10 inspected. Nitrogen/10Cmin/30-800C fromSection2.4 p5; default30s firstcoagulationbath fromSection3.4 p11. Generic residue temperature remains blank rather than inferred as800C fromscanendpoint. MaximumDTGrate isnotTmax. ANF/AMcontrolLOI bars have no printedvalues and are not estimated; othercoagulationdurations lack matchedTG/LOI. MissingLOIprotocol/finaloxide-AgNWloadings andsourcefigurelabel inconsistencies remainexplicitlimitations.

Six other sources addzero pairs: completeCNF/PANISI lacksTGgas; completeACSramieSI has6BLstates/12N2-airTGconditions but lacksheatingrate andmain403; PI2792main hascomposition/LOI/form conflicts withSIpending; washing-fabric19010044 is a review with no ownpairs; Heliyoncotton37120 hasonlycitedLOI/noownTG; RSCc6ra00067c TGnumeric/ramps andSIreview blocked by403. Per-sourceholds preserve progress and avoidrepeatqueries. Strictly exceeding500 requires84 additionalverifiedsamples. Publicfacts/provenance only; privatecaches remainoutside andmetadata libraryunchanged. Exact-headtests/scientificgate/snapshotCI and independentmain readback precedeconditionallease release.


## b64 CN-3, EHP/MHP and mono-substituted CN cotton sources

Thirty-seven genuinely new sample states add thirty-seven nitrogen TG conditions from four original papers. CN-3 contributes eight twill/print-cloth states, EHP/MHP contributes eight twill states, and mono-substituted CN contributes four twill states. Exact table LOI means, reported uncertainties and R600 are retained. Author-defined onsets stay separate from DTG maxima, percentage-loss metrics and MCC heat-release temperatures. Methods give nitrogen at 10 C/min and 60 mL/min, with source-specific recipes and initial post-cure wash state.

Whole-paper screening preserves contradictory controls, unmatched washes, repeated CN-1 comparison observations and inconsistent caption aliases as holds. The EHP20 second onset remains withheld. The separate piperazine2014 paper lacks an explicit standalone TG ramp and is excluded; a referenced TGA-FTIR method is not silently inherited. Seventeen initial wool/polyamide states from a fourth paper pair exact Table7 thermal metrics with Table13 LOI. Their nitrogen ramp is20 C/min, residue is explicitly810 C and the two colemanite preparation methods remain distinct. Five-cycle washed TG observations lack washed LOI and stay excluded. Independent original-source review passed at exact draft hashes, including official ACS SI TableS2 and original wool/polyamide PDF table pixels. Main author text access and unavailable PDF pixel review are stated accurately. Source fulltexts remain private.

All 238 tests, compilation, scientific validation and exact-head snapshot CI passed. PR #31 merged; all three postmerge checks passed and the writer lease was released.


## b64 publication checkpoint

[PR #31](https://github.com/PolyFT/textile-tga-database/pull/31) merged as `e1bcd504499fb54fb384fd506c37972a4f416621`. Exact head `0ca912840351812eaa3d8ba730908bd3c36c67ab` passed [validation 36782087584](https://github.com/PolyFT/textile-tga-database/actions/runs/36782087584), including 238 tests, compilation, scientific validation and committed-snapshot consistency. Main independently confirms 454 unique states, 522 TG conditions, 101 DOI and errors=[]. Thirty-seven genuinely new states add 37 conditions; washed observations without matching LOI and reused comparison data remain excluded. Snapshot SHA-256: `39dab74ac89fada184b53ad0cfd1d88fbf570fd9d50a87af8090f6cebda9c20f`.

Postmerge processing, validation and rebuild runs 36782212667, 36782212690 and 36782212708 passed. The writer lease was released through compare-and-swap. Refresh the live progress JSON, main, queue and open PRs before another publication. Source fulltexts remain private. The strict greater-than-500 milestone requires 47 further states.


## b65 original fibrous aerogel batch

Three genuinely new states / three TG conditions / zero old-pair evidence upgrades. Two directional aramid fiber-network aerogels (ANFs/ACMCA, DOI10.1007/s40820-025-01728-x) have ownLOI27/31 fromSection3.4p12 and exactTmax551.135/545.108C plusR80033.57/36.92 fromofficialTableS1. Nitrogen/10Cmin explicitlyreported inSection2.5p4. Method30-100C range conflicts with hightemperatureTG; canonical scanendpoints remain blank. RawTi retained withcontradictory95%weight-lossdefinition, neverconvertedtoT5/Tonset. Peakrateunit andsolventratio conflicts preserved; no normalizedpeakrate or inferredsolventvolume.

One standalone ANFs/MMT aerogel fiber shell material (DOI10.1007/s40820-023-01200-8) has ownLOI33.1 and genericTGresidue58.5 fromSection3.3p9/Figure3, nitrogen/10Cmin fromSection2.5p5. Genericresiduetemperature unknown; nofixed-temperatureR inferred. Shellmaterial TG isnotassignedtofullcoaxialTEfiber. PureANFs unlabelledLOI, approximate~35 n/p/fullfiberLOI, SIcores andwashed electricalperformance remainheld. Completeoriginalmain/SI forbothsources reviewed; originalFigure3pixelsandTableS1cellstructure checked.

ANF/silica source10.3390/polym15010141 held: nitrogeninmethods vs oxygeninmain/SI TGcaptions. LM/alginate10.1002/advs.202303406 mainhasnoexactTGmetrics andSIaccesspending. Holds/queue preserved. Latestmain b64 andallpriorfingerprints remainunchanged. Proposedtotal457; strictlyexceeding500 requires44more. Metadata libraryuntouched; publicfacts/provenance only, fulltextcaches outside. Exact-headCI andindependentmainreadback remainpublicationgates.


## b66 bacterial cellulose textile sources

Nine genuinely new sample states add twelve TG condition records from three original papers. Four plant-treated or control states supply seven nitrogen/air observations at 800 C; two zein/gluten and three marine-powder states supply nitrogen residues at 1000 C. These are nanofibrous sheet textiles developed as leather substitutes. Repeated atmospheres count as conditions of the same prepared state.

Original fulltext methods, exact thermal prose and LOI tables establish sample identity, treatment, ramp and atmosphere. Spinach preparation pH conflicts, unmatched screening doses, potentially reused controls and curve-only residues remain held. Entrapment-only marine dose screening is distinct from the admitted crosslinked final specimens. Source-specific access and review limitations are retained, and all fulltexts remain private. Independent review passed at exact draft hashes.

Published through PR33 at merge 7b0797a02853e22184cc7204ee7843ab0d2b1cb6. All 247 tests, exact-head validation and snapshot consistency passed at 89ff41c39b305242365eb060922f42e58ffd81a3. All three postmerge workflows passed, and the writer lease was released. Snapshot SHA256: e2299167e8f466ddd3c7135b08a95edb64adbcfcc061e324b781ab6e1a38973f.



## b67 citrus BC and SMSN jute sources

Four genuinely new sample states add four nitrogen TG observations from two original papers. Two citrus peel-crosslinked bacterial cellulose textiles retain exact final residues with unspecified assessment temperature; the 800 C scan endpoint is kept separately. Control and 8% SMSN jute fabrics retain exact residues at 500 C. Source-specific preparations, textile forms and method limitations are explicit.

Potentially reused BC controls, unmatched dose screens, washed color-fastness specimens and unpaired jute concentrations remain held. Original-source review passed at exact draft hashes; source fulltexts remain private.

Published through PR34 at merge 79172e84229ff1b5d0be47579f15aa5174cb935b. All 253 tests, exact-head validation and snapshot consistency passed at 797a48c288d31ba5defd6af0161b363832943feb. All three postmerge workflows passed and the writer lease was released. Snapshot SHA256: b47a6cdee86b2fbb5747b297c145c5d943f69517f896540321b72a552b1aed77.


## b68 PLA nonwoven source review

Two genuinely new states and two verified nitrogen TG conditions, with zero evidence-only upgrades (DOI10.1016/j.jclepro.2020.124497). Own PLA LOI18.3 and PLA/25%APTris LOI30.0 in Section3.4.1 match Table3 experimental T10/T50/Tmax/R800. Section2.4.6 reports N2/10°C/min and6±1mg; Section2.4.2 reports nonwoven LOI specimens15×6cm² and five repeats. Complete primary main XML and official DOCX SI were reviewed; original Figure5a and SI FigureS2 were inspected.

All five formulations are retained in both TG atmospheres (ten input rows). Two air pair rows remain condition-partial because the SI does not independently state the air ramp; mass/instrument metadata are also withheld for air. Three intermediate formulations in each gas remain TG-only because their LOI bars have no printed exact values. No LOI calculation from relative improvements, calculated-char substitution, cone/MCC substitution, or extra independent states for air.

Twenty additional primary-source screens retain their specific recovery gates and SI review status. SA/PADL co-produces films and fibers without a clear fire-test form crosswalk. Bicomponent PLA TG tests only as-spun fibers while LOI tests thermally bonded nonwovens. RTM MRP residue30.9 is author-calculated relative to the organic fraction, rather than measured whole-laminate residue; control LOI is approximate. POD methods10°C/min versus discussion20°C/min remain conflicting. Other sources lack their own LOI, TG, exact values or same-form mapping. These screens add zero verified pairs.

[PR35](https://github.com/PolyFT/textile-tga-database/pull/35) merged as `bb1738f4dab1d52779625a4fa9124f5203c67880`. Exact head `70c12a69a1a2bf3561ba82a908ed24ae07be7deb` passed [run36787271745](https://github.com/PolyFT/textile-tga-database/actions/runs/36787271745), including255 tests, compilation, scientific validation and committed-snapshot consistency. Postmerge runs36787377032/36787377087/36787377108 all passed. Independent main readback confirms472 states/543 conditions/109DOI and errors=[]. All541 prior master rows are unchanged across every common field. Input snapshot hash:`39146f0262a8bef010e8402b281b9a26c69eda0eb480c3b91a01ac96a403ff60`; master CSV hash:`514bb4f11914b4dc084e13230fd362db2e28a35d7ef539e23dc2ff5af5a3e9d4`.

Strictly exceeding500 requires29 more states; reaching2000 requires1528. Public facts and concise DOI locators only; the metadata library remains untouched and its root selection awaits user confirmation. Refresh main, open PRs, source queue and lease before the next publication.



## b69 casein, nylon/cotton and SHP cotton sources

Thirteen genuinely new sample states add thirteen nitrogen TG conditions from three original papers. Four casein-coated or control cotton states use20 bilayers with distinct bath concentrations; four nylon/cotton states distinguish zero to three spray layers; five cotton states preserve source-specific SHP/MA/TEA/TiO2 recipes. Exact LOI, author-defined onsets and residues at600 C are retained.

Reported LOI uncertainties retain their original definitions. Ambiguous TG/DTA maximum temperatures, MCC temperatures, unmatched durability washes and unresolved preparation details are held or explicitly left unknown. Independent original-source review passed at exact draft hashes. Source fulltexts remain private.

Published through PR36 at merge 618c0656c078ea881678820d45837e8241f57201. All 261 tests, scientific validation and exact-head snapshot consistency passed at 79d50ca3e63504a1cdd829de3323dcf15a8f049f. All three postmerge workflows passed and the lease was released. Every digest input blob and the entire local report were reconciled to the public branch before merge. Snapshot SHA256: 6e2e55e9521fe7bdc80dde737871304ae35263b730be2c57a22f5b83d0f90849.



## b70 boron coating and LPU comparator sources

Seven genuinely new sample states add nine TG conditions from two original papers. Two PAH/PSP/APB-coated cotton states retain separate nitrogen and air observations, the 120 C prehold, source T5 uncertainty and generic final residue. Five LPU-comparator cotton states retain exact source onsets and LOI; only the control residue is explicitly assigned to 700 C. Other residue assessment temperatures remain unknown.

Three named LPU variants conflict with prose LOI and stay held. Unmatched conditioned specimens, missing comparator recipe details and gas-purge distinctions remain explicit. Seven additional source screens preserve missing thermal conditions, bulk-to-fabric mismatches, source contradictions and unavailable originals as holds. Independent original-source review passed at exact draft hashes; all source fulltexts remain private.

B70 merged in PR #37 after all 267 tests and exact-head snapshot validation passed. Main contains 492 verified sample states, 565 TG conditions and 114 DOI sources. All three postmerge workflows passed; the writer lease was released. Three additional wool states have independent original-source approval and remain queued for a later data batch. A separate source-identity schema change is planned before any non-DOI proceedings can be admitted.


## b71 Fiber network and woven laminate source review

Nine genuinely new independent states add twelve TG condition records; zero existing-pair evidence upgrades. Complete original main text and all listed numerical supplements were reviewed for the accepted sources. Source PDFs and private paths remain outside this public repository.

- DOI 10.3390/polym17172377: all five BC/BS/BSM initial ambient-pressure-dried BC fiber-network aerogels pair own Table 2 TG with Table 3 LOI. Air at 10 C/min. Low-temperature T5 represents total mass loss in the moisture stage, never decomposition Tonset; main decomposition Tmax remains distinct. Table 2 char is generic residue with unknown assessment temperature, not inferred R600. MMT loading basis is the wet mixture. Complete six-page SI reviewed.
- DOI 10.3390/polym12102379: three initial woven-fabric PBF-a laminates (glass, basalt and carbon), each at nitrogen and ambient-air TG conditions, pair exact own LOI in Section 3.3.1 with Tables A4/A5 T10 and explicitly800C char. T2 preserved separately, not relabelled. Whole-laminate residue, volume-fraction composition and curing cycle retained. Neat resin and literature comparator data excluded from textile target. Complete original Appendix reviewed.
- DOI 10.1007/s42765-022-00231-x: one initial ionic solution blow-spun Nomex membrane pairs own air T5=376C with LOI28.39 and source-reported sigma0.152709. Complete36-page SI supplies TG-specific10C/min and LOI TableS2/S3. Six repeated splines are one state. PrintedT95 means95% mass remaining; argonDTA and nitrogenDSC are separate assays. Filtering, aging, acid and washing variants lack own pairs.

Twelve further source holds preserve failed access, original SI read status, form/condition conflicts, cited rather than own LOI, or absence of TG. CSNF-DACMC full main and SI contain MCC heat-release Tmax302C, which is not TG; it remains excluded. No abstract, graph estimate or candidate is counted toward the target.

Proposed total: 501 independent states, 577 TG conditions and 117 DOI. Strictly exceeding500 needs 0 more; reaching2000 needs 1499. Exact-head CI, normal merge and independent main readback must precede lease release.
