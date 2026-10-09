# -*- coding: utf-8 -*-
"""Settle the lag-vs-error question that the main conclusion hinges on.

Background (docs/RESULTS_SENSITIVITY.md): richness is significant under the
spatial LAG model at both 1 and 2 degrees, and non-significant under the spatial
ERROR model at both. Which family the data prefer flips with grain. Two
independent ways to adjudicate:

PART 1 - nest both models in the Spatial Durbin family and test restrictions.
  SLX   y = Xb + WXt + e
  SAR   y = rWy + Xb + e                     (lag)
  SEM   y = Xb + u,  u = lWu + e             (error)
  SDM   y = rWy + Xb + WXt + e               (Durbin; nests SAR and SEM)
  SDEM  y = Xb + WXt + u, u = lWu + e        (Durbin error; nests SEM and SLX)
  LR(SDM vs SAR) tests t=0. LR(SDM vs SEM) is the common-factor test: if it is
  not rejected the error model is adequate. Richness effects are reported as
  direct / indirect / total impacts with simulation-based intervals, because in
  SDM the raw coefficient is not the marginal effect.

PART 2 - spatial block cross-validation (Ploton et al. 2020).
  Model-free with respect to the lag/error choice: does adding richness to a
  climate+effort model improve OUT-OF-SAMPLE prediction of GPP when whole
  spatial blocks are held out? Random K-fold is run alongside to show how much
  random CV flatters the model when neighbours leak across folds.

All variables are z-scored for Part 1, so coefficients are standardised.
"""
import os
import sys
import warnings

import numpy as np
import pandas as pd
from scipy.stats import chi2, norm
from spreg import ML_Error, ML_Lag, OLS as sOLS

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
sys.path.insert(0, HERE)
from weights_sensitivity import queen_from_grid

X_COLS = ["rarefied_250", "log_effort", "temp_c", "precip_mm_yr"]
RICH = "rarefied_250"
RNG = np.random.default_rng(20261006)


def z(s):
    return (s - s.mean()) / s.std()


def coef(model, name):
    """Coefficient and SE for a named regressor in a spreg model."""
    names = list(model.name_x)
    if hasattr(model, "name_yend") and model.name_yend:
        names = names + list(model.name_yend)
    i = names.index(name)
    return float(model.betas[i][0]), float(np.sqrt(model.vm[i, i])), i


