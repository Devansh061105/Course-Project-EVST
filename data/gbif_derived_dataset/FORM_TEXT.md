# Text for the GBIF derived dataset form (fill the bracketed parts)

**Title:** Bird occurrence records used for effort-corrected richness in South and Southeast Asia, 1-degree grid (Course Project 9)

**Source URL (persistent):** [Zenodo DOI link, e.g. https://doi.org/10.5281/zenodo.XXXXXXX]

**Original download DOI:** leave empty (no GBIF download was made; data came from the occurrence search API)

**Description:**
Per-cell species abundance vectors for birds (Aves, GBIF taxonKey 212) obtained through the GBIF occurrence search API with a species facet, for 884 one-degree cells covering 5-31N, 68-102E. Filters: hasCoordinate=true, hasGeospatialIssue=false, occurrenceStatus=PRESENT, year 2000-2024. The records were used to compute Hurlbert-rarefied species richness and a survey-effort covariate per cell, which were then compared with MODIS productivity. Records were queried on 2026-10-05/06; the attached counts were re-queried on 2026-10-09 with identical filters (71,716,026 records from 110 datasets, against 71,719,018 summed over cells at pull time; the small difference is database drift and records on shared cell edges). The Zenodo deposit holds the per-cell table and code.

**Contributing datasets file:** `dataset_counts.csv` (two columns, no header: datasetKey, number of records).
