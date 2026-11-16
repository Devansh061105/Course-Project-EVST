# -*- coding: utf-8 -*-
"""How small is the within-ecoregion effect? Bounds, power, and slopes by ecoregion.

"Not significant" is not a finding. This script turns the within-ecoregion result
into statements that can be defended:

  A. Equivalence tests (two one-sided tests, TOST). For each sample, is the
     within-ecoregion coefficient demonstrably SMALLER than a stated bound? Two
     bounds are used: half of that sample's own cross-regional coefficient, and a
     fixed 0.10 SD. Also the minimum effect each sample could have detected with
     80% power, and the largest effect its 95% interval allows.
  B. Slopes ecoregion by ecoregion. Richness and GPP are residualised on the
     controls and on ecoregion means, a slope is fitted inside every ecoregion
     with at least MIN_CELLS cells, and the slopes are combined by random-effects
     meta-analysis (DerSimonian-Laird). Ecoregions are separate groups of cells,
     so unlike pooling across taxa this treats independent units as independent.
     Reported: pooled slope, between-ecoregion heterogeneity (tau, I-squared, Q
     test) and a 95% prediction interval for the slope in a new ecoregion.
  C. A mixed model with a random intercept and a random richness slope per
     ecoregion, as a cross-check on B.

Cached data only. Writes data/within_bounds.csv and data/ecoregion_slopes.csv.
"""
import os
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import chi2, norm, t as tdist

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
CLIM = ["temp_c", "precip_mm_yr"]
MIN_CELLS = 8
FIXED_BOUND = 0.10
ROWS, SLOPES = [], []


def z(s):
    return (s - s.mean()) / s.std()


def fit(d, rich, effort, fe):
    X = pd.DataFrame({c: z(d[c].astype(float)) for c in [rich, effort] + CLIM})
    if fe:
        X = pd.concat([X, pd.get_dummies(d.eco_name, prefix="fe", drop_first=True,
                                         dtype=float)], axis=1)
    m = sm.OLS(z(d.gpp.astype(float)), sm.add_constant(X)).fit(
        cov_type="cluster", cov_kwds={"groups": d.eco_name})
    return m.params[rich], m.bse[rich]


def tost(b, se, bound):
    """p-value of the equivalence test |beta| < bound (the larger of the two one-sided p)."""
    return max(1 - norm.cdf((b + bound) / se), norm.cdf((b - bound) / se))


def bounds(d, rich, effort, label):
    b0, s0 = fit(d, rich, effort, False)
    b, se = fit(d, rich, effort, True)
    half = abs(b0) / 2
    p_half, p_fix = tost(b, se, half), tost(b, se, FIXED_BOUND)
    hi95 = b + 1.645 * se                       # one-sided 95% upper bound
    mde = (1.960 + 0.842) * se                  # detectable with 80% power at alpha 0.05
    print("%-26s n=%-4d across %+.3f | within %+.3f (se %.3f), 90%% CI [%+.3f, %+.3f]"
          % (label, len(d), b0, b, se, b - 1.645 * se, b + 1.645 * se))
    print("%-26s        smaller than half the across-region effect (%.3f)? p = %.4f %s | "
          "smaller than %.2f? p = %.4f %s"
          % ("", half, p_half, "YES" if p_half < 0.05 else "not shown",
             FIXED_BOUND, p_fix, "YES" if p_fix < 0.05 else "not shown"))
    print("%-26s        largest effect compatible (95%% bound) %+.3f = %.0f%% of the across-"
          "region effect; detectable with 80%% power: %.3f"
          % ("", hi95, 100 * hi95 / b0, mde))
    ROWS.append({"sample": label, "n": len(d), "beta_across": b0, "se_across": s0,
                 "beta_within": b, "se_within": se, "lo90": b - 1.645 * se,
                 "hi90": b + 1.645 * se, "half_bound": half, "p_tost_half": p_half,
                 "p_tost_fixed": p_fix, "upper95": hi95, "upper95_share": hi95 / b0,
                 "mde80": mde})
    return b, se, p_half


