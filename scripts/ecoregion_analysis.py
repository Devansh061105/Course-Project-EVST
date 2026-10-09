# -*- coding: utf-8 -*-
"""Biogeographic structure: is the association between or within regions?

Rarefied richness at 1 degree partly reflects the REGIONAL species pool, which
is historically determined and spatially structured at ~1000 km - the scale of
the residual plateau. If the richness-GPP association is only BETWEEN
biogeographic regions (big-pool regions happen to be wetter and more productive),
it should vanish under region fixed effects. If it holds WITHIN regions, it is
not a species-pool artefact.

  A  plan Step 8 exactly: OLS with cluster-robust SEs by ecoregion
  B  + biome fixed effects       (between-biome differences removed)
  C  + ecoregion fixed effects   (within-ecoregion variation only)
  D  single biome: Tropical & Subtropical Moist Broadleaf Forests
  E  leave-one-ecoregion-out CV  (predict GPP in an ecoregion never seen)
Plus the residual plateau after each, to see whether biogeography absorbs it.
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
from confounder_analysis import plateau

RICH = "rarefied_250"
BASE = ["log_effort", "temp_c", "precip_mm_yr"]
RNG = np.random.default_rng(41)


def z(s):
    return (s - s.mean()) / s.std()


def prep(y):
    m = pd.read_csv(os.path.join(DATA, "model_cells.csv"))
    e = pd.read_csv(os.path.join(DATA, "ecoregions_1p0.csv"))
    d = m.merge(e, on="cell_id", how="inner").dropna(subset=["eco_name"])
    d = d.reset_index(drop=True)
    for c in [y, RICH] + BASE:
        d[c] = z(d[c].astype(float))
    return d


def fit(d, y, fe=None, label=""):
    X = d[[RICH] + BASE].copy()
    if fe:
        X = pd.concat([X, pd.get_dummies(d[fe], prefix=fe, drop_first=True,
                                         dtype=float)], axis=1)
    X = sm.add_constant(X)
    m = sm.OLS(d[y], X).fit(cov_type="cluster", cov_kwds={"groups": d.eco_name})
    plat = plateau(m.resid.values, d.lat_c.values, d.lon_c.values)
    print("%-44s n=%-4d beta %+.3f  se %.3f  p=%.4f  plateau I=%+.3f"
          % (label, int(m.nobs), m.params[RICH], m.bse[RICH], m.pvalues[RICH], plat))
    return m


def sem_with_fe(d, y, fe, label):
    X = d[[RICH] + BASE].copy()
    if fe:
        X = pd.concat([X, pd.get_dummies(d[fe], prefix=fe, drop_first=True,
                                         dtype=float)], axis=1)
    w = queen_from_grid(d.lat_c.values, d.lon_c.values, 1.0)
    w.transform = "r"
    s = ML_Error(d[y].values.reshape(-1, 1), X.values.astype(float), w=w)
    b = float(s.betas[1][0]); se = float(np.sqrt(s.vm[1, 1]))
    print("%-44s SEM beta %+.3f  p=%.4f  lambda=%.2f"
          % (label, b, 2 * (1 - norm.cdf(abs(b / se))), float(s.lam)))


def leave_one_ecoregion_out(d, y):
    yv = d[y].values
    e0 = np.full(len(d), np.nan); e1 = np.full(len(d), np.nan)
    for g in d.eco_name.unique():
        te = (d.eco_name == g).values; tr = ~te
        for cols, e in ((BASE, e0), (BASE + [RICH], e1)):
            Xtr = np.column_stack([np.ones(tr.sum())] + [d[c].values[tr] for c in cols])
            Xte = np.column_stack([np.ones(te.sum())] + [d[c].values[te] for c in cols])
            bb, *_ = np.linalg.lstsq(Xtr, yv[tr], rcond=None)
            e[te] = (yv[te] - Xte @ bb) ** 2
    diff = e0 - e1
    g = d.eco_name.values
    sb = pd.Series(diff).groupby(g).sum().values
    nb = pd.Series(np.ones(len(d))).groupby(g).sum().values
    reps = [sb[ix].sum() / nb[ix].sum()
            for ix in (RNG.integers(0, len(sb), len(sb)) for _ in range(4000))]
    lo, hi = np.percentile(reps, [2.5, 97.5]) / e0.mean() * 100
    print("leave-one-ecoregion-out CV (%d ecoregions): richness cuts out-of-sample "
          "MSE by %+.1f%%, 95%% CI [%+.1f, %+.1f]%s"
          % (len(sb), 100 * diff.mean() / e0.mean(), lo, hi, "  *" if lo > 0 else ""))


def main():
    for y in ("gpp", "npp"):
        d = prep(y)
        print("\n" + "=" * 92)
        print("RESPONSE %s  (standardised; SEs cluster-robust by ecoregion, %d clusters)"
              % (y.upper(), d.eco_name.nunique()))
        print("=" * 92)
        fit(d, y, None, "A  baseline, clustered by ecoregion (plan Step 8)")
        fit(d, y, "realm", "   + realm fixed effects")
        fit(d, y, "biome", "B  + biome fixed effects")
        fit(d, y, "eco_name", "C  + ecoregion fixed effects (within-ecoregion)")
        mb = d[d.biome == "Tropical & Subtropical Moist Broadleaf Forests"].reset_index(drop=True)
        for c in [y, RICH] + BASE:
            mb[c] = z(mb[c])
        fit(mb, y, None, "D  moist broadleaf forest biome only")
        print()
        sem_with_fe(d, y, None, "   spatial error, no FE")
        sem_with_fe(d, y, "biome", "   spatial error + biome FE")
        sem_with_fe(mb, y, None, "   spatial error, moist broadleaf only")
        print()
        leave_one_ecoregion_out(d, y)


if __name__ == "__main__":
    main()
