# -*- coding: utf-8 -*-
"""Plan deliverable 2: the clean merged per-cell dataset, with a data dictionary.

Writes data/final/biodiversity_productivity_1deg.csv (884 rows, one per 1-degree
grid cell) and data/final/CODEBOOK.md. Everything is assembled from the pipeline
outputs; nothing is re-computed except in_model and case_study.
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
OUT = os.path.join(DATA, "final")
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, HERE)
from gbif_lib import CASE_STUDIES

m = pd.read_csv(os.path.join(DATA, "merged_cells.csv"))
m["wc_mode"] = m.wc_mode.round()
conf = pd.read_csv(os.path.join(DATA, "confounders_1p0.csv"))
eco = pd.read_csv(os.path.join(DATA, "ecoregions_1p0.csv"))
cov = pd.read_csv(os.path.join(DATA, "coverage_model_cells.csv"))
mod = pd.read_csv(os.path.join(DATA, "model_cells.csv"))

d = (m.merge(conf, on="cell_id", how="left")
       .merge(eco, on="cell_id", how="left")
       .merge(cov[["cell_id", "S_cov90", "S_cov95", "cov_at_250"]], on="cell_id", how="left"))
d["in_model"] = d.cell_id.isin(set(mod.cell_id)).astype(int)

CASES = {"Western Ghats": CASE_STUDIES["western_ghats"],
         "Thar Desert": (25.0, 30.0, 69.0, 74.0),
         "Eastern Himalaya": CASE_STUDIES["eastern_himalaya"]}
d["case_study"] = ""
for name, (a, b, c, e) in CASES.items():
    d.loc[d.lat_c.between(a, b) & d.lon_c.between(c, e), "case_study"] = name

cols = ["cell_id", "lat_c", "lon_c", "lat_min", "lat_max", "lon_min", "lon_max",
        "is_land", "wc_mode", "natural_frac", "excluded_frac", "water_frac",
        "total_records", "log_effort", "sp_resolved_records", "obs_richness",
        "facet_truncated", "below_min_records", "rarefied_50", "rarefied_100",
        "rarefied_250", "S_cov90", "S_cov95", "cov_at_250",
        "gpp", "npp", "ndvi", "evi", "temp_c", "precip_mm_yr",
        "elev_mean", "elev_sd", "ndvi_cv",
        "eco_id", "eco_name", "biome", "realm", "case_study", "in_model"]
missing = [c for c in cols if c not in d.columns]
assert not missing, missing
d = d[cols]
d.to_csv(os.path.join(OUT, "biodiversity_productivity_1deg.csv"), index=False)

DOC = {
 "cell_id": ("id", "Grid cell id rRRcCC (row from 5N, column from 68E)"),
 "lat_c / lon_c": ("deg", "Cell centroid (EPSG:4326)"),
 "lat_min..lon_max": ("deg", "Cell bounds; cells are 1x1 degree, 5-31N, 68-102E"),
 "is_land": ("0/1", "1 if WorldCover has coverage for the cell (open ocean = 0)"),
 "wc_mode": ("code", "Dominant ESA WorldCover v200 class, 500 m sampling (10 tree, 20 shrub, 30 grass, 40 crop, 50 built, 60 bare, 80 water, ...)"),
 "natural_frac": ("0-1", "Fraction of the cell in tree/shrub/grass/bare/wetland/mangrove/moss classes"),
 "excluded_frac": ("0-1", "Fraction cropland + built-up"),
 "water_frac": ("0-1", "Fraction permanent water"),
 "total_records": ("count", "GBIF bird occurrence records 2000-2024, georeferenced, no geospatial issue, PRESENT; Aves taxonKey 212"),
 "log_effort": ("log10", "log10(total_records), the sampling-effort covariate"),
 "sp_resolved_records": ("count", "Records identified to species (the rarefaction input; ~3% fewer than total_records)"),
 "obs_richness": ("species", "Observed species count (raw, effort-dependent)"),
 "facet_truncated": ("0/1", "1 if species list hit the GBIF facet limit (none do)"),
 "below_min_records": ("0/1", "1 if total_records < 20 (excluded from models)"),
 "rarefied_50/100/250": ("species", "Hurlbert (1971) expected species in a random sample of n species-resolved records; blank if the cell has fewer than n"),
 "S_cov90 / S_cov95": ("species", "Chao & Jost (2012) coverage-standardised richness at 90% / 95% sample coverage; blank if not reached"),
 "cov_at_250": ("0-1", "Sample coverage achieved by the fixed n=250 rarefaction"),
 "gpp / npp": ("kg C m-2 yr-1", "MODIS MOD17A3HGF v061, 2019-2023 mean, fill values masked"),
 "ndvi / evi": ("index", "MODIS MOD13Q1 v061, 2019-2023 mean of 16-day composites, fill masked"),
 "temp_c": ("deg C", "ERA5-Land 2 m air temperature, 2019-2023 mean"),
 "precip_mm_yr": ("mm/yr", "ERA5-Land total precipitation, 2019-2023 mean x 12"),
 "elev_mean / elev_sd": ("m", "SRTM 30 m elevation: cell mean and standard deviation (topographic heterogeneity)"),
 "ndvi_cv": ("ratio", "Mean per-pixel coefficient of variation of NDVI 2019-2023 (seasonality)"),
 "eco_id / eco_name / biome / realm": ("label", "RESOLVE Ecoregions 2017 polygon containing the cell centroid; blank for 394 cells: 254 open-ocean cells and 140 land cells whose centroid lies outside every polygon (mostly coastal)"),
 "case_study": ("label", "Extension C region box the centroid lies in, else blank"),
 "in_model": ("0/1", "1 for the 221 cells used in the main models: dominant class not cropland/built-up/water, >=250 species-identified records (needed to rarefy at n=250; this, not the nominal >=20-record rule, is the binding threshold), GPP and climate present"),
}
with open(os.path.join(OUT, "CODEBOOK.md"), "w", encoding="utf-8") as f:
    f.write("# Codebook: biodiversity_productivity_1deg.csv\n\n")
    f.write("884 rows (1-degree cells, 5-31N x 68-102E). Built by `scripts/make_dataset.py`.\n")
    f.write("Missing values are blank. Environmental values are 2019-2023 means; bird records 2000-2024.\n\n")
    f.write("| column | unit | description |\n|---|---|---|\n")
    for k, (u, t) in DOC.items():
        f.write("| `%s` | %s | %s |\n" % (k, u, t))
    f.write("\n## Provenance\nGBIF occurrences via live faceted API queries (no download DOI yet: register a "
            "derived dataset before publication). MOD17A3HGF v061 doi:10.5067/MODIS/MOD17A3HGF.061; "
            "MOD13Q1 v061 doi:10.5067/MODIS/MOD13Q1.061; ERA5-Land doi:10.5194/essd-13-4349-2021; "
            "ESA WorldCover v200 doi:10.5281/zenodo.7254221; SRTM doi:10.5067/MEaSUREs/SRTM/SRTMGL1.003; "
            "RESOLVE Ecoregions doi:10.1093/biosci/bix014.\n")

print("wrote %d rows x %d columns" % (d.shape[0], d.shape[1]))
print("in_model: %d | land: %d | with ecoregion: %d | case-study cells: %s"
      % (d.in_model.sum(), d.is_land.sum(), d.eco_name.notna().sum(),
         d.case_study.value_counts().drop("", errors="ignore").to_dict()))
print("columns with any blank: %s" % ", ".join(c for c in d.columns if d[c].isna().any()))
