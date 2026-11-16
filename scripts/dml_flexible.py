# -*- coding: utf-8 -*-
"""Does the richness coefficient survive flexible, non-linear controls?

Every model so far controls for climate with straight lines. If productivity or
richness responds to temperature and rainfall in a curved or interacting way,
linear controls leave part of the climate signal in the richness coefficient. A
reviewer's first question about the cross-regional result is therefore: is +0.27
just imperfectly controlled climate?

Double/debiased machine learning (Chernozhukov et al. 2018) answers it for the
partially linear model  GPP = theta * richness + g(controls) + noise :

  1. predict GPP from the controls with a flexible learner, out of fold;
  2. predict richness from the controls the same way;
  3. regress the GPP residuals on the richness residuals: that slope is theta.

Controls: survey effort, temperature, precipitation, mean elevation, topographic
heterogeneity and NDVI seasonality. In the "within ecoregions" version each
ecoregion's mean is first removed from GPP and from richness.
Learners: random forest and gradient boosting, plus ordinary least squares as a
check that the procedure reproduces the linear answer. Folds are spatial blocks
of 4 degrees, so a cell is never predicted from its own neighbours; the split is
repeated REPS times and the estimates combined by the median rule. Standard
errors are clustered by ecoregion.

At 1 degree and 0.5 degree. Cached data only.
Writes data/dml_estimates.csv.
"""
import os
import warnings

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from scipy.stats import norm

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
X_COLS = ["log_effort", "temp_c", "precip_mm_yr", "elev_mean", "elev_sd", "ndvi_cv"]
REPS = 5
FOLDS = 5
BLOCK = 4.0
EST = []


def z(s):
    return (s - s.mean()) / s.std()


def learner(name, seed):
    if name == "linear":
        return LinearRegression()
    if name == "random forest":
        return RandomForestRegressor(n_estimators=300, min_samples_leaf=5, max_features=0.5,
                                     random_state=seed, n_jobs=-1)
    return GradientBoostingRegressor(n_estimators=300, max_depth=3, learning_rate=0.05,
                                     subsample=0.8, random_state=seed)


def crossfit(y, d, X, blocks, name, seed):
    rng = np.random.default_rng(seed)
    ub = np.unique(blocks)
    fold_of = dict(zip(ub, rng.permutation(len(ub)) % FOLDS))
    fold = np.array([fold_of[b] for b in blocks])
    ry = np.empty(len(y)); rd = np.empty(len(y))
    for k in range(FOLDS):
        te = fold == k
        ry[te] = y[te] - learner(name, seed).fit(X[~te], y[~te]).predict(X[te])
        rd[te] = d[te] - learner(name, seed).fit(X[~te], d[~te]).predict(X[te])
    return ry, rd


def theta_se(ry, rd, groups):
    th = (rd * ry).sum() / (rd * rd).sum()
    e = ry - th * rd
    score = pd.Series(rd * e).groupby(groups).sum().values       # clustered by ecoregion
    g = len(score)
    se = np.sqrt((score ** 2).sum() * g / (g - 1)) / (rd * rd).sum()
    return th, se


def run(d, rich, tag):
    d = d.dropna(subset=X_COLS + ["eco_name"]).reset_index(drop=True)
    y = z(d.gpp.astype(float)).values; r = z(d[rich].astype(float)).values
    Xe = np.column_stack([z(d[c].astype(float)).values for c in X_COLS])
    # Within ecoregions: remove each ecoregion's mean from GPP and richness first.
    # (Ecoregion dummies cannot be learned out of fold when whole spatial blocks,
    # and so whole ecoregions, are held out; demeaning does not have that problem.)
    yw = y - pd.Series(y).groupby(d.eco_name.values).transform("mean").values
    rw = r - pd.Series(r).groupby(d.eco_name.values).transform("mean").values
    blocks = (np.floor(d.lat_c / BLOCK).astype(int).astype(str) + "_"
              + np.floor(d.lon_c / BLOCK).astype(int).astype(str)).values
    groups = d.eco_name.values
    print("\n=== flexible controls, %s degree: n = %d, %d spatial blocks ===" % (tag, len(d),
                                                                                len(set(blocks))))
    print("%-18s %-16s %9s %8s %9s %12s %12s" % ("controls", "learner", "theta", "se", "p",
                                                 "R2 of GPP", "R2 of rich."))
    for label, yy, rr in (("environment", y, r), ("within ecoregions", yw, rw)):
        X = Xe
        for name in ("linear", "random forest", "gradient boosting"):
            ths, ses, r2y, r2d = [], [], [], []
            for rep in range(REPS):
                ry, rd = crossfit(yy, rr, X, blocks, name, 100 + rep)
                th, se = theta_se(ry, rd, groups)
                ths.append(th); ses.append(se)
                r2y.append(1 - (ry ** 2).sum() / ((yy - yy.mean()) ** 2).sum())
                r2d.append(1 - (rd ** 2).sum() / ((rr - rr.mean()) ** 2).sum())
            th = float(np.median(ths))
            se = float(np.sqrt(np.median(np.array(ses) ** 2 + (np.array(ths) - th) ** 2)))
            p = 2 * (1 - norm.cdf(abs(th / se)))
            print("%-18s %-16s %+9.3f %8.3f %9.4f %12.3f %12.3f"
                  % (label, name, th, se, p, np.median(r2y), np.median(r2d)))
            EST.append({"grain": tag, "controls": label, "learner": name, "theta": th, "se": se,
                        "p": p, "r2_gpp": float(np.median(r2y)),
                        "r2_richness": float(np.median(r2d)), "n": len(d)})
            if name == "random forest":
                print("DML %s %s, random forest: theta = %+.3f (se %.3f, p = %.4f)"
                      % (tag, label, th, se, p))


def main():
    m1 = pd.read_csv(os.path.join(DATA, "model_cells.csv"))
    c1 = pd.read_csv(os.path.join(DATA, "confounders_1p0.csv"))
    e1 = pd.read_csv(os.path.join(DATA, "ecoregions_1p0.csv"))[["cell_id", "eco_name"]]
    run(m1.merge(c1, on="cell_id").merge(e1, on="cell_id", how="left"), "rarefied_250", "1.0")

    m5 = pd.read_csv(os.path.join(DATA, "merged_cells_0p5.csv"))
    c5 = pd.read_csv(os.path.join(DATA, "confounders_0p5.csv"))[["cell_id", "elev_mean",
                                                                 "elev_sd", "ndvi_cv"]]
    e5 = pd.read_csv(os.path.join(DATA, "ecoregions_0p5.csv"))[["cell_id", "eco_name"]]
    d5 = m5[m5.gpp.notna() & m5.wc_mode.notna() & ~m5.wc_mode.isin([40, 50, 80])
            & (m5.total_records >= 20) & m5.rarefied.notna() & m5.temp_c.notna()
            & m5.precip_mm_yr.notna()]
    run(d5.merge(c5, on="cell_id").merge(e5, on="cell_id", how="left"), "rarefied", "0.5")
    pd.DataFrame(EST).to_csv(os.path.join(DATA, "dml_estimates.csv"), index=False)


if __name__ == "__main__":
    main()
