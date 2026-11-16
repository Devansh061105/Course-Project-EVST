# -*- coding: utf-8 -*-
"""Extension F: protected land, survey effort, and the richness-productivity link.

Added 2026-11-16 (scope lock lifted a second time by the user; DECISIONS.md).
The plan's closing section is about conservation policy. Three questions the
existing data can answer once each cell has a protected fraction:

  F1  Do birdwatchers concentrate on protected land?  (effort ~ protection)
      If so, citizen-science richness maps are partly maps of where parks are.
  F2  Are more-protected cells richer or more productive than their climate
      predicts?  (richness, GPP ~ protection + controls)
  F3  Is the richness-productivity slope different where more land is protected?
      (GPP ~ richness x protection + controls)

Protected fraction of each cell's LAND area, from the 0.05-degree WDPA grids in
data/gee_extras.npz, under two definitions:
  strict  IUCN management categories Ia-IV (reserves, national parks, sanctuaries)
  all     every designated WDPA polygon (in India this adds ~180,000 Reserve and
          Protected Forest polygons; in China the public WDPA is incomplete)
Run at 1 degree and 0.5 degree. Standardised coefficients, SEs clustered by
ecoregion. Writes data/protected_1p0.csv, data/protected_0p5.csv and
data/extension_f_estimates.csv.
"""
import os
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
RES = 0.05
EST = []


def z(s):
    return (s - s.mean()) / s.std()


def cell_fraction(lat_c, lon_c, size, grid, land):
    n = int(round(size / RES))
    out = np.full(len(lat_c), np.nan)
    for k, (la, lo) in enumerate(zip(lat_c, lon_c)):
        j0 = int(round((31 - (la + size / 2)) / RES)); i0 = int(round((lo - size / 2 - 68) / RES))
        p = grid[j0:j0 + n, i0:i0 + n]; l = land[j0:j0 + n, i0:i0 + n]
        if l.any():
            out[k] = np.clip(p[l], 0, 1).mean()
    return out


def fit(d, y, cols, fe=False, inter=None):
    X = pd.DataFrame({c: z(d[c].astype(float)) for c in cols})
    if inter:
        X["inter"] = X[inter[0]] * X[inter[1]]
    if fe:
        X = pd.concat([X, pd.get_dummies(d.eco_name, prefix="fe", drop_first=True,
                                         dtype=float)], axis=1)
    return sm.OLS(z(d[y].astype(float)), sm.add_constant(X)).fit(
        cov_type="cluster", cov_kwds={"groups": d.eco_name})


def line(tag, label, m, col, key):
    print("  %-52s beta %+.3f  se %.3f  p = %.4f" % (label, m.params[col], m.bse[col], m.pvalues[col]))
    EST.append({"grain": tag, "quantity": key, "beta": m.params[col], "se": m.bse[col],
                "p": m.pvalues[col], "n": int(m.nobs)})


def run(d, tag, rich):
    clim = ["temp_c", "precip_mm_yr"]
    print("\n=== %s degree: n = %d modelled cells ===" % (tag, len(d)))
    for key, name in (("prot_strict", "strict (IUCN Ia-IV)"), ("prot_all", "all WDPA")):
        print("protected fraction, %s: mean %.3f, median %.3f, cells with none %.0f%%, "
              "cells above 10%% %.0f%%" % (name, d[key].mean(), d[key].median(),
                                           100 * (d[key] == 0).mean(), 100 * (d[key] > 0.1).mean()))
    for key, name in (("prot_strict", "strict"), ("prot_all", "all")):
        print(" protection definition: %s" % name)
        line(tag, "F1 effort ~ protection + climate", fit(d, "log_effort", [key] + clim), key,
             "F1 effort ~ protection (%s)" % name)
        line(tag, "F1 same, within ecoregions", fit(d, "log_effort", [key] + clim, fe=True), key,
             "F1 within (%s)" % name)
        line(tag, "F2 raw richness ~ protection + climate", fit(d, "obs_richness", [key] + clim),
             key, "F2 raw richness (%s)" % name)
        line(tag, "F2 corrected richness ~ protection + effort + climate",
             fit(d, rich, [key, "log_effort"] + clim), key, "F2 corrected richness (%s)" % name)
        line(tag, "F2 GPP ~ protection + climate", fit(d, "gpp", [key] + clim), key,
             "F2 GPP (%s)" % name)
        line(tag, "F2 GPP ~ protection + climate, within ecoregions",
             fit(d, "gpp", [key] + clim, fe=True), key, "F2 GPP within (%s)" % name)
        m = fit(d, "gpp", [rich, key, "log_effort"] + clim, inter=(rich, key))
        line(tag, "F3 richness x protection interaction (GPP model)", m, "inter",
             "F3 interaction (%s)" % name)
        print("  %-52s beta %+.3f  (p = %.4f)" % ("   richness main effect in that model",
                                                 m.params[rich], m.pvalues[rich]))
        if name == "strict":
            f1 = fit(d, "log_effort", [key] + clim)
            print("PROT %s: effort ~ strict protection beta = %+.3f (p = %.4f); "
                  "richness x protection interaction = %+.3f (p = %.4f)"
                  % (tag, f1.params[key], f1.pvalues[key], m.params["inter"], m.pvalues["inter"]))
    for name, s in (("cells with strict protection > 5%", d[d.prot_strict > 0.05]),
                    ("cells with no strict protection", d[d.prot_strict == 0])):
        if len(s) > 25 and s.eco_name.nunique() > 5:
            mm = fit(s, "gpp", [rich, "log_effort"] + clim)
            print("  slope in %-36s n=%-4d richness beta %+.3f  se %.3f  p = %.4f"
                  % (name, len(s), mm.params[rich], mm.bse[rich], mm.pvalues[rich]))


