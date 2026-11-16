# -*- coding: utf-8 -*-
"""Extension D: is the result specific to birds? Vascular plants as a second taxon.

Added 2026-11-16 at the user's request (scope lock lifted; docs/DECISIONS.md).
Plants are the group biodiversity-productivity theory is actually about, and
their GBIF records come from herbaria and iNaturalist rather than eBird, so
they carry a different sampling bias from the bird data.

Same cells, mask, climate controls and model chain as the bird analysis:
  naive -> rarefied alone -> corrected (HC3) -> cluster-robust by ecoregion
  -> ecoregion fixed effects -> spatial error model, for GPP and NPP,
with the bird model refitted on the SAME cells so the two taxa are compared
like for like.

It also reports how well rarefaction works for plants at all. A regional flora
has thousands of species and most cells hold a few hundred records, so a
rarefied sample is close to "every record a different species": the measure has
little room to vary and sample coverage is low. Those diagnostics are printed
first because they limit what the plant models can show.

Needs data/gbif_cells_plants.csv and data/gbif_cache_plants.json
(gbif_pull_taxon2.py). Writes data/plants_model_cells.csv.
"""
import json
import os
import sys
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm, spearmanr
from spreg import ML_Error

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
sys.path.insert(0, HERE)
from weights_sensitivity import queen_from_grid
from coverage_rarefaction import coverage_at

LEVELS = (50, 100, 250)
PRIMARY = 100
CLIM = ["temp_c", "precip_mm_yr"]
EST = []            # every chain estimate, for fig 10 (data/extension_d_estimates.csv)
CASES = {"Western Ghats": (8, 16, 74, 77), "Thar Desert": (25, 30, 69, 74),
         "Eastern Himalaya": (26, 29, 88, 97)}


def z(s):
    return (s - s.mean()) / s.std()


def load():
    m = pd.read_csv(os.path.join(DATA, "merged_cells.csv"))
    m["wc_mode"] = m.wc_mode.round()
    p = pd.read_csv(os.path.join(DATA, "gbif_cells_plants.csv"))
    e = pd.read_csv(os.path.join(DATA, "ecoregions_1p0.csv"))
    d = m.merge(p, on="cell_id", validate="one_to_one").merge(
        e[["cell_id", "eco_name"]], on="cell_id", how="left")
    if d.plant_facet_truncated.sum():
        raise SystemExit("%d cells hit the plant facet limit: raise "
                         "FACET_LIMIT_PLANTS and re-pull them before modelling"
                         % d.plant_facet_truncated.sum())
    d["plant_log_effort"] = np.log10(d.plant_total_records.clip(lower=1))
    nat = d[d.is_land.astype(bool) & ~d.wc_mode.isin([40, 50, 80]) & d.gpp.notna()
            & d.temp_c.notna() & d.precip_mm_yr.notna()].copy()
    return d, nat


def ols(d, y, cols, cluster=None, fe=None):
    X = pd.DataFrame({c: z(d[c].astype(float)) for c in cols})
    if fe:
        X = pd.concat([X, pd.get_dummies(d[fe], prefix="fe", drop_first=True,
                                         dtype=float)], axis=1)
    X = sm.add_constant(X)
    yy = z(d[y].astype(float))
    if cluster is not None:
        return sm.OLS(yy, X).fit(cov_type="cluster", cov_kwds={"groups": d[cluster]})
    return sm.OLS(yy, X).fit(cov_type="HC3")


def sem(d, y, cols):
    X = np.column_stack([z(d[c].astype(float)).values for c in cols])
    w = queen_from_grid(d.lat_c.values, d.lon_c.values, 1.0)
    w.transform = "r"
    s = ML_Error(z(d[y].astype(float)).values.reshape(-1, 1), X, w=w)
    b = float(s.betas[1][0]); se = float(np.sqrt(s.vm[1, 1]))
    return b, se, 2 * (1 - norm.cdf(abs(b / se))), float(s.lam)


def line(label, m, col, tag=None, y=None, spec=None):
    if spec:
        EST.append({"taxon": tag, "response": y, "spec": spec, "beta": m.params[col],
                    "se": m.bse[col], "p": m.pvalues[col], "n": int(m.nobs)})
    print("  %-46s n=%-4d beta %+.3f  se %.3f  p=%.4f  R2=%.3f"
          % (label, int(m.nobs), m.params[col], m.bse[col], m.pvalues[col], m.rsquared))


