# -*- coding: utf-8 -*-
"""Extension D, step 2: pull the second taxon (vascular plants) per 1-degree cell.

Same single faceted request per cell as the bird pull (gbif_pull.py), same
filters and year range, but with a higher facet ceiling because plant cells can
exceed 1,200 species (DECISIONS.md, project-review correction 8).

Writes:
  data/gbif_cache_plants.json  - per-cell {total, abundance vector}; append-only
  data/gbif_cells_plants.csv   - per-cell richness table

Restartable: cached cells are skipped. Cells already fetched by
taxon2_check.py (identical request) are copied in, not re-pulled.
"""
import csv
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gbif_lib import (TAXA, build_grid, gbif_cell, hurlbert_rarefy, load_cache,
                      save_cache)

DATA = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "data"))
CACHE = os.path.join(DATA, "gbif_cache_plants.json")
SEED = os.path.join(DATA, "taxon2_check_cache.json")
TAXON = "plants"
FACET_LIMIT_PLANTS = 5000
RAREFY_LEVELS = (50, 100, 250)

grid = build_grid(1.0)
cache = load_cache(CACHE)
seed = load_cache(SEED)
n_seed = 0
for k, v in seed.items():
    if k.startswith(TAXON + "|") and k not in cache:
        cache[k] = v
        n_seed += 1
if n_seed:
    save_cache(CACHE, cache)
print("seeded %d cells from taxon2_check cache; %d cached at start"
      % (n_seed, len(cache)), flush=True)

t0 = time.time()
for i, cell in enumerate(grid, 1):
    ck = "%s|%s" % (TAXON, cell["cell_id"])
    if ck in cache:
        continue
    total, ab = gbif_cell(cell["lat_min"], cell["lat_max"], cell["lon_min"],
                          cell["lon_max"], TAXA[TAXON],
                          facet_limit=FACET_LIMIT_PLANTS)
    cache[ck] = {"total": total, "ab": ab}
    save_cache(CACHE, cache)
    if i % 50 == 0:
        print("  %d/%d cells (cached %d) %.0fs" % (i, len(grid), len(cache),
                                                  time.time() - t0), flush=True)
    time.sleep(0.3)
print("pull complete in %.0fs" % (time.time() - t0), flush=True)

cols = (["cell_id", "plant_total_records", "plant_sp_resolved_records",
         "plant_obs_richness", "plant_facet_truncated"]
        + ["plant_rarefied_%d" % n for n in RAREFY_LEVELS])
out = os.path.join(DATA, "gbif_cells_plants.csv")
n_trunc = 0
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    for cell in grid:
        rec = cache["%s|%s" % (TAXON, cell["cell_id"])]
        ab = rec["ab"]
        trunc = int(len(ab) >= FACET_LIMIT_PLANTS)
        n_trunc += trunc
        row = {"cell_id": cell["cell_id"], "plant_total_records": rec["total"],
               "plant_sp_resolved_records": sum(ab),
               "plant_obs_richness": len(ab), "plant_facet_truncated": trunc}
        for n in RAREFY_LEVELS:
            v = hurlbert_rarefy(ab, n)
            row["plant_rarefied_%d" % n] = "" if v is None else round(v, 4)
        w.writerow(row)
print("wrote %s: %d cells, %d facet-truncated" % (out, len(grid), n_trunc),
      flush=True)
if n_trunc:
    print("FACET_LIMIT_PLANTS too low for %d cells: raise it and re-pull those "
          "cells before using their rarefied values" % n_trunc, flush=True)
