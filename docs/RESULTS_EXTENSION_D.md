# Extension D — is the result specific to birds? Vascular plants (2026-11-16)

Reproduce: `python scripts/extension_d_plants.py` (reads the cached pull; no
network). Data: `scripts/gbif_pull_taxon2.py` → `data/gbif_cache_plants.json`,
`data/gbif_cells_plants.csv`. Figure: `figures/fig10_second_taxon.png`.
Why plants, and why the scope lock was lifted: `docs/DECISIONS.md`, 2026-11-16.

## What was done
The bird model chain was repeated with vascular plants (Tracheophyta) on the same
grid, mask, climate controls and years (2000–2024), and the bird models were
refitted on the cells that have both taxa so the comparison is like for like.

| | plants | birds |
|---|---|---|
| GBIF records in the 884 cells | 1,364,346 (1,316,540 identified to species) | 71.7 million |
| contributing datasets | 435 | 110 |
| median records per natural-cover cell | 424 | 8,175 |
| facet-truncated cells (limit 5,000) | 0 | 0 |
| cells in the model | 193 (rarefied at 100) | 221 (rarefied at 250) |
| cells with both taxa | 180 | 180 |

## The answer
**The pattern is not specific to birds.** Effort-corrected plant richness is
positively associated with productivity across the region, with almost the same
coefficient as the birds, and — like the birds — the association disappears
inside ecoregions.

Standardised richness coefficients (Fig 10a):

| specification | plants, GPP | birds (same cells), GPP | plants, NPP | birds, NPP |
|---|---|---|---|---|
| rarefied richness alone | +0.218 | +0.504 | +0.301 | +0.552 |
| **corrected: + effort, temperature, precipitation** | **+0.264** (p < 0.0001) | **+0.277** (p < 0.0001) | +0.327 | +0.407 |
| same, SEs clustered by ecoregion | +0.264 (p = 0.0002) | +0.277 (p = 0.0001) | +0.327 (p = 0.0008) | +0.407 (p < 0.0001) |
| + ecoregion fixed effects (within) | −0.027 (p = 0.49) | +0.033 (p = 0.66) | +0.006 (p = 0.89) | +0.110 (p = 0.20) |
| spatial error model | −0.008 (p = 0.77) | +0.057 (p = 0.09) | +0.038 (p = 0.28) | +0.142 (p = 0.001) |
| R² gained by adding richness to climate + effort | +6.8 points | +5.5 points | +10.5 points | +11.8 points |

Plants: n = 193. Birds: n = 180.

### 1. Same size across regions
Corrected plant richness has β = +0.264 for GPP against +0.277 for birds on the
shared cells, and both are stronger for NPP. The plant coefficient is stable to
the rarefaction level: +0.241 at 50 records (208 cells), +0.264 at 100 (193),
+0.309 at 250 (155).

### 2. Same collapse within ecoregions
With ecoregion fixed effects the plant coefficient is −0.027 (p = 0.49) for GPP
and +0.006 for NPP; under the spatial error model it is −0.008 (p = 0.77). This
is the bird result (`RESULTS_ADJUDICATION.md`) reproduced with a different group
of organisms recorded by a different community of observers. It strengthens the
reading that the association is a contrast **between** regions.

### 3. The two taxa carry partly independent signals between regions
With both in one model, bird richness keeps β = +0.190 (p = 0.001) and plant
richness +0.209 (p < 0.0001); R² rises from 0.601 (birds only) to 0.648. With
ecoregion fixed effects both are indistinguishable from zero (+0.047, p = 0.59;
−0.051, p = 0.36).

### 4. Birds and plants agree only weakly on where diversity is high (Fig 10b)
| comparison | r |
|---|---|
| raw species counts | +0.431 |
| effort-corrected richness | +0.299 (Spearman +0.306, p < 0.0001) |
| corrected richness, climate removed | +0.335 |
| survey effort, birds vs plants (log records) | +0.544 |

