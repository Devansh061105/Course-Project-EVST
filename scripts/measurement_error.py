# -*- coding: utf-8 -*-
"""Is the weak within-ecoregion slope just measurement error in richness?

A regression slope is biased towards zero when its predictor is measured with
error (attenuation). Rarefied richness is an estimate, and inside an ecoregion
the true differences between cells are small, so the same amount of noise is a
larger share of the signal there. If that share were large, "the link fades
within ecoregions" could be an artefact. This script measures it.

  1. Sampling error of each cell's rarefied richness: bootstrap the cell's
     species-abundance vector (multinomial resampling of its N records, 200
     times) and recompute Hurlbert's E[S_250]. The bootstrap SD is the standard
     error of that cell's richness.
  2. Reliability = share of the richness variance that is not sampling error,
     computed for richness as it enters each model: raw, net of the controls,
     and net of controls plus ecoregion fixed effects (the within-ecoregion case).
  3. Corrected slopes two ways: dividing by the reliability (classical
     errors-in-variables), and SIMEX (add extra noise of known size, watch the
     slope fall, extrapolate back to zero noise), which does not assume the
     error variance is the same in every cell.

At 1 degree (221 cells) and 0.5 degree. Cached data only.
Writes data/measurement_error_cells.csv and data/measurement_error_estimates.csv.

What this does NOT cover: error that is not sampling error (observers preferring
some habitats or species). That is the job of the effort covariate and the mask.
"""
import json
import os
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.special import gammaln

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
RNG = np.random.default_rng(404)
NBOOT = 200
N_RARE = 250
CTRL = ["log_effort", "temp_c", "precip_mm_yr"]
ZETAS = [0.0, 0.5, 1.0, 1.5, 2.0]
NSIM = 200
EST = []


def z(s):
    return (s - s.mean()) / s.std()


def rarefy(ab, n=N_RARE):
    """Vectorised Hurlbert E[S_n]; same quantity as gbif_lib.hurlbert_rarefy."""
    ab = ab[ab > 0].astype(float)
    N = ab.sum()
    if N < n:
        return np.nan
    ok = (N - ab) >= n
    logp = (gammaln(N - ab[ok] + 1) - gammaln(N - ab[ok] - n + 1)
            - gammaln(N + 1) + gammaln(N - n + 1))
    return float((~ok).sum() + (1 - np.exp(logp)).sum())


def boot_se(ab):
    ab = np.asarray(ab, dtype=np.int64)
    N = int(ab.sum()); p = ab / N
    v = [rarefy(RNG.multinomial(N, p)) for _ in range(NBOOT)]
    return float(np.nanstd(v, ddof=1))


def resid(d, col, fe):
    X = pd.DataFrame({c: z(d[c].astype(float)) for c in CTRL})
    if fe:
        X = pd.concat([X, pd.get_dummies(d.eco_name, prefix="fe", drop_first=True,
                                         dtype=float)], axis=1)
    return sm.OLS(d[col].astype(float), sm.add_constant(X)).fit().resid


def slope(d, rich_values, fe):
    X = pd.DataFrame({"rich": rich_values, **{c: z(d[c].astype(float)) for c in CTRL}})
    if fe:
        X = pd.concat([X, pd.get_dummies(d.eco_name, prefix="fe", drop_first=True,
                                         dtype=float)], axis=1)
    m = sm.OLS(z(d.gpp.astype(float)), sm.add_constant(X)).fit(
        cov_type="cluster", cov_kwds={"groups": d.eco_name})
    return m.params["rich"], m.bse["rich"]


