# Extension B — linear or hump-shaped? (2026-10-06)

Reproduce: `python scripts/extension_b.py`. Richness is mean-centred before
squaring (otherwise x and x² are near-collinear and the quadratic term's SE is
meaningless). Tested under OLS, ML_Lag and ML_Error, at two grains, at three
rarefaction levels. ΔAIC = AIC(quadratic) − AIC(linear); |ΔAIC| < 2 is
conventionally "indistinguishable".

## Result: linear. No support for a hump.

| spec | model | ΔAIC | b₂ (p) | turning point |
|---|---|---|---|---|
| 1°, rare250 | OLS | +1.93 | +1.8e-05 (0.75) | outside range |
| 1°, rare250 | ML_Lag | +2.00 | +2.3e-06 (0.95) | outside range |
| 1°, rare250 | ML_Error | −0.31 | −4.4e-05 (0.13) | inside, n.s. |
| 1°, rare100 | OLS | −0.57 | +4.7e-04 (0.063) | inside, convex |
| 1°, rare100 | ML_Lag | +1.18 | +1.4e-04 (0.36) | — |
| 1°, rare100 | ML_Error | +0.91 | −1.3e-04 (0.30) | — |
| 1°, rare50 | OLS | **−4.49** | **+2.7e-03 (0.0002)** | inside, **convex** |
| 1°, rare50 | ML_Lag | −1.36 | +1.0e-03 (0.064) | — |
| 1°, rare50 | ML_Error | +1.88 | −1.4e-04 (0.73) | — |
| 2°, rare250 | OLS | +2.00 | +1.7e-06 (0.99) | outside range |
| 2°, rare250 | ML_Lag | +1.53 | +4.9e-05 (0.49) | outside range |
| 2°, rare250 | ML_Error | +0.88 | +7.2e-05 (0.29) | inside, n.s. |

**11 of 12 specifications are indistinguishable from linear.** In the primary
specification (1°, n=250, the level used throughout Extension A) the quadratic
term is non-significant under all three models, and under OLS and ML_Lag its
turning point falls outside the observed richness range entirely — a gently
curved slope, not a hump.

## The one exception argues against the hump, not for it
The single case where the quadratic wins on AIC — 1°, rarefied at n=50, OLS,
ΔAIC = −4.49, p = 0.0002 — has a **positive** squared term. A vertex inside the
data range with b₂ > 0 is a **minimum**, a U shape, not the hump-backed model.
Richness would have to *decrease* productivity at low diversity and increase it
at high diversity, which no study in the literature review proposes.

It also fails to replicate: under ML_Lag it weakens to p = 0.064, and under
ML_Error the sign flips to negative at p = 0.73. It is most likely an artefact of
rarefying to only 50 records, where the richness estimate is noisiest.

(An earlier version of the script mislabelled this case "a real hump" because it
checked only whether the vertex lay inside the data range, not the sign of b₂.
Fixed — the label now distinguishes concave humps from convex minima.)

## Where this lands in the literature debate
The plan frames Extension B as a test between two camps in the review:

- **Linear / complementarity** — Liang et al. (2016) report a positive
  concave-down relationship in global forests; Deng et al. (2025) give the
  canopy-structure mechanism. **This is the side our data support.**
- **Unimodal / selection effects** — Fraser et al. (2015) recover the classical
  hump in global grasslands. **Not supported here.**
- **Saturation at scale** — Gonzalez et al. (2020). Our concave-down term under
  ML_Error (b₂ = −4.4e-05) points weakly this way but is non-significant
  (p = 0.13), so it is at most a hint.

Worth noting Liang et al. describe their relationship as concave-*down*, i.e.
decelerating, which is a mild version of what our ML_Error specification hints
at. We cannot distinguish decelerating-positive from straight-line at this n.

## The caveat that governs this result
Extension B asks what *shape* the relationship has. Extension A and the spatial
refit showed the relationship's *existence* is specification-dependent: under the
spatial error model at 1°, the linear richness term is itself non-significant
(p = 0.51). Fitting a curve to an association that may not be there is a weak
exercise.

The defensible statement for the report is therefore:

> There is no evidence of a hump-shaped biodiversity–productivity relationship at
> this grain. Where an association is detectable at all, it is adequately
> described by a straight line; adding curvature never improves fit by a
> meaningful margin.
