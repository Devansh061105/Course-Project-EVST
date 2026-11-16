# -*- coding: utf-8 -*-
"""Extension A, tested by experiment: does rarefaction really remove survey effort?

Extension A shows that rarefied richness is far less correlated with effort than
raw richness. That is a correlation across different places. This script tests
the correction directly, on the SAME place: take heavily surveyed cells, throw
away records at random until they look as poorly surveyed as the Thar Desert
or less, and see what each richness measure does.

  A correct effort correction should give the same answer for a cell whether we
  keep all of its records or a random 1% of them. Raw richness should collapse.

Method. For each of the best-surveyed modelled cells, draw random subsamples of
m records without replacement from its species-abundance vector (multivariate
hypergeometric), for m from 250 up to the full cell. For each subsample compute
raw richness and Hurlbert-rarefied richness at n = 250. Repeat REPS times.

Then a second experiment at the level of the whole analysis: thin EVERY modelled
cell to at most CAP records, recompute rarefied richness, refit the corrected
model, and compare the richness coefficient with the full-data +0.273.

Reads the cached pull only (data/gbif_cache.json). No network.
Writes data/effort_simulation_curves.csv and data/effort_simulation_refit.csv.
"""
import json
import os
import sys

import numpy as np
import pandas as pd
import statsmodels.api as sm

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
sys.path.insert(0, HERE)
from gbif_lib import hurlbert_rarefy

RNG = np.random.default_rng(2026)
REPS = 200
LEVELS = [250, 500, 1000, 3000, 10000, 30000, 100000]
N_CELLS = 12
CAPS = [250, 500, 1000, 3000, 10000]
REFIT_REPS = 50


def z(s):
    return (s - s.mean()) / s.std()


def thin(ab, m):
    """Random subsample of m records without replacement."""
    return RNG.multivariate_hypergeometric(ab, m)


def main():
    cache = json.load(open(os.path.join(DATA, "gbif_cache.json"), encoding="utf-8"))
    model = pd.read_csv(os.path.join(DATA, "model_cells.csv"))
    ab = {c: np.array(cache["birds|" + c]["ab"], dtype=np.int64) for c in model.cell_id}

    # ---- experiment 1: one cell at many effort levels ----------------------
    top = model.sort_values("sp_resolved_records", ascending=False).head(N_CELLS)
    rows = []
    for r in top.itertuples():
        a = ab[r.cell_id]; N = int(a.sum())
        full_raw = int((a > 0).sum()); full_rare = hurlbert_rarefy(a.tolist(), 250)
        for m in LEVELS:
            if m >= N:
                continue
            raw = np.empty(REPS); rare = np.empty(REPS)
            for k in range(REPS):
                s = thin(a, m); s = s[s > 0]
                raw[k] = len(s); rare[k] = hurlbert_rarefy(s.tolist(), 250)
            rows.append({"cell_id": r.cell_id, "records_full": N, "records_kept": m,
                         "raw_full": full_raw, "raw_mean": raw.mean(),
                         "raw_ratio": raw.mean() / full_raw,
                         "rare_full": full_rare, "rare_mean": rare.mean(),
                         "rare_sd": rare.std(), "rare_ratio": rare.mean() / full_rare})
    cur = pd.DataFrame(rows)
    cur.to_csv(os.path.join(DATA, "effort_simulation_curves.csv"), index=False)
    print("=== Experiment 1: %d best-surveyed cells (%s to %s identified records), "
          "%d random thinnings each ===" % (N_CELLS, f"{top.sp_resolved_records.min():,}",
                                            f"{top.sp_resolved_records.max():,}", REPS))
    print("%-14s %22s %26s %18s" % ("records kept", "raw richness / full", "rarefied richness / full",
                                    "rarefied SD (spp)"))
    for m, g in cur.groupby("records_kept"):
        print("%-14s %22.3f %26.3f %18.2f" % (f"{m:,}", g.raw_ratio.mean(), g.rare_ratio.mean(),
                                              g.rare_sd.mean()))
    lo = cur[cur.records_kept == 250]
    print("SIM at 250 records kept: raw richness falls to %.1f%% of its full value; "
          "rarefied richness stays at %.1f%%" % (100 * lo.raw_ratio.mean(),
                                                 100 * lo.rare_ratio.mean()))
    worst = (cur.rare_ratio - 1).abs().max()
    print("SIM largest bias of the mean rarefied richness at any thinning level: %.2f%%"
          % (100 * worst))

    # ---- experiment 2: thin the whole dataset and refit --------------------
    X0 = ["log_effort", "temp_c", "precip_mm_yr"]
    full = sm.OLS(z(model.gpp), sm.add_constant(pd.DataFrame(
        {"rich": z(model.rarefied_250), **{c: z(model[c]) for c in X0}}))).fit()
    print("\n=== Experiment 2: every modelled cell thinned to at most CAP records, "
          "model refitted (%d repeats) ===" % REFIT_REPS)
    print("full data: richness beta = %+.3f (n = %d)" % (full.params["rich"], len(model)))
    out = []
    for cap in CAPS:
        betas = []; rr = []
        for _ in range(REFIT_REPS):
            rare = np.empty(len(model)); eff = np.empty(len(model))
            for i, c in enumerate(model.cell_id):
                a = ab[c]; N = int(a.sum())
                s = thin(a, cap) if N > cap else a
                s = s[s > 0]
                rare[i] = hurlbert_rarefy(s.tolist(), 250); eff[i] = np.log10(min(N, cap))
            d = pd.DataFrame({"rich": z(pd.Series(rare)), "temp_c": z(model.temp_c),
                              "precip_mm_yr": z(model.precip_mm_yr)})
            if cap > 250:                       # at cap 250 every cell has the same effort
                d["log_effort"] = z(pd.Series(eff))
            f = sm.OLS(z(model.gpp), sm.add_constant(d)).fit()
            betas.append(f.params["rich"])
            rr.append(np.corrcoef(rare, model.rarefied_250)[0, 1])
        b = np.array(betas)
        out.append({"cap": cap, "beta_mean": b.mean(), "beta_lo": np.percentile(b, 2.5),
                    "beta_hi": np.percentile(b, 97.5), "r_with_full": np.mean(rr),
                    "beta_full": full.params["rich"]})
        print("REFIT cap %-6s beta = %+.3f [%+.3f, %+.3f]   r with full-data rarefied "
              "richness = %.3f" % (f"{cap:,}", b.mean(), np.percentile(b, 2.5),
                                   np.percentile(b, 97.5), np.mean(rr)))
    pd.DataFrame(out).to_csv(os.path.join(DATA, "effort_simulation_refit.csv"), index=False)


if __name__ == "__main__":
    main()
