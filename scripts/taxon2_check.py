# -*- coding: utf-8 -*-
"""Extension D, step 1: choose the second taxon by live record density.

Samples every 5th modelled cell (data/model_cells.csv) and asks GBIF for the
species-abundance vector of each candidate group. A group is usable only if
most modelled cells hold enough species-identified records to rarefy.
Cache: data/taxon2_check_cache.json (append-only, restartable).
"""
import csv
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gbif_lib import gbif_cell, hurlbert_rarefy, load_cache, save_cache

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
CACHE = os.path.join(DATA, "taxon2_check_cache.json")
CANDIDATES = {"mammals": 359, "lepidoptera": 797, "plants": 7707728,
              "reptiles_squamata": 11592253, "amphibians": 131}
FACET = 5000

with open(os.path.join(DATA, "model_cells.csv"), encoding="utf-8") as f:
    cells = list(csv.DictReader(f))[::5]

cache = load_cache(CACHE)
for taxon, key in CANDIDATES.items():
    for c in cells:
        ck = "%s|%s" % (taxon, c["cell_id"])
        if ck in cache:
            continue
        total, ab = gbif_cell(float(c["lat_min"]), float(c["lat_max"]),
                              float(c["lon_min"]), float(c["lon_max"]), key,
                              facet_limit=FACET)
        cache[ck] = {"total": total, "ab": ab}
        save_cache(CACHE, cache)
        time.sleep(0.3)

print("sampled modelled cells: %d" % len(cells))
print("%-18s %8s %6s %6s %6s %6s %6s" % ("taxon", "median", ">=50", ">=100",
                                         ">=250", "trunc", "medS50"))
for taxon in CANDIDATES:
    recs = [cache["%s|%s" % (taxon, c["cell_id"])] for c in cells]
    n = sorted(sum(r["ab"]) for r in recs)
    s50 = sorted(v for v in (hurlbert_rarefy(r["ab"], 50) for r in recs) if v)
    print("%-18s %8d %6d %6d %6d %6d %6.1f" % (
        taxon, n[len(n) // 2], sum(x >= 50 for x in n), sum(x >= 100 for x in n),
        sum(x >= 250 for x in n), sum(len(r["ab"]) >= FACET for r in recs),
        s50[len(s50) // 2] if s50 else 0))
