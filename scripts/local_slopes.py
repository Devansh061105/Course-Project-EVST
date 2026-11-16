# -*- coding: utf-8 -*-
"""Extension C, quantified: does the richness-productivity slope hold everywhere?

Geographically weighted regression (GWR; Brunsdon, Fotheringham & Charlton 1996)
of the corrected model

    gpp ~ rarefied richness + log10(effort) + temperature + precipitation

(all standardised over the whole sample, so local slopes are on the same scale
as the global beta). One weighted regression per cell, adaptive bisquare kernel
over the k nearest modelled cells, k chosen by AICc. Implemented directly in
numpy; no GWR package is required.

Reported honestly, because GWR over-reads easily:
  * AICc of GWR against the global OLS (is local variation worth its parameters?)
  * Monte Carlo stationarity test: shuffle the cells' locations and ask whether
    the observed spread of local slopes exceeds what location-free data give
  * local t-tests at the da Silva & Fotheringham (2016) adjusted alpha, which
    corrects for the many dependent local tests
  * local condition numbers (Wheeler & Tiefelsdorf 2005: local collinearity can
    manufacture slope patterns); cells above 30 are flagged

Run at 1 degree (primary) and 0.5 degree (replication).
Writes data/local_slopes_1p0.csv, data/local_slopes_0p5.csv and
data/local_slopes_profile.csv (median local slope at every candidate bandwidth:
how the slope grows as the window widens from a neighbourhood to the region).
"""
import os
import warnings

import numpy as np
import pandas as pd
from scipy.stats import t as tdist

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
CTRL = ["log_effort", "temp_c", "precip_mm_yr"]
CASES = {"Western Ghats": (8, 16, 74, 77), "Thar Desert": (25, 30, 69, 74),
         "Eastern Himalaya": (26, 29, 88, 97)}
N_PERM = 499
PROFILE = []          # slope summary at every candidate bandwidth (for fig 9c)
RNG = np.random.default_rng(97)


def z(s):
    return (s - s.mean()) / s.std()


def haversine_km(lat, lon):
    la = np.radians(lat)[:, None]; lo = np.radians(lon)[:, None]
    a = (np.sin((la - la.T) / 2) ** 2
         + np.cos(la) * np.cos(la.T) * np.sin((lo - lo.T) / 2) ** 2)
    return 6371.0 * 2 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def kernel(D, k):
    """Adaptive bisquare: bandwidth at each cell = distance to its k-th neighbour."""
    b = np.sort(D, axis=1)[:, k][:, None]
    W = (1 - (D / b) ** 2) ** 2
    W[D >= b] = 0.0
    return W, b.ravel()


def gwr(y, X, W, full=True):
    n, p = X.shape
    B = np.empty((n, p)); S = np.empty((n, n)) if full else None
    cc = np.empty((n, p)); cond = np.empty(n)
    for i in range(n):
        w = W[i]
        Xw = X * w[:, None]
        C = np.linalg.solve(X.T @ Xw, Xw.T)          # p x n
        B[i] = C @ y
        if full:
            S[i] = X[i] @ C
            cc[i] = (C ** 2).sum(axis=1)
            Xs = X[w > 0] * np.sqrt(w[w > 0])[:, None]
            Xs = Xs / np.sqrt((Xs ** 2).sum(axis=0))  # Belsley column scaling
            sv = np.linalg.svd(Xs, compute_uv=False)
            cond[i] = sv[0] / sv[-1]
    if not full:
        return B
    resid = y - S @ y
    rss = float(resid @ resid)
    tr = np.trace(S); trss = float((S * S).sum())
    sigma2 = rss / (n - 2 * tr + trss)
    aicc = n * np.log(rss / n) + n * np.log(2 * np.pi) + n * (n + tr) / (n - 2 - tr)
    return {"B": B, "se": np.sqrt(cc * sigma2), "enp": tr, "aicc": aicc,
            "rss": rss, "cond": cond, "resid": resid}


def ols_aicc(y, X):
    n, p = X.shape
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    rss = float(((y - X @ b) ** 2).sum())
    return b, n * np.log(rss / n) + n * np.log(2 * np.pi) + n * (n + p) / (n - 2 - p)