Part of the raw correlation is shared effort: places with many bird records also
have many plant records. After correction the agreement is weak, in line with
Wolters, Bengtsson & Zaitsev (2006), whose review of 237 cross-taxon richness
correlations found an average effect of 0.374, "positive but weak". One taxon is
a poor stand-in for another in this region.

## How far the plant measure can be trusted (read before citing the numbers)
| | plants @50 | plants @100 | plants @250 | birds @250 |
|---|---|---|---|---|
| cells | 208 | 193 | 155 | 221 |
| median expected species | 44.0 | 80.6 | 169.8 | 118.3 |
| distinct species per record | 0.88 | 0.81 | 0.68 | 0.47 |
| median sample coverage | 0.22 | 0.34 | 0.50 | 0.76 |
| correlation with log effort | −0.02 | −0.05 | −0.10 | +0.24 |

- **Rarefaction removes the effort signal.** Raw plant richness correlates
  r = +0.83 with log effort (birds: +0.81); rarefied plant richness does not
  (−0.05). In that sense the Extension A correction works for plants too.
- **But the samples are far from complete (Fig 10c).** In a draw of 100 plant
  records, 81 are different species, and the draw covers only about a third of
  the records' species pool (coverage 0.34, against 0.76 for birds at 250). At
  this coverage rarefied richness mostly measures how evenly records are spread
  over species, not how many species a cell holds.
- **The Western Ghats show the problem.** Its 7 modelled cells have a median of
  26,527 plant records and 1,061 recorded species, yet only 51.0 expected species
  per 100 records — below the Eastern Himalaya (79.5 from 633 records) — because
  a few commonly photographed species dominate the record pool. For birds the
  same two regions are close (117.6 and 137.6).
- **Different bias, not no bias.** Plant occurrence data are known to be gappy
  and biased along taxonomic, spatial and temporal dimensions (Meyer, Weigelt &
  Kreft 2016), and herbarium collecting concentrates near roads and herbaria and
  on a few prolific collectors (Daru et al. 2018). That the plant result matches
  the bird result despite a different bias structure is the point of the
  comparison; it does not make the plant measure a clean richness estimate.
- **Case studies are thin.** Only 2 Thar cells and 7 Western Ghats cells have 100
  identified plant records; no plant case-study ranking is reported.

## What this does and does not change
- **H1 (association):** supported for a second taxon, at the same strength, with
  the same between-region character.
- **Direction:** for plants, diversity driving productivity is at least a
  proposed mechanism (complementarity), unlike for birds. But this design cannot
  separate it from the reverse: water and energy availability are the core
  predictors of vascular plant richness worldwide (Kreft & Jetz 2007), and they
  drive GPP too. The within-ecoregion null applies to plants as it does to birds.
- **Limitations paragraph:** "birds only" becomes "birds, checked against
  vascular plants at 1°".

## Not done
- Plants at 0.5° or 2° (1° only).
- Block cross-validation, the Hawkins test and the quadratic test for plants.
- A GBIF derived-dataset DOI for the plant records. The bird DOI does not cover
  them. Contributing-dataset counts are ready:
  `data/gbif_derived_dataset/dataset_counts_plants.csv` (435 datasets,
  1,362,316 records, queried 2026-11-16 by `scripts/gbif_dataset_counts.py`; the
  per-cell pull summed to 1,364,346, the difference being records on shared cell
  edges).

## References (Crossref-checked and abstracts read, 2026-11-16)
- Meyer, Weigelt & Kreft (2016) Ecology Letters 19: 992–1006. doi:10.1111/ele.12624
- Daru, Park, Primack, Willis et al. (2018) New Phytologist 217: 939–955. doi:10.1111/nph.14855
- Kreft & Jetz (2007) PNAS 104: 5925–5930. doi:10.1073/pnas.0608361104
- Wolters, Bengtsson & Zaitsev (2006) Ecology 87: 1886–1895. doi:10.1890/0012-9658(2006)87[1886:RATSRO]2.0.CO;2