def by_ecoregion(d, rich, effort, tag):
    """Residual-on-residual slope inside each ecoregion, then DerSimonian-Laird."""
    Z = pd.DataFrame({c: z(d[c].astype(float)) for c in ["gpp", rich, effort] + CLIM})
    D = pd.get_dummies(d.eco_name, prefix="fe", drop_first=True, dtype=float)
    X = sm.add_constant(pd.concat([Z[[effort] + CLIM], D], axis=1))
    ry = sm.OLS(Z.gpp, X).fit().resid.values
    rr = sm.OLS(Z[rich], X).fit().resid.values
    res = []
    for name, idx in d.groupby("eco_name").indices.items():
        if len(idx) < MIN_CELLS:
            continue
        x, y = rr[idx], ry[idx]
        b = (x * y).sum() / (x * x).sum()
        e = y - b * x
        se = np.sqrt((e * e).sum() / (len(idx) - 1) / (x * x).sum())
        res.append((name, len(idx), b, se))
        SLOPES.append({"grain": tag, "eco_name": name, "n": len(idx), "beta": b, "se": se})
    k = len(res)
    b = np.array([r[2] for r in res]); v = np.array([r[3] for r in res]) ** 2
    w = 1 / v
    fixed = (w * b).sum() / w.sum()
    Q = (w * (b - fixed) ** 2).sum()
    C = w.sum() - (w ** 2).sum() / w.sum()
    tau2 = max(0.0, (Q - (k - 1)) / C)
    wr = 1 / (v + tau2)
    pooled = (wr * b).sum() / wr.sum(); se_p = np.sqrt(1 / wr.sum())
    i2 = max(0.0, (Q - (k - 1)) / Q) if Q > 0 else 0.0
    tq = tdist.ppf(0.975, max(k - 2, 1))
    pi = (pooled - tq * np.sqrt(tau2 + se_p ** 2), pooled + tq * np.sqrt(tau2 + se_p ** 2))
    cells = sum(r[1] for r in res)
    print("\n--- slopes by ecoregion, %s degree: %d ecoregions with >= %d cells (%d of %d cells) ---"
          % (tag, k, MIN_CELLS, cells, len(d)))
    print("ECO %s: pooled within-ecoregion slope %+.3f (se %.3f, 95%% CI %+.3f to %+.3f), p = %.4f"
          % (tag, pooled, se_p, pooled - 1.96 * se_p, pooled + 1.96 * se_p,
             2 * (1 - norm.cdf(abs(pooled / se_p)))))
    print("ECO %s: heterogeneity tau = %.3f, I2 = %.0f%%, Q = %.1f on %d df (p = %.4f); "
          "95%% prediction interval for a new ecoregion %+.3f to %+.3f"
          % (tag, np.sqrt(tau2), 100 * i2, Q, k - 1, 1 - chi2.cdf(Q, k - 1), pi[0], pi[1]))
    pos = sum(1 for r in res if r[2] > 0)
    sig_pos = sum(1 for r in res if r[2] - 1.96 * r[3] > 0)
    sig_neg = sum(1 for r in res if r[2] + 1.96 * r[3] < 0)
    print("ECO %s: slope positive in %d of %d ecoregions; individually significant: %d positive, "
          "%d negative" % (tag, pos, k, sig_pos, sig_neg))
    for r in sorted(res, key=lambda r: r[2]):
        print("    %-58s n=%-3d %+.3f (se %.3f)" % (r[0][:58], r[1], r[2], r[3]))
    SLOPES.append({"grain": tag, "eco_name": "POOLED (random effects)", "n": cells,
                   "beta": pooled, "se": se_p, "tau": np.sqrt(tau2), "i2": i2,
                   "pi_lo": pi[0], "pi_hi": pi[1]})

    try:
        md = pd.concat([Z, d[["eco_name"]].reset_index(drop=True)], axis=1)
        mm = sm.MixedLM(md.gpp, sm.add_constant(md[[rich, effort] + CLIM]), groups=md.eco_name,
                        exog_re=sm.add_constant(md[[rich]])).fit(reml=True, method="lbfgs")
        sd_slope = float(np.sqrt(max(mm.cov_re.iloc[1, 1], 0)))
        print("MIXED %s: fixed richness slope %+.3f (se %.3f, p = %.4f); SD of the slope across "
              "ecoregions %.3f" % (tag, mm.params[rich], mm.bse[rich], mm.pvalues[rich], sd_slope))
    except Exception as e:
        print("MIXED %s: did not converge (%s)" % (tag, str(e)[:60]))


