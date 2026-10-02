# Source verification progress — 2026-10-02

The reviewed dataset contains **1000 unique reviewed source/sample/washing states**, **1251 TG condition records**, and **283 original sources (281 DOI sources and 2 registered non-DOI proceedings)**. The near-term target is 500 unique states; **0 remain**. The long-term target remains 2000.

## Batches

- b38: 60 reviewed states, represented by 67 TG conditions. Of these, 15 were genuinely new or newly completed pairs and 45 were existing states upgraded with source evidence
- b39: 81 additional reviewed states, represented by 97 TG conditions. Of these, 56 are new-source or newly completed pairs; 25 are existing states upgraded with source evidence or missing conditions
- b40: 21 additional reviewed states and 31 conditions, comprising 5 new alginate/aramid/PTFE laminate states and 16 existing states with verified source evidence
- b41: 59 additional reviewed states and 59 conditions from seven papers; all 59 were existing numeric sample states upgraded with primary-source evidence. There are zero genuinely new scientific states in this batch
- Cumulative: 799 new/newly completed paired states and 201 existing paired states with upgraded evidence
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


## Reviewed source identity schema

PR #39 introduced an optional, registry-bound identity path for original conference proceedings without DOI identifiers. All 292 tests, exact-head snapshot CI and four postmerge workflows passed. The accepted master remained byte-identical at 501 sample states, 577 conditions and 117 DOI sources; no new observations or registered sources were added. The code-review mirror collision was fixed and regression-tested before merge. The writer lease has been released. Later source batches must independently register each original document and bind every observation review to its exact provenance; DOI and non-DOI cohorts remain separate.


## b72 Local greige nonwoven and PAN woven source review

Six genuinely new independent states add six verified TG conditions; zero evidence upgrades. Two complete locally held published primary articles were reviewed with original numerical table/prose pixels. Neither primary lists supplementary materials; publisher external inventories were inaccessible(403), so no claim is made that unidentified external files were inspected. All admitted numbers/methods and preparation are in the primary. Source caches and private paths remain outside the public repository and the library stays read-only.

- DOI10.1016/j.polymdegradstab.2011.08.014: initial uncured Untreated,D1U2,D2 greige100g/m2 cotton nonwoven. Exact ownLOI21.6/30.0/30.0 in p.2015 Section3.1 pairs originalTable3 celluloseTp and explicitly600C char at nitrogen5C/min.0.8%P/3.4%N maps uniquely byTable1 toD1U2; char-lengthD1U3 typo and high-P1.6/1.7 descriptors retained. All11TGrows preserved,8unpaired. SourceTu urea peak andTf end temperature are not onset/extra peak. Parentheses areSDofthree runs; WLu headerunit inconsistency retained. D2D4 label unresolved. Bench furnace18C/min is notTGA. This resolves the previous original-fulltext access hold; no kinetics extrapolation used.
- DOI10.1016/j.apsusc.2017.09.155: initialPAN,A-PAN,P-A-PAN plain-woven400g/m2 fabrics pair ownTable2/TG nitrogen10C/min andTable4 zero-cycleLOI18.1/25.2/34.1. Water-removal86/93C sourceTmax1 kept separate; sourceTmax2/3 numbering retained. A-PAN residue47.39vs47.59 withheld from cleanR800. PA reagent identity wording conflict retained. GenericfiberLOI17 is not ownfabric18.1. WashedLOI5/10/20cycle labels32.3/31.4/29.8 lack matchedTG and are not extra pairs.

Four further source holds cover graph-onlyTG/LOI, MCC/PCFC substitution, manuscript figure/caption or scan-range conflicts, and unavailable listedSI/unresolved formulation links. Proposed total:507 independent states/583 TGconditions/119 DOI; 1493 remain to2000. Normal exact-head CI, merge and postmerge readback required.


## b73 original textile sources and registered proceedings

This batch adds 29 genuinely new sample states at 33 TG conditions: 21 states from eight DOI sources and eight states from two official conference proceedings. The complete inventory now contains 536 reviewed sample states and 616 conditions. The DOI cohort contains 528 states from 127 DOI sources; the non-DOI cohort contains eight states from two independently registered original documents.

All numerical evidence, preparation and condition mappings passed independent original-source review. Contradictory residues, unmatched wash states, uncertain endpoints and possible reused controls remain held. The OPF refinement admits only its explicit low-temperature T5; it does not repair the conflicting residue temperature. Fulltexts remain private.

B73 merged in PR #41 after all 302 tests and exact-head snapshot validation passed. All three postmerge workflows passed and the writer lease was released. Main now contains 536 reviewed states and 616 conditions from 129 sources: 127 DOI sources and two registered proceedings. The non-DOI cohort has eight states; original documents remain private. Nine separately identified author-preprint states have independent science review and remain queued for a later batch with explicit publication-type reporting and final-version reuse holds.


## b74 Original local cotton and wool review

Eleven genuinely new independent sample states add21 TG condition records from five complete original manuscripts; zero existing-pair evidence upgrades. All32 exact source TG rows retained, with11 unpaired rows excluded from target. Source/sample/wash states are counted once across atmospheres. Accepted batch is entirely DOI-backed; existing eight non-DOI states and two proceedings sources are preserved separately. Original text, tables, captions and references read; printed numerical pages viewed. No listed SI in main or distinct matching local supplement; external supplemental inventories not inspected. All source caches and private paths remain outside the repository, and the library remains strictly read-only.

- 10.1016/j.polymdegradstab.2020.109312: three initial TTPBD-treated cotton states/six nitrogen-air conditions. Table1 LOI23.5/26.3/27.5 and Table2 TG. ControlLOI28.5 contradicts increasing-from-control prose and is held, not silently corrected to18.5. Bath10/20/30wt% differs from dry add-on7.0/13.2/17.6%. Reagent and control residue-at-Tmax discrepancies retained. WashedLOI has no matchedTG.
- 10.1016/j.polymdegradstab.2020.109101: untreated wool, initial WS20B5, and exactly30wash WS20B5; six conditions. Table1/Table6 LOI25.0/36.0/29.6 with source SD and three repeats. Table5 T25/T50/T75 are percent-weight-loss thresholds, not DTG peaks. SourceS20B5 alias linked by unique20%SA+5%BTCA recipe; native label retained. Isothermal250C TG has no LOI and is distinct from240C FTIR pretreatment; both isothermal conditions held. No laundering-equivalence assumption.
- 10.1016/j.polymdegradstab.2015.07.003: own untreated cottonLOI18.8 pairs Table1 Ton-set297C/Tmax358C/R60014%. Five treatedTGrows held for concentration/add-on/catalyst mapping and25/30% LOI branch discrepancies. Actual optimized23.7%add-on not assigned to25%TG. Vertical-burning char and washedLOI not TG substitutes.
- 10.1016/j.polymdegradstab.2019.04.024: one untreated cotton state/two conditions. Own18.5LOI pairs printed N2R7007% and air28.76%residue at372C.372C is an explicit residue assessment temperature, not assignedTmax. About-values and generic treatedTG cannot be mapped to18/23/26%WG. No curve estimates.
- 10.1016/j.polymdegradstab.2020.109302: Cotton and CS/LS/cotton17.0/25.2%weight-gain states/six conditions. N2TG-FTIR20Cmin/25mLmin differs from airTG10Cmin/30mLmin. T5 moisture threshold is not onset; Rmax is%/min. LS-only17.1%LOI24.7 versus26 conflict holds bothTGrows. CottonN2R70013 versus12.5 withheld; CS/LS25.2char27 versus27.1 preserves table integer precision. No guessed layer counts or component ratio.

Proposed total:547 states/637 conditions/132 DOI sources plus2 non-DOI sources; 1453 remain to2000. Exact-head CI, normal merge and independent postmerge readback required.


## Publication-type reporting verification

PR #43 added explicit publication-type source, sample-state and condition totals without changing observations or source identity. All 321 tests and exact-head validation passed. Merge d6953b405dcc5378cef47dbb74d240bfef465217 passed validation, master rebuild and processing checks. The complete master remains byte-identical, with 547 states, 637 conditions and 134 sources (132 DOI sources and two registered proceedings). Current metadata labels 132 sources unspecified and two proceedings; zero explicitly marked preprints does not establish absence of legacy preprints. The reporting writer lease has been released.


## b75 Original local cotton and polyester review

Four complete primary texts reviewed. Three accepted DOI sources add **14 genuinely new independent sample states and 14 TG condition records**; zero old-state evidence upgrades. All16 native TG rows retained, with2 unpaired rows excluded. Source-native thresholds, stage order, uncertainty and preparation recorded; printed numerical/method pages viewed.

- 10.1016/j.polymdegradstab.2017.11.018: six initial145g/m2cotton states. Table3 TG and directly printed Figure6 LOI18/18/19.9/24.6/21.4/27.7; extra2HC has no recipe/LOI and stays TG-only. Synthetic air60mL/min,10C/min,700C endpoint; composition fractions not reported. T1/T5/T10 are mass-loss thresholds, not decomposition onsets or moisture peaks. Bath concentrations1/5/10wt% differ from dryadd-ons3.3/8.6/15.9%; silica/mercerization routes remain distinct. LOI +/-0.5 is experimental error, notSD. PCFC and five-wash data do not supply same-state TG/LOI.
- 10.1016/j.polymdegradstab.2016.02.009: four initial semi-bleached twill cotton states, Table2 LOI18.2/20.5/21.2/24.5 and Table3 TG atair20C/min. Native Tonset5% mapped only toT5, Vmax negative%/min retained, R600explicit. Bath50/100/200g/L versus dryadd-on5.4/9.4/18.7%; own control phosphorus0.79mg/g. Complete official SI reviewed: text/captions/allfour NMR-FTIR figures, no additional TG/LOI. COT-Si11.4 and washed1/5/30cycleLOI not paired with initialTG.
- 10.1016/j.polymdegradstab.2019.109028: four initial polyester fabric states, Table2 explicitT5/Tmax and Table3 LOI21.2/27.2/28.1/28.8 atN2/10C/min/50mL/min. One/two/three dips remain distinct; exact control alkali history unknown. Figure3/table endpoint ordering and rate-unit conflicts leave all endpoint/peakresidues and Vmax outside clean fields, retaining original table facts and notes. DPP has three nativeTGpeaks but no ownLOI and stays TG-only. Ten-washLOI has no matched TG.
- 10.1016/j.polymdegradstab.2020.109286: zero accepted states. Complete primary review held because TG wool fibers versus LOI fabric lack proven form correspondence; nitrogen residue37/38% also conflicts. Fifty-washLOI has no same-stateTG.

Explicit journal-article metadata corroborated by original publisher covers for the three accepted sources; manuscript version is recorded separately. Legacy missing-type cohorts and registered proceedings remain unchanged. No independent reviewer or curve-digitization claim. Fulltexts, SI and private paths remain outside repository; the library remains strictly read-only. Proposed total:561 states/651 conditions/135 DOI sources plus2 non-DOI sources; 1439 remain to2000. Normal exact-head CI, merge and independent postmerge readback required.


## b76 original-source expansion with explicit preprint reporting

This batch adds 28 genuinely new sample states at 43 TG conditions from 10 DOI sources. Four author preprints contribute 12 states at 21 conditions and are counted explicitly as preprints. Related final journal versions remain source-wide alias/reuse holds until independent cross-version adjudication. The total is 589 states, 694 conditions and 147 sources (145 DOI sources and 2 registered non-DOI proceedings). No numerical evidence upgrade is counted as a new state.

All source drafts passed independent original-evidence review. Generic residues retain unknown temperatures, and assay-specific preparation remains explicit. Fulltexts remain private. The writer lease remains active pending exact-head CI and postmerge checks.


## b76 publication checkpoint

PR #45 merged as 05e8f3e5acb73c25dd883c626e48462744ea7934 after all 338 tests and exact-head validation passed. The complete remote report and 23 relevant file blobs matched the reviewed local snapshot. Postmerge validation, master rebuild and processing checks all passed; the writer lease has been released.

The accepted total is 589 sample states, 694 TG conditions and 147 sources (145 DOI sources plus two registered proceedings). This batch adds 28 genuinely new states and zero evidence-only upgrades. Four explicitly labelled author preprints contribute 12 states and 21 conditions; their related final journal versions remain source-wide reuse holds. All 651 previous condition records retain identical values in every existing field. Original fulltexts remain private.

Snapshot SHA-256: 71c7fc5865d0995d9f89c05463b66be9d6e0c7a3bbc64ad4867f8ad6ddf96ad3.


## b77 Original local polyester, cotton and viscose review

Three complete original journal sources add **12 genuinely new initial textile sample states and 21 TG conditions**, with **zero evidence-only upgrades**. Four TG-only rows remain outside the target; all 25 native TG rows are retained. Nitrogen and air measurements count once per independent sample state. Complete official ACMPEP and TSPDP supplements were reviewed, including every embedded figure, caption and table; neither supplies additional TG–LOI pairs.

- 10.1016/j.polymdegradstab.2019.108998: six coated polyester states and nine conditions. Table 1 LOI values match the exact recipes and bilayer counts in Tables 2–3. Uncoated polyester has LOI=N/A and is excluded. Native Tonset10% is stored as T10; missing degradation stages retain their positions. Residues are reported at 600°C. The 100°C/30 min TG prehold and original mL/s purge units are preserved. Nitrogen GSM peak 2 conflicts between table (390°C) and prose (385°C), so the clean peak field is withheld.
- 10.1016/j.polymdegradstab.2019.04.009: two initial woven cotton states and four conditions. Section 3.1 restricts TG to the 30% ACMPEP treatment; Table 7 initial LOI values are 17.8/42.0. Bath concentration (30%) differs from weight gain (33.4%). Fabric residue is explicitly assessed at 760°C, not 800°C. Other bath concentrations and washed LOI states lack matching TG. Pure-compound TG rows have no LOI. Missing catalyst amount and drying temperature remain unspecified.
- 10.1016/j.polymdegradstab.2021.109620: four initial viscose fabric states and eight conditions. Table 1 TG matches the numerical table embedded in Figure 4 (LOI 18.0/22.4/25.1/26.8). Bath concentrations differ from weight gains. R700 and residue at Tmax are distinct; preparative rinses are not durability washing. The original NMR discrepancy is documented. Missing LOI repetitions, TG mass/flow and fabric construction are not guessed.
- 10.1016/j.polymdegradstab.2016.03.003: a fourth complete primary source is held, with zero accepted states. LOI 71.2 versus 71.6, a possible instrument ceiling, ambiguity between one- and two-step treatments, and possible control reuse require resolution. Dry-cleaning MCC measurements do not provide durability TG–LOI pairs.

Publication types and source versions are explicit; no independent second-reviewer or curve-digitization claim is made. Fulltexts, supplements, caches and private paths remain outside the repository; the library is strictly read-only. All 343 tests pass, the validator reports no errors, and all 694 previous condition records retain identical values in every existing field. Proposed total: **601 states / 715 conditions / 150 sources**; **1399 remain** to 2000. Exact-head CI, normal merge and independent postmerge readback are required before releasing the publication lease.


## b78 original-source expansion with explicit preprint reporting

This batch adds 19 genuinely new sample states at 31 TG conditions from 5 DOI sources. Explicit author-preprint contributions are 3 states at 3 conditions from 1 sources. Related publication versions remain source-wide alias/reuse holds until independent cross-version adjudication; additional later controls are held only at their exact sample labels. The total is 620 states, 746 conditions and 155 sources (153 DOI sources and 2 registered non-DOI proceedings). No numerical evidence upgrade is counted as a new state.

All source drafts passed independent original-evidence review. Generic residues retain unknown temperatures, and assay-specific preparation remains explicit. Fulltexts remain private. The writer lease remains active pending exact-head CI and postmerge checks.


## b78 publication checkpoint

PR #47 merged as 1be0c8558ebc96aaa6ca31540d5375128dd62f4b after all 351 tests and exact final-head validation passed. All 18 relevant remote file blobs and the complete validation report matched the reviewed local snapshot. Postmerge validation, master rebuild and processing checks passed; the writer lease has been released.

The accepted inventory contains 620 sample states, 746 TG conditions and 155 sources (153 DOI sources plus two registered proceedings). This batch adds 19 new states and zero evidence-only upgrades. The explicit author-preprint cohort contains five sources, 15 states and 24 conditions. Source-version holds and sample-scoped later-control holds remain active; all 715 previous condition records preserve every prior field. Fulltext caches remain private.

Snapshot SHA-256: a071e0a580415b95406f2664c57f42e37a3db2e9124cb9d34de434e8c38d654d.


## b79 Original local cotton and wet-spun viscose review

Three complete original journal papers add **11 genuinely new initial sample states and 11 TG conditions**, with **zero existing-state evidence upgrades**. Twelve native TG rows are preserved, including one unpaired HPTP control outside the target. Original methods and numerical pages were visually checked; no curve estimates are admitted.

- **10.1016/j.polymdegradstab.2012.07.016:** three PEPBP cotton states at native add-on 0/5.0/21.2%, LOI 19.4/25.7/33.8, matched through Tables 1 and 2. TG is static air, 10 C/min, 100–600 C; residues at 500/550/600 C retain their native temperatures. Initial decomposition temperature is stored as Tonset with its unspecified definition, never T5 or T10. The printed add-on formula uses final mass in the denominator. The 30 wt% bath example is not assigned to every add-on. The 11.7% add-on has LOI but no matching TG.
- **10.1007/s12221-012-0718-3:** three initial HPTP viscose fibers, FRVF-3/4/5, at 12/16/20 wt%, LOI 28.4/28.6/34.7. TG is air at 10 C/min. TG maxima 272/267/262 C are distinct from DSC peaks. Residues 6.3/8.9/11.1% were assessed at *around* 590 C; that approximate temperature is preserved separately, with no clean R600/R800 field. Control LOI is not taken from a cited value or an unlabelled curve. Washed LOI has no washed TG.
- **10.1007/s12221-015-1005-x:** five initial PMEP viscose fibers at 0/5/10/15/20%, own unwashed Table 2 LOI 19/27/31/33/35 and Table 4 TG. TG is nitrogen at 10 C/min to 500 C. Residues belong to 500 C; DSC Table 3 is excluded. Native peak-rate values and unit/chemical-notation anomalies are retained without correction. Nominal additive percentage is not measured post-spinning retention. Durability-washed LOI is not paired with initial TG.
- Six additional sources are held in the batch manifest and review queue, with complete versus bounded review scopes explicit. AATMP cotton has a 700/800 C endpoint conflict and ambiguous TG recipe. PPy/PA cotton and DAP/urea nonwoven have powdered-TG versus fabric-LOI issues, with prior-source LOI reuse also unresolved for DAP/urea. Silk metal-salt TG lacks a reported ramp; wool PCFC residue cannot replace curve-only TG. The Cellulose fiber-blend source has complete official SI, including Table S2 and all seven embedded images, but TG form is not specified against its twisted-web LOI form; zero states admitted.

