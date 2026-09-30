# Recovered legacy audit

- PA56 7 states and ZnO/MDPA 4 states remain genuinely new relative to original inputs.
- Used repaired csv_ingest.read_source_csv with bytecode writing disabled; no repository changes.
- Read 42 observation files, 873 accepted observations; removed 2 exact wrappers; quarantined 1 malformed unrelated NYCO record.
- Separately inspected 4 non-observation source indexes (20 rows), including their wrapper; neither target DOI nor any new union DOI appeared there.
- Checked source titles for different/missing DOI aliases; no near-identical legacy title candidates were found.

## Full union versus recovered pre-b38 baseline
- 78 independent source/sample/wash states, 89 condition rows.
- 65 new-source states (63 full-condition, 2 partial), 6 old TG states newly completed with LOI, 7 old pairs reverified.
- No earlier extraction classification changed after wrapper recovery.
- Legacy overlaps are only fib9110069 (7 exact labels) and 15280837221116590 (6 exact labels). Their overlapping TG numbers agree.
- Old wash fields are blank. Identity is source-specific: same exact sample label, same TG values, and the primary-source table crosswalk. Blank wash is never globally interpreted as zero, and distinct washed states are not merged.
- Both atmosphere observations for cashmere/alginate, PNCTSi cotton, and ramie remain condition records within one source/sample/wash state.

## Union versus current b38
- 18 union states are already included in b38: 7 fib9110069, 7 PA56, 4 ZnO/MDPA.
- pending_after_b38_pairs.json/CSV contains 60 independent states / 71 condition rows absent from b38.
- Of these, 58 states have full conditions and 2 are partial ma16010286 candidates.
- Pending state categories: 54 new-source states (52 full-condition + 2 partial), 4 old TG-to-pair completions, and 2 old-pair condition reverifications.
- Do not treat all 60 pending states as 60 net additions to paired data. The 2 reverifications already had LOI; the 2 partial states remain candidates.
- Exact b38 comparisons retain sample label and washing_state, rather than DOI-only collapsing.

Detailed per-state old record IDs, old source rows, washing history, changed fields, and current-b38 status are in recovered_legacy_diff.csv/JSON.
