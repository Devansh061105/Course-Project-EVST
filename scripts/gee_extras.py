# -*- coding: utf-8 -*-
"""Extra Earth Engine layers added 2026-11-16 (Extensions E and F, map overlays).

  gpp_annual   MODIS MOD17A3HGF GPP for each year 2001-2023, mean per 1-degree
               cell (26 x 34). Fill values (> 65500) are masked at the native
               500 m BEFORE aggregating, because the asset's own pyramid averages
               them in (see docs/VERIFICATION.md section 7).
  protected    Fraction of each 0.05-degree pixel inside a protected area, from
               WDPA polygons (WCMC/WDPA/current/polygons): status Designated,
               Inscribed or Established; UNESCO-MAB biosphere reserves excluded
               (the usual WDPA convention, since they include unprotected buffer
               zones). Point-only records are not included.
  border       Country outlines at 0.05 degrees (USDOS/LSIB_SIMPLE/2017), 1 = line.
  eco_id       RESOLVE Ecoregions 2017 ECO_ID at 0.05 degrees (0 = none).
Writes data/gee_extras.npz and data/eco_names.json (ECO_ID -> name, biome).

Needs an authenticated Earth Engine account: set EE_PROJECT.
"""
import json
import os
import sys

import ee
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gbif_lib import REGION

EE_PROJECT = os.environ.get("EE_PROJECT", "")
if not EE_PROJECT:
    sys.exit("set EE_PROJECT")
ee.Initialize(project=EE_PROJECT)

DATA = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data"))
L0, L1 = REGION["lon_min"], REGION["lon_max"]
B0, B1 = REGION["lat_min"], REGION["lat_max"]
GEOM = ee.Geometry.Rectangle([L0, B0, L1, B1], None, False)
YEARS = list(range(2001, 2024))


def grid(res):
    return {"dimensions": {"width": int(round((L1 - L0) / res)),
                           "height": int(round((B1 - B0) / res))},
            "affineTransform": {"scaleX": res, "shearX": 0, "translateX": L0,
                                "shearY": 0, "scaleY": -res, "translateY": B1},
            "crsCode": "EPSG:4326"}


def pixels(img, res):
    a = ee.data.computePixels({"expression": img.unmask(-9999).toFloat().rename("v"),
                               "fileFormat": "NUMPY_NDARRAY", "grid": grid(res)})
    return np.asarray(a["v"], dtype=np.float32)


path = os.path.join(DATA, "gee_extras.npz")
out = dict(np.load(path)) if os.path.exists(path) else {}     # layers already pulled are kept
ONE_DEG = [1, 0, L0, 0, -1, B1]

# ---- annual GPP per 1-degree cell -----------------------------------------
if "gpp_annual" not in out:
    ic = ee.ImageCollection("MODIS/061/MOD17A3HGF").select("Gpp")
    proj = ic.first().projection()
    annual = []
    for y in YEARS:
        img = ee.Image(ic.filter(ee.Filter.calendarRange(y, y, "year")).first())
        img = (img.updateMask(img.lte(65500)).multiply(0.0001).setDefaultProjection(proj)
               .reduceResolution(ee.Reducer.mean(), maxPixels=65536)
               .reproject(crs="EPSG:4326", crsTransform=ONE_DEG))
        a = pixels(img, 1.0)
        annual.append(a)
        ok = a[a > -9000]
        print("GPP %d: %d cells with data, mean %.3f" % (y, ok.size, ok.mean()), flush=True)
    out["gpp_annual"] = np.stack(annual)
    out["years"] = np.array(YEARS)

