# -*- coding: utf-8 -*-
"""Extension E: are species-rich places more STABLE in their productivity?

Added 2026-11-16 (scope lock lifted a second time by the user; DECISIONS.md).
The first four extensions ask about the level of productivity. The other half
of the biodiversity-ecosystem-function literature is about its stability over
time: diverse systems are expected to vary less from year to year (the insurance
effect). This asks whether that shows up in 23 years of satellite GPP.

Per 1-degree cell, from annual MODIS GPP 2001-2023 (data/gee_extras.npz):
  instability   log of the detrended coefficient of variation: the SD of the
                yearly values around a straight-line trend, divided by the mean
  trend         linear change in GPP, percent of the cell's mean per year

Models (standardised; SEs clustered by ecoregion), each with the richness term:
  S1  + effort, mean temperature, mean precipitation      (the usual controls)
  S2  + year-to-year variability of rainfall and temperature
      (a place with erratic rain has erratic GPP whatever lives there)
  S3  + mean GPP    (the CV falls mechanically as the mean rises)
then S3 with ecoregion fixed effects and under the spatial error model, for birds
(221 cells) and for plants (cells with >= 100 identified plant records).

A NEGATIVE richness coefficient means richer cells are more stable.
Writes data/extension_e_cells.csv and data/extension_e_estimates.csv.
"""
import contextlib
import io
import os
import sys
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm
from spreg import ML_Error

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
sys.path.insert(0, HERE)
from weights_sensitivity import queen_from_grid

EST = []


def z(s):
    return (s - s.mean()) / s.std()


def series_stats(a, years):
    """a: (years, cells). Returns mean, raw CV, detrended CV, trend in % of mean per year."""
    t = years - years.mean()
    mean = a.mean(axis=0)
    slope = (t[:, None] * (a - mean)).sum(axis=0) / (t ** 2).sum()
    resid = a - mean - slope * t[:, None]
    return mean, a.std(axis=0, ddof=1) / mean, resid.std(axis=0, ddof=2) / mean, 100 * slope / mean


def fit(d, y, cols, fe=False):
    X = pd.DataFrame({c: z(d[c].astype(float)) for c in cols})
    if fe:
        X = pd.concat([X, pd.get_dummies(d.eco_name, prefix="fe", drop_first=True,
                                         dtype=float)], axis=1)
    return sm.OLS(z(d[y]), sm.add_constant(X)).fit(cov_type="cluster",
                                                  cov_kwds={"groups": d.eco_name})


def sem(d, y, cols):
    X = np.column_stack([z(d[c].astype(float)).values for c in cols])
    w = queen_from_grid(d.lat_c.values, d.lon_c.values, 1.0)
    w.transform = "r"
    with contextlib.redirect_stdout(io.StringIO()):
        s = ML_Error(z(d[y]).values.reshape(-1, 1), X, w=w)
    b = float(s.betas[1][0]); se = float(np.sqrt(s.vm[1, 1]))
    return b, se, 2 * (1 - norm.cdf(abs(b / se)))


def chain(d, rich, effort, tag):
    base = [rich, effort, "temp_c", "precip_mm_yr"]
    var = ["log_precip_cv", "temp_sd"]
    specs = [("S1 usual controls", base), ("S2 + climate variability", base + var),
             ("S3 + mean GPP", base + var + ["log_gpp_mean"])]
    print("\n--- %s: n = %d ---" % (tag, len(d)))
    for y, yl in (("log_cv", "instability (log detrended CV)"), ("trend", "GPP trend, % per year")):
        print(" response: %s" % yl)
        for name, cols in specs:
            m = fit(d, y, cols)
            print("  %-34s beta %+.3f  se %.3f  p = %.4f  R2 = %.3f"
                  % (name, m.params[rich], m.bse[rich], m.pvalues[rich], m.rsquared))
            EST.append({"taxon": tag, "response": y, "spec": name, "beta": m.params[rich],
                        "se": m.bse[rich], "p": m.pvalues[rich], "n": int(m.nobs)})
        m = fit(d, y, specs[2][1], fe=True)
        print("  %-34s beta %+.3f  se %.3f  p = %.4f" % ("S3 + ecoregion fixed effects",
                                                        m.params[rich], m.bse[rich], m.pvalues[rich]))
        EST.append({"taxon": tag, "response": y, "spec": "S3 within ecoregions",
                    "beta": m.params[rich], "se": m.bse[rich], "p": m.pvalues[rich],
                    "n": int(m.nobs)})
        b, se, p = sem(d, y, specs[2][1])
        print("  %-34s beta %+.3f  se %.3f  p = %.4f" % ("S3 spatial error model", b, se, p))
        EST.append({"taxon": tag, "response": y, "spec": "S3 spatial error", "beta": b,
                    "se": se, "p": p, "n": len(d)})
        if y == "log_cv":
            m3 = fit(d, y, specs[2][1])
            print("STAB %s: richness coefficient for instability, full controls: %+.3f "
                  "(p = %.4f); within ecoregions %+.3f (p = %.4f)"
                  % (tag, m3.params[rich], m3.pvalues[rich], m.params[rich], m.pvalues[rich]))


