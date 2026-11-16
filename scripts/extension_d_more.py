# -*- coding: utf-8 -*-
"""Extension D, completed: the gaps listed in RESULTS_EXTENSION_D.md, plus a third taxon.

  M1  Plants at 1 degree: the two tests the birds had and the plants lacked,
      the quadratic (hump) test and leave-block-out cross-validation.
  M2  Plants at 0.5 degree: the same chain at the finer grain
      (data/gbif_cells_plants_0p5.csv from gbif_pull_generic.py plants 0.5).
  M3  Butterflies and moths (Lepidoptera) at 1 degree: a third taxon recorded by
      yet another community of observers (gbif_pull_generic.py lepidoptera 1.0).

Same mask, climate controls and standardisation as everywhere else; SEs
clustered by ecoregion. Each part is skipped with a message if its pull is
missing. Writes data/extension_d_more_estimates.csv.
"""
import contextlib
import io
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

CLIM = ["temp_c", "precip_mm_yr"]
RNG = np.random.default_rng(88)
EST = []


def z(s):
    return (s - s.mean()) / s.std()


def ols(d, y, cols, fe=False):
    X = pd.DataFrame({c: z(d[c].astype(float)) for c in cols})
    if fe:
        X = pd.concat([X, pd.get_dummies(d.eco_name, prefix="fe", drop_first=True,
                                         dtype=float)], axis=1)
    return sm.OLS(z(d[y].astype(float)), sm.add_constant(X)).fit(
        cov_type="cluster", cov_kwds={"groups": d.eco_name})


def sem(d, y, cols, cell):
    X = np.column_stack([z(d[c].astype(float)).values for c in cols])
    w = queen_from_grid(d.lat_c.values, d.lon_c.values, cell)
    w.transform = "r"
    with contextlib.redirect_stdout(io.StringIO()):
        s = ML_Error(z(d[y].astype(float)).values.reshape(-1, 1), X, w=w)
    b = float(s.betas[1][0]); se = float(np.sqrt(s.vm[1, 1]))
    return b, se, 2 * (1 - norm.cdf(abs(b / se)))


def chain(d, rich, effort, tag, cell, key):
    cols = [rich, effort] + CLIM
    m = ols(d, "gpp", cols); f = ols(d, "gpp", cols, fe=True)
    b, se, p = sem(d, "gpp", cols, cell)
    print("  %-30s n=%-4d corrected beta %+.3f (p = %.4f) | within ecoregions %+.3f "
          "(p = %.4f) | spatial error %+.3f (p = %.4f)"
          % (tag, len(d), m.params[rich], m.pvalues[rich], f.params[rich], f.pvalues[rich], b, p))
    for spec, bb, ss, pp in (("corrected", m.params[rich], m.bse[rich], m.pvalues[rich]),
                             ("within", f.params[rich], f.bse[rich], f.pvalues[rich]),
                             ("sem", b, se, p)):
        EST.append({"part": key, "taxon": tag, "spec": spec, "beta": bb, "se": ss, "p": pp,
                    "n": len(d)})
    return m, f


def block_gain(d, rich, effort, block=4.0, nboot=3000):
    """Out-of-sample MSE reduction from adding richness, leave-one-block-out,
    block bootstrap for the interval (same construction as spatial_cv.py)."""
    blk = pd.factorize(np.floor(d.lat_c / block).astype(int).astype(str) + "_"
                       + np.floor(d.lon_c / block).astype(int).astype(str))[0]
    Z = pd.DataFrame({c: z(d[c].astype(float)) for c in ["gpp", rich, effort] + CLIM})
    y = Z.gpp.values; e0 = np.empty(len(d)); e1 = np.empty(len(d))
    for g in np.unique(blk):
        te = blk == g
        for cols, e in (([effort] + CLIM, e0), ([rich, effort] + CLIM, e1)):
            X = np.column_stack([np.ones(len(d))] + [Z[c].values for c in cols])
            bb, *_ = np.linalg.lstsq(X[~te], y[~te], rcond=None)
            e[te] = (y[te] - X[te] @ bb) ** 2
    s0 = pd.Series(e0).groupby(blk).sum().values; s1 = pd.Series(e1).groupby(blk).sum().values
    gain = 100 * (1 - s1.sum() / s0.sum())
    reps = []
    for _ in range(nboot):
        ix = RNG.integers(0, len(s0), len(s0))
        reps.append(100 * (1 - s1[ix].sum() / s0[ix].sum()))
    return gain, np.percentile(reps, 2.5), np.percentile(reps, 97.5)


