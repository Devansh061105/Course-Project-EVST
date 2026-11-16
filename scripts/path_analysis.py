# -*- coding: utf-8 -*-
"""Which way does the richness-productivity link run? A path analysis.

H1 as written has biodiversity driving productivity. Species-energy theory has
productivity driving bird richness. With one snapshot in time the two cannot be
told apart from model fit: the path models "richness -> GPP" and "GPP -> richness"
are statistically equivalent once both include climate. This script says so with
numbers, and then uses the one handle the data offer.

  1. Path coefficients for both directions, with bootstrap intervals, and a
     decomposition of the raw richness-GPP correlation into the part shared
     through climate and the part left as a direct link.
  2. The "common cause only" model (climate drives both, no link): tested by the
     partial correlation of richness and GPP given climate and effort.
  3. A discriminating test using topographic heterogeneity (SD of elevation), a
     classic driver of richness with no obvious direct effect on productivity
     once temperature and rainfall are held fixed:
        richness -> GPP  predicts  heterogeneity and GPP are related given climate
        GPP -> richness  predicts  they are unrelated given climate
     Reported as (a) the partial correlation, (b) Shipley's d-separation test for
     each model, (c) a two-stage least squares estimate with heterogeneity as the
     instrument. All three rest on the same untestable assumption (heterogeneity
     affects GPP only through richness), so they are evidence, not proof.

Run at 1 degree (221 cells) and 0.5 degree (about 670 cells). Standardised
variables throughout. Writes data/path_analysis_estimates.csv.
"""
import os
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import chi2
from statsmodels.sandbox.regression.gmm import IV2SLS

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
RNG = np.random.default_rng(73)
NBOOT = 2000
EST = []


def z(s):
    return (s - s.mean()) / s.std()


def fit(d, y, cols, cluster=True):
    X = sm.add_constant(d[cols])
    if cluster and "eco_name" in d and d.eco_name.notna().all():
        return sm.OLS(d[y], X).fit(cov_type="cluster", cov_kwds={"groups": d.eco_name})
    return sm.OLS(d[y], X).fit(cov_type="HC3")


def beta(d, y, cols, target):
    X = np.column_stack([np.ones(len(d))] + [d[c].values for c in cols])
    b, *_ = np.linalg.lstsq(X, d[y].values, rcond=None)
    return b[1 + cols.index(target)]


def boot(d, y, cols, target):
    n = len(d)
    v = [beta(d.iloc[RNG.integers(0, n, n)], y, cols, target) for _ in range(NBOOT)]
    return np.percentile(v, [2.5, 97.5])


def partial_r(d, a, b, given):
    ra = sm.OLS(d[a], sm.add_constant(d[given])).fit().resid
    rb = sm.OLS(d[b], sm.add_constant(d[given])).fit().resid
    return np.corrcoef(ra, rb)[0, 1]


def record(tag, what, est, lo=np.nan, hi=np.nan, p=np.nan):
    EST.append({"grain": tag, "quantity": what, "estimate": est, "lo": lo, "hi": hi, "p": p})


