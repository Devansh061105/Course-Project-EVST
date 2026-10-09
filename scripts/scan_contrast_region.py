# -*- coding: utf-8 -*-
"""Find a replacement dry-contrast region for Extension C.

The Deccan Plateau failed: all 25 land cells are cropland-dominant (mean 77%
converted), so it cannot survive the natural-land-cover restriction. We need a
region that is (a) dry, to contrast with the wet Western Ghats, (b) still
largely natural, and (c) adequately surveyed.

Rather than picking candidate boxes by hand, this scans every 5x5-degree window
over the grid at 1-degree steps and scores them on the cells that actually
survive the analysis mask.
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
sys.path.insert(0, HERE)
from gbif_lib import CASE_STUDIES

DROP_MODE = {40, 50, 80}
MIN_RECORDS = 20
WIN = 5.0
MIN_CELLS = 8
MIN_NATURAL = 0.55

df = pd.read_csv(os.path.join(DATA, "merged_cells.csv"))
df["wc_mode"] = df.wc_mode.round()

elig = df[df.gpp.notna() & df.wc_mode.notna() & (~df.wc_mode.isin(DROP_MODE))
          & (df.total_records >= MIN_RECORDS) & df.rarefied_250.notna()
          & df.temp_c.notna() & df.precip_mm_yr.notna()].copy()
print("eligible cells across study region: %d" % len(elig))

wg = elig[(elig.lat_c.between(*CASE_STUDIES["western_ghats"][:2]))
          & (elig.lon_c.between(*CASE_STUDIES["western_ghats"][2:]))]
print("Western Ghats reference: n=%d  precip=%.0fmm  natural=%.2f  GPP=%.2f"
      % (len(wg), wg.precip_mm_yr.mean(), wg.natural_frac.mean(), wg.gpp.mean()))

rows = []
for lat0 in np.arange(df.lat_c.min() - 0.5, df.lat_c.max() - WIN + 0.5, 1.0):
    for lon0 in np.arange(df.lon_c.min() - 0.5, df.lon_c.max() - WIN + 0.5, 1.0):
        sub = elig[(elig.lat_c.between(lat0, lat0 + WIN))
                   & (elig.lon_c.between(lon0, lon0 + WIN))]
        if len(sub) < MIN_CELLS:
            continue
        if sub.natural_frac.mean() < MIN_NATURAL:
            continue
        rows.append({
            "lat_min": lat0, "lat_max": lat0 + WIN,
            "lon_min": lon0, "lon_max": lon0 + WIN,
            "n": len(sub),
            "precip": sub.precip_mm_yr.mean(),
            "natural": sub.natural_frac.mean(),
            "gpp": sub.gpp.mean(),
            "temp": sub.temp_c.mean(),
            "med_records": sub.total_records.median(),
            "rare250": sub.rarefied_250.mean(),
        })

cand = pd.DataFrame(rows).sort_values("precip")
print("\nwindows passing filters (n>=%d cells, natural>=%.2f): %d"
      % (MIN_CELLS, MIN_NATURAL, len(cand)))

# Greedy non-overlapping pick, driest first.
chosen = []
for _, r in cand.iterrows():
    if any(not (r.lon_max <= c.lon_min or r.lon_min >= c.lon_max
                or r.lat_max <= c.lat_min or r.lat_min >= c.lat_max)
           for c in chosen):
        continue
    chosen.append(r)
    if len(chosen) >= 6:
        break

print("\n%-28s %4s %8s %8s %6s %6s %10s" % (
    "window (lat / lon)", "n", "precip", "natural", "GPP", "temp", "med_recs"))
print("-" * 80)
for c in chosen:
    print("%-28s %4d %8.0f %8.2f %6.2f %6.1f %10.0f" % (
        "%.0f-%.0fN  %.0f-%.0fE" % (c.lat_min, c.lat_max, c.lon_min, c.lon_max),
        c.n, c.precip, c.natural, c.gpp, c.temp, c.med_records))

print("\nFor reference, the three planned case studies:")
for name, (a, b, cc, d) in CASE_STUDIES.items():
    s = elig[(elig.lat_c.between(a, b)) & (elig.lon_c.between(cc, d))]
    if s.empty:
        print("  %-17s NO ELIGIBLE CELLS" % name)
    else:
        print("  %-17s n=%-3d precip=%-6.0f natural=%.2f GPP=%.2f"
              % (name, len(s), s.precip_mm_yr.mean(), s.natural_frac.mean(),
                 s.gpp.mean()))
