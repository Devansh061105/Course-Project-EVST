# -*- coding: utf-8 -*-
"""Assign each 1-degree cell its RESOLVE ecoregion, biome and realm.

Plan Step 8 asks for cluster-robust standard errors "grouped by biogeographic
sub-region". Until now that was approximated with arbitrary 4-degree blocks.
This replaces the approximation with the RESOLVE Ecoregions 2017 polygons
(Dinerstein et al. 2017), via one server-side spatial join of cell centroids.

Writes data/ecoregions_1p0.csv.
"""
import csv
import json
import os
import sys

import ee

EE_PROJECT = os.environ.get("EE_PROJECT", "")
# Optional cell size in degrees (default 1.0, which reads the existing 1-degree
# grid file and writes ecoregions_1p0.csv exactly as before).
CELL = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
TAG = ("%.1f" % CELL).replace(".", "p")
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))

if not EE_PROJECT:
    sys.exit("set EE_PROJECT")
ee.Initialize(project=EE_PROJECT)

if CELL == 1.0:
    with open(os.path.join(DATA, "grid_1deg.geojson"), "r", encoding="utf-8") as f:
        feats = json.load(f)["features"]
else:
    sys.path.insert(0, HERE)
    from gbif_lib import build_grid, grid_geojson
    feats = grid_geojson(build_grid(CELL))["features"]
print("cell size %.1f deg, %d cells" % (CELL, len(feats)), flush=True)

pts = ee.FeatureCollection([
    ee.Feature(ee.Geometry.Point([f["properties"]["lon_c"], f["properties"]["lat_c"]]),
               {"cell_id": f["properties"]["cell_id"]})
    for f in feats])

eco = ee.FeatureCollection("RESOLVE/ECOREGIONS/2017")
joined = ee.Join.saveFirst("eco").apply(
    primary=pts, secondary=eco,
    condition=ee.Filter.intersects(leftField=".geo", rightField=".geo"))


def flat(f):
    e = ee.Feature(f.get("eco"))
    return ee.Feature(None, {"cell_id": f.get("cell_id"),
                             "eco_name": e.get("ECO_NAME"),
                             "eco_id": e.get("ECO_ID"),
                             "biome": e.get("BIOME_NAME"),
                             "realm": e.get("REALM")})


rows = []
BATCH = 300
lst = joined.toList(joined.size())
n = joined.size().getInfo()
print("cell centroids inside an ecoregion: %d of %d" % (n, len(feats)), flush=True)
for b in range(0, n, BATCH):
    chunk = ee.FeatureCollection(lst.slice(b, min(b + BATCH, n))).map(flat).getInfo()
    rows += [ft["properties"] for ft in chunk["features"]]
    print("  fetched %d" % len(rows), flush=True)

cols = ["cell_id", "eco_id", "eco_name", "biome", "realm"]
with open(os.path.join(DATA, "ecoregions_%s.csv" % TAG), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k) for k in cols})
if sum(1 for r in rows if r.get("eco_name")) == 0:
    sys.exit("ABORT: no ecoregion names returned - check property names")
print("wrote data/ecoregions_%s.csv (%d rows)" % (TAG, len(rows)))
