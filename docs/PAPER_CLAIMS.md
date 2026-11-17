# Claims and evidence, for turning this into a paper (2026-11-16)

Not the report. A map from each claim a paper could make to the evidence behind
it, the figure that shows it, and the caveat that has to travel with it. Use it
to decide what the paper says before writing a word of it.

## The one-sentence finding
Across South and Southeast Asia, effort-corrected species richness and
ecosystem productivity are positively associated, but most of the association
linear models report is broad-scale environmental structure: once that is
removed, by ecoregion, by flexible climate controls or by spatial scale, a
small, positive, taxon-consistent association of about 0.05–0.07 SD remains,
whose direction the data cannot identify.

## Claims a paper can make

| # | Claim | Strongest evidence | Figure | Caveat that must accompany it |
|---|---|---|---|---|
| 1 | Raw richness from citizen-science records is largely a map of survey effort, and rarefaction removes that dependence. | r with log effort 0.81 raw, 0.24 corrected. Thinning a cell to 250 records: raw count falls to 23%, corrected richness stays at 99.8%; refitted coefficient +0.255 to +0.274 against +0.273. | 7, 11 | Random thinning is not how real effort differs; that part is handled by the effort covariate and the mask. |
| 2 | Corrected richness estimates are precise: sampling error is 1% of their within-ecoregion variance. | Bootstrap SE median 0.5–0.8 species against an SD of 19; reliability 0.990 within ecoregions at both grains; SIMEX-corrected slopes unchanged. | — | Sampling error only, not observer preference. |
| 3 | With linear climate controls, richness is associated with productivity across the region (β ≈ +0.23 to +0.27). | Positive in 320 of 320 across-region specifications, 98.8% significant; unbiased under Hawkins subsampling; about 9% out-of-sample gain under block cross-validation. | 3, 12 | See claim 4: about half of this is non-linear climate. |
| 4 | **About half of that linear coefficient is curvature in the climate response.** | Double machine learning with spatially blocked cross-fitting: +0.289 → +0.172 / +0.144 at 1°; +0.182 → +0.073 at 0.5°. | 21 | 220 cells is small for tree ensembles; estimates vary by ±0.03 with learner. |
| 5 | **The association is a broad-scale phenomenon.** | Band regression on Moran eigenvector maps: slope +0.82 (1°) and +0.55 (0.5°) in the broadest patterns (patches about 700–800 km), near zero in finer ones. Local slopes rise from +0.01 to +0.26 as the window widens. Ecoregion fixed effects cut the coefficient by 75–90%. | 19, 9, 4 | Band boundaries are equal-count quarters, an arbitrary choice. |
| 6 | **A small positive association remains at local scale and within ecoregions, and it is demonstrably small.** | 0.5°: pooled over 35 ecoregions +0.069 (95% CI +0.030 to +0.108); mixed model +0.069; non-spatial component +0.092; flexible-control within estimate +0.050; +0.071 to +0.075 with coverage-based richness and +0.062 with records limited to 2019–23. Equivalence tests show it is less than half the linear across-region coefficient in all five samples. | 18, 20 | Detectable only at 0.5°; the 1° sample cannot resolve effects below about 0.15. |
| 7 | Ecoregions differ in the sign and size of the relationship. | I² = 46%, τ = 0.064, heterogeneity p = 0.002; 95% prediction interval −0.07 to +0.21; 5 ecoregions significantly positive, 3 negative. | 18 | Eight of 35 significant where about two are expected by chance; do not interpret single ecoregions. The local-slope stationarity test (p = 0.92) found no smooth geographic trend in the slope. |
| 8 | The pattern is shared by three groups of organisms recorded by different communities. | Plants: +0.264 across, −0.027 within (1°); +0.228, +0.015 (0.5°). Butterflies and moths: +0.512, −0.087. | 17 | Plant and butterfly samples are far from complete (coverage 0.34 at 100 records); the butterfly coefficient is not comparable in size. |
| 9 | The relationship is linear over the observed range; there is no hump. | Quadratic indistinguishable from linear in 11 of 12 specifications; slope positive among the richest quarter, 15% and 10% of cells at both grains. | 8, 13 | The fitted spline dips at the top at 1°; the upper-tail slopes show that is not in the data. |
| 10 | Richness does not buy stability of productivity beyond what climate explains. | Raw r = −0.36; with rainfall variability and mean GPP controlled, +0.14 (birds) and −0.09 (plants); zero within ecoregions for both. | 15 | MOD17 GPP is partly driven by its meteorological inputs, which works against finding a diversity effect. |
| 11 | Inference from gridded data like these must allow for spatial dependence: 221 cells are worth about 36 independent observations. | Clifford–Dutilleul effective sample size; climate-adjusted correlation p = 0.055 at 1°, 0.018 at 0.5°. | 5, 19 | — |
| 12 | Citizen-science bird records are near-complete at this grain over much of South Asia and thin in identifiable places. | Sample coverage: median 0.997 in modelled cells; 46 natural-cover cells excluded for lack of records. | 16 | A gap in GBIF is not always a gap in knowledge. |

## Claims a paper must not make
- **That biodiversity raises productivity, or carbon uptake.** Direction is not
  identified: the two path models are equivalent in fit and the attempted
  instrument fails its validity check (`RESULTS_DIRECTION.md`).
- **Anything about protected areas.** India's parks are largely missing from the
  public database (`RESULTS_EXTENSION_F.md`).
- **Anything about carbon stocks.** GPP and NPP are yearly fluxes.
- **That the result is "for India".** Only 36% of modelled cells are in India.
- **That the within-ecoregion effect is zero.** It is small and positive at 0.5°.

## What a reviewer will still ask for
1. **A second region or an independent dataset.** Everything rests on one region
   and one GBIF snapshot. (Deliberately out of scope: the team decided on
   2026-11-16 to keep the study to this region.)
2. **Direction.** A time series or natural experiment; a cross-section cannot do it.
3. **A productivity measure not modelled from climate.** MOD17 uses meteorological
   inputs, which builds some climate–GPP correlation in by construction. A
   solar-induced fluorescence product, or flux-tower GPP, would be the check.
4. **Citable data for the plant and butterfly records** (no GBIF DOI yet). The
   protected-area data are the November 2026 WDPA release.
5. **Richness of the producers themselves.** Plants are the group the theory is
   about, and their records are the weakest here.

## Suggested structure
Introduction (the policy claim and the sampling-bias problem) → Data and effort
correction (claims 1, 2) → The association and its robustness (3, 4, 9) → Scale
(5, 6, 7, 11) → Generality across taxa (8) → Stability (10) → What the data
cannot say (direction, protection) → Implications for monitoring (12).

Each number above is re-checked by `python scripts/reproduce_all.py`.
