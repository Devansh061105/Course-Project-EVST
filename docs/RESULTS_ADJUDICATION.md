# Adjudication: what the richness–productivity association actually is (2026-10-06)

**This document supersedes the headline conclusions of `RESULTS_SPATIAL.md`
("H0 cannot be rejected") and `RESULTS_SENSITIVITY.md` ("specification-
dependent").** Those were correct about the model outputs but drew the wrong
inference. Five further analyses, all on the same 221 one-degree cells, resolve
the question.

Scripts: `adjudicate_lag_error.py`, `spatial_cv.py`, `hawkins_subsample.py`,
`robustness_suite.py`, `confounder_analysis.py`, `ecoregion_analysis.py`,
`coverage_rarefaction.py`. All coefficients standardised unless stated.

## The answer
Effort-corrected bird richness is **positively associated with productivity
across South and Southeast Asia**, and the association is real in the sense that matters for
estimation: it is not an artefact of spatial autocorrelation, and it transfers to
held-out regions. But it is **mostly a between-ecoregion pattern**. Adding
ecoregion fixed effects cuts the richness coefficient by about 75-90%: from
+0.273 to +0.030 at 1 degree (95% CI -0.08 to +0.14) and from +0.228 to +0.058
at 0.5 degree (95% CI +0.01 to +0.11, p = 0.021). Richness retains 38.5% (1
degree) to 59.9% (0.5 degree) of its variance within ecoregions, and ecoregion
identity also removes the broad residual autocorrelation that drove every earlier
spatial result.

**Correction (2026-10-06, after the 0.5-degree run).** Earlier versions of this
document said the association "vanishes" within ecoregions and that the 1-degree
null was "not a power failure". Both overstated it. The 1-degree within-ecoregion
test (n = 220, SE 0.055) could only detect effects of about 0.15 SD or more
(80% power); the 0.5-degree test (n = 671, SE 0.025) detects about 0.07 SD, and
finds +0.058. The two intervals overlap on [+0.01, +0.11], so the grains agree on
a **small positive within-ecoregion effect of roughly 0.03-0.06 SD**, which the
1-degree data were too coarse to resolve.

So the data show that species-rich *regions* are strongly more productive, and
that within a region places with more bird species are weakly more productive.
They do not show that local biodiversity raises local productivity, because the
direction is not identified (see interpretive caveats) and the within-region
effect is a quarter of the cross-regional one at best.

## 1. Spatial Durbin family (`adjudicate_lag_error.py`)
Nesting lag and error models in the Durbin family, 1°:

| model | AIC | richness β | p |
|---|---|---|---|
| OLS | 455.9 | +0.273 | <0.0001 |
| SLX | 418.8 | +0.116 | 0.051 |
| SAR (lag) | 210.1 | +0.079 | 0.005 |
| SEM (error) | 144.7 | +0.017 | 0.506 |
| SDM (Durbin lag) | 139.5 | +0.034 | 0.207 |
| **SDEM (Durbin error)** | **128.7** | +0.044 | 0.155 |

LR tests reject both pure forms against their Durbin extensions (SDM vs SAR
LR=78.6; SDM vs SEM LR=15.3, p=0.004). SDEM is best by AIC at 1° (gap 10.8 to
SDM); its richness effects are all non-significant (total +0.121, p=0.156). The
SDM gives significant impacts but with indirect effects 6.5× the direct effect
(total +0.743) — a global-spillover structure with no ecological mechanism for
productivity. At 2° SDM edges SDEM by AIC (69.7 vs 72.7, n=67).

Literature: Kissling & Carl (2008) found spatial-error SAR models the most
reliable on simulated species data, with lag and mixed models showing weak type I
error control and unpredictable bias. Halleck Vega & Elhorst (2015) advise
starting from local-spillover (SLX-type) models absent a theory for global
spillovers.

## 2. Spatial block cross-validation (`spatial_cv.py`)
Out-of-sample MSE reduction from adding richness to climate + effort, block
bootstrap weighting each held-out cell equally:

| scheme | R²oos without → with | MSE reduction | CI excludes 0 |
|---|---|---|---|
| random 10-fold | 0.489 → 0.539 | 9.6% | yes |
| 2° blocks | 0.466 → 0.515 | 9.2% | yes |
| 3° blocks | 0.440 → 0.496 | 9.9% | yes |
| 4° blocks | 0.425 → 0.480 | 9.4% | yes (borderline) |
| 6° blocks | 0.355 → 0.410 | 8.4% | no |
| 8° blocks | 0.293 → 0.348 | 7.8% | no |
| buffered LOO, 5° | 0.218 → 0.276 | 7.4% | yes |

The gain does not shrink under blocking; the 6°/8° CIs widen because 14–23
blocks leave little to resample. Leave-one-**ecoregion**-out: GPP +9.4%
[−0.4, +18.0]; NPP +14.2% [+0.8, +25.8].

**Superseded:** an earlier version (`adjudicate_lag_error.py` Part 2) reported
"no reliable gain" from averaging per-fold RMSE, which weights a 1-cell block
like a 15-cell block. That verdict was wrong.

Literature: Roberts et al. (2017) recommend blocked CV for structured data and
warn that blocking can force extrapolation — visible here as baseline R²oos
falling from 0.49 to 0.29 as blocks grow.

## 3. Hawkins et al. (2007) subsampling test (`hawkins_subsample.py`)
Residual correlogram: I = 0.67 at 0–1.5°, 0.25 by 4.5°, then a **plateau of
~0.15–0.19 out to 9°**, reaching zero only at ~10.5°. Fully independent
subsamples are infeasible (4–8 cells); spacings clearing the short-range decay:

| spacing | cells/subsample | median β [95%] | full β percentile | β>0 |
|---|---|---|---|---|
| ≥3.0° | 34 | +0.268 [+0.047, +0.509] | 52nd | 99% |
| ≥4.5° | 17 | +0.282 [−0.156, +0.707] | 48th | 91% |
| ≥6.0° | 13 | +0.298 [−0.320, +0.914] | 45th | 87% |

The full-data OLS estimate sits at the centre of every distribution: **not biased
by spatial autocorrelation**, as Hawkins et al. found for bird richness at the
same 110 km grain. Bini et al. (2009) report OLS-to-spatial shifts across 97
datasets as common but usually small; ours (−94%) is not small, which flags
richness as unusually entangled with regional structure — explained in §6.

## 4. Robustness matrix (`robustness_suite.py`)
One choice changed at a time; OLS β / SEM β (p) / 4° block-CV gain:

| variant | OLS | SEM | CV |
|---|---|---|---|
| GPP (baseline) | +0.273 | +0.017 (0.51) | +9.4% |
| **NPP** | **+0.384** | **+0.093 (0.008)** | **+14.6% \*** |
| NDVI | +0.274 | +0.044 (0.11) | +11.1% \* |
| EVI | +0.212 | +0.017 (0.45) | +7.0% |
| mask natural ≥ 0.5 | +0.286 | +0.023 (0.37) | +10.1% \* |
| mask natural ≥ 0.7 | +0.258 | +0.067 (0.028) | +9.0% |
| mask cropland+built < 0.3 | +0.249 | +0.016 (0.61) | +9.1% |
| no land-cover mask | +0.251 | +0.055 (0.002) | +7.4% |
| rarefied @100 | +0.242 | +0.011 (0.66) | +7.3% \* |
| rarefied @50 | +0.226 | −0.001 (0.97) | +6.2% |
| coverage 0.90 | +0.304 | +0.045 (0.16) | +11.3% |
| coverage 0.95 | +0.329 | +0.053 (0.16) | +12.4% |

Raw vs corrected richness on the **same 221 cells**: raw OLS +0.458, CV +8.5%
[−9.4, +23.5]; corrected OLS +0.273, CV +9.4% [−0.3, +19.2]. Similar average
transfer, but raw richness's out-of-sample benefit is far less consistent (CI
width 33 vs 19.5 points) and its in-sample coefficient overstates it. (An earlier
claim that raw richness "transfers worst" compared different cell sets — 253 vs
221 — and is withdrawn.)