def main():
    g = np.load(os.path.join(DATA, "gee_extras.npz"))
    years = g["years"].astype(float)
    m = pd.read_csv(os.path.join(DATA, "model_cells.csv"))
    e = pd.read_csv(os.path.join(DATA, "ecoregions_1p0.csv"))[["cell_id", "eco_name"]]
    all_cells = pd.read_csv(os.path.join(DATA, "merged_cells.csv"))
    j = np.round(31 - all_cells.lat_c - 0.5).astype(int).values
    i = np.round(all_cells.lon_c - 68 - 0.5).astype(int).values

    def cells(key):
        a = g[key][:, j, i].astype(float)
        a[a < -9000] = np.nan
        return a

    gp, pr, te = cells("gpp_annual"), cells("precip_annual"), cells("temp_annual")
    gm, gcv, gdcv, gtr = series_stats(gp, years)
    pm, pcv, pdcv, _ = series_stats(pr, years)
    s = pd.DataFrame({"cell_id": all_cells.cell_id, "gpp_mean_2001_2023": gm, "gpp_cv": gcv,
                      "gpp_cv_detrended": gdcv, "trend": gtr, "precip_cv": pdcv,
                      "temp_sd": np.nanstd(te - np.nanmean(te, axis=0), axis=0, ddof=1)})
    s["log_cv"] = np.log(s.gpp_cv_detrended)
    s["log_precip_cv"] = np.log(s.precip_cv)
    s["log_gpp_mean"] = np.log(s.gpp_mean_2001_2023)

    d = m.merge(s, on="cell_id").merge(e, on="cell_id", how="left")
    d = d.dropna(subset=["log_cv", "log_precip_cv", "temp_sd", "eco_name"]).reset_index(drop=True)
    print("=== Extension E: stability of productivity, 2001-2023 ===")
    print("modelled cells with a complete 23-year GPP series: %d of %d" % (len(d), len(m)))
    print("detrended CV of annual GPP: median %.3f (5th-95th percentile %.3f to %.3f)"
          % (d.gpp_cv_detrended.median(), d.gpp_cv_detrended.quantile(0.05),
             d.gpp_cv_detrended.quantile(0.95)))
    print("GPP trend: median %+.2f%% per year; positive in %.0f%% of cells"
          % (d.trend.median(), 100 * (d.trend > 0).mean()))
    print("raw correlations with corrected bird richness: instability r = %+.3f, "
          "trend r = %+.3f, mean GPP r = %+.3f"
          % (np.corrcoef(d.rarefied_250, d.log_cv)[0, 1],
             np.corrcoef(d.rarefied_250, d.trend)[0, 1],
             np.corrcoef(d.rarefied_250, d.log_gpp_mean)[0, 1]))
    print("what drives instability on its own: r with rainfall variability %+.3f, "
          "with mean precipitation %+.3f, with mean GPP %+.3f"
          % (np.corrcoef(d.log_precip_cv, d.log_cv)[0, 1],
             np.corrcoef(d.precip_mm_yr, d.log_cv)[0, 1],
             np.corrcoef(d.log_gpp_mean, d.log_cv)[0, 1]))
    chain(d, "rarefied_250", "log_effort", "birds")

    pp = os.path.join(DATA, "plants_model_cells.csv")
    if os.path.exists(pp):
        p = pd.read_csv(pp)[["cell_id", "plant_rarefied_100", "plant_log_effort", "lat_c",
                             "lon_c", "temp_c", "precip_mm_yr"]]
        dp = p.merge(s, on="cell_id").merge(e, on="cell_id", how="left")
        dp = dp.dropna(subset=["log_cv", "log_precip_cv", "temp_sd", "eco_name"]).reset_index(drop=True)
        chain(dp, "plant_rarefied_100", "plant_log_effort", "plants")

    d[["cell_id", "lat_c", "lon_c", "gpp_mean_2001_2023", "gpp_cv", "gpp_cv_detrended", "trend",
       "precip_cv", "temp_sd"]].to_csv(os.path.join(DATA, "extension_e_cells.csv"), index=False)
    s[["cell_id", "gpp_cv_detrended", "trend"]].to_csv(
        os.path.join(DATA, "extension_e_all_cells.csv"), index=False)
    pd.DataFrame(EST).to_csv(os.path.join(DATA, "extension_e_estimates.csv"), index=False)


if __name__ == "__main__":
    main()
