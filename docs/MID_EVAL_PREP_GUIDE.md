# Mid-Evaluation Prep Guide — Project 9: Biodiversity and Ecosystem Productivity

*Prepared 2026-10-06, after a full review of the project. Every number here comes
from results that were re-run and checked (27/27 headline checks pass; see
`VERIFICATION.md`). Where the guide says something is uncertain, it is.*

**How to use this:** read sections 1–4 for the story, section 9 for the results,
and section 14 for likely questions and answers. Sections 5–6 are the "what tools,
where, why" reference. Section 11 lists the errors we caught, which is worth
knowing: examiners respect a team that found its own mistakes.

---

## 1. The project in 60 seconds
We asked whether places with more bird species are also more productive (plants
fix more carbon there). We built a grid of 884 one-degree cells over South and
Southeast Asia and gave each cell two numbers: **bird species richness**, from
71.7 million citizen-science records (98.8% eBird, accessed through GBIF), and
**productivity**, from NASA MODIS satellite data processed in Google Earth Engine.

The catch is that citizen-science records pile up where birdwatchers go, so raw
species counts mostly measure *survey effort*. We corrected for that
(rarefaction), controlled for climate, removed farmland, and dealt with the fact
that neighbouring cells are not independent.

**Finding:** species-rich *regions* are clearly more productive, but most of the
link is between regions. Within an ecoregion it shrinks by 75–90%, to a small,
fragile positive effect. We cannot tell which way causation runs, and theory
suggests productivity drives bird richness rather than the reverse.

## 2. Why the question matters
- In 2022, 196 countries adopted the **Kunming–Montreal Global Biodiversity
  Framework** (halt and reverse biodiversity loss by 2030; mobilise ≥ $200bn/yr).
  Part of the case for that money is that biodiverse ecosystems store and fix
  more carbon.
- Forest-plot studies support a positive biodiversity–productivity link (Liang et
  al. 2016; Duffy et al. 2017; Chen et al. 2023), with a canopy-structure mechanism
  (Deng et al. 2025). But they are plot-scale, and conservation is planned at
  landscape scale.
- Citizen-science data (GBIF/eBird) is increasingly used to track biodiversity
  targets, so knowing how biased it is, and how to correct it, matters in itself.

*Note: the literature review does not name the Global Biodiversity Framework (its
20-reference cap left no room for a policy source). The report introduction must
add it with a citation.*

## 3. Research question, hypotheses, extensions
**H1:** effort-corrected biodiversity is positively associated with productivity
(GPP) after controlling for climate and restricting to natural land cover.
**H0:** no meaningful association remains after those corrections.

| Extension | Question | Answer so far |
|---|---|---|
| **A** naive vs corrected | Does correcting for survey effort change the picture? | Yes, a lot. Raw counts are mostly effort (r = 0.81 with effort, falling to 0.24 after correction). |
| **B** linear vs hump | Is the relationship a straight line or a hump? | Linear. No evidence of a hump in 11 of 12 specifications. |
| **C** case studies | Does it hold in three contrasting landscapes? | The regional ranking *flips* after correction; productivity varies 10× while corrected richness varies 1.3×. |

## 4. Study design
| Choice | What | Why |
|---|---|---|
| Region | 5–31°N, 68–102°E | Holds all three case studies plus enough cells for statistics |
| Grid | 1° × 1° cells (≈111 km), 884 cells, 630 on land | Plan's choice; big enough that each cell has many records. Re-run at 0.5° and 2° as robustness checks. |
| Taxon | Birds (class Aves) | Decided by a live data check: about 200× more records per cell than plants (section 8) |
| Period | Birds 2000–2024; environment 2019–2023 means | Climatological averages. A matched-window (2019–23) check gives the same picture. |
| Unit of analysis | 221 "modelled" cells | Natural cover dominant, ≥250 species-identified records, complete data |

