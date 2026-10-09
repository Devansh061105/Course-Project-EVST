# -*- coding: utf-8 -*-
"""Stress-test the small within-ecoregion effect found at 0.5 degrees.

The 0.5-degree within-ecoregion coefficient for GPP is +0.058 (p = 0.021). Within
an ecoregion the obvious non-causal explanations are:
  - elevation gradients (richness and productivity both change with altitude),
  - topographic heterogeneity (Stein et al. 2014),
  - productivity seasonality (Coops et al. 2009),
  - one or two ecoregions driving everything.
This adds those controls, repeats for NPP, and checks leave-one-ecoregion-out
stability and out-of-sample transfer. Needs data/confounders_0p5.csv
(gee_confounders.py 0.5), merged_cells_0p5.csv, ecoregions_0p5.csv.
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
sys.path.insert(0, HERE)

RICH = "rarefied"
BASE = ["log_effort", "temp_c", "precip_mm_yr"]
TOPO = ["elev_sd"]            # mean elevation is collinear with temperature (VIF ~80)
SEAS = ["ndvi_cv"]
RNG = np.random.default_rng(66)


def z(s):
    return (s - s.mean()) / s.std()


def load():
    m = pd.read_csv(os.path.join(DATA, "merged_cells_0p5.csv"))
    e = pd.read_csv(os.path.join(DATA, "ecoregions_0p5.csv"))
    c = pd.read_csv(os.path.join(DATA, "confounders_0p5.csv"))
    d = m[m.gpp.notna() & m.wc_mode.notna() & ~m.wc_mode.isin([40, 50, 80])
          & (m.total_records >= 20) & m[RICH].notna() & m.temp_c.notna()
          & m.precip_mm_yr.notna()].merge(e, on="cell_id").merge(c, on="cell_id")
    d = d.dropna(subset=["eco_name", "elev_sd", "ndvi_cv", "npp"]).reset_index(drop=True)
    return d


def fit(d, y, controls, fe, label):
    cols = [RICH] + controls
    z_ = d[[y] + cols].astype(float).apply(z)
    X = z_[cols]
    if fe:
        X = pd.concat([X, pd.get_dummies(d[fe], drop_first=True, dtype=float)], axis=1)
    m = sm.OLS(z_[y], sm.add_constant(X)).fit(
        cov_type="cluster", cov_kwds={"groups": d.eco_name})
    print("  %-40s beta %+.3f  se %.3f  p=%.4f" % (label, m.params[RICH], m.bse[RICH],
                                                    m.pvalues[RICH]))
    return m.params[RICH], m.bse[RICH], m.pvalues[RICH]


def main():
    d = load()
    print("n = %d cells, %d ecoregions\n" % (len(d), d.eco_name.nunique()))

    for y in ("gpp", "npp"):
        print("=== %s (standardised; SEs clustered by ecoregion) ===" % y.upper())
        fit(d, y, BASE, None, "baseline (effort + climate)")
        fit(d, y, BASE, "biome", "+ biome FE")
        fit(d, y, BASE, "eco_name", "+ ecoregion FE  [within]")
        fit(d, y, BASE + TOPO, "eco_name", "  + topographic heterogeneity")
        fit(d, y, BASE + SEAS, "eco_name", "  + NDVI seasonality")
        fit(d, y, BASE + TOPO + SEAS, "eco_name", "  + both  (full within model)")
        print()

    # ---- is the within effect carried by a few ecoregions? -----------------
    print("=== leave-one-ecoregion-out, full within model (GPP) ===")
    cols = [RICH] + BASE + TOPO + SEAS
    out = []
    for g in d.eco_name.unique():
        s = d[d.eco_name != g]
        if s.eco_name.nunique() < 5:
            continue
        z_ = s[["gpp"] + cols].astype(float).apply(z)
        X = pd.concat([z_[cols], pd.get_dummies(s.eco_name, drop_first=True, dtype=float)], axis=1)
        m = sm.OLS(z_["gpp"], sm.add_constant(X)).fit(
            cov_type="cluster", cov_kwds={"groups": s.eco_name})
        out.append((g, int((d.eco_name == g).sum()), m.params[RICH], m.pvalues[RICH]))
    o = pd.DataFrame(out, columns=["dropped", "n_cells", "beta", "p"])
    print("  %d refits: beta range %+.3f to %+.3f ; p<0.05 in %d / %d"
          % (len(o), o.beta.min(), o.beta.max(), (o.p < 0.05).sum(), len(o)))
    worst = o.sort_values("beta").head(3)
    for r in worst.itertuples():
        print("   dropping %-34s (%3d cells): beta %+.3f p=%.3f"
              % (r.dropped[:34], r.n_cells, r.beta, r.p))

    # ---- which biomes? ------------------------------------------------------
    print("\n=== within-ecoregion effect by biome (GPP, base controls) ===")
    for b, s in d.groupby("biome"):
        if s.eco_name.nunique() < 4 or len(s) < 40:
            continue
        z_ = s[["gpp", RICH] + BASE].astype(float).apply(z)
        X = pd.concat([z_[[RICH] + BASE], pd.get_dummies(s.eco_name, drop_first=True, dtype=float)], axis=1)
        m = sm.OLS(z_["gpp"], sm.add_constant(X)).fit(
            cov_type="cluster", cov_kwds={"groups": s.eco_name})
        print("  %-48s n=%3d (%2d ecoregions)  beta %+.3f p=%.3f"
              % (b[:48], len(s), s.eco_name.nunique(), m.params[RICH], m.pvalues[RICH]))

    # ---- leave-one-ecoregion-out prediction ---------------------------------
    print("\n=== leave-one-ecoregion-out CV: does richness help predict an unseen ecoregion? ===")
    for y in ("gpp", "npp"):
        yv = d[y].values
        e0 = np.full(len(d), np.nan); e1 = np.full(len(d), np.nan)
        for g in d.eco_name.unique():
            te = (d.eco_name == g).values; tr = ~te
            for cs, e in ((BASE + TOPO + SEAS, e0), (BASE + TOPO + SEAS + [RICH], e1)):
                Xtr = np.column_stack([np.ones(tr.sum())] + [d[c].values[tr] for c in cs])
                Xte = np.column_stack([np.ones(te.sum())] + [d[c].values[te] for c in cs])
                b, *_ = np.linalg.lstsq(Xtr, yv[tr], rcond=None)
                e[te] = (yv[te] - Xte @ b) ** 2
        diff = e0 - e1
        gk = d.eco_name.values
        sb = pd.Series(diff).groupby(gk).sum().values
        nb = pd.Series(np.ones(len(d))).groupby(gk).sum().values
        reps = [sb[ix].sum() / nb[ix].sum()
                for ix in (RNG.integers(0, len(sb), len(sb)) for _ in range(4000))]
        lo, hi = np.percentile(reps, [2.5, 97.5]) / e0.mean() * 100
        print("  %s: richness cuts out-of-sample MSE by %+.1f%%  95%% CI [%+.1f, %+.1f]%s"
              % (y.upper(), 100 * diff.mean() / e0.mean(), lo, hi, "  *" if lo > 0 else ""))


if __name__ == "__main__":
    main()