Publication types and foreign-source reuse holds are preserved. No independent reviewer is claimed. The public repository contains only factual measurements, concise DOI/locator evidence, tests and validation outputs; fulltexts, SI files, private paths and caches remain outside it. Proposed total is **631 states / 757 conditions / 158 sources**, with **1369 states remaining to 2000**. Exact-head CI, normal merge and independent terminal postmerge verification are required before release.

Local verification: **356 tests pass**, validation errors `[]`, compilation and diff checks pass. All **746 previous condition records preserve every previous field value**; only the eleven new conditions are added. Snapshot SHA-256: `3f8fe9e7c38db22124f86ddf47b05e90c0293e78b036b35bef868f895ab442e2`.


## b80 banana-peel and bounded licorice textile states

This batch adds 12 genuinely new sample states at 12 TG conditions from 2 DOI sources. Ten banana-peel-paper states and two distinct licorice treatments retain their exact residue temperatures of 880, 884 or 885 °C. Six later-source control/commercial labels remain held for reuse adjudication. Source recipe uncertainties and global atmosphere wording remain disclosed. The total is 643 states, 769 conditions and 160 sources (158 DOI sources and 2 registered non-DOI proceedings). No numerical evidence upgrade is counted as a new state.

All source drafts passed independent original-evidence review. Generic residues retain unknown temperatures, and assay-specific preparation remains explicit. Fulltexts remain private. The writer lease remains active pending exact-head CI and postmerge checks.

### B80 terminal publication checkpoint — 2026-10-01

PR #49 merged as `360694ec3b7be3474fa09d96a120032ab57e52bc` after exact-head validation run 36807013834 passed on `66311e73e4efc144612cd4193c080a63028d6fc1`. All 362 regression tests passed. Fifteen final-head files and the complete validation report matched the locally verified snapshot; all 757 prior condition rows retained every existing field. The three postmerge checks (36807287306, 36807287298, 36807287330) passed before release commit `d721ce7ed73e62a61f1861a40294d28c57697065`.

The admitted batch adds 12 new states and 12 conditions, bringing the reviewed total to 643 states, 769 conditions and 160 sources (158 DOI and two registered non-DOI sources). Explicit preprint counts remain five sources, 15 states and 24 conditions. The scientific snapshot is `c4988be3dfe9ad1fe49695cd9a38e8052e2ebf5892b4d3b7484dfb7303f3c249`. Original source documents remain private, and all conflicting metrics and six later comparator reuse holds remain excluded.


## b81 Complete original CS/PA, ACPMPA and SPMA cotton review

Three complete local original journal articles add **6 genuinely new initial independent sample states and 8 TG conditions**, with **zero existing-state evidence upgrades**. Thirteen native TG rows are preserved; three air conditions without an explicit ramp and two SPMA compound rows with source conflicts stay outside the target. Original method and numerical/figure pixels were checked. SPMA official SI was read in full, including six tables and its one embedded image. One reviewer; no independent-reviewer or curve-estimation claim.

- **10.1016/j.ijbiomac.2021.02.023:** three initial polyester/cotton65/35 fabric states Uncoated/PC-10BL/PC-20BL, LOI17.3/23.7/29.2, match Table1 and Table3 nitrogen TG at10C/min. Native10%loss is T10; stage1/2 maxima and residues explicitly700C retain their definitions. The method endpoint800C does not change R700. AirTable3 facts have no explicit own ramp and are held. The preparation heading PEI/PA onPET conflicts with consistent CS/PA blend body/title/materials; the discrepancy is explicit. Washed20BL24.8, otherbilayers and CONEchar are not substituted.
- **10.1016/j.ijbiomac.2020.11.022:** two own initial raw/35%ACPMPA-treated cotton states, LOI18.5/49.2 fromTable3, have fourTable1 nitrogen/airTG conditions at10C/min. This local original is a publisher article-in-press proof, not a final paginated version or an author preprint. The native35%bath has unknown percentage basis and differs from24%weightgain. Char values retain assessment697C forN2treated and656C foraircontrol; N2controlabove694C andairtreated genericresidue staytemperature-unknown, with noR700 inferred. Nativewaterstage endpoints,globalTmax andrates%/C remain distinct. N2treated stage3loss24.23Table versus26.96prose andwashed30/35%identity conflicts remain explicit.
- **10.1007/s42114-021-00348-4:** one initial UV-cured SPMA-5 cotton state at native20%add-on, LOI23.5, is matched by officialTablesS1/S2/S3/S5 andpublishedFigure5A. TG is staticN2,50-800C,10C/min,3-5mg; nativeTi182.7C is initialdecomposition with unspecifiedthreshold, notT5/T10. ItsR80026.1% andmaximumloss9.6%/min are tabulated. TwoSPMA/APP formulations retain native LOI26.5/29.8 and Table/prose swappedTi plus ambiguousFigure6C assignment, but are not approved. SPMA/APP2 washing-prose initial28 versusinitial29.8 is unresolved. Figure6C TGIR282C is not a SPMA5 peak; nonUV andwashedstates lackmatchingTG.
- **10.1016/j.cej.2021.130556** has complete primary text review but unreviewed critical SI formulations/airTG; official SI retrieval returns403. **10.1016/j.cej.2020.128361** has partial primary review and missing critical LOI/TG SI; both addzero states, with exact review limits in the manifest/queue.

Previous inputs and foreign source-version/reuse holds are preserved. Public additions contain factual data and concise DOI/table/figure locators only; source fulltexts, SI, images and privatepaths remain outside the repository. Proposed total **649 states / 777 conditions / 163 sources**, with **1351 states remaining to2000**. Exact-head CI, normal merge and independent terminal postmerge verification must precede release.


## b82 original-reviewed fiber and textile states

This batch adds 17 genuinely new sample states at 21 TG conditions from 4 DOI sources. Measured LOI is separated from char-derived calculations, conflicting TG metrics remain held, and every pair uses its own preparation and assay evidence. Related-source and unmatched-state reuse holds remain explicit. The total is 666 states, 798 conditions and 167 sources (165 DOI sources and 2 registered non-DOI proceedings). No extra atmosphere or numerical evidence upgrade is counted as a new state.

All source drafts passed independent original-evidence review. Generic residues retain unknown temperatures, and assay-specific preparation remains explicit. Fulltexts remain private. The writer lease remains active pending exact-head CI and postmerge checks.

### B82 terminal publication checkpoint — 2026-10-01

PR #51 merged as `5b99543efa26217c2bd5a1ad4ae82f9325cd5a79` after exact-head validation run 36810200610 passed on `7ce018c2592c1dd4ce85eb1831cbdf4a007309fe`. All 374 regression tests passed, including a run against the prior master before snapshot materialization. Source regressions read the reviewed incoming records so they remain independent of build order. Seventeen final-head files and the full validation report matched the local scientific snapshot; all 777 prior condition rows retained every existing field.

The three postmerge checks (36810453920, 36810453780, 36810453834) passed before writer-lease release `1f633570ede7d4408dd8577bb0f7a5bf95344867`. This batch adds 17 new states and 21 conditions, bringing the dataset to 666 states, 798 conditions and 167 sources (165 DOI and two registered non-DOI sources). Explicit preprint counts remain five sources, 15 states and 24 conditions. Snapshot: `fe66b456b36cca0aa06cf1d1abcec6f706cd563ed1ed6dad28e033f0685996bf`. Calculated LOI, conflicting metrics and unmatched or reused specimens remain held; fulltexts remain private.


## b83 Original cotton review: ASNDP, ABTMPA, Fe/DOPO, PLUEG and ASMPEA

Six complete local original primary articles were reviewed. Five sources add **10 genuinely new independent cotton sample/washing states, 20 TG conditions and zero existing-state evidence upgrades**. Thirty native TG rows are preserved, with **10 conditions outside the verified target**. Original methods, numerical tables and printed figure coordinates were checked. Official FR-LO SI (all paragraphs, TableS1 and four images) and ASMPEA SI (all labels and three spectra) were reviewed in full. One primary reviewer; no independent-reviewer or curve-estimation claim. Other four primaries list no SI; their external SI inventories were not inspected.

- **10.1007/s10570-020-03632-6:** own uncoated and 450g/L Cotton-ASNDP-4 initial states have four N2/air conditions. Tables1/2 and the explicit450g/L TG scope connect LOI18.6/29.5 to native Tonset, Tmax and R750. Native plus-minus values are retained without calling them standard deviations. IPDT1402.8 is a derived integral index, not a physical TG temperature. Other bath formulations and all washed states lack own TG.
- **10.1007/s10570-020-03615-7:** initial31wt% ABTMPA cotton adds one state/two conditions, LOI50.2. Native Figure5 printed coordinates resolve the shifted Table1 char row: treated N2/air char42.40/23.07 explicitly600C. Two control TG rows remain unpaired because initial LOI17.5 in Table3 conflicts with17.1 in prose. Native air Tmax295 is retained; stage boundaries and moisture losses are not T5/T10. Native LOI standard D3163-2000 is not silently corrected.
- **10.1007/s10570-020-03636-2:** own initial pristine cotton adds one state/two conditions, LOI18,R8008.25N2/7.8air. Pristine N2Tmax379Table/375prose and airT5337Table/325prose remain raw, with clean conflicting metrics blank. Four Fe-grafted/Fe@DOPO TG rows are held because preparation says60C6h in prose versus60C4h in Scheme1. The cited2019 precursor was read only for bounded recipe/control comparison; its assay values were not imported. DOPO-only and all washed LOI lack own TG.
- **10.1007/s10570-021-03714-z:** exact40% PLUEGD cotton initial and after50LCs are separately paired, LOI42.7/28.6, at four N2/air conditions. Figure7 explicitly prints T10, degradation-peak and600Cchar coordinates; no curve estimation. Native% bath/catalyst/NaOH bases are unspecified. Two own-control TG rows stay unpaired because LOI is only approximately18. PLU/PLUD and lower baths lack own TG.
- **10.1016/j.ijbiomac.2021.07.130:** four initial C0/FRC20/FRC25/FRC30 cotton states, LOI17.1/37.9/39.0/40.2, have eight Table3 N2/air TG conditions. Original Figure9Ia prints each exact initial LOI; Figure9Ib prints initial weight gains14.6/16.7/18.4. Table3 air second-peak residue header incorrectly prints Celsius: raw numbers and native unit are retained without assigning clean percent values. DSC conditions, ASMPEA-powder water peaks, CONE char and washed LOI are not substituted for fabric TG. Official SI contains only three spectra.
- **10.1007/s10570-020-03648-y:** complete original plus complete official SI review adds zero pairs. Table5 explicitly names TG cotton fibers while LOI uses cotton fabric; specimen-form equivalence is unresolved. Two native TG/LOI fact rows are held. SI literature comparators are not own new formulations. T10 and rapid-degradation Tend differ from onset and method endpoint; TG R70037.24 differs from MCC char36.8.

All previous inputs, source-version holds and scoped reuse holds are preserved. Fulltexts, SI, images and privatepaths stay outside the repository and the literature library remains read-only. Proposed total **676 states /818 conditions /172 sources**, with **1324 states remaining to2000**. Exact-head CI, normal merge and independent terminal postmerge verification precede owned lease release.


## b84 original-reviewed fiber and textile states

This batch adds 6 genuinely new sample states at 9 TG conditions from 4 DOI sources. Measured LOI is separated from char-derived calculations, conflicting TG metrics remain held, and every pair uses its own preparation and assay evidence. Related-source and unmatched-state reuse holds remain explicit. The total is 682 states, 827 conditions and 176 sources (174 DOI sources and 2 registered non-DOI proceedings). No extra atmosphere or numerical evidence upgrade is counted as a new state.

All source drafts passed independent original-evidence review. Generic residues retain unknown temperatures, and assay-specific preparation remains explicit. Fulltexts remain private. The writer lease remains active pending exact-head CI and postmerge checks.

### B84 terminal publication checkpoint — 2026-10-01

PR #53 merged as `b563eeba6d772fa16c1ba886ab03a35ed6238397` after exact-head validation run 36813443302 passed on `17a952482d078835cd3626e5eeab0afc3d50480a`. All 389 regression tests passed before snapshot materialization. Seventeen final-head files and the full validation report matched the local snapshot; all 818 prior condition rows retained every existing field. The three postmerge checks (36813768386, 36813768396, 36813768454) passed before writer-lease release `1c825a2417422879c4eab79b4298234bc994289d`.

This batch adds six new states and nine conditions, bringing the dataset to 682 states, 827 conditions and 176 sources (174 DOI and two registered non-DOI sources). Explicit preprint counts remain five sources, 15 states and 24 conditions. Snapshot: `25e3524d42754218827d432032c8a19e9f3939bf7e539ebdd4fe8295b9168d50`. Source-specific form limits, native stage numbering, undefined metrics, unmatched treatments and reused comparators remain explicit. Fulltexts remain private.


## b85 Cotton networks: complete original and supplement review

Five complete local original articles add **11 genuinely new independent initial cotton states and 14 TG conditions**, with **zero existing-state evidence upgrades**. All native methods and data tables/printed figure values were checked. Three complete official supplements were reviewed. Twenty native numerical TG rows and five curve-only sample fact rows are preserved; **six numerical conditions and all five curve-only states remain outside the verified target**. One primary reviewer; no independent-review or curve-estimation claim.

- **10.1007/s10570-020-03645-1:** own uncoated control adds one state/two N2/air conditions, LOI18.0. Table2 T5/Tmax and residue at Tmax remain distinct. Control airR800 is a dash and stays blank. Four HPAE3/BTCA3 conditions are held: main initial LOI29.4/29.0 conflicts with28.7 in washing prose/SI, while HPAE3 preparative rinse state and initial weight gains differ. Complete official TableS1 and VFT image do not resolve these issues. Other baths and washed states lack own TG.
- **10.1007/s10570-021-03716-x:** complete original and complete official SI add zero pairs. Figure5 explicitly prints initial LOI18.0/19.3/20.4/21.3/20.7 for five separate chlorination/chelation states, but TG metrics are only unlabelled curves. No curve coordinates are estimated. Native LOI size150x98mm and room-temperature TGstart are retained. Washed, metal comparator, storage and rechlorination states do not have own numerical TG/LOI pairs.
- **10.1007/s10570-019-02586-8:** own pristine and APP-loaded initial fabric add two states/four N2/air conditions. Table1's native Tonset is expressly defined as5wt%massloss and therefore recorded as T5, with raw header retained. Two APP@PDA conditions are held because DDM modification state is unresolved between preparation/Scheme1/SI and the later superhydrophobic modification discussion. Complete official legacyDOC SI, including all three rendered figures, was reviewed. Washed10cycleLOI has no own TG; CONEchar39.8 is not TG39.0.
- **10.1007/s10570-021-03874-y:** control and three PEI10wt%/THPC1,5,10wt% baths add four initial states/four N2 conditions. Table2 matches printed Figure5 LOI18.7/25.0/29.0/29.7 and R7009.4/30.2/36.7/37.6. Native nitrogen flow60mL/s is retained raw without silently substituting60mL/min; normal TG100Cpreheat/cool is documented separately. Washed1X/2X have VFT only. MCC heating/char and TGIR mass do not replace regular TG.
- **10.1007/s10570-021-03980-x:** own Cotton0/1/2/3 codes connect Table1's0/10/20/30wt% PEI-P baths to Tables2/3, adding four initial states/four N2 conditions. LOI18.1/31.4/35.8/38.7 pairs with exact T5/Tmax/R700. Regular TG mass5mg is distinct from TGIR10mg. Washed10/30/50homecycleLOI has no own TG. Source synthesis/recipe unknowns and catalyst basis are not inferred.

All previous inputs, source-version and sample-scoped reuse holds are preserved. Public evidence contains only factual data and DOI/page/table/figure locators; fulltexts, supplements, images and private paths remain outside the repository. Published total **693 states /841 conditions /180 sources**, with **1307 states remaining to2000**. PR #54 merged as `ff5184cd2490e3b04dec372b53736b5e92fbece8` after exact-head CI run36815129223 passed on `f523b58f1a18faa6ac3e1117934ef46c893cdeca`. All396 offline tests passed. The three distinct postmerge runs36815251837/36815251867/36815251838 reached terminal success. All11 changed-file blobs, the full validation report and the master SHA-256 matched the reviewed snapshot; all827 previous condition rows retained their prior fields. Snapshot `9fe87f21872f6617c390ba337db4e1d9fe5b989baa6dc4f2171b9487116edead`; master SHA-256 `9bb0f8f81a45e99835695551165df021a18c7a247be8b649e0d800d3181a242e`. Owned lease release follows this verification.


## b86 original-reviewed fiber and textile states

This batch adds 9 genuinely new sample states at 10 TG conditions from 5 DOI sources. Measured LOI is separated from char-derived calculations, conflicting TG metrics remain held, and every pair uses its own preparation and assay evidence. Related-source and unmatched-state reuse holds remain explicit. The total is 702 states, 851 conditions and 185 sources (183 DOI sources and 2 registered non-DOI proceedings). No extra atmosphere or numerical evidence upgrade is counted as a new state.

All source drafts passed independent original-evidence review. Generic residues retain unknown temperatures, and assay-specific preparation remains explicit. Fulltexts remain private. The writer lease remains active pending exact-head CI and postmerge checks.


### b86 publication checkpoint

PR #55 merged at `4363eab49c41cd3fbc6e6c884d3430d209140704`. Exact-head validation run `36816753992` passed for `7177873f8ad58778eb0722e8e141e3ba7bb9bf79`. All 403 tests passed; all 841 previous condition rows retain every existing field. All 17 changed public file blobs and the complete remote validation report matched the reviewed local snapshot.

All three merge-commit checks passed: validation `36817063985`, master rebuild `36817064074`, and processing `36817064091`. The writer lease was released at `3d05987e62f13ecd5e2e3fa13bdb032d6e777739`. Main contains 702 states, 851 conditions and 185 sources (183 DOI sources and two registered non-DOI proceedings). Explicit author-preprint totals are seven sources, 19 states and 29 conditions; DOI presence does not establish peer review.


## b87 Cotton: native metrics and source conflicts

Four complete published journal originals add **5 genuinely new initial cotton states and 9 TG conditions**, with **zero existing-state evidence upgrades**. All methods, tables and printed numerical figure labels were checked in original text and relevant native pages. Sixteen source-fact rows are retained: nine accepted conditions, four unpaired numerical TG conditions, and three stage/approximate-only fact rows. One primary reviewer. Originals list no SI and cached local inventory has only their primary PDFs; external supplement inventories were not checked.