def run(d, tag):
    R, G, T, P, E, H = "rich", "gpp", "temp", "precip", "effort", "het"
    print("\n=== path analysis, %s degree: n = %d ===" % (tag, len(d)))

    # 1. both directions
    r_rg = np.corrcoef(d[R], d[G])[0, 1]
    b_gr = beta(d, G, [R, E, T, P], R); ci1 = boot(d, G, [R, E, T, P], R)
    b_rg = beta(d, R, [G, E, T, P], G); ci2 = boot(d, R, [G, E, T, P], G)
    print("raw correlation richness-GPP: r = %+.3f" % r_rg)
    print("PATH %s: richness -> GPP | climate, effort   beta = %+.3f  [%+.3f, %+.3f]"
          % (tag, b_gr, ci1[0], ci1[1]))
    print("PATH %s: GPP -> richness | climate, effort   beta = %+.3f  [%+.3f, %+.3f]"
          % (tag, b_rg, ci2[0], ci2[1]))
    r2a = fit(d, G, [R, E, T, P], False).rsquared + fit(d, R, [E, T, P], False).rsquared
    r2b = fit(d, R, [G, E, T, P], False).rsquared + fit(d, G, [E, T, P], False).rsquared
    print("the two directions are equivalent in fit: both reproduce the same partial "
          "correlation (sum of equation R2 %.3f vs %.3f is not a test)" % (r2a, r2b))
    record(tag, "richness -> GPP path", b_gr, ci1[0], ci1[1])
    record(tag, "GPP -> richness path", b_rg, ci2[0], ci2[1])
    shared = r_rg - b_gr
    print("DECOMP %s: of r = %.3f, direct link %.3f (%.0f%%), shared through climate "
          "and effort %.3f (%.0f%%)" % (tag, r_rg, b_gr, 100 * b_gr / r_rg, shared,
                                        100 * shared / r_rg))
    record(tag, "share of raw correlation due to shared climate", shared / r_rg)

    # 2. common cause only
    pr = partial_r(d, R, G, [T, P, E])
    m = fit(d, G, [R, E, T, P])
    print("COMMON-CAUSE %s: partial r(richness, GPP | climate, effort) = %+.3f, "
          "p = %.4f (SEs clustered by ecoregion) -> %s"
          % (tag, pr, m.pvalues[R], "rejected" if m.pvalues[R] < 0.05 else "not rejected"))
    record(tag, "partial r richness-GPP given climate", pr, p=m.pvalues[R])

    # 3. heterogeneity as the discriminating variable
    print("topographic heterogeneity: r with richness %+.3f, with GPP %+.3f"
          % (np.corrcoef(d[H], d[R])[0, 1], np.corrcoef(d[H], d[G])[0, 1]))
    first = fit(d, R, [H, E, T, P])
    print("  heterogeneity -> richness | climate, effort: beta = %+.3f, p = %.4f"
          % (first.params[H], first.pvalues[H]))
    a = fit(d, G, [H, E, T, P])           # claim of 'GPP -> richness': H indep GPP | climate
    b = fit(d, G, [H, R, E, T, P])        # claim of 'richness -> GPP': H indep GPP | richness, climate
    print("DSEP %s: model 'GPP -> richness' claims heterogeneity is unrelated to GPP given "
          "climate: beta = %+.3f, p = %.4f" % (tag, a.params[H], a.pvalues[H]))
    print("DSEP %s: model 'richness -> GPP' claims heterogeneity is unrelated to GPP given "
          "richness and climate: beta = %+.3f, p = %.4f" % (tag, b.params[H], b.pvalues[H]))
    for name, mm in (("GPP -> richness", a), ("richness -> GPP", b)):
        C = -2 * np.log(max(mm.pvalues[H], 1e-300))
        print("  Fisher's C for '%s': C = %.2f, df = 2, p = %.4f (small p = model rejected)"
              % (name, C, 1 - chi2.cdf(C, 2)))
        record(tag, "d-sep p, model " + name, mm.params[H], p=mm.pvalues[H])
    exog = sm.add_constant(d[[R, E, T, P]]); inst = sm.add_constant(d[[H, E, T, P]])
    iv = IV2SLS(d[G], exog, inst).fit()
    f1 = (first.params[H] / first.bse[H]) ** 2
    lo, hi = iv.params[R] - 1.96 * iv.bse[R], iv.params[R] + 1.96 * iv.bse[R]
    print("IV %s: richness -> GPP with heterogeneity as instrument: beta = %+.3f "
          "[%+.3f, %+.3f], p = %.4f; first-stage F = %.1f (%s)"
          % (tag, iv.params[R], lo, hi, iv.pvalues[R], f1,
             "adequate" if f1 >= 10 else "WEAK instrument, estimate unreliable"))
    if b.pvalues[H] < 0.05:
        print("IV %s VERDICT: not valid. Heterogeneity still predicts GPP with richness "
              "held fixed (p = %.4f), so it does not act only through richness; the IV "
              "estimate is %.1f times the OLS one, which is the signature of a bad "
              "instrument. Direction stays unidentified."
              % (tag, b.pvalues[H], iv.params[R] / b_gr))
    record(tag, "IV richness -> GPP", iv.params[R], lo, hi, iv.pvalues[R])
    record(tag, "IV first-stage F", f1)

    # within ecoregions
    de = d.dropna(subset=["eco_name"])
    D = pd.get_dummies(de.eco_name, prefix="fe", drop_first=True, dtype=float)
    X = pd.concat([de[[H, E, T, P]], D], axis=1)
    w = sm.OLS(de[G], sm.add_constant(X)).fit(cov_type="cluster",
                                             cov_kwds={"groups": de.eco_name})
    print("within ecoregions: heterogeneity -> GPP | climate: beta = %+.3f, p = %.4f"
          % (w.params[H], w.pvalues[H]))


def main():
    m1 = pd.read_csv(os.path.join(DATA, "model_cells.csv"))
    c1 = pd.read_csv(os.path.join(DATA, "confounders_1p0.csv"))
    e1 = pd.read_csv(os.path.join(DATA, "ecoregions_1p0.csv"))[["cell_id", "eco_name"]]
    d1 = m1.merge(c1, on="cell_id").merge(e1, on="cell_id", how="left")
    d1 = d1.dropna(subset=["elev_sd"]).reset_index(drop=True)
    a = pd.DataFrame({"rich": z(d1.rarefied_250), "gpp": z(d1.gpp), "temp": z(d1.temp_c),
                      "precip": z(d1.precip_mm_yr), "effort": z(d1.log_effort),
                      "het": z(np.log10(d1.elev_sd.clip(lower=1))),
                      "eco_name": d1.eco_name})
    run(a.dropna(subset=["eco_name"]).reset_index(drop=True), "1.0")

    m5 = pd.read_csv(os.path.join(DATA, "merged_cells_0p5.csv"))
    c5 = pd.read_csv(os.path.join(DATA, "confounders_0p5.csv"))[["cell_id", "elev_sd"]]
    e5 = pd.read_csv(os.path.join(DATA, "ecoregions_0p5.csv"))[["cell_id", "eco_name"]]
    d5 = m5[m5.gpp.notna() & m5.wc_mode.notna() & ~m5.wc_mode.isin([40, 50, 80])
            & (m5.total_records >= 20) & m5.rarefied.notna() & m5.temp_c.notna()
            & m5.precip_mm_yr.notna()]
    d5 = d5.merge(c5, on="cell_id").merge(e5, on="cell_id", how="left")
    d5 = d5.dropna(subset=["elev_sd", "eco_name"]).reset_index(drop=True)
    b = pd.DataFrame({"rich": z(d5.rarefied), "gpp": z(d5.gpp), "temp": z(d5.temp_c),
                      "precip": z(d5.precip_mm_yr), "effort": z(d5.log_effort),
                      "het": z(np.log10(d5.elev_sd.clip(lower=1))),
                      "eco_name": d5.eco_name})
    run(b, "0.5")
    pd.DataFrame(EST).to_csv(os.path.join(DATA, "path_analysis_estimates.csv"), index=False)


if __name__ == "__main__":
    main()
