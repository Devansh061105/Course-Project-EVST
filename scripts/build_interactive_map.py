# -*- coding: utf-8 -*-
"""Build the two interactive maps:

  docs/interactive_map.html     flat per-cell atlas: switchable layers, a per-cell
                                record and a linked richness-GPP scatter
  docs/interactive_map_3d.html  3D terrain: ground coloured by land cover, greenness,
                                productivity or elevation; one column per cell for
                                bird or plant richness; click any place for its record

Both are single self-contained HTML files (no server, no map tiles). The 3D page
loads three.js from a CDN and embeds the 0.05-degree grids from
data/terrain_grid_0p05.npz (gee_terrain_grid.py); it is skipped if that file is
missing.

Reads only finished tables:
  data/final/biodiversity_productivity_1deg.csv   per-cell dataset
  data/countries_1p0.csv                          country label per land cell
  data/local_slopes_1p0.csv                       local_slopes.py (optional)
  data/gbif_cells_plants.csv                      gbif_pull_taxon2.py (optional)
The model residual is refitted here with the corrected specification
(standardised GPP ~ rarefied richness + log effort + temperature + precipitation).

Usage: python build_interactive_map.py [fragment_dir]
The optional argument also writes each page body without the <html> wrapper
(atlas_2d.html, atlas_3d.html) into that directory.
"""
import base64
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
DATA = os.path.join(ROOT, "data")
WC = {10: "Tree cover", 20: "Shrubland", 30: "Grassland", 40: "Cropland",
      50: "Built-up", 60: "Bare or sparse", 70: "Snow and ice", 80: "Water",
      90: "Wetland", 95: "Mangrove", 100: "Moss and lichen"}


def z(s):
    return (s - s.mean()) / s.std()


def num(v, nd):
    return None if pd.isna(v) else round(float(v), nd)