def main():
    g = np.load(os.path.join(DATA, "gee_extras.npz"))
    land = np.load(os.path.join(DATA, "terrain_grid_0p05.npz"))["lc"] > 0
    strict, allp = g["protected_strict"], g["protected"]

    full = pd.read_csv(os.path.join(DATA, "final", "biodiversity_productivity_1deg.csv"))
    full["prot_strict"] = cell_fraction(full.lat_c.values, full.lon_c.values, 1.0, strict, land)
    full["prot_all"] = cell_fraction(full.lat_c.values, full.lon_c.values, 1.0, allp, land)
    c = pd.read_csv(os.path.join(DATA, "countries_1p0.csv"))
    lc = full[full.prot_strict.notna()].merge(c, on="cell_id", how="left")
    print("protected share of land by country (1-degree land cells; countries with >= 10 cells):")
    t = lc.groupby("country").agg(cells=("prot_strict", "size"), strict=("prot_strict", "mean"),
                                  all=("prot_all", "mean"))
    for k, r in t[t.cells >= 10].sort_values("cells", ascending=False).iterrows():
        print("  %-12s cells %-4d strict %5.1f%%   all WDPA %5.1f%%"
              % (k, r.cells, 100 * r.strict, 100 * r["all"]))
    full[["cell_id", "lat_c", "lon_c", "prot_strict", "prot_all"]].to_csv(
        os.path.join(DATA, "protected_1p0.csv"), index=False)

    d1 = full[(full.in_model == 1)].dropna(subset=["eco_name", "prot_strict"]).reset_index(drop=True)
    run(d1, "1.0", "rarefied_250")
    # The public WDPA holds almost none of India's national parks and sanctuaries
    # (strict cover 0.2% here against roughly 5% in reality) and is incomplete for
    # China, so the same models are repeated without those two countries.
    d1 = d1.merge(c, on="cell_id", how="left")
    sub1 = d1[~d1.country.isin(["India", "China"])].reset_index(drop=True)
    run(sub1, "1.0 excl. India and China", "rarefied_250")

    m5 = pd.read_csv(os.path.join(DATA, "merged_cells_0p5.csv"))
    e5 = pd.read_csv(os.path.join(DATA, "ecoregions_0p5.csv"))[["cell_id", "eco_name"]]
    m5["prot_strict"] = cell_fraction(m5.lat_c.values, m5.lon_c.values, 0.5, strict, land)
    m5["prot_all"] = cell_fraction(m5.lat_c.values, m5.lon_c.values, 0.5, allp, land)
    m5[["cell_id", "lat_c", "lon_c", "prot_strict", "prot_all"]].to_csv(
        os.path.join(DATA, "protected_0p5.csv"), index=False)
    d5 = m5[m5.gpp.notna() & m5.wc_mode.notna() & ~m5.wc_mode.isin([40, 50, 80])
            & (m5.total_records >= 20) & m5.rarefied.notna() & m5.temp_c.notna()
            & m5.precip_mm_yr.notna()].merge(e5, on="cell_id", how="left")
    d5 = d5.dropna(subset=["eco_name", "prot_strict"]).reset_index(drop=True)
    run(d5, "0.5", "rarefied")
    parent = full[["lat_c", "lon_c", "cell_id"]].merge(c, on="cell_id", how="left")
    key = dict(zip(zip(parent.lat_c, parent.lon_c), parent.country))
    d5["country"] = [key.get((np.floor(a) + 0.5, np.floor(b) + 0.5))
                     for a, b in zip(d5.lat_c, d5.lon_c)]
    sub5 = d5[~d5.country.isin(["India", "China"])].reset_index(drop=True)
    run(sub5, "0.5 excl. India and China", "rarefied")
    pd.DataFrame(EST).to_csv(os.path.join(DATA, "extension_f_estimates.csv"), index=False)


if __name__ == "__main__":
    main()