- **10.1007/s10570-021-03728-7:** own original cotton and ADBSPA-cotton-4 at350g/L add two states/four N2/air conditions. Tables1/2 give LOI18.2±0.2/31.7±0.2 and native T10, DTG maxima and R700. Residues at each Tmax and IPDT are separate fields. Unknown uncertainty statistic and the isolated ASNDP acronym are retained. Other baths and washed states have no own numerical TG.
- **10.1007/s10570-021-03981-w:** Figure7 expressly identifies300g/L DOPO-AP cotton, adding one state/two conditions with own LOI40.2 and printed R70039.81%N2/16.19%air. The method start40C versus Table2 start35C conflict leaves clean TGstart blank. Table2 stage endpoints/losses are not T5/T10/Tonset/Tmax; two control stage-only fact rows remain outside target. TGIR powder3–5mg is not regular TG mass.
- **10.1007/s10570-021-04054-8:** own untreated Table1LOI18 and Table2TG add one state/two conditions. Native Tonset273/279C stays onset, not T5. Regular TG851 mass5mg differs from TGFTIR mass10mg/flow50mLmin. Two generic treated conditions are held because Table2 does not specify which300/350/400gL bath; no unique LOI is assigned.
- **10.1007/s10570-021-04019-x:** own untreated LOI18 and explicit air pyrolysis peaks338/487C add one state/one condition. All750C residues are approximate and stay outside clean residue fields; the N2 control has no exact TG metric. Two350gL treated conditions are held for initial LOI31.2 in tables versus31.5 in washing prose. Nitrogen second/third overallstage peaks247/299C retain numbering after waterstage; air first/second pyrolysis peaks245/289C exclude water. Regular TG35–750C is separate from TGIR25–800C.

The locally reviewed APGDPE final journal **10.1007/s10570-021-04049-5** is excluded from this import because b86 already admits its preprint and establishes a related-version reuse hold. No new sample or evidence upgrade is claimed for that repeated source. All previous field values, source-version and reuse holds remain. Public facts use DOI/page/table/figure provenance; original files, images and private paths stay outside the repository. Proposed total **707 states /860 conditions /189 sources**, with **1293 remaining to2000**. Exact-head CI, normal merge and verified terminal postmerge checks precede owned lease release.


### b87 Publication checkpoint

PR #56 merged at `c7c61853117c9ebefa47f71b06a93e202c864fc1`. Exact-head validation run `36817725797` passed for `79970269819bb67a7de747f952478de8f9c82806`; all410 offline tests and compilation passed. All851 previous condition rows retain every prior field. All11 changed public file blobs, the complete remote main report and independently fetched master bytes match the reviewed snapshot. Snapshot SHA256: `51daf9c49689d502a6fb67a73ccaf90c3c6d16f40ee1726f302ce9d6a0c52116`; master SHA256: `cd516a82125114338ff5281d167255ce5619847df042591fa356445d520e0ac7`.

All three merge-commit checks completed successfully: validation `36817882740`, master rebuild `36817882725`, and processing `36817882680`. Main contains **707 reviewed states /860 conditions /189 sources**, with1293 states remaining to2000. This batch adds5 new paired states/9 conditions and0 evidence upgrades; all7 unpaired fact rows stay excluded. The live JSON records lease release after these checks and independent readback. Literature originals and caches remain private; original file hashes are unchanged. Subsequent private screens are not included in these totals.


## b88 original-reviewed fiber and textile states

This batch adds 7 newly verified paired states at 7 TG conditions from 3 DOI sources: 5 new-source states and 2 completed legacy TG-only pairs. Measured LOI is separated from char-derived calculations, conflicting TG metrics remain held, and every pair uses its own preparation and assay evidence. Related-source and unmatched-state reuse holds remain explicit. The total is 714 states, 867 conditions and 192 sources (190 DOI sources and 2 registered non-DOI proceedings). No extra atmosphere or numerical evidence upgrade is counted as a new state.

All source drafts passed independent original-evidence review. Generic residues retain unknown temperatures, and assay-specific preparation remains explicit. Fulltexts remain private. The writer lease remains active pending exact-head CI and postmerge checks.


### b88 publication checkpoint

PR #57 merged at `923a6efb0e1f682ee88dedf137ab7b26d134609b`. Exact-head validation run `36819255497` passed for `5afe4c6dfd63cd81b272abcb290cbdf37b4c35ab`. All 415 regression tests passed; all 860 previous condition rows retain every existing field. All 14 changed public file blobs and the complete remote validation report matched the local reviewed snapshot. The temporary branch workflow is absent.

All three merge-commit checks passed: validation `36819741336`, master rebuild `36819741337` and processing `36819741339`. The writer lease was released at `800c221540f2a87f231cfd7a48319027264400b0`. Main contains 714 states, 867 conditions and 192 sources (190 DOI sources and two registered non-DOI proceedings). The batch adds five new-source states and two newly completed legacy TG-only pairs, with zero upgrades of already paired states. Explicit author-preprint totals remain seven sources, 19 states and 29 conditions.


## b89 Cotton: exact endpoints and unresolved treatment doses

Three complete local published journal originals and two complete official supplements add **6 genuinely new initial cotton states and 8 TG conditions**, with **zero existing-state evidence upgrades**. One primary reviewer; no curve estimation or independent-reviewer claim. Twenty-eight factual rows retain eight accepted conditions, three held numerical TG conditions, one approximate generic TG fact and sixteen unmatched LOI-only observations. Held facts are excluded from the target.

- **10.1007/s10570-020-03041-9:** own initial control and15%AMOP fabric add two states/three conditions. Exact N2T10 is310/289C; residue9/33% is at720C, not run end800C. Control air residue0.14% is also at720C. Separate390/325/543C residues, generic approximate treated-air residues, stage boundaries and TGIR gas peaks remain distinct. Bath percentage basis and catalyst dose are unknown. Initial preparative SDBS handwash is separate from30LC durability washing. Other baths/washedLOI lack own numericalTG. Complete official SI FiguresS1-S3 adds no numericalTG.
- **10.1007/s10570-021-04127-8:** own untreated Table1LOI18/Table2TG add one state/two conditions. Native Tonset remains onset; Table2 explicitly gives R75013.2%N2/0.53%air, despite regular run end800C. Two generic treated numerical conditions remain held because50/150/250/350gL concentration is not identified. Complete official7pageSI FiguresS1-S9/TableS1 does not resolve dose; washedLOI and initial30.9 do not establish TG350gL. RegularTG flow is unknown, separate from TGFTIR50mLmin. Native washing-run/three-washes and tensile-dose ambiguities are retained.
- **10.1007/s10570-019-02948-2:** own untreated/PAA/PAA-BF-ATP fabric add three states/three N2conditions with exactLOI18.5/18.3/23.1. Own decomposition peaks360/366C exclude preceding dehydration. PAA-BF-ATP residue22.96% is explicitly600C. GenericZnOTG residue23.36% and conflictingpeak336/348C remain held; none is assigned to0.4%ZnO/LOI24.4 or another concentration. All fiveZnO-doseLOIs are retained separately without matchedTG. The duplicated preparation subsection leaves quantitative polymer/bath recipe unknown.

All867 prior condition rows must retain every prior field. Source/version/reuse holds remain. Public numerical facts use DOI/page/table/figure provenance; original articles, supplements, images and private paths remain outside the repository. Published total **720 states /875 conditions /195 sources**, with **1280 remaining to2000**. Exact-head CI, normal merge, three distinct terminal postmerge checks and full snapshot/master readback precede owned lease release.


### b89 Publication checkpoint

PR #58 merged at `558fed756e120e091108e2fe9b856333fa8601fd`. Exact-head validation run `36820618335` passed for `b4d55d953af0a06952354fad76c00db2a67cac04`; all423 offline tests and compilation passed. All867 previous condition rows retain every prior field. All11 changed public file blobs, the complete remote main report and independently fetched master bytes match the reviewed snapshot. Snapshot SHA256: `875f24f8033c1ae3fcf183f8a7c502788f155611a68be2a2d5c11490883953af`; master SHA256: `007c8a1eb5299111a125db025aacd09717e7f228e7a87b7e283bec913ad3a889`.

All three merge-commit checks completed successfully: validation `36820749731`, master rebuild `36820749736`, and processing `36820749727`. Main contains **720 reviewed states /875 conditions /195 sources**, with1280 states remaining to2000. This batch adds6 new paired states/8 conditions and0 evidence upgrades; all20 unmatched fact rows stay excluded. Live JSON records lease release after these checks and independent readback. Literature originals and caches remain private;three original hashes andtwo supplement hashes are unchanged. Subsequent private preparations are not included in these totals.


## b90 original-reviewed fiber and textile states

This batch adds 17 newly verified paired states at 17 TG conditions from 6 DOI sources: 17 new-source states and 0 completed legacy TG-only pairs. Measured LOI is separated from char-derived calculations, conflicting TG metrics remain held, and every pair uses its own preparation and assay evidence. Related-source and unmatched-state reuse holds remain explicit. The total is 737 states, 892 conditions and 201 sources (199 DOI sources and 2 registered non-DOI proceedings). No extra atmosphere or numerical evidence upgrade is counted as a new state.

All source drafts passed independent original-evidence review. Generic residues retain unknown temperatures, and assay-specific preparation remains explicit. Fulltexts remain private. The writer lease remains active pending exact-head CI and postmerge checks.


### B90 publication checkpoint