def part1(d, cell):
    print("=" * 78)
    print("PART 1 - Spatial Durbin family, %.1f deg, n=%d (standardised)" % (cell, len(d)))
    print("=" * 78)
    w = queen_from_grid(d.lat_c.values, d.lon_c.values, cell)
    w.transform = "r"
    zd = d[X_COLS + ["gpp"]].astype(float).apply(z)
    y = zd.gpp.values.reshape(-1, 1)
    X = zd[X_COLS].values

    fits = {
        "OLS":  sOLS(y, X, w=w, name_x=X_COLS, name_y="gpp"),
        "SLX":  sOLS(y, X, w=w, slx_lags=1, name_x=X_COLS, name_y="gpp"),
        "SAR":  ML_Lag(y, X, w=w, name_x=X_COLS, name_y="gpp"),
        "SEM":  ML_Error(y, X, w=w, name_x=X_COLS, name_y="gpp"),
        "SDM":  ML_Lag(y, X, w=w, slx_lags=1, name_x=X_COLS, name_y="gpp"),
        "SDEM": ML_Error(y, X, w=w, slx_lags=1, name_x=X_COLS, name_y="gpp"),
    }

    print("\n%-6s %10s %9s %10s %9s %12s" % ("model", "logL", "AIC", "rich b", "p", "W_rich t (p)"))
    print("-" * 64)
    for k, m in fits.items():
        b, se, _ = coef(m, RICH)
        p = 2 * (1 - norm.cdf(abs(b / se)))
        wtxt = ""
        if "W_" + RICH in list(m.name_x):
            bt, set_, _ = coef(m, "W_" + RICH)
            wtxt = "%+.3f (%.3f)" % (bt, 2 * (1 - norm.cdf(abs(bt / set_))))
        print("%-6s %10.2f %9.2f %+10.3f %9.4f %14s"
              % (k, m.logll, m.aic, b, p, wtxt))

    k_wx = len(X_COLS)
    print("\nLikelihood-ratio tests (df=%d):" % k_wx)
    for big, small, meaning in (
            ("SDM", "SAR", "WX terms needed beyond lag?"),
            ("SDM", "SEM", "common-factor test: is the ERROR model adequate?"),
            ("SDEM", "SEM", "WX terms needed beyond error?"),
            ("SDEM", "SLX", "spatial error needed beyond SLX?")):
        df_ = k_wx if small in ("SAR", "SEM") else 1
        lr = 2 * (fits[big].logll - fits[small].logll)
        p = 1 - chi2.cdf(lr, df_)
        print("  %-4s vs %-4s LR=%7.2f df=%d p=%.4g  %s -> %s"
              % (big, small, lr, df_, p, meaning,
                 "%s rejected" % small if p < 0.05 else "%s NOT rejected" % small))

    # ---- impacts for SDM, by simulation from the parameter covariance -----
    sdm = fits["SDM"]
    bvec = sdm.betas.flatten()
    V = sdm.vm
    # spreg's ML_Lag name_x already ends with the spatial-lag name (W_gpp), and
    # rho is the LAST element of betas. Do not append a name for it.
    names = list(sdm.name_x)
    ib = names.index(RICH)
    it = names.index("W_" + RICH)
    ir = len(bvec) - 1
    Wd = w.full()[0]
    n = Wd.shape[0]
    I = np.eye(n)
    draws = RNG.multivariate_normal(bvec, V, size=1000)
    dirs, tots = [], []
    for dr in draws:
        rho = dr[ir]
        if abs(rho) >= 0.99:
            continue
        A = np.linalg.inv(I - rho * Wd)
        S = A @ (dr[ib] * I + dr[it] * Wd)
        dirs.append(np.trace(S) / n)
        tots.append(S.sum() / n)
    dirs, tots = np.array(dirs), np.array(tots)
    ind = tots - dirs

    def ci(a):
        return "%+.3f [%+.3f, %+.3f]%s" % (
            np.median(a), np.percentile(a, 2.5), np.percentile(a, 97.5),
            "  *" if (np.percentile(a, 2.5) > 0 or np.percentile(a, 97.5) < 0) else "")

    print("\nSDM richness impacts (median, 95%% sim. interval; * = excludes 0), %d draws:"
          % len(dirs))
    print("  direct   %s" % ci(dirs))
    print("  indirect %s" % ci(ind))
    print("  total    %s" % ci(tots))

    # SDEM impacts are linear: direct=b, indirect=t, total=b+t
    sd = fits["SDEM"]
    b, seb, i1 = coef(sd, RICH)
    t, set_, i2 = coef(sd, "W_" + RICH)
    var_tot = sd.vm[i1, i1] + sd.vm[i2, i2] + 2 * sd.vm[i1, i2]
    tot = b + t
    ptot = 2 * (1 - norm.cdf(abs(tot / np.sqrt(var_tot))))
    print("SDEM richness: direct %+.3f (p=%.3f), indirect %+.3f (p=%.3f), total %+.3f (p=%.3f)"
          % (b, 2 * (1 - norm.cdf(abs(b / seb))), t,
             2 * (1 - norm.cdf(abs(t / set_))), tot, ptot))
    return fits


def ols_predict(train, test, cols):
    Xtr = np.column_stack([np.ones(len(train))] + [train[c].values for c in cols])
    Xte = np.column_stack([np.ones(len(test))] + [test[c].values for c in cols])
    beta, *_ = np.linalg.lstsq(Xtr, train.gpp.values, rcond=None)
    return Xte @ beta


