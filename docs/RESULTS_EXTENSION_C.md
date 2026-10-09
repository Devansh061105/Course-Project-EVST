# Extension C — three case-study landscapes (2026-10-06)

Reproduce: `python scripts/extension_c.py`. Deccan Plateau replaced by Thar /
western Rajasthan (see `docs/DECISIONS.md`).

## Profiles

| | Western Ghats | Thar Desert | Eastern Himalaya |
|---|---|---|---|
| box | 8–16°N, 74–77°E | 25–30°N, 69–74°E | 26–29°N, 88–97°E |
| land cells / eligible | 20 / **7** | 25 / **8** | 27 / **24** |
| dominant cover | water 35%, tree 35%, cropland 30% | cropland 52%, bare 44% | **tree 74%**, grassland 15% |
| natural fraction | 0.44 | 0.57 | **0.84** |
| climate | 24.3 °C, 2499 mm | 27.0 °C, **241 mm** | **12.0 °C**, 3013 mm |
| GPP (kgC/m²/yr) | **2.15** | **0.21** | 1.48 |
| NDVI | 0.62 | 0.15 | 0.51 |
| median records/cell | **1,098,270** | 7,911 | 76,542 |
| raw observed richness | 456 | 209 | 450 |
| rarefied richness @250 | 113.8 | 98.0 | **126.3** |
| corrected-model residual | +0.256 (under-predicts) | −1.063 (over-predicts) | −0.297 (over-predicts) |

## The headline: the ranking flips

| region | median records | raw S | rank | rarefied S | rank | GPP | rank |
|---|---|---|---|---|---|---|---|
| Western Ghats | 1,098,270 | 456 | **1** | 113.8 | **2** | 2.15 | 1 |
| Thar Desert | 7,911 | 209 | 3 | 98.0 | 3 | 0.21 | 3 |
| Eastern Himalaya | 76,542 | 450 | **2** | 126.3 | **1** | 1.48 | 2 |

The Western Ghats looks like the most species-rich of the three on raw counts.
After effort correction the Eastern Himalaya is. The Ghats carry **14× more
records per cell**, and that alone was doing the work.

This is precisely what the plan predicted for this region: "high biodiversity,
historically under-sampled in citizen-science databases. This is the case where
the naive-vs-corrected gap from Extension A should be largest." It is.

## The spreads are the argument

| quantity | spread across the three regions |
|---|---|
| survey effort | **139×** |
| raw richness | 2.18× |
| **rarefied richness** | **1.29×** |
| GPP | **10.03×** |

Effort varies 139-fold. Raw richness varies 2.2-fold — part of which is real and
part of which is just that variation in effort. Corrected richness varies only
1.3-fold. Meanwhile productivity varies 10-fold.

That is the clearest statement of why the regression is weak: across these three
landscapes, **productivity varies by an order of magnitude while effort-corrected
diversity is nearly flat.** Climate moves productivity; corrected diversity
barely moves at all.

## Where each region complicates the story

**Western Ghats.** Only 7 of 20 land cells survive the mask — a 1° box on the
west coast is 35% sea and 30% cropland. The model *under*-predicts GPP here
(+0.256), i.e. the Ghats are more productive than richness and climate alone
imply. Plausibly the structural effects the literature emphasises: Kothandaraman
et al. (2020) attribute 77.2% of carbon-stock variance to stand structure against
only 6.7% to diversity, and Najeeb et al. (2025) point to large trees
specifically. Neither is visible to a 1° grid cell.

**Thar Desert** (box 25–30°N, 69–74°E: 14 land cells in India, 11 in
Pakistan; modelled 6 India, 2 Pakistan). The model *over*-predicts badly (−1.063 — the largest
residual of the three). Even with 241 mm of rain, the fitted climate response
expects more productivity than the desert delivers; the linear precipitation term
is a poor description at the arid extreme. Also note the mask is doing less work
here than it appears: 52% of cells are cropland-dominant, leaving only 8 eligible.
Those cropland cells are in Rajasthan (Barmer–Nagaur, the Ganganagar side) and
in Pakistan's Indus plains (Sindh, Bahawalpur). **Corrected 2026-10-06:** an earlier
version attributed them to the "irrigated Punjab/Haryana margin", which lies
mostly east of the box.

**Eastern Himalaya** (24 modelled cells: 14 India, 5 China/Tibet, 3 Bhutan, 2
Myanmar — the box reaches 29°N, so it is not only foothills). The cleanest region by far — 24 of 27 cells
eligible, 84% natural cover, the least contaminated by agriculture. It is also
the coldest (12.0 °C) and wettest (3013 mm), and the model over-predicts slightly
(−0.297), consistent with temperature limiting productivity at altitude despite
abundant rain.

## On the comparison the plan asked for
The plan asks whether the Western Ghats result "matches the published Western
Ghats carbon-storage literature." It cannot be compared directly, and this is
worth stating rather than glossing:

Kothandaraman et al. (2020) report **336.8 Mg C/ha**, an ecosystem carbon
**stock**. We measure MODIS GPP, **2.15 kgC/m²/yr = 21.5 Mg C/ha/yr**, an annual
**flux**. A stock and a flux are different quantities — exactly the conflation
flagged in the literature review's "what is actually being measured" section. A
forest can hold a large stock while fixing carbon slowly, or vice versa.

What *is* comparable is the qualitative claim, and it agrees: both find the
Western Ghats at the productive/carbon-rich end, and both find diversity a
secondary driver behind structure and environment.

## Caveats
- Case studies are small after masking (7, 8, 24 cells). Narratives are
  qualitative; no separate per-region regressions were fitted, and none should be.
- Residual means are descriptive, not tests.
- The Western Ghats box is coarse for a mountain range ~100 km wide; at 1°
  resolution each cell mixes escarpment, coast and plain. The 0.5° run
  (in progress) will show whether this materially changes the profile.
