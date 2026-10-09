# -*- coding: utf-8 -*-
"""Plan Step 8: rerun the whole pipeline at a different grid size.

Usage:  python grid_robustness.py 2.0
        python grid_robustness.py 0.5

Rebuilds the grid, re-pulls GBIF, re-extracts Earth Engine, re-merges and
refits both OLS and the spatial error model at the requested cell size, so the
1-degree conclusion can be checked against a coarser and a finer grain.
Everything is cached per cell size, so re-running is cheap and interruption-safe.
"""
import csv
import json
import os
import sys
import time
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
import libpysal
import esda
from scipy.stats import norm
from spreg import ML_Error, ML_Lag, OLS as sOLS

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
sys.path.insert(0, HERE)
from gbif_lib import (FACET_LIMIT, TAXA, build_grid, gbif_cell, grid_geojson,
                      hurlbert_rarefy, load_cache, save_cache)
from weights_sensitivity import queen_from_grid

CELL = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
TAG = ("%.1f" % CELL).replace(".", "p")
TAXON = "birds"
MIN_RECORDS = 20
RARE_N = 250
DROP_MODE = {40, 50, 80}
BATCH = 50
EE_PROJECT = os.environ.get("EE_PROJECT", "")
X_COLS = ["rarefied", "log_effort", "temp_c", "precip_mm_yr"]
RI = X_COLS.index("rarefied") + 1

grid = build_grid(CELL)
print("=== cell size %.1f deg : %d cells ===" % (CELL, len(grid)), flush=True)

# Finer grids: skip sub-cells whose parent 1-degree cell is open sea (no
# WorldCover coverage at all). They can never enter a model, and pulling them
# roughly doubles run time. Only affects cells not already cached.
SEA = set()
_parent = os.path.join(DATA, "merged_cells.csv")
if CELL < 1.0 and os.path.exists(_parent):
    _p = pd.read_csv(_parent)
    _sea_parents = set(zip(_p[_p.wc_mode.isna()].lat_c.round(2),
                           _p[_p.wc_mode.isna()].lon_c.round(2)))
    for c in grid:
        key = (round(np.floor(c["lat_c"]) + 0.5, 2), round(np.floor(c["lon_c"]) + 0.5, 2))
        if key in _sea_parents:
            SEA.add(c["cell_id"])
    print("  skipping %d sub-cells whose 1-degree parent is open sea" % len(SEA), flush=True)

# ---------------------------------------------------------------- GBIF
gcache_p = os.path.join(DATA, "gbif_cache_%s.json" % TAG)
gcache = load_cache(gcache_p)
# MAX_PULLS caps one run so it finishes inside a bounded window (background tasks
# are killed at ~30 min). Progress is cached; re-running continues where it stopped.
MAX_PULLS = int(os.environ.get("MAX_PULLS", "0")) or None
t0 = time.time()
for i, c in enumerate(grid, 1):
    if c["cell_id"] in gcache or c["cell_id"] in SEA:
        continue
    if MAX_PULLS and globals().get("pulled", 0) >= MAX_PULLS:
        break
    total, ab = gbif_cell(c["lat_min"], c["lat_max"], c["lon_min"], c["lon_max"],
                          TAXA[TAXON])
    gcache[c["cell_id"]] = {"total": total, "ab": ab}
    # Save by number of cells actually PULLED, not by grid index: with cached and
    # sea cells skipped, a grid-index trigger can go hundreds of pulls unsaved.
    pulled = globals().get("pulled", 0) + 1
    globals()["pulled"] = pulled
    if pulled % 50 == 0:
        save_cache(gcache_p, gcache)
        print("  gbif grid pos %d/%d, cached %d  %.0fs"
              % (i, len(grid), len(gcache), time.time() - t0), flush=True)
    time.sleep(0.25)
save_cache(gcache_p, gcache)
remaining = sum(1 for c in grid if c["cell_id"] not in gcache and c["cell_id"] not in SEA)
print("  gbif: %d cells cached, %d land cells remaining, %.0fs"
      % (len(gcache), remaining, time.time() - t0), flush=True)
if remaining:
    print("  STOPPED at MAX_PULLS=%s - re-run to continue (cache saved)" % MAX_PULLS,
          flush=True)
    sys.exit(0)
print("  gbif done", flush=True)

# ---------------------------------------------------------------- Earth Engine
import ee
if not EE_PROJECT:
    sys.exit("set EE_PROJECT")
ee.Initialize(project=EE_PROJECT)

ecache_p = os.path.join(DATA, "gee_cache_%s.json" % TAG)
ecache = load_cache(ecache_p)
start, end = "2019-01-01", "2023-12-31"


def _mask(img, band, lo, hi):
    b = img.select(band)
    return b.updateMask(b.gte(lo).And(b.lte(hi)))


mod17 = (ee.ImageCollection("MODIS/061/MOD17A3HGF").filterDate(start, end)
         .map(lambda i: _mask(i, "Gpp", 0, 65500)).mean()
         .multiply(0.0001).rename(["gpp"]))
era = ee.ImageCollection("ECMWF/ERA5_LAND/MONTHLY_AGGR").filterDate(start, end)
clim = (era.select("temperature_2m").mean().subtract(273.15).rename("temp_c")
        .addBands(era.select("total_precipitation_sum").mean()
                  .multiply(1000.0 * 12.0).rename("precip_mm_yr")))
wc = ee.Image("ESA/WorldCover/v200/2021").select("Map")
natural = wc.remap([10, 20, 30, 60, 90, 95, 100], [1] * 7, 0).rename("natural_frac")