def part1():
    path = os.path.join(DATA, "plants_model_cells.csv")
    if not os.path.exists(path):
        return print("M1 skipped: run extension_d_plants.py first")
    d = pd.read_csv(path).dropna(subset=["eco_name"]).reset_index(drop=True)
    rich = "plant_rarefied_100"
    print("=== M1. Plants at 1 degree: hump test and cross-validation (n = %d) ===" % len(d))
    Z = pd.DataFrame({c: z(d[c].astype(float)) for c in ["gpp", rich, "plant_log_effort"] + CLIM})
    lin = sm.OLS(Z.gpp, sm.add_constant(Z[[rich, "plant_log_effort"] + CLIM])).fit()
    Z["sq"] = Z[rich] ** 2
    quad = sm.OLS(Z.gpp, sm.add_constant(Z[[rich, "sq", "plant_log_effort"] + CLIM])).fit()
    print("M1 plants quadratic vs linear: dAIC = %+.2f; squared term %+.3f (p = %.3f) -> %s"
          % (quad.aic - lin.aic, quad.params["sq"], quad.pvalues["sq"],
             "no support for a hump" if quad.aic - lin.aic > -2 else
             ("concave (hump-like)" if quad.params["sq"] < 0 else "convex, not a hump")))
    g, lo, hi = block_gain(d, rich, "plant_log_effort")
    print("M1 plants 4-degree block CV: adding richness cuts out-of-sample MSE by %.1f%% "
          "[%.1f, %.1f]" % (g, lo, hi))
    b = d.dropna(subset=["rarefied_250"])
    g2, lo2, hi2 = block_gain(b, "rarefied_250", "log_effort")
    print("   birds on the cells with both taxa (n = %d): %.1f%% [%.1f, %.1f]"
          % (len(b), g2, lo2, hi2))


def part2():
    path = os.path.join(DATA, "gbif_cells_plants_0p5.csv")
    if not os.path.exists(path):
        return print("\nM2 skipped: run gbif_pull_generic.py plants 0.5 first")
    p = pd.read_csv(path)
    if p.plant_facet_truncated.sum():
        raise SystemExit("plant cells at the facet limit: raise it and re-pull")
    m = pd.read_csv(os.path.join(DATA, "merged_cells_0p5.csv"))
    e = pd.read_csv(os.path.join(DATA, "ecoregions_0p5.csv"))[["cell_id", "eco_name"]]
    d = p.drop(columns=["lat_c", "lon_c"]).merge(m, on="cell_id").merge(e, on="cell_id", how="left")
    d = d.dropna(subset=["eco_name", "gpp", "temp_c", "precip_mm_yr"])
    d["plant_log_effort"] = np.log10(d.plant_total_records.clip(lower=1))
    print("\n=== M2. Plants at 0.5 degree ===")
    print("cells pulled %d; plant records %d; median records per cell %d"
          % (len(p), p.plant_total_records.sum(), p.plant_total_records.median()))
    for n in (100, 50):
        s = d.dropna(subset=["plant_rarefied_%d" % n]).reset_index(drop=True)
        mm, ff = chain(s, "plant_rarefied_%d" % n, "plant_log_effort",
                       "plants, rarefied at %d" % n, 0.5, "M2")
        if n == 100:
            print("M2 plants 0.5 deg: corrected beta = %+.3f (p = %.4f), within ecoregions "
                  "%+.3f (p = %.4f), n = %d" % (mm.params["plant_rarefied_100"],
                                                mm.pvalues["plant_rarefied_100"],
                                                ff.params["plant_rarefied_100"],
                                                ff.pvalues["plant_rarefied_100"], len(s)))
            b = s[s.rarefied.notna() & (s.total_records >= 20)].reset_index(drop=True)
            chain(b, "rarefied", "log_effort", "birds, same cells", 0.5, "M2")
            print("  bird vs plant corrected richness at 0.5 degree: r = %+.3f (n = %d)"
                  % (np.corrcoef(b.rarefied, b.plant_rarefied_100)[0, 1], len(b)))


