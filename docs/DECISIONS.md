# Decisions (append-only)

## 2026-10-05 — Per-cell richness from one faceted request, not record pagination
**Decision.** Query GBIF `occurrence/search` with `facet=speciesKey&facetLimit=1200&limit=0`
and read the species-abundance vector straight out of the facet response.

**Why.** The plan's Step 3 anticipated paginating 300 records at a time, with the
asynchronous Download API as a fallback for cells above the 100k offset ceiling.
That is unnecessary: the faceted response returns total occurrence count *and*
the per-species counts in a single request (~1.2 s per cell), which is exactly
the input Hurlbert rarefaction needs. 884 cells take ~20 min instead of hours,
and no Darwin Core Archive files touch the disk (C: is nearly full).

**Caveat recorded in code.** Facets truncate at `facetLimit`. Birds saturate at
451 species in the densest cell, so 1200 is safe; the pull flags any cell where
`obs_richness >= FACET_LIMIT` as `facet_truncated=1`.

## 2026-10-05 — Taxon locked to birds (Aves, taxonKey 212)
**Decision.** Birds, not vascular plants.

**Why.** Live density check over all 76 case-study cells (`scripts/taxon_check.py`,
results in `data/taxon_check.json`), per plan Step 2 which requires checking the
three case-study regions specifically rather than the region as a whole:

| taxon | median records/cell, Western Ghats | Deccan | E. Himalaya | usable cells | facet-truncated |
|---|---|---|---|---|---|
| birds | 196,920 | 29,642 | 94,063 | 72/76 | 0 |
| plants | 826 | 145 | 428 | 69/76 | 5 |

Two independent reasons. (1) Coverage: birds carry ~200× more records per cell,
driven by eBird ingestion; the Eastern Himalaya, which the plan flagged as the
highest-risk region, has a median of 94k bird records and needs no backup
sub-region. (2) Method validity: five dense plant cells returned ≥1200 species,
so their facet vectors truncate and rarefaction on them would be silently wrong.
India holds ~18,000 vascular plant species against ~1,300 birds, so this is
structural, not a parameter to tune.

**Consequence.** The taxonomic-restriction limitation in the report's limitations
paragraph is now specifically "birds only, which are better recorded than any
other group and may therefore understate sampling bias elsewhere."

## 2026-10-05 — Study region 5–31°N, 68–102°E at 1° resolution (884 cells)
**Decision.** Rectangular grid covering India, Sri Lanka, Bangladesh, Nepal,
Bhutan and Myanmar, giving 24 / 25 / 27 cells in the three case-study regions.

**Why.** Plan Step 1 asks for a regional rather than global extent, sized to hold
all three case studies plus surrounding area for statistical power. 884 cells is
comfortably powered for a handful of covariates and keeps API and GEE compute
tractable. Well below 60°N, so lat/lon distortion is not a concern.

**Known artefact.** The Western Ghats box spans the Arabian Sea coast, so 4 of its
24 cells returned zero records. These are genuinely sea, not undersampled land;
the WorldCover natural-cover fraction from Step 4 will remove them.

## 2026-10-05 — Rarefaction at three levels, not one
**Decision.** Compute Hurlbert rarefied richness at n = 50, 100 and 250 records
per cell, and keep raw total records as a separate covariate.

**Why.** The plan specifies rarefaction plus raw totals as a covariate, following
current practice. Computing three standardisation levels costs nothing extra
(the abundance vector is already in hand) and turns the arbitrary choice of n
into a sensitivity check, which pre-empts the obvious reviewer question.

**Implementation.** `hurlbert_rarefy` in `scripts/gbif_lib.py`, computed in log
space via `lgamma` because the binomial coefficients overflow at eBird-scale
record counts. Validated against hand-computed values, and against the
properties E[S_n]=S at n=N, E[S_1]=1, and monotonicity in n.

## 2026-10-05 — Deccan Plateau replaced by Thar / Western Rajasthan for Extension C
**Decision.** The dry-contrast case study becomes **25–30°N, 69–74°E** (Thar
Desert / western Rajasthan). The Deccan Plateau is reported as a finding, not
used as a case study.

**Why.** All 25 Deccan land cells are cropland-dominant, mean cropland+built-up
fraction 0.77, natural fraction 0.22; only 1 of 25 falls below 50% converted.
Zero cells survive the natural-land-cover restriction, so the region cannot
serve as a natural-ecosystem contrast at 1° resolution.

