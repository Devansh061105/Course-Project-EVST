# Inference: how solid, how large, and at what scale (2026-11-16)

Five analyses on the existing study region and data, aimed at the questions a
journal reviewer would ask of the main result. Nothing here is a new extension.
All run from cached data.

| # | Question | Script | Figure |
|---|---|---|---|
| 1 | Is the cross-regional coefficient just badly controlled climate? | `dml_flexible.py` | `fig21_flexible_controls` |
| 2 | Is the weak within-ecoregion slope just noise in the richness estimates? | `measurement_error.py` | — |
| 3 | How small is the within-ecoregion effect, stated as a bound? | `within_effect_bounds.py` | `fig20_within_bounds` |
| 4 | What is the slope inside each ecoregion, and do ecoregions differ? | `within_effect_bounds.py` | `fig18_ecoregion_slopes` |
| 5 | At what spatial scale does the link live, and how many independent observations are there? | `scale_decomposition.py` | `fig19_scale_bands` |

## What changes in the project's conclusions
**The headline cross-regional coefficient (+0.27) was overstated; the best
single description is now a small positive association of about +0.05 to +0.07
SD that holds both across and within regions at 0.5°, plus a broad-scale
component that linear climate controls had been attributing to richness.**

1. With flexible, non-linear controls the across-region coefficient falls from
   +0.29 to +0.14–0.17 at 1° and from +0.18 to +0.07 at 0.5° (section 1).
2. At 0.5° that flexible across-region estimate (+0.07) and the within-ecoregion
   estimates (+0.05 to +0.07, sections 1, 3, 4) agree. Two different ways of
   removing broad environmental structure give the same answer.
3. The within-ecoregion effect is real but small at 0.5° (pooled +0.069, 95% CI
   +0.030 to +0.108) and demonstrably less than half the linear across-region
   coefficient in all five samples (section 3).
4. It is not an artefact of measurement error (section 2).
5. The large linear coefficient comes from the broadest spatial patterns, patches
   of roughly 700–800 km, where three-quarters of the climate-adjusted variation
   in productivity sits (section 5).
6. By a test that respects spatial autocorrelation, the 221 one-degree cells are
   worth about 36 independent observations, and the climate-adjusted correlation
   is then borderline (p = 0.055) at 1° and significant (p = 0.018) at 0.5°.

`RESULTS_ADJUDICATION.md` reached "strong across regions, weak within". That
stands as a description of the linear models. This document adds that the
"strong across regions" part is mostly non-linear environment.

---

## 1. Flexible controls (double/debiased machine learning)
Every earlier model controls for climate with straight lines. If productivity
or richness responds to temperature and rainfall with curvature or interactions,
linear controls leave climate signal in the richness coefficient.

Method (Chernozhukov et al. 2018), for GPP = θ·richness + g(controls) + noise:
predict GPP from the controls with a flexible learner, out of fold; predict
richness the same way; regress residuals on residuals. Controls: effort,
temperature, precipitation, mean elevation, topographic heterogeneity, NDVI
seasonality. Folds are 4° spatial blocks, so no cell is predicted from its
neighbours; five repeated splits combined by the median rule; standard errors
clustered by ecoregion. "Within ecoregions" removes each ecoregion's mean from
GPP and richness first.

| | learner | 1° θ (p) | 0.5° θ (p) |
|---|---|---|---|
| **across regions** | straight-line controls | +0.289 (< 0.0001) | +0.182 (0.0001) |
| | random forest | **+0.172 (0.015)** | **+0.073 (0.080)** |
| | gradient boosting | +0.144 (0.021) | +0.073 (0.051) |
| **within ecoregions** | straight-line controls | +0.098 (0.065) | +0.064 (0.012) |
| | random forest | +0.075 (0.19) | +0.050 (0.040) |
| | gradient boosting | +0.080 (0.15) | +0.045 (0.11) |

n = 220 (1°) and 671 (0.5°).

- **Flexible controls remove 40–50% of the across-region coefficient at 1° and
  about 60% at 0.5°.** The flexible learners predict GPP much better out of fold
  than a linear model (R² 0.69–0.77 against 0.52 at 1°; 0.67 against 0.44 at
  0.5°), so the straight-line controls were leaving real climate structure
  behind.
- **What remains is positive at both grains**, significant at 1° (p ≈ 0.02) and
  borderline at 0.5° (p = 0.05–0.08).
- **Within ecoregions the learner makes little difference** (+0.05 to +0.10),
  as expected: once ecoregion means are removed the controls predict almost
  nothing out of fold.

Limits: 220 cells is a small sample for tree ensembles. They under-fit, which
leaves some confounding in and biases θ upward if anything. The "straight-line"
row here differs slightly from the OLS in `RESULTS_EXTENSION_A.md` (+0.273)
because it adds topography and seasonality as controls and is fitted out of
fold. Random-forest results depend on the scikit-learn version, so the
reproducibility check on them has a wide tolerance (±0.04).

## 2. Measurement error in richness
A slope is biased towards zero when its predictor is noisy, and inside an
ecoregion the true differences between cells are small, so noise is a larger
share of the signal. Could that be why the within-ecoregion slope is weak?

