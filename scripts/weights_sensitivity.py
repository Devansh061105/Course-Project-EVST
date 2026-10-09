# -*- coding: utf-8 -*-
"""Plan Step 8: does the null survive a different spatial weights matrix?

The null result rests on ML_Error with distance-band weights at 1.5 degrees.
That threshold was a judgement call, so this refits the same specification under
queen contiguity, several distance bands and several k-nearest-neighbour
matrices, and reports what happens to the rarefied-richness coefficient each
time.
"""
import os
import sys
import warnings

import numpy as np
import pandas as pd
import libpysal
import esda
from libpysal.weights import W, DistanceBand, KNN
from scipy.stats import norm
from spreg import ML_Error, ML_Lag, OLS as sOLS

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))

X_COLS = ["rarefied_250", "log_effort", "temp_c", "precip_mm_yr"]
RI = X_COLS.index("rarefied_250") + 1          # +1 for the constant


def queen_from_grid(lats, lons, cell=1.0, tol=1e-6):
    """Queen contiguity for a regular lattice given cell centroids: neighbours
    are cells whose centroids differ by at most one cell in each axis."""
    n = len(lats)
    neigh = {i: [] for i in range(n)}
    for i in range(n):
        dlat = np.abs(lats - lats[i])
        dlon = np.abs(lons - lons[i])
        hit = np.where((dlat <= cell + tol) & (dlon <= cell + tol))[0]
        neigh[i] = [int(j) for j in hit if j != i]
    return W(neigh, silence_warnings=True)


def run(d, w, label, cell=1.0):
    y = d["gpp"].astype(float).values.reshape(-1, 1)
    X = d[X_COLS].astype(float).values
    w.transform = "r"
    try:
        ols = sOLS(y, X, w=w, spat_diag=True, moran=True)
        mi_ols = ols.moran_res[0]
        rlm_lag, rlm_err = ols.rlm_lag[0], ols.rlm_error[0]
        err = ML_Error(y, X, w=w)
        lag = ML_Lag(y, X, w=w)
        b = float(err.betas[RI][0])
        se = float(np.sqrt(err.vm[RI, RI]))
        p = 2 * (1 - norm.cdf(abs(b / se)))
        mi_f = esda.Moran(np.asarray(err.e_filtered).flatten(), w,
                          permutations=499)
        better = "error" if err.aic < lag.aic else "lag"
        print("%-26s %5d %7.3f %7.1f %7.1f %6s %+10.5f %9.4f %8.3f %7.3f"
              % (label, w.n, mi_ols, rlm_lag, rlm_err, better, b, p,
                 mi_f.I, mi_f.p_sim))
        return p
    except Exception as e:
        print("%-26s FAILED: %s" % (label, str(e)[:60]))
        return None


def main():
    d = pd.read_csv(os.path.join(DATA, "model_cells.csv"))
    lats, lons = d.lat_c.values, d.lon_c.values
    coords = list(zip(lons, lats))
    print("n = %d cells\n" % len(d))
    print("%-26s %5s %7s %7s %7s %6s %10s %9s %8s %7s" % (
        "weights", "n", "MoranI", "rLMlag", "rLMerr", "AICwin",
        "beta_rich", "p_rich", "resMorI", "p_res"))
    print("-" * 104)

    ps = {}
    ps["queen"] = run(d, queen_from_grid(lats, lons, 1.0), "queen contiguity")
    for t in (1.0, 1.5, 2.0, 2.5, 3.0):
        ps["db%.1f" % t] = run(
            d, DistanceBand(coords, threshold=t, binary=True,
                            silence_warnings=True), "distance band %.1f deg" % t)
    for k in (4, 6, 8, 12):
        ps["knn%d" % k] = run(d, KNN(coords, k=k), "k-nearest neighbours k=%d" % k)

    ok = {k: v for k, v in ps.items() if v is not None}
    print("\n%d/%d weights specifications ran" % (len(ok), len(ps)))
    sig = [k for k, v in ok.items() if v < 0.05]
    print("richness significant (p<0.05) under: %s" % (sig if sig else "NONE"))
    print("p range: %.4f to %.4f" % (min(ok.values()), max(ok.values())))


if __name__ == "__main__":
    main()