Replacement chosen by a sliding 5°×5° window scan over all eligible cells
(`scripts/scan_contrast_region.py`), ranked by precipitation among windows with
≥8 eligible cells and mean natural fraction ≥0.55:

| region | n | precip | natural | GPP | median records |
|---|---|---|---|---|---|
| Thar / W Rajasthan | 8 | 241 mm | 0.84 | 0.21 | 7,911 |
| Western Ghats (reference) | 7 | 2,499 mm | 0.78 | 2.15 | — |
| Eastern Himalaya | 24 | 3,013 mm | 0.86 | 1.48 | — |

The Thar gives a ~10× contrast in both rainfall and productivity while remaining
84% natural. The Deccan would have been a weaker contrast even had it survived:
semi-arid but heavily farmed, confounding land use with climate.

**Consequence.** The Deccan's exclusion is itself reportable for Section 4 of the
plan — the dry savanna/grassland contrast has been almost entirely converted to
agriculture, which bears directly on where conservation arguments apply.

**Caveat.** Case studies are small after masking (7, 8 and 24 eligible cells).
Narratives should be qualitative, not separate regressions.

## 2026-10-05 — Spatial error model adopted; H1 not supported at 1° resolution
**Decision.** Report the spatial error model as the primary specification, and
report that effort-corrected richness is **not** significantly associated with
GPP once spatial dependence is modelled.

**Why.** Robust LM error (29.43) exceeds robust LM lag (24.84); spatial error AIC
is 31.11 against the lag model's 102.85; and only the error model leaves
spatially clean residuals (Moran's I on `e_filtered` = +0.034, p = 0.198, versus
+0.161, p = 0.002 for the lag model). In that specification rarefied richness has
β = +0.00069, p = 0.506. See `docs/RESULTS_SPATIAL.md`.

**Not a failure.** The plan's risk table pre-registers this outcome as valid, and
it is consistent with Adler et al. (2011) and Gonzalez et al. (2020) from the
literature review. The naive-vs-corrected reveal becomes stronger, not weaker.

## 2026-10-06 — Interpretation: a between-ecoregion association, not a local effect
**Decision.** Report the richness–productivity association as real across regions
but largely absent within ecoregions (corrected below: small, not zero). Supersedes the 2026-10-05 entry "Spatial error model
adopted; H1 not supported at 1° resolution", whose model outputs stand but whose
inference was wrong.

