# -*- coding: utf-8 -*-
"""The 1-degree headline chain, repeated at 0.5 degrees (plan Step 8 grid-size check).

Needs data/merged_cells_0p5.csv (grid_robustness.py 0.5) and
data/ecoregions_0p5.csv (gee_ecoregions.py 0.5). GPP only: grid_robustness.py
extracts GPP, not NPP. Same specification as the 1-degree analysis:
  gpp ~ rarefied(250) + log10(effort) + temperature + precipitation
standardised, natural-cover cells only (dominant class not cropland / built-up /
water), >= 250 species-identified records (rarefaction at n = 250).

Chain: baseline (SEs clustered by ecoregion) -> + biome FE -> + ecoregion FE
(within-ecoregion) -> spatial error -> leave-block-out CV (blocks scaled to the
same geographic size as the 1-degree 4-degree blocks).
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

CELL = 0.5
RICH = "rarefied"
CTRL = ["log_effort", "temp_c", "precip_mm_yr"]
RNG = np.random.default_rng(55)


def z(s):
    return (s - s.mean()) / s.std()


def load():
    m = pd.read_csv(os.path.join(DATA, "merged_cells_0p5.csv"))
    e = pd.read_csv(os.path.join(DATA, "ecoregions_0p5.csv"))
    n0 = len(m)
    d = m[m.gpp.notna() & m.wc_mode.notna() & ~m.wc_mode.isin([40, 50, 80])
          & (m.total_records >= 20) & m[RICH].notna()
          & m.temp_c.notna() & m.precip_mm_yr.notna()].copy()
    d = d.merge(e, on="cell_id", how="left")
    print("0.5-degree cells in file: %d  | pass mask + records + data: %d  | with ecoregion: %d"
          % (n0, len(d), d.eco_name.notna().sum()))
    return d


def block_cv(d, y, block_deg, nboot=3000):
    blk = pd.factorize(np.floor(d.lat_c / block_deg).astype(int).astype(str) + "_"
                       + np.floor(d.lon_c / block_deg).astype(int).astype(str))[0]
    yv = d[y].values
    e0 = np.empty(len(d)); e1 = np.empty(len(d))
    for f in np.unique(blk):
        te = blk == f; tr = ~te
        for cols, e in ((CTRL, e0), (CTRL + [RICH], e1)):
            Xtr = np.column_stack([np.ones(tr.sum())] + [d[c].values[tr] for c in cols])
            Xte = np.column_stack([np.ones(te.sum())] + [d[c].values[te] for c in cols])
            b, *_ = np.linalg.lstsq(Xtr, yv[tr], rcond=None)
            e[te] = (yv[te] - Xte @ b) ** 2
    sb = pd.Series(e0 - e1).groupby(blk).sum().values
    nb = pd.Series(np.ones(len(d))).groupby(blk).sum().values
    reps = [sb[ix].sum() / nb[ix].sum()
            for ix in (RNG.integers(0, len(sb), len(sb)) for _ in range(nboot))]
    lo, hi = np.percentile(reps, [2.5, 97.5]) / e0.mean() * 100
    return 100 * (e0 - e1).mean() / e0.mean(), lo, hi, len(np.unique(blk))


def main():
    d = load()
    d = d.dropna(subset=["eco_name"]).reset_index(drop=True)
    y = "gpp"
    for c in [y, RICH] + CTRL:
        d[c] = z(d[c].astype(float))
    print("modelled: %d cells in %d ecoregions, %d biomes\n"
          % (len(d), d.eco_name.nunique(), d.biome.nunique()))

    def ols(fe, label):
        X = d[[RICH] + CTRL].copy()
        if fe:
            X = pd.concat([X, pd.get_dummies(d[fe], drop_first=True, dtype=float)], axis=1)
        m = sm.OLS(d[y], sm.add_constant(X)).fit(
            cov_type="cluster", cov_kwds={"groups": d.eco_name})
        pl = plateau(m.resid.values, d.lat_c.values, d.lon_c.values)
        print("%-44s beta %+.3f  se %.3f  p=%.4f  plateau I=%+.3f"
              % (label, m.params[RICH], m.bse[RICH], m.pvalues[RICH], pl))
        return m

    print("GPP, standardised, SEs clustered by ecoregion")
    ols(None, "A  baseline")
    ols("biome", "B  + biome fixed effects")
    ols("eco_name", "C  + ecoregion fixed effects (within)")

    try:
        w = queen_from_grid(d.lat_c.values, d.lon_c.values, CELL)
        w.transform = "r"
        islands = len(w.islands)
        s = ML_Error(d[y].values.reshape(-1, 1), d[[RICH] + CTRL].values, w=w)
        b, se = float(s.betas[1][0]), float(np.sqrt(s.vm[1, 1]))
        print("\nspatial error (queen, %d island cells): beta %+.3f  p=%.4f  lambda=%.2f"
              % (islands, b, 2 * (1 - norm.cdf(abs(b / se))), float(s.lam)))
    except Exception as e:
        print("\nspatial error model failed: %s" % str(e)[:100])

    print("\nleave-block-out CV (richness added to climate + effort):")
    for B in (2.0, 4.0):
        g, lo, hi, nb = block_cv(d, y, B)
        print("  %.0f-degree blocks (%d): MSE reduction %+.1f%%  95%% CI [%+.1f, %+.1f]%s"
              % (B, nb, g, lo, hi, "  *" if lo > 0 else ""))

    tot = d[RICH].var(ddof=0)
    within = (d[RICH] - d.groupby("eco_name")[RICH].transform("mean")).var(ddof=0)
    print("\nrichness variance within ecoregions at 0.5 deg: %.1f%% (1 deg: 38.5%%)"
          % (100 * within / tot))
    print("\n1-degree reference: baseline +0.273, biome FE +0.182, ecoregion FE +0.030 "
          "(p=0.59), SEM +0.017 (p=0.51), 4-deg block CV +9.4%")


if __name__ == "__main__":
    main()