**NPP is consistently stronger than GPP** and is the only response surviving the
spatial error model. NPP is the carbon left after plant respiration — the energy
available to consumers — which is what species–energy theory predicts bird
richness should track (Evans et al. 2005; Hurlbert 2004). **Qualifier (review,
2026-10-06):** MOD17 NPP is GPP minus *modelled*, temperature-driven respiration.
It is near zero in the hot Thar cells (NPP/GPP 0.03–0.18) and at the ~0.70
ceiling in cold Tibetan cells, so part of NPP's stronger association may be the
algorithm stretching the climatic extremes rather than ecology. Treat the
species–energy reading as consistent with the NPP result, not demonstrated by it.

## 5. Confounders (`confounder_analysis.py`, `gee_confounders.py`)
| GPP model | OLS β | CV | residual plateau I |
|---|---|---|---|
| baseline | +0.273 | +9.4% \* | 0.166 |
| + elevation, topographic heterogeneity | +0.320 | +11.8% \* | 0.137 |
| + NDVI seasonality | +0.218 | +7.7% | 0.159 |
| + all | +0.242 | +8.3% \* | 0.150 |

Topographic heterogeneity is a **suppressor**: rugged cells are species-rich
(r = +0.25; Stein et al. 2014) but slightly less productive, so controlling for it
raises the richness coefficient. Seasonality absorbs ~20% (Coops et al. 2009: the
seasonal component of MODIS fPAR best predicts bird richness). **Neither touches
the residual plateau.** SEM stays non-significant for GPP throughout.
Temperature and mean elevation are collinear (VIF 89 / 77; lapse rate);
richness's own VIF is 1.87, so its coefficient is unaffected, but write-ups should
use elevation SD alone.