def run(d, rich, tag, cell, k_grid):
    d = d.reset_index(drop=True)
    y = z(d.gpp.astype(float)).values
    X = np.column_stack([np.ones(len(d))] + [z(d[c].astype(float)).values
                                             for c in [rich] + CTRL])
    n, p = X.shape
    D = haversine_km(d.lat_c.values, d.lon_c.values)
    b_ols, aicc_ols = ols_aicc(y, X)

    best = None
    for k in k_grid:
        if k >= n:
            break
        W, bw = kernel(D, k)
        f = gwr(y, X, W)
        qs = np.percentile(f["B"][:, 1], [25, 50, 75])
        PROFILE.append({"grain": tag, "k": k, "bandwidth_km": float(np.median(bw)),
                        "aicc": f["aicc"], "enp": f["enp"], "beta_q25": qs[0],
                        "beta_median": qs[1], "beta_q75": qs[2],
                        "global_beta": b_ols[1]})
        if best is None or f["aicc"] < best[1]["aicc"]:
            best = (k, f, W, bw)
    k, f, W, bw = best
    beta = f["B"][:, 1]; tval = beta / f["se"][:, 1]
    alpha_adj = 0.05 / (f["enp"] / p)
    tcrit = tdist.ppf(1 - alpha_adj / 2, n - f["enp"])
    sig = np.abs(tval) > tcrit

    # Monte Carlo stationarity: break the link between data and location.
    obs_sd = beta.std()
    null = np.empty(N_PERM)
    for r in range(N_PERM):
        ix = RNG.permutation(n)
        null[r] = gwr(y[ix], X[ix], W, full=False)[:, 1].std()
    p_mc = (1 + (null >= obs_sd).sum()) / (N_PERM + 1)

    print("\n=== GWR %s deg: n=%d ===" % (tag, n))
    print("global OLS richness beta = %+.3f   AICc OLS = %.1f" % (b_ols[1], aicc_ols))
    print("GWR %s: k = %d neighbours (median bandwidth %.0f km)  ENP = %.1f  AICc GWR = %.1f"
          % (tag, k, np.median(bw), f["enp"], f["aicc"]))
    print("GWR %s: AICc gain over OLS = %.1f" % (tag, aicc_ols - f["aicc"]))
    q = np.percentile(beta, [0, 25, 50, 75, 100])
    print("GWR %s: local richness beta min %+.3f  q25 %+.3f  median %+.3f  q75 %+.3f  max %+.3f"
          % ((tag,) + tuple(q)))
    print("GWR %s: local beta > 0 in %.1f%% of cells" % (tag, 100 * (beta > 0).mean()))
    print("GWR %s: adjusted alpha = %.4f (t crit %.2f); significant positive %d, negative %d, of %d"
          % (tag, alpha_adj, tcrit, (sig & (beta > 0)).sum(), (sig & (beta < 0)).sum(), n))
    print("GWR %s: stationarity Monte Carlo (SD of local beta %.3f vs null median %.3f): p = %.3f"
          % (tag, obs_sd, np.median(null), p_mc))
    print("GWR %s: local condition number median %.1f, max %.1f, cells > 30: %d"
          % (tag, np.median(f["cond"]), f["cond"].max(), (f["cond"] > 30).sum()))

    out = d[["cell_id", "lat_c", "lon_c"]].copy()
    out["local_beta_richness"] = beta
    out["local_se"] = f["se"][:, 1]
    out["local_t"] = tval
    out["sig_adjusted"] = sig.astype(int)
    out["local_cond"] = f["cond"]
    out["bandwidth_km"] = bw
    for j, c in enumerate(CTRL, start=2):
        out["local_beta_" + c] = f["B"][:, j]
    out["case_study"] = ""
    for name, (a, b_, c_, e_) in CASES.items():
        m = (out.lat_c.between(a, b_) & out.lon_c.between(c_, e_))
        out.loc[m, "case_study"] = name
    if "eco_name" in d:
        out["eco_name"] = d.eco_name.values

    print("local richness slope by case-study region (%s deg):" % tag)
    for name in CASES:
        s = out[out.case_study == name]
        if len(s):
            print("  %-17s cells %-3d median %+.3f  range %+.3f to %+.3f  significant %d"
                  % (name, len(s), s.local_beta_richness.median(),
                     s.local_beta_richness.min(), s.local_beta_richness.max(),
                     s.sig_adjusted.sum()))
    if "eco_name" in out:
        g = (out.dropna(subset=["eco_name"]).groupby("eco_name").local_beta_richness
             .agg(["size", "median"]).query("size >= 8").sort_values("median"))
        print("ecoregions with >= 8 cells, by median local slope (%s deg):" % tag)
        for name, r in g.iterrows():
            print("  %-58s n=%-3d median %+.3f" % (name[:58], r["size"], r["median"]))
        btw = out.dropna(subset=["eco_name"])
        gm = btw.groupby("eco_name").local_beta_richness.transform("mean")
        share = ((gm - btw.local_beta_richness.mean()) ** 2).sum() / (
            (btw.local_beta_richness - btw.local_beta_richness.mean()) ** 2).sum()
        print("GWR %s: share of local-slope variance between ecoregions = %.1f%%"
              % (tag, 100 * share))
    out.to_csv(os.path.join(DATA, "local_slopes_%s.csv" % tag.replace(".", "p")),
               index=False)
    return out


def main():
    m1 = pd.read_csv(os.path.join(DATA, "model_cells.csv"))
    e1 = pd.read_csv(os.path.join(DATA, "ecoregions_1p0.csv"))
    d1 = m1.merge(e1[["cell_id", "eco_name"]], on="cell_id", how="left")
    run(d1, "rarefied_250", "1.0", 1.0, range(20, 221, 4))

    m5 = pd.read_csv(os.path.join(DATA, "merged_cells_0p5.csv"))
    e5 = pd.read_csv(os.path.join(DATA, "ecoregions_0p5.csv"))
    d5 = m5[m5.gpp.notna() & m5.wc_mode.notna() & ~m5.wc_mode.isin([40, 50, 80])
            & (m5.total_records >= 20) & m5["rarefied"].notna()
            & m5.temp_c.notna() & m5.precip_mm_yr.notna()].copy()
    d5 = d5.merge(e5[["cell_id", "eco_name"]], on="cell_id", how="left")
    run(d5, "rarefied", "0.5", 0.5, range(30, 671, 10))
    pd.DataFrame(PROFILE).to_csv(os.path.join(DATA, "local_slopes_profile.csv"),
                                 index=False)


if __name__ == "__main__":
    main()