def part3():
    path = os.path.join(DATA, "gbif_cells_lepidoptera_1p0.csv")
    if not os.path.exists(path):
        return print("\nM3 skipped: run gbif_pull_generic.py lepidoptera 1.0 first")
    l = pd.read_csv(path).drop(columns=["lat_c", "lon_c"])
    if l.lepid_facet_truncated.sum():
        raise SystemExit("Lepidoptera cells at the facet limit: raise it and re-pull")
    m = pd.read_csv(os.path.join(DATA, "merged_cells.csv"))
    m["wc_mode"] = m.wc_mode.round()
    e = pd.read_csv(os.path.join(DATA, "ecoregions_1p0.csv"))[["cell_id", "eco_name"]]
    d = m.merge(l, on="cell_id").merge(e, on="cell_id", how="left")
    pl = os.path.join(DATA, "gbif_cells_plants.csv")
    if os.path.exists(pl):
        d = d.merge(pd.read_csv(pl)[["cell_id", "plant_rarefied_100"]], on="cell_id", how="left")
    nat = d[d.is_land.astype(bool) & ~d.wc_mode.isin([40, 50, 80]) & d.gpp.notna()
            & d.temp_c.notna() & d.precip_mm_yr.notna() & d.eco_name.notna()].copy()
    nat["lepid_log_effort"] = np.log10(nat.lepid_total_records.clip(lower=1))
    print("\n=== M3. Butterflies and moths at 1 degree ===")
    print("records in all cells: %d (%d identified to species); median per natural-cover "
          "cell %d" % (l.lepid_total_records.sum(), l.lepid_sp_resolved_records.sum(),
                       nat.lepid_total_records.median()))
    for n in (50, 100, 250):
        s = nat.dropna(subset=["lepid_rarefied_%d" % n])
        v = s["lepid_rarefied_%d" % n]
        print("  rarefied at %-3d cells %-4d median %.1f  distinct species per record %.2f  "
              "r with log effort %+.3f" % (n, len(s), v.median(), v.median() / n,
                                           np.corrcoef(v, s.lepid_log_effort)[0, 1]))
    s = nat.dropna(subset=["lepid_rarefied_100"]).reset_index(drop=True)
    print("  raw richness vs log effort: r = %+.3f"
          % np.corrcoef(s.lepid_obs_richness, s.lepid_log_effort)[0, 1])
    mm, ff = chain(s, "lepid_rarefied_100", "lepid_log_effort", "Lepidoptera, rarefied at 100",
                   1.0, "M3")
    print("M3 lepidoptera: corrected beta = %+.3f (p = %.4f), within ecoregions %+.3f "
          "(p = %.4f), n = %d" % (mm.params["lepid_rarefied_100"], mm.pvalues["lepid_rarefied_100"],
                                  ff.params["lepid_rarefied_100"], ff.pvalues["lepid_rarefied_100"],
                                  len(s)))
    chain(nat.dropna(subset=["lepid_rarefied_50"]).reset_index(drop=True), "lepid_rarefied_50",
          "lepid_log_effort", "Lepidoptera, rarefied at 50", 1.0, "M3")
    b = s.dropna(subset=["rarefied_250"]).reset_index(drop=True)
    chain(b, "rarefied_250", "log_effort", "birds, same cells", 1.0, "M3")
    print("  agreement of corrected richness: Lepidoptera vs birds r = %+.3f (n = %d)"
          % (np.corrcoef(b.lepid_rarefied_100, b.rarefied_250)[0, 1], len(b)))
    if "plant_rarefied_100" in s:
        c = s.dropna(subset=["plant_rarefied_100"])
        print("  agreement of corrected richness: Lepidoptera vs plants r = %+.3f (n = %d)"
              % (np.corrcoef(c.lepid_rarefied_100, c.plant_rarefied_100)[0, 1], len(c)))


def main():
    part1(); part2(); part3()
    pd.DataFrame(EST).to_csv(os.path.join(DATA, "extension_d_more_estimates.csv"), index=False)


if __name__ == "__main__":
    main()
