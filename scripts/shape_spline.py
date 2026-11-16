# -*- coding: utf-8 -*-
"""Extension B, without assuming a parabola: is the relationship curved at all?

extension_b.py compares a straight line with a quadratic. A quadratic can only
bend once and symmetrically, so "no hump" could be an artefact of that shape.
This script lets the data choose the shape:

  1. natural cubic splines of richness with 2, 3 and 4 free parameters,
     against the straight line (AIC, F-test, and block cross-validation, since
     a flexible curve can always fit better in-sample);
  2. a single-breakpoint ("broken stick") model, with the breakpoint searched
     over the middle 80% of the richness range and a permutation p-value that
     accounts for the search;
  3. the slope in the lower, middle and upper third of richness.

Same corrected specification as everywhere else (effort, temperature and
precipitation as controls, standardised), at 1 degree and 0.5 degree.
Writes data/shape_spline_curves.csv (fitted partial curves, for fig 11).
"""
import os
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
from patsy import dmatrix

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
RNG = np.random.default_rng(19)
CTRL = ["log_effort", "temp_c", "precip_mm_yr"]
NPERM = 499
CURVES = []


def z(s):
    return (s - s.mean()) / s.std()


def design(d, rich_cols):
    X = pd.concat([rich_cols.reset_index(drop=True), d[CTRL].reset_index(drop=True)], axis=1)
    X.index = d.index
    return sm.add_constant(X, has_constant="add")


def block_mse(d, make_x, block_deg):
    """Leave-one-block-out mean squared error, each cell weighted equally."""
    blk = (np.floor(d.lat_c / block_deg).astype(int).astype(str) + "_"
           + np.floor(d.lon_c / block_deg).astype(int).astype(str)).values
    y = d.y.values; err = np.empty(len(d))
    X = make_x(d).values
    for b in np.unique(blk):
        te = blk == b
        coef, *_ = np.linalg.lstsq(X[~te], y[~te], rcond=None)
        err[te] = (y[te] - X[te] @ coef) ** 2
    return err.mean()


def best_break(d):
    lo, hi = np.percentile(d.rich, [10, 90])
    best = (np.inf, None)
    for c in np.linspace(lo, hi, 41):
        X = design(d, pd.DataFrame({"rich": d.rich, "hinge": np.clip(d.rich - c, 0, None)}))
        rss = sm.OLS(d.y, X).fit().ssr
        if rss < best[0]:
            best = (rss, c)
    return best


