# Extension E — are species-rich places more stable? (2026-11-16)

Reproduce: `python scripts/extension_e_stability.py` (cached data only).
Data: annual GPP and climate 2001–2023 in `data/gee_extras.npz`
(`scripts/gee_extras.py`). Figure: `figures/fig15_stability.png`.
Why a fifth extension exists: `docs/DECISIONS.md`, 2026-11-16 (second lock lift).

## The question
Extensions A–D are about the *level* of productivity. The other half of the
biodiversity–ecosystem-function literature is about its *stability*: diverse
systems are expected to vary less from year to year. Tilman, Reich & Knops (2006)
found this in a decade-long grassland experiment, Isbell et al. (2015) found
diverse grassland communities changed less during climate extremes across 46
experiments, and Oehri et al. (2017) reported that landscape-scale productivity
"and its temporal stability" increase with diversity in 447 Swiss 1 km² plots.
Does it show in 23 years of satellite GPP over this region?

## Measures
Per 1° cell, from annual MODIS GPP 2001–2023:
- **instability**: the detrended coefficient of variation (SD of the yearly
  values around a straight-line trend, divided by the mean), logged;
- **trend**: linear change, percent of the cell's mean per year.

220 of 221 modelled cells have a complete series. Median year-to-year variation
is 4.8% (5th–95th percentile 2.9% to 11.4%). GPP rose in 82% of cells (median
+0.22% per year). The 2019–2023 mean of this series matches the project's GPP
table at r = 1.000 (maximum difference 0.002).

## Result: richer cells look steadier, but not once the obvious drivers are in
Raw correlation of corrected bird richness with instability: **r = −0.36**.
Standardised richness coefficients for instability (negative = steadier; SEs
clustered by ecoregion):

| specification | birds (n = 220) | plants (n = 193) |
|---|---|---|
| S1: effort, mean temperature, mean precipitation | −0.171 (p = 0.064) | −0.385 (p = 0.0001) |
| S2: + year-to-year variability of rainfall and temperature | −0.082 (p = 0.32) | −0.294 (p = 0.0003) |
| S3: + mean GPP | **+0.144 (p = 0.039)** | −0.090 (p = 0.23) |
| S3 within ecoregions | **+0.000 (p = 1.00)** | **+0.002 (p = 0.98)** |
| S3, spatial error model | +0.060 (p = 0.11) | −0.050 (p = 0.17) |

- **What drives instability is climate and the mean, not richness.** Instability
  correlates +0.55 with rainfall variability and −0.68 with mean GPP: dry,
  unproductive cells swing most.
- **For birds the apparent stabilising effect is gone by S2** and reverses sign
  once mean GPP is held fixed.
- **For plants it survives climate variability (−0.29) but not mean GPP (−0.09,
  n.s.).**
- **Within ecoregions it is zero for both taxa** (+0.000 and +0.002).

So there is **no evidence here for a diversity–stability effect that is separate
from the level of productivity**. Richer cells are steadier because they are
wetter, less variable in rainfall and more productive.

A caution on S3: if richness raised mean productivity, and mean productivity
lowered variability, then controlling for the mean would remove a real pathway.
S2 is the model that does not make that assumption, and under S2 the plant
result is negative and significant across regions. The within-ecoregion zero
holds under either reading.

## Trend
| specification | birds | plants |
|---|---|---|
| S1 | −0.126 (p = 0.066) | −0.413 (p = 0.0001) |
| S2 | −0.053 (p = 0.46) | −0.330 (p < 0.0001) |
| S3 | +0.160 (p = 0.077) | −0.202 (p = 0.012) |
| S3 within ecoregions | −0.009 (p = 0.88) | −0.019 (p = 0.75) |
| S3, spatial error model | −0.008 (p = 0.81) | −0.125 (p = 0.002) |

Plant-rich cells greened *less* over 2001–2023 across regions; nothing within
ecoregions. The likeliest reading is saturation (already-productive forest has
less room to gain than dry land that is greening), but that was not tested.

## Limits
- GPP here is a modelled satellite product. MOD17 GPP is driven by light,
  temperature and vapour-pressure inputs, so part of its interannual variation
  is the meteorological forcing, not vegetation. That inflates the role of
  climate variability and works against finding a diversity effect.
- Richness is one value per cell from records pooled over 2000–2024; it is not
  measured per year, so this is a cross-section of stabilities, not a time series
  of diversity.
- 1° only. A 1° cell averages over many ecosystems, which itself stabilises GPP
  (a statistical portfolio effect unrelated to species).
- The three papers cited report effects for *plant* diversity in grasslands or
  mixed landscapes at plot scale; birds over 1° cells are a long way from that.

## References (Crossref-checked and abstracts read, 2026-11-16)
- Tilman, Reich & Knops (2006) *Nature* 441: 629–632. doi:10.1038/nature04742
- Isbell et al. (2015) *Nature* 526: 574–577. doi:10.1038/nature15374
- Oehri, Schmid, Schaepman-Strub & Niklaus (2017) *PNAS* 114: 10160–10165.
  doi:10.1073/pnas.1703928114
- Loreau & de Mazancourt (2013) *Ecology Letters* 16: 106–115.
  doi:10.1111/ele.12073 (mechanisms; background only)
