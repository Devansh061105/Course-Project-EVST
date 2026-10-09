# -*- coding: utf-8 -*-
"""Label each 1-degree cell centroid with its country (US State Dept LSIB 2017).

Written during the 2026-10-06 project review to check geographic descriptions
in the docs (which countries the study region and each case-study box cover).
Writes data/countries_1p0.csv.
"""
import csv
import json
import os
import sys

import ee

EE_PROJECT = os.environ.get("EE_PROJECT", "")
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
if not EE_PROJECT:
    sys.exit("set EE_PROJECT")
ee.Initialize(project=EE_PROJECT)

with open(os.path.join(DATA, "grid_1deg.geojson"), "r", encoding="utf-8") as f:
    feats = json.load(f)["features"]
pts = ee.FeatureCollection([
    ee.Feature(ee.Geometry.Point([x["properties"]["lon_c"], x["properties"]["lat_c"]]),
               {"cell_id": x["properties"]["cell_id"]}) for x in feats])
lsib = ee.FeatureCollection("USDOS/LSIB_SIMPLE/2017")
joined = ee.Join.saveFirst("c").apply(
    primary=pts, secondary=lsib,
    condition=ee.Filter.intersects(leftField=".geo", rightField=".geo"))
flat = joined.map(lambda f: ee.Feature(None, {
    "cell_id": f.get("cell_id"), "country": ee.Feature(f.get("c")).get("country_na")}))
rows = [x["properties"] for x in flat.getInfo()["features"]]
with open(os.path.join(DATA, "countries_1p0.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["cell_id", "country"])
    w.writeheader()
    for r in rows:
        w.writerow({"cell_id": r.get("cell_id"), "country": r.get("country")})
print("centroids inside a country polygon: %d of %d" % (len(rows), len(feats)))
