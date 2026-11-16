# -*- coding: utf-8 -*-
"""Most-recorded bird and plant species per 1-degree land cell (for the maps).

The richness pulls keep only counts per species, not which species they are.
This asks GBIF for the top TOP_N species of each cell (one faceted request per
cell and taxon, same filters as the richness pulls) and then looks up each
species key once for its scientific and English name.

Caches (append-only, restartable; never delete):
  data/top_species_cache.json     "taxon|cell_id" -> [[speciesKey, records], ...]
  data/species_names_cache.json   speciesKey -> {"sci": ..., "en": ...}
Writes data/top_species_1p0.json for build_interactive_map.py.

Display only: no model uses these names.
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gbif_lib import API, TAXA, UA, YEAR_RANGE, load_cache, save_cache

DATA = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data"))
TOP_N = 4
TOPC = os.path.join(DATA, "top_species_cache.json")
NAMEC = os.path.join(DATA, "species_names_cache.json")


def get(url, retries=4):
    delay = 2.0
    for attempt in range(retries):
        try:
            return json.load(urllib.request.urlopen(
                urllib.request.Request(url, headers=UA), timeout=120))
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(delay)
            delay *= 2


m = pd.read_csv(os.path.join(DATA, "merged_cells.csv"))
p = pd.read_csv(os.path.join(DATA, "gbif_cells_plants.csv"))
d = m.merge(p, on="cell_id")
d = d[d.wc_mode.notna()]
todo = {"birds": d[d.total_records > 0], "plants": d[d.plant_total_records > 0]}

top = load_cache(TOPC)
t0 = time.time()
for taxon, cells in todo.items():
    for i, r in enumerate(cells.itertuples(), 1):
        ck = "%s|%s" % (taxon, r.cell_id)
        if ck in top:
            continue
        q = {"decimalLatitude": "%g,%g" % (r.lat_min, r.lat_max),
             "decimalLongitude": "%g,%g" % (r.lon_min, r.lon_max),
             "taxonKey": TAXA[taxon], "hasCoordinate": "true",
             "hasGeospatialIssue": "false", "occurrenceStatus": "PRESENT",
             "year": YEAR_RANGE, "facet": "speciesKey", "facetLimit": TOP_N, "limit": 0}
        res = get(API + urllib.parse.urlencode(q))
        f = res.get("facets") or []
        top[ck] = [[int(c["name"]), c["count"]] for c in (f[0]["counts"] if f else [])]
        save_cache(TOPC, top)
        if i % 100 == 0:
            print("  %s %d/%d  %.0fs" % (taxon, i, len(cells), time.time() - t0), flush=True)
        time.sleep(0.3)
print("top species cached for %d cell-taxon pairs" % len(top), flush=True)

names = load_cache(NAMEC)
keys = sorted({str(k) for v in top.values() for k, _ in v} - set(names))
for i, k in enumerate(keys, 1):
    s = get("https://api.gbif.org/v1/species/%s" % k)
    names[k] = {"sci": s.get("canonicalName") or s.get("scientificName") or k,
                "en": s.get("vernacularName") or ""}
    save_cache(NAMEC, names)
    if i % 100 == 0:
        print("  names %d/%d  %.0fs" % (i, len(keys), time.time() - t0), flush=True)
    time.sleep(0.3)

out = {}
for ck, lst in top.items():
    taxon, cid = ck.split("|")
    out.setdefault(cid, {})[taxon] = [
        [names[str(k)]["sci"], names[str(k)]["en"], n] for k, n in lst]
with open(os.path.join(DATA, "top_species_1p0.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False)
print("wrote data/top_species_1p0.json: %d cells, %d distinct species named"
      % (len(out), len(names)), flush=True)
