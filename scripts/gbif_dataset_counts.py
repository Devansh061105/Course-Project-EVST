# -*- coding: utf-8 -*-
"""Contributing-dataset counts for a GBIF derived-dataset registration.

One faceted request over the whole study region (same filters as the per-cell
pulls), faceted by datasetKey. Writes
data/gbif_derived_dataset/dataset_counts_<taxon>.csv (datasetKey, records; no
header - the format the GBIF derived-dataset form accepts).

Usage: python gbif_dataset_counts.py plants
"""
import csv
import json
import os
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gbif_lib import API, REGION, TAXA, UA, YEAR_RANGE

taxon = sys.argv[1] if len(sys.argv) > 1 else "plants"
params = {
    "decimalLatitude": "%g,%g" % (REGION["lat_min"], REGION["lat_max"]),
    "decimalLongitude": "%g,%g" % (REGION["lon_min"], REGION["lon_max"]),
    "taxonKey": TAXA[taxon], "hasCoordinate": "true", "hasGeospatialIssue": "false",
    "occurrenceStatus": "PRESENT", "year": YEAR_RANGE, "facet": "datasetKey",
    "facetLimit": 5000, "limit": 0,
}
req = urllib.request.Request(API + urllib.parse.urlencode(params), headers=UA)
d = json.load(urllib.request.urlopen(req, timeout=180))
counts = d["facets"][0]["counts"]
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data",
                   "gbif_derived_dataset", "dataset_counts_%s.csv" % taxon)
with open(out, "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows([c["name"], c["count"]] for c in counts)
print("%s: %d records in the region, %d contributing datasets (sum %d) -> %s"
      % (taxon, d["count"], len(counts), sum(c["count"] for c in counts),
         os.path.normpath(out)))
