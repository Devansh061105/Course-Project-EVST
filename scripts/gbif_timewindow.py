# -*- coding: utf-8 -*-
"""Time-window robustness: match the GBIF record window to the environmental one.

The main analysis uses bird records from 2000-2024 but GPP / climate means from
2019-2023. If richness has shifted (or survey effort has moved geographically,
which eBird growth makes likely), the mismatch could bias the association. This
re-pulls only the cells that pass the land-cover mask, restricted to 2019-2023
records, and refits the headline models.
"""
import json
import os
import sys
import time
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm
from spreg import ML_Error

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
sys.path.insert(0, HERE)
from gbif_lib import TAXA, build_grid, gbif_cell, hurlbert_rarefy, load_cache, save_cache
from weights_sensitivity import queen_from_grid
from robustness_suite import block_cv_gain

YEARS = "2019,2023"
CACHE = os.path.join(DATA, "gbif_cache_2019_2023.json")
CTRL = ["log_effort", "temp_c", "precip_mm_yr"]


def z(s):
    return (s - s.mean()) / s.std()


m = pd.read_csv(os.path.join(DATA, "merged_cells.csv"))
m["wc_mode"] = m.wc_mode.round()
cand = m[m.wc_mode.notna() & ~m.wc_mode.isin([40, 50, 80]) & m.gpp.notna()
         & m.temp_c.notna() & m.precip_mm_yr.notna()].copy()
grid = {c["cell_id"]: c for c in build_grid(1.0)}
cache = load_cache(CACHE)
todo = [cid for cid in cand.cell_id if cid not in cache]
print("candidate cells (pass land-cover mask): %d, to pull: %d" % (len(cand), len(todo)),
      flush=True)
t0 = time.time()
for k, cid in enumerate(todo, 1):
    g = grid[cid]
    total, ab = gbif_cell(g["lat_min"], g["lat_max"], g["lon_min"], g["lon_max"],
                          TAXA["birds"], year=YEARS)
    cache[cid] = {"total": total, "ab": ab}
    if k % 25 == 0:
        save_cache(CACHE, cache)
        print("  %d/%d  %.0fs" % (k, len(todo), time.time() - t0), flush=True)
    time.sleep(0.3)
save_cache(CACHE, cache)

cand["total_19_23"] = [cache[c]["total"] for c in cand.cell_id]
cand["rare250_19_23"] = [hurlbert_rarefy(cache[c]["ab"], 250) for c in cand.cell_id]
cand["log_effort_19_23"] = np.log10(cand.total_19_23.clip(lower=1))

base = pd.read_csv(os.path.join(DATA, "model_cells.csv"))
both = cand.merge(base[["cell_id", "rarefied_250"]], on="cell_id", suffixes=("", "_base"))
print("\nrecords 2019-2023 as share of 2000-2024 (median over cells): %.2f"
      % (cand.total_19_23 / cand.total_records.clip(lower=1)).median())
print("correlation of rarefied richness, 2019-23 vs 2000-24 (shared cells, n=%d): %.3f"
      % (both.rare250_19_23.notna().sum(),
         both[["rare250_19_23", "rarefied_250_base"]].dropna().corr().iloc[0, 1]))

d = cand[(cand.total_19_23 >= 20) & cand.rare250_19_23.notna()].reset_index(drop=True)
d = d.rename(columns={"rare250_19_23": "rich", "log_effort_19_23": "log_effort_w"})
print("\nmodel cells with 2019-23 records: %d (main analysis: %d)" % (len(d), len(base)))
ctrl = ["log_effort_w", "temp_c", "precip_mm_yr"]
eco = pd.read_csv(os.path.join(DATA, "ecoregions_1p0.csv"))
for y in ("gpp", "npp"):
    zd = d[[y, "rich"] + ctrl].astype(float).apply(z)
    ols = sm.OLS(zd[y], sm.add_constant(zd[["rich"] + ctrl])).fit(cov_type="HC3")
    w = queen_from_grid(d.lat_c.values, d.lon_c.values, 1.0); w.transform = "r"
    sem = ML_Error(zd[y].values.reshape(-1, 1), zd[["rich"] + ctrl].values, w=w)
    bs = float(sem.betas[1][0]); ps = 2 * (1 - norm.cdf(abs(bs / np.sqrt(sem.vm[1, 1]))))
    dd = d.copy(); dd[y] = dd[y].astype(float)
    for c in ctrl + ["rich"]:
        dd[c] = dd[c].astype(float)
    CTRL_BAK = list(CTRL)
    import robustness_suite as R
    R.CTRL = ctrl
    g, lo, hi = block_cv_gain(dd, y, "rich")
    R.CTRL = CTRL_BAK
    e = zd.join(d[["cell_id"]]).merge(eco, on="cell_id").dropna(subset=["eco_name"])
    X = pd.concat([e[["rich"] + ctrl], pd.get_dummies(e.eco_name, drop_first=True,
                                                      dtype=float)], axis=1)
    fe = sm.OLS(e[y], sm.add_constant(X)).fit(cov_type="cluster",
                                              cov_kwds={"groups": e.eco_name})
    print("%s 2019-23: OLS %+.3f (p=%.1e) | SEM %+.3f (p=%.3f) | CV %+.1f%% [%+.1f, %+.1f] "
          "| within-ecoregion %+.3f (p=%.3f)"
          % (y.upper(), ols.params["rich"], ols.pvalues["rich"], bs, ps, g, lo, hi,
             fe.params["rich"], fe.pvalues["rich"]))
