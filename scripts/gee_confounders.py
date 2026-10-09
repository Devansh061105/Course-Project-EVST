# -*- coding: utf-8 -*-
"""Extract two candidate confounders per 1-degree cell via Earth Engine.

Residual spatial autocorrelation in the corrected model persists to ~10 degrees
(docs/RESULTS_SPATIAL.md), which points to an omitted broad-scale driver. Two
textbook candidates that could raise bird richness AND alter productivity:

  elev_mean, elev_sd   SRTM 30 m, sampled at 500 m. elev_sd is topographic
                       heterogeneity - a near-universal positive driver of
                       richness (Stein, Gerstner & Kreft 2014, Ecol. Lett.).
  ndvi_cv              per-pixel coefficient of variation of MOD13Q1 NDVI over
                       2019-2023, then cell-averaged: productivity seasonality,
                       the component Coops et al. (2009) found most predictive of
                       bird richness from MODIS.

Writes data/confounders_1p0.csv. Cached per batch; restart-safe.
"""
import csv
import json
import os
import sys
import time

import ee

EE_PROJECT = os.environ.get("EE_PROJECT", "")
# Optional cell size (degrees). 1.0 (default) reproduces the original behaviour
# exactly. For finer grids only the cells already pulled from GBIF are extracted,
# and NPP is added (the 1-degree table already has it from gee_cells.csv).
CELL = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
TAG = ("%.1f" % CELL).replace(".", "p")
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
CACHE = os.path.join(DATA, "confounders_cache_%s.json" % TAG)
BATCH = 50

if not EE_PROJECT:
    sys.exit("set EE_PROJECT")
ee.Initialize(project=EE_PROJECT)

if CELL == 1.0:
    with open(os.path.join(DATA, "grid_1deg.geojson"), "r", encoding="utf-8") as f:
        feats = json.load(f)["features"]
else:
    sys.path.insert(0, HERE)
    from gbif_lib import build_grid, grid_geojson
    with open(os.path.join(DATA, "gbif_cache_%s.json" % TAG), "r", encoding="utf-8") as f:
        have = set(json.load(f))
    feats = [x for x in grid_geojson(build_grid(CELL))["features"]
             if x["properties"]["cell_id"] in have]
print("cell size %.1f deg: %d cells to extract" % (CELL, len(feats)), flush=True)

elev = ee.Image("USGS/SRTMGL1_003").select("elevation")


def _mask(img):
    b = img.select("NDVI")
    return b.updateMask(b.gte(-2000).And(b.lte(10000))).multiply(0.0001)


ndvi = (ee.ImageCollection("MODIS/061/MOD13Q1")
        .filterDate("2019-01-01", "2023-12-31").map(_mask))
ndvi_cv = ndvi.reduce(ee.Reducer.stdDev()).divide(
    ndvi.reduce(ee.Reducer.mean()).max(0.05))     # floor avoids /0 over desert

# Every image here is SINGLE-band, so every reducer needs setOutputs - otherwise
# the property is named after the reducer and the column comes back all null.
def _npp(img):
    b = img.select("Npp")
    return b.updateMask(b.gte(-30000).And(b.lte(32700))).multiply(0.0001)


npp = (ee.ImageCollection("MODIS/061/MOD17A3HGF")
       .filterDate("2019-01-01", "2023-12-31").map(_npp).mean())

PRODUCTS = [
    (elev, ee.Reducer.mean().setOutputs(["elev_mean"]), 500, "elev_mean"),
    (elev, ee.Reducer.stdDev().setOutputs(["elev_sd"]), 500, "elev_sd"),
    (ndvi_cv, ee.Reducer.mean().setOutputs(["ndvi_cv"]), 500, "ndvi_cv"),
]
if CELL != 1.0:
    PRODUCTS.append((npp, ee.Reducer.mean().setOutputs(["npp"]), 500, "npp"))
KEYS = [p[3] for p in PRODUCTS]

cache = {}
if os.path.exists(CACHE):
    with open(CACHE, "r", encoding="utf-8") as f:
        cache = json.load(f)
todo = [f for f in feats if f["properties"]["cell_id"] not in cache]
print("cells: %d, cached %d, to do %d" % (len(feats), len(cache), len(todo)), flush=True)

t0 = time.time()
for b in range(0, len(todo), BATCH):
    chunk = todo[b:b + BATCH]
    fc = ee.FeatureCollection({"type": "FeatureCollection", "features": chunk})
    acc = {f["properties"]["cell_id"]: {} for f in chunk}
    for img, red, scale, key in PRODUCTS:
        for attempt in range(3):
            try:
                res = img.reduceRegions(collection=fc, reducer=red, scale=scale,
                                        tileScale=4).getInfo()
                for ft in res["features"]:
                    acc[ft["properties"]["cell_id"]][key] = ft["properties"].get(key)
                break
            except Exception as e:
                if attempt == 2:
                    print("  FAIL %s: %s" % (key, str(e)[:120]), flush=True)
                else:
                    time.sleep(5 * (attempt + 1))
    cache.update(acc)
    tmp = CACHE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cache, f)
    os.replace(tmp, CACHE)
    print("  batch %d-%d  %.0fs" % (b, b + len(chunk), time.time() - t0), flush=True)

cols = ["cell_id"] + KEYS
with open(os.path.join(DATA, "confounders_%s.csv" % TAG), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    for ft in feats:
        cid = ft["properties"]["cell_id"]
        row = {"cell_id": cid}
        row.update({k: cache.get(cid, {}).get(k) for k in cols[1:]})
        w.writerow(row)

nonnull = {k: sum(1 for c in cache.values() if c.get(k) is not None) for k in cols[1:]}
print("non-null per column: %s" % nonnull, flush=True)
if min(nonnull.values()) == 0:
    sys.exit("ABORT: a column is entirely null - check reducer output names")
print("wrote data/confounders_%s.csv" % TAG)
