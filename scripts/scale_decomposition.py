# -*- coding: utf-8 -*-
"""At what spatial scale does the richness-productivity link live?

Ecoregion fixed effects split the association into "between" and "within" using
borders drawn by biogeographers. This does the same job with no borders at all,
and into more than two pieces.

  1. Moran's eigenvector maps (distance-based MEM; Dray, Legendre & Peres-Neto
     2006). The cells' geography is turned into a set of orthogonal spatial
     patterns, ordered from continent-wide gradients to cell-to-cell texture.
  2. Band regression (Engle 1974). GPP and richness, both net of effort and
     climate, are projected onto four bands of those patterns (broad to fine) and
     onto what is left (no spatial structure). A separate slope is fitted in each
     band. Because the patterns are orthogonal, the bands are independent pieces
     of the same data and their slopes can be compared directly.
  3. An effective-sample-size test of the overall correlation (Clifford,
     Richardson & Hemon 1989; Dutilleul 1993): how many independent observations
     the autocorrelated cells are worth, and whether the correlation is still
     significant on that count.

At 1 degree and 0.5 degree. Cached data only. Writes data/scale_bands.csv.
"""
import os
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.sparse.csgraph import minimum_spanning_tree
from scipy.stats import t as tdist

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
CTRL = ["log_effort", "temp_c", "precip_mm_yr"]
NBANDS = 4
ROWS = []


def z(s):
    return (s - s.mean()) / s.std()


def haversine(lat, lon):
    la = np.radians(lat)[:, None]; lo = np.radians(lon)[:, None]
    a = (np.sin((la - la.T) / 2) ** 2
         + np.cos(la) * np.cos(la.T) * np.sin((lo - lo.T) / 2) ** 2)
    return 6371.0 * 2 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def dbmem(D):
    """Eigenvectors with positive spatial autocorrelation, broad to fine, and their Moran's I."""
    n = len(D)
    thr = minimum_spanning_tree(D).toarray().max()          # longest link that keeps all cells joined
    A = np.where((D <= thr) & (D > 0), 1 - (D / (4 * thr)) ** 2, 0.0)
    C = np.eye(n) - np.ones((n, n)) / n
    lam, vec = np.linalg.eigh(C @ A @ C)
    order = np.argsort(lam)[::-1]
    lam, vec = lam[order], vec[:, order]
    keep = lam > 1e-8 * lam[0]
    moran = n / A.sum() * lam[keep]
    return vec[:, keep], moran, thr


def zero_crossing_km(v, D, width):
    """Distance at which a pattern's autocorrelation first falls to zero: its patch size."""
    v = v - v.mean(); s2 = (v * v).mean()
    edges = np.arange(0, D.max() + width, width)
    for a, b in zip(edges[:-1], edges[1:]):
        m = (D > a) & (D <= b)
        if m.sum() < 30:
            continue
        if (np.outer(v, v)[m]).mean() / s2 <= 0:
            return (a + b) / 2
    return np.nan


def clifford(x, y, D, width):
    """Effective sample size for the correlation of two autocorrelated variables."""
    n = len(x)
    x = x - x.mean(); y = y - y.mean()
    sx2, sy2 = (x * x).mean(), (y * y).mean()
    r = (x * y).mean() / np.sqrt(sx2 * sy2)
    XX, YY = np.outer(x, x), np.outer(y, y)
    tot = n * sx2 * sy2                                     # distance class 0: each cell with itself
    edges = np.arange(0, D.max() + width, width)
    for a, b in zip(edges[:-1], edges[1:]):
        m = (D > a) & (D <= b)
        if m.any():
            tot += m.sum() * XX[m].mean() * YY[m].mean()
    var_r = tot / (n * n * sx2 * sy2)
    neff = 1 + 1 / var_r if var_r > 0 else np.nan
    if not np.isfinite(neff) or neff <= 2:
        return r, neff, np.nan
    tval = r * np.sqrt((neff - 2) / (1 - r * r))
    return r, neff, 2 * (1 - tdist.cdf(abs(tval), neff - 2))


