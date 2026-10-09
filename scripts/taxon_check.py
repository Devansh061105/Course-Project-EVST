# -*- coding: utf-8 -*-
"""Plan Step 2: pick one taxonomic group.

Checks record density for birds vs vascular plants in the three case-study
regions SPECIFICALLY (not just the region as a whole), because the plan flags
the Eastern Himalaya as the likely-thin one. Run this before committing to a
taxon; switching now is cheap, switching in week 4 is not.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gbif_lib import (CASE_STUDIES, FACET_LIMIT, TAXA, build_grid, cells_in_box,
                      gbif_cell, hurlbert_rarefy, load_cache, save_cache)

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
CACHE = os.path.join(DATA, "taxon_check_cache.json")
MIN_RECORDS = 20          # plan: exclude cells below this before rarefying
RAREFY_N = 50             # common sample size for the comparison

grid = build_grid(1.0)
cache = load_cache(CACHE)
rows = []

for taxon, key in TAXA.items():
    for region, box in CASE_STUDIES.items():
        for cell in cells_in_box(grid, box):
            ck = "%s|%s" % (taxon, cell["cell_id"])
            if ck not in cache:
                total, ab = gbif_cell(cell["lat_min"], cell["lat_max"],
                                      cell["lon_min"], cell["lon_max"], key)
                cache[ck] = {"total": total, "ab": ab}
                save_cache(CACHE, cache)
                time.sleep(0.3)
            rec = cache[ck]
            ab = rec["ab"]
            rows.append({
                "taxon": taxon, "region": region, "cell_id": cell["cell_id"],
                "total": rec["total"],
                "sp_resolved": sum(ab),
                "obs_richness": len(ab),
                "truncated": len(ab) >= FACET_LIMIT,
                "rarefied50": hurlbert_rarefy(ab, RAREFY_N),
            })

with open(os.path.join(DATA, "taxon_check.json"), "w", encoding="utf-8") as f:
    json.dump(rows, f, indent=1)


def pct(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(p * (len(xs) - 1)))] if xs else 0


print("%-7s %-17s %5s %7s %7s %7s %6s %6s" % (
    "taxon", "region", "cells", "median", "min", "max", "usable", "trunc"))
print("-" * 72)
for taxon in TAXA:
    for region in CASE_STUDIES:
        sub = [r for r in rows if r["taxon"] == taxon and r["region"] == region]
        tot = [r["total"] for r in sub]
        usable = sum(1 for r in sub if r["total"] >= MIN_RECORDS)
        trunc = sum(1 for r in sub if r["truncated"])
        print("%-7s %-17s %5d %7d %7d %7d %4d/%-2d %6d" % (
            taxon, region, len(sub), pct(tot, 0.5), min(tot), max(tot),
            usable, len(sub), trunc))
    print()

print("Rarefied richness at n=%d (median across usable cells):" % RAREFY_N)
for taxon in TAXA:
    for region in CASE_STUDIES:
        v = [r["rarefied50"] for r in rows
             if r["taxon"] == taxon and r["region"] == region and r["rarefied50"]]
        print("  %-7s %-17s n=%-3d median %.1f" % (
            taxon, region, len(v), pct(v, 0.5) if v else 0))
