# -*- coding: utf-8 -*-
"""Where should the next bird surveys go? A survey-gap ranking.

The analysis drops natural-cover cells with fewer than 250 identified bird
records, and even modelled cells differ widely in how complete their species
lists are. This script turns that into something a citizen-science programme
could act on: for every natural-cover land cell,

  completeness   sample coverage of its bird records (Chao & Jost 2012): the
                 estimated share of the cell's birds, by individuals, that belong
                 to species already recorded there. 0 for a cell with no records.
  expected       corrected richness predicted from environment alone (temperature,
                 precipitation, elevation, topographic heterogeneity, NDVI), from
                 a model fitted to the modelled cells and checked by leave-one-
                 block-out cross-validation
  priority       expected richness x (1 - completeness), rescaled 0-100: many
                 species expected, few of them documented.

It is a ranking aid, not a result about biodiversity. Its two weak points are
printed with it: how well the environment-only model predicts held-out cells,
and the fact that coverage near 1 can still hide rare species.

Reads cached data only. Writes data/survey_gaps_1p0.csv.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
sys.path.insert(0, HERE)
from coverage_rarefaction import full_coverage

PRED = ["temp_c", "precip_mm_yr", "elev_mean", "elev_sd", "ndvi"]


def design(d, mu, sd):
    Z = (d[PRED] - mu) / sd
    Z["elev_sd"] = np.log10(d.elev_sd.clip(lower=1)) - np.log10(max(mu["elev_sd"], 1))
    X = np.column_stack([np.ones(len(d)), Z.values, Z.temp_c ** 2, Z.precip_mm_yr ** 2])
    return X


def main():
    d = pd.read_csv(os.path.join(DATA, "final", "biodiversity_productivity_1deg.csv"))
    d["wc_mode"] = d.wc_mode.round()
    c = pd.read_csv(os.path.join(DATA, "countries_1p0.csv"))
    d = d.merge(c, on="cell_id", how="left")
    nat = d[d.wc_mode.notna() & ~d.wc_mode.isin([40, 50, 80])].dropna(subset=PRED).copy()
    cache = json.load(open(os.path.join(DATA, "gbif_cache.json"), encoding="utf-8"))

    cov = []
    for cid in nat.cell_id:
        x = np.array(cache["birds|" + cid]["ab"], dtype=float)
        cov.append(full_coverage(x) if x.sum() > 0 else 0.0)
    nat["completeness"] = np.clip(cov, 0, 1)

    fit = nat[nat.in_model == 1]
    mu, sd = fit[PRED].mean(), fit[PRED].std()
    y = fit.rarefied_250.values
    X = design(fit, mu, sd)
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    r2_in = 1 - ((y - X @ b) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    blk = (np.floor(fit.lat_c / 4).astype(int).astype(str) + "_"
           + np.floor(fit.lon_c / 4).astype(int).astype(str)).values
    pred = np.empty(len(fit))
    for g in np.unique(blk):
        te = blk == g
        bb, *_ = np.linalg.lstsq(X[~te], y[~te], rcond=None)
        pred[te] = X[te] @ bb
    r2_cv = 1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    rmse = np.sqrt(((y - pred) ** 2).mean())
    print("natural-cover land cells: %d  (modelled %d, not modelled %d)"
          % (len(nat), (nat.in_model == 1).sum(), (nat.in_model != 1).sum()))
    print("GAPS environment-only model of corrected richness: R2 in-sample %.3f, "
          "leave-one-4-degree-block-out R2 %.3f, RMSE %.1f species" % (r2_in, r2_cv, rmse))

    lo, hi = np.percentile(y, [1, 99])
    nat["expected_richness"] = np.clip(design(nat, mu, sd) @ b, lo, hi)
    # A prediction for a cell whose climate or terrain lies outside anything the model
    # was fitted on is an extrapolation; flag it rather than hide it.
    lo_p, hi_p = fit[PRED].min(), fit[PRED].max()
    nat["extrapolated"] = ((nat[PRED] < lo_p) | (nat[PRED] > hi_p)).any(axis=1).astype(int)
    raw = nat.expected_richness * (1 - nat.completeness)
    nat["priority"] = 100 * raw / raw.max()
    nat = nat.sort_values("priority", ascending=False).reset_index(drop=True)

    print("\ncompleteness of bird records (sample coverage):")
    for name, s in (("modelled cells", nat[nat.in_model == 1]),
                    ("natural-cover cells not modelled", nat[nat.in_model != 1])):
        print("  %-34s n=%-4d median %.3f   below 0.90: %d   no records at all: %d"
              % (name, len(s), s.completeness.median(), (s.completeness < 0.9).sum(),
                 (s.total_records == 0).sum()))
    un = nat[nat.in_model != 1]
    print("GAPS natural-cover cells left out of the models for too few records: %d; "
          "median expected richness there %.1f against %.1f in modelled cells"
          % (len(un), un.expected_richness.median(),
             nat[nat.in_model == 1].expected_richness.median()))

    print("\ntop 15 survey priorities:")
    print("%-8s %-7s %-7s %-12s %9s %12s %9s %9s %7s  %s" % (
        "cell", "lat", "lon", "country", "records", "completeness", "expected", "priority",
        "extrap", "ecoregion"))
    for r in nat.head(15).itertuples():
        print("%-8s %-7.1f %-7.1f %-12s %9d %12.2f %9.1f %9.1f %7s  %s" % (
            r.cell_id, r.lat_c, r.lon_c, str(r.country)[:12], r.total_records, r.completeness,
            r.expected_richness, r.priority, "yes" if r.extrapolated else "",
            str(r.eco_name)[:40]))
    print("GAPS extrapolated predictions: %d of the top 30, %d of all %d cells"
          % (nat.head(30).extrapolated.sum(), nat.extrapolated.sum(), len(nat)))
    top = nat.head(30)
    print("\nwhere the top 30 priorities are:")
    for k, v in top.country.value_counts().items():
        print("  %-14s %d" % (k, v))
    print("GAPS top-30 priority cells: %d in %s, the largest share"
          % (top.country.value_counts().iloc[0], top.country.value_counts().index[0]))
    print("\nmean priority by country (countries with >= 5 natural-cover cells):")
    g = nat.groupby("country").agg(cells=("priority", "size"), priority=("priority", "mean"),
                                   completeness=("completeness", "median"),
                                   records=("total_records", "median"))
    for k, r in g[g.cells >= 5].sort_values("priority", ascending=False).iterrows():
        print("  %-14s cells %-3d mean priority %5.1f   median completeness %.2f   "
              "median records %d" % (k, r.cells, r.priority, r.completeness, r.records))

    keep = ["cell_id", "lat_c", "lon_c", "country", "eco_name", "in_model", "total_records",
            "obs_richness", "completeness", "expected_richness", "extrapolated", "priority"]
    nat[keep].to_csv(os.path.join(DATA, "survey_gaps_1p0.csv"), index=False)
    print("\nwrote data/survey_gaps_1p0.csv (%d cells)" % len(nat))


if __name__ == "__main__":
    main()
