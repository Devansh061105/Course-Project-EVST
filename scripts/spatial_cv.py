# -*- coding: utf-8 -*-
"""Spatial block cross-validation with correct inference.

Does adding effort-corrected richness to a climate+effort model improve
OUT-OF-SAMPLE prediction of GPP when whole spatial blocks are held out?

Inference: each held-out cell contributes d_i = e0_i^2 - e1_i^2 (squared-error
reduction from adding richness). Cells are summed within their block, and blocks
are resampled with replacement. This weights every cell equally while respecting
spatial dependence within blocks. The earlier version averaged per-fold RMSE,
which weights a 1-cell block like a 15-cell block and let tiny noisy folds
dominate - its "no reliable gain" verdict contradicted the pooled RMSE and is
superseded by this script.
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
RICH = "rarefied_250"
BASE = ["log_effort", "temp_c", "precip_mm_yr"]
RNG = np.random.default_rng(7)
NBOOT = 5000


def fit_predict(tr, te, cols, y="gpp"):
    Xtr = np.column_stack([np.ones(len(tr))] + [tr[c].values for c in cols])
    Xte = np.column_stack([np.ones(len(te))] + [te[c].values for c in cols])
    b, *_ = np.linalg.lstsq(Xtr, tr[y].values, rcond=None)
    return Xte @ b


def oos(d, folds, cols):
    p = np.full(len(d), np.nan)
    for f in np.unique(folds):
        te = folds == f
        p[te] = fit_predict(d[~te], d[te], cols)
    return p


def evaluate(d, folds, label, extra_sets=None):
    y = d.gpp.values
    p0 = oos(d, folds, BASE)
    p1 = oos(d, folds, BASE + [RICH])
    e0, e1 = (y - p0) ** 2, (y - p1) ** 2
    sst = np.sum((y - y.mean()) ** 2)
    r2_0, r2_1 = 1 - e0.sum() / sst, 1 - e1.sum() / sst

    # block bootstrap of the MSE reduction, cells weighted equally
    blocks = pd.Series(e0 - e1).groupby(folds).sum().values
    nblk = pd.Series(np.ones(len(d))).groupby(folds).sum().values
    reps = np.empty(NBOOT)
    for k in range(NBOOT):
        idx = RNG.integers(0, len(blocks), len(blocks))
        reps[k] = blocks[idx].sum() / nblk[idx].sum()
    lo, hi = np.percentile(reps, [2.5, 97.5])
    dmse = (e0 - e1).mean()
    rel = 100 * dmse / e0.mean()
    print("%-30s R2oos %.3f -> %.3f  dMSE %+.4f (%+.1f%%)  95%% CI [%+.4f, %+.4f]  %s"
          % (label, r2_0, r2_1, dmse, rel, lo, hi,
             "richness HELPS" if lo > 0 else "no reliable gain"))
    return dmse, lo, hi


def main():
    d = pd.read_csv(os.path.join(DATA, "model_cells.csv")).reset_index(drop=True)
    print("n = %d cells, 1-degree grid\n" % len(d))

    # random 10-fold, single partition for the same bootstrap machinery
    # (blocks of size ~1: equivalent to a cell-level bootstrap)
    folds = RNG.permutation(np.arange(len(d)) % 10)
    evaluate(d, np.arange(len(d)), "leave-one-cell-out")
    evaluate(d, folds, "random 10-fold")
    for B in (2.0, 3.0, 4.0, 6.0, 8.0):
        blk = pd.factorize(np.floor(d.lat_c / B).astype(int).astype(str) + "_"
                           + np.floor(d.lon_c / B).astype(int).astype(str))[0]
        evaluate(d, blk, "leave-block-out %.0f deg (%d blk)" % (B, blk.max() + 1))

    # Buffered LOO: hold out one cell AND drop its neighbours within r degrees
    # from training, so no near-duplicate neighbour leaks information.
    print("\nbuffered leave-one-out (training excludes cells within r of the test cell):")
    y = d.gpp.values
    for r in (1.5, 3.0, 5.0):
        p0 = np.empty(len(d)); p1 = np.empty(len(d))
        for i in range(len(d)):
            dist = np.hypot(d.lat_c - d.lat_c[i], d.lon_c - d.lon_c[i])
            tr = d[dist > r]
            te = d.iloc[[i]]
            p0[i] = fit_predict(tr, te, BASE)[0]
            p1[i] = fit_predict(tr, te, BASE + [RICH])[0]
        e0, e1 = (y - p0) ** 2, (y - p1) ** 2
        # bootstrap over 4-degree blocks for the CI
        blk = pd.factorize(np.floor(d.lat_c / 4).astype(int).astype(str) + "_"
                           + np.floor(d.lon_c / 4).astype(int).astype(str))[0]
        sb = pd.Series(e0 - e1).groupby(blk).sum().values
        nb = pd.Series(np.ones(len(d))).groupby(blk).sum().values
        reps = [sb[ix].sum() / nb[ix].sum()
                for ix in (RNG.integers(0, len(sb), len(sb)) for _ in range(NBOOT))]
        lo, hi = np.percentile(reps, [2.5, 97.5])
        sst = np.sum((y - y.mean()) ** 2)
        print("  r=%.1f deg   R2oos %.3f -> %.3f  dMSE %+.4f (%+.1f%%)  CI [%+.4f, %+.4f]  %s"
              % (r, 1 - e0.sum() / sst, 1 - e1.sum() / sst, (e0 - e1).mean(),
                 100 * (e0 - e1).mean() / e0.mean(), lo, hi,
                 "HELPS" if lo > 0 else "no reliable gain"))


if __name__ == "__main__":
    main()