## 6. Ecoregions — the decisive analysis (`ecoregion_analysis.py`)
RESOLVE Ecoregions 2017 (Dinerstein et al. 2017): 220 of 221 cells, 56
ecoregions, 8 biomes, 2 realms. SEs cluster-robust by ecoregion — **this is plan
Step 8 as written**, replacing the 4° block approximation.

| GPP model | β | se | p | residual plateau |
|---|---|---|---|---|
| A — baseline, clustered by ecoregion | +0.273 | 0.072 | 0.0001 | 0.170 |
| + realm FE | +0.271 | 0.069 | 0.0001 | 0.173 |
| B — + biome FE | +0.182 | 0.079 | 0.021 | 0.141 |
| **C — + ecoregion FE (within)** | **+0.030** | **0.055** | **0.587** | **−0.027** |
| D — moist broadleaf biome only | +0.147 | 0.146 | 0.313 | 0.135 |

NPP: A +0.383; B +0.257 (p=0.003); C +0.099 (p=0.12); SEM + biome FE +0.079
(p=0.019).

**Variance within ecoregions:** richness 38.5%, GPP 9.8%, NPP 15.6%,
temperature 4.1%, precipitation 24.8%. The within-ecoregion test is not starved
of *predictor* variation, but GPP has little variance left (9.8%), so the test is
weak at this grain: SE 0.055 gives a minimum detectable effect of ~0.15 SD. The
non-significant 1-degree result is therefore compatible with a small true effect
(the 0.5-degree run in section 8 finds +0.058). Coverage-standardised richness
gives the same within-ecoregion result (GPP +0.033–0.038, p ≈ 0.6).

**Ecoregion fixed effects eliminate the residual plateau (0.170 → −0.027).**
The unidentified regional driver behind the spatial-error results was biogeography.

## How the pieces fit
- OLS sees the cross-regional pattern; its estimate is unbiased (§3).
- The spatial error model absorbs that pattern as regional structure (λ ≈ 0.9),
  because richness varies at the same ~1000 km scale as the residual (§1, §3).