def chain(d, rich, effort, tag):
    cols = [rich, effort] + CLIM
    de = d.dropna(subset=["eco_name"])
    for y in ("gpp", "npp"):
        dy = d.dropna(subset=[y]); dye = de.dropna(subset=[y])
        print(" %s, response %s" % (tag, y.upper()))
        line("rarefied richness alone", ols(dy, y, [rich]), rich, tag, y, "alone")
        line("corrected: + effort + temp + precip (HC3)", ols(dy, y, cols), rich, tag, y,
             "corrected")
        base = ols(dy, y, [effort] + CLIM)
        full = ols(dy, y, cols)
        print("  %-46s %.3f -> %.3f (+%.1f points)" % (
            "R2 without -> with richness", base.rsquared, full.rsquared,
            100 * (full.rsquared - base.rsquared)))
        line("corrected, SEs clustered by ecoregion", ols(dye, y, cols, "eco_name"), rich)
        line("+ ecoregion fixed effects (within)", ols(dye, y, cols, "eco_name", "eco_name"),
             rich, tag, y, "within")
        b, se, p, lam = sem(dy, y, cols)
        EST.append({"taxon": tag, "response": y, "spec": "sem", "beta": b, "se": se,
                    "p": p, "n": len(dy)})
        print("  %-46s n=%-4d beta %+.3f  p=%.4f  lambda=%.2f"
              % ("spatial error model", len(dy), b, p, lam))