**Which countries?** The region is South **and Southeast** Asia, not just South
Asia. Land cells: India 257, China 77, Myanmar 60, Thailand 29, Pakistan 25,
Nepal 13, Bangladesh 13, plus Sri Lanka, Laos, Malaysia, Bhutan and Indonesia.
**The 221 modelled cells are only 36% India** (China 22%, Myanmar 17%, Thailand
10%). This is because most Indian land is cropland and fails the natural-cover
filter. Do not describe the result as "Indian".

## 5. Data sources — what, where from, why
| Data | Source | Resolution | Used for | Why this one | Citation |
|---|---|---|---|---|---|
| Bird occurrences | GBIF API (98.8% eBird) | point records | richness, effort | Free, global, no login; the plan's choice | GBIF derived-dataset DOI **still to register** |
| GPP, NPP | MODIS MOD17A3HGF v061 | 463 m, yearly | productivity (response) | Standard satellite productivity product | Running & Zhao 2021, doi:10.5067/MODIS/MOD17A3HGF.061 |
| NDVI, EVI | MODIS MOD13Q1 v061 | 232 m, 16-day | robustness, seasonality | Alternative productivity proxies | Didan 2021, doi:10.5067/MODIS/MOD13Q1.061 |
| Temperature, rainfall | ERA5-Land monthly | ~11 km | climate controls | Consistent global reanalysis | Muñoz-Sabater et al. 2021 |
| Land cover | ESA WorldCover v200 (2021) | 10 m | cropland/water mask | Highest-resolution global map | Zanaga et al. 2022 |
| Elevation | SRTM GL1 | 30 m | topography confounder | Standard DEM | NASA JPL 2013 |
| Ecoregions | RESOLVE Ecoregions 2017 | polygons | biogeographic units | Plan Step 8 asks for "biogeographic sub-regions" | Dinerstein et al. 2017 |
| Countries | US State Dept LSIB 2017 | polygons | describing the study area | Checking claims only | — |

All environmental data units and valid ranges were checked against the official
Earth Engine catalogue (`VERIFICATION.md` §2).

## 6. Tools — what, where, why
| Tool | What it did | Where (script) | Why |
|---|---|---|---|
| **Python 3** (pandas, numpy) | All data handling | every script | Standard; the whole team can read it |
| **GBIF occurrence API** | Bird records per cell | `gbif_lib.py`, `gbif_pull.py` | **One request per cell** using a *species facet*: it returns the full species list with counts in a single call, instead of paging through millions of records. Verified exact (12/12 counts matched). |
| **Google Earth Engine** (`earthengine-api`) | Satellite and climate values per cell | `gee_extract_chunked.py`, `gee_confounders.py`, `gee_ecoregions.py` | Processes terabytes of imagery on Google's servers; we only download per-cell averages. Free for academic use (Community tier). |
| **statsmodels** | OLS regression, robust and clustered standard errors, VIF | `merge_and_extA.py`, most analysis scripts | Standard, well-documented statistics |
| **libpysal / esda** | Spatial neighbour matrices, Moran's I | `spatial_refit.py`, `weights_sensitivity.py` | Standard Python spatial statistics (PySAL) |
| **spreg** | Spatial lag, spatial error and Durbin models | `spatial_refit.py`, `adjudicate_lag_error.py` | Fits the spatial models the plan's Step 8 implies |
| **scipy** | Rarefaction maths (log-gamma), p-values | `gbif_lib.py`, `coverage_rarefaction.py` | Numerically stable at millions of records |
| **matplotlib** | Figures 1–8 | `make_figures.py` | Static, print-quality figures |
| **Crossref / Semantic Scholar / Europe PMC / DataCite APIs** | Checked every reference exists and read its abstract | (research, not in pipeline) | So nothing is cited that we have not read |
| **iNEXT source code** (R, by Chao) | Checked our coverage formula | `coverage_rarefaction.py` | The method's authors' own code (difference 5×10⁻¹³) |
| **ORNL DAAC MODIS API** | Tested as a no-login fallback | — (not used in results) | Only needed if Earth Engine approval had been slow |
| **python-docx** | The literature review document | — | Required format (Times New Roman 12, 1.5 spacing) |