- Block CV finds richness transferable because a cell's richness signals what
  *kind* of region it sits in (§2).
- Within regions most of it is gone, but a small positive effect remains at 0.5° (§6, §8).

## Interpretive caveats for the report
1. **Direction.** Bird richness is an implausible *cause* of plant productivity;
   the BEF mechanisms in the literature review (complementarity, canopy structure)
   concern plant diversity. The species–energy literature treats productivity as
   the driver of bird richness (Evans et al. 2005; Hurlbert 2004; Coops et al.
   2009). The plan's H1 is framed biodiversity → productivity; the data cannot
   distinguish the directions, and theory favours the reverse.
2. **Scale.** The between/within contrast mirrors Chase & Leibold (2002), where
   the same data gave a hump among ponds and a positive line among watersheds.
3. **The plan's case is still served.** Extension A's reveal holds and sharpens:
   raw → corrected → within-ecoregion strips the association step by step, and
   each step is attributable to a named mechanism (effort, climate, biogeography).

## 7. Time-window match (`gbif_timewindow.py`)
Records restricted to 2019–2023 to match the environmental means; re-pulled for
the 267 cells passing the land-cover mask. 2019–23 records are a median 51% of
the 2000–24 total (eBird growth). Rarefied richness from the two windows
correlates r = 0.938 (203 shared cells).

| | 2000–24 (main, n=221) | 2019–23 (n=203) |
|---|---|---|
| GPP OLS | +0.273 | +0.223 |
| GPP SEM | +0.017 (0.51) | +0.030 (0.27) |
| GPP 4° block CV | +9.4% | +5.8% [−3.3, +14.9] |
| GPP within-ecoregion | +0.030 (0.59) | +0.003 (0.97) |
| NPP SEM | +0.093 (0.008) | +0.090 (0.010) |
| NPP within-ecoregion | +0.099 (0.12) | +0.057 (0.50) |

Same qualitative picture. OLS shrinks slightly and CV loses significance, both
expected with half the records (noisier richness) and 18 fewer cells. The
within-ecoregion null strengthens.

## Figures (`make_figures.py` → `figures/`)
Each PNG has a CSV of its plotted values beside it (table view).
1. `fig1_study_area_mask` — grid, mask classes, case-study boxes.
2. `fig2_maps_richness_gpp` — corrected richness and GPP maps.
3. `fig3_attenuation` — richness β (GPP, NPP) across specifications.
4. `fig4_between_within` — between- vs within-ecoregion partial plots, both net
   of effort and climate (between slope 0.0127/species, p=0.002; within 0.0012,
   p=0.53).
5. `fig5_correlogram` — residual Moran's I with and without ecoregion FE.
6. `fig6_case_study_spreads` — effort 138.8×, GPP 10.0×, raw richness 2.2×,
   corrected richness 1.3×.
7. `fig7_naive_vs_corrected` — Extension A scatter (raw vs rarefied richness vs GPP;
   effort correlation 0.81 → 0.24).
8. `fig8_linear_vs_quadratic` — Extension B partial-residual plot (ΔAIC +1.9).

Palette validated with the dataviz validator against #ffffff (slots 1–3,
all-pairs PASS; aqua at 2.82:1 is direct-labelled per the relief rule).
Corrections made during visual review: fig3 rows relabelled because they are not
cumulative and its first title was false (effort correction *raises* β); fig4
left panel re-done net of climate/effort so both panels share the same
adjustment; fig6 dodged so Western Ghats is not hidden under E Himalaya.

## 8. The 0.5-degree grid (`grid_robustness.py 0.5`, `grain_0p5_analysis.py`)
3,340 land cells pulled (0 facet-truncated), 672 pass the mask and have >= 250 species-identified
records (needed to rarefy at n = 250) (671 with an ecoregion, in 64 ecoregions and 10 biomes).
GPP only (the 0.5-degree extractor does not pull NPP).