Each cell's rarefied richness was given a standard error by bootstrapping its
species-abundance vector (multinomial resampling of its records, 200 times).

| | 1° | 0.5° |
|---|---|---|
| standard error of a cell's richness, median / 90th percentile / max (species) | 0.53 / 1.91 / 3.52 | 0.84 / 2.38 / 3.56 |
| SD of richness across cells (species) | 19.3 | 18.6 |
| reliability, raw richness | 0.997 | 0.994 |
| reliability, net of controls | 0.995 | 0.993 |
| **reliability, net of controls and ecoregion** | **0.990** | **0.990** |
| within-ecoregion slope, observed → corrected by reliability → SIMEX | +0.030 → +0.030 → +0.031 | +0.058 → +0.058 → +0.058 |
| across-region slope, observed → corrected → SIMEX | +0.273 → +0.274 → +0.275 | +0.228 → +0.229 → +0.229 |

**No.** Even inside ecoregions 99% of the variation in richness is signal.
Correcting for the error, by the reliability ratio or by simulation-extrapolation
(Cook & Stefanski 1994), changes no slope in the second decimal place.

This covers sampling error only. Bias from observers preferring certain
habitats or species is not sampling error and is not corrected by this; that is
what the effort covariate and the land-cover mask are for. The bootstrap also
cannot see species that were never recorded.

## 3. Bounds on the within-ecoregion effect
"Not significant" is not a finding. Equivalence tests (two one-sided tests;
Lakens 2017) ask instead whether the effect is demonstrably smaller than a
stated size.

| sample | n | across | within (90% CI) | smaller than half the across effect? | smaller than 0.10? | largest effect compatible (95%) | detectable with 80% power |
|---|---|---|---|---|---|---|---|
| birds, 1° | 220 | +0.273 | +0.030 (−0.060, +0.120) | **yes**, p = 0.026 | not shown, p = 0.10 | +0.120 (44% of across) | 0.154 |
| birds, 0.5° | 671 | +0.228 | +0.058 (+0.017, +0.099) | **yes**, p = 0.013 | **yes**, p = 0.046 | +0.099 (43%) | 0.070 |
| plants, 1° | 193 | +0.264 | −0.027 (−0.092, +0.038) | **yes**, p = 0.004 | **yes**, p = 0.033 | +0.038 (14%) | 0.111 |
| plants, 0.5° | 425 | +0.228 | +0.015 (−0.043, +0.074) | **yes**, p = 0.003 | **yes**, p = 0.009 | +0.074 (32%) | 0.099 |
| butterflies and moths, 1° | 139 | +0.512 | −0.087 (−0.239, +0.065) | **yes**, p = 0.033 | not shown, p = 0.44 | +0.065 (13%) | 0.258 |

**In all five samples the within-ecoregion effect is shown to be less than half
the linear across-region coefficient.** In three of five it is also shown to be
below 0.10 SD. The 1° bird sample and the butterfly sample are too small to
establish the tighter bound; their "detectable effect" column says why.

The five samples share cells and are not independent, so they are reported side
by side and not pooled.

## 4. The slope inside each ecoregion
Richness and GPP were residualised on the controls and on ecoregion means; a
slope was then fitted inside every ecoregion with at least 8 cells, and the
slopes combined by random-effects meta-analysis (DerSimonian & Laird 1986).
Ecoregions are separate sets of cells, so they can be treated as independent.

| | 0.5° | 1° |
|---|---|---|
| ecoregions (cells) | 35 (567 of 671) | 7 (85 of 220) |
| **pooled slope (95% CI)** | **+0.069 (+0.030, +0.108), p = 0.0006** | +0.028 (−0.086, +0.141), p = 0.63 |
| between-ecoregion SD of the slope (τ) | 0.064 | 0.116 |
| I² | 46% | 63% |
| heterogeneity test | Q = 62.4 on 34 df, p = 0.002 | Q = 16.0 on 6 df, p = 0.014 |
| 95% prediction interval for a new ecoregion | −0.068 to +0.205 | −0.306 to +0.362 |
| slope positive | 27 of 35 | 5 of 7 |
| individually significant | 5 positive, 3 negative | 1 positive, 1 negative |
| mixed model with random slopes: fixed slope (SD of slope) | +0.069, p = 0.0007 (0.048) | +0.054, p = 0.16 (0.076) |

- **At 0.5° the within-ecoregion effect is small, positive and clearly not
  zero**, and a mixed model with random slopes gives the same number (+0.069).
- **Ecoregions genuinely differ.** About half of the variation between their
  slopes is real (I² = 46%), and a new ecoregion's slope could plausibly be
  anywhere from slightly negative to +0.2.
- The five individually significant positive slopes are the Sri Lanka dry-zone
  forests (+0.74, the same place the local-slope analysis flagged), Eastern
  Himalayan subalpine conifer forests (+0.29), South Deccan Plateau dry deciduous
  forests (+0.20), Kayah-Karen montane rain forests (+0.16) and Khathiar-Gir dry
  deciduous forests (+0.12). The three significant negative ones are the South
  Western Ghats montane rain forests (-0.63, 9 cells), Terai-Duar savanna and
  grasslands (-0.32, 9 cells) and Northern Indochina subtropical forests (-0.16,
  38 cells). With 35 ecoregions about two would be significant by chance.
