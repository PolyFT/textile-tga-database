# Source verification progress — 2026-09-30

The reviewed dataset contains **333 unique DOI/sample/washing states**, **383 TG condition records**, and **77 papers**. The near-term target is 500 unique states; **167 remain**. The long-term target remains 2000.

## Batches

- b38: 60 reviewed states, represented by 67 TG conditions. Of these, 15 were genuinely new or newly completed pairs and 45 were existing states upgraded with source evidence
- b39: 81 additional reviewed states, represented by 97 TG conditions. Of these, 56 are new-source or newly completed pairs; 25 are existing states upgraded with source evidence or missing conditions
- b40: 21 additional reviewed states and 31 conditions, comprising 5 new alginate/aramid/PTFE laminate states and 16 existing states with verified source evidence
- b41: 59 additional reviewed states and 59 conditions from seven papers; all 59 were existing numeric sample states upgraded with primary-source evidence. There are zero genuinely new scientific states in this batch
- Cumulative: 135 new/newly completed paired states and 198 existing paired states with upgraded evidence
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
