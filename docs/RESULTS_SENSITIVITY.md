# Sensitivity checks (plan Step 8) — 2026-10-06

> **SUPERSEDED 2026-10-06 by `RESULTS_ADJUDICATION.md`.** The lag-vs-error split is resolved there: Durbin-family tests, block CV, the Hawkins subsampling test and ecoregion fixed effects. Kept for history.

## 1. Spatial weights: the null is robust at 1 degree
Same specification, n = 221, ten weights matrices
(`scripts/weights_sensitivity.py`):

| weights | β richness | p | AIC winner | resid Moran I (p) |
|---|---|---|---|---|
| queen contiguity | +0.00069 | 0.506 | error | +0.034 (0.21) |
| distance band 1.0° | +0.00111 | 0.367 | error | −0.126 (0.02) |
| distance band 1.5° | +0.00069 | 0.506 | error | +0.034 (0.20) |
| distance band 2.0° | +0.00096 | 0.387 | error | +0.048 (0.09) |
| distance band 2.5° | +0.00174 | 0.157 | error | +0.057 (0.03) |
| distance band 3.0° | +0.00131 | 0.319 | error | +0.062 (0.02) |
| kNN k=4 | +0.00109 | 0.328 | error | +0.002 (0.45) |
| kNN k=6 | +0.00161 | 0.150 | error | +0.061 (0.04) |
| kNN k=8 | +0.00166 | 0.155 | error | +0.064 (0.02) |
| kNN k=12 | +0.00263 | **0.041** | error | +0.051 (0.02) |

Spatial error wins AIC in **10/10**. Richness is non-significant in **9/10**
(p = 0.15–0.51); only kNN k=12 reaches significance, marginally. β stays in
0.0007–0.0026 throughout, against the OLS estimate of 0.011. Queen contiguity
and distance band 1.5° are identical, as expected on a regular 1° lattice.

**Conclusion: at 1°, the null does not depend on the weights choice.**

## 2. Grid size: the conclusion is NOT robust to grain
`scripts/grid_robustness.py`. This is the important caveat.

| grain | n | robust LM lag | robust LM err | AIC lag | AIC err | preferred |
|---|---|---|---|---|---|---|
| 1.0° | 221 | 24.8 | 29.4 | 102.85 | **31.11** | **error** |
| 2.0° | 67 | 19.8 | 0.0 | **32.00** | 38.09 | **lag** |

Richness coefficient under each model:

| grain | ML_Lag β (p) | ML_Error β (p) |
|---|---|---|
| 1.0° | +0.00350 (**0.0025**) | +0.00069 (0.506) |
| 2.0° | +0.00698 (**0.0001**) | +0.00021 (0.917) |

Both grains leave spatially clean residuals under both models, so neither is
rejectable on diagnostics alone (1°: lag I=+0.161 p=0.002 — not clean; error
I=+0.034 p=0.20. 2°: lag I=+0.083 p=0.17; error I=+0.074 p=0.17).

**The result is specification-dependent, and the preferred specification flips
with grain.** The lag family says richness matters at both grains; the error
family says it does not at either. At 1° the evidence favours the error family
decisively (AIC gap of 72, robust LM slightly favours error, and the lag model's
residuals are *not* clean). At 2° it favours the lag family (robust LM 19.8 vs
0.0, AIC gap of 6 — much weaker).

0.5° is running and is the tiebreaker.

## What this means for the write-up
The honest statement is **not** "H0 cannot be rejected". It is:

> Whether effort-corrected richness predicts productivity depends on how the
> spatial dependence is modelled. If the dependence is in the outcome (a spatial
> lag — productivity in one cell responds to productivity in its neighbours),
> richness retains a significant positive association. If it is in the errors (a
> spatial error — some unmeasured, spatially structured driver affects both),
> richness does not. At 1° the data favour the error interpretation; at 2° they
> favour the lag interpretation.

This is a stronger result than a clean yes or no, because it localises exactly
where the uncertainty lives. It also bears directly on Grace et al. (2016) from
the literature review: an unmeasured spatially structured common cause is
precisely what a spatial error model represents.

## Still outstanding
- 0.5° run (in progress, ~105 min: 3,536 GBIF cells + Earth Engine).
- Rarefaction level sensitivity (n=50 / 100 / 250 columns already exist in
  `data/gbif_cells.csv`, not yet modelled).
- Extension B (linear vs quadratic, AIC) has not been run.

## Bug fixed during this work
`grid_robustness.py` initially trimmed MOD17 and WorldCover-natural to single
bands to save compute, which made `reduceRegions` name their outputs `mean`
instead of `gpp`/`natural_frac`. Both columns came back null for all 221 cells
and the filter silently returned zero eligible rows. Fixed with `setOutputs`,
and a guard now aborts loudly if any required column is entirely null. This is
the same root cause as the earlier `wc_mode` bug: **single-band images are named
by the reducer, not the band.**
