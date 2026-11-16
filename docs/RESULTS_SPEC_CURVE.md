# Specification curve: 960 versions of the model (2026-11-16)

Reproduce: `python scripts/spec_curve.py` (cached data only; about 6 minutes).
Figure: `figures/fig12_spec_curve.png`. All 960 rows: `data/spec_curve.csv`.

The robustness matrix in `RESULTS_ADJUDICATION.md` section 4 changes one choice at
a time. This fits every combination, following the specification-curve idea of
Simonsohn, Simmons & Nelson (2020) and the multiverse analysis of Steegen et al.
(2016): results depend on analytic choices that are defensible but arbitrary, so
show all of them.

| choice | options |
|---|---|
| response | GPP, NPP, NDVI, EVI |
| richness measure | rarefied at 250, 100, 50 records; coverage-based at 0.90, 0.95 |
| land-cover mask | dominant class natural; natural fraction ≥ 0.5; ≥ 0.7; no mask |
| controls | effort + climate; + topography; + seasonality; + both |
| estimator | OLS; OLS with ecoregion fixed effects; spatial error model |

4 × 5 × 4 × 4 × 3 = **960 models**, each standardised within its own sample.

## Result
| estimator | models | median β | 10th–90th percentile | β > 0 | positive and p < 0.05 |
|---|---|---|---|---|---|
| OLS (across regions) | 320 | **+0.240** | +0.151 to +0.378 | 100.0% | 98.8% |
| ecoregion fixed effects (within) | 320 | **+0.039** | +0.009 to +0.110 | 95.9% | 11.2% |
| spatial error model | 320 | **+0.033** | −0.003 to +0.100 | 88.4% | 28.7% |
| all | 960 | +0.066 | −0.038 to +0.541 (full range) | 94.8% | |

- **No specification gives a significantly negative coefficient** (0 of 960).
- **The headline does not depend on a lucky choice.** Across regions the
  coefficient is positive in every one of 320 specifications and significant in
  98.8%. Within regions it is small and positive, and significant in only about a
  tenth to a quarter of specifications.
- **The split is by estimator, not by data choice** (Fig 12b). Changing the
  response, the richness measure, the mask or the controls moves the coefficient
  much less than switching between an across-region and a within-region estimator.

Median β by choice (OLS / within-region estimators):

| choice | option | OLS | within |
|---|---|---|---|
| response | NPP | +0.345 | +0.089 |
| | GPP | +0.242 | +0.033 |
| | NDVI | +0.211 | +0.047 |
| | EVI | +0.172 | +0.013 |
| richness | coverage 0.95 | +0.317 | +0.057 |
| | coverage 0.90 | +0.286 | +0.050 |
| | rarefied 250 | +0.246 | +0.035 |
| | rarefied 100 | +0.216 | +0.037 |
| | rarefied 50 | +0.209 | +0.021 |
| mask | natural ≥ 0.7 | +0.242 | +0.052 |
| | dominant class natural | +0.258 | +0.033 |
| | natural ≥ 0.5 | +0.255 | +0.033 |
| | no mask | +0.207 | +0.035 |
| controls | + topography | +0.305 | +0.020 |
| | effort + climate | +0.261 | +0.045 |
| | + both | +0.211 | +0.029 |
| | + seasonality | +0.203 | +0.056 |

NPP is the strongest response and the coverage-based richness measures give
larger coefficients than fixed-size rarefaction, both as already noted in
`RESULTS_ADJUDICATION.md`.

## Limits
- All 960 models use the 1° grid and the same GBIF pull; they are not independent
  tests, and the percentages above are descriptive, not a joint significance test.
- OLS standard errors are clustered by ecoregion; the spatial-error p-values use
  the model's own asymptotic errors.

## References (Crossref-checked and abstracts read, 2026-11-16)
- Simonsohn, Simmons & Nelson (2020) Specification curve analysis. *Nature Human
  Behaviour* 4: 1208–1214. doi:10.1038/s41562-020-0912-z
- Steegen, Tuerlinckx, Gelman & Vanpaemel (2016) Increasing transparency through a
  multiverse analysis. *Perspectives on Psychological Science* 11: 702–712.
  doi:10.1177/1745691616658637
