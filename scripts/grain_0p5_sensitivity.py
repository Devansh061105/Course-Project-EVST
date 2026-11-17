# -*- coding: utf-8 -*-
"""Two robustness checks that existed only at 1 degree, repeated at 0.5 degrees.

1. Coverage-based richness (Chao & Jost 2012). The 0.5-degree chain rarefies every
   cell to 250 records; here cells are instead compared at equal sample coverage
   (0.90 and 0.95), computed from the cached abundance vectors. No network.
2. Time-window match. Bird records are 2000-2024, the environmental means are
   2019-2023. Records are re-pulled for 2019-2023 only and the chain is refitted.

The pull covers only the cells that enter the 0.5-degree model (natural cover,
>= 250 species-identified records in 2000-2024): a cell with fewer than 250 such
records in the long window cannot have 250 in the short one, so pulling the rest
would cost requests and change nothing. One faceted request per cell, 0.3 s apart,
cached in data/gbif_cache_0p5_2019_2023.json; cached cells are never pulled again.
MAX_PULLS caps one run; re-running continues from the cache.

Models (same as grain_0p5_analysis.py), GPP standardised:
  A  baseline: richness + log10(effort) + temperature + precipitation,
     SEs clustered by ecoregion
  C  + ecoregion fixed effects (within)
  spatial error model, queen contiguity
"""
import json
import os
import sys
import time
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
from coverage_rarefaction import coverage_at, full_coverage, m_for_coverage
from gbif_lib import (FACET_LIMIT, TAXA, build_grid, gbif_cell, hurlbert_rarefy,
                      load_cache, save_cache)
from weights_sensitivity import queen_from_grid

CELL = 0.5
YEARS = "2019,2023"
RARE_N = 250
TARGETS = (0.90, 0.95)
CLIM = ["temp_c", "precip_mm_yr"]
CACHE_ALL = os.path.join(DATA, "gbif_cache_0p5.json")
CACHE_WIN = os.path.join(DATA, "gbif_cache_0p5_2019_2023.json")
MAX_PULLS = int(os.environ.get("MAX_PULLS", "0")) or None
OUT = []


def z(s):
    return (s - s.mean()) / s.std()


def load():
    m = pd.read_csv(os.path.join(DATA, "merged_cells_0p5.csv"))
    e = pd.read_csv(os.path.join(DATA, "ecoregions_0p5.csv"))
    d = m[m.gpp.notna() & m.wc_mode.notna() & ~m.wc_mode.isin([40, 50, 80])
          & (m.total_records >= 20) & m.rarefied.notna()
          & m.temp_c.notna() & m.precip_mm_yr.notna()].copy()
    return d.merge(e, on="cell_id", how="left")


def chain(d, rich, effort, tag, label):
    """Baseline, within-ecoregion and spatial error fits; one printed line."""
    s = d.dropna(subset=[rich, effort, "eco_name"]).reset_index(drop=True)
    cols = [rich, effort] + CLIM
    zd = s[["gpp"] + cols].astype(float).apply(z)
    a = sm.OLS(zd["gpp"], sm.add_constant(zd[cols])).fit(
        cov_type="cluster", cov_kwds={"groups": s.eco_name})
    X = pd.concat([zd[cols], pd.get_dummies(s.eco_name, drop_first=True, dtype=float)],
                  axis=1)
    c = sm.OLS(zd["gpp"], sm.add_constant(X)).fit(
        cov_type="cluster", cov_kwds={"groups": s.eco_name})
    try:
        w = queen_from_grid(s.lat_c.values, s.lon_c.values, CELL)
        w.transform = "r"
        sem = ML_Error(zd["gpp"].values.reshape(-1, 1), zd[cols].values, w=w)
        bs = float(sem.betas[1][0])
        ps = 2 * (1 - norm.cdf(abs(bs / float(np.sqrt(sem.vm[1, 1])))))
    except Exception as exc:                       # reported, not hidden
        print("  spatial error model failed for %s: %s" % (tag, str(exc)[:80]))
        bs, ps = np.nan, np.nan
    print("%s %s (n=%d, %d ecoregions): baseline %+.3f (p=%.4f) | within-ecoregion "
          "%+.3f (se %.3f, p=%.4f) | spatial error %+.3f (p=%.4f)"
          % (tag, label, len(s), s.eco_name.nunique(), a.params[rich], a.pvalues[rich],
             c.params[rich], c.bse[rich], c.pvalues[rich], bs, ps))
    OUT.append({"check": tag, "variant": label, "n": len(s),
                "ecoregions": s.eco_name.nunique(),
                "baseline_beta": a.params[rich], "baseline_p": a.pvalues[rich],
                "within_beta": c.params[rich], "within_se": c.bse[rich],
                "within_p": c.pvalues[rich], "sem_beta": bs, "sem_p": ps})
    return s