# ---- annual precipitation and temperature per 1-degree cell (ERA5-Land) ----
if "precip_annual" not in out:
    era = ee.ImageCollection("ECMWF/ERA5_LAND/MONTHLY_AGGR")
    eproj = era.first().projection()
    pa, ta = [], []
    for y in YEARS:
        yr = era.filter(ee.Filter.calendarRange(y, y, "year"))
        pr = (yr.select("total_precipitation_sum").sum().multiply(1000)
              .setDefaultProjection(eproj).reduceResolution(ee.Reducer.mean(), maxPixels=1024)
              .reproject(crs="EPSG:4326", crsTransform=ONE_DEG))
        te = (yr.select("temperature_2m").mean().subtract(273.15)
              .setDefaultProjection(eproj).reduceResolution(ee.Reducer.mean(), maxPixels=1024)
              .reproject(crs="EPSG:4326", crsTransform=ONE_DEG))
        pa.append(pixels(pr, 1.0)); ta.append(pixels(te, 1.0))
        print("climate %d: precip mean %.0f mm, temp mean %.1f C"
              % (y, pa[-1][pa[-1] > -9000].mean(), ta[-1][ta[-1] > -9000].mean()), flush=True)
    out["precip_annual"] = np.stack(pa)
    out["temp_annual"] = np.stack(ta)

# ---- protected fraction at 0.05 degrees -----------------------------------
# Two definitions. "protected" is every designated WDPA polygon; in India that
# includes about 180,000 Reserve Forest and Protected Forest polygons (forest-law
# categories, not wildlife reserves), which is why it reads 18% of Indian land.
# "protected_strict" keeps IUCN management categories Ia-IV only (strict reserves,
# national parks, wildlife sanctuaries): the usual definition in the literature.
wdpa = (ee.FeatureCollection("WCMC/WDPA/current/polygons").filterBounds(GEOM)
        .filter(ee.Filter.inList("STATUS", ["Designated", "Inscribed", "Established"]))
        .filter(ee.Filter.neq("DESIG_ENG", "UNESCO-MAB Biosphere Reserve")))
strict = wdpa.filter(ee.Filter.inList("IUCN_CAT", ["Ia", "Ib", "II", "III", "IV"]))
for key, fc in (("protected", wdpa), ("protected_strict", strict)):
    if key in out:
        continue
    print("WDPA polygons, %s: %d" % (key, fc.size().getInfo()), flush=True)
    prot = (ee.Image.constant(0).byte().paint(fc, 1)
            .reproject(crs="EPSG:4326", scale=1000)
            .reduceResolution(ee.Reducer.mean(), maxPixels=256)
            .reproject(crs="EPSG:4326", crsTransform=[0.05, 0, L0, 0, -0.05, B1]))
    out[key] = pixels(prot, 0.05)
    print("%s: mean fraction over the whole box %.4f" % (key, out[key].clip(0).mean()),
          flush=True)

# ---- country outlines and ecoregion ids at 0.05 degrees -------------------
if "border" not in out:
    lsib = ee.FeatureCollection("USDOS/LSIB_SIMPLE/2017").filterBounds(GEOM)
    out["border"] = pixels(ee.Image().byte().paint(lsib, 1, 1), 0.05)
if "eco_id" not in out:
    eco = ee.FeatureCollection("RESOLVE/ECOREGIONS/2017").filterBounds(GEOM)
    out["eco_id"] = pixels(eco.reduceToImage(["ECO_ID"], ee.Reducer.first()), 0.05)
    ids = eco.aggregate_array("ECO_ID").getInfo()
    names = eco.aggregate_array("ECO_NAME").getInfo()
    biomes = eco.aggregate_array("BIOME_NAME").getInfo()
    with open(os.path.join(DATA, "eco_names.json"), "w", encoding="utf-8") as f:
        json.dump({str(int(i)): [n, b] for i, n, b in zip(ids, names, biomes)}, f,
                  ensure_ascii=False)
    print("border pixels %d; ecoregions %d" % ((out["border"] > 0).sum(), len(set(ids))),
          flush=True)

np.savez_compressed(path, **out)
print("wrote %s (%.0f KB)" % (path, os.path.getsize(path) / 1024))