# setOutputs is MANDATORY for any SINGLE-band image: reduceRegions names the
# output property after the reducer ("mean"/"mode"), not after the band, so
# without it the column comes back null for every cell and the filter silently
# drops everything. Multi-band images (clim) are named by band and are fine.
PRODUCTS = [(mod17, ee.Reducer.mean().setOutputs(["gpp"]), 500, ["gpp"]),
            (clim, ee.Reducer.mean(), 11132, ["temp_c", "precip_mm_yr"]),
            (natural, ee.Reducer.mean().setOutputs(["natural_frac"]), 500,
             ["natural_frac"]),
            (wc, ee.Reducer.mode().setOutputs(["wc_mode"]), 500, ["wc_mode"])]

gj = grid_geojson(grid)["features"]
todo = [f for f in gj if f["properties"]["cell_id"] not in ecache
        and f["properties"]["cell_id"] not in SEA
        and f["properties"]["cell_id"] in gcache]
t0 = time.time()
for b in range(0, len(todo), BATCH):
    chunk = todo[b:b + BATCH]
    fc = ee.FeatureCollection({"type": "FeatureCollection", "features": chunk})
    acc = {f["properties"]["cell_id"]: {} for f in chunk}
    for img, red, scale, keys in PRODUCTS:
        for attempt in range(3):
            try:
                res = img.reduceRegions(collection=fc, reducer=red, scale=scale,
                                        tileScale=4).getInfo()
                for ft in res["features"]:
                    p = ft["properties"]
                    acc[p["cell_id"]].update({k: p.get(k) for k in keys})
                break
            except Exception as e:
                if attempt == 2:
                    print("    EE fail %s: %s" % (keys, str(e)[:80]), flush=True)
                else:
                    time.sleep(5 * (attempt + 1))
    ecache.update(acc)
    if (b // BATCH) % 5 == 0:
        save_cache(ecache_p, ecache)
        print("  gee %d/%d  %.0fs" % (b + len(chunk), len(todo), time.time() - t0),
              flush=True)
save_cache(ecache_p, ecache)
print("  gee done: %d cells, %.0fs" % (len(ecache), time.time() - t0), flush=True)

# ---------------------------------------------------------------- assemble
rows = []
for c in grid:
    g = gcache.get(c["cell_id"])
    e = ecache.get(c["cell_id"], {})
    if g is None:
        continue
    ab = g["ab"]
    rows.append({
        "cell_id": c["cell_id"], "lat_c": c["lat_c"], "lon_c": c["lon_c"],
        "total_records": g["total"], "obs_richness": len(ab),
        "truncated": int(len(ab) >= FACET_LIMIT),
        "rarefied": hurlbert_rarefy(ab, RARE_N),
        "gpp": e.get("gpp"), "temp_c": e.get("temp_c"),
        "precip_mm_yr": e.get("precip_mm_yr"),
        "natural_frac": e.get("natural_frac"),
        "wc_mode": None if e.get("wc_mode") is None else round(e["wc_mode"]),
    })
df = pd.DataFrame(rows)
# Guard: an all-null column means a reduceRegions output-naming mismatch, not
# an absence of data. Fail loudly rather than silently filtering to zero rows.
for _c in ("gpp", "temp_c", "precip_mm_yr", "natural_frac", "wc_mode"):
    if df[_c].notna().sum() == 0:
        sys.exit("ABORT: column '%s' is null for all %d cells - check the "
                 "reduceRegions output name (single-band images need "
                 "setOutputs)." % (_c, len(df)))

df["log_effort"] = np.log10(df.total_records.clip(lower=1))
df.to_csv(os.path.join(DATA, "merged_cells_%s.csv" % TAG), index=False)
print("  truncated cells: %d" % df.truncated.sum(), flush=True)

d = df[df.gpp.notna() & df.wc_mode.notna() & (~df.wc_mode.isin(DROP_MODE))
       & (df.total_records >= MIN_RECORDS) & df.rarefied.notna()
       & df.temp_c.notna() & df.precip_mm_yr.notna()].copy()
print("  eligible cells: %d of %d" % (len(d), len(df)), flush=True)
if len(d) < 30:
    sys.exit("  too few eligible cells to model at this grain")

# ---------------------------------------------------------------- fit
y = d.gpp.astype(float).values.reshape(-1, 1)
X = d[X_COLS].astype(float).values
w = queen_from_grid(d.lat_c.values, d.lon_c.values, CELL)
w.transform = "r"

ols_sm = sm.OLS(d.gpp.astype(float),
                sm.add_constant(d[X_COLS].astype(float))).fit(cov_type="HC3")
o = sOLS(y, X, w=w, spat_diag=True, moran=True)
err = ML_Error(y, X, w=w)
lag = ML_Lag(y, X, w=w)
b = float(err.betas[RI][0]); se = float(np.sqrt(err.vm[RI, RI]))
p = 2 * (1 - norm.cdf(abs(b / se)))
mi_f = esda.Moran(np.asarray(err.e_filtered).flatten(), w, permutations=499)

print("\n--- RESULTS at %.1f deg (n=%d) ---" % (CELL, len(d)))
print("  OLS+HC3   richness beta=%+.6f  p=%.4g" % (
    ols_sm.params["rarefied"], ols_sm.pvalues["rarefied"]))
print("  Moran I (OLS resid) = %.3f" % o.moran_res[0])
print("  robust LM lag=%.1f  robust LM error=%.1f  -> AIC winner: %s"
      % (o.rlm_lag[0], o.rlm_error[0], "error" if err.aic < lag.aic else "lag"))
print("  ML_Error  richness beta=%+.6f  se=%.6f  p=%.4f  -> %s"
      % (b, se, p, "SIGNIFICANT" if p < 0.05 else "not significant"))
print("  residual Moran I (e_filtered) = %+.3f (p=%.3f)" % (mi_f.I, mi_f.p_sim))
