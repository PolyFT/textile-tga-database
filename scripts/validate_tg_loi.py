#!/usr/bin/env python3
"""Validate TG-LOI CSVs and build a strict paired master table."""

from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT_DIR = DATA / "automation"
OUT_DIR.mkdir(parents=True, exist_ok=True)
MASTER = DATA / "tg_loi_master.csv"
REPORT = OUT_DIR / "validation_report.json"

TG_FIELDS = [
    "T1_C","T5_C","T10_C","T20_C","T40_C","T50_C","Tonset_C",
    "Tmax1_C","Tmax2_C","Tmax3_C","R400_pct","R500_pct","R550_pct",
    "R600_pct","R650_pct","R700_pct","R800_pct","residue_pct",
    "residue_at_Tmax_pct","residue_at_Tmax1_pct","residue_at_Tmax2_pct","residue_at_Tmax3_pct",
]

def num(s):
    return pd.to_numeric(s, errors="coerce")

def load_all() -> pd.DataFrame:
    frames = []
    paths = [DATA / "scatter_ready.csv"]
    paths += sorted((DATA / "incoming").glob("verified*.csv"))
    for p in paths:
        if not p.exists():
            continue
        try:
            df = pd.read_csv(p, low_memory=False)
        except Exception as exc:
            print(f"skip {p}: {exc}")
            continue
        df["source_file"] = str(p.relative_to(ROOT))
        frames.append(df)
    if not frames:
        return pd.DataFrame()
    cols = sorted(set().union(*(f.columns for f in frames)))
    return pd.concat([f.reindex(columns=cols) for f in frames], ignore_index=True)

def main():
    df = load_all()
    errors = []
    if df.empty:
        raise SystemExit("No input data found")

    for col in [c for c in df.columns if c.startswith("T") and c.endswith("_C")]:
        x = num(df[col])
        bad = df[x.notna() & ((x < 20) | (x > 1500))]
        if len(bad):
            errors.append(f"{col}: {len(bad)} values outside 20–1500 °C")

    percent_cols = [c for c in df.columns if c.endswith("_pct") and (
        c == "LOI_pct" or c.startswith("R") or "residue" in c.lower()
    )]
    for col in percent_cols:
        x = num(df[col])
        bad = df[x.notna() & ((x < 0) | (x > 100))]
        if len(bad):
            errors.append(f"{col}: {len(bad)} values outside 0–100%")

    loi = num(df.get("LOI_pct", pd.Series(index=df.index, dtype=float)))
    tg_present = pd.Series(False, index=df.index)
    for col in TG_FIELDS:
        if col in df:
            tg_present |= num(df[col]).notna()

    atm = df.get("atmosphere", pd.Series("", index=df.index)).fillna("").astype(str).str.strip()
    rate = num(df.get("heating_rate_C_min", pd.Series(index=df.index, dtype=float)))

    strict = loi.notna() & tg_present & atm.ne("") & rate.notna()
    if "direct_numeric_use" in df:
        tag = df["direct_numeric_use"].fillna("").astype(str).str.lower()
        strict &= ~tag.str.contains("tg-only|否|no", regex=True)

    master = df.loc[strict].copy()
    doi = master.get("DOI", pd.Series("", index=master.index)).fillna("").astype(str).str.lower().str.strip()
    sample = master.get("sample_state", pd.Series("", index=master.index)).fillna("").astype(str).str.strip()
    atmosphere = master.get("atmosphere", pd.Series("", index=master.index)).fillna("").astype(str).str.strip()
    heating = master.get("heating_rate_C_min", pd.Series("", index=master.index)).fillna("").astype(str).str.strip()
    master["pair_quality"] = "A"
    master["pair_key"] = doi + "||" + sample + "||" + atmosphere + "||" + heating
    master = master.drop_duplicates(subset=["pair_key"], keep="first")
    master.to_csv(MASTER, index=False)

    report = {
        "all_loaded_rows": int(len(df)),
        "strict_tg_loi_pairs": int(len(master)),
        "rows_with_numeric_loi": int(loi.notna().sum()),
        "rows_with_any_tg_numeric": int(tg_present.sum()),
        "rows_missing_atmosphere_among_pair_candidates": int((loi.notna() & tg_present & atm.eq("")).sum()),
        "rows_missing_heating_rate_among_pair_candidates": int((loi.notna() & tg_present & rate.isna()).sum()),
        "target_pairs": 2000,
        "remaining_to_target": max(0, 2000 - int(len(master))),
        "errors": errors,
    }
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if errors:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