## 7. The pipeline, step by step (plan Section 6)
| Plan step | What we did | Script | Status |
|---|---|---|---|
| 1 Grid | 884 cells, exported as GeoJSON for Earth Engine | `gbif_lib.py` | Done |
| 2 Taxon | Birds vs plants live check across the case-study regions | `taxon_check.py` | Done → birds |
| 3 GBIF + rarefaction | One faceted request per cell; Hurlbert rarefaction at 50/100/250 records | `gbif_pull.py` | Done (0 truncated cells) |
| 4 Earth Engine | GPP, NPP, NDVI, EVI, climate, land cover; 2019–23 means; fill values masked | `gee_extract_chunked.py` | Done |
| 5 Merge + sanity | Join on cell id; Western Ghats more productive than Thar (PASS) | `merge_and_extA.py` | Done |
| 6 Extension A | Naive vs corrected regression, robust SEs | `merge_and_extA.py` | Done |
| 7 Extension B | Linear vs quadratic by AIC | `extension_b.py` | Done |
| 8 Checks | Moran's I, VIF, grid size (0.5°/1°/2°), clustering by ecoregion | several | Done, and extended |
| 9 Extension C | Three case studies | `extension_c.py` | Done |
| 10 Write-up | Report and presentation | — | **Not started** (planned for weeks 7–8) |

## 8. Key decisions and changes from the plan
| Decision | What and why |
|---|---|
| **Birds, not plants** | Plants had about 200× fewer records per cell (Deccan median 145 vs 29,642), so plant richness could not be rarefied reliably in most cells. (A second reason we gave earlier, that dense plant cells overflow the request limit, was wrong: 1,200 was our own setting, and raising it returns every species.) |
| **Facet request instead of paging** | The plan expected 300-record pages and async downloads. One faceted request gives what rarefaction needs, so 884 cells took about 20 minutes. |
| **Deccan Plateau → Thar Desert** | All 25 Deccan land cells are cropland-dominated (77% converted), so none survive the natural-cover filter. The Thar was chosen by a systematic scan: 10× drier and 10× less productive than the Western Ghats, 84% natural. The Deccan's conversion is itself a finding. |
| **Rarefy at 250 records** | Standard choice; also tested at 50 and 100, and with coverage-based standardisation (Chao & Jost 2012). This is the real data threshold: cells need ≥ 250 species-identified records. |
| **Water also masked** | The plan masked cropland and built-up land. Sea and lake cells were added, because otherwise they enter the model as "natural" cells with zero productivity. |
| **Clustering by ecoregion** | The plan's Step 8 asks for clustering "by biogeographic sub-region"; RESOLVE ecoregions implement it (56 clusters at 1°). |
| **NPP reported alongside GPP** | NPP (carbon left after plant respiration) is closer to the energy available to birds. Caveat: it is partly modelled (section 12). |

## 9. Results

### 9.1 The data look right
- The Western Ghats come out productive (GPP 2.15 kg C m⁻² yr⁻¹, NDVI 0.62) and
  the Thar barely productive (0.21), as expected.
- All values are within physical ranges: GPP 0.07–2.93; NPP below GPP everywhere;
  temperature −8 to 28 °C; rainfall 205–5,319 mm/yr.

### 9.2 Extension A — correcting for survey effort (1°, 221 cells, standardised)
| Model | Richness coefficient | R² |
|---|---|---|
| Raw richness only (naive) | +0.445 | 0.20 |
| Effort-corrected richness only | +0.558 | 0.31 |
| Corrected + effort + temperature + rainfall | +0.273 | 0.56 |

- **Raw species counts are mostly effort.** Correlation with survey effort falls
  from 0.81 to 0.24 after rarefaction (Fig 7).
- Correcting richness actually makes the bivariate link *stronger*, because a
  noisy measure is replaced by a cleaner one. Adding climate then **halves** it.
- Richness adds only **5 percentage points of R²** beyond climate. Temperature is
  the strongest single predictor.

