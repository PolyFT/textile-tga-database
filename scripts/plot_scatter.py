#!/usr/bin/env python3
"""
Generic paper-scatter generator for data/scatter_ready.csv.
Example:
  python scripts/plot_scatter.py --x Tmax1_C --y LOI_pct --atmosphere N2 --material 棉
"""
import argparse
import csv
import math
import matplotlib.pyplot as plt

def to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

p = argparse.ArgumentParser()
p.add_argument("--csv", default="data/scatter_ready.csv")
p.add_argument("--x", default="Tmax1_C")
p.add_argument("--y", default="LOI_pct")
p.add_argument("--atmosphere", default=None)
p.add_argument("--material", default=None)
p.add_argument("--dataset", default=None, choices=[None, "literature", "commercial"])
p.add_argument("--out", default="scatter.png")
args = p.parse_args()

rows = []
with open(args.csv, encoding="utf-8-sig", newline="") as f:
    for r in csv.DictReader(f):
        if args.atmosphere and r.get("atmosphere") != args.atmosphere:
            continue
        if args.material and r.get("material_category") != args.material:
            continue
        if args.dataset and r.get("dataset_type") != args.dataset:
            continue
        x, y = to_float(r.get(args.x)), to_float(r.get(args.y))
        if x is None or y is None:
            continue
        rows.append((x, y, r))

fig, ax = plt.subplots(figsize=(5.2, 4.2))
ax.scatter([r[0] for r in rows], [r[1] for r in rows], alpha=0.75, s=24)
ax.set_xlabel(args.x)
ax.set_ylabel(args.y)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
fig.tight_layout()
fig.savefig(args.out, dpi=600, bbox_inches="tight")
print(f"{len(rows)} points -> {args.out}")