PR [#59](https://github.com/PolyFT/textile-tga-database/pull/59) merged at `25f230bc6e041dcab9b0fdf44928a463b3b9c261` after exact-head validation run `36822252303` passed. All 431 tests passed. All 18 changed public file blobs and the complete validation report matched the reviewed snapshot `88f6c377b302d2454a7fbb00863d284512db2d7764b923d38b9f68e1394e493b`; all 875 prior condition rows preserved every prior field. Three distinct merge-commit checks (validation, master rebuild and processing) passed. The writer lease was released.

Verified total: **737 unique states, 892 conditions, 201 sources (199 DOI sources and two registered proceedings)**. This batch adds 17 new-source paired states, zero completed legacy TG-only pairs and zero evidence upgrades. Explicit author-preprint counts remain seven sources, 19 states and 29 conditions. Retain the PTAP/PVPA shared control once, all conflicting residue and peak holds, unknown methods and assay-specific preparation. Source fulltexts remain private.


## b91 Local wool and silk: exact formulations and conservative comparator holds

Four completely reviewed local publisher journal originals add **12 genuinely new initial wool/silk states and17 TG conditions**, with **zero existing-state evidence upgrades**. Fifty factual rows retain17 accepted conditions,9 held numericalTG conditions and24 unpairedLOI observations. One primary reviewer; no independent-reviewer claim or curve estimation. Publisher accepted manuscript and article-in-press versions are explicit; locators match the reviewed version.

- **10.1016/j.matdes.2015.07.163:** five initial wool states have own Table1LOI25.4/26.1/29.0/29.9/29.4 and Table3T10/T50. Native T60 remains a separate source field. Regular nitrogenTG10C/min differs from MCC; no MCC Tmax or flow is assigned toTG. No exact residue percentage is reported. Preparative wash is separate from durability washing.
- **10.1016/j.porgcoat.2014.01.023:** control and300g/L MEDP silk with5%MBAA/5%BAPO have exact char32/36% andLOI25.5/28.0. Table2 explicitly reports5%crosslinker. Figure4 uses10%MBAA,so its treatedTG is held separately. Char assessment temperature is unknown and not assigned600C. Table2 fused100g/LLOI text and Table4MPBP/200gL/initial28 conflict are preserved; washedLOI has no ownTG.
- **10.1016/j.porgcoat.2017.06.025:** control/PA-BTCA/PA-TiO2-BTCA silk add3states/6conditions,LOI24.8/31.8/36.8. Native Table3 nitrogenR600 and airR700 remain explicit; methodsrunend600C versus airfigure/residue700C conflict leaves clean air runend blank. PCFC peaks/residues/repeats are notTG. PurePA compound and all washedLOIs remain unpaired.
- **10.1016/j.tca.2018.05.011:** the publisher accepted journal manuscript admits onlyWool2/Wool3 exhaustion-assisted48gLPA20gLBTCA,.6/1.5gLTiO2,withLOI34.4/36.1 andTable4T20/T50/R700. Pad-only150/7/80formulations and washed states are held separately. Wool1LOI is only an unlabelled curve. Both control gases are held for possible sample-scoped comparator reuse against10.3390/polym8040122:matching controlLOI23.6 andairT20/T50,with differing residues/N2thresholds; reuse is not proven and no whole-paper alias is asserted. Nativeowf conversion inconsistencies remain unresolved.

All892 prior condition rows retain every prior field. Only numerical facts, concise source findings and DOI/page/table/figure locators are public. Four original PDFs and duplicate library versions remain external and read-only. Proposed total **749 states /909 conditions /205 sources**, with **1251 remaining to2000**. Exact-head CI, ordinary merge, three terminal postmerge workflows and complete remote master/report readback precede release of the owned lease.


PR [#60](https://github.com/PolyFT/textile-tga-database/pull/60) merged at `b31e7d464b5fc98ca31f306770e1c891597d8e2d` after exact-head validation run `36823468025` passed. All439 tests pass, all892 previous condition records retain every prior field, and all11 changed public file blobs plus the complete remote validation report/master match the reviewed snapshot `a3750980f4ac18070645c190564a8f20b8283f66a26147613ddf3e8c9877f486`. Three distinct terminal merge-SHA workflows passed (validation, master rebuild and processing). Verified total **749 states /909 conditions /205 sources**, with1251 remaining to2000. No PDFs, fulltexts, images or private paths published. Original four PDF hashes unchanged; source/version/formulation/endpoint/reuse holds retained. Owned lease release follows this verified publication checkpoint.


## b92 original-reviewed fiber and textile states

This batch adds 16 newly verified paired states at 21 TG conditions from 3 DOI sources: 16 new-source states and 0 completed legacy TG-only pairs. Measured LOI is separated from char-derived calculations, conflicting TG metrics remain held, and every pair uses its own preparation and assay evidence. Related-source and unmatched-state reuse holds remain explicit. The total is 765 states, 930 conditions and 208 sources (206 DOI sources and 2 registered non-DOI proceedings). No extra atmosphere or numerical evidence upgrade is counted as a new state.

All source drafts passed independent original-evidence review. Generic residues retain unknown temperatures, and assay-specific preparation remains explicit. Fulltexts remain private. The writer lease remains active pending exact-head CI and postmerge checks.


### B92 publication checkpoint

PR [#61](https://github.com/PolyFT/textile-tga-database/pull/61) merged at `c5efded7b6e481b42284c6a880dce3d29f83ba7e` after exact-head validation run `36824995652` passed. All 445 tests passed. All 14 changed public file blobs and the complete validation report matched snapshot `0205a0d195986a08a212253cc60932a410bfbe359d18d43d2cc70c6a32e7eeb4`; every prior field in all 909 condition rows was preserved. Three distinct merge-commit checks passed: validation, master rebuild and processing. The writer lease was released.

Verified total: **765 unique states, 930 conditions, 208 sources (206 DOI sources and two registered proceedings)**. This batch adds 16 new-source paired states, zero completed legacy TG-only pairs and zero evidence upgrades. Two atmospheres for five hydrogel states remain ten conditions, not ten states. Keep the three hydrogel temperature holds, DHTP source/wash/metric limitations and the PET treated-LOI conflict. Explicit author-preprint counts remain seven sources, 19 states and 29 conditions. Fulltexts remain private.


## b93 Local wool and viscose: source-native metric distinctions

Four complete local published journal originals add **11 genuinely new initial textile states and11 TG conditions**, with **zero existing-state evidence upgrades**. Thirty-eight factual rows retain11 accepted conditions,10 held native numericalTG conditions,1 stage/qualitativeTG fact and16 unpairedLOI observations. One primary reviewer; no independent-reviewer claim or curve estimation.

- **10.1016/0040-6031(96)02839-0:** eight own wool fiber states I-VIII pair Table1LOI24/27/28/27.5/31/33.5/32.5/31 with char0.8/2.4/3.3/4.4/8.3/9.5/5.1/6.0%. Char assessment temperature is unknown; no fixed-temperature residue is inferred. Static air10K/min is explicit. DTA exotherms inKelvin and activation energies remain source fields, notTG/DTG peaks. Native complex formulae and individual bath-dose uncertainty are preserved. Publisher PII matches DOI; first-page1995 header conflicts with1996 acceptance/copyright/subsequent headers.
- **10.1002/app.24217:** own blend-spun viscose Fiber1/Fiber4 pair LOI19/31 with TableIII remainedmass11.61/27.65%. NitrogenTG20C/min differs from airDSC10C/min. Generic residue temperature is unknown despite the500C run endpoint; noR500. DSC drying/decomposition peaks and repeated native TableIII columnlabels remain raw. Fiber2/3/5 have LOI only and are excluded. Native Zn2SO4 bath formula is retained literally.
- **10.1007/s10570-016-0970-6:** only own untreated viscose woven control has exactLOI17.1/N2R80012.7. Approximate control peaks are raw, notcleanTGmetrics. Generic grafted nitrogen/air peaks have no exactGP6.1/6.8/7.5/8.7 crosswalk, so those4 exactLOIs remain unpaired; qualitative control-air residue is notzero. Source-native ASTM D6413-08 LOI citation conflict and preparation/optimization differences remain explicit.
- **10.1007/s10965-016-0954-0:** all17 facts remain held. Eight fabric Table3/4 TG-LOI matches lack explicit fabric-specific ramp attribution: methods name DPOWPU polymers, so10C/min is notsilently assigned to fabrics. Nine latex-film LOIs do not provide textile TG pairs. Initial fabric recipes, native stage numbering and480C residues remain factual evidence outside target.

All930 prior condition records retain every prior field. Only numerical facts and concise DOI/page/table/figure provenance are public; originals and local paths remain external and read-only. Proposed total **776 states /941 conditions**, with **1224 remaining to2000**. Exact-head CI, ordinary merge, three terminal postmerge workflows and complete remote master/report readback precede lease release.

PR [#62](https://github.com/PolyFT/textile-tga-database/pull/62) merged at `4feaf77ead0a0a331c8b2771ed1871d604ecb840` after exact-head validation run `36826198308` passed. All453 tests passed; all930 prior rows retain every prior field. Three distinct merge-commit workflows succeeded: validation `36826341964`, master rebuild `36826342045` and processing `36826342091`. All11 changed public blobs, complete remote report and remote master bytes match snapshot `db32ff54a3b95a77100d511a398df636005f646d29e96b841396367978f63d5c` and master SHA256 `460599b81fdff59eeee1aec5a756420310aa1516cce3e6668800dc48942d253c`. Four original PDFs, also the four matching cached inventory records, retain their original hashes. Verified total: **776 source/sample/washing states /941 conditions /211 sources**; **11 new states, zero evidence upgrades,27 held factual rows excluded**. Owned lease release follows this publication proof.


## b94 original-reviewed fiber and textile states

This batch adds 6 newly verified paired states at 6 TG conditions from 2 DOI sources: 6 new-source states and 0 completed legacy TG-only pairs. Measured LOI is separated from char-derived calculations, conflicting TG metrics remain held, and every pair uses its own preparation and assay evidence. Related-source and unmatched-state reuse holds remain explicit. The total is 782 states, 947 conditions and 213 sources (211 DOI sources and 2 registered non-DOI proceedings). No extra atmosphere or numerical evidence upgrade is counted as a new state.

All source drafts passed independent original-evidence review. Generic residues retain unknown temperatures, and assay-specific preparation remains explicit. Fulltexts remain private. The writer lease remains active pending exact-head CI and postmerge checks.


### B94 publication checkpoint

PR [#63](https://github.com/PolyFT/textile-tga-database/pull/63) merged at `9a47e3f67f644db8455b1196b74f73619b56ea2c` after exact-head validation run `36827722828` passed. All 458 tests passed. All 13 batch-owned public file blobs and the complete validation report matched snapshot `55e76e1c569347f5d6aa3c781253009a0134c1a8c025ef258f8263cea1ef458a`; every prior field in all 941 condition rows was preserved. Concurrent main retry-state updates were preserved byte-for-byte, bringing the postmerge file comparison to 14 files. Three distinct merge-commit checks passed: validation, master rebuild and processing. The writer lease was released.

Verified total: **782 unique states, 947 conditions, 213 sources (211 DOI sources and two registered proceedings)**. This batch adds six new-source polypropylene textile pairs, zero completed legacy TG-only pairs and zero evidence upgrades. Keep the five-percent-loss definitions, unknown LOI uncertainty type, actual modified-PP control formulation, draw-ratio conflict and held treated temperatures/LOIs. Explicit author-preprint counts remain seven sources, 19 states and 29 conditions. Fulltexts remain private.


## b95 Local PET and silk: complete TG-only pairs from printed LOI labels

Five complete local published journal originals add **six newly paired textile states and six TG conditions**: **two new-source silk states and four existing PET TG-only states completed**, with **zero existing paired-state evidence upgrades**. Twenty-eight factual rows retain six accepted conditions,16 held native numerical TG facts and six LOI-only facts. One primary reviewer; no independent-reviewer claim or curve estimation.

- **10.1002/app.20689:** Figure8 prints exact LOI19/28.7/21.4/25.5 for PET/PANI-g-PET/POAN-g-PET/POT-g-PET, completing the four pre-existing TG-only records. TableIII explicitly reports R7000.4/6.90/3.75/4.50%; TableIV gives two major DTG peaks for each. Moisture/HCl loss, step start/end temperatures, grafting efficiency and 2DTG kinetics are separate source fields. Native Figure8 PEF axis labels versus PET captions and TableIII loss/endmass inconsistencies remain explicit. NH3-dedoped reflectance/weight-loss specimens are not assigned to the regular final fabrics.
- **10.1016/j.polymdegradstab.2008.10.024:** untreated silk LOI22.8/R60030.6 and exact20%HFPO/5.8%BTCA/4.6%NaH2PO2 silk after1HW LOI27.7/R60041.2 add two new-source states. Native Ti252/220 remains raw because the decomposition criterion is undefined. The control-specific laundering protocol is not separately reported; no control1HW claim is made. Five other exact LOIs lack same-state TG. Preserve Table4 30HFPO BTCA5.8 versus Table3/5 8.7; no washed-state substitution.
- **10.1002/app.1497:** all13 facts remain held. Ten treated PET and PET/cotton TableII/III LOI/Rf pairs have explicit fabric50C/min/50-550C but no explicit fabric atmosphere. Earlier air methods name the DCTBPP compound and are not silently transferred. Generic residue assessment temperature is unknown. Untreated Rf0 conflicts with Ru13.1/11 and the curves; both native values are preserved without a clean control residue. F and Nr are separate from TG char yield. Washed PET LOI27 has no own TG. DOI identity was checked against official Wiley metadata matching the local original's authors/title/volume/pages.
- **10.1016/j.tca.2011.01.007:** treated wool preparation92C in Tables4/5/7 and conclusion versus95C in TG prose remains unresolved; native LOI31.9/char33.34 are held. **10.1002/app.35353:** native treated LOI26.5/char31.06 is held for HCl versus formic-acid identity conflicts in experimental design/regression. The two related controls share authors, fabric,LOI25.4,third-stage391-597C and DSC enthalpy140.2, but differ in TG loss/char: possible sample-scoped reuse remains unresolved, so neither control adds a pair and no whole-paper alias is asserted. Generic char temperatures remain unknown; no stage boundary, DSC peak or21-run CCD burn-length response becomes a TG-LOI sample.

All947 prior condition records retain every prior field. Only numerical facts and concise DOI/page/table/figure provenance are public; originals and local paths remain external and read-only. Proposed total **788 states /953 conditions**, with **1212 remaining to2000**. Exact-head CI, ordinary merge, three terminal merge-commit workflows and complete remote master/report readback precede lease release.


PR [#64](https://github.com/PolyFT/textile-tga-database/pull/64) merged at `5e94c0875a4c95f76a47d483ac9018d95067a679` after exact-head validation run `36829625836` passed. All 466 tests passed. Three distinct merge-commit workflows reached terminal success: processing `36829816307`, validation `36829816311`, and master rebuild `36829816505`. All 11 batch-owned public file blobs, the complete remote report and independently fetched 4,015,410-byte master blob match snapshot `7928819d12e4df82458b569b59e3d030c51459a47df314433320b96b47f4f483` and master SHA-256 `29a2ca50fc1899da81175b833e74e01ffea32da20b7cab233332435d6f08b9cc`. Every prior field of all 947 conditions is preserved; concurrent candidate/retry updates are preserved. Five originals and six local inventory records remain hash-unchanged. Verified total: **788 sample states / 953 TG conditions / 215 sources (213 DOI sources and two registered proceedings)**. This batch has **two new-source states, four newly completed TG-only pairs, zero existing-pair evidence upgrades and six added conditions**; all 22 held facts remain excluded. The owned b95 lease is ready for release after this proof is recorded.


## b96 original-reviewed fiber and textile states

This batch adds 14 newly verified paired states at 20 TG conditions from 4 DOI sources: 14 new-source states and 0 completed legacy TG-only pairs. Measured LOI is separated from char-derived calculations, conflicting TG metrics remain held, and every pair uses its own preparation and assay evidence. Related-source and unmatched-state reuse holds remain explicit. The total is 802 states, 973 conditions and 219 sources (217 DOI sources and 2 registered non-DOI proceedings). No extra atmosphere or numerical evidence upgrade is counted as a new state.

All source drafts passed independent original-evidence review. Generic residues retain unknown temperatures, and assay-specific preparation remains explicit. Fulltexts remain private. The writer lease remains active pending exact-head CI and postmerge checks.


### b96 publication checkpoint

PR [#65](https://github.com/PolyFT/textile-tga-database/pull/65) merged at `c3fc858d7fca3b6cb4151da6eb6f3e3f17402536` after exact-head validation run `36831709333` passed on `38503247df08b66eb613996366a8cdedaa91c98b`. All 473 tests passed. Merge-commit validation `36832018371`, master rebuild `36832018413` and processing `36832018369` reached terminal success. All 16 batch-owned public file blobs and the complete validation report match snapshot `455ee03d30cebfd52c26f45b222d892d1dc8dc9aa07f46ffa56baeada8102227`; all 953 previous condition records preserve every scientific field. Concurrent retry state is preserved byte-for-byte.

Verified totals are **802 states / 973 conditions / 219 sources (217 DOI sources and two registered proceedings)**. The batch adds 14 new-source states and 20 conditions, with no completed legacy pairs or existing-pair upgrades. Explicit author preprints remain 7 sources / 19 states / 29 conditions. The owned writer lease was released at `1930ec786ebea03515f4f51802d161c3034df9ec`; the latest-publication metadata now identifies this verified batch. Source documents remain private and all numerical, preparation and reuse holds remain active.


## b97 Local sol-gel textile formulations and atmosphere records

Two complete local published journal originals add **20 new-source initial textile states and 36 TG conditions**, with **zero completed legacy TG-only pairs and zero existing-pair evidence upgrades**. All 37 native numerical conditions remain public; the one held SiCO condition stays outside the target. One primary reviewer; no independent-reviewer or statistical-independence claim.

- **10.1002/app.32954:** TablesI/II and TableIII supply 16 PET, cotton and 15/35%-cotton blend formulations, each with nitrogen/air TG and exact same-state LOI. Two atmospheres yield32 conditions, not32 samples. Native T1*/T2*/T3* are differential-TG weight-loss maxima; empty component positions remain in raw fields. PET nativeT2* is the first actual peak; air cotton nativeT3* is its second actual peak. R700 is explicitly reported and may contain inorganic silica; no pure-carbon-char interpretation. TEOS/H2O1:1/2:1/3:1 are molar ratios, not fabric add-on. Source70C24h preparation, unknown TG mass/flow/reps and native instrument string remain literal; cone100x100x0.5mm/three repeats are not TG/LOI metadata.
- **10.1016/j.carbpol.2011.10.032:** Table2 and Table3 add own CO/TiCO/ZrCO/AlCO states: LOI19/22/21/22 and R7500/9/7/9%. Native Tonset5%316/293/284/296C maps to T5, not generic onset. Source R360/R500/R750 are TG observations; the separately footnoted1100C1h muffle residues and vertical-burn residues do not become TG endpoints or additional sample pairs. SiCO numeric LOI22/T5315/R75010 remains held for the silica-specific80C15h/60C1h preparative rinse versus the later generic100C30min/120C15min procedure scope; no sequence is chosen or invented. FratelliBallesio200gsm asreceived cotton is not assigned to the separate Klopman TEOS2011 fabric cohort. Unknown LOI size/reps and approximate TG massca10mg remain explicit; cone/vertical replicates stay separate.

The source identities, known aliases/queue and exact prior metric/gas/ramp comparison were checked; all973 prior conditions retain every field. Eight related local originals were initially screened, not claimed as completed source extractions. Public facts use DOI/page/table/figure provenance; local originals/caches/paths stay external and read-only. Proposed total **822 states /1009 conditions**, with **1178 remaining to2000**. Exact-head CI, ordinary merge, three successful merge-commit workflows and complete remote master/report readback precede owned-lease release.


PR [#66](https://github.com/PolyFT/textile-tga-database/pull/66) merged at `b8d016367e3de2db298803e5429d00cd4ece96fe` after exact-head validation run `36833629320` passed on `e6b30c36f1c4ffce017e8e689c32e31aadd17f92`. All 481 tests passed. Three distinct merge-commit workflows reached terminal success: processing `36834101566`, validation `36834101616`, and master rebuild `36834101598`. All 11 batch-owned public file blobs, the complete remote main report and independently fetched 4,362,721-byte master blob match snapshot `46c7e9b4ea94e21696bcf6be91f192097fea26fcb92920830f1e368af86cbd11` and master SHA-256 `c4fadf9bbadf65ffeedb081fd78f5a9fe0c5a2b75294cd28e75e5171ee6fe9aa`. Every prior field of all 973 conditions and all three concurrent automatic candidate/retry files are preserved. Two originals and two local inventory records remain hash-unchanged. Verified total: **822 sample states / 1009 TG conditions / 221 sources (219 DOI sources and two registered proceedings)**. This batch adds **20 new-source states, zero completed legacy TG-only pairs, zero existing-pair evidence upgrades and 36 conditions**; the SiCO preparation hold remains excluded. The owned b97 lease is ready for release after this proof is recorded.


## b98 original-reviewed fiber and textile states

This batch adds 22 newly verified paired states at 22 TG conditions from 6 DOI sources: 22 new-source states and 0 completed legacy TG-only pairs. Measured LOI is separated from char-derived calculations, conflicting TG metrics remain held, and every pair uses its own preparation and assay evidence. Related-source and unmatched-state reuse holds remain explicit. The total is 844 states, 1031 conditions and 227 sources (225 DOI sources and 2 registered non-DOI proceedings). No extra atmosphere or numerical evidence upgrade is counted as a new state.

All source drafts passed independent original-evidence review. Generic residues retain unknown temperatures, and assay-specific preparation remains explicit. Fulltexts remain private. The writer lease remains active pending exact-head CI and postmerge checks.


### b98 publication checkpoint

PR [#67](https://github.com/PolyFT/textile-tga-database/pull/67) merged at `ce308be776b8b28c60c970bd2ae3c37bdca5fa77` after exact-head validation run `36836205823` passed on `7c5e46aadf3219da5a7ce038a394b68db5c97336`. All 490 tests passed. Merge-commit validation `36836672202`, master rebuild `36836672192` and processing `36836672155` reached terminal success. All 18 batch-owned public file blobs and the complete validation report match snapshot `b903d0c910a55b13cce70edac0e70592361d0b52819a2658ea227e4aca5c2a54`; every scientific field of the 1009 prior condition records is preserved.

Verified totals are **844 states / 1031 conditions / 227 sources (225 DOI sources and two registered proceedings)**. This batch adds 22 newly paired states and 22 conditions. Four states come from an explicitly identified author preprint; the complete preprint cohort is now 8 sources / 23 states / 33 conditions. Four natural-laminate LOIs repeat an earlier LOI-only study, while this admitted original supplies the matched TG; the earlier sample labels remain reuse-excluded. No repeated version, extra atmosphere or evidence upgrade is counted as a new state. The owned lease was released at `cc4c1f74604b852e0e5ad1722f64b83643088c7c`, and latest-publication metadata identifies this batch. Original documents remain private; all metric, specimen and reuse holds remain active.


## b99 Local polyester native labels and sample-scoped holds

Three complete journal originals add **four new-source initial PET fabric states and four TG conditions**, with **zero completed legacy TG-only pairs and zero existing-pair evidence upgrades**. All 22 concise native fact rows remain public; 18 held rows stay outside the target. One primary reviewer; no independent-reviewer or statistical-independence claim.

- **10.1007/s12221-019-9189-0:** FEP2/3/4/5 LOI25.1/26.2/25.5/25.3 are explicit printed Fig12 labels, not estimates. Own TG prose residues26.85/28.10/19.50/18.00 pair to the same initial PET fabric labels. FEP2 residue temperature remains unknown; FEP3/4/5 retain750C. N2,10Cmin,25-750C,30mLmin are TG methods; Table4 is DSC and supplies no TG peaks. FEP1controlLOI19.5/proseR7507.00 remains held because Fig5 powder/control legend and prose attribution conflict; FEP0powder is nontextile and has no LOI. PRP2/4/7g per20mL extraction does not become fabric add-on or bath wt%; the 90C preparative wash is distinct from antibacterial durability washing. Detailed sol preparation and generic4h stirring scopes remain explicit rather than inventing a combined sequence. Repeated FEP3 labels in one FTIR caption are retained as a caption issue; native panel labels, ordered prose and Fig10/11 crosswalk identify FEP4/5.
- **10.1002/app.46414:** Six initial numerical TG/LOI conditions remain held while the mentioned SI is unretrieved and its scope is unknown. Native generic residues retain unknown temperatures; 800C run end is not R800. Source Tsecond stays a second-degradation-step observation, not a proven DTG maximum; signed DTGmax is percent/min. Table2 native LOI uncertainties and source GB/T2403-1993/130x65x4mm stay literal. Washed45-times/20min LOI31.0 has no own washed TG, so it supplies no pair. Preparative rinses are distinct from durability washes; Py-GC-MS and cone methods stay separate.
- **10.1016/j.polymer.2021.123761:** Three states/six N2-air TG conditions and three lower-add-on LOI-only facts remain held for the related coating/control comparator audit. The related105971 original still needs correct source material after payload identity failed; no unrelated document supplies facts. Source86gcm-2 is retained raw and not silently corrected to GSM; free-gel TG, cone residues and Py-GC-MS protocols are not fabric TG/LOI fields.

All1031 prior condition records preserve every field; prior DOI/queue/known-alias and exact LOI/residue/gas/ramp comparison found no accepted-row match. Only numerical facts and concise DOI/page/table/figure provenance are public. Local originals/caches/paths stay external and read-only. Proposed total **848 states /1035 conditions**, with **1152 remaining to2000**. Exact-head CI, ordinary merge, three successful merge-commit workflows and complete remote master/report readback precede owned-lease release.

## b99 publication checkpoint

[PR #68](https://github.com/PolyFT/textile-tga-database/pull/68) merged as `61738f3049dec116d3e8974b15a9612ed8aaf2b8`. Exact-head `59fd3ed871240bc982b32e406ed3e3858ad8ca15` passed [validation 36838944349](https://github.com/PolyFT/textile-tga-database/actions/runs/36838944349). All three merge-SHA workflows reached terminal success: validation 36839145976, master rebuild 36839145698, and processing 36839145992. All 498 offline tests passed.

Four genuinely new initial polyester sample states and four TG conditions were accepted, with zero existing-pair evidence upgrades or legacy TG-only completions. Main has 848 reviewed source/sample/washing states and 1,035 conditions across 226 DOI and 228 sources; these counts do not establish statistical independence of experimental replicates. Eighteen held fact rows remain excluded. All fields of the previous 1,031 condition rows and the concurrent extraction/retry state were preserved. Independent Git-blob retrieval verified all 11 changed public files and the 4,606,858-byte master. The complete remote-main validation JSON matches the local rebuild, with zero errors. Master SHA-256: `980a78613e184c3ae5e89f916f48f0042bd27ca95b3343c0c65d0fd5f316995e`; snapshot SHA-256: `ce368477c8d5e20bd83a8a62ffd3695e7633de0e3c9acec52e379f30f5ac2703`. Three original PDFs and their three local inventory entries retain their hashes. No original files, full texts, source images, or private paths were published. The b99 lease can now be released through the separately checked progress record; future publishers must refresh main, queue, lease and open PRs.


## b100 original-reviewed fiber and textile states

This batch adds 19 newly verified paired states at 19 TG conditions from 5 DOI sources: 19 new-source states and 0 completed legacy TG-only pairs. Measured LOI is separated from char-derived calculations, conflicting TG metrics remain held, and every pair uses its own preparation and assay evidence. Related-source and unmatched-state reuse holds remain explicit. The total is 867 states, 1054 conditions and 233 sources (231 DOI sources and 2 registered non-DOI proceedings). No extra atmosphere or numerical evidence upgrade is counted as a new state.

All source drafts passed independent original-evidence review. Generic residues retain unknown temperatures, and assay-specific preparation remains explicit. Fulltexts remain private. PR #69 is merged and its exact-head CI, complete remote snapshot verification and all three merge-commit workflows passed. The B100 writer lease has been released.


### B100 publication verification

- PR: https://github.com/PolyFT/textile-tga-database/pull/69
- Exact reviewed head: `5c786dddd6ad9231ea188b7329472a4f1d11efe2`; validation run `36841484440`, attempt 2, passed
- Merge commit: `95eebc55f0db9995e8a9c69cdc093423ad7eefe0`
- Merge-commit validation, master rebuild and processing runs `36842077611`, `36842077781` and `36842077530` all passed
- All 16 changed public file blobs and the complete validation report matched the reviewed snapshot; all 1,035 prior condition records retain every existing field
- Snapshot: `3d10a2f0e76cc55610fc16c227aec21e912e3b0a61965f2690afc9848ea3e6e1`
- Lease release: `40a9a6496212a0036e321a64d8f824f13f109fb3`
- Verified total: 867 states, 1,054 conditions and 233 sources, comprising 231 DOI sources and two registered proceedings. The author-preprint cohort remains separately labelled: eight sources, 23 states and 33 conditions

All 19 B100 additions are new paired source states; no evidence upgrade or additional atmosphere is counted as a new state. Source-specific exclusions and raw method values remain explicit.


## b101 Local cotton siloxane and native metric holds

Four complete original journal papers (45 native pages) add **four new initial cotton fabric states / four TG conditions**, with **zero legacy completions and zero existing-pair evidence upgrades**. All 37 concise fact rows are retained; 33 held rows are excluded from the target. Review by one primary reviewer does not establish independent experimental replicates.

- **10.1007/s12221-018-7874-z:** Control and PNPDMS350g/L cotton pair Table1 LOI18.00/29.82 with Table2 same-state TG. All subsequent treated fabric is explicitly350g/L on p862; lower concentrations have no own TG. The control381.16C peak stays in the printed stage2 column with stage1 blank. Initial temperatures335.00/203.44 are generic onset, not T5/T10. Treated DTG maxima204.95/333.78 are uncontested. Its residue conflict14.76Table2 versus14.67prose is retained raw; canonical residue/R800/temperature remain blank, with no selection or average. ControlR8006.59 is consistent. N2/20mLmin/10Cmin/roomtemperature-800C and GB/T5454-2009 remain distinct from synthesis and water-repellency methods.
- **10.1007/s12221-019-9008-7:** Table1/2 control and GNCTSi250g/L cotton supply two initial pairs (LOI18/30.1). Selection250g/L for all other experiments is explicit p1343. Table2 first and second onsets are kept separate; the latter remains raw and is not T5/T10. R8001/29 is explicit; equal prose residues at500/738C are separate assessment points. TGair/20mLmin/10Cmin/25-800C is not the nitrogen synthesis gas. Bath urea5% and PBTCA10% are distinct from measured add-on18.5wt%owf. Grammage from another paper is not assigned. Four other concentrations and five durability-washed LOI rows have no own TG and remain held.
- **10.1002/app.47280:** Eight-page original reviewed for the related PNCTSi/NCTSi chemistry and comparator audit; four N2/air numerical conditions, one200g/L LOI-only state, and four washed LOI rows remain held. Supporting information is mentioned and FigS1 is cited for13C-NMR, but its complete scope remains unretrieved after official-page403. Its cited PNPDMS350g/L comparison is not an extra observation. BTCA/water-acetone recipe is not the GNCTSi PBTCA/water-isopropanol recipe. Preparative NaOH wash is distinct from durability laundering.
- **10.1007/s10570-019-02327-x:** Complete23-page original retains twelve held observations. Control LOI18.5prose/18printedFig5 conflicts. Printed N2 remaining-mass labels at216/283/331/383C do not become T5, onset, DTG maxima or final char yields. Air decomposition-stage peaks remain raw while their DTG definition is unresolved;150C water loss stays separate. Dynamic air/N2 and350C isothermal programs are distinct; air methods are not assigned to N2. Colour-table preparation scope differs from fire-finishing methods. Lower concentrations and three washed LOI states have no own TG. Dried extract, DSC and cone results are not textile TG pairs.

All1054 prior condition rows preserve every field; known queues/aliases and prior numeric conditions were checked for accepted-row reuse. Public provenance uses DOI/page/table/figure only, with originals and private caches kept outside the repository. Proposed totals **871 states /1058 conditions**, **1129 remaining to2000**. Release the owned lease only after exact-head CI, ordinary merge, three terminal successful merge-SHA workflows and full independent remote master/report proof.


### B101 publication verification

PR #70 (https://github.com/PolyFT/textile-tga-database/pull/70) merged at `99d304a7213ae4c43d50c2a359dcdcc323c33c57`; exact reviewed head `6e2653cde73a3e8d2b7cc938fe0a88cb50e6983a` passed CI run `36843206217`. Merge validation, rebuild and processing runs `36843536801`, `36843536804` and `36843536952` all finished successfully. All 513 offline tests passed, with zero validator errors. The verified total is **871 source/sample states and 1058 TG condition records**, comprising 233 DOI sources and two registered non-DOI sources. B101 adds four pairs and four conditions, with zero evidence upgrades; 33 held fact rows remain excluded. All 1054 earlier condition records preserve every existing field, and the three concurrent extraction-state files match the preceding main. All 11 changed public blobs and the complete rebuilt validation report match the reviewed snapshot. The independent remote master contains 4,840,648 bytes, SHA-256 `41dc3ad2e2f6dbbb76abadefc9b50730017990fdd9a83bf2552cdf6ebe5d993f`; snapshot SHA-256 `eb902585d536943a7770fadd568f3fd8040cb88787ce5d24f2fe51e7d5838fbb`. All four original files and four local inventory entries retain their hashes. No fulltexts, source images, private paths or annotations were published. The owned B101 lease is eligible for release through the separately checked progress record. The 2000-state goal remains active, with 1129 states still required.


## b102 original-reviewed fiber and textile states

This batch adds 10 newly verified paired states at 10 TG conditions from 4 DOI sources: 10 new-source states and 0 completed legacy TG-only pairs. Measured LOI is separated from char-derived calculations, conflicting TG metrics remain held, and every pair uses its own preparation and assay evidence. Related-source and unmatched-state reuse holds remain explicit. The total is 881 states, 1068 conditions and 239 sources (237 DOI sources and 2 registered non-DOI proceedings). No extra atmosphere or numerical evidence upgrade is counted as a new state.

All source drafts passed independent original-evidence review. Generic residues retain unknown temperatures, and assay-specific preparation remains explicit. Fulltexts remain private. The writer lease was released after the exact-head and postmerge checks passed.


### B102 publication verification

PR [71](https://github.com/PolyFT/textile-tga-database/pull/71) merged as `17d40f86e325143c54304d3041dadcfa385de017` after exact-head validation run `36846927946` passed on `e89f0ed008c724d63beb5956155e41344c64ce5b`. All 16 changed public file blobs and the complete validation report match the independently built snapshot. All 1,058 earlier condition records preserve every field; 519 local tests passed.

The merge-commit validation, master rebuild and processing runs (`36847324381`, `36847324440`, `36847324422`) all succeeded. Lease release commit: `0a0a3cc3e680becaa8baaed035eb1676a479047f`. The verified total is 881 unique states, 1,068 TG conditions and 239 original sources, comprising 237 DOI sources and two registered proceedings. The author-preprint subgroup remains separately reported as eight sources, 23 states and 33 conditions. B102 adds ten new-source paired states and zero evidence-only upgrades; potentially reused silica controls remain held.


## b103 Local cotton cyclic siloxane source and reuse holds

Two complete published originals and their complete official supporting materials add **two new initial cotton states / four N2-air TG conditions** from PCTSi350/450g/L, with zero legacy completions and zero evidence upgrades. All 28 concise fact rows remain traceable; 24 held rows do not enter the target. One primary reviewer checked the cached HTML, five linked tables, graphic abstract/Scheme1/Figs1-12, the second paper's 17 native pages and both complete SIs (five converted pages). This does not establish independent experimental replicates.

- **10.1007/s10570-020-03016-w:** Own Table1 LOI27.5/29.5 and Table2 TG name350/450g/L initial cotton. Four gas conditions count as two states. N2 R80038.1/38.9 agrees with prose; its calculated29.9 is excluded. Treated air residue remains raw only because Fig6c labelled terminal ordering appears inconsistent with Table2; no curve estimate or relabelling. Water onset135/peak162C is not decomposition; Table2 onset204/203N2 and211/210air and stage maxima stay source-native. Table1 250g/LLOI24.8 versus200g/Lprose remains a whole-pair hold. Both controls repeat04054-8 numerical conditions; source-control max369/368N2 and344/343air conflicts stay raw, with no new control count. PBTCA/urea amounts are unknown. RegularTGca5mg40-800C10Cmin has unknown flows; TGFTIRca10mg40-700CN250mLmin remains distinct. LOI150x58mmGB/T5454-1997 is separate from VFT, cone and tensile tests. The complete SI only contains NMR.
- **10.1007/s10570-020-03370-9:** All12 facts held. Fig6caption explicitly500g/L links Table1LOI29.5 and Table2TG, but preparationp3pH3.6 versus Scheme2p5pH3 changes sol-gel conditions and remains unresolved. No pH selected. Source synthetic APTMS116.53g/0.2mol andproduct138.93g/0.09mol notation anomalies stay raw, without correction or loading inference. Control TG vectors repeat04054-8 despite ownLOI18.1 versus18, so both new controls remain held. TG851ca5mg40-800C10CminN2/air20mLmin/twice is distinct from STA6000TGFTIRca10mg40-700CN250mLmin. Native second onset295N2 is not Tmax2=315 orT5/T10;water below120C stays separate. Cone abstract/Table3 disagreements do not becomeTGresidue. Four lower concentrations andfour washedLOIs have no ownTG. Cloth weave,grammage andpretreatment are unreported; no122gsm borrowed. Complete SI includes NMR,gas intensities andsynthesis mechanism, with no additional pairs.

Related **10.1007/s10570-021-04054-8** original methods and Tables1/2 (PDFp3/4/7/8) were rechecked: native control TG matches; its linear PPDMS and instruments differ. These are reuse concerns, not a claim of experimental identity or a change to its existing accepted records. All1068 prior condition rows preserve every field. Public provenance uses DOI/table/figure/PDFpage only; originals/fulltext/images/SI/privatepaths stay external. Proposed totals **883 states /1072 conditions**, **1117 remaining to2000**. Release the owned lease only after exact-head CI, ordinary merge, three terminal successful merge-SHA workflows and full independent remote master/report proof.


### B103 publication verification

B103 [PR #72](https://github.com/PolyFT/textile-tga-database/pull/72) merged as `675d9a89e5b07401635212d528a4825c6a6fa53d`. Exact PR head `e5395d2b8219314807026d47f91935c2c10b7087` passed CI run `36848861393`; all three merge-SHA runs `36849239337`, `36849239400`, and `36849239411` finished successfully. Offline tests: 534 passed; validation errors: zero.

This batch adds two PCTSi cotton sample states and four N2/air test records, with zero evidence upgrades. Totals: 883 reviewed source/sample/washing states, 1072 conditions, 238 DOI sources and 240 total sources. Twenty-four fact rows remain excluded. Two full originals and two official supplements were reviewed. All fields in the 1068 previous conditions were preserved; the three read-only library originals and 23 private evidence cache files retained their hashes. No original fulltexts, supplements, images or private paths were published.

All eleven changed public file blobs match the merged Git tree. Independent remote master bytes (4,984,324 bytes) have SHA-256 `fec7e84b27a24cd474acfd4902b6e9ddf478654b072ea0ac96b71b35e310fa93`; the complete remote validation report equals the local rebuilt and stored report. Scientific snapshot: `4c5e837a88a85e4085f517ef0a72a346c19f26b9c879444f8a7c1eb389394e60`. Concurrent extraction/retry state files were preserved. This is primary source review; it does not establish independent review by a second reviewer or independent physical specimens across publications.


## b104 original-reviewed fiber and textile states

This batch adds 4 newly verified paired states at 4 TG conditions from 2 DOI sources: 4 new-source states and 0 completed legacy TG-only pairs. Measured LOI is separated from char-derived calculations, conflicting TG metrics remain held, and every pair uses its own preparation and assay evidence. Related-source and unmatched-state reuse holds remain explicit. The total is 887 states, 1076 conditions and 242 sources (240 DOI sources and 2 registered non-DOI proceedings). No extra atmosphere or numerical evidence upgrade is counted as a new state.

All source drafts passed independent original-evidence review. Generic residues retain unknown temperatures, and assay-specific preparation remains explicit. Fulltexts remain private. The writer lease was released after the exact-head and postmerge checks passed.


### B104 publication verification

PR [73](https://github.com/PolyFT/textile-tga-database/pull/73) merged as `964aba518b8fff173007f140ee07aad19a65a04a` after exact-head validation run `36851289871` passed on `54843f7db934a913d3e86f3b0f227d7628cd4e73`. All 14 changed public file blobs and the complete report match the independently built snapshot. Every field of all 1,072 earlier condition records is unchanged; 538 local tests passed.

The merge-commit validation, master rebuild and processing runs (`36851813948`, `36851813914`, `36851814098`) all succeeded. Lease release commit: `936ba097c17f233657f743765fedb210383f8857`. The verified total is 887 unique states, 1,076 TG conditions and 242 sources (240 DOI sources plus two registered proceedings). Four new-source paired states were added, with no evidence-only upgrades. The author-preprint subgroup remains separately reported as eight sources, 23 states and 33 conditions.

Sample-scoped journal A/B/C/E reuse guards are public. The earlier admitted conference C retains its original fields and remains the sole counted repeated observation. Only distinct journal D/F states were admitted; no source-wide exclusion or cross-publication method substitution was used.


## b105 Local PEI/HCCP and iron phosphonate cotton originals

Two complete original PDFs (22 native pages) and one complete official supporting DOCX (two converted pages) add **six new initial cotton states / nine TG conditions**, with zero legacy completions and zero evidence upgrades. All23 concise facts are retained;14 held records remain outside the target. One primary reviewer checked all native primary pages, figures, tables and methods and the full SI. Multiple gas conditions do not add sample states or establish independent physical specimens.

- **10.1007/s10570-020-03047-3:** Three Cotton-P6H3/P8H4/P10H5 states have LOI25.3/28.5/33.8 in mainTable2PDFp7, nitrogenT5/Tmax/R700 in mainTable1PDFp6 and airT5/Tmax/R700 in officialSITableS1p2. Their measuredadd-ons15/18/23% are total finish, not reagent fractions. T5 remains5%massloss, notTonset. RegularTGQ50ca10mgambient-700C10Cmin is distinct from TGFTIRca15mg40-700C20Cmin;100Cpreheat/cooling removes water and does not create new aged specimens. Source gas flow60mL/s andbalance40mL/s retained raw, not corrected to mL/min. Untreated nitrogenLOI18.7/T5327/Tmax368/R7009.4/Rmax26.9 repeat03874-y, so both new control conditions remain held; its existing rows remain intact. HCCP is not the related THPC finish. Cotton-P10airTG has no ownLOI. One/two wash states have VFT only. NeatP6H3 scraped from glass, MCC peak temperatures andVFTchar do not become textileTG pairs.
- **10.1007/s12221-021-0003-4:** Own uncoated cotton and FeP/APP/PEI-2BL/4BL have LOI17.8/25.4/28.0 (mainTable1PDFp6) and explicit nitrogenR8009.9/33.3/35.1 (mainthermalprosePDFp5/Fig6p6); only controlTmax374 is numerically stated. TreatedT5/Tmax and all air curves remain unestimated. TA-STDQ60050-800C20Cmin, flow/mass/replicates unknown. LOI130x60mm has three averaged samples; native plusminus statistic is undefined. APP/PEI2/4BLLOI20.2/23.1 lacks ownTG; no borrowed FeP data. Cone residues13.11/18.80 are not TG33.3/35.1. Table4 washed10/20/30LC has cone data only, no ownLOI/TG. Table3 PET/ramie comparison values come from cited studies. FeP/APP1:10 ratio and solution description stay source-native; measuredWG is not component loading.

Related03874-y native methods/Table2/LOItext (PDFp4/6/7/8) were rechecked for control reuse; no new full-review claim or alteration of those existing measurements. DOI/table/figure/PDFpage locators are public; original PDFs, fulltexts, images, SI and private paths remain outside the repository. Release the owned lease only after exact-head CI, ordinary merge, all three terminal successful merge-SHA workflows and complete independent remote master/report verification.

### B105 publication verification

PR [#74](https://github.com/PolyFT/textile-tga-database/pull/74) merged with head `353874ef72cf98002e82cba0523de7ce8e323b41` and merge `9baa001fa8fa18926210a9c08dd23c0aa1417a0b`. Exact-head validation run [36852924748](https://github.com/PolyFT/textile-tga-database/actions/runs/36852924748) succeeded. All three merge-commit workflows completed successfully: validation [36853337794](https://github.com/PolyFT/textile-tga-database/actions/runs/36853337794), master rebuild [36853337744](https://github.com/PolyFT/textile-tga-database/actions/runs/36853337744), and processing [36853337763](https://github.com/PolyFT/textile-tga-database/actions/runs/36853337763).

This batch adds 6 reviewed cotton sample states and 9 TG conditions, with 0 existing-pair evidence upgrades; 14 incomplete, reused-control, curve-only or unmatched fact rows remain held. Main contains 893 verified sample states, 1085 conditions, 242 DOI sources and 244 sources; 550 offline tests passed. Two complete primary PDFs (22 pages) and one complete official supplement (2 pages) were reviewed; four pages of a related original were rechecked for control reuse.

Independent remote verification matched all 11 batch file blobs and the complete rebuilt validation report, with zero validation errors. All fields of the 1076 previous condition records and the three concurrent processing-state files remained unchanged. The remote master is 5060017 bytes, SHA-256 `aee8c4f28a5e3db1a4ac586c4dcedb2be905fc563d9cf5ecbe6595a23cac2bcb`; dataset snapshot SHA-256 `3b99ecc6be6b281ed94f7ae014744319f8d0406a200a257e641d4d357a44eef2`. Hashes of three read-only library originals and two private evidence cache files remained unchanged. Public changes contain factual data, source locators, tests and validation results; no original full texts, supplements, images or private paths were published. The writer lease is released only after these checks and this proof are recorded.


## b106 original-reviewed fiber and textile states

This batch adds 10 newly verified paired states at 10 TG conditions from 3 DOI sources: 10 new-source states and 0 completed legacy TG-only pairs. Measured LOI is separated from char-derived calculations, conflicting TG metrics remain held, and every pair uses its own preparation and assay evidence. Related-source and unmatched-state reuse holds remain explicit. The total is 903 states, 1095 conditions and 247 sources (245 DOI sources and 2 registered non-DOI proceedings). No extra atmosphere or numerical evidence upgrade is counted as a new state.

All source drafts passed independent original-evidence review. Generic residues retain unknown temperatures, and assay-specific preparation remains explicit. Fulltexts remain private. The writer lease remains active pending exact-head CI and postmerge checks.


### B106 publication verification

PR #75 merged at `2448181a84a07ba4f9317e3300097b4b97adf0ee` after validation run `36855468479` passed on exact head `4ead04ae13c3a1661a4994dc9af58786869541c8`. Merge-commit validation, rebuild and processing runs `36855902423`, `36855902388` and `36855902329` all succeeded. All 14 changed public file blobs and the complete validation report matched the locally validated snapshot; all fields of the previous 1,085 condition records were preserved. The temporary workflow is absent. Local validation passed 554 tests and syntax checks.

The verified total is 903 unique sample states, 1,095 TG conditions and 247 original sources (245 DOI sources and two registered proceedings). This batch adds ten new-source states, with no legacy completion or existing-pair evidence upgrade. Conflicting DDM peaks and SMPIC residues remain excluded; glass-veil generic residues retain unknown assessment temperatures. The B106 writer lease was released at `18c438fee9996087f211af33796aaeda13fdb52b` after these checks. Full original documents remain private.


## b107 Local GCN and rGO/casein cotton originals

Two complete original PDFs (27 native pages) add **eight new initial cotton states / thirteen TG conditions**, with zero legacy completions and zero existing-pair evidence upgrades. All24 concise fact rows are retained;11 remain outside the target. One primary reviewer checked all native pages, figures, tables, and methods. Neither complete original cites SI; no SI review or independent-reviewer claim is made. Conditions do not add sample states or establish independent physical specimens.

- **10.1007/s10853-021-05877-3:** Five Table1 formulations (PDFp4/printed9681) have explicit LOI18.1/21.3/24.6/26.8/30.5 and air/argon TG Tables2/3 on PDFp7/9684. Own121g/m2 cotton fabric maps across both assays; captions referring to constituent fibers do not authorize separate fiber specimens. Ar is argon, not nitrogen. Residue is explicitly700C although the regularTG run ends800C at10C/min. PG4BLair T5158.5C remains sourceT5 with earlycoatingdegradation caveat, not Tonset/T10. TGmass/flow and LOIreplicates/uncertainty are unreported; MCC5mg/oxygenflow/peaktemperatures and mechanicaltestfourrepeats are not borrowed. Native totalfinish add-ons do not establish component fractions. Six washed states have Fig8c directly printed LOI labels, but no correspondingTG, and remain held. Prose claims about washedLOI trends conflict with Fig8c; no correction is inferred.
- **10.1007/s10570-020-03356-7:** Three initial(rGO/CA)-1/-5/-10 ownplainwoven120g/m2 fabric states have LOI21.2/22.6/23.6 in explicit PDFp6prose/Fig5p7 and DTGsecondstage maxima296.7/287.4/290.9, R60024.8/29.9/32.7 in Table2PDFp7. These peaks are stored as Tmax2, leaving firstpeak/T5 curve estimates blank; more precise prose residues are retained separately and agree with table rounding. NitrogenQ500ca5mg30-600C10C/min;flow unreported. ControlLOI18.0abstract versus18.2body is unresolved, so its canonicalLOI is blank and the pair remains held. Methods report APPdip10min but Table1reports1min; the resolvedduration stays blank and both source reports remain. Materials label gamma-aminopropyltriethoxysilane as PEI while methods name polyethyleneimine; actual primeridentity remains unresolved. The same initial source-labelled formulation maps to TG andLOI; these recipe discrepancies do not create invented extra states. Preparativerinsing/reduction is distinct from durabilitywashing. Four washedstates have Table4VFTonly, no ownTG/LOI. The240min/five45minwashcycle arithmetic conflict is preserved without inferring a homewashcount. Cone residues/peaktimes are notTG.

DOI/table/figure/PDFpage locators are public; original PDFs, fulltexts, images and private paths stay outside the repository. Preserve all prior records and concurrent processing state. Release the owned lease only after exact-head CI, ordinary merge, three terminal successful merge-SHA workflows, and independent complete remote master/report verification.

### B107 publication verification

PR [#76](https://github.com/PolyFT/textile-tga-database/pull/76) merged with head `bc7785f2a7e33c91039eb0aed439fff9a979bfe6` and merge `0ad850a91a8c3a784daa8178979866b6f573e1f3`. Exact-head validation [36856819696](https://github.com/PolyFT/textile-tga-database/actions/runs/36856819696) succeeded. All three merge-commit workflows completed successfully: validation [36857190349](https://github.com/PolyFT/textile-tga-database/actions/runs/36857190349), master rebuild [36857190267](https://github.com/PolyFT/textile-tga-database/actions/runs/36857190267), and processing [36857190232](https://github.com/PolyFT/textile-tga-database/actions/runs/36857190232).

B107 adds 8 reviewed initial cotton sample states and 13 TG conditions, with 0 existing-pair evidence upgrades or legacy completions; 11 incomplete or conflicting fact rows remain held. Main contains 911 verified states, 1108 conditions, 247 DOI sources and 249 overall sources. All567 offline tests passed. Both complete original PDFs (27 native pages) were reviewed by one primary reviewer; no SI or independent-reviewer claim is made.

Independent verification matched all11 batch file blobs at the merge commit, the 5242708-byte remote master and the complete rebuilt validation report with zero errors. All fields of1095 prior condition records and six concurrent processing-state files remained unchanged, preserving B106. Remote master SHA-256: `eb31ab21660da365080284c394cd4067e60f253272b463c24a538cb58958997c`. Dataset snapshot SHA-256: `cb283ae0a221d7316b84bf499737e6fd04b6a97772d8c28bf3c5b81b6c8eba58`. Both read-only library originals retained their hashes. Public changes include factual observations, exact source locators, tests and validation results; no original full texts, images, SI or private paths were published. Release the owned lease only after this proof is recorded.


## b108 Local A-POSS/PA cotton original

One complete published original (15 native PDF pages), **10.1016/j.cej.2020.125661**, adds **six new initial cotton states / twelve TG conditions**; zero legacy completions or evidence upgrades. All15 concise fact rows remain in incoming;three LOI-only states remain outside the target. One primary reviewer checked every native page, methods, figures, tables and captions. SI is referenced but unavailable locally; the official publisher returned HTTP403. No SI or independent-reviewer claim is made.

Main Table1(PDFp5), Table2(TG,p11), Table3(LOI,p11) and methods(pp2-4) explicitly map own220g/m2 plain-woven fabric control/C1/C2/C3/C3-PDMS/C3-PDMS-TiO2 to LOI18.0/21.0/24.5/28.0/28.0/29.0. The source pristine/control is already NaOH-pretreated, rinsed and dried, not raw cotton. Each initial state has Q5000TG air/N2 at20C/min,30-800C; LOI HC-2GB/T5454-1997,58x150mm. Two gases do not add sample states. T5 retains5%loss; first decomposition and second air char-oxidation maxima retain source stage numbers. T75 stays a typed source field, not T80/T50/T10. Slashes remain blank. VFT five repeats, cone35kW/m2, neatA-POSS TG and abrasion WCA are not fabric TG/LOI conditions.

C3-PDMS-TiO2 N2 R800 is33.6% in Table2 versus33.7% in p8prose: both raw reports remain, canonical residue/R800/endpoint blank for that condition, with uncontested T5/Tmax1 retained. Table1 A-POSS/PA bath molarity.067/.134/.201 and methods1/2/3mmol in30mLcombinedsolutions have unresolved concentration basis; both raw recipe reports remain without correcting either or assigning a final combined concentration. Same source-labelled preparation maps both assays. Totaldryfinishadd-on5.0/7.6/10.6/15.0/16.2% is not component fractions. TGmass/flow/repeats andLOIrepeats/uncertainty are unreported.

Cotton-PDMS-TiO2LOI20.0 and five-detergent-wash(C3)5LOI24.0/(C3-PDMS-TiO2)5LOI28.0 lack ownmainTG and remain held; SI is pending. Wash protocol40C five12mincycles/ECE nonphosphatedetergent/DIrinse/dry45C8h stays distinct from50 abrasioncycles. Source fabric:detergent20:1byweight and specimen>350x500mm reports remain verbatim metadata; no inferred correction of this ratio or40x40cmpreparationgeometry. No initial TG is transferred to washed specimens. Source/sample states do not establish independent experimental replicates.

Public evidence consists of concise facts and DOI/page/table/figure locators. All original files, fulltexts, images and private paths stay outside the repository; preserve previous records and concurrent processing state. Release the owned lease only after exact-head CI, ordinary merge, three successful terminal merge-SHA workflows and complete independent remote master/report verification.


## b108 publication checkpoint

PR [#77](https://github.com/PolyFT/textile-tga-database/pull/77) merged with head `dd2b99a06d1259d0a77433bf4b033f9257289ffb` as `0f1fabb1bcc7584de1537e9f9c78caf510eb4aca`. [Exact-head CI](https://github.com/PolyFT/textile-tga-database/actions/runs/36860663678) passed all576 offline tests, compilation, scientific validation and snapshot consistency. All three merge-SHA workflows (36860944697, 36860944722, 36860944773) completed successfully.

B108 adds six new initial cotton states and twelve TG conditions, with zero legacy completions or existing-pair evidence upgrades. Three LOI-only facts remain held. Main contains917 reviewed states,1120 conditions,248DOIs and250sources. All15 native pages of the original were reviewed;referenced SI could not be retrieved because the publisher returnedHTTP403. No SI or independent-reviewer claim is made.

Independent remote verification matched all11 batch file blobs, the complete 5306968-byte master and the complete rebuilt report with zero errors. All fields of1108 prior condition records, six concurrent processing-state files and the read-only original hash were preserved. Master SHA-256:`afc7155107881c019c06762ee95fd75f995467dcec54a37c347ba5f8042d8e5b`;dataset snapshot:`5d610a4fb0bf13cde8bb8426a45d20ec9c7784783a2d011c5790ec20defd2c95`. Public files contain concise facts, source locators, tests and validation results;no original fulltexts,images,SI or private paths were published. Release the owned lease after this proof is recorded.


## b110 Local GO/ZIF, HBPOPN and AM/CS/APP cotton originals

Three complete publisher originals (77 native PDF pages) add **twelve new initial fabric states / fifteen TG conditions**, with zero legacy completions and zero existing-pair evidence upgrades. All30 concise fact rows remain in incoming;15 HBPOPN LOI-only states remain outside the target. One primary reviewer checked every native page, tables, figures, captions and methods. No SI is cited in these complete originals; no SI or independent-reviewer claim is made. Different gas conditions do not add sample states or establish independent physical replicates.

- **10.1016/j.matchemphys.2020.123656:** Three initial woven-cotton states / six N2 and air conditions map TG Table1 (PDFp18/printed15) to LOI Table2 (PDFp19/printed16). N2 control R700 conflicts (7.4 table versus 7.3 prose); only that metric and its endpoint are blank. Air control R700 is 3.2; 3.4 belongs to GO-cotton. Generic source Tmax, total-mass-loss T5/T10 and preparation rinses are kept distinct from additional DTG stages and durability washing.
- **10.1016/j.carbpol.2019.115648:** Untreated and initial HBPOPN160g/L fabrics / two N2 conditions map LOI Table1 (PDFpp13–14) to explicit R800 2.5/31.5 in thermal prose (PDFp16) and conclusion (PDFp21). The later thermal-oxidative wording contradicts the N2 method/DTG caption and remains flagged; no air condition is inferred. Three other initial doses and twelve washed LOI states lack their own TG and remain held. One accelerated AATCC cycle equals five home laundering cycles in this source.
- **10.1007/s10570-020-03140-7:** Seven initial CS/APP and AM-CS/APP fabric states / seven N2 conditions join recipes in Table1 (PDFp4), directly printed LOI labels in Fig2 (PDFp6), and numerical TG Table3 (PDFp9). R800 is distinct from cone residue; air dimensional-stability photos are not air TG. AM solution concentration, APP bath concentration and measured dry finish add-on retain their original bases. Ambient start, missing assay repeats and unreported extra DTG peaks are not filled in.

Detailed source limitations, recipe uncertainties and publication versions remain in the observation fields and batch manifest.

Public evidence contains concise facts and DOI/page/table/figure locators. Originals, fulltexts, images and private paths remain external. Preserve all existing rows and concurrent processing state; release the owned lease only after exact-head CI, ordinary merge, three successful merge-SHA checks and independent complete remote master/report verification.


## b110 Publication verification

PR [#78](https://github.com/PolyFT/textile-tga-database/pull/78) merged with head `5eaecde15c128ef56b7f146c8deaf9c9239d94e6` and merge commit `af90e7ca0ffe60ae739b56f966935fc36db7deaf`. Exact-head validation [run 36869697646](https://github.com/PolyFT/textile-tga-database/actions/runs/36869697646) passed. All three merge-commit workflows finished successfully: validation, master rebuild and processing.

B110 adds twelve new initial cotton fabric states and fifteen TG conditions, with zero legacy completions or existing-pair evidence upgrades. Fifteen LOI-only facts remain held. Main contains929 reviewed states,1135conditions,251DOIs and253overall sources. All592 offline tests passed. Three complete publisher originals (77 native pages) were reviewed by one primary reviewer; no SI or independent-reviewer claim is made.

Independent remote verification matched all11 batch file blobs, the complete5413339-byte master and the complete rebuilt report with zero errors. All original fields of1120 prior condition records, six concurrent processing-state files and the three read-only original hashes were preserved. Master SHA-256:`a0dabcfb1ac156050a3239be46951e36a0ea3cfbb6a659117a32a461d5a3b80e`;dataset snapshot:`82d73c80d4d1a995cca001a187d424811b420bc8132c0f444e26b210975cd3e7`. Public files contain concise facts, source locators, tests and validation results;original fulltexts,images,SI and private paths remain external. Release the owned lease after this proof is recorded.


## b111 Local CH/PA/Ba, amino-acid and graphene cotton originals

Three complete local publisher originals (38 native pages) and one complete official DOCX supplementary file add **ten new initial fabric states / seventeen TG conditions**, with zero legacy completions and zero existing-pair evidence upgrades. All76 concise fact rows remain in incoming;59 held facts remain outside the target. One primary reviewer checked every original page and all official DOCX7 tables/paragraphs plus12 rendered pages; six video supplements were not reviewed. Repeated gas conditions and LOI replicates do not increase the state count.

- **CH/PA/Ba:** three states/six conditions. PA/Ba LOI18.0 versus unnamed Lewis-reference16.4 stays held; source T10 and zero R600 are preserved. Water-stirred HFT-only states receive no initial TG/LOI.
- **Amino-acid finishes:** four states/eight conditions. Exact prose LOI and Table5 TG agree; CY600 remains600C while the scan ends700C. Air control second peak491.2C is char oxidation. Thirty-nine graph-only and three exact40LC LOI-only states stay held; unknown bath-percent basis and uncertainty type remain unknown.
- **Graphene:** three initial states/three N2 conditions, Table1 LOI with SI TableS4 fixed-temperature masses. K2CO3 concentration60versus2mg/mL holds that fourth state. Nominal700C versus SI run-end near800C and LOI-standard edition09versus11 are retained without choosing corrections. Generic SI onset/midpoint and DSC peaks are raw metadata, not inferred T5/T10/DTG. Washed, binder, char and feed-ratio burn-only states remain held.

Public evidence contains numerical facts and DOI/page/table/figure locators. Originals, full texts, SI, images and private paths remain external. Existing data and concurrent processing files are preserved; exact-head CI, ordinary merge and complete remote verification precede lease release.


## b111 publication checkpoint

[PR #79](https://github.com/PolyFT/textile-tga-database/pull/79) merged as `5e3d8986c2f77a7d397caa69a2af84e0b9915df4` after [exact-head validation run 36878304376](https://github.com/PolyFT/textile-tga-database/actions/runs/36878304376) succeeded on `3d0f17d0ecc6b707d8f4d642b79f90efea08b82d`: all609 offline tests, compilation, scientific validation and snapshot consistency. All three merge-triggered validation/rebuild/processing runs succeeded. Independent Git-tree/blob readback verifies all11 public blobs and the complete5,562,631-byte master, 939 reviewed states/1152 conditions/254 DOI/256 sources, errors=[]; all1135 prior condition fields and seven concurrent processing/discovery files match the actual pre-merge main. Source originals and the official SI hashes remain unchanged. Snapshot SHA-256:`81634890a350e6cd6d0627919c8ea543029756adb605316f0b45d8d249ec3a6b`; master SHA-256:`6fac4daedf6e61a99a72889a4540ca0fd61be44836e4f4a3460afe678651589a`.

B111 adds10 genuinely new states/17 conditions, zero evidence upgrades and zero legacy completions. All59 holds remain outside the target. The owner releases the B111 single-writer lease after this complete publication proof; the next publisher must refresh main, PRs, source queue and lease. The next PEI/PA/AgNW cotton original is partially reviewed and not counted. Target2000 remains active,1061 states remaining.


## b112 Local CEJ multilayer, PAA/ATP and sodium metaborate cotton originals

Five complete local originals (86 native pages) and one complete official DOCX supplement add **seven new source/sample/washing states / ten TG conditions**, with zero legacy completions and zero existing-pair evidence upgrades. All76 concise fact rows remain in incoming;66 held facts stay outside the target. One primary reviewer checked every original page and the supplement's115 paragraphs,2tables and3 rendered pages.

- **PEI/PA/AgNW:** three initial states/six air and nitrogen conditions. Intermediate AgNW doses have TG only. T5, air second char-oxidation peak and R800 remain distinct; TG-IR and EMI durability do not supply regular TG or washed LOI.
- **PAA/ATP:** only the1percent ATP-feed cotton has explicit R60019.56 and LOI22.7. Six other formulations have exact LOI but graph-only TG and stay held. Relative char improvements do not yield invented absolute values.
- **Sodium metaborate:** own control, initial finish and washed finish provide three separate states at air20C/min. Official TableS1 R700 and TableS2 LOI agree with main-text state labels. Cone char is separate. Native peak-mass metadata and washed peak/rate disagreements stay raw;9.4percent is washing weight loss, not remaining add-on.
- **ASGTMPA and DCTP/TEA:** complete reviews preserve33 and17 held facts respectively. Contradictory regular TG gas/ramp wording and unreported TG gas prevent their admission; other assays cannot repair those gaps. Washed or other-dose LOI never borrows initial TG.

Public evidence contains numerical facts and DOI/page/table/figure locators. Originals, full texts, SI, images and private paths remain external. Existing data and concurrent processing files are preserved; exact-head CI, ordinary merge and complete remote verification precede lease release.


### b112 publication proof

[PR #80](https://github.com/PolyFT/textile-tga-database/pull/80) merged as `a2c019b69795ebd01e43fa38bb9c86aed92bd8e8` after exact-head [validation run 36890464664](https://github.com/PolyFT/textile-tga-database/actions/runs/36890464664) passed on `c4f0f33ce64229dc81b7e71204ae6f1dbbc2aa34`. All621 offline tests, compilation and scientific validation pass; the three merge-triggered checks also succeeded. Independent remote verification confirms946 states,1162 conditions,257 DOI sources and259 total sources. All1152 prior condition records and their fields, eleven published file blobs, seven concurrent processing files, five original hashes and the official supplement hash are preserved. The complete 5666653-byte master has SHA256 `584369c85f1afec121698ca38ba872d2a632243d1903baddcc5f49818e5bd421`; the full remote report matches a fresh rebuild. Snapshot: `fc31e3335bb612b29ef3d0bffe2df329c3e3db9bc9bd7568ad87fc376d5b4fec`. Seven new pairs, zero evidence upgrades and zero legacy completions are published;66 held facts remain excluded. The writer lease is released only after this verified publication record is saved.


## b113 Local 2020 reaction-finished and hybrid-coated cotton originals

Four complete originals (56 native pages) and three complete official DOCX supplements add **four new source/sample/washing states / eight TG conditions**, with zero legacy completions and zero existing-pair evidence upgrades. All69 fact records remain in incoming;61 holds remain outside the target. One primary reviewer checked all original pages,59 supplement paragraphs,one table and nine rendered supplement pages.

- **AGATMPA:** own initial control and35wt% finish have exact Table2 LOI and Table4 T10/Tmax/R700 in air and nitrogen at20K/min. T10 is neither T5 nor Tonset; loose completion wording does not redefine maximum mass-loss temperature. Two other doses have graph-only TG;13 washed LOI states have no matching washed TG. Duplicated washed weight-gain labels remain unresolved.
- **AMHPE:** own control and30mass% finish have exact Table1 LOI and Table3 Tonset/Tmax/residues in both gases. Air R700 and R800 remain separate values and temperatures; the control second peak is char oxidation. Two other initial doses and15 washed LOI states have no own TG and stay held.
- **PBN:** all15 facts remain held. Table2 R900 and same-state Figure5 TG curves contradict one another. Early control moisture peaks, approximate control LOI, unclassified abstract washing state and graph-only washed LOI stay raw. Three curing runs and50 washing cycles are never paired with initial measurements.
- **Hydrophobic LAP/NH4-HMP/HTMS:** all12 facts remain held. Method600C, nitrogen Figure4 to700C, air Figure5 to800C and unqualified residue-table headings conflict. The control LOI and three nitrogen temperatures exactly match an existing different-source control; independence/provenance remains unresolved and the new control is not counted. This numeric match does not establish misconduct. Existing records are preserved. Washed LOI never borrows initial TG.

The supplements contain NMR or cone/SEM/contact-angle evidence and do not supply additional TG-LOI pairs or resolve the held conflicts. Public evidence contains numerical facts and DOI/page/table/figure locators; originals, fulltexts, SI, images and local paths remain external. Exact-head checks and complete remote verification precede lease release.


### b113 publication proof

[PR #81](https://github.com/PolyFT/textile-tga-database/pull/81) merged as `f972cd018f2d140a218ff27d92a5fc94a67acbe3` after exact-head [validation run 36898638414](https://github.com/PolyFT/textile-tga-database/actions/runs/36898638414) passed on `80e16de74173a9edb3ca34e64635f9bb1e6c7a48`. All631 offline tests, compilation and scientific validation pass; the three merge-triggered checks also succeeded. Independent remote verification confirms950 states,1170 conditions,259 DOI sources and261 total sources. All1162 prior condition records and their fields, eleven published file blobs, seven concurrent processing files, four original hashes and three official supplement hashes are preserved. The complete 5733692-byte master has SHA256 `902c6a8ab944253a1d00b9ca92b597402eb1473ae47e1635c6aa7fddb02f533b`; the full remote report matches a fresh rebuild. Snapshot: `74d8c4cd2d05baa33563ec99974fd0cfadbd4bbbc381945ddaf165002c282a9b`. Four new pairs, zero evidence upgrades and zero legacy completions are published;61 held facts remain excluded. The writer lease is released only after this verified publication record is saved.


## b114 Local APHOMPA, GBAP, CTSGP and ASPBH cotton originals

Four complete originals (58 native pages) and one complete official DOCX supplement add **five new source/sample/washing states / eight TG conditions**. Existing-pair evidence upgrades and legacy completions are both zero. All57 fact records are preserved in incoming;49 holds remain outside the target. One primary reviewer checked all original pages and all13 supplement paragraphs and two rendered pages.

- **APHOMPA:** initial control and30percent finish have own Table1 LOI18.2/40.5 and explicit nitrogen R60011.9/45.4 at10K/min. Printed R60111.6 and R60245.4 coordinates retain their distinct temperatures. Interval-loss prose conflicts and graphical boundaries remain raw, never T5/T10/Tonset/Tmax. Air ramp is unreported;two other doses and ten washed states have no own TG.
- **GBAP:** all19 facts stay held. Table2/Figure6 identify three curings and30 laundry cycles but no treated concentration;the100g/L standard selected for another laundering experiment is not silently applied to TG. Control LOI19 has unspecified washing state. Early moisture peaks and native DTG-rate unit conflicts remain raw;graph LOI is never estimated.
- **CTSGP:** only the initial untreated control is paired in air and nitrogen using Table1/Table2. Treated initial LOI29.0 versus zero-wash28.8 remains unresolved, with all values preserved and neither chosen for approval. WG7.6 lacks dose mapping;four dyed and three washed states have no own TG. Mass at Tmax remains distinct from R700.
- **ASPBH:** own initial control and350g/L finish pair exact thermal prose with Table1/zero-wash Table3. Air control residue prose conflicts with the figure plateau, so its char is blank rather than zero;the explicit main Tmax344 remains usable. Treated N2 stage ranges are not exact peaks;R80042.9 is explicit. Isolated Tmax344/ramp coincidences do not establish aliases;the full N2 onset/peak/char profile has no prior exact match. Main aminoethyl versus SI aminopropyl and undefined PBTCA metadata remain unresolved;both assays still explicitly concern the same350g/L source-labelled fabric. Two other doses and three washed states stay unpaired.

The supplement contains a synthesis mechanism only, with no additional TG/LOI measurements. Numerical facts and DOI/page/table/figure locators are public;originals, fulltext, supplement files, images and private paths remain external. No independent reviewer or experimental-replicate claim is made. Exact-head checks and independent complete remote verification precede lease release.


### b114 publication proof

[PR #82](https://github.com/PolyFT/textile-tga-database/pull/82) merged as `0dc66888e7e6d73e7c0b2150dc3bccf69d3264e2` after exact-head [validation run 36907631928](https://github.com/PolyFT/textile-tga-database/actions/runs/36907631928) passed on `ea92adf11a2869bfb10e833ee8c344921668ab8d`. All643 offline tests, compilation and scientific validation pass; the three merge-triggered checks also succeeded. Independent remote verification confirms955 states,1178 conditions,262 DOI sources and264 total sources. All1170 prior condition records and their fields, eleven published file blobs, seven concurrent processing files, four original hashes and one official supplement hash are preserved. The complete 5813197-byte master has SHA256 `bdf17abf42694f1d8a4f9eb2b0b3c853496e47e83557efc992a49efd30240299`; the full remote report matches a fresh rebuild. Snapshot: `0297b8114bae75f2254c5a1acb100e5af8f849e47c326086aef79591ec434a81`. Five new pairs, zero evidence upgrades and zero legacy completions are published;49 held facts remain excluded. The writer lease is released only after this verified publication record is saved.


## b115 Local silk, lyocell, polyester and wool originals

Six complete native originals (75 pages) add **nine new source/sample/washing states and eleven TG conditions**. Existing-pair evidence upgrades and legacy completions are zero. All 69 fact records are preserved; 58 held records remain outside the target. One primary reviewer checked every original page. No SI was cited or found in the local DOI inventory.

- **Silk:** own initial control LOI23.5 matches Table1 TG. Exact Kelvin conversion retains residue at699.85C, never rounded toR700. Seven modified doses have bounded or graph-only LOI and remain held.
- **Lyocell:** own control and30wtpercent finish after30 native laundry cycles retain unconflicted T10/residue measurements in both gases. Initial treated LOI44.6 versus40.6, all Table3 peak/figure disagreements, and N2control R80013.32 versus13.6 remain unresolved. Canonical disputed fields are blank;30LC is not renamed150LC.
- **Polyester:** four initial ZnCl2 doses have matching own LOI and explicitly defined onset temperatures. Table2caption10percent despite four dose rows is retained. SourceTdmax is held because Figure5 uses DTA voltage units; source residual percentages have no explicit associated temperature and stay raw. Add-on denominatorWt and conflicting4to99percent prose are preserved. Three washed states have no own TG.
- **Wool:** initial control/treated LOI24.1/26.6 pairs with Table5 air TG. The64C moisture peak stays separate from protein decomposition and char oxidation peaks. The5/15wash columns contain VBT only; dyed mechanical samples are separate.
- **Ag-lyocell:** all19 facts remain held because the complete original supplies no TG heating rate. Six TG tests preserve native thresholds, residues and unresolved peak prose/table disagreements; no10C/min is borrowed.
- **EADP-lyocell:** all12 facts remain held because standalone TG explicitly tests fibers and LOI explicitly tests separately supplied fabrics, without proof of the same form/state. Initial37.8 versus38 LOI and TG-dose mapping remain unresolved. N2residue800C and air residue700C are distinct; no graph estimates or washed TG transfer.

Only numerical facts and DOI/page/table/figure locators are public. Original files, fulltext, images and private paths remain external. No source correction, independent reviewer or physical-replicate claim is made. Exact-head checks, ordinary merge and independent complete remote verification precede lease release.


### b115 publication proof

[PR #83](https://github.com/PolyFT/textile-tga-database/pull/83) merged as `a3cc8e4c64576ca1d9d11a697bf29487204980fa` after exact-head [validation run 36915330598](https://github.com/PolyFT/textile-tga-database/actions/runs/36915330598) passed on `6845608f161a884c2ce2c578ecab6e9809c68674`. All657 offline tests, compilation and scientific validation passed; all three merge-triggered checks succeeded. Independent remote verification confirms964 states,1189 conditions,266 DOI sources and268 total sources. All1178 prior condition records and their fields, eleven published file blobs, seven concurrent processing files and six original hashes are preserved. The complete5932848-byte master has SHA256 `f07a12012f7cac366657a2b7192ae61304d57f8e7235e1b6cc0d86a86e97f7e5`; the full remote report matches a fresh rebuild. Snapshot:`4566a899417c915c870ecf52b219e519046e196fa2a7729fcd6683a3f55ddde1`. Nine new pairs and eleven TG conditions are published; evidence upgrades and legacy completions are zero;58 held facts remain excluded. Lease release follows this verified publication record.


## b116 Local lyocell, cotton and ramie originals

Six complete local originals (86 pages: five native publisher PDFs and one publisher accepted manuscript), plus one complete official supplement, add **six new source/sample/washing states and ten TG conditions**. Existing-pair evidence upgrades and legacy completions are zero. All 102 fact records are preserved; 92 held records remain outside the target. One primary reviewer checked every original page and all three NMR spectra and the caption in the official B5 supplement.

- **VCFR lyocell:** own initial control/GP24wt% fabric has LOI17/39.8 and exact Table2 T5/T50/main DTG peaks at15C/min in nitrogen. ControlR80014 in Table2 versus13.6 in prose stays raw; canonical residue is blank. Three washed states have LOI only.
- **ADDTMPA cotton:** own control/30% initial fabrics explicitly match TG in nitrogen and air to LOI18/41.5. Table3/4 T10 and main DTG peaks are distinct from T5/Tonset; aircontrol second472.5C peak is char oxidation. Char is at600C although the test ends700C. Other concentrations and all washed states lack corresponding TG; unlabelled LOI curves are not estimated.
- **B5 ADPTMPA cotton:** own control/40wt% initial fabrics have LOI18.6/46.5 and matching air/nitrogen TG at20K/min. Treated nitrogen char42.03 in Table3/conclusion versus40.03 in prose stays unresolved; canonical nitrogen residue is blank. Seventeen other-dose/washed facts have no own TG. The official supplement contains NMR only and supplies no additional pair or residue adjudication.
- **PVPA/BPEI ramie:** all five native TG states remain held; the complete original reports vertical burning and MCC but no own LOI. Synthesis supplement is cited but unavailable locally and is not claimed reviewed. Source layer-count and residue prose/table discrepancies remain.
- **ADGP cotton:** all14 facts remain held. No own control LOI is reported, treated TG dose/state is unspecified, and method endpoint700C conflicts with800C results. Table1 caption10-30% differs from actual10/20/40% rows; no silent source correction or borrowed40% cone identity.
- **AMHMPA cotton:** the full accepted journal manuscript is explicitly labelled as this version. All24 facts remain held; own control LOI is about16%, standalone TG-treated dose is unspecified, and70g/L cone/90g/L TGIR identities are not transferred to TG. Raw600C char3.6/38.5 and exact/curve-only LOI facts remain distinct; no cytotoxicity or EDX metric is counted as TG/LOI.

Numerical facts and DOI/page/table/figure locators are public. Originals, fulltext, supplements, images and local paths remain external. No independent reviewer or experimental-replicate claim is made. Exact-head checks, ordinary merge and independent complete remote verification precede lease release.


### b116 publication proof

[PR #84](https://github.com/PolyFT/textile-tga-database/pull/84) merged as `d2aec8fffffa6ce4babf8c32e45009a9a3778465` after exact-head [validation run 36924419342](https://github.com/PolyFT/textile-tga-database/actions/runs/36924419342) passed on `109d1fe4fc3cb5386c30cda9154ef37524b177e7`. All671 offline tests, compilation and scientific validation passed; all three merge-triggered checks succeeded. Independent remote verification confirms970 states,1199 conditions,269 DOI sources and271 total sources. All1189 prior condition records and their fields, eleven published file blobs, eight concurrent processing files and six original hashes and one official supplement hash are preserved. The complete6005788-byte master has SHA256 `1bf5cb459fe314857c9314f510a8d10bf31fea7a63b1cda14d4c6744a69b29b2`; the full remote report matches a fresh rebuild. Snapshot:`148af58605d2dd0a9b72594fcf98d207b232ebdbc5c19769a60786508b234826`. Six new pairs and ten TG conditions are published; evidence upgrades and legacy completions are zero;92 held facts remain excluded. Lease release follows this verified publication record.


## b117 Local cotton coatings and hyperbranched generations

Four complete native publisher originals (43 pages) add **six new source/sample/washing states and six TG conditions**. Existing-pair evidence upgrades and legacy completions are zero. All47 fact records are preserved;41 held records remain outside the target. One primary reviewer checked all native and text pages; no supplement is cited in these originals.

- **PCQS/PA multilayers:** own initial Cotton, Cotton-PEI,30-layer and30-layer-Cl fabrics have LOI18.2/18.7/29.8/28.5 and author-labelled main DTG peaks375/380/339/336C in nitrogen at10C/min. Control T5=312/R600=8 and unchlorinated30 T5=291/R600=37 are explicit; chlorinated30 has R600=34 but no own T5/add-on. PEI residue and10/20-layer TG remain unreported. Native layer/bilayer terminology is retained. A single PEI peak380C matches an air wool/PP source numerically, but material, formulation, gas and LOI differ; it is not shared-sample evidence.
- **Casein cotton:** all22 facts remain held. Seven initial TG rows use native10percent mass-loss temperature, two DTG stages and residues at variable DTG temperatures; control R800<1 remains a bound. No own LOI is reported. Fifteen washed, aged and abraded horizontal-burn residues are not TG residues or LOI.
- **Attapulgite cotton:** all6 initial/washed LOI facts remain held because no own TG is reported. Native10/15/20 laundering counts are preserved; the zero-time table row duplicates the initial treated state.
- **Hyperbranched HBPOPN cotton:** generation3/4 initial160g/L fabrics have LOI42.7/43, T10=252/247, main DTG307/290 and R800=33.1/34.8 at20K/min in nitrogen. The paper explicitly reuses generation2 data from DOI10.1016/j.carbpol.2019.115648, already reviewed. Generation2 and the possibly shared control are held without recounting or changing prior rows; generation2 R80031.4 here versus31.5 in the prior source remains unresolved. Nine washed states have LOI only. Water evaporation is not the main decomposition peak;600C mass loss is not a directly reported residue.

Numerical facts and DOI/page/table/figure locators are public. Originals, fulltext, images and local paths remain external. No independent reviewer or experimental-replicate claim is made. Exact-head checks, ordinary merge and independent complete remote verification precede lease release.


### b117 publication proof

[PR #85](https://github.com/PolyFT/textile-tga-database/pull/85) merged as `c2f3a4fe3ce829af530193c251e55f59e646fa3e` after exact-head [validation run 36929245049](https://github.com/PolyFT/textile-tga-database/actions/runs/36929245049) passed on `69327f5b9dc832ec08fdc2586c0798885ce45542`. All682 offline tests, compilation and scientific validation passed; all three merge-triggered checks succeeded. Independent remote verification confirms976 states,1205 conditions,271 DOI sources and273 total sources. All1199 prior condition records and their fields, eleven published file blobs, eight concurrent processing files and four original hashes are preserved. The complete6079546-byte master has SHA256 `316dc4102e0c64ab1a502fb110051bab2b532b964f1a13f1c428311a8d85510f`; the full remote report matches a fresh rebuild. Snapshot:`4c5904c975bbefa35b0e7e211f162a5063cb09a4cd208ff67013e13c5daef2bc`. Six new pairs and six TG conditions are published; evidence upgrades and legacy completions are zero;41 held facts remain excluded. Lease release follows this verified publication record.


## b118 Local water-glass cotton, borate silk and manganese coatings

Three complete native publisher originals (29 pages) add **six new source/sample/washing states and twelve TG conditions**. Existing-pair evidence upgrades and legacy completions are zero. All43 fact records are preserved;31 held records remain outside the target. One primary reviewer checked every native and text page. No supplement is cited in these originals; a local HTML method section corroborates the missing TG heating rate in the manganese paper. Two byte-identical silk PDF filenames represent one source.

- **Water-glass/U/AP cotton:** five initial formulations plus their untreated control have exact Table5 LOI19/20/42/47/26/28 and corresponding Table2 nitrogen/Table3 air TG rows at10C/min. Two atmospheres give12 conditions for6 states. Native Tonset5% explicitly means5wt% mass loss, recorded as T5. Nitrogen WG-only T5=118C includes the authors' water/silanol explanation and is distinct from its374C main decomposition peak. Air Tmax2 is char oxidation. Residue is at600C despite an800C method endpoint. Air-control R600<1.0 remains a raw bound; canonical residue stays blank. Residues at variable Tmax temperatures and PCFC/cone outputs are not fixed-temperature TG residues.
- **GBCAE silk:** all17 initial/washed facts remain held. TG Table1 has air T10 and residues at125/425/700C for control/150/300g/L, but no heating rate is reported. Most dose/wash LOI values are unlabelled curves. Explicit prose values remain raw where unresolved; no curve estimate, other-dose TG or washed TG is borrowed. PCFC char is not TG char; instrument dimensions/repeats are not guessed.
- **Manganese PEI/PSP cotton:** all14 initial/washed facts remain held. Seven initial Table1 TG rows have nitrogen T10/main DTG/R800, but no TG heating rate; the1C/s ramp,4-5mg mass and600C endpoint belong to MCC. Seven washed Table3 LOI rows have no corresponding washed TG. Initial MCC char34.7% and TG R80038.2% for Mn-15BL are distinct; washed MCC char32.43% is not washed TG. Native DI-rinse repeats are not converted into home laundry cycles. Surface EDS atomic percentages are not bulk formulation loadings.

Numerical facts and DOI/page/table/figure locators are public. Originals, fulltext, images and local paths remain external. No independent reviewer claim is made. Exact-head checks, ordinary merge and independent complete remote verification precede lease release.


### b118 publication proof

[PR #86](https://github.com/PolyFT/textile-tga-database/pull/86) merged as `1e4872c5f32c64a3be8ef7720627c9c62fb2a092` after exact-head [validation run 36932824726](https://github.com/PolyFT/textile-tga-database/actions/runs/36932824726) passed on `e5f162efe724a4f6046d009be8e6ac175877767d`. All691 offline tests, compilation and scientific validation passed; all three merge-triggered checks succeeded. Independent remote verification confirms982 states,1217 conditions,272 DOI sources and274 total sources. All1205 prior condition records and their fields, eleven published file blobs, eight concurrent processing files and three original hashes are preserved. The complete6168349-byte master has SHA256 `d609d95b469ed664eb69ec73d68b7fbbc39f72ca188b1a331ba1e37f2a56aba7`; the full remote report matches a fresh rebuild. Snapshot:`58cff0c972c91d75fa58588c13018bc3596ef7c3bb3e1cf1f65cd23ec0ed1aa6`. Six new pairs and twelve TG conditions are published; evidence upgrades and legacy completions are zero;31 held facts remain excluded. Lease release follows this verified publication record.


## b119 Cotton polyborate multilayers, UV comonomers and held PA6.6 hybrid coatings

Three complete native primary originals (32 pages) add **four new independent initial sample states and eight TG conditions**. Existing-pair evidence upgrades and legacy completions are zero. All46 fact rows remain available;38 held facts stay outside the target. One primary reviewer checked all native and text pages. The PA6.6 original cites an unread supplement; this coverage gap remains explicit and all its12 source-condition facts are held.

- **10.1007/s10570-016-0928-8:** untreated cotton and5/10/20PHMGP-SPB bilayers have Table3 LOI18.5/24.5/29/41 and Table1 own nitrogen/air TG at10C/min,50-600C. Eight conditions represent four states. Generic Tonset is not T5 or T10. Air-control onset360C in Table1 conflicts with358C in prose; its canonical onset remains blank while its own Tmax384/556C and R6001.1 remain exact. Nitrogen residues at variable DTG maxima and vertical/horizontal flame residues are distinct from R600. MCC60C/min/80mL/min are not regular TG conditions. No SI is cited in all12 pages.
- **10.1007/s12221-017-7628-3:** all26 initial/wash facts remain held. Six explicit Table2 initial TG/LOI rows lack the TG atmosphere. Fourteen washed LOI states have no own washed TG. Crosslinked initial MBAAm/TAHT LOI43 in Table3 conflicts with34/36 in prose; neither value is silently selected. Unlabelled Figure2 curves are not digitized. Dimensionless residue number and fabric weight fraction are not TG char values.
- **10.1016/j.porgcoat.2020.105640:** six initial PA6.6 fabric states have12 air/nitrogen TG condition facts and exact Table4 LOI. Their cited Appendix A supplement remains unavailable: no matching local attachment, inaccessible publisher page and unsuccessful conventional public attachment candidates. All12 facts are held pending supplement review; whole-source completion is not claimed. Table5 exact R700 values remain distinct from rounded prose and600C furnace-char images; native multiple DTG peaks retain their order. Regular TG flow is unreported;55mL/min belongs to TG-FTIR only. GO/CS versus CS/GO sample-label order does not create extra samples. Native graft/weight-gain percentages are not recalculated from inconsistent printed formulas. Washed Table6 reports vertical burning, with no own washed LOI/TG pair.

Public evidence contains factual values and DOI/page/table/figure locators. Originals, fulltexts, supplements, images and private paths remain external. Exact-head checks, ordinary merge, three terminal postmerge checks and complete remote byte verification precede owned lease release.


### b119 publication proof

[PR #87](https://github.com/PolyFT/textile-tga-database/pull/87) merged as `ed861fed4006f39da854d6313abdf268b9fe1d11` after exact-head [validation run 36935490167](https://github.com/PolyFT/textile-tga-database/actions/runs/36935490167) passed on `7a17469d400dc49ba31aed56c7d3642fe8029c92`. All701 offline tests, compilation and scientific validation passed; all three merge-triggered checks succeeded. Independent remote verification confirms986 states,1225 conditions,273 DOI sources and275 total sources. All1217 prior condition records and their fields, eleven published file blobs, eight concurrent processing files and three original hashes are preserved. The complete6242702-byte master has SHA256 `0507fcfe67f301d72a63c052acacd3429104deee063fd79fcc0541722309b13b`; the full remote report matches a fresh rebuild. Snapshot:`4318270e5746578cf91610fcc14d71a3ae064cf7c669af4668fc5c17badf0d8a`. Four new pairs and eight TG conditions are published; evidence upgrades and legacy completions are zero;38 held facts remain excluded. Lease release follows this verified publication record.


## b120 Cotton P/N/Si finishes: exact controls, dose mapping and conflicting LOI

Three complete native primary originals (36 pages) add **four new independent initial sample states and seven TG conditions**. Existing-pair evidence upgrades and legacy completions are zero. All41 factual records remain available;34 held records stay outside the target. One primary reviewer checked all native and text pages; no supplements are cited in these originals and zero supplements are claimed as reviewed.

- **10.1007/s12221-016-5316-3:** Table1 untreated CO has LOI18.4; Table2 reports nitrogen T5=309.8C and sole DTG peak361.8C in the native Tmax2 column. TG209F3, nitrogen,10C/min,room temperature to700C. CO is distinct from the NaH2PO2 catalyst-only CO-FR0 state with LOI22.5. Raw control R70015.9 conflicts with the prose description as negligible, so canonical residue is blank while exact T5/DTG remain usable. Generic FR-treated TG lacks a concentration crosswalk and is not assigned to150g/L. The200g/L Table1 row repeats the native CO-FR100 label; concentration and label are both preserved. Pure FR powder is distinct from cotton fabric. Nine held records remain excluded.
- **10.1007/s10570-019-02608-5:** own Table3 control LOI18.2 pairs with two gas conditions at20K/min,40-700C. Nitrogen R7008.5 is explicitly reported; air Table1 partA T5=283.5C,T10=318.1C,Tmax=298.2C,R700=0 are retained as printed. No correction from estimated curves is introduced. The30percent FR state has LOI52.9 in the abstract but52.0 in Table3/body; both of its TG conditions are held. Its50LC LOI also conflicts27.2/27.9. Fifteen washed LOI records lack their own washed TG;20/40percent initial samples lack dose-specific TG. Literature comparison blocks from Liu2018b and Wang2016 are not new own samples. Nineteen held records remain excluded.
- **10.1007/s10570-019-02465-2:** own control and Cotton-DTSP30 have LOI18.2/30.3 and two gas conditions each; STA6000,10C/min,40-800C. Nitrogen T5/Tmax/R800 are280/368/11.2 for control and269/315/40.0 for the treated fabric. Air has explicitly reported R8003.4/17.5; air T5/peaks are not borrowed from nitrogen or estimated. Residues at the nitrogen DTG peak42.0/75.2 and cone residue17.97 are distinct from fixed-temperature TG residues. The30wtpercent coating bath corresponds to16percent fabric weight gain. The preparation rinse is part of the initial state. Lower-dose and durability-washed LOI records have no own matched TG; six held records remain excluded.

Public evidence contains factual values and DOI/page/table/figure locators. Originals, fulltexts, images and private paths remain external. Exact-head checks, ordinary merge, three terminal postmerge checks and complete remote byte verification precede owned lease release.


### b120 publication proof

[PR #88](https://github.com/PolyFT/textile-tga-database/pull/88) merged as `66236931dc8c891b5d0a20a620d9634ab16f902d` after exact-head [validation run 36938428082](https://github.com/PolyFT/textile-tga-database/actions/runs/36938428082) passed on `d354c33396af6fcddec801e33137c4de04b0173f`. All721 offline tests, compilation and scientific validation passed; all three merge-triggered checks succeeded. Independent remote verification confirms990 states,1232 conditions,276 DOI sources and278 total sources. All1225 prior condition records and their fields, eleven published file blobs, eight concurrent processing files and three original hashes are preserved. The complete6291614-byte master has SHA256 `340a0d9abff18ec1ac3ca8535ef2254cdc499c8bc8368ef6afef8e1b9541c0f0`; the full remote report matches a fresh rebuild. Snapshot:`f3eefaddab7d5ba35bed19b88413d367b2b459caf0a04cecc307d1e745290ea1`. Four new pairs and seven TG conditions are published; evidence upgrades and legacy completions are zero;34 held facts remain excluded. Lease release follows this verified publication record.


## b121 Cotton finishes: native thresholds, gas conditions and dose identity

Three complete native primary originals (37 pages) and two complete publisher supplements (four converted native pages, including all tables and the reaction figure) add **six new independent initial sample states and twelve TG conditions**. Evidence upgrades and legacy completions are zero. All42 factual records are preserved;30 held records remain excluded. One primary reviewer checked the complete primary originals and supplements. Fulltexts, supplements, images and private paths remain outside this public repository.

- **10.1016/j.apsusc.2019.145175:** own Table1(PDFp9) and thermal text(pp7-8) pair OCF LOI17.8±0.45 and TCFSi LOI31.8±0.84 with nitrogen and air. TCFSi is explicitly300g/L PEPAS,125g/L CYPA and hydrothermal nanoSiO2 on112g/m2 woven cotton. TG209 uses10C/min,30-700C and approximately5mg dried sample. Air native decomposition onsets292.73/246.98C and reported maximum decomposition temperatures354.43/305.65C are explicit; onset is neither T5/T10 nor the30-110C water-loss event. Air R700 is3.41/15.02%; nitrogen R700 is7.92/37.94%, with no numerical nitrogen onset or peak copied from air. The reported LOI uncertainty type and replicate count are unspecified. LOI dimensions are150x48mm. Five TCF formulations without silica and four20/50-wash states have no own matched TG; nine facts are held. All11 primary pages were reviewed; no supplement is cited.
- **10.1016/j.carbpol.2017.05.054:** own Table1(PDFp7,printed281) and Table2(p8,printed282) pair untreated cotton and2/5/8wt% DHTP finishing baths with LOI18.3/26.1/26.7/27.2, giving four states and eight gas conditions. Cotton is plain woven228g/m2. The204F1 methods are nitrogen/air,10C/min,30-800C,5mg and open alumina pans. Native Tonset10% is recorded as T10, not generic onset or T5. Table1 residues are at600C, despite the800C method endpoint; peak-temperature residues are separate. Air control R600<1.0 is preserved as a bound, with canonical residue blank and exact T10/DTG peaks retained. MPTES-only pretreatment has TG but no own LOI. The8wt% bath has an add-on conflict60.4% in Table2 versus61.4% in prose/conclusion; both native values remain raw while the explicit bath identity remains usable. Nine washed LOI records lack washed TG, and zero-wash rows do not add states. Eleven facts are held. All9 primary pages and complete SI TableS1 were reviewed. The retrieved Elsevier CDN attachment matches the exact publisher PII and all four DHTP mechanical-value pairs in the primary original; the blocked ScienceDirect parent fulltext is not claimed as reviewed.
- **10.1007/s10570-019-02900-4:** own Table1(PDFp8) control LOI18 matches Table2(p11) untreated cotton in air and nitrogen within this original, but both control records remain outside the new-state target because of a possible cross-source shared control. TGA851 uses10K/min,40-800C; the fabric is scoured/bleached100% plain cotton,122g/m2. Air native Tonset/Tmax1/Tmax2 are294/344/489C with R800 printed as a dash, kept blank; nitrogen values are312/369C with R80017.3% and no second peak. Generic onset is not T5/T10. The treated TG label has no concentration crosswalk in the17-page original or complete official Springer supplement, so its air/N2 TG is not assigned to400g/L based on LOI27.6 or the conclusion. Three initial bath-dose LOI records and three washed SI LOI records remain held, together with two generic treated TG records. The supplement defines0.5% detergent,49C,15min and60rpm per cycle, followed by a rinse and70C/1h drying, but provides no washed TG and no treated-dose mapping. Theoretical TG curves, pure flame-retardant powder and cone residue are separate from measured fabric TG. The exact nitrogen control profile (LOI18,Tonset312C,Tmax369C,R80017.3%,10K/min,40-800C) matches the existing control in10.1007/s10570-020-03488-w; the cotton supplier and several authors also coincide, and the air principal peak344C agrees. The originals do not establish experimental independence or a formal sample alias, so both new control gas records are conservatively held pending identity adjudication. All ten factual records from this paper are excluded from the new target; no evidence upgrade or change to prior rows is claimed.

Exact-head checks, ordinary merge, three terminal postmerge checks and complete remote byte verification precede release of the owned writer lease.


### b121 publication proof

[PR #89](https://github.com/PolyFT/textile-tga-database/pull/89) merged as `163c625193d769173516a0a58fa6941ca7f26b39` after exact-head [validation run 36942821389](https://github.com/PolyFT/textile-tga-database/actions/runs/36942821389) passed on `7153349f47cb2583360ff60549ce656c8c55c2c5`. All741 offline tests, compilation and scientific validation passed; all three merge-triggered checks succeeded. Independent remote verification confirms996 states,1244 conditions,278 DOI sources and280 total sources. All1232 prior condition records and their fields, eleven published file blobs, eight concurrent processing files and three original hashes are preserved. The complete6397237-byte master has SHA256 `58c887c82ea35aa8a891a829a3618ab7e250b061e210f8be558d7a7fb2807543`; the full remote report matches a fresh rebuild. Snapshot:`d7299b2a9a112fee22ffc717c80c00ff850d3b1e714be9e5d011008cac563498`. Six new pairs and twelve TG conditions are published; evidence upgrades and legacy completions are zero;30 held facts remain excluded. Lease release follows this verified publication record.


## b122 Fiber identity and treatment lineage

Four complete primary originals (41 native and text pages) add **four new independent initial sample states and seven TG condition records**. Evidence upgrades and legacy completions are zero. All44 factual records are preserved;37 held records remain outside the verified target. One primary reviewer checked all pages; no supplement is cited in these originals. Fulltexts, images and private paths remain outside this public repository.

- **10.1007/s10570-018-2193-5:** own Table2(PDFp13) and thermal text(pp6-9) identify only control cotton and7%ASXPEA cotton, with LOI17.6/41.8 and nitrogen/air TG at20K/min,40-800C. The cotton is124.35g/m2. Own nitrogen R700 is8.6/38.7%; treated air R700 is15.3%, while control air remaining char is qualitative and kept blank. Native air decomposition onsets270/240C and control air DTG maximum346C are explicit. Nitrogen mass-loss range endpoints are neither onset nor peak; no air temperatures are copied. R700 is not the800C method endpoint, and air treated first-stage mass loss38.7% is separate from nitrogen R70038.7%. TGIR8mg and40-600C methods do not supply the main TG mass or endpoint. Native3/5/7/10% concentrations and Table1 bath30/50/70/100g/L are retained without assuming an unspecified percentage basis. Three other initial dose LOIs and fifteen washed LOIs lack same-state TG; eighteen facts are held.
- **10.1007/s12221-011-0166-5:** own fiber Table5(PDFp7,printed172) reports PET/PET-FR/PET-ZnPCD LOI22/29/31, but the whole original has no own fiber TG. Table2(p4) TG belongs to bulk plastic compounds with20wt%total filler, whereas the fibers are produced by diluting the masterbatch to0.5wt%inorganic content before spinning. Plastic LOI dimensions are not assigned to fibers. All three textile LOI facts are held; zero pairs are added.
- **10.1007/s13726-017-0595-0:** own Table3(PDFp8,printed122) reports PVDF porous fiber LOI24.2. Own thermal text(p5,printed119) and numerical Fig4c annotations(p6,printed120) report generic onset463.80C and DTG peak478.86C. The TG method is nitrogen,10C/min,25-800C; char is curve-only and left blank. DSC melting158.8C is a different measurement. The three successive drawing speeds2.6/3.5/4.8m/min describe one production sequence, not three independent samples. LOI uses10g of fibers paved100x40x2mm; cone dimensions and cone replicate counts do not supply LOI conditions. One state and one nitrogen condition are added.
- **10.1016/j.porgcoat.2019.05.010:** the unique uncoated110g/m2 knitted PET control has own Table1(PDFp3,printed164) LOI21.1 with explicitly reported SD0.08. Own Tables3/4(p5,printed166) give nitrogen T10/Tmax/R600402C/436C/5.09% and air T10/Tmax1/Tmax2/R600401C/432C/564C/0.42%. Native onset T-10% is explicitly10wt%mass loss and recorded as T10, not generic onset or T5. TG uses10C/min,room temperature-650C; the reported residue is at600C. Table1 and alkali-treated Table2 reuse PET-1/5/10/20BL labels but report distinct add-ons and LOIs. Thermal Tables3/4 and Fig5 do not explicitly resolve which coated treatment lineage was tested, so both four-dose LOI series and eight treated TG records remain held. Only the uncoated control adds one independent state and two gas conditions.

Exact-head checks, ordinary merge, three terminal postmerge checks and complete remote byte verification precede release of the owned writer lease.


### b122 publication proof

[PR #90](https://github.com/PolyFT/textile-tga-database/pull/90) merged as `eaeef5f285464e855f3d17e054d98b578c531246` after exact-head [validation run 36945659446](https://github.com/PolyFT/textile-tga-database/actions/runs/36945659446) passed on `3f7f9d8bd785a7233ac80a65367ac8950deabb3e`. All761 offline tests, compilation and scientific validation passed; all three merge-triggered checks succeeded. Independent remote verification confirms1000 states,1251 conditions,281 DOI sources and283 total sources. All1244 prior condition records and their fields, eleven published file blobs, eight concurrent processing files and four original hashes are preserved. The complete6468225-byte master has SHA256 `be2fe684f54b9d8ff198a7ac3a6c3e0c8f2d6ae239de74ce562112eabd60719f`; the full remote report matches a fresh rebuild. Snapshot:`e91829adbc3264baad75906d6027f116d82c14b30c40d9ed13ef49ea5bc22efd`. Four new pairs and seven TG conditions are published; evidence upgrades and legacy completions are zero;37 held facts remain excluded. Lease release follows this verified publication record.
