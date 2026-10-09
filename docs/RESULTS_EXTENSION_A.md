# Extension A results — naive vs corrected (2026-10-05)

> **Updated 2026-10-06:** the spatial and biogeographic follow-up is in `RESULTS_ADJUDICATION.md`; read that for the current interpretation. The naive-vs-corrected numbers below still stand.

Reproduce: `python scripts/merge_and_extA.py`. Inputs `data/gbif_cells.csv`
(884 cells, birds, 2000–2024) and `data/gee_cells.csv` (884 cells, 2019–2023
means). Model rows: `data/model_cells.csv`.

## Sample construction

| stage | cells |
|---|---|
| grid | 884 |
| with WorldCover coverage (i.e. land) | 630 |
| after dropping cropland-dominant (40) | −217 |
| after dropping water-dominant (80) | −146 |
| with GPP, ≥250 species-identified records (rarefiable at n=250), climate present | **221** |

## Headline

H1 is **supported in direction but modest in size**. Effort-corrected richness
stays positively and significantly associated with GPP after climate controls.

Standardised betas, all on the **same 221 cells** (the raw coefficients in the
script output are not comparable: raw species count and expected-species-at-250
are different units, and the naive model otherwise runs on 582 cells):

| specification | richness β | R² |
|---|---|---|
| raw richness alone (naive spec) | +0.445 | 0.198 |
| rarefied richness alone | +0.558 | 0.311 |
| **corrected: rarefied + effort + temp + precip** | **+0.273** | **0.558** |

Full corrected model: temp β=+0.494 (p=7e-30), precip β=+0.341 (p=2e-08),
rarefied richness β=+0.273 (p=1.6e-08), log10(effort) β=−0.069 (p=0.14, n.s.).
VIF all ≤1.47, so the richness coefficient is not collinearity-inflated.

## What the correction actually did

The gap the plan expected is **not** a sign flip. It is an attenuation plus a
decoupling:

1. **Richness–effort correlation collapses.** Raw richness correlates r=0.809
   with log effort; rarefied richness correlates r=0.241. Rarefaction does the
   job it was chosen for — raw counts were substantially a map of observer
   effort.
2. **The richness effect halves once climate enters**, 0.558 → 0.273. Most of
   what looked like a biodiversity–productivity signal is climate acting on both.
3. **Richness explains little unique variance.** R² is 0.507 with climate and
   effort alone, 0.558 adding richness: richness contributes **5.1 percentage
   points**. Temperature is by far the strongest single predictor.

This is a defensible, reportable result and it aligns with Grace et al. (2016)
from the literature review — productivity and richness are jointly driven by
shared environmental causes rather than linked by one direct path.

## Two findings that change the project

### 1. Spatial autocorrelation is severe — p-values above are optimistic
Moran's I on corrected-model residuals (distance-band weights, 1.5° threshold,
999 permutations): **I = 0.7233, E[I] = −0.0045, z = 15.73, p = 0.001.**

This is not a mild violation. Neighbouring cells are strongly non-independent,
so the reported standard errors are too small and the significance is overstated.
The coefficient estimates remain usable; the inference does not. Before any
p-value from this model is quoted in the report it needs cluster-robust SEs by
biogeographic sub-region, or a spatial lag/error model. This is exactly the
failure Ploton et al. (2020) describes, and it is cited in the literature review.

### 2. The Deccan Plateau case study is unusable as designed
All 25 Deccan land cells are cropland-dominant; mean cropland+built-up fraction
0.77, mean natural fraction 0.22. Only **1 of 25** cells falls below 50%
converted. The region does not survive the natural-land-cover restriction at 1°
resolution.

This is not a pipeline bug — it is a real land-use fact, and it is itself a
finding: the dry savanna/grassland contrast the plan wanted has been almost
entirely converted to agriculture. Options, in order of preference:

- **Report it as a result** and replace the Deccan with a dry contrast region
  that retains natural cover (candidates: Kachchh/Thar margin, or the Eastern
  Ghats remnant belt). Keeps Extension C intact and gains a genuine finding.
- Relax the mask to `excluded_frac < 0.7` for the Deccan only — recovers 9 cells
  but compares partly-agricultural land against natural land, which is the exact
  confound the mask exists to prevent. Not recommended.
- Drop to two case studies. Weakest option; loses the plan's contrast design.

## Caveats carried forward
- 2019–2023 environmental means vs 2000–2024 occurrence records; the time
  windows do not match. Defensible for a climatological mean, worth stating.
- A 1° cell holds ~54,000 MODIS GPP pixels (463 m) and ~94 ERA5-Land pixels
  (11 km). **Corrected 2026-10-06:** an earlier version said ~1 ERA5-Land pixel,
  repeating the plan's Step 4; checked against Earth Engine's nominal pixel sizes.
  At 1° both products are heavily averaged, so the mismatch matters little here.
- Rarefaction at n=250 drops cells below that threshold. n=50 and n=100 columns
  exist in `gbif_cells.csv` for the sensitivity check.
- Birds only. Better recorded than any other group, so this likely understates
  the sampling-bias problem rather than overstating it.
