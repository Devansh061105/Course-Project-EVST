# Verification record (2026-10-06)

What has been independently checked, how, and how to re-check it.

## 1. Every headline number reproduces from cached data
`python scripts/reproduce_all.py` re-runs all 17 analysis scripts (data acquisition
excluded — it reads the cached GBIF / Earth Engine outputs) and compares 27
documented headline numbers against the fresh logs in `data/repro/`.

Result 2026-10-06: **17/17 scripts exit 0; 27/27 checks PASS**, covering the
model sample (221 cells), Extension A (corrected OLS coefficient), the spatial
error result, weights sensitivity, Extension B (AIC), Extension C (spreads, Thar
rainfall), the Durbin family (SDEM AIC, LR test), block CV, the Hawkins test, the
robustness matrix (NPP), confounders, the ecoregion fixed-effects result (β, p,
residual plateau), variance decomposition, the 2019–23 time-window refit and the 0.5° chain
(baseline, within-ecoregion β and p, spatial error).
Figures are regenerated in the same run.

Re-run after any change to code or data and before the final report.

## 2. Dataset metadata matches the official Earth Engine catalogue
Checked against the Earth Engine STAC entries:

| dataset | what the code assumes | catalogue |
|---|---|---|
| MOD17A3HGF v061 | Gpp/Npp scale 0.0001, kg C m⁻²; valid Gpp 0–65500, Npp −30000–32700 | identical |
| MOD13Q1 v061 | NDVI/EVI scale 0.0001; valid −2000–10000 | identical |
| ERA5-Land monthly aggr. | temperature in K; precipitation in m per month (→ ×1000×12 = mm/yr) | identical; monthly cadence confirmed |
| ESA WorldCover v200 | class codes 10…100 (40 cropland, 50 built-up, 80 water) | identical |
| SRTM GL1 v003 | elevation in m | identical |

Physical plausibility: Western Ghats GPP 2.15 kg C m⁻² yr⁻¹ (typical tropical
forest), Thar 241 mm yr⁻¹ rainfall (desert).

## 3. GBIF facet counts are exact
The pipeline reads each cell's species-abundance vector from one faceted search
request. Elasticsearch aggregations can be approximate, so 12 species across the
abundance distribution of a 465,847-record cell (ranks 1–3, quartiles, and six
singletons) were re-counted with independent per-species queries: **12/12 exact
matches.**

## 4. Implemented formulas checked against authoritative sources
- **Hurlbert (1971) rarefaction** — hand-computed values; E[S_n]=S at n=N;
  E[S_1]=1; monotone in n (2026-10-05).
- **Chao & Jost (2012) coverage** — compared with the authors' own R package
  iNEXT (`Chat.Ind`, `invChat.R`): algebraically identical, max numeric
  difference 5×10⁻¹³ over 200 random vectors, identical to 10 d.p. on a
  3.76M-record cell, monotone in m.

## 5. References
All 14 references added for the analysis (beyond the literature review's 20) were
checked against Crossref for existence and bibliographic details, **and** their
abstracts were read; each is cited only for what its abstract supports
(`LITERATURE_NOTES.md`). Data-product DOIs resolved via DataCite / Crossref.

## 6. Full project review (2026-10-06)
Static check of all 27 scripts (pyflakes), data plausibility checks on the final
dataset, a country labelling of every cell, Earth Engine pixel-size checks, and a
read-through of every doc against the results. Found and fixed (details in
`DECISIONS.md`, entry "Project-review corrections"):

| # | Error | Fix |
|---|---|---|
| 1 | Study region described as "South Asia"; modelled cells are only 36% India | Wording corrected; country table in DECISIONS |
| 2 | Thar box called "W Rajasthan"; 11/25 land cells are in Pakistan; cropland wrongly attributed to Punjab/Haryana | Renamed **Thar Desert**; narrative corrected |
| 3 | "E Himalaya foothills" box includes 5 Tibetan modelled cells | Renamed **Eastern Himalaya** |
| 4 | Docs said ≥20 records; the binding rule is ≥250 species-identified records (rarefaction) | Docs, codebook and Fig 1 legend corrected |
| 5 | "~1 ERA5-Land pixel per 1° cell" (from the plan); true value ~94 | Corrected; mismatch matters little at 1° |
| 6 | `spatial_refit.py` tested the error model on `u` (printed I = 0.878) | Now `e_filtered` (I = 0.034) |
| 7 | `merge_and_extA.py` sanity check against an empty Deccan printed FAIL every run | Now against the Thar (PASS) |
| 8 | `adjudicate_lag_error.py` Part 2 printed the superseded per-fold CV verdict | Relabelled, points to `spatial_cv.py` |
| 9 | `gee_extract.py` (superseded) still contained three known bugs | Exits on start with a pointer |
| 10 | NPP "species-energy" reading did not mention MOD17's modelled respiration | Qualifier added |
| 11 | Project index pointed to a non-existent `PROJECT_CONTEXT.md` | Replaced by the prep guide |
| 12 | Taxon decision cited plant "truncation" as structural; it was our own facet limit (all 1,265 species return at a higher limit) | Rationale corrected to record density only |

Checks that passed: all scripts parse; richness ordering (rarefied_50 ≤ 100 ≤ 250
≤ observed); NPP ≤ GPP everywhere; GPP 0.07–2.93 kg C m⁻² yr⁻¹; temperature
−8 to 28 °C; precipitation 205–5,319 mm; land-cover fractions sum ≤ 1; model
cells have no masked classes and no missing predictors. After the fixes:
17/17 scripts run, 27/27 headline checks pass.

## Known limits of this verification
- Data acquisition itself is not re-run (it is slow and the APIs change over
  time); the caches in `data/` are the frozen inputs. GBIF results will differ
  slightly if re-pulled later, because GBIF keeps ingesting records.
- The verification checks that the code does what the docs say and that the
  inputs mean what the code assumes. It does not check the interpretation —
  that is argued in `RESULTS_ADJUDICATION.md`.