### 9.3 Neighbouring cells are not independent (spatial autocorrelation)
- Residual **Moran's I = 0.72** (p = 0.001): nearby cells have similar leftovers,
  so ordinary p-values are too optimistic. The plan flagged this as the most
  common flaw reviewers catch.
- What we did, in increasing strength:
  1. Robust and clustered standard errors.
  2. Spatial lag and spatial error models, and the Durbin family that contains both.
  3. **Spatial block cross-validation**: hold out whole regions and test prediction.
  4. The **Hawkins et al. (2007) subsampling test**: refit on cells spaced far apart.
- Results:
  - The OLS coefficient is **not biased** by the autocorrelation. It sits at the
    45th–52nd percentile of the spaced-out subsamples, exactly as Hawkins et al.
    found for birds at the same grid size.
  - Richness **improves prediction in held-out regions** by about 9%.
  - At 1°, the spatial error model (the type Kissling & Carl 2008 found most
    reliable) makes richness non-significant (β 0.017, p = 0.51). At 0.5° it does
    not (β 0.090, p < 0.0001). The 1° null was partly a lack of statistical power.

### 9.4 The decisive result — between vs within ecoregions (Figs 3, 4, 5)
| GPP, standardised, SEs clustered by ecoregion | 1° (n = 220) | 0.5° (n = 671) |
|---|---|---|
| Baseline (effort + climate) | +0.273 | +0.228 |
| + biome fixed effects | +0.182 | +0.151 |
| **+ ecoregion fixed effects (within-ecoregion)** | **+0.030 (p = 0.59)** | **+0.058 (p = 0.021)** |

- Comparing cells only **within the same ecoregion** removes about 75–90% of the
  association.
- What remains is small: roughly 0.03–0.06 standard deviations. It is detectable
  at 0.5° but not at 1°, where the test could only detect effects of about
  0.15 SD or more.
