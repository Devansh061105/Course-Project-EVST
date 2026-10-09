# -*- coding: utf-8 -*-
"""Plan Step 4, chunked fallback for gee_extract.py.

Two changes from the single-shot version:

1. Cells are processed in batches, so each getInfo payload is small and each
   request stays inside Earth Engine's interactive timeout. Results are cached
   per batch, so a failure at batch 12 of 18 does not lose the first 11.

2. WorldCover is sampled at 500 m rather than 100 m. It is a 10 m product, but
   we only need the cropland / built-up / water FRACTION of a 1-degree cell:
   500 m sampling still gives ~49,000 samples per cell, which pins a fraction
   far more tightly than the analysis needs, while costing 25x less compute
   than 100 m and ~2500x less than native 10 m.
"""
import csv
import json
import os
import sys
import time

import ee

EE_PROJECT = os.environ.get("EE_PROJECT", "")
YEARS = (2019, 2023)
BATCH = 50

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
CACHE = os.path.join(DATA, "gee_cache.json")

# 40 cropland, 50 built-up (plan Step 4). 80 permanent water added: sea cells
# are not undersampled land. 70 snow/ice also excluded from "natural terrestrial".
WC_EXCLUDE = [40, 50]
WC_WATER = [80]
WC_NATURAL = [10, 20, 30, 60, 90, 95, 100]

if not EE_PROJECT:
    sys.exit("Set EE_PROJECT first.")
ee.Initialize(project=EE_PROJECT)

with open(os.path.join(DATA, "grid_1deg.geojson"), "r", encoding="utf-8") as f:
    feats = json.load(f)["features"]
print("grid: %d cells" % len(feats), flush=True)

start, end = "%d-01-01" % YEARS[0], "%d-12-31" % YEARS[1]

# Fill values MUST be masked before averaging. MOD17 Gpp fill is 65535 against a
# valid range of 0-65500; averaging it unmasked inflates a Western Ghats land
# cell by 21% and turns every sea cell into a spurious 6.5534 kgC/m2/yr maximum.
# Npp fill 32767 (valid -30000..32700); MOD13 VI fill -3000 (valid -2000..10000).
def _mask(img, band, lo, hi):
    b = img.select(band)
    return b.updateMask(b.gte(lo).And(b.lte(hi)))


mod17 = (ee.ImageCollection("MODIS/061/MOD17A3HGF").filterDate(start, end)
         .map(lambda i: _mask(i, "Gpp", 0, 65500)
              .addBands(_mask(i, "Npp", -30000, 32700)))
         .mean().multiply(0.0001).rename(["gpp", "npp"]))
mod13 = (ee.ImageCollection("MODIS/061/MOD13Q1").filterDate(start, end)
         .map(lambda i: _mask(i, "NDVI", -2000, 10000)
              .addBands(_mask(i, "EVI", -2000, 10000)))
         .mean().multiply(0.0001).rename(["ndvi", "evi"]))
era = ee.ImageCollection("ECMWF/ERA5_LAND/MONTHLY_AGGR").filterDate(start, end)
temp_c = era.select("temperature_2m").mean().subtract(273.15).rename("temp_c")
precip = (era.select("total_precipitation_sum").mean()
          .multiply(1000.0 * 12.0).rename("precip_mm_yr"))
wc = ee.Image("ESA/WorldCover/v200/2021").select("Map")

frac = (wc.remap(WC_NATURAL, [1] * len(WC_NATURAL), 0).rename("natural_frac")
        .addBands(wc.remap(WC_EXCLUDE, [1] * len(WC_EXCLUDE), 0).rename("excluded_frac"))
        .addBands(wc.remap(WC_WATER, [1] * len(WC_WATER), 0).rename("water_frac")))

cache = {}
if os.path.exists(CACHE):
    with open(CACHE, "r", encoding="utf-8") as f:
        cache = json.load(f)
print("cached cells: %d" % len(cache), flush=True)

PRODUCTS = [
    (mod17, ee.Reducer.mean(), 500, ["gpp", "npp"]),
    (mod13, ee.Reducer.mean(), 250, ["ndvi", "evi"]),
    (temp_c.addBands(precip), ee.Reducer.mean(), 11132, ["temp_c", "precip_mm_yr"]),
    (frac, ee.Reducer.mean(), 500, ["natural_frac", "excluded_frac", "water_frac"]),
    # setOutputs is required: for a SINGLE-band image reduceRegions names the
    # output property after the reducer ("mode"), not after the band, so without
    # this the wc_mode column comes back empty for every cell and the
    # cropland/urban/water restriction silently does nothing.
    (wc, ee.Reducer.mode().setOutputs(["wc_mode"]), 500, ["wc_mode"]),
]

todo = [f for f in feats if f["properties"]["cell_id"] not in cache]
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
                    print("  FAILED scale=%d keys=%s: %s" % (scale, keys, str(e)[:160]),
                          flush=True)
                else:
                    time.sleep(5 * (attempt + 1))
    cache.update(acc)
    tmp = CACHE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cache, f)
    os.replace(tmp, CACHE)
    print("  batch %d-%d done (%d cached) %.0fs"
          % (b, b + len(chunk), len(cache), time.time() - t0), flush=True)

cols = ["cell_id", "gpp", "npp", "ndvi", "evi", "temp_c", "precip_mm_yr",
        "wc_mode", "natural_frac", "excluded_frac", "water_frac"]
out = os.path.join(DATA, "gee_cells.csv")
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    n = 0
    for ft in feats:
        cid = ft["properties"]["cell_id"]
        if cid not in cache:
            continue
        row = {"cell_id": cid}
        row.update({k: cache[cid].get(k) for k in cols[1:]})
        w.writerow(row)
        n += 1
print("wrote %s: %d cells in %.0fs" % (out, n, time.time() - t0), flush=True)
