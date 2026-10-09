# -*- coding: utf-8 -*-
"""DEPRECATED - do not run. Use gee_extract_chunked.py.

This first version has three known bugs fixed only in the chunked script:
WorldCover class 80 (water) counted as natural; MODIS fill values averaged as
data; single-band mode output not renamed (wc_mode came back all null). It also
states that a 1-degree cell holds ~1 ERA5-Land pixel; the true figure is ~94.

Plan Step 4: extract environmental variables per grid cell via Earth Engine.

NOT YET RUN - needs an approved Google Earth Engine account (see docs/TODO.md).
Written in advance so extraction can start the day approval lands.

Setup, once:
    pip install earthengine-api
    earthengine authenticate
    # then set EE_PROJECT below to your Cloud project id

Pulls, for every cell, in ONE server-side reduceRegions per product (not a
client-side loop over cells):
    MOD17A3HGF  Gpp, Npp          500 m    annual
    MOD13Q1     NDVI, EVI         250 m    16-day composites
    ERA5-Land   temp, precip      ~11 km   monthly aggregates
    WorldCover  dominant class    10 m     + natural-cover fraction

Writes data/gee_cells.csv.
"""
import os
import sys

import sys as _sys
_sys.exit('gee_extract.py is deprecated: use gee_extract_chunked.py')

import ee

EE_PROJECT = os.environ.get("EE_PROJECT", "")   # <-- set this
YEARS = (2019, 2023)                            # plan: 3-5 yr mean, not one year
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))

# WorldCover v200 class codes. Cropland (40) and built-up (50) are excluded
# entirely per plan Step 4, so managed output is never compared with natural.
WC_EXCLUDE = [40, 50]
WC_NATURAL = [10, 20, 30, 60, 70, 80, 90, 95, 100]

if not EE_PROJECT:
    sys.exit("Set EE_PROJECT (your Earth Engine Cloud project id) first.")
ee.Initialize(project=EE_PROJECT)

with open(os.path.join(DATA, "grid_1deg.geojson"), "r", encoding="utf-8") as f:
    grid_gj = __import__("json").load(f)
cells = ee.FeatureCollection(grid_gj)
print("grid loaded: %d cells" % len(grid_gj["features"]))

start, end = "%d-01-01" % YEARS[0], "%d-12-31" % YEARS[1]

# --- productivity: annual GPP/NPP, mean over the year range -----------------
# MOD17A3HGF scale factor is 0.0001 kg C m-2 for both Gpp and Npp.
mod17 = (ee.ImageCollection("MODIS/061/MOD17A3HGF")
         .filterDate(start, end).select(["Gpp", "Npp"]).mean()
         .multiply(0.0001).rename(["gpp", "npp"]))

# --- vegetation indices: 16-day composites, mean over range -----------------
mod13 = (ee.ImageCollection("MODIS/061/MOD13Q1")
         .filterDate(start, end).select(["NDVI", "EVI"]).mean()
         .multiply(0.0001).rename(["ndvi", "evi"]))

# --- climate: ERA5-Land monthly, K -> degC and m -> mm/yr ------------------
era = ee.ImageCollection("ECMWF/ERA5_LAND/MONTHLY_AGGR").filterDate(start, end)
temp_c = era.select("temperature_2m").mean().subtract(273.15).rename("temp_c")
precip_mm = (era.select("total_precipitation_sum").mean()
             .multiply(1000.0 * 12.0).rename("precip_mm_yr"))

# --- land cover: dominant class + natural fraction -------------------------
wc = ee.Image("ESA/WorldCover/v200/2021").select("Map")
natural = wc.remap(WC_NATURAL, [1] * len(WC_NATURAL), 0).rename("natural_frac")
excluded = wc.remap(WC_EXCLUDE, [1] * len(WC_EXCLUDE), 0).rename("excluded_frac")


def reduce_to(img, reducer, scale, tag):
    """One server-side reduceRegions call for the whole FeatureCollection."""
    fc = img.reduceRegions(
        collection=cells, reducer=reducer, scale=scale,
        tileScale=4,                      # generous: avoids compute timeouts
    )
    print("  queued %s at %dm" % (tag, scale))
    return fc


def to_dict(fc, keys):
    """Pull a FeatureCollection down to {cell_id: {key: value}}."""
    out = {}
    for feat in fc.getInfo()["features"]:
        p = feat["properties"]
        out[p["cell_id"]] = {k: p.get(k) for k in keys}
    return out


print("extracting (each product is one server-side reduction)...")
# Native resolutions per plan Step 4: do not upsample a coarse product.
gpp_d = to_dict(reduce_to(mod17, ee.Reducer.mean(), 500, "MOD17 GPP/NPP"),
                ["gpp", "npp"])
veg_d = to_dict(reduce_to(mod13, ee.Reducer.mean(), 250, "MOD13 NDVI/EVI"),
                ["ndvi", "evi"])
clim_d = to_dict(reduce_to(temp_c.addBands(precip_mm), ee.Reducer.mean(), 11132,
                           "ERA5-Land"), ["temp_c", "precip_mm_yr"])
lc_d = to_dict(reduce_to(natural.addBands(excluded), ee.Reducer.mean(), 100,
                         "WorldCover fractions"), ["natural_frac", "excluded_frac"])
mode_d = to_dict(reduce_to(wc.rename("wc_mode"), ee.Reducer.mode(), 100,
                           "WorldCover mode"), ["wc_mode"])

import csv
cols = ["cell_id", "gpp", "npp", "ndvi", "evi", "temp_c", "precip_mm_yr",
        "wc_mode", "natural_frac", "excluded_frac"]
out = os.path.join(DATA, "gee_cells.csv")
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    for feat in grid_gj["features"]:
        cid = feat["properties"]["cell_id"]
        row = {"cell_id": cid}
        for d in (gpp_d, veg_d, clim_d, lc_d, mode_d):
            row.update(d.get(cid, {}))
        w.writerow(row)
print("wrote %s" % out)
print("NOTE: a 1-deg cell holds ~50k GPP pixels but only ~1 ERA5-Land pixel. "
      "Document this resolution mismatch in the methodology (plan Step 4).")
