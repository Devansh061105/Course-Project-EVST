# -*- coding: utf-8 -*-
"""Fine grids for the 3D terrain map (visual layer only; no analysis uses them).

One Earth Engine request per band over the study region at 0.05 degrees
(680 x 520 pixels, about 5.5 km):
  elev   ETOPO1 bedrock elevation, m (NOAA/NGDC/ETOPO1; sea floor negative)
  lc     ESA WorldCover v200 class, pyramid mode (0 = no coverage, i.e. open sea)
  ndvi   MODIS MOD13Q1 NDVI, 2019-2023 mean
  gpp    MODIS MOD17A3HGF GPP, 2019-2023 mean, kg C m-2 yr-1
Missing values are -9999. Writes data/terrain_grid_0p05.npz (the cache: the map
builder reads it, so Earth Engine is needed only once).

Needs an authenticated Earth Engine account: set EE_PROJECT to your own Cloud
project, as for the other gee_*.py scripts.
"""
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

RES = 0.05
W = int(round((REGION["lon_max"] - REGION["lon_min"]) / RES))
H = int(round((REGION["lat_max"] - REGION["lat_min"]) / RES))
GRID = {"dimensions": {"width": W, "height": H},
        "affineTransform": {"scaleX": RES, "shearX": 0, "translateX": REGION["lon_min"],
                            "shearY": 0, "scaleY": -RES, "translateY": REGION["lat_max"]},
        "crsCode": "EPSG:4326"}
T0, T1 = "2019-01-01", "2024-01-01"

gpp_ic = ee.ImageCollection("MODIS/061/MOD17A3HGF").filterDate(T0, T1).select("Gpp")
bands = {
    "elev": ee.Image("NOAA/NGDC/ETOPO1").select("bedrock"),
    "lc": ee.ImageCollection("ESA/WorldCover/v200").first().select("Map"),
    "ndvi": ee.ImageCollection("MODIS/061/MOD13Q1").filterDate(T0, T1).select("NDVI")
              .mean().multiply(0.0001),
    # MOD17 fill values (> 65500) are not masked in the asset, and the image
    # pyramid averages them into coarser levels. Mask at native 500 m first, then
    # aggregate explicitly, otherwise coastal and barren pixels read as GPP ~6.
    "gpp": gpp_ic.map(lambda i: i.updateMask(i.lte(65500))).mean().multiply(0.0001)
             .setDefaultProjection(gpp_ic.first().projection())
             .reduceResolution(ee.Reducer.mean(), maxPixels=512)
             .reproject(crs="EPSG:4326", crsTransform=[RES, 0, REGION["lon_min"],
                                                       0, -RES, REGION["lat_max"]]),
}
out = {}
for name, img in bands.items():
    arr = ee.data.computePixels({
        "expression": img.unmask(-9999).toFloat().rename("v"),
        "fileFormat": "NUMPY_NDARRAY", "grid": GRID})
    a = np.asarray(arr["v"], dtype=np.float32)
    out[name] = a
    ok = a[a > -9000]
    print("%-5s shape %s  valid %d of %d  min %.3f  median %.3f  max %.3f"
          % (name, a.shape, ok.size, a.size, ok.min(), np.median(ok), ok.max()), flush=True)

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data",
                    "terrain_grid_0p05.npz")
np.savez_compressed(path, res=RES, lon_min=REGION["lon_min"], lat_max=REGION["lat_max"], **out)
print("wrote %s (%.0f KB)" % (os.path.normpath(path), os.path.getsize(path) / 1024))
