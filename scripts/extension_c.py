# -*- coding: utf-8 -*-
"""Extension C (plan Step 9): case-study deep dive.

Three contrasting landscapes. The Deccan Plateau was dropped because all 25 of
its land cells are cropland-dominant (see docs/DECISIONS.md); Thar / western
Rajasthan replaces it as the dry contrast.

For each region: the land-cover and climate profile, the richness and
productivity figures, how the corrected model performs there (residuals), and
the naive-vs-corrected comparison at regional level - which is where Extension A
becomes legible, because the regions REORDER when effort is corrected.
"""
import os
import sys
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))

REGIONS = {
    "Western Ghats":      (8.0, 16.0, 74.0, 77.0),
    "Thar Desert": (25.0, 30.0, 69.0, 74.0),
    "Eastern Himalaya": (26.0, 29.0, 88.0, 97.0),
}
WC_NAMES = {10: "tree cover", 20: "shrubland", 30: "grassland", 40: "cropland",
            50: "built-up", 60: "bare/sparse", 70: "snow/ice", 80: "water",
            90: "wetland", 95: "mangrove", 100: "moss/lichen"}
DROP_MODE = {40, 50, 80}
CTRL = ["log_effort", "temp_c", "precip_mm_yr"]

df = pd.read_csv(os.path.join(DATA, "merged_cells.csv"))
df["wc_mode"] = df.wc_mode.round()
model = pd.read_csv(os.path.join(DATA, "model_cells.csv"))

# Corrected model, refit here so residuals are available per cell.
X = sm.add_constant(model[["rarefied_250"] + CTRL].astype(float))
fit = sm.OLS(model.gpp.astype(float), X).fit(cov_type="HC3")
model = model.assign(resid=fit.resid, fitted=fit.fittedvalues)


def pick(d, box):
    a, b, c, e = box
    return d[(d.lat_c.between(a, b)) & (d.lon_c.between(c, e))]


print("=" * 78)
print("EXTENSION C — three case-study landscapes")
print("=" * 78)

for name, box in REGIONS.items():
    land = pick(df[df.is_land], box)
    elig = pick(model, box)
    print("\n--- %s  (%.0f-%.0fN, %.0f-%.0fE) ---"
          % (name, box[0], box[1], box[2], box[3]))
    if land.empty:
        print("   no land cells")
        continue

    mix = land.wc_mode.value_counts(normalize=True)
    mixs = ", ".join("%s %.0f%%" % (WC_NAMES.get(int(k), k), 100 * v)
                     for k, v in mix.head(4).items())
    print("   land cells %d, eligible after mask %d" % (len(land), len(elig)))
    print("   dominant land cover: %s" % mixs)
    print("   mean natural frac %.2f | cropland+built %.2f | water %.2f"
          % (land.natural_frac.mean(), land.excluded_frac.mean(),
             land.water_frac.mean()))
    if elig.empty:
        print("   NO ELIGIBLE CELLS — cannot model this region")
        continue
    print("   climate: %.1f degC, %.0f mm/yr" % (elig.temp_c.mean(),
                                                 elig.precip_mm_yr.mean()))
    print("   productivity: GPP %.2f kgC/m2/yr (NDVI %.2f)"
          % (elig.gpp.mean(), elig.ndvi.mean()))
    print("   survey effort: median %,.0f records/cell"
          .replace(",", "") % elig.total_records.median())
    print("   richness: raw observed %.0f | rarefied@250 %.1f"
          % (elig.obs_richness.mean(), elig.rarefied_250.mean()))
    print("   corrected-model residual: mean %+.3f (model %s here)"
          % (elig.resid.mean(),
             "under-predicts" if elig.resid.mean() > 0 else "over-predicts"))

# ---------------------------------------------------------------- the reveal
print("\n" + "=" * 78)
print("REGIONAL REORDERING — Extension A made legible")
print("=" * 78)
rows = []
for name, box in REGIONS.items():
    e = pick(model, box)
    if e.empty:
        continue
    rows.append({"region": name, "n": len(e),
                 "records": e.total_records.median(),
                 "raw_S": e.obs_richness.mean(),
                 "rare_S": e.rarefied_250.mean(),
                 "gpp": e.gpp.mean()})
r = pd.DataFrame(rows)
r["rank_raw"] = r.raw_S.rank(ascending=False).astype(int)
r["rank_rare"] = r.rare_S.rank(ascending=False).astype(int)
r["rank_gpp"] = r.gpp.rank(ascending=False).astype(int)
print("\n%-20s %4s %12s %8s %5s %8s %5s %7s %5s" % (
    "region", "n", "med records", "raw S", "rank", "rare S", "rank", "GPP", "rank"))
print("-" * 82)
for _, x in r.iterrows():
    print("%-20s %4d %12.0f %8.0f %5d %8.1f %5d %7.2f %5d" % (
        x.region, x.n, x.records, x.raw_S, x.rank_raw, x.rare_S, x.rank_rare,
        x.gpp, x.rank_gpp))

print("\neffort spread: %.0fx between most- and least-surveyed region"
      % (r.records.max() / r.records.min()))
print("raw-richness spread:      %.2fx" % (r.raw_S.max() / r.raw_S.min()))
print("rarefied-richness spread: %.2fx" % (r.rare_S.max() / r.rare_S.min()))
print("GPP spread:               %.2fx" % (r.gpp.max() / r.gpp.min()))
if (r.rank_raw != r.rank_rare).any():
    print("\n-> RANKING CHANGES after effort correction.")
else:
    print("\n-> ranking unchanged by effort correction; magnitudes compress.")