def main():
    e1 = pd.read_csv(os.path.join(DATA, "ecoregions_1p0.csv"))[["cell_id", "eco_name"]]
    e5 = pd.read_csv(os.path.join(DATA, "ecoregions_0p5.csv"))[["cell_id", "eco_name"]]
    b1 = pd.read_csv(os.path.join(DATA, "model_cells.csv")).merge(e1, on="cell_id", how="left")
    b1 = b1.dropna(subset=["eco_name"]).reset_index(drop=True)
    m5 = pd.read_csv(os.path.join(DATA, "merged_cells_0p5.csv"))
    b5 = m5[m5.gpp.notna() & m5.wc_mode.notna() & ~m5.wc_mode.isin([40, 50, 80])
            & (m5.total_records >= 20) & m5.rarefied.notna() & m5.temp_c.notna()
            & m5.precip_mm_yr.notna()].merge(e5, on="cell_id", how="left")
    b5 = b5.dropna(subset=["eco_name"]).reset_index(drop=True)

    print("=== A. Equivalence tests and power ===")
    bounds(b1, "rarefied_250", "log_effort", "birds, 1 degree")
    b, se, p = bounds(b5, "rarefied", "log_effort", "birds, 0.5 degree")
    print("TOST birds 0.5 deg: within effect smaller than half the across-region effect, "
          "p = %.4f" % p)

    pp = os.path.join(DATA, "plants_model_cells.csv")
    if os.path.exists(pp):
        p1 = pd.read_csv(pp).dropna(subset=["eco_name"]).reset_index(drop=True)
        bounds(p1, "plant_rarefied_100", "plant_log_effort", "plants, 1 degree")
    p5 = os.path.join(DATA, "gbif_cells_plants_0p5.csv")
    if os.path.exists(p5):
        q = pd.read_csv(p5).drop(columns=["lat_c", "lon_c"]).merge(m5, on="cell_id").merge(
            e5, on="cell_id", how="left")
        q = q.dropna(subset=["eco_name", "gpp", "temp_c", "precip_mm_yr", "plant_rarefied_100"])
        q["plant_log_effort"] = np.log10(q.plant_total_records.clip(lower=1))
        bounds(q.reset_index(drop=True), "plant_rarefied_100", "plant_log_effort",
               "plants, 0.5 degree")
    lp = os.path.join(DATA, "gbif_cells_lepidoptera_1p0.csv")
    if os.path.exists(lp):
        m1 = pd.read_csv(os.path.join(DATA, "merged_cells.csv"))
        m1["wc_mode"] = m1.wc_mode.round()
        l = pd.read_csv(lp).drop(columns=["lat_c", "lon_c"]).merge(m1, on="cell_id").merge(
            e1, on="cell_id", how="left")
        l = l[l.is_land.astype(bool) & ~l.wc_mode.isin([40, 50, 80])].dropna(
            subset=["eco_name", "gpp", "temp_c", "precip_mm_yr", "lepid_rarefied_100"])
        l["lepid_log_effort"] = np.log10(l.lepid_total_records.clip(lower=1))
        bounds(l.reset_index(drop=True), "lepid_rarefied_100", "lepid_log_effort",
               "butterflies and moths, 1 degree")

    print("\n=== B and C. Slopes by ecoregion ===")
    by_ecoregion(b5, "rarefied", "log_effort", "0.5")
    by_ecoregion(b1, "rarefied_250", "log_effort", "1.0")
    pd.DataFrame(ROWS).to_csv(os.path.join(DATA, "within_bounds.csv"), index=False)
    pd.DataFrame(SLOPES).to_csv(os.path.join(DATA, "ecoregion_slopes.csv"), index=False)


if __name__ == "__main__":
    main()