| GPP, standardised, SEs clustered by ecoregion | 1 deg (n=220) | 0.5 deg (n=671) |
|---|---|---|
| A baseline (effort + climate) | +0.273 (p=0.0001) | +0.228 (p<0.0001) |
| B + biome FE | +0.182 (p=0.021) | +0.151 (p=0.001) |
| C + ecoregion FE (within) | +0.030 (p=0.59) | **+0.058 (p=0.021)** |
| spatial error (queen) | +0.017 (p=0.51) | **+0.090 (p<0.0001)**, lambda 0.88 |
| 4-degree block CV, MSE reduction | +9.4% [+0.2, +19.2] | +6.0% [-1.1, +12.5] |
| 2-degree block CV | +9.2% [+0.2, +17.5] | +6.1% [+0.2, +12.1] |
| residual plateau after ecoregion FE | -0.027 | -0.011 |
| richness variance within ecoregions | 38.5% | 59.9% |
| min. detectable within effect (80% power) | 0.154 SD | 0.070 SD |

What this changes:
- The **spatial error null does not replicate**. At 0.5 degree the error model
  (preferred by AIC and robust LM, robust LM error 192 vs lag 21) keeps richness
  significant. The 1-degree null was partly a grain / power result, not purely
  "the error process absorbing everything".
- **Ecoregion FE still remove most of the association** (0.228 -> 0.058, 75%) and
  still flatten the broad residual plateau, so the between-region story stands.
- The earlier robustness claim "10/10 weights specifications prefer the spatial
  error model" was at 1 degree only; it also holds at 0.5 (AIC winner: error).
- Block CV gain is a little smaller and its 4-degree CI now includes 0; the 2-degree
  CI excludes it. Blocking at this grain leaves 44-112 blocks.

## 9. Stress-testing the 0.5-degree within-ecoregion effect (`grain_0p5_extended.py`)
Elevation SD, NDVI seasonality (`gee_confounders.py 0.5`) and NPP added at 0.5
degree. n = 671 cells, 64 ecoregions, SEs clustered by ecoregion, standardised.

| within-ecoregion richness coefficient | GPP | NPP |
|---|---|---|
| ecoregion FE, effort + climate | +0.058 (p=0.021) | +0.077 (p=0.016) |
| + topographic heterogeneity (elev. SD) | +0.041 (p=0.081) | +0.052 (p=0.068) |
| + NDVI seasonality | +0.068 (p=0.005) | +0.089 (p=0.005) |
| + both | **+0.051 (p=0.024)** | **+0.064 (p=0.020)** |

- **Not driven by any one ecoregion.** Dropping each of the 64 in turn: GPP β
  stays between +0.046 and +0.071, p < 0.05 in 64/64 refits.
- **Mixed on topography.** Topographic heterogeneity alone pulls p above 0.05 (it
  absorbs about a quarter of the effect), while seasonality raises it. Together
  the effect survives at p ≈ 0.02, but it is not far from the threshold.
- **Thin within biomes.** Estimated separately, the two largest biomes (moist
  broadleaf n=388; dry broadleaf n=92) give only about +0.03 (p = 0.4-0.5);
  temperate conifer +0.12 (p = 0.16, 43 cells). With 6-31 ecoregions per biome
  these tests are weak, so this is not evidence of absence, but the pooled +0.05
  is not uniformly supported.
- **Small out-of-sample value.** Leave-one-ecoregion-out CV: richness reduces MSE
  by 4.9% for GPP [-0.3, +9.3] and 4.5% for NPP [-1.1, +9.1]; both intervals
  touch zero.
- NPP again gives the larger coefficient, as at 1 degree.

**Net reading.** A small positive within-ecoregion association of about
0.04-0.07 SD is supported at 0.5 degree and survives elevation-heterogeneity and
seasonality controls. It is real enough not to be called zero, small enough
(a quarter of the cross-regional effect) that it should not carry a causal claim,
and fragile enough (topography, individual biomes, out-of-sample) that the report
should present it as a range, not a point.

## Still outstanding
- Everything else is in `TODO.md`.