def part_coverage(d):
    print("=== 1. coverage-based richness at 0.5 degrees ===")
    cache = json.load(open(CACHE_ALL, encoding="utf-8"))
    rows = []
    for cid in d.cell_id:
        x = np.array(cache[cid]["ab"], dtype=float)
        n = x.sum()
        row = {"cell_id": cid, "coverage_full": full_coverage(x),
               "cov_at_250": coverage_at(x, n, RARE_N) if n > RARE_N else np.nan}
        for t in TARGETS:
            tag = "cov%02d" % int(round(t * 100))
            m = m_for_coverage(x, t)
            row["m_" + tag] = m
            row["S_" + tag] = hurlbert_rarefy(list(x.astype(int)), m) if m else np.nan
        rows.append(row)
    cov = pd.DataFrame(rows)
    cov.to_csv(os.path.join(DATA, "coverage_0p5.csv"), index=False)
    d = d.merge(cov, on="cell_id")
    print("model cells: %d; full-sample coverage: min %.4f, median %.4f"
          % (len(d), d.coverage_full.min(), d.coverage_full.median()))
    print("coverage reached by the fixed n=250 standardisation: min %.3f, median %.3f, "
          "max %.3f" % (d.cov_at_250.min(), d.cov_at_250.median(), d.cov_at_250.max()))
    for t in TARGETS:
        tag = "cov%02d" % int(round(t * 100))
        print("coverage %.2f: reached in %d of %d cells (records needed: median %.0f); "
              "r with rarefied-250 = %.3f"
              % (t, d["S_" + tag].notna().sum(), len(d), d["m_" + tag].median(),
                 d[["rarefied", "S_" + tag]].corr().iloc[0, 1]))
    chain(d, "rarefied", "log_effort", "COV", "rarefied 250, all cells")
    for t in TARGETS:
        tag = "cov%02d" % int(round(t * 100))
        s = d[d["S_" + tag].notna()]
        chain(s, "S_" + tag, "log_effort", "COV", "coverage %.2f" % t)
        chain(s, "rarefied", "log_effort", "COV", "rarefied 250, coverage-%.2f cells" % t)


def part_timewindow(d):
    print("\n=== 2. records restricted to 2019-2023, 0.5 degrees ===")
    grid = {c["cell_id"]: c for c in build_grid(CELL)}
    cache = load_cache(CACHE_WIN)
    todo = [cid for cid in d.cell_id if cid not in cache]
    print("cells in the 0.5-degree model: %d, to pull: %d" % (len(d), len(todo)),
          flush=True)
    t0 = time.time()
    for k, cid in enumerate(todo, 1):
        if MAX_PULLS and k > MAX_PULLS:
            break
        g = grid[cid]
        total, ab = gbif_cell(g["lat_min"], g["lat_max"], g["lon_min"], g["lon_max"],
                              TAXA["birds"], year=YEARS)
        cache[cid] = {"total": total, "ab": ab}
        if k % 25 == 0:
            save_cache(CACHE_WIN, cache)
            print("  %d/%d  %.0fs" % (k, len(todo), time.time() - t0), flush=True)
        time.sleep(0.3)
    if todo:
        save_cache(CACHE_WIN, cache)
    left = sum(1 for cid in d.cell_id if cid not in cache)
    if left:
        print("STOPPED with %d cells still to pull (MAX_PULLS=%s); re-run to continue"
              % (left, MAX_PULLS))
        return False

    trunc = sum(1 for cid in d.cell_id if len(cache[cid]["ab"]) >= FACET_LIMIT)
    if trunc:
        sys.exit("ABORT: %d cells hit the facet limit; raise FACET_LIMIT" % trunc)
    d = d.copy()
    d["total_w"] = [cache[c]["total"] for c in d.cell_id]
    d["rich_w"] = [hurlbert_rarefy(cache[c]["ab"], RARE_N) for c in d.cell_id]
    d["rich_w"] = d.rich_w.astype(float)
    d["log_effort_w"] = np.log10(d.total_w.clip(lower=1))
    print("facet-truncated cells: 0")
    print("records 2019-2023 as share of 2000-2024 (median over cells): %.2f"
          % (d.total_w / d.total_records.clip(lower=1)).median())
    both = d.dropna(subset=["rich_w"])
    print("cells that still have %d species-identified records in 2019-2023: %d of %d"
          % (RARE_N, len(both), len(d)))
    print("correlation of rarefied richness, 2019-23 vs 2000-24 (n=%d): %.3f"
          % (len(both), both[["rich_w", "rarefied"]].corr().iloc[0, 1]))
    chain(d, "rarefied", "log_effort", "WIN", "2000-24 records, all cells")
    chain(both, "rich_w", "log_effort_w", "WIN", "2019-23 records")
    chain(both, "rarefied", "log_effort", "WIN", "2000-24 records, same cells")
    return True


def main():
    d = load()
    part_coverage(d)
    done = part_timewindow(d)
    pd.DataFrame(OUT).to_csv(os.path.join(DATA, "grain_0p5_sensitivity.csv"), index=False)
    if not done:
        sys.exit(2)


if __name__ == "__main__":
    main()