def main():
    d = pd.read_csv(os.path.join(DATA, "final", "biodiversity_productivity_1deg.csv"))
    d = d[d.is_land.astype(str).isin(["True", "1", "1.0"])].copy()
    d["wc_mode"] = d.wc_mode.round()
    d = d.merge(pd.read_csv(os.path.join(DATA, "countries_1p0.csv")), on="cell_id", how="left")

    m = d[d.in_model == 1]
    X = np.column_stack([np.ones(len(m))] + [z(m[c]).values for c in
                        ("rarefied_250", "log_effort", "temp_c", "precip_mm_yr")])
    y = z(m.gpp).values
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    d["resid"] = pd.Series(y - X @ b, index=m.index)

    ls_path = os.path.join(DATA, "local_slopes_1p0.csv")
    if os.path.exists(ls_path):
        ls = pd.read_csv(ls_path)[["cell_id", "local_beta_richness", "sig_adjusted"]]
        d = d.merge(ls, on="cell_id", how="left")
    else:
        d["local_beta_richness"] = np.nan; d["sig_adjusted"] = np.nan
    pl_path = os.path.join(DATA, "gbif_cells_plants.csv")
    if os.path.exists(pl_path):
        d = d.merge(pd.read_csv(pl_path), on="cell_id", how="left")
    else:
        for c in ("plant_total_records", "plant_obs_richness", "plant_rarefied_100"):
            d[c] = np.nan

    # Optional per-cell extras from the 2026-11-16 analyses; each is skipped if absent.
    extras = (("survey_gaps_1p0.csv", ["completeness", "priority"]),
              ("extension_e_all_cells.csv", ["gpp_cv_detrended", "trend"]),
              ("protected_1p0.csv", ["prot_strict", "prot_all"]),
              ("gbif_cells_lepidoptera_1p0.csv", ["lepid_total_records", "lepid_rarefied_100"]))
    for name, cols in extras:
        path = os.path.join(DATA, name)
        if os.path.exists(path):
            d = d.merge(pd.read_csv(path)[["cell_id"] + cols], on="cell_id", how="left")
        else:
            for c in cols:
                d[c] = np.nan
    ts_path = os.path.join(DATA, "top_species_1p0.json")
    top = json.load(open(ts_path, encoding="utf-8")) if os.path.exists(ts_path) else {}

    cells = []
    for r in d.itertuples():
        status = "m" if r.in_model == 1 else ("c" if r.wc_mode in (40, 50) else "o")
        sp = top.get(r.cell_id, {})
        cells.append({
            "cp": num(r.completeness, 2), "pr": num(r.priority, 1),
            "cv": num(100 * r.gpp_cv_detrended, 1), "tr": num(r.trend, 2),
            "pa": num(r.prot_all, 2), "pst": num(r.prot_strict, 2),
            "ln": num(r.lepid_total_records, 0), "lpc": num(r.lepid_rarefied_100, 1),
            "tb": sp.get("birds", []), "tp": sp.get("plants", []),
            "id": r.cell_id, "la": r.lat_c, "lo": r.lon_c, "st": status,
            "cty": None if pd.isna(r.country) else r.country,
            "eco": None if pd.isna(r.eco_name) else r.eco_name,
            "wc": WC.get(int(r.wc_mode)) if not pd.isna(r.wc_mode) else None,
            "nat": num(r.natural_frac, 2), "n": num(r.total_records, 0),
            "so": num(r.obs_richness, 0), "sc": num(r.rarefied_250, 1),
            "gpp": num(r.gpp, 3), "npp": num(r.npp, 3), "t": num(r.temp_c, 1),
            "p": num(r.precip_mm_yr, 0), "res": num(r.resid, 2),
            "ls": num(r.local_beta_richness, 3),
            "lsig": int(r.sig_adjusted) if not pd.isna(r.sig_adjusted) else 0,
            "pn": num(r.plant_total_records, 0), "ps": num(r.plant_obs_richness, 0),
            "pc": num(r.plant_rarefied_100, 1),
            "cs": None if pd.isna(r.case_study) else r.case_study,
            "el": num(r.elev_mean, 0),
        })

    frag_dir = sys.argv[1] if len(sys.argv) > 1 else None
    emit("interactive_map_template.html", "interactive_map.html", "atlas_2d.html",
         json.dumps(cells, separators=(",", ":"), ensure_ascii=False), "/*__DATA__*/[]",
         'A 3D terrain version is in <a href="interactive_map_3d.html">interactive_map_3d.html</a>.',
         frag_dir)
    print("  %d land cells, %d modelled, %d with a local slope, %d with plant richness"
          % (len(cells), sum(c["st"] == "m" for c in cells),
             sum(c["ls"] is not None for c in cells), sum(c["pc"] is not None for c in cells)))

    tg = os.path.join(DATA, "terrain_grid_0p05.npz")
    if not os.path.exists(tg):
        print("3D page skipped: data/terrain_grid_0p05.npz not found (run gee_terrain_grid.py)")
        return
    g = np.load(tg)
    elev, lc, ndvi, gpp = g["elev"], g["lc"], g["ndvi"], g["gpp"]

    def enc(a):
        return base64.b64encode(np.ascontiguousarray(a).tobytes()).decode("ascii")

    def byte(a, hi):        # 0 = no data, 1..255 = 0..hi
        out = np.zeros(a.shape, np.uint8)
        ok = a > -9000
        out[ok] = 1 + np.round(np.clip(a[ok], 0, hi) / hi * 254).astype(np.uint8)
        return out

    grid = {"w": int(elev.shape[1]), "h": int(elev.shape[0]), "res": float(g["res"]),
            "elev": enc(np.clip(elev, 0, 65535).astype("<u2")),
            "lc": enc(np.where(lc > 0, lc, 0).astype(np.uint8)),
            "ndvi": enc(byte(ndvi, 0.9)), "gpp": enc(byte(gpp, 3.3))}
    # Overlay byte per pixel: bit 0 country border, bit 1 ecoregion boundary,
    # bits 2-7 protected fraction (all designated WDPA polygons) in 63 steps.
    ex = os.path.join(DATA, "gee_extras.npz")
    if os.path.exists(ex):
        x = np.load(ex)
        eco = x["eco_id"]
        edge = np.zeros(eco.shape, bool)
        edge[:, 1:] |= eco[:, 1:] != eco[:, :-1]
        edge[1:, :] |= eco[1:, :] != eco[:-1, :]
        edge &= lc > 0
        prot = np.round(np.clip(x["protected"], 0, 1) * 63).astype(np.uint8)
        prot[lc <= 0] = 0
        ov = ((x["border"] > 0).astype(np.uint8) | (edge.astype(np.uint8) << 1) | (prot << 2))
        grid["ov"] = enc(ov.astype(np.uint8))
    payload = json.dumps({"cells": cells, "grid": grid}, separators=(",", ":"),
                         ensure_ascii=False)
    emit("interactive_map3d_template.html", "interactive_map_3d.html", "atlas_3d.html",
         payload, "/*__DATA__*/{cells: [], grid: null}",
         'A flat version with more layers is in <a href="interactive_map.html">interactive_map.html</a>.',
         frag_dir)


def emit(template, out_name, frag_name, data, marker, nav, frag_dir):
    with open(os.path.join(HERE, template), encoding="utf-8") as f:
        tpl = f.read()
    assert marker in tpl and "<!--__NAV__-->" in tpl, template
    body = tpl.replace(marker, data)
    page = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '<style>body{margin:0}[hidden]{display:none!important}</style>\n</head>\n<body>\n'
            + body.replace("<!--__NAV__-->", nav) + "\n</body>\n</html>\n")
    out = os.path.join(ROOT, "docs", out_name)
    with open(out, "w", encoding="utf-8") as f:
        f.write(page)
    print("wrote %s (%.0f KB)" % (os.path.relpath(out, ROOT), len(page) / 1024))
    if frag_dir:
        fp = os.path.join(frag_dir, frag_name)
        with open(fp, "w", encoding="utf-8") as f:
            f.write(body.replace("<!--__NAV__-->", ""))
        print("wrote fragment %s" % fp)


if __name__ == "__main__":
    main()
