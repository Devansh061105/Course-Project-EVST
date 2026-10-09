# -*- coding: utf-8 -*-
"""Replicate the Hawkins et al. (2007) test on our data.

Hawkins et al. (2007, Ecography 30:375-384) used bird richness in 110x110 km
grid cells - essentially our grain - and asked whether residual spatial
autocorrelation biases OLS coefficients. Method:
  1. From a residual correlogram, find the distance beyond which OLS residuals
     are no longer autocorrelated.
  2. Repeatedly draw subsamples of cells spaced at least that far apart, so each
     subsample is approximately spatially independent.
  3. Fit OLS to each subsample; compare the full-data coefficient with the
     distribution of subsample coefficients.
They found all 22 coefficients indistinguishable, and concluded OLS estimates are
unbiased while inference is what autocorrelation damages.

Here the coefficient of interest is effort-corrected richness. The subsample
distribution also gives an inference-honest view of that coefficient that does
not depend on choosing between lag and error SAR models.
"""
import os
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
X_COLS = ["rarefied_250", "log_effort", "temp_c", "precip_mm_yr"]
RICH = "rarefied_250"
RNG = np.random.default_rng(2007)
NSUB = 2000


def z(s):
    return (s - s.mean()) / s.std()


def correlogram(resid, lat, lon, edges):
    zr = (resid - resid.mean()) / resid.std()
    D = np.hypot(lat[:, None] - lat[None, :], lon[:, None] - lon[None, :])
    out = []
    for a, b in zip(edges[:-1], edges[1:]):
        Wm = ((D > a) & (D <= b)).astype(float)
        np.fill_diagonal(Wm, 0)
        S = Wm.sum()
        if S == 0:
            out.append((a, b, np.nan, 0))
            continue
        I = (len(zr) / S) * (zr @ Wm @ zr) / (zr @ zr)
        out.append((a, b, I, int(S / 2)))
    return out


def spaced_subsample(lat, lon, dmin):
    """Random greedy draw of cells with all pairwise distances >= dmin."""
    order = RNG.permutation(len(lat))
    chosen = []
    for i in order:
        if all(np.hypot(lat[i] - lat[j], lon[i] - lon[j]) >= dmin for j in chosen):
            chosen.append(i)
    return np.array(chosen)


def main():
    d = pd.read_csv(os.path.join(DATA, "model_cells.csv")).reset_index(drop=True)
    zd = d[X_COLS + ["gpp"]].astype(float).apply(z)
    lat, lon = d.lat_c.values, d.lon_c.values

    full = sm.OLS(zd.gpp, sm.add_constant(zd[X_COLS])).fit(cov_type="HC3")
    b_full = full.params[RICH]
    print("full data n=%d: standardised richness beta = %+.3f (HC3 p=%.2g)"
          % (len(d), b_full, full.pvalues[RICH]))

    edges = np.arange(0, 16.5, 1.5)
    cg = correlogram(full.resid.values, lat, lon, edges)
    print("\nresidual correlogram (Moran's I by distance class, degrees):")
    dmin = None
    for a, b, I, npairs in cg:
        flag = ""
        if dmin is None and not np.isnan(I) and I < 0.05:
            dmin = b if a > 0 else b
            flag = "  <- first class with I < 0.05"
        print("  %4.1f-%4.1f  I=%+.3f  pairs=%5d%s" % (a, b, I, npairs, flag))
    if dmin is None:
        dmin = edges[-1]
    # Hawkins used the minimum distance needed to avoid short-distance residual
    # SAC; take the lower edge of the first non-autocorrelated class.
    dmin = max(dmin - 1.5, 1.5)

    # Residual SAC here has TWO components: a steep short-distance decay
    # (I 0.67 -> 0.25 by 4.5 deg) and a broad regional plateau (I ~0.15 out to
    # ~9 deg, zero only by ~10.5 deg). Subsampling beyond 10.5 deg leaves 4-8
    # cells - too few to fit five parameters. Hawkins et al. targeted the
    # SHORT-distance component, so test at distances that clear the steep decay.
    print("\nfull-SAC-free spacing would be %.1f deg: infeasible at this extent; "
          "testing short-distance spacings instead" % (dmin + 1.5))
    for dist in (3.0, 4.5, 6.0):
        betas, ps, ns = [], [], []
        for _ in range(NSUB):
            idx = spaced_subsample(lat, lon, dist)
            if len(idx) < len(X_COLS) + 6:
                continue
            s = zd.iloc[idx]
            m = sm.OLS(s.gpp, sm.add_constant(s[X_COLS])).fit()
            betas.append(m.params[RICH]); ps.append(m.pvalues[RICH]); ns.append(len(idx))
        betas, ps = np.array(betas), np.array(ps)
        if len(betas) == 0:
            print("\nspacing %.1f deg: no subsample reached %d cells - skipped"
                  % (dist, len(X_COLS) + 6))
            continue
        pct = (betas < b_full).mean() * 100
        print("\nsubsamples spaced >= %.1f deg: %d draws, median n=%d cells"
              % (dist, len(betas), int(np.median(ns))))
        print("  richness beta: median %+.3f, 95%% interval [%+.3f, %+.3f]"
              % (np.median(betas), *np.percentile(betas, [2.5, 97.5])))
        print("  full-data beta %+.3f sits at the %.0fth percentile of the subsample "
              "distribution -> %s"
              % (b_full, pct, "indistinguishable (OLS unbiased)" if 2.5 < pct < 97.5
                 else "OUTSIDE the subsample distribution"))
        print("  beta > 0 in %.0f%% of subsamples; p < 0.05 in %.0f%%"
              % (100 * (betas > 0).mean(), 100 * (ps < 0.05).mean()))


if __name__ == "__main__":
    main()