def run(d, tag, block_deg):
    d = d.reset_index(drop=True)
    print("\n=== shape of the relationship, %s degree: n = %d ===" % (tag, len(d)))
    lin = sm.OLS(d.y, design(d, d[["rich"]])).fit()
    cv_lin = block_mse(d, lambda x: design(x, x[["rich"]]), block_deg)
    print("%-26s AIC %8.2f   block-CV MSE %.4f" % ("straight line", lin.aic, cv_lin))
    for df in (2, 3, 4):                         # free richness parameters
        # knots are fixed from the full sample so every CV fold uses the same basis
        B = dmatrix("cr(x, df=%d) - 1" % (df + 1), {"x": d.rich}, return_type="dataframe")
        B.columns = ["s%d" % i for i in range(B.shape[1])]
        Bc = B.iloc[:, 1:]                       # drop one column: basis sums to 1
        sp = sm.OLS(d.y, design(d, Bc)).fit()
        f, p, _ = sp.compare_f_test(lin)
        dd = pd.concat([d, Bc], axis=1)
        cv = block_mse(dd, lambda x, cols=list(Bc.columns): design(x, x[cols]), block_deg)
        print("%-26s AIC %8.2f   block-CV MSE %.4f   dAIC vs line %+6.2f   F-test p = %.4f"
              % ("spline, %d parameters" % df, sp.aic, cv, sp.aic - lin.aic, p))
        if df == 3:
            print("SPLINE %s: 3-parameter spline vs line: dAIC = %+.2f, F-test p = %.4f, "
                  "block-CV MSE %.4f vs %.4f (%s out of sample)"
                  % (tag, sp.aic - lin.aic, p, cv, cv_lin,
                     "spline better" if cv < cv_lin else "line better"))
            grid = np.linspace(d.rich.quantile(0.02), d.rich.quantile(0.98), 60)
            Bg = dmatrix("cr(x, df=4) - 1", {"x": d.rich}, return_type="dataframe")
            info = Bg.design_info
            from patsy import build_design_matrices
            Gm = np.asarray(build_design_matrices([info], {"x": grid})[0])[:, 1:]
            curve = Gm @ sp.params[list(Bc.columns)].values
            line = lin.params["rich"] * grid
            for g, c, l in zip(grid, curve - curve.mean(), line - line.mean()):
                CURVES.append({"grain": tag, "rich_z": g, "spline": c, "line": l})

    rss1, c = best_break(d)
    Xb = design(d, pd.DataFrame({"rich": d.rich, "hinge": np.clip(d.rich - c, 0, None)}))
    bk = sm.OLS(d.y, Xb).fit()
    gain = lin.ssr - rss1
    null = np.empty(NPERM)
    resid = lin.resid.values; fitted = lin.fittedvalues.values
    for k in range(NPERM):                       # permute residuals under the linear null
        dp = d.copy(); dp["y"] = fitted + RNG.permutation(resid)
        l0 = sm.OLS(dp.y, design(dp, dp[["rich"]])).fit().ssr
        null[k] = l0 - best_break(dp)[0]
    p = (1 + (null >= gain).sum()) / (NPERM + 1)
    below, above = bk.params["rich"], bk.params["rich"] + bk.params["hinge"]
    print("BREAK %s: best breakpoint at richness z = %+.2f; slope below %+.3f, above %+.3f; "
          "permutation p (search-adjusted) = %.3f" % (tag, c, below, above, p))

    q = d.rich.quantile([1 / 3, 2 / 3]).values
    for name, m in (("lower third", d.rich <= q[0]), ("middle third", (d.rich > q[0]) & (d.rich <= q[1])),
                    ("upper third", d.rich > q[1])):
        s = d[m]
        f = sm.OLS(s.y, design(s, s[["rich"]])).fit(cov_type="HC3")
        print("  slope in the %-13s n=%-4d beta %+.3f  se %.3f  p = %.3f"
              % (name, len(s), f.params["rich"], f.bse["rich"], f.pvalues["rich"]))
    # A flexible curve can dip at its upper end without the data declining there.
    # The direct check for a hump: is the slope negative among the richest cells?
    tail = []
    for share in (0.25, 0.15, 0.10):
        s = d[d.rich > d.rich.quantile(1 - share)]
        f = sm.OLS(s.y, design(s, s[["rich"]])).fit(cov_type="HC3")
        tail.append(f.params["rich"])
        print("  slope among the richest %2.0f%% n=%-4d beta %+.3f  se %.3f  p = %.3f"
              % (100 * share, len(s), f.params["rich"], f.bse["rich"], f.pvalues["rich"]))
    print("TAIL %s: slope among the richest quarter %+.3f; negative in %d of 3 upper-tail "
          "subsets -> %s" % (tag, tail[0], sum(t < 0 for t in tail),
                             "no decline at high richness" if all(t > 0 for t in tail)
                             else "a decline at high richness cannot be ruled out"))


def main():
    m1 = pd.read_csv(os.path.join(DATA, "model_cells.csv"))
    d1 = pd.DataFrame({"y": z(m1.gpp), "rich": z(m1.rarefied_250), "lat_c": m1.lat_c,
                       "lon_c": m1.lon_c, **{c: z(m1[c]) for c in CTRL}})
    run(d1, "1.0", 4.0)
    m5 = pd.read_csv(os.path.join(DATA, "merged_cells_0p5.csv"))
    m5 = m5[m5.gpp.notna() & m5.wc_mode.notna() & ~m5.wc_mode.isin([40, 50, 80])
            & (m5.total_records >= 20) & m5.rarefied.notna() & m5.temp_c.notna()
            & m5.precip_mm_yr.notna()]
    d5 = pd.DataFrame({"y": z(m5.gpp), "rich": z(m5.rarefied), "lat_c": m5.lat_c,
                       "lon_c": m5.lon_c, **{c: z(m5[c]) for c in CTRL}})
    run(d5, "0.5", 4.0)
    pd.DataFrame(CURVES).to_csv(os.path.join(DATA, "shape_spline_curves.csv"), index=False)


if __name__ == "__main__":
    main()
