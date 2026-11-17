# Extension F — protected land, survey effort and the richness–productivity link (2026-11-16)

Reproduce: `python scripts/extension_f_protected.py` (cached data only).
Data: WDPA protected-area grids in `data/gee_extras.npz` (`scripts/gee_extras.py`).
No figure. Why a sixth extension exists: `docs/DECISIONS.md`, 2026-11-16.

> **This extension is data-limited and its results are inconclusive.** The
> public protected-area database does not describe India or China well enough,
> and those two countries hold 58% of the modelled cells. Read section 1 before
> anything else. The one thing that holds everywhere is a null: there is no
> evidence that the richness–productivity slope differs with protection.

## 1. The data problem (the main finding of this extension)
Protected share of land by country, from the World Database on Protected Areas
(WDPA) as served by Earth Engine, 1° land cells:

| country | cells | strict (IUCN Ia–IV) | all designated sites |
|---|---|---|---|
| India | 257 | **0.2%** | 18.4% |
| China | 77 | 1.3% | 4.1% |
| Myanmar | 60 | 7.6% | 8.7% |
| Thailand | 29 | 18.4% | 19.6% |
| Pakistan | 25 | 6.7% | 15.3% |
| Bangladesh | 13 | 1.0% | 4.3% |
| Nepal | 13 | 6.4% | 22.2% |

- **India, strict: 0.2%.** India's protected areas cover about 5.3% of the
  country: 173,629.52 km² (5.28%) as of January 2023, of which 106 national parks
  cover 44,402.95 km² (1.35%) and 567 wildlife sanctuaries 122,564.86 km² (3.73%).
  **Source status (checked 2026-11-17):** these figures are quoted from the
  Wikipedia article "Protected areas of India", which attributes them to the
  Wildlife Institute of India's National Wildlife Database (4 January 2023). The
  Institute's own lists are PDFs linked from https://wii.gov.in/envis and were
  **not opened**, so cite the Institute only after reading them. In the WDPA the
  national parks and sanctuaries total about 20,800 km² of reported area (536
  polygons), roughly an eighth of the 167,000 km² above. The parks are largely
  absent from the public polygons.
- **India, all sites: 18.4%.** This is not parks either. About 180,000 of India's
  190,000 polygons are "Reserve Forest" or "Protected Forest": categories under
  forest law, not wildlife reserves.
- **China: 4.1% (strict 1.3%).** This also reads as incomplete; it was not
  checked against official Chinese figures.

So neither definition measures protection in India, and the "all sites"
definition measures something different in India from everywhere else. Every
model below is therefore also run without India and China (93 cells at 1°, 289
at 0.5°), and that subset is the one to read.

## 2. Results
Standardised coefficients; SEs clustered by ecoregion; strict protection unless
stated.

### F1. Do birdwatchers concentrate on protected land?
| sample | effort ~ protection + climate |
|---|---|
| 1°, all cells (n = 220) | +0.010 (p = 0.90) |
| 0.5°, all cells (n = 671) | +0.017 (p = 0.75) |
| **1°, without India and China (n = 93)** | **+0.232 (p = 0.062)** |
| **0.5°, without India and China (n = 289)** | **+0.124 (p = 0.085)** |
| 0.5°, without India and China, all designated sites | +0.187 (p = 0.009) |

Where the protection data are usable, cells with more protected land have more
bird records. The effect is positive at both grains but only marginally
significant under the strict definition. **Suggestive, not established.**

### F2. Are more-protected cells richer than their climate predicts?
| sample | raw richness | corrected richness |
|---|---|---|
| 0.5°, without India and China | +0.150 (p = 0.015) | +0.096 (p = 0.15) |
| 1°, without India and China | +0.153 (p = 0.098) | −0.003 (p = 0.98) |

Raw richness rises with protection; effort-corrected richness does not, or not
clearly. Together with F1 this is the pattern expected if **part of the apparent
richness of protected landscapes is extra survey effort** — the Extension A point
again, on a policy-relevant variable. It is a pattern in two small samples, not
a demonstrated effect.

### F3. Does the richness–productivity slope depend on protection?
| sample | richness × protection interaction |
|---|---|
| 1°, all cells | −0.007 (p = 0.92) |
| 0.5°, all cells | −0.023 (p = 0.42) |
| 1°, without India and China | +0.095 (p = 0.23) |
| 0.5°, without India and China | +0.064 (p = 0.24) |

**No.** The interaction is not distinguishable from zero in any sample, grain or
definition. In the usable subset at 0.5° the slope is +0.171 in cells with more
than 5% strict protection and +0.195 in cells with none.

(In the full sample the slope looks much weaker in protected cells, +0.018
against +0.395 at 1°. That contrast is an artefact of section 1: "protected"
there mostly separates Southeast Asia from India and China, not protected from
unprotected land.)

## What the closing section can and cannot say
- **Can say:** protected-area data for this region are not good enough to test
  conservation claims at grid scale; India's parks are missing from the public
  database. This is a concrete, checkable data-reliability point.
- **Can say, with "suggests":** where the data are usable, protected landscapes
  attract more bird records, and their richness advantage shrinks once effort is
  corrected.
- **Cannot say:** anything about whether protection raises richness or
  productivity, or about where conservation money should go. A cell's protected
  share is a coarse measure, protection is not randomly placed (parks sit on
  remote, rugged, forested land), and the usable sample is 93 cells.

## Limits
- Protected share per 1° or 0.5° cell, not per record: we cannot say whether the
  records themselves were made inside parks.
- Only polygons are used; sites stored as points are omitted.
- WDPA is the November 2026 release (current at extraction, 2026-11-16), while
  bird records span 2000–2024; some sites were designated during that period.

## Sources
- UNEP-WCMC and IUCN (2026), Protected Planet: The World Database on Protected
  Areas (WDPA), November 2026 release. Earth Engine asset
  `WCMC/WDPA/current/polygons`, accessed 2026-11-16. The release month is read
  from the asset's metadata (period 2026-11-01 to 2026-12-01, updated 2026-11-06),
  checked 2026-11-17.
- Boakes et al. (2010) Distorted views of biodiversity: spatial and temporal bias
  in species occurrence data. *PLoS Biology* 8: e1000385.
  doi:10.1371/journal.pbio.1000385 (Crossref-checked; summary read: 170,000 bird
  sightings over two centuries, changing data-gathering trends "may confound a
  true picture of biodiversity change". Background for effort bias only.)