def run(d, rich, tag, cell_km):
    d = d.reset_index(drop=True)
    n = len(d)
    D = haversine(d.lat_c.values, d.lon_c.values)
    X = sm.add_constant(pd.DataFrame({c: z(d[c].astype(float)) for c in CTRL}))
    y = sm.OLS(z(d.gpp.astype(float)), X).fit().resid.values
    r = sm.OLS(z(d[rich].astype(float)), X).fit().resid.values
    y = y - y.mean(); r = r - r.mean()
    E, moran, thr = dbmem(D)
    K = E.shape[1]
    print("\n=== spatial scale of the association, %s degree: n = %d ===" % (tag, n))
    print("%d spatial patterns with positive autocorrelation (cells joined up to %.0f km)" % (K, thr))
    ols = (r * y).sum() / (r * r).sum()
    print("all scales together (net of effort and climate): slope %+.3f" % ols)
    print("%-22s %9s %12s %10s %10s %9s %8s %8s %14s" % (
        "band", "patterns", "Moran's I", "patch km", "% of rich", "% of GPP", "slope", "se", "p"))
    bounds = np.linspace(0, K, NBANDS + 1).astype(int)
    names = ["1 broadest", "2", "3", "4 finest"]
    used = np.zeros(n)
    for b in range(NBANDS):
        Eb = E[:, bounds[b]:bounds[b + 1]]
        k = Eb.shape[1]
        ys, rs = Eb.T @ y, Eb.T @ r
        slope = (rs * ys).sum() / (rs * rs).sum()
        res = ys - slope * rs
        se = np.sqrt((res * res).sum() / (k - 1) / (rs * rs).sum())
        p = 2 * (1 - tdist.cdf(abs(slope / se), k - 1))
        patch = zero_crossing_km(Eb @ rs, D, cell_km)
        print("%-22s %9d %5.2f - %4.2f %10.0f %9.1f%% %8.1f%% %+8.3f %8.3f %14.4f" % (
            names[b], k, moran[bounds[b + 1] - 1], moran[bounds[b]], patch,
            100 * (rs * rs).sum() / (r * r).sum(), 100 * (ys * ys).sum() / (y * y).sum(),
            slope, se, p))
        ROWS.append({"grain": tag, "band": names[b], "patterns": k, "patch_km": patch,
                     "share_richness": (rs * rs).sum() / (r * r).sum(),
                     "share_gpp": (ys * ys).sum() / (y * y).sum(), "slope": slope, "se": se, "p": p})
        if b == 0:
            first = (slope, p)
        used += 0
    yr, rr_ = y - E @ (E.T @ y), r - E @ (E.T @ r)
    slope = (rr_ * yr).sum() / (rr_ * rr_).sum()
    res = yr - slope * rr_
    df = n - K - 1 - len(CTRL) - 1
    se = np.sqrt((res * res).sum() / df / (rr_ * rr_).sum())
    p = 2 * (1 - tdist.cdf(abs(slope / se), df))
    print("%-22s %9s %12s %10s %9.1f%% %8.1f%% %+8.3f %8.3f %14.4f" % (
        "no spatial structure", "-", "<= 0", "-", 100 * (rr_ * rr_).sum() / (r * r).sum(),
        100 * (yr * yr).sum() / (y * y).sum(), slope, se, p))
    ROWS.append({"grain": tag, "band": "no spatial structure", "patterns": n - K,
                 "patch_km": np.nan, "share_richness": (rr_ * rr_).sum() / (r * r).sum(),
                 "share_gpp": (yr * yr).sum() / (y * y).sum(), "slope": slope, "se": se, "p": p})
    print("SCALE %s: slope in the broadest band %+.3f (p = %.4f); with no spatial structure "
          "%+.3f (p = %.4f)" % (tag, first[0], first[1], slope, p))

    for label, a, b in (("raw richness and GPP", z(d[rich].astype(float)).values,
                         z(d.gpp.astype(float)).values),
                        ("net of effort and climate", r, y)):
        rho, neff, pv = clifford(a, b, D, cell_km)
        print("NEFF %s, %s: r = %+.3f; %d cells are worth %.0f independent observations; "
              "p = %.4f" % (tag, label, rho, n, neff, pv))
        ROWS.append({"grain": tag, "band": "effective n: " + label, "patterns": n,
                     "slope": rho, "se": neff, "p": pv})


def main():
    m1 = pd.read_csv(os.path.join(DATA, "model_cells.csv"))
    run(m1, "rarefied_250", "1.0", 111.0)
    m5 = pd.read_csv(os.path.join(DATA, "merged_cells_0p5.csv"))
    d5 = m5[m5.gpp.notna() & m5.wc_mode.notna() & ~m5.wc_mode.isin([40, 50, 80])
            & (m5.total_records >= 20) & m5.rarefied.notna() & m5.temp_c.notna()
            & m5.precip_mm_yr.notna()]
    run(d5, "rarefied", "0.5", 55.5)
    pd.DataFrame(ROWS).to_csv(os.path.join(DATA, "scale_bands.csv"), index=False)


if __name__ == "__main__":
    main()
