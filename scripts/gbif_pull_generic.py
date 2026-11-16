# -*- coding: utf-8 -*-
"""Per-cell GBIF pull for any taxon at 1 or 0.5 degrees (Extension D follow-ups).

Usage:  python gbif_pull_generic.py lepidoptera 1.0
        python gbif_pull_generic.py plants 0.5

Same single faceted request per cell, filters and years as the bird pull.
Facet limit 5000. Own append-only cache per taxon and grain:
  data/gbif_cache_<taxon>_<grain>.json   key "taxon|cell_id"
At 1 degree every grid cell is pulled; cells already fetched by taxon2_check.py
(identical request) are copied in, not re-pulled. At 0.5 degree only cells that
can enter a model are pulled (natural-cover dominant class and a GPP value in
data/merged_cells_0p5.csv), which avoids about two thirds of the requests.
Writes data/gbif_cells_<taxon>_<grain>.csv.
"""
import csv
import os
import sys
import time

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gbif_lib import (TAXA, build_grid, gbif_cell, hurlbert_rarefy, load_cache,
                      save_cache)

TAXON = sys.argv[1]
CELL = float(sys.argv[2])
TAG = ("%.1f" % CELL).replace(".", "p")
DATA = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data"))
CACHE = os.path.join(DATA, "gbif_cache_%s_%s.json" % (TAXON, TAG))
FACET = 5000
LEVELS = (50, 100, 250)

grid = build_grid(CELL)
if CELL < 1.0:
    m = pd.read_csv(os.path.join(DATA, "merged_cells_%s.csv" % TAG))
    keep = set(m[m.wc_mode.notna() & ~m.wc_mode.round().isin([40, 50, 80])
                 & m.gpp.notna()].cell_id)
    grid = [c for c in grid if c["cell_id"] in keep]
print("%s at %.1f deg: %d cells to hold" % (TAXON, CELL, len(grid)), flush=True)

cache = load_cache(CACHE)
if CELL == 1.0:
    seed = load_cache(os.path.join(DATA, "taxon2_check_cache.json"))
    n = 0
    for k, v in seed.items():
        if k.startswith(TAXON + "|") and k not in cache:
            cache[k] = v
            n += 1
    if n:
        save_cache(CACHE, cache)
        print("seeded %d cells from the taxon2_check cache" % n, flush=True)

t0 = time.time()
for i, c in enumerate(grid, 1):
    ck = "%s|%s" % (TAXON, c["cell_id"])
    if ck in cache:
        continue
    total, ab = gbif_cell(c["lat_min"], c["lat_max"], c["lon_min"], c["lon_max"],
                          TAXA[TAXON], facet_limit=FACET)
    cache[ck] = {"total": total, "ab": ab}
    save_cache(CACHE, cache)
    if i % 100 == 0:
        print("  %d/%d (cached %d) %.0fs" % (i, len(grid), len(cache), time.time() - t0),
              flush=True)
    time.sleep(0.3)
print("pull complete in %.0fs" % (time.time() - t0), flush=True)

pre = "plant" if TAXON == "plants" else TAXON[:5]
cols = (["cell_id", "lat_c", "lon_c", pre + "_total_records", pre + "_sp_resolved_records",
         pre + "_obs_richness", pre + "_facet_truncated"]
        + ["%s_rarefied_%d" % (pre, n) for n in LEVELS])
out = os.path.join(DATA, "gbif_cells_%s_%s.csv" % (TAXON, TAG))
ntr = 0
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    for c in grid:
        rec = cache["%s|%s" % (TAXON, c["cell_id"])]
        ab = rec["ab"]
        tr = int(len(ab) >= FACET)
        ntr += tr
        row = {"cell_id": c["cell_id"], "lat_c": c["lat_c"], "lon_c": c["lon_c"],
               pre + "_total_records": rec["total"], pre + "_sp_resolved_records": sum(ab),
               pre + "_obs_richness": len(ab), pre + "_facet_truncated": tr}
        for n in LEVELS:
            v = hurlbert_rarefy(ab, n)
            row["%s_rarefied_%d" % (pre, n)] = "" if v is None else round(v, 4)
        w.writerow(row)
print("wrote %s: %d cells, %d facet-truncated" % (out, len(grid), ntr), flush=True)
if ntr:
    print("RAISE FACET: %d cells truncated; their rarefied values are invalid" % ntr,
          flush=True)