- Ecoregion identity also **removes the broad leftover spatial pattern** (Fig 5:
  residual Moran's I at 4.5–9° falls from 0.17 to −0.03). The "mystery regional
  driver" behind the earlier spatial results was **biogeography**.
- Interpretation: species-rich ecoregions (e.g. the Eastern Himalaya and Myanmar's
  montane forests)
  are wet and productive; species-poor ones (e.g. the Thar) are dry. This matches
  the literature on **regional species pools** (Ricklefs 1987; Cornell & Harrison
  2014) and **scale-dependent** productivity–diversity relationships (Chase &
  Leibold 2002: the same data gave a hump among ponds and a straight line among
  watersheds).
- The small within-ecoregion effect at 0.5° survives controls for topography and
  seasonality (+0.051, p = 0.024) and is not driven by any single ecoregion (64/64
  leave-one-out refits stay significant). It is fragile: topography alone pushes
  p to 0.08, and it is not significant within each large biome separately.

### 9.5 Extension B — straight line or hump? (Fig 8)
- **Linear.** Adding a squared term never improves the fit meaningfully
  (primary specification ΔAIC +1.9; 11 of 12 specifications indistinguishable).
- The one exception (rarefied at only 50 records) is U-shaped, not a hump, and
  disappears under spatial models.
- This sides with the complementarity studies (Liang et al. 2016; Deng et al.
  2025), not the unimodal "hump" (Fraser et al. 2015).

### 9.6 Extension C — three landscapes (Figs 1, 2, 6)
| | Western Ghats | Thar Desert | Eastern Himalaya |
|---|---|---|---|
| Countries | India | India 14, Pakistan 11 land cells | India, Tibet (China), Bhutan, Myanmar |
| Modelled cells | 7 | 8 | 24 |
| Rainfall / GPP | 2,499 mm / 2.15 | 241 mm / 0.21 | 3,013 mm / 1.48 |
| Median records per cell | 1,098,270 | 7,911 | 76,542 |
| Raw richness (rank) | 456 (**1st**) | 209 (3rd) | 450 (**2nd**) |
| Corrected richness (rank) | 113.8 (**2nd**) | 98.0 (3rd) | 126.3 (**1st**) |

- **The ranking flips.** The Western Ghats look richest only because they carry
  14× more records than the Eastern Himalaya. This is the plan's predicted
  "naive vs corrected" moment.
- **Spreads:** survey effort varies 139×, GPP 10×, raw richness 2.2×, corrected
  richness only **1.3×**. Productivity varies a lot; corrected diversity barely
  moves.
- The Western Ghats cannot be compared numerically with Kothandaraman et al.
  (2020). They report a carbon **stock** (336.8 Mg C/ha); we measure a carbon
  **flux** (GPP). Qualitatively they agree.

### 9.7 Robustness — what did not change the answer
Productivity measured as NPP, NDVI or EVI · five land-cover masks · rarefaction
at 50/100/250 and coverage-based · topography and seasonality controls · records
from 2019–23 only · ten spatial neighbour definitions · grids of 0.5°, 1° and 2°.
The between-region association held throughout. The within-region effect is
small everywhere.

### 9.8 The one-paragraph conclusion
Effort-corrected bird richness and productivity are positively associated across
South and Southeast Asia, and the association is not an artefact of sampling
effort or spatial autocorrelation. It is overwhelmingly a between-region pattern:
within an ecoregion it shrinks to roughly a quarter or less and is fragile. The
design cannot establish direction, and macroecological theory (species–energy;
Evans et al. 2005; Hurlbert 2004; Coops et al. 2009) points to productivity
driving bird richness. **So the data do not support the claim that adding
biodiversity raises productivity at landscape scale**, which is the claim the
policy framing leans on.

## 10. Figures (all in `figures/`, each with a CSV of the plotted values)
| Fig | Shows | One-line message |
|---|---|---|
| 1 | Study grid and mask | Two-thirds of land is cropland or excluded; the Deccan disappears |
| 2 | Maps of corrected richness and GPP | Both are high in the wet north-east |
| 3 | Richness coefficient across models | Climate and biogeography account for most of the association |
| 4 | Between vs within ecoregions | Clear between regions, much weaker within |
| 5 | Residual autocorrelation by distance | Ecoregions absorb the broad spatial pattern |
| 6 | Case-study spreads | Effort 139×, GPP 10×, corrected richness 1.3× |
| 7 | Naive vs corrected scatter | Raw richness mostly tracks effort |
| 8 | Linear vs quadratic | No hump |

## 11. Quality control — errors we found and fixed
Showing these is a strength. Each was caught by a check, not by luck.

| Error | How it was caught | Effect if missed |
|---|---|---|
| MODIS fill value (65535) averaged as real data | Implausible GPP maximum of 6.55 | Sea cells would have looked hyper-productive |
| Water counted as "natural" land | Code review | Sea cells would have created a fake positive link |
| Earth Engine renamed a single-band output ("mode", not "wc_mode") | Column entirely empty | The land mask silently did nothing |
| Same naming bug reintroduced at 2° | Zero eligible cells | A guard now aborts if any column is empty |
| Spatial-error residual tested on the wrong quantity | Cross-check against the textbook | Misleading I = 0.878 (true 0.034) |
| Cross-validation averaged per block, not per cell | Contradicted the pooled numbers | Wrongly reported "no predictive gain" |
| "Not a power failure" claim at 1° | The 0.5° run found a small effect | Overstated "vanishes within regions" |
| "South Asia" / "W Rajasthan" / "foothills" labels | Country labelling of every cell | Wrong geography in the report |
| "≥ 20 records" threshold | Data check (the real minimum is 250 identified) | Misdescribed sample |
| "~1 climate pixel per cell" (from the plan) | Earth Engine pixel sizes | Actually ~94 pixels |
| "Plants overflow GBIF's species limit" | Re-querying with a higher limit | It was our own setting; birds were chosen for record density alone |

Plus independent checks: GBIF counts exact; coverage formula matches the authors'
code; every reference's abstract read; every headline number re-runs automatically
(`scripts/reproduce_all.py`).

## 12. Limitations (say these before you are asked)
1. **Direction is not identified.** Birds are consumers; they are unlikely to
   drive plant productivity. The association is probably productivity → richness.
2. **Birds only**, which are the best-recorded group, so sampling bias is
   probably *understated* compared with other taxa.
3. **Selection by survey effort.** Cells need ≥ 250 identified records, so the 50
   least-surveyed land cells are excluded — exactly the places bias matters most.
4. **The modelled sample is mostly outside India** (36% India), because India is
   mostly farmland.
5. **GPP and NPP are modelled fluxes**, not measured carbon stocks. NPP includes
   modelled respiration, which stretches hot and cold extremes.
6. **Small case studies** (7, 8 and 24 cells): their narratives are qualitative.
7. **Time windows:** birds 2000–24 vs environment 2019–23. Checked: matching the
   windows gives the same result.
8. **Within-ecoregion effect** is real at 0.5° but fragile; report it as a range
   (0.03–0.06 SD), not a point.
9. **No GBIF DOI yet**: the data are not yet citable in the form GBIF requires.

## 13. Progress against the 8-week plan
- **Weeks 1–6 (setup, data, models, checks, case studies, figures): done.** We
  are ahead: the plan expected only items 1–2 of the deliverables checklist by
  midpoint; 6 of 8 are done, 1 is partly done (the introduction still needs the
  policy source) and 1 is not started (the policy section) — `DELIVERABLES_MAP.md`.
- **Week 7–8 still to do:** the written report (including the policy section,
  deliverable 8), the presentation, registering the GBIF derived-dataset DOI, and
  adding a Global Biodiversity Framework source to the introduction.
- **Team decision needed:** how to frame H1, given that direction is not
  identified. Recommendation: present it as an association test, with
  "productivity drives richness" as the leading alternative explanation.

## 14. Likely viva questions — with answers
**Q: Why birds and not plants?**
We checked live, in all three case-study regions. Plants had about 200× fewer
records per cell (e.g. Deccan median 145 vs 29,642 for birds), too few to rarefy
reliably. One dense plant cell has 1,265 species in only 4,192 records. Birds
are also the most consistently recorded group (98.8% eBird). *(We earlier also
cited a GBIF request limit; that turned out to be our own setting, so do not use
it as a reason.)*

**Q: Isn't GBIF data biased?**
Yes, heavily, and that is the point of Extension A. Raw richness correlates 0.81
with survey effort. Rarefaction cuts that to 0.24, we include effort as a
covariate, and the case-study ranking flips once corrected. 98.8% of our records
are eBird, so the bias is towards where birdwatchers go.

**Q: What is rarefaction?**
It asks: if every cell had only 250 records, how many species would we expect?
It compares cells at equal effort (Hurlbert 1971). We also tested 50 and 100
records and coverage-based standardisation (Chao & Jost 2012), which compares
cells at equal completeness. Same answer.

**Q: Why GPP?**
It is the plan's measure: a standard satellite estimate of carbon fixed by plants.
We also tested NPP, NDVI and EVI. GPP and NPP are fluxes (carbon per year), not
carbon stocks.

**Q: Why remove cropland?**
Farm productivity reflects irrigation and fertiliser, not natural ecology. We also
removed water, which the plan missed and which would have created a fake signal.

**Q: What happened to the Deccan?**
Every Deccan land cell is cropland-dominated (77% converted), so no natural cells
remained. We replaced it with the Thar Desert, chosen by a systematic scan. The
Deccan's loss is itself a finding about land conversion.

**Q: How did you handle spatial autocorrelation?**
We measured it (Moran's I 0.72), then used clustered standard errors, spatial
lag/error/Durbin models, spatial block cross-validation, and the Hawkins
subsampling test. The coefficient is not biased by it; ecoregion identity explains
most of it.

**Q: Your 1° and 0.5° results differ — which is right?**
They agree. At 1° the within-ecoregion effect (+0.03) has a 95% CI of −0.08 to
+0.14, and the test could only detect effects ≥ 0.15 SD. At 0.5°, with three
times as many cells, it detects +0.058. Both point to a small positive
within-region effect.

**Q: So does biodiversity increase productivity?**
Our data cannot say. The association is mainly between regions, where species
pools and climate differ, and the direction is not identified. Birds are
consumers; theory and prior work suggest productivity supports more bird species.

**Q: Did you find the hump?**
No. The relationship is adequately linear. This sides with Liang et al. (2016),
not Fraser et al. (2015).

**Q: How does this relate to Chase & Leibold (2002)?**
They showed the same productivity–diversity data look different at different
scales. We see the same: a clear pattern between regions, much weaker within.

**Q: Why are most modelled cells outside India?**
India's land is mostly cropland, so the natural-cover filter removes most Indian
cells. The modelled sample is 36% India and 64% China, Myanmar, Thailand, Nepal
and others.

**Q: How do you know your code is correct?**
One script re-runs every analysis and checks 27 headline numbers (all pass). We
also checked the data units against the official catalogue, that GBIF counts are
exact, and our formulas against the authors' own code. We list the bugs we found
in section 11.

**Q: What would you do with more time?**
Repeat with another taxon (e.g. plants at a coarser grain), use structural or
lidar data to test the canopy mechanism, and register the GBIF DOI.

**Q: Policy implication?**
Citizen-science biodiversity data must be bias-corrected before use: raw counts
mostly track birdwatchers. The data do **not** justify claiming that more
biodiversity means more carbon uptake at landscape scale.

## 15. Glossary
- **GPP / NPP:** gross / net primary productivity. Carbon fixed by plants per year,
  before / after plant respiration (kg C m⁻² yr⁻¹).
- **NDVI / EVI:** satellite greenness indices.
- **Rarefaction:** expected species count at a fixed number of records.
- **Coverage:** estimated fraction of the community's individuals belonging to
  species already seen; a measure of sample completeness.
- **Survey effort:** number of records in a cell (log-transformed as a covariate).
- **Standardised coefficient (β):** change in the response, in standard
  deviations, per one-SD change in the predictor; comparable across models.
- **HC3 / clustered SEs:** standard errors robust to unequal variance / to
  correlation within groups (here, ecoregions).
- **Moran's I:** how similar neighbouring values are (0 = independent).
- **Spatial lag / error / Durbin models:** regressions that model spatial
  dependence in the outcome, the errors, or both, with neighbour predictors.
- **Fixed effects:** a dummy per group; the coefficient then uses only
  within-group variation.
- **Block cross-validation:** testing prediction on whole held-out regions.
- **VIF:** variance inflation factor; a collinearity check (ours ≤ 1.5 for the
  main model).
- **AIC:** model-fit score penalised for complexity; lower is better, and a
  difference under 2 means "indistinguishable".
- **Ecoregion / biome:** RESOLVE biogeographic units (ecoregions nest in biomes).

## 16. Where everything is
| Need | File |
|---|---|
| Current interpretation (master) | `docs/RESULTS_ADJUDICATION.md` |
| Extensions A / B / C | `docs/RESULTS_EXTENSION_A.md`, `_B.md`, `_C.md` |
| Why each choice | `docs/DECISIONS.md` |
| What is left | `docs/TODO.md` |
| Plan deliverables → files | `docs/DELIVERABLES_MAP.md` |
| What was checked | `docs/VERIFICATION.md` |
| Extra references (abstracts read) | `docs/LITERATURE_NOTES.md` |
| Clean dataset + codebook | `data/final/` |
| Figures | `figures/` |
| Re-run everything | `python scripts/reproduce_all.py` |

## 17. Suggested 10-minute presentation flow
1. Question and policy stakes (1 min) — sections 1–2.
2. Data and tools (1.5 min) — Fig 1, sections 5–6; the "98.8% eBird" fact.
3. The bias problem (2 min) — Fig 7 and the case-study rank flip (Fig 6).
4. Main result (2.5 min) — Figs 3 and 4: between vs within.
5. Robustness and spatial checks (1.5 min) — Fig 5; "the coefficient is not biased".
6. Limitations, direction, next steps (1.5 min) — sections 12–13.
