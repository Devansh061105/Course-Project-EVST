# -*- coding: utf-8 -*-
"""Specification curve: the richness coefficient under every reasonable choice.

The robustness matrix (robustness_suite.py) changes one choice at a time. This
changes them all at once: every combination of

  response         GPP, NPP, NDVI, EVI
  richness         rarefied at 250 / 100 / 50 records; coverage-based at 0.90 / 0.95
  land-cover mask  dominant class natural (the default); natural fraction >= 0.5;
                   natural fraction >= 0.7; no mask (all land)
  controls         effort + climate; + topography; + seasonality; + both
  estimator        OLS; OLS with ecoregion fixed effects; spatial error model

is fitted (4 x 5 x 4 x 4 x 3 = 960 models, standardised within each sample), and
the richness coefficients are sorted. If the headline depended on one lucky
specification it would show here. The point is the split by estimator: the
between-region estimators (OLS) against the within-region ones (fixed effects,
spatial error).

Reads data/final/biodiversity_productivity_1deg.csv. No network.
Writes data/spec_curve.csv (one row per model).
"""
import itertools
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

RESP = ["gpp", "npp", "ndvi", "evi"]
RICH = ["rarefied_250", "rarefied_100", "rarefied_50", "S_cov90", "S_cov95"]
MASK = {"dominant class natural": lambda d: ~d.wc_mode.isin([40, 50, 80]),
        "natural fraction >= 0.5": lambda d: d.natural_frac >= 0.5,
        "natural fraction >= 0.7": lambda d: d.natural_frac >= 0.7,
        "no mask (all land)": lambda d: d.wc_mode.notna()}
BASE = ["log_effort", "temp_c", "precip_mm_yr"]
CTRL = {"effort + climate": BASE,
        "+ topography": BASE + ["elev_mean", "elev_sd"],
        "+ seasonality": BASE + ["ndvi_cv"],
        "+ both": BASE + ["elev_mean", "elev_sd", "ndvi_cv"]}
EST = ["OLS", "ecoregion FE", "spatial error"]


def z(s):
    return (s - s.mean()) / s.std()


def main():
    d0 = pd.read_csv(os.path.join(DATA, "final", "biodiversity_productivity_1deg.csv"))
    d0["wc_mode"] = d0.wc_mode.round()
    d0 = d0[d0.wc_mode.notna() & (d0.total_records >= 20)]
    rows = []
    for y, r, mk, ck in itertools.product(RESP, RICH, MASK, CTRL):
        cols = CTRL[ck]
        d = d0[MASK[mk](d0)].dropna(subset=[y, r, "eco_name"] + cols).reset_index(drop=True)
        if len(d) < 60:
            continue
        Z = pd.DataFrame({c: z(d[c].astype(float)) for c in [y, r] + cols})
        X = sm.add_constant(Z[[r] + cols])
        for est in EST:
            if est == "OLS":
                f = sm.OLS(Z[y], X).fit(cov_type="cluster", cov_kwds={"groups": d.eco_name})
                b, se = f.params[r], f.bse[r]
            elif est == "ecoregion FE":
                D = pd.get_dummies(d.eco_name, prefix="fe", drop_first=True, dtype=float)
                f = sm.OLS(Z[y], pd.concat([X, D], axis=1)).fit(
                    cov_type="cluster", cov_kwds={"groups": d.eco_name})
                b, se = f.params[r], f.bse[r]
            else:
                w = queen_from_grid(d.lat_c.values, d.lon_c.values, 1.0)
                w.transform = "r"
                s = ML_Error(Z[y].values.reshape(-1, 1), Z[[r] + cols].values, w=w)
                b, se = float(s.betas[1][0]), float(np.sqrt(s.vm[1, 1]))
            p = 2 * (1 - norm.cdf(abs(b / se)))
            rows.append({"response": y, "richness": r, "mask": mk, "controls": ck,
                         "estimator": est, "n": len(d), "beta": b, "se": se, "p": p})
    out = pd.DataFrame(rows).sort_values("beta").reset_index(drop=True)
    out.to_csv(os.path.join(DATA, "spec_curve.csv"), index=False)

    print("SPEC models fitted: %d" % len(out))
    print("SPEC all models: beta > 0 in %.1f%%; median %+.3f; range %+.3f to %+.3f"
          % (100 * (out.beta > 0).mean(), out.beta.median(), out.beta.min(), out.beta.max()))
    print("\n%-16s %7s %9s %9s %9s %12s %14s" % ("estimator", "models", "median", "q10", "q90",
                                                  "beta > 0", "p < 0.05, +"))
    for est in EST:
        s = out[out.estimator == est]
        print("SPEC %-14s %4d %+9.3f %+9.3f %+9.3f %11.1f%% %13.1f%%"
              % (est, len(s), s.beta.median(), s.beta.quantile(0.1), s.beta.quantile(0.9),
                 100 * (s.beta > 0).mean(), 100 * ((s.p < 0.05) & (s.beta > 0)).mean()))
    neg = out[(out.p < 0.05) & (out.beta < 0)]
    print("significantly negative models: %d of %d" % (len(neg), len(out)))
    print("\nmedian beta by choice (all estimators pooled / OLS only / within-region only):")
    wi = out[out.estimator != "OLS"]; ol = out[out.estimator == "OLS"]
    for col in ("response", "richness", "mask", "controls"):
        for k in out[col].unique():
            print("  %-10s %-26s %+7.3f / %+7.3f / %+7.3f"
                  % (col, k, out[out[col] == k].beta.median(), ol[ol[col] == k].beta.median(),
                     wi[wi[col] == k].beta.median()))


if __name__ == "__main__":
    main()
