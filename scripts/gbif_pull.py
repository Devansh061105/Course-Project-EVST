# -*- coding: utf-8 -*-
"""Plan Step 3: pull GBIF occurrence data per grid cell, full study region.

Writes:
  data/grid_1deg.geojson   - grid for ingestion as an ee.FeatureCollection (Step 4)
  data/gbif_cache.json     - per-cell {total, abundance vector}, restartable
  data/gbif_cells.csv      - per-cell richness table (the GBIF half of Step 5)

Caches after every cell, so a network failure on cell 400 of 884 does not force
a restart. Safe to re-run: cached cells are skipped.
"""
import csv
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gbif_lib import (FACET_LIMIT, TAXA, build_grid, gbif_cell, grid_geojson,
                      hurlbert_rarefy, load_cache, save_cache)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
CACHE = os.path.join(DATA, "gbif_cache.json")

TAXON = "birds"
MIN_RECORDS = 20                       # plan: drop cells below this before rarefying
RAREFY_LEVELS = (50, 100, 250)         # sensitivity to the standardisation level

grid = build_grid(1.0)

with open(os.path.join(DATA, "grid_1deg.geojson"), "w", encoding="utf-8") as f:
    json.dump(grid_geojson(grid), f)
print("grid: %d cells -> data/grid_1deg.geojson" % len(grid), flush=True)

cache = load_cache(CACHE)
t0 = time.time()
for i, cell in enumerate(grid, 1):
    ck = "%s|%s" % (TAXON, cell["cell_id"])
    if ck in cache:
        continue
    total, ab = gbif_cell(cell["lat_min"], cell["lat_max"],
                          cell["lon_min"], cell["lon_max"], TAXA[TAXON])
    cache[ck] = {"total": total, "ab": ab}
    save_cache(CACHE, cache)
    if i % 25 == 0:
        done = sum(1 for k in cache if k.startswith(TAXON + "|"))
        el = time.time() - t0
        print("  %d/%d cells (cached %d) %.0fs elapsed" % (i, len(grid), done, el),
              flush=True)
    time.sleep(0.3)

print("pull complete in %.0fs" % (time.time() - t0), flush=True)

cols = (["cell_id", "lat_c", "lon_c", "lat_min", "lat_max", "lon_min", "lon_max",
         "total_records", "sp_resolved_records", "obs_richness",
         "facet_truncated", "below_min_records"]
        + ["rarefied_%d" % n for n in RAREFY_LEVELS])

out = os.path.join(DATA, "gbif_cells.csv")
n_written = n_usable = n_trunc = 0
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    for cell in grid:
        rec = cache.get("%s|%s" % (TAXON, cell["cell_id"]))
        if rec is None:
            continue
        ab = rec["ab"]
        row = {k: cell[k] for k in ("cell_id", "lat_c", "lon_c", "lat_min",
                                    "lat_max", "lon_min", "lon_max")}
        row.update({
            "total_records": rec["total"],
            "sp_resolved_records": sum(ab),
            "obs_richness": len(ab),
            "facet_truncated": int(len(ab) >= FACET_LIMIT),
            "below_min_records": int(rec["total"] < MIN_RECORDS),
        })
        for n in RAREFY_LEVELS:
            v = hurlbert_rarefy(ab, n)
            row["rarefied_%d" % n] = "" if v is None else round(v, 4)
        w.writerow(row)
        n_written += 1
        n_usable += rec["total"] >= MIN_RECORDS
        n_trunc += len(ab) >= FACET_LIMIT

print("wrote %s: %d cells, %d usable (>=%d records), %d facet-truncated"
      % (out, n_written, n_usable, MIN_RECORDS, n_trunc), flush=True)
