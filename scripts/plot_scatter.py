#!/usr/bin/env python3
"""Plot reviewed TG–LOI data by default; legacy exploration must be explicit."""
import argparse
import csv
import math

try:
    from .pairing import evidence_issues
except ImportError:
    from pairing import evidence_issues


def to_float(value):
    try:
        number = float(value)
        return number if math.isfinite(number) else None
    except (TypeError, ValueError):
        return None


def select_rows(records, args):
    result = []
    for row in records:
        if not args.exploratory and (row.get('pair_quality') != 'A' or evidence_issues(row)):
            continue
        if args.atmosphere and row.get('atmosphere') != args.atmosphere:
            continue
        if args.heating_rate is not None and to_float(row.get('heating_rate_C_min')) != args.heating_rate:
            continue
        if args.material and row.get('material_category') != args.material:
            continue
        if args.dataset and row.get('dataset_type') != args.dataset:
            continue
        x, y = to_float(row.get(args.x)), to_float(row.get(args.y))
        if x is not None and y is not None:
            result.append((x, y, row))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--csv', default='data/tg_loi_master.csv')
    parser.add_argument('--x', default='Tmax1_C')
    parser.add_argument('--y', default='LOI_pct')
    parser.add_argument('--atmosphere')
    parser.add_argument('--heating-rate', type=float)
    parser.add_argument('--material')
    parser.add_argument('--dataset', choices=['literature', 'commercial'])
    parser.add_argument('--exploratory', action='store_true', help='Allow pending/quarantined/legacy data, visibly labeled as exploratory')
    parser.add_argument('--out', default='scatter.png')
    args = parser.parse_args()
    with open(args.csv, encoding='utf-8-sig', newline='') as handle:
        rows = select_rows(csv.DictReader(handle), args)
    if not rows:
        raise SystemExit('No eligible points. Review source evidence or explicitly choose --exploratory with a candidate CSV.')
    conditions = {(r[2].get('atmosphere'), r[2].get('heating_rate_C_min')) for r in rows}
    if not args.exploratory and len(conditions) > 1:
        raise SystemExit('Multiple TG conditions remain. Filter --atmosphere and --heating-rate, or explicitly use --exploratory.')
    import matplotlib.pyplot as plt  # Optional pre-existing plotting dependency, not required for validation.
    fig, ax = plt.subplots(figsize=(5.2, 4.2))
    ax.scatter([r[0] for r in rows], [r[1] for r in rows], alpha=0.75, s=24)
    ax.set_xlabel(args.x)
    ax.set_ylabel(args.y)
    ax.set_title('Exploratory: unreviewed / quarantined data' if args.exploratory else 'Evidence-reviewed exact pairs', fontsize=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.tight_layout()
    fig.savefig(args.out, dpi=600, bbox_inches='tight')
    print(f'{len(rows)} points -> {args.out}; exploratory={args.exploratory}')


if __name__ == '__main__':
    main()