- 1° has only seven ecoregions with enough cells; it is too coarse for this.

Fig 18 is the forest plot.

## 5. Spatial scale, and how many independent observations
Ecoregion fixed effects split the association into two pieces along borders
drawn by biogeographers. Moran's eigenvector maps (Dray, Legendre & Peres-Neto
2006) do it with no borders: the cells' geography becomes a set of orthogonal
spatial patterns ordered from continent-wide gradients to cell-to-cell texture.
GPP and richness, net of effort and climate, were projected onto four bands of
those patterns and onto the remainder with no spatial structure, and a slope
fitted in each band (band regression; Engle 1974).

| band | 1°: slope (p) | share of richness / GPP | 0.5°: slope (p) | share of richness / GPP |
|---|---|---|---|---|
| broadest patterns (patches of about 720 / 805 km) | **+0.820 (0.003)** | 35% / 75% | **+0.553 (0.003)** | 32% / 76% |
| broad | +0.160 (0.20) | 7% / 2% | −0.021 (0.81) | 8% / 4% |
| fine | −0.163 (0.35) | 5% / 3% | +0.020 (0.72) | 7% / 1% |
| finest patterns | −0.188 (0.37) | 3% / 3% | +0.148 (0.029) | 5% / 2% |
| no spatial structure | −0.022 (0.58) | 51% / 16% | **+0.092 (0.0002)** | 49% / 18% |

68 patterns at 1° (17 per band), 206 at 0.5° (51–52 per band).

- **The large slope is confined to the broadest band.** Three-quarters of the
  climate-adjusted variation in productivity is in patterns hundreds of
  kilometres across, and that is where richness and productivity move together.
- **Half of the variation in richness has no spatial structure at all**, and
  there the slope is zero at 1° and small but clearly positive at 0.5° (+0.092).
  That local component is the same small effect sections 1, 3 and 4 find.
- The intermediate bands carry little variance and no detectable slope.

**Effective sample size** (Clifford, Richardson & Hémon 1989; Dutilleul 1993):

| | 1° | 0.5° |
|---|---|---|
| cells | 221 | 672 |
| worth this many independent observations (raw / net of climate) | 37 / 36 | 80 / 86 |
| raw correlation, richness–GPP | +0.558, p = 0.0003 | +0.364, p = 0.0009 |
| net of effort and climate | +0.321, **p = 0.055** | +0.256, **p = 0.018** |

The cells carry about a sixth to an eighth of the information their count
suggests. On that count the climate-adjusted association is borderline at 1°
and holds at 0.5°. This is a stricter test than the cluster-robust standard
errors used elsewhere, and it agrees with the Hawkins subsampling result that
the *estimate* is unbiased while its *precision* was overstated.

## Limits common to all five
- One region, one snapshot in time, one-degree and half-degree cells.
- Direction remains unidentified (`RESULTS_DIRECTION.md`); every number here is
  an association.
- Sections 1 and 5 use birds only.
- The band boundaries in section 5 are equal-count quarters of the spatial
  patterns, an arbitrary but pre-stated choice; "patch size" is where a band's
  autocorrelation first reaches zero and is only resolved for the broadest band
  (the others fall below one cell width).

## References
Checked against Crossref 2026-11-16. Abstracts read where available (Clifford
1989, DerSimonian & Laird 1986, Lakens 2017); the others have no abstract in
Europe PMC and are cited as the source of a method only.

- Chernozhukov, Chetverikov, Demirer, Duflo, Hansen, Newey & Robins (2018)
  Double/debiased machine learning for treatment and structural parameters.
  *The Econometrics Journal* 21: C1–C68. doi:10.1111/ectj.12097
- Cook & Stefanski (1994) Simulation-extrapolation estimation in parametric
  measurement error models. *JASA* 89: 1314–1328. doi:10.1080/01621459.1994.10476871
- Lakens (2017) Equivalence tests. *Social Psychological and Personality Science*
  8: 355–362. doi:10.1177/1948550617697177
- DerSimonian & Laird (1986) Meta-analysis in clinical trials. *Controlled
  Clinical Trials* 7: 177–188. doi:10.1016/0197-2456(86)90046-2
- Dray, Legendre & Peres-Neto (2006) Spatial modelling: a comprehensive framework
  for principal coordinate analysis of neighbour matrices (PCNM). *Ecological
  Modelling* 196: 483–493. doi:10.1016/j.ecolmodel.2006.02.015
- Engle (1974) Band spectrum regression. *International Economic Review* 15: 1–11.
  doi:10.2307/2526084
- Clifford, Richardson & Hémon (1989) Assessing the significance of the
  correlation between two spatial processes. *Biometrics* 45: 123–134.
  doi:10.2307/2532039
- Dutilleul (1993) Modifying the t test for assessing the correlation between two
  spatial processes. *Biometrics* 49: 305–314. doi:10.2307/2532625
