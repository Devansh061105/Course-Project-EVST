# Which way does the link run? Path analysis (2026-11-16)

Reproduce: `python scripts/path_analysis.py` (cached data only, about 20 s).
Figure: `figures/fig14_direction.png`. Estimates: `data/path_analysis_estimates.csv`.

This addresses the open question in `TODO.md`: H1 as written has biodiversity
driving productivity, while species–energy theory has productivity driving bird
richness. **Short answer: this dataset cannot tell the two apart, and the one test
that could have done so fails its own validity check.** That supports framing H1
as an association and naming species–energy as the leading alternative.

## 1. Both directions fit equally well
Standardised path coefficients, controlling for climate and survey effort
(bootstrap 95% intervals over cells):

| | 1° (n = 220) | 0.5° (n = 671) |
|---|---|---|
| raw correlation, richness–GPP | +0.557 | +0.367 |
| richness → GPP | +0.273 [+0.180, +0.368] | +0.228 [+0.165, +0.290] |
| GPP → richness | +0.378 [+0.249, +0.508] | +0.291 [+0.204, +0.369] |

The two models are statistically equivalent: each reproduces the same partial
correlation between richness and GPP, so no fit statistic can prefer one. Writing
the arrow in either direction is a choice made from theory, not from these data.

## 2. About half of the raw correlation is shared climate
Of the raw correlation, 51% at 1° (38% at 0.5°) runs through temperature,
rainfall and effort acting on both variables; 49% (62%) is left as a direct link.

## 3. "Climate drives both and nothing else" is rejected across regions
The partial correlation of richness and GPP given climate and effort is +0.321
(p = 0.0001, SEs clustered by ecoregion) at 1° and +0.257 (p < 0.0001) at 0.5°.
So a pure common-cause model does not hold across the region. Within ecoregions
it very nearly does (`RESULTS_ADJUDICATION.md`: +0.030 at 1°, +0.058 at 0.5°).

## 4. The attempt to identify direction, and why it fails
Topographic heterogeneity (the SD of elevation in a cell) is a classic driver of
species richness. If it affected productivity only through richness, it would
separate the two stories:

- *richness → GPP* predicts heterogeneity and GPP are related given climate, and
  unrelated once richness is held fixed;
- *GPP → richness* predicts heterogeneity and GPP are unrelated given climate.

| test | 1° | 0.5° |
|---|---|---|
| heterogeneity → richness, given climate and effort | +0.491 (p < 0.0001) | +0.385 (p < 0.0001) |
| heterogeneity → GPP, given climate (claim of *GPP → richness*) | +0.546 (p = 0.0006) | +0.541 (p < 0.0001) |
| heterogeneity → GPP, given richness and climate (claim of *richness → GPP*) | +0.479 (p = 0.005) | +0.495 (p < 0.0001) |
| Shipley d-separation test, *GPP → richness* | C = 14.8, p = 0.0006 | C = 22.3, p < 0.0001 |
| Shipley d-separation test, *richness → GPP* | C = 10.6, p = 0.005 | C = 20.1, p < 0.0001 |
| two-stage least squares, richness → GPP | +1.114 [+0.695, +1.533] | +1.405 [+1.025, +1.785] |
| first-stage F | 18.7 | 28.8 |

**Both single-direction models are rejected**, because heterogeneity predicts GPP
on its own account: its coefficient barely moves when richness is added (+0.546 →
+0.479). Rugged natural-cover cells are more productive than their mean
temperature and rainfall suggest, whatever their richness. (A likely reason, not
tested here: the climate data are smooth at about 9 km, and hills keep forest that
plains have lost.)

That makes heterogeneity an **invalid instrument**. The two-stage estimate is 4.1
times the OLS coefficient at 1° and 6.2 times at 0.5°, which is what a violated
exclusion restriction looks like, not evidence of a large causal effect. The
first-stage F is adequate, so the problem is validity, not weakness.
**The IV number must not be quoted as an effect size.**

## What to say in the report
- The data support an association between effort-corrected richness and
  productivity across regions that climate alone does not explain.
- They do not identify its direction. Stating this, with the equivalence of the
  two path models as the reason, is stronger than asserting either direction.
- A natural experiment or time series would be needed; a cross-section of grid
  cells is not enough.

## Limits
- Bootstrap intervals resample cells independently, so they are somewhat narrow
  given the spatial autocorrelation; the clustered p-values in section 3 are the
  ones to rely on.
- Path analysis assumes linear relations and no unmeasured common causes beyond
  those in the model; the heterogeneity result is direct evidence that at least
  one more exists.

## References (Crossref-checked, 2026-11-16)
- Shipley (2000) A new inferential test for path models based on directed acyclic
  graphs. *Structural Equation Modeling* 7: 206–218. doi:10.1207/S15328007SEM0702_4
  (no abstract available; cited as the source of the d-separation test only)
- Grace et al. (2016) — already in the literature review.
