# -*- coding: utf-8 -*-
"""Does the richness-productivity association survive plausible confounders?

Adds elevation (mean), topographic heterogeneity (elevation SD; Stein et al.
2014) and productivity seasonality (NDVI coefficient of variation; Coops et al.
2009) to the corrected model, one block at a time, and asks:

  1. does the richness coefficient survive (OLS, spatial error, block CV)?
  2. do the confounders absorb the broad residual plateau (I ~0.15 out to ~9 deg)
     that pointed to an omitted regional driver in the first place?
"""
import os
import sys
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm
from spreg import ML_Error
from statsmodels.stats.outliers_influence import variance_inflation_factor

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
sys.path.insert(0, HERE)
from weights_sensitivity import queen_from_grid

RICH = "rarefied_250"
BASE = ["log_effort", "temp_c", "precip_mm_yr"]
TOPO = ["elev_mean", "elev_sd"]
SEAS = ["ndvi_cv"]
RNG = np.random.default_rng(31)


def z(s):
    return (s - s.mean()) / s.std()


def plateau(resid, lat, lon, lo=4.5, hi=9.0):
    """Mean residual Moran's I over the broad 4.5-9 degree band."""
    zr = (resid - resid.mean()) / resid.std()
    D = np.hypot(lat[:, None] - lat[None, :], lon[:, None] - lon[None, :])
    Wm = ((D > lo) & (D <= hi)).astype(float)
    return (len(zr) / Wm.sum()) * (zr @ Wm @ zr) / (zr @ zr)


def block_cv(d, y, cols_base, cols_full, B=4.0, nboot=3000):
    blk = pd.factorize(np.floor(d.lat_c / B).astype(int).astype(str) + "_"
                       + np.floor(d.lon_c / B).astype(int).astype(str))[0]
    yv = d[y].values
    e = {}
    for tag, cols in (("b", cols_base), ("f", cols_full)):
        ee_ = np.empty(len(d))
        for f in np.unique(blk):
            te = blk == f; tr = ~te
            Xtr = np.column_stack([np.ones(tr.sum())] + [d[c].values[tr] for c in cols])
            Xte = np.column_stack([np.ones(te.sum())] + [d[c].values[te] for c in cols])
            b, *_ = np.linalg.lstsq(Xtr, yv[tr], rcond=None)
            ee_[te] = (yv[te] - Xte @ b) ** 2
        e[tag] = ee_
    diff = e["b"] - e["f"]
    sb = pd.Series(diff).groupby(blk).sum().values
    nb = pd.Series(np.ones(len(d))).groupby(blk).sum().values
    reps = [sb[ix].sum() / nb[ix].sum()
            for ix in (RNG.integers(0, len(sb), len(sb)) for _ in range(nboot))]
    lo, hi = np.percentile(reps, [2.5, 97.5]) / e["b"].mean() * 100
    return 100 * diff.mean() / e["b"].mean(), lo, hi


def run(d, y, controls, label):
    zd = d[[y, RICH] + controls].astype(float).apply(z)
    zd[["lat_c", "lon_c"]] = d[["lat_c", "lon_c"]].values
    X = sm.add_constant(zd[[RICH] + controls])
    ols = sm.OLS(zd[y], X).fit(cov_type="HC3")
    w = queen_from_grid(d.lat_c.values, d.lon_c.values, 1.0)
    w.transform = "r"
    sem = ML_Error(zd[y].values.reshape(-1, 1), zd[[RICH] + controls].values, w=w)
    bs = float(sem.betas[1][0]); ps = 2 * (1 - norm.cdf(abs(bs / np.sqrt(sem.vm[1, 1]))))
    plat = plateau(ols.resid.values, d.lat_c.values, d.lon_c.values)
    g, lo, hi = block_cv(zd, y, controls, controls + [RICH])
    print("%-30s OLS %+.3f (p=%.1e) R2=%.3f | SEM %+.3f (p=%.3f) AIC %6.1f | "
          "plateau I=%+.3f | CV %+5.1f%% [%+5.1f,%+5.1f]%s"
          % (label, ols.params[RICH], ols.pvalues[RICH], ols.rsquared, bs, ps,
             sem.aic, plat, g, lo, hi, " *" if lo > 0 else ""))
    return ols


def main():
    m = pd.read_csv(os.path.join(DATA, "model_cells.csv"))
    c = pd.read_csv(os.path.join(DATA, "confounders_1p0.csv"))
    d = m.merge(c, on="cell_id", how="left")
    miss = d[TOPO + SEAS].isna().any(axis=1).sum()
    d = d.dropna(subset=TOPO + SEAS).reset_index(drop=True)
    print("n = %d cells (%d dropped for missing confounder values)\n" % (len(d), miss))

    print("correlations with effort-corrected richness and GPP:")
    cm = d[[RICH, "gpp", "elev_mean", "elev_sd", "ndvi_cv", "temp_c", "precip_mm_yr"]].corr()
    print(cm[[RICH, "gpp"]].round(3).to_string())

    for y in ("gpp", "npp"):
        print("\n=== response: %s ===" % y.upper())
        run(d, y, BASE, "baseline (effort+climate)")
        run(d, y, BASE + TOPO, "+ elevation, topo heterog.")
        run(d, y, BASE + SEAS, "+ NDVI seasonality")
        full = run(d, y, BASE + TOPO + SEAS, "+ all confounders")

    Xv = sm.add_constant(d[[RICH] + BASE + TOPO + SEAS].astype(float)).values
    print("\nVIF, full model:")
    for i, t in enumerate([RICH] + BASE + TOPO + SEAS, start=1):
        print("  %-14s %.2f" % (t, variance_inflation_factor(Xv, i)))


if __name__ == "__main__":
    main()
