# Spatial refit — the result that changes the conclusion (2026-10-05)

> **SUPERSEDED 2026-10-06 by `RESULTS_ADJUDICATION.md`.** The model outputs below are correct; the conclusion "H0 cannot be rejected" is not. The association is real across regions (unbiased per the Hawkins test, transferable under block CV) but shrinks by ~75-90% within ecoregions (a small positive effect remains at 0.5°). Kept for history.

Reproduce: `python scripts/spatial_refit.py` (plus the LM specification tests).
n = 221 cells, same specification as Extension A:
`gpp ~ rarefied_250 + log_effort + temp_c + precip_mm_yr`.

## Why this was necessary
Extension A reported rarefied richness at p = 1.6e-08 using HC3 errors. But
Moran's I on those residuals was 0.723 (z = 15.4, p = 0.001): neighbouring cells
are strongly non-independent, so those standard errors are too small. The plan
makes this check mandatory in Step 8, and Ploton et al. (2020) — cited in the
literature review — is specifically about this failure.

## Which spatial specification is correct
| test | statistic | p |
|---|---|---|
| LM lag | 220.88 | 5.8e-50 |
| LM error | 225.47 | 5.8e-51 |
| robust LM lag | 24.84 | 6.2e-07 |
| **robust LM error** | **29.43** | **5.8e-08** |

| model | AIC | residual Moran's I | p |
|---|---|---|---|
| OLS | — | +0.7233 | 0.001 |
| spatial lag | 102.85 | +0.1612 | 0.002 |
| **spatial error** | **31.11** | **+0.0336** | **0.198** |

The spatial **error** model wins on every criterion: higher robust LM, AIC lower
by 72, and it is the only specification whose residuals are spatially clean
(the lag model still leaves significant autocorrelation). Residual Moran's I for
the error model must be computed on `e_filtered`, not `u` — testing `u` gives a
misleadingly high 0.878 because `u` is the unfiltered `y − Xb`.

Note `pr2` is **not** comparable between lag and error models (the lag model's
includes the lag term's own explanatory power). AIC and residual diagnostics are
the right criteria here.

## The verdict on rarefied richness

| estimator | β | se | p | |
|---|---|---|---|---|
| OLS + HC3 (Extension A) | +0.01097 | 0.00194 | <0.0001 | significant |
| OLS + cluster-robust (4° blocks, 39 clusters) | +0.01097 | 0.00287 | 0.0001 | significant |
| spatial lag (ML) | +0.00350 | 0.00116 | 0.0025 | significant |
| **spatial error (ML) — correct specification** | **+0.00069** | **0.00104** | **0.5059** | **NOT significant** |

**Once spatial dependence is modelled correctly, the biodiversity–productivity
association does not survive.** The coefficient falls by 94% from the Extension A
estimate and is indistinguishable from zero.

Climate does survive: temp p = 0.0009, precip p < 0.0001 in the same model.
Sampling effort is non-significant throughout (p = 0.14 to 0.81), which is
expected — rarefaction had already stripped the effort signal out of richness
(r fell from 0.809 to 0.241).

## What this means
**H0 cannot be rejected.** The plan states it as: "No meaningful association
remains once sampling effort, climate, and land cover are properly accounted
for." That is what the data show, with spatial dependence added to the list.

This is a valid and reportable finding, not a failure. The plan's own risk table
anticipates it — "Weak/null correlation after correction → Frame explicitly as a
valid finding. Several cited studies report the relationship weakening at scale,
which would align with, not contradict, existing literature." It is consistent
with Adler et al. (2011) and with Gonzalez et al. (2020) on scale dependence,
both already in the literature review.

**The naive-vs-corrected gap is still the strongest presentation moment** — it is
just larger than the plan expected. Raw richness alone: β = +0.445 standardised,
p < 1e-11. Fully corrected with spatial structure: indistinguishable from zero.
Three separate corrections each remove part of the apparent signal:

1. rarefaction decouples richness from observer effort (r 0.809 → 0.241)
2. climate controls halve what remains (standardised β 0.558 → 0.273)
3. spatial structure removes essentially all of the rest (β → 0.0007, p = 0.51)

## Caveats on this result
- n = 221 after masking; the cropland and water exclusions are aggressive.
- Distance-band weights at 1.5° are one reasonable choice; the result should be
  checked against queen contiguity and a different threshold before the final
  report, and against the 0.5°/2° grid-size robustness runs (plan Step 8).
- The ML_Error optimiser emits a bounded-method tolerance warning; benign, but
  worth re-running with an alternative method as a check.
- A null result at 1° does not imply a null at plot scale. The forest-inventory
  studies in the literature review operate at a completely different grain.
