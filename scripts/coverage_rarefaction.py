# -*- coding: utf-8 -*-
"""Coverage-based standardisation (Chao & Jost 2012, Ecology 93:2533-2547).

Hurlbert rarefaction standardises every cell to the same number of records.
Chao & Jost argue cells should instead be compared at equal sample COMPLETENESS
(coverage: the fraction of individuals in the community belonging to species
already detected). Two cells rarefied to 250 records can sit at very different
completeness if one community is far more even than the other.

For each cell's species-abundance vector X (n records):
  sample coverage at size m < n  (Chao & Jost 2012, eq. 4a):
      C_m = 1 - sum_i (X_i / n) * C(n - X_i, m) / C(n - 1, m)
  find m* with C_m* = target by bisection, then report Hurlbert S(m*).
Cells whose full-sample coverage is below the target would need extrapolation
and are left missing rather than extrapolated.

Also decomposes richness and GPP variance within vs between ecoregions, which
shows how much predictor variation survives within ecoregions (it does NOT show the
within-ecoregion test is well powered: GPP keeps only ~10% of its variance there).
"""
import json
import os
import sys
import warnings

import numpy as np
import pandas as pd
from scipy.special import gammaln

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
sys.path.insert(0, HERE)
from gbif_lib import hurlbert_rarefy

TARGETS = (0.90, 0.95)


def lchoose(a, k):
    return gammaln(a + 1) - gammaln(k + 1) - gammaln(a - k + 1)


def coverage_at(x, n, m):
    """Expected sample coverage of a rarefied sample of size m (vectorised)."""
    ok = (n - x) >= m
    term = np.zeros_like(x, dtype=float)
    term[ok] = np.exp(lchoose(n - x[ok], m) - lchoose(n - 1, m))
    return 1.0 - np.sum((x / n) * term)


def full_coverage(x):
    n = x.sum()
    f1 = (x == 1).sum(); f2 = (x == 2).sum()
    if n < 2:
        return np.nan
    if f2 > 0:
        a = (n - 1) * f1 / ((n - 1) * f1 + 2 * f2)
    else:
        a = (n - 1) * (f1 - 1) / ((n - 1) * (f1 - 1) + 2) if f1 > 1 else 0.0
    return 1 - (f1 / n) * a


def m_for_coverage(x, target):
    n = int(x.sum())
    lo, hi = 1, n - 1
    if hi < 2 or coverage_at(x, n, hi) < target:
        return None
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if coverage_at(x, n, mid) >= target:
            hi = mid
        else:
            lo = mid
    return hi


def main():
    cache = json.load(open(os.path.join(DATA, "gbif_cache.json"), encoding="utf-8"))
    rows = []
    for key, rec in cache.items():
        cid = key.split("|", 1)[1]
        x = np.array(rec["ab"], dtype=float)
        row = {"cell_id": cid, "n_sp_resolved": int(x.sum()),
               "coverage_full": full_coverage(x) if x.sum() >= 2 else np.nan}
        for t in TARGETS:
            m = m_for_coverage(x, t) if x.sum() >= 20 else None
            tag = "cov%02d" % int(round(t * 100))
            row["m_" + tag] = m
            row["S_" + tag] = hurlbert_rarefy(list(x.astype(int)), m) if m else np.nan
        rows.append(row)
    cov = pd.DataFrame(rows)
    cov.to_csv(os.path.join(DATA, "coverage_1p0.csv"), index=False)

    model = pd.read_csv(os.path.join(DATA, "model_cells.csv"))
    d = model.merge(cov, on="cell_id", how="left")
    print("model cells: %d" % len(d))
    print("full-sample coverage: min %.4f  median %.4f"
          % (d.coverage_full.min(), d.coverage_full.median()))
    for t in TARGETS:
        tag = "cov%02d" % int(round(t * 100))
        print("coverage %.2f: reached in %d cells; records needed m*: median %.0f, "
              "range %.0f-%.0f"
              % (t, d["S_" + tag].notna().sum(), d["m_" + tag].median(),
                 d["m_" + tag].min(), d["m_" + tag].max()))

    # coverage implied by the fixed n=250 standardisation used so far
    c250 = []
    for cid in d.cell_id:
        x = np.array(cache["birds|" + cid]["ab"], dtype=float)
        c250.append(coverage_at(x, x.sum(), 250) if x.sum() > 250 else np.nan)
    d["cov_at_250"] = c250
    print("\ncoverage achieved by the fixed n=250 standardisation: "
          "min %.3f  median %.3f  max %.3f  -> spread of %.3f"
          % (np.nanmin(c250), np.nanmedian(c250), np.nanmax(c250),
             np.nanmax(c250) - np.nanmin(c250)))
    print("correlation rarefied_250 vs S_cov90 = %.3f ; vs S_cov95 = %.3f"
          % (d[["rarefied_250", "S_cov90"]].corr().iloc[0, 1],
             d[["rarefied_250", "S_cov95"]].corr().iloc[0, 1]))
    d[["cell_id", "S_cov90", "S_cov95", "m_cov90", "m_cov95", "cov_at_250",
       "coverage_full"]].to_csv(os.path.join(DATA, "coverage_model_cells.csv"), index=False)

    # variance decomposition within / between ecoregions
    eco = pd.read_csv(os.path.join(DATA, "ecoregions_1p0.csv"))
    e = model.merge(eco, on="cell_id").dropna(subset=["eco_name"])
    print("\nvariance decomposition across %d ecoregions (n=%d):" % (e.eco_name.nunique(), len(e)))
    for c in ("rarefied_250", "gpp", "npp", "temp_c", "precip_mm_yr"):
        tot = e[c].var(ddof=0)
        within = (e[c] - e.groupby("eco_name")[c].transform("mean")).var(ddof=0)
        print("  %-14s within-ecoregion share of variance: %5.1f%%" % (c, 100 * within / tot))


if __name__ == "__main__":
    main()