**Why.** Four methods that do not depend on choosing a spatial model agree the
cross-regional association is real: the OLS estimate is unbiased (Hawkins et al.
2007 subsampling test: full β at the 45th–52nd percentile of spatially spaced
subsamples), and it transfers out of sample (~9% MSE reduction under 2–4° block
CV). Ecoregion fixed effects then remove ~90% of it (GPP β 0.273 → 0.030,
p = 0.59) while richness keeps 38.5% of its variance within ecoregions, and they
eliminate the broad residual plateau (Moran's I at 4.5–9° 0.170 → −0.027). The
spatial error model's null was the error process absorbing regional (biogeographic)
structure, not evidence of no association. Full record: `RESULTS_ADJUDICATION.md`.

## 2026-10-06 (later) — Correction: the within-ecoregion effect is small, not zero
**Decision.** Replace "the association vanishes within ecoregions" with "ecoregion
fixed effects remove ~75-90% of it; a small positive within-ecoregion effect of
~0.03-0.06 SD remains".

**Why.** The 0.5-degree run (n = 671, 64 ecoregions) gives a within-ecoregion
coefficient of +0.058 (SE 0.025, p = 0.021), and a spatial error coefficient of
+0.090 (p < 0.0001). The 1-degree within-ecoregion estimate (+0.030, SE 0.055,
CI -0.08 to +0.14) is compatible with it; that test could only detect effects of
~0.15 SD, so its non-significance was low power, contrary to the earlier note that
it was "not a power failure". `RESULTS_ADJUDICATION.md` section 8 has the table.
Section 6's statement that the 1-degree spatial-error null reflected the error
process absorbing regional structure is also weakened: at 0.5 degree that model
retains the effect.

## 2026-10-06 — Plan Step 8 clustering implemented by RESOLVE ecoregion
**Decision.** Cluster-robust SEs by RESOLVE ecoregion (56 clusters) replace the
4° spatial blocks used earlier.

**Why.** The plan specifies clustering "by biogeographic sub-region". Four-degree
blocks were an approximation made before an ecoregion layer was in hand. RESOLVE
Ecoregions 2017 (Dinerstein et al. 2017) is available in Earth Engine and covers
220 of 221 model cells.

## 2026-10-06 — Report NPP alongside GPP
**Decision.** Keep GPP as the primary response (the plan's choice) and report NPP
as a second, theory-motivated response throughout.

**Why.** NPP gives a consistently stronger association (OLS 0.384 vs 0.273) and is
the only response that survives the spatial error model (p = 0.008). NPP is the
carbon left after plant respiration — the energy available to consumers — which is
what species–energy theory predicts bird richness should track (Evans et al. 2005;
Hurlbert 2004). It also connects directly to the literature review's "what is
actually being measured" section.

## 2026-10-06 — Figure conventions
Static PNGs at 220 dpi with a CSV of plotted values beside each. Palette: dataviz
reference slots 1–3 (blue, orange, aqua), validated all-pairs against #ffffff;
aqua (2.82:1) is always direct-labelled. Magnitude maps use one-hue ramps (blue,
then orange for a second simultaneous ramp). No dual axes, solid hairline grids.

## 2026-10-06 — Project-review corrections (append-only record)
A full review (code, data, docs) found these errors in earlier entries and docs;
the fixes are applied in code and results docs, and recorded here rather than by
editing old entries.

1. **Study-region composition.** The 2026-10-05 entry says the region covers
   "India, Sri Lanka, Bangladesh, Nepal, Bhutan and Myanmar". Labelling centroids
   with US State Dept LSIB boundaries (`scripts/gee_countries.py`) shows land cells
   in India 257, China 77, Myanmar 60, Thailand 29, Pakistan 25, Nepal 13,
   Bangladesh 13, Sri Lanka 6, Laos 4, Malaysia 3, Bhutan 3, Indonesia 1 (139
   coastal centroids fall outside every polygon). The 221 **modelled** cells are
   India 79 (36%), China 48, Myanmar 38, Thailand 22, Nepal 11, Sri Lanka 5,
   Pakistan 4, Laos 4, Malaysia 3, Bangladesh 3, Bhutan 3. "South Asia" is wrong;
   the analysis is South and Southeast Asia and is weighted away from India,
   because most Indian land is cropland and fails the natural-cover mask.
2. **Case-study names.** "Thar / W Rajasthan" → **Thar Desert** (11 of its 25 land
   cells are in Pakistan). "E Himalaya foothills" → **Eastern Himalaya** (5 of 24
   modelled cells are in Tibet). The "Punjab/Haryana" cropland claim in
   RESULTS_EXTENSION_C was wrong.
3. **Effective record threshold.** Docs said cells need ≥20 records. Rarefying at
   n = 250 requires 250 species-identified records, so that is the binding rule (the
   sparsest modelled cell has 285). 50 land cells with 20–249 records are excluded
   by it — the least-surveyed cells, which matters for the sampling-bias argument.
4. **Pixel counts.** The plan (Step 4) and two project files said a 1° cell holds
   ~1 ERA5-Land pixel. Earth Engine nominal scales: ERA5-Land 11,132 m → ~94
   pixels per cell; MOD17 463 m → ~54,000.
5. **NPP caveat.** MOD17 NPP is GPP minus *modelled*, temperature-driven
   respiration. In the hot Thar cells it is near zero (NPP/GPP 0.03–0.18); in cold
   Tibetan cells it sits at the ~0.70 ceiling. Some of NPP's stronger association
   may come from that algorithm stretching the climatic extremes, so the
   species-energy reading of the NPP result (2026-10-06 "Report NPP alongside GPP")
   needs this qualifier.
6. **Code.** `spatial_refit.py` tested the spatial-error residual on `u` instead of
   `e_filtered` (printed I = 0.878; correct value 0.034) — fixed. `merge_and_extA.py`
   compared the Western Ghats with an empty Deccan and printed FAIL on every run —
   now compares with the Thar. `adjudicate_lag_error.py` Part 2 still printed the
   superseded per-fold CV verdict — relabelled. `gee_extract.py` (superseded, with
   three known bugs) now exits on start with a pointer to the chunked version.
7. **Index.** The project index pointed to `docs/PROJECT_CONTEXT.md`, which never
   existed; replaced with the prep guide.
8. **Taxon rationale.** The 2026-10-05 taxon entry gives two reasons for birds over
   plants and calls the second (five dense plant cells truncated at the facet
   limit) "structural, not a parameter to tune". That is wrong: 1,200 was our own
   `FACET_LIMIT`, and GBIF accepts higher values — the densest plant cell (r22c22)
   returns all 1,265 species with `facetLimit=5000`. The decision stands on the
   first reason alone: plants have ~200× fewer records per cell (e.g. Deccan
   median 145 vs 29,642), and cell r22c22 holds 1,265 species in only 4,192 records,
   far too sparse to rarefy.

## 2026-11-16 — Scope lock lifted by the user: vascular plants added as Extension D
**Decision.** A fourth extension is added: the model chain is repeated for a second
taxon, vascular plants (Tracheophyta, taxonKey 7707728). The plan locked the
project at three extensions "unless weeks 1-6 finish comfortably early"; the
analysis for A/B/C was complete on 2026-10-06 and the user asked for the addition
on 2026-11-16 after being shown that it breaks the lock. The lock now stands at
**four** extensions (A, B, C, D).

**Why plants.** Live density check on every fifth modelled cell (45 cells,
`scripts/taxon2_check.py`, cache `data/taxon2_check_cache.json`):

| group | median identified records / cell | cells with ≥ 50 | ≥ 100 | ≥ 250 |
|---|---|---|---|---|
| vascular plants | 524 | 37 | 35 | 30 |
| Lepidoptera | 160 | 33 | 28 | 16 |
| Squamata | 54 | 25 | 17 | 11 |
| amphibians | 34 | 22 | 17 | 9 |
| mammals | 21 | 19 | 13 | 9 |

Plants are the only other group with enough records in most modelled cells, and
they are the group biodiversity–productivity theory is about. This does not
overturn the 2026-10-05 choice of birds as the primary taxon: plants still carry
orders of magnitude fewer records per cell, and that check was dominated by the
cropland Deccan cells, which are not modelled.

**How.** `scripts/gbif_pull_taxon2.py`: one faceted request per 1° cell, same
filters and years as the birds, facet limit 5000 (project-review correction 8),
own append-only cache `data/gbif_cache_plants.json`. Analysis in
`scripts/extension_d_plants.py`; results in `docs/RESULTS_EXTENSION_D.md`.

**Consequences.** (1) The GBIF derived-dataset DOI (10.15468/dd.jf64nx) covers the
bird records only; plant records need their own citation before they appear in a
report (TODO). (2) `data/final/biodiversity_productivity_1deg.csv` is unchanged,
so it still matches the Zenodo deposit; plant columns live in
`data/gbif_cells_plants.csv` and `data/plants_model_cells.csv`. (3) The
limitations paragraph can no longer say "birds only".

## 2026-11-16 — Local slopes (GWR) added inside Extension C
**Decision.** Geographically weighted regression of the corrected model at 1° and
0.5° (`scripts/local_slopes.py`, `docs/RESULTS_LOCAL_SLOPES.md`, Fig 9).

**Why.** Extension C asks whether the relationship holds in every landscape and
answers with three boxes chosen in advance. Local slopes answer it for every
modelled cell, and the slope-against-window-size curve shows the between-region
result without relying on ecoregion boundaries. It is reported as part of
Extension C, with a Monte Carlo stationarity test and a multiple-testing
correction, because GWR maps are easy to over-interpret.

**Implementation note.** Written directly in numpy (adaptive bisquare kernel,
AICc bandwidth) to avoid adding the `mgwr` dependency.

## 2026-11-16 — Interactive atlas
**Decision.** `docs/interactive_map.html`, one self-contained page built by
`scripts/build_interactive_map.py` from the finished per-cell tables: switchable
layers, a per-cell record and a linked richness–GPP scatter. No map tiles and no
server, so it opens from the repo and can be shown in the presentation. It
displays results; it adds no analysis of its own.

## 2026-11-16 — Cache writes retry on Windows file locks
`gbif_lib.save_cache` now retries `os.replace` on `PermissionError`. The first
plant pull died at cell ~230 when another process briefly held the cache file;
nothing was lost (the cache is written after every cell) and the pull resumed.

## 2026-11-16 — 3D terrain map; ETOPO1 and 0.05° grids for display only
**Decision.** A second interactive page, `docs/interactive_map_3d.html`: the study
region as 3D terrain with the ground coloured by land cover, NDVI, GPP or
elevation, one column per 1° cell for bird or plant richness, and a record for any
place clicked. The user asked for it after seeing the flat atlas.

**Data.** `scripts/gee_terrain_grid.py` pulls four 0.05° grids (680 × 520) once and
caches them in `data/terrain_grid_0p05.npz`: ETOPO1 elevation, WorldCover class,
MOD13Q1 NDVI and MOD17A3HGF GPP (2019–2023 means). These grids are **for display
only**; no model uses them. ETOPO1 is used instead of the SRTM of the analysis
because it is already at a coarse resolution and covers the sea.

**Two things to know.** (1) MOD17 fill values are not masked in the Earth Engine
asset and get averaged into the coarser pyramid levels; the GPP grid is therefore
masked at 500 m and aggregated explicitly (the first attempt was wrong, see
`VERIFICATION.md` section 7). (2) The page loads three.js from a CDN, so it needs
an internet connection when it is opened; the flat atlas does not need one for its
content (only for its web fonts). Relief is exaggerated (25× by default) and the
page says so.

## 2026-11-16 (later) — Scope lock lifted a second time: Extensions E and F
**Decision.** After being shown a list in which three items were marked as needing
the scope lock lifted again, with a recommendation against them, the user asked
for everything on the list except the report. Recorded here because it overrides
the "no fifth extension" rule written earlier the same day. The lock now stands
at **six** extensions:

- **E** richness and the year-to-year stability of productivity
  (`RESULTS_EXTENSION_E.md`);
- **F** protected land (`RESULTS_EXTENSION_F.md`).

The third item, a third taxon (butterflies and moths), is the same question as
Extension D and is reported inside it, not as a seventh extension.

**Do not add a seventh.** The project is now wide; further work should go into
the report.

## 2026-11-16 (later) — Additions inside the existing extensions
- **A:** thinning experiment (`effort_simulation.py`).
- **B:** flexible-curve and breakpoint tests (`shape_spline.py`).
- **D:** plants at 0.5°, plant cross-validation and hump test, Lepidoptera
  (`extension_d_more.py`, `gbif_pull_generic.py`).
- **Cross-cutting:** path analysis for direction (`path_analysis.py`), a
  960-model specification curve (`spec_curve.py`), a survey-gap ranking
  (`survey_gaps.py`).

## 2026-11-16 (later) — Protected areas: two definitions, and a subset without India and China
**Decision.** Extension F reports protection two ways (IUCN categories Ia–IV, and
all designated WDPA polygons) and repeats every model without India and China.

**Why.** The first extract gave India 18% protected. A breakdown by designation
showed about 180,000 of India's 190,000 WDPA polygons are Reserve Forest or
Protected Forest, while its national parks and sanctuaries total only about
20,800 km² of reported area: the parks are largely missing from the public
database. Under the strict definition India reads 0.2%. Neither number measures
protection in India, so results that include India are not interpretable and the
extension is labelled data-limited.

## 2026-11-16 (later) — Species names are fetched for display only
`gbif_top_species.py` asks GBIF for the four most-recorded bird and plant species
per land cell (1,176 requests) and resolves 1,187 species keys to names, with
their own append-only caches. The richness pulls store counts without species
identity, so this is a separate, display-only request; no model uses it.

## 2026-11-16 (later) — Tests, continuous integration and hosted maps
- `tests/test_core.py`: 17 unit tests of rarefaction, coverage, the grid, the GWR
  kernel, thinning and the stability statistics, against hand-computed or
  by-construction values.
- `.github/workflows/checks.yml`: on every push, run the tests and
  `reproduce_all.py`, which now exits non-zero if any check fails.
- GitHub Pages serves `docs/` (with `docs/.nojekyll` so files are served as they
  are), giving the two maps public URLs. The user asked for the push and for the
  hosting.

## 2026-11-16 (later) - Presentation deck as a PowerPoint file
`presentation/Project9_Biodiversity_Productivity.pptx`, 13 slides with speaker notes,
built by `presentation/build_deck.js` (pptxgenjs) from the figures. The deck is kept as a file in the repo. Every number on the slides comes from the `RESULTS_*.md` files; if a result
changes, change the script and rebuild. Slide 6 states that the fitted curve dips at
the top end and why that is not a decline in the data, because the figure shows it.