def cv_scores(d, folds, sets):
    preds = {k: np.full(len(d), np.nan) for k in sets}
    per_fold = {k: [] for k in sets}
    for f in np.unique(folds):
        te = folds == f
        tr = ~te
        if te.sum() == 0 or tr.sum() < 20:
            continue
        for k, cols in sets.items():
            p = ols_predict(d[tr], d[te], cols)
            preds[k][te] = p
            per_fold[k].append(np.sqrt(np.mean((d.gpp.values[te] - p) ** 2)))
    out = {}
    yv = d.gpp.values
    for k in sets:
        m = ~np.isnan(preds[k])
        rmse = np.sqrt(np.mean((yv[m] - preds[k][m]) ** 2))
        r2 = 1 - np.sum((yv[m] - preds[k][m]) ** 2) / np.sum((yv[m] - yv[m].mean()) ** 2)
        out[k] = (rmse, r2, np.array(per_fold[k]))
    return out


def part2(d):
    print("\n" + "=" * 78)
    print("PART 2 - spatial block cross-validation (out-of-sample GPP), n=%d" % len(d))
    print("=" * 78)
    d = d.reset_index(drop=True).copy()
    d["gpp"] = d.gpp.astype(float)
    base = ["log_effort", "temp_c", "precip_mm_yr"]
    sets = {"climate+effort": base,
            "climate+effort+richness": base + [RICH],
            "richness only": [RICH]}

    print("\n%-28s %-24s %8s %8s" % ("scheme", "model", "RMSE", "R2_oos"))
    print("-" * 72)

    # random K-fold, repeated
    reps = []
    for r in range(20):
        folds = RNG.permutation(np.arange(len(d)) % 10)
        reps.append(cv_scores(d, folds, sets))
    for k in sets:
        rm = np.mean([x[k][0] for x in reps]); r2 = np.mean([x[k][1] for x in reps])
        print("%-28s %-24s %8.4f %8.3f" % ("random 10-fold (x20)", k, rm, r2))
    gain_rand = np.mean([x["climate+effort"][0] - x["climate+effort+richness"][0]
                         for x in reps])

    results = {"random": gain_rand}
    for B in (3.0, 4.0, 6.0):
        blk = (np.floor(d.lat_c / B).astype(int).astype(str) + "_"
               + np.floor(d.lon_c / B).astype(int).astype(str))
        codes = pd.factorize(blk)[0]
        s = cv_scores(d, codes, sets)
        for k in sets:
            print("%-28s %-24s %8.4f %8.3f"
                  % ("leave-block-out %.0f deg (%d)" % (B, len(np.unique(codes))),
                     k, s[k][0], s[k][1]))
        a = s["climate+effort"][2]
        b = s["climate+effort+richness"][2]
        diff = a - b                       # >0 means richness helped that fold
        boot = [RNG.choice(diff, len(diff)).mean() for _ in range(2000)]
        lo, hi = np.percentile(boot, [2.5, 97.5])
        print("   richness gain per fold: mean %+.4f, 95%% boot CI [%+.4f, %+.4f], "
              "helped in %d/%d folds -> %s"
              % (diff.mean(), lo, hi, (diff > 0).sum(), len(diff),
                 "(per-fold metric; SUPERSEDED by spatial_cv.py)"))
        results[B] = (diff.mean(), lo, hi)

    print("\nrandom-CV richness gain (RMSE reduction) = %+.4f" % gain_rand)
    print("NOTE: this Part 2 averages per-fold RMSE, which weights a 1-cell block like a "
          "15-cell block. Its per-fold intervals are not valid inference; use "
          "scripts/spatial_cv.py (cell-weighted block bootstrap) instead.")
    return results


def main():
    d = pd.read_csv(os.path.join(DATA, "model_cells.csv"))
    part1(d, 1.0)
    part2(d)

    p2 = os.path.join(DATA, "merged_cells_2p0.csv")
    if os.path.exists(p2):
        d2 = pd.read_csv(p2)
        d2["log_effort"] = np.log10(d2.total_records.clip(lower=1))
        d2 = d2[d2.gpp.notna() & d2.wc_mode.notna() & (~d2.wc_mode.isin([40, 50, 80]))
                & (d2.total_records >= 20) & d2.rarefied.notna()
                & d2.temp_c.notna() & d2.precip_mm_yr.notna()].copy()
        d2 = d2.rename(columns={"rarefied": RICH})
        part1(d2, 2.0)


if __name__ == "__main__":
    main()
