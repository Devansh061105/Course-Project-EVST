# -*- coding: utf-8 -*-
"""Plan Steps 5 + 6: merge the two halves, sanity-check, run Extension A.

Extension A is the naive-vs-corrected reveal:
  naive      GPP ~ raw observed richness, no controls, no land-cover mask
  corrected  GPP ~ rarefied richness + log(effort) + temp + precip,
             restricted to natural-land-cover cells
Both with HC3 heteroskedasticity-robust standard errors, because ecological
data of this kind rarely satisfies constant variance.
"""
import os
import sys

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))

sys.path.insert(0, HERE)
from gbif_lib import CASE_STUDIES

# WorldCover classes to drop as the dominant class of a cell.
# 40 cropland and 50 built-up per plan Step 4; 80 permanent water added because
# the Arabian Sea / Bay of Bengal cells are not undersampled land, they are sea.
DROP_MODE = {40: "cropland", 50: "built-up", 80: "water"}
MIN_RECORDS = 20
RAREFY_COL = "rarefied_250"

gbif = pd.read_csv(os.path.join(DATA, "gbif_cells.csv"))
gee = pd.read_csv(os.path.join(DATA, "gee_cells.csv"))
df = gbif.merge(gee, on="cell_id", how="inner", validate="one_to_one")
print("merged: %d cells (gbif %d, gee %d)" % (len(df), len(gbif), len(gee)))

# Earth Engine returns the categorical mode through pyramid resampling, so the
# values carry float noise (79.9999999999998 rather than 80.0) and 630 cells
# appear as 248 distinct "classes". Round to recover the WorldCover codes.
df["wc_mode"] = df.wc_mode.round()
# A null wc_mode means WorldCover has no coverage for the cell at all, i.e. open
# ocean. Those are not land with missing data; they are excluded outright.
df["is_land"] = df.wc_mode.notna()
print("land cells (WorldCover coverage): %d of %d" % (df.is_land.sum(), len(df)))

# ---------------------------------------------------------------- Step 5
print("\n=== Step 5: sanity check, one cell per case-study region ===")
for name, (a, b, c, d) in CASE_STUDIES.items():
    sub = df[(df.lat_c.between(a, b)) & (df.lon_c.between(c, d))]
    sub = sub[sub.is_land & (~sub.wc_mode.isin(DROP_MODE)) & sub.gpp.notna()]
    if sub.empty:
        print("  %-17s NO CELLS SURVIVE THE MASK" % name)
        continue
    r = sub.sort_values("total_records", ascending=False).iloc[0]
    print("  %-17s cell %s  GPP=%.3f  NDVI=%.2f  T=%.1fC  P=%.0fmm  "
          "wc_mode=%s  records=%d  obs_S=%d  rare250=%.1f"
          % (name, r.cell_id, r.gpp, r.ndvi, r.temp_c, r.precip_mm_yr,
             int(r.wc_mode), r.total_records, r.obs_richness,
             r[RAREFY_COL] if pd.notna(r[RAREFY_COL]) else float("nan")))

wg = df[(df.lat_c.between(*CASE_STUDIES["western_ghats"][:2]))
        & (df.lon_c.between(*CASE_STUDIES["western_ghats"][2:]))
        & df.is_land & (~df.wc_mode.isin(DROP_MODE)) & df.gpp.notna()]
# The plan's check compared the Western Ghats with the Deccan, but no Deccan cell
# survives the natural-cover mask (all cropland-dominant), so the comparison is
# made against the replacement dry contrast, the Thar Desert (docs/DECISIONS.md).
tr = df[df.lat_c.between(25.0, 30.0) & df.lon_c.between(69.0, 74.0)
        & df.is_land & (~df.wc_mode.isin(DROP_MODE)) & df.gpp.notna()]
print("\n  CHECK Western Ghats GPP (%.3f) > Thar Desert GPP (%.3f)? %s"
      % (wg.gpp.mean(), tr.gpp.mean(),
         "PASS" if wg.gpp.mean() > tr.gpp.mean() else "FAIL - investigate upstream"))

# ---------------------------------------------------------------- Step 6
print("\n=== Step 6 / Extension A ===")
df["log_effort"] = np.log10(df.total_records.clip(lower=1))

naive_df = df[df.gpp.notna() & df.obs_richness.notna()].copy()

corr_df = df[df.gpp.notna()
             & df.is_land
             & (~df.wc_mode.isin(DROP_MODE))
             & (df.total_records >= MIN_RECORDS)
             & df[RAREFY_COL].notna()
             & df.temp_c.notna() & df.precip_mm_yr.notna()].copy()

print("naive     n = %d (all cells with GPP, no mask, no effort control)" % len(naive_df))
print("corrected n = %d (natural cover, >=%d records, rarefiable at 250)"
      % (len(corr_df), MIN_RECORDS))
dropped = len(naive_df) - len(corr_df)
by_mode = df[df.is_land & df.wc_mode.isin(DROP_MODE)].wc_mode.value_counts().to_dict()
print("  excluded by dominant class: %s"
      % ", ".join("%s=%d" % (DROP_MODE[int(k)], v) for k, v in sorted(by_mode.items())))


def fit(d, y, xs, label):
    X = sm.add_constant(d[xs].astype(float))
    m = sm.OLS(d[y].astype(float), X).fit(cov_type="HC3")
    print("\n--- %s ---" % label)
    print("  n=%d  R2=%.4f  adjR2=%.4f  AIC=%.1f" % (m.nobs, m.rsquared,
                                                     m.rsquared_adj, m.aic))
    print("  %-16s %12s %10s %9s %9s" % ("term", "coef", "se(HC3)", "t", "p"))
    for t in m.params.index:
        print("  %-16s %12.5g %10.4g %9.2f %9.4f"
              % (t, m.params[t], m.bse[t], m.tvalues[t], m.pvalues[t]))
    return m


naive = fit(naive_df, "gpp", ["obs_richness"], "NAIVE: GPP ~ raw richness")
corrected = fit(corr_df, "gpp",
                [RAREFY_COL, "log_effort", "temp_c", "precip_mm_yr"],
                "CORRECTED: GPP ~ rarefied richness + log10(effort) + climate")

# VIF: the corrected model's richness coefficient is only interpretable if
# effort and climate are not collinear with it (plan Step 8).
print("\n--- VIF (corrected model) ---")
Xv = sm.add_constant(corr_df[[RAREFY_COL, "log_effort", "temp_c",
                              "precip_mm_yr"]].astype(float)).values
for i, t in enumerate(["const", RAREFY_COL, "log_effort", "temp_c", "precip_mm_yr"]):
    if t == "const":
        continue
    print("  %-16s %.2f" % (t, variance_inflation_factor(Xv, i)))

print("\n--- THE REVEAL ---")
nb = naive.params["obs_richness"]
cb = corrected.params[RAREFY_COL]
print("  naive     richness coef = %+.6g  (p=%.4g)" % (nb, naive.pvalues["obs_richness"]))
print("  corrected richness coef = %+.6g  (p=%.4g)" % (cb, corrected.pvalues[RAREFY_COL]))
print("  effort    coef          = %+.6g  (p=%.4g)"
      % (corrected.params["log_effort"], corrected.pvalues["log_effort"]))
print("  sign flip: %s" % ("YES" if np.sign(nb) != np.sign(cb) else "no"))

df.to_csv(os.path.join(DATA, "merged_cells.csv"), index=False)
corr_df.to_csv(os.path.join(DATA, "model_cells.csv"), index=False)
print("\nwrote data/merged_cells.csv (%d rows), data/model_cells.csv (%d rows)"
      % (len(df), len(corr_df)))