def run(d, rich, tag):
    d = d.reset_index(drop=True)
    sd_r = d[rich].std()
    print("\n=== measurement error in corrected richness, %s degree: n = %d ===" % (tag, len(d)))
    print("standard error of a cell's richness (species): median %.2f, 90th percentile %.2f, "
          "max %.2f; SD of richness across cells %.1f"
          % (d.se.median(), d.se.quantile(0.9), d.se.max(), sd_r))
    small = d[d.sp_resolved < 1000]
    print("cells with fewer than 1,000 records: %d, median SE there %.2f"
          % (len(small), small.se.median() if len(small) else float("nan")))
    err = (d.se ** 2).mean()
    rz = z(d[rich].astype(float))
    for name, fe, signal in (("raw richness", None, d[rich].var()),
                             ("net of controls", False, resid(d, rich, False).var()),
                             ("net of controls and ecoregion", True, resid(d, rich, True).var())):
        rel = 1 - err / signal
        print("  reliability of richness, %-30s %.3f   (error variance %.1f of %.1f)"
              % (name, rel, err, signal))
        if fe is None:
            continue
        b, se = slope(d, rz, fe)
        label = "within ecoregions" if fe else "across regions"
        print("  %-18s slope observed %+.3f (se %.3f) -> corrected by reliability %+.3f"
              % (label, b, se, b / rel))
        EST.append({"grain": tag, "model": label, "reliability": rel, "beta_observed": b,
                    "se": se, "beta_reliability": b / rel})
        # SIMEX: extra noise with each cell's own error variance, in SD units of richness
        sims = []
        for zeta in ZETAS:
            if zeta == 0:
                sims.append(b); continue
            bs = []
            for _ in range(NSIM):
                noisy = d[rich].values + RNG.normal(0, np.sqrt(zeta) * d.se.values)
                bs.append(slope(d, (noisy - noisy.mean()) / noisy.std(), fe)[0])
            sims.append(float(np.mean(bs)))
        coef = np.polyfit(ZETAS, sims, 2)
        simex = float(np.polyval(coef, -1.0))
        print("  %-18s SIMEX: slope at added noise x0, x1, x2 = %+.3f, %+.3f, %+.3f -> "
              "extrapolated to no error %+.3f" % (label, sims[0], sims[2], sims[4], simex))
        EST[-1]["beta_simex"] = simex
        for zeta, s_ in zip(ZETAS, sims):
            EST.append({"grain": tag, "model": label + " (simex path)", "zeta": zeta,
                        "beta_observed": s_})
        if fe:
            print("MERR %s: within-ecoregion reliability %.3f; slope %+.3f observed, %+.3f "
                  "after correction (SIMEX %+.3f)" % (tag, rel, b, b / rel, simex))


def main():
    m1 = pd.read_csv(os.path.join(DATA, "model_cells.csv"))
    e1 = pd.read_csv(os.path.join(DATA, "ecoregions_1p0.csv"))[["cell_id", "eco_name"]]
    c1 = json.load(open(os.path.join(DATA, "gbif_cache.json"), encoding="utf-8"))
    d1 = m1.merge(e1, on="cell_id", how="left").dropna(subset=["eco_name"]).reset_index(drop=True)
    d1["se"] = [boot_se(c1["birds|" + c]["ab"]) for c in d1.cell_id]
    d1["sp_resolved"] = d1.sp_resolved_records
    run(d1, "rarefied_250", "1.0")

    m5 = pd.read_csv(os.path.join(DATA, "merged_cells_0p5.csv"))
    e5 = pd.read_csv(os.path.join(DATA, "ecoregions_0p5.csv"))[["cell_id", "eco_name"]]
    c5 = json.load(open(os.path.join(DATA, "gbif_cache_0p5.json"), encoding="utf-8"))
    d5 = m5[m5.gpp.notna() & m5.wc_mode.notna() & ~m5.wc_mode.isin([40, 50, 80])
            & (m5.total_records >= 20) & m5.rarefied.notna() & m5.temp_c.notna()
            & m5.precip_mm_yr.notna()].merge(e5, on="cell_id", how="left")
    d5 = d5.dropna(subset=["eco_name"]).reset_index(drop=True)
    d5["se"] = [boot_se(c5[c]["ab"]) for c in d5.cell_id]
    d5["sp_resolved"] = [sum(c5[c]["ab"]) for c in d5.cell_id]
    run(d5, "rarefied", "0.5")

    out = pd.concat([d1[["cell_id", "lat_c", "lon_c", "se"]].assign(grain=1.0),
                     d5[["cell_id", "lat_c", "lon_c", "se"]].assign(grain=0.5)])
    out.to_csv(os.path.join(DATA, "measurement_error_cells.csv"), index=False)
    pd.DataFrame(EST).to_csv(os.path.join(DATA, "measurement_error_estimates.csv"), index=False)


if __name__ == "__main__":
    main()
