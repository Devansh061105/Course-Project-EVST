# -*- coding: utf-8 -*-
"""Robustness matrix for the richness-productivity association (1 degree).

Each variant changes ONE analytical choice relative to the baseline
(GPP response, dominant-class mask, Hurlbert rarefaction at n=250) and is scored
three ways, so a reader can see whether any single choice drives the result:

  OLS     standardised beta, HC3 p          (point estimate; unbiased per
                                              Hawkins et al. 2007)
  SEM     standardised beta, ML p           (recommended SAR form per
                                              Kissling & Carl 2008)
  CV      out-of-sample MSE reduction from adding richness, leave-4-degree-
          block-out, block-bootstrap 95% CI (Roberts et al. 2017)

Variants
  response   GPP (baseline), NPP, NDVI, EVI
  mask       dominant-class (baseline); natural_frac >= 0.5; >= 0.7;
             cropland+built < 0.3; land only (no land-cover mask)
  rarefy     n = 250 (baseline), 100, 50
"""
import os
import sys
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
from weights_sensitivity import queen_from_grid

CTRL = ["log_effort", "temp_c", "precip_mm_yr"]
RNG = np.random.default_rng(11)
NBOOT = 3000


def z(s):
    return (s - s.mean()) / s.std()


def block_cv_gain(d, y, rich, B=4.0):
    blk = pd.factorize(np.floor(d.lat_c / B).astype(int).astype(str) + "_"
                       + np.floor(d.lon_c / B).astype(int).astype(str))[0]
    yv = d[y].values
    e0 = np.empty(len(d)); e1 = np.empty(len(d))
    for f in np.unique(blk):
        te = blk == f; tr = ~te
        for cols, e in ((CTRL, e0), (CTRL + [rich], e1)):
            Xtr = np.column_stack([np.ones(tr.sum())] + [d[c].values[tr] for c in cols])
            Xte = np.column_stack([np.ones(te.sum())] + [d[c].values[te] for c in cols])
            b, *_ = np.linalg.lstsq(Xtr, yv[tr], rcond=None)
            e[te] = (yv[te] - Xte @ b) ** 2
    sb = pd.Series(e0 - e1).groupby(blk).sum().values
    nb = pd.Series(np.ones(len(d))).groupby(blk).sum().values
    reps = np.empty(NBOOT)
    for k in range(NBOOT):
        ix = RNG.integers(0, len(sb), len(sb))
        reps[k] = sb[ix].sum() / nb[ix].sum()
    gain = 100 * (e0 - e1).mean() / e0.mean()
    lo, hi = np.percentile(reps, [2.5, 97.5]) / e0.mean() * 100
    return gain, lo, hi


def score(d, y, rich, label):
    d = d.dropna(subset=[y, rich] + CTRL).reset_index(drop=True)
    if len(d) < 40:
        print("%-34s n=%-4d too few cells" % (label, len(d)))
        return
    zd = d[[y, rich] + CTRL].astype(float).apply(z)
    ols = sm.OLS(zd[y], sm.add_constant(zd[[rich] + CTRL])).fit(cov_type="HC3")
    w = queen_from_grid(d.lat_c.values, d.lon_c.values, 1.0)
    w.transform = "r"
    sem = ML_Error(zd[y].values.reshape(-1, 1), zd[[rich] + CTRL].values, w=w)
    bs = float(sem.betas[1][0]); ses = float(np.sqrt(sem.vm[1, 1]))
    ps = 2 * (1 - norm.cdf(abs(bs / ses)))
    g, lo, hi = block_cv_gain(d, y, rich)
    print("%-34s n=%-4d OLS %+.3f (p=%.1e) | SEM %+.3f (p=%.3f) | CV %+5.1f%% [%+5.1f, %+5.1f]%s"
          % (label, len(d), ols.params[rich], ols.pvalues[rich], bs, ps, g, lo, hi,
             " *" if lo > 0 else ""))


def main():
    m = pd.read_csv(os.path.join(DATA, "merged_cells.csv"))
    m["wc_mode"] = m.wc_mode.round()
    m["log_effort"] = np.log10(m.total_records.clip(lower=1))
    base_ok = (m.wc_mode.notna() & (m.total_records >= 20)
               & m.temp_c.notna() & m.precip_mm_yr.notna())
    dom = base_ok & ~m.wc_mode.isin([40, 50, 80])

    print("CV column: out-of-sample MSE reduction from adding richness, "
          "leave-4deg-block-out; * = block-bootstrap CI excludes 0\n")
    print("--- response variable (dominant-class mask, rarefied@250) ---")
    for y in ("gpp", "npp", "ndvi", "evi"):
        score(m[dom], y, "rarefied_250", "response = %s" % y.upper())

    print("\n--- land-cover mask (GPP, rarefied@250) ---")
    nonwater = m.water_frac < 0.5
    masks = {
        "dominant class (baseline)": dom,
        "natural_frac >= 0.5": base_ok & nonwater & (m.natural_frac >= 0.5),
        "natural_frac >= 0.7": base_ok & nonwater & (m.natural_frac >= 0.7),
        "cropland+built < 0.3": base_ok & nonwater & (m.excluded_frac < 0.3),
        "land only, NO land-cover mask": base_ok & nonwater,
    }
    for lab, msk in masks.items():
        score(m[msk], "gpp", "rarefied_250", "mask = " + lab)

    print("\n--- rarefaction level (GPP, dominant-class mask) ---")
    for col in ("rarefied_250", "rarefied_100", "rarefied_50"):
        score(m[dom], "gpp", col, "richness = " + col)

    print("\n--- raw (uncorrected) richness, for contrast ---")
    score(m[dom], "gpp", "obs_richness", "richness = raw observed (naive)")


if __name__ == "__main__":
    main()
