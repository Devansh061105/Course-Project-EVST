# -*- coding: utf-8 -*-
"""Shared helpers: GBIF occurrence queries, grid construction, Hurlbert rarefaction.

Design note: per-cell richness is obtained from ONE faceted search request
(facet=speciesKey), not by paginating occurrence records. The facet response
carries the full species-abundance vector for the cell, which is exactly the
input Hurlbert rarefaction needs. This avoids the 300-record page / 100k offset
limits described in the project plan's Step 3 entirely.
"""
import json
import math
import os
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.gbif.org/v1/occurrence/search?"
UA = {"User-Agent": "project9-biodiversity-coursework/0.1"}

# Facet ceiling. Probed live: a dense Western Ghats bird cell saturates at 451
# species, so 1200 leaves ample headroom. A cell returning exactly this many
# species is flagged as possibly truncated rather than silently trusted.
FACET_LIMIT = 1200

TAXA = {"birds": 212, "plants": 7707728}      # Aves (class), Tracheophyta (phylum)
YEAR_RANGE = "2000,2024"

# Case-study regions (plan Extension C) as (lat_min, lat_max, lon_min, lon_max)
CASE_STUDIES = {
    "western_ghats":     (8.0, 16.0, 74.0, 77.0),
    "deccan_plateau":    (15.0, 20.0, 75.0, 80.0),
    "eastern_himalaya":  (26.0, 29.0, 88.0, 97.0),
}

# Study region: covers all three case studies plus surrounding area for
# statistical power (plan Step 1). EPSG:4326, well below 60 deg lat.
REGION = {"lat_min": 5.0, "lat_max": 31.0, "lon_min": 68.0, "lon_max": 102.0}


def gbif_cell(lat_min, lat_max, lon_min, lon_max, taxon_key,
              year=YEAR_RANGE, facet_limit=FACET_LIMIT, retries=4):
    """Return (total_records, species_abundance_list) for one bounding box."""
    params = {
        "decimalLatitude": "%g,%g" % (lat_min, lat_max),
        "decimalLongitude": "%g,%g" % (lon_min, lon_max),
        "taxonKey": taxon_key,
        "hasCoordinate": "true",
        "hasGeospatialIssue": "false",
        "occurrenceStatus": "PRESENT",
        "year": year,
        "facet": "speciesKey",
        "facetLimit": facet_limit,
        "limit": 0,
    }
    url = API + urllib.parse.urlencode(params)
    delay = 2.0
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            d = json.load(urllib.request.urlopen(req, timeout=120))
            facets = d.get("facets") or []
            counts = facets[0]["counts"] if facets else []
            return d["count"], [c["count"] for c in counts]
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
            if attempt == retries - 1:
                raise
            time.sleep(delay)
            delay *= 2
    raise RuntimeError("unreachable")


def build_grid(cell_deg=1.0, region=REGION):
    """Systematic lat/lon grid. Returns list of dicts, EPSG:4326."""
    cells = []
    nlat = int(round((region["lat_max"] - region["lat_min"]) / cell_deg))
    nlon = int(round((region["lon_max"] - region["lon_min"]) / cell_deg))
    for i in range(nlat):
        for j in range(nlon):
            lat0 = region["lat_min"] + i * cell_deg
            lon0 = region["lon_min"] + j * cell_deg
            cells.append({
                "cell_id": "r%02dc%02d" % (i, j),
                "lat_min": round(lat0, 6), "lat_max": round(lat0 + cell_deg, 6),
                "lon_min": round(lon0, 6), "lon_max": round(lon0 + cell_deg, 6),
                "lat_c": round(lat0 + cell_deg / 2, 6),
                "lon_c": round(lon0 + cell_deg / 2, 6),
            })
    return cells


def grid_geojson(cells):
    """FeatureCollection for direct ingestion as an ee.FeatureCollection."""
    feats = []
    for c in cells:
        ring = [[c["lon_min"], c["lat_min"]], [c["lon_max"], c["lat_min"]],
                [c["lon_max"], c["lat_max"]], [c["lon_min"], c["lat_max"]],
                [c["lon_min"], c["lat_min"]]]
        feats.append({
            "type": "Feature",
            "properties": {k: c[k] for k in
                           ("cell_id", "lat_c", "lon_c", "lat_min", "lat_max",
                            "lon_min", "lon_max")},
            "geometry": {"type": "Polygon", "coordinates": [ring]},
        })
    return {"type": "FeatureCollection", "features": feats}


def cells_in_box(cells, box):
    """Cells whose centroid falls inside a (lat_min, lat_max, lon_min, lon_max) box."""
    a, b, c_, d = box
    return [x for x in cells if a <= x["lat_c"] <= b and c_ <= x["lon_c"] <= d]


def hurlbert_rarefy(abundances, n):
    """Expected species in a random sample of n individuals, drawn WITHOUT
    replacement (Hurlbert 1971, eq. 8):

        E[S_n] = sum_i [ 1 - C(N - N_i, n) / C(N, n) ]

    Computed in log space via lgamma so the binomials do not overflow for the
    large record counts typical of eBird-derived cells. Returns None when the
    cell holds fewer than n species-resolved records.
    """
    N = sum(abundances)
    if n <= 0 or N < n:
        return None

    def log_choose(a, k):
        if k < 0 or k > a:
            return None
        return (math.lgamma(a + 1) - math.lgamma(k + 1) - math.lgamma(a - k + 1))

    log_den = log_choose(N, n)
    exp_s = 0.0
    for ni in abundances:
        lc = log_choose(N - ni, n)
        if lc is None:          # species so abundant that N-ni < n
            exp_s += 1.0
        else:
            exp_s += 1.0 - math.exp(lc - log_den)
    return exp_s


def load_cache(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f)
    os.replace(tmp, path)