def main():
    d, nat = load()
    cache = json.load(open(os.path.join(DATA, "gbif_cache_plants.json"), encoding="utf-8"))
    print("cells: %d in grid, %d natural-cover land cells with GPP and climate"
          % (len(d), len(nat)))
    print("plant records in all cells: %d total, %d identified to species"
          % (d.plant_total_records.sum(), d.plant_sp_resolved_records.sum()))
    print("plant records per natural-cover cell: median %d (birds: %d)"
          % (nat.plant_total_records.median(), nat.total_records.median()))

    print("\n=== D0. Does rarefaction work for plants? ===")
    print("%-6s %6s %12s %10s %12s %14s %14s" % (
        "level", "cells", "median E[S]", "E[S]/n", "CV of E[S]", "coverage at n",
        "r(E[S],effort)"))
    for n in LEVELS:
        s = nat.dropna(subset=["plant_rarefied_%d" % n])
        cov = []
        for cid in s.cell_id:
            x = np.array(cache["plants|" + cid]["ab"], dtype=float)
            cov.append(coverage_at(x, x.sum(), n))
        v = s["plant_rarefied_%d" % n]
        print("%-6d %6d %12.1f %10.2f %12.3f %14.2f %+14.3f" % (
            n, len(s), v.median(), v.median() / n, v.std() / v.mean(),
            np.median(cov), np.corrcoef(v, s.plant_log_effort)[0, 1]))
    sb = nat.dropna(subset=["rarefied_250"])
    fin = pd.read_csv(os.path.join(DATA, "final", "biodiversity_productivity_1deg.csv"),
                      usecols=["cell_id", "cov_at_250"])
    bcov = sb.merge(fin, on="cell_id").cov_at_250.median()
    print("birds  %6d %12.1f %10.2f %12.3f %14.2f %+14.3f   (rarefied at 250, for scale)" % (
        len(sb), sb.rarefied_250.median(), sb.rarefied_250.median() / 250,
        sb.rarefied_250.std() / sb.rarefied_250.mean(), bcov,
        np.corrcoef(sb.rarefied_250, sb.log_effort)[0, 1]))
    s = nat[nat.plant_sp_resolved_records >= PRIMARY]
    print("raw plant richness vs log effort: r = %+.3f (birds, raw: %+.3f)" % (
        np.corrcoef(s.plant_obs_richness, s.plant_log_effort)[0, 1],
        np.corrcoef(sb.obs_richness, sb.log_effort)[0, 1]))

    rich = "plant_rarefied_%d" % PRIMARY
    P = nat.dropna(subset=[rich]).reset_index(drop=True)
    print("\n=== D1. Plant model chain (rarefied at %d; %d cells) ===" % (PRIMARY, len(P)))
    line("naive: raw plant richness alone", ols(P, "gpp", ["plant_obs_richness"]),
         "plant_obs_richness")
    chain(P, rich, "plant_log_effort", "plants")
    m = ols(P, "gpp", [rich, "plant_log_effort"] + CLIM)
    print("PLANTS corrected GPP beta = %+.3f (p = %.4f, n = %d)"
          % (m.params[rich], m.pvalues[rich], int(m.nobs)))

    print("\n=== D2. Rarefaction level sensitivity (corrected model, GPP) ===")
    for n in LEVELS:
        c = "plant_rarefied_%d" % n
        s = nat.dropna(subset=[c])
        line("plants rarefied at %d" % n, ols(s, "gpp", [c, "plant_log_effort"] + CLIM), c)

    B = P.dropna(subset=["rarefied_250"]).reset_index(drop=True)
    print("\n=== D3. Birds refitted on the cells that have both taxa (%d cells) ===" % len(B))
    chain(B, "rarefied_250", "log_effort", "birds (same cells)")
    print(" Both taxa in one model (GPP):")
    both = ols(B, "gpp", ["rarefied_250", rich, "log_effort", "plant_log_effort"] + CLIM)
    line("bird richness | plants + controls", both, "rarefied_250")
    line("plant richness | birds + controls", both, rich)
    be = B.dropna(subset=["eco_name"])
    bothfe = ols(be, "gpp", ["rarefied_250", rich, "log_effort", "plant_log_effort"] + CLIM,
                 "eco_name", "eco_name")
    line("bird richness, + ecoregion FE", bothfe, "rarefied_250")
    line("plant richness, + ecoregion FE", bothfe, rich)

    print("\n=== D4. Do the two taxa agree on where diversity is high? ===")
    r_raw = np.corrcoef(B.obs_richness, B.plant_obs_richness)[0, 1]
    r_cor = np.corrcoef(B.rarefied_250, B[rich])[0, 1]
    rs = spearmanr(B.rarefied_250, B[rich])
    print("bird vs plant richness, raw counts:      r = %+.3f" % r_raw)
    print("bird vs plant richness, effort-corrected: r = %+.3f  (Spearman %+.3f, p = %.4f)"
          % (r_cor, rs.correlation, rs.pvalue))
    print("bird effort vs plant effort (log records): r = %+.3f"
          % np.corrcoef(B.log_effort, B.plant_log_effort)[0, 1])
    rb = ols(B, "rarefied_250", CLIM).resid
    rp = ols(B, rich, CLIM).resid
    print("corrected richness, climate partialled out: r = %+.3f"
          % np.corrcoef(rb, rp)[0, 1])

    print("\n=== D5. Case-study regions, plants ===")
    print("%-17s %6s %14s %10s %14s %14s" % ("region", "cells", "median records",
                                              "raw S", "rarefied@%d" % PRIMARY,
                                              "bird rare@250"))
    for name, (a, b, c, e) in CASES.items():
        s = P[P.lat_c.between(a, b) & P.lon_c.between(c, e)]
        if len(s) == 0:
            print("%-17s no cell with >= %d identified plant records" % (name, PRIMARY))
            continue
        print("%-17s %6d %14d %10.0f %14.1f %14.1f" % (
            name, len(s), s.plant_total_records.median(), s.plant_obs_richness.median(),
            s[rich].median(), s.rarefied_250.median()))

    keep = ["cell_id", "lat_c", "lon_c", "gpp", "npp", "temp_c", "precip_mm_yr",
            "eco_name", "plant_total_records", "plant_sp_resolved_records",
            "plant_obs_richness", "plant_log_effort"] + [
            "plant_rarefied_%d" % n for n in LEVELS] + [
            "total_records", "obs_richness", "rarefied_250", "log_effort"]
    P[keep].to_csv(os.path.join(DATA, "plants_model_cells.csv"), index=False)
    pd.DataFrame(EST).to_csv(os.path.join(DATA, "extension_d_estimates.csv"), index=False)
    print("\nwrote data/plants_model_cells.csv (%d cells)" % len(P))


if __name__ == "__main__":
    main()
