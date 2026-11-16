# Where should the next bird surveys go? (2026-11-16)

Reproduce: `python scripts/survey_gaps.py` (cached data only).
Figure: `figures/fig16_survey_gaps.png`. Table: `data/survey_gaps_1p0.csv`.

Written for the plan's closing section on citizen-science data reliability. It
is a **ranking aid**, not a finding about biodiversity.

## What it computes
For each of the 267 natural-cover land cells:

- **completeness** — sample coverage of the cell's bird records (Chao & Jost
  2012): the estimated share of the cell's birds, by individuals, that belong to
  species already recorded. Zero for a cell with no records.
- **expected richness** — effort-corrected richness predicted from environment
  alone (temperature, precipitation, elevation, topographic heterogeneity, NDVI),
  from a model fitted to the 221 modelled cells.
- **priority** — expected richness × (1 − completeness), rescaled to 0–100.

## How far to trust the prediction
The environment-only model explains 52% of the variance in corrected richness
in-sample and **46% when whole 4° blocks are held out** (RMSE 14.1 species). That
is good enough to rank cells, not to predict a cell's richness. Ten of the 267
cells (six of the top 30) lie outside the climate or terrain range the model was
fitted on, mostly on the Tibetan Plateau; they are flagged `extrapolated` in the
table.

## Results
| | cells | median completeness | below 0.90 | no records at all |
|---|---|---|---|---|
| modelled cells | 221 | 0.997 | 11 | 0 |
| natural-cover cells not modelled | 46 | 0.563 | 37 | 4 |

- **46 natural-cover cells are left out of every model** because they have fewer
  than 250 identified bird records. Their expected richness (median 99.6) is
  lower than in the modelled cells (117.8), so the analysis is somewhat tilted
  towards richer landscapes.
- **The gaps are concentrated in three places** (Fig 16b): the Baluchistan xeric
  woodlands of western Pakistan, the hill forests of eastern and northern
  Myanmar, and the Tibetan margin in China. Of the 30 highest-priority cells, 18
  are in China, 6 in Myanmar and 5 in Pakistan.
- **India, Nepal, Thailand and Sri Lanka are essentially complete at this grain**
  (median completeness 1.00; mean priority below 1).

| country | natural-cover cells | mean priority | median completeness | median records |
|---|---|---|---|---|
| Pakistan | 11 | 39.4 | 0.85 | 80 |
| China | 77 | 13.9 | 0.95 | 626 |
| Myanmar | 47 | 12.3 | 0.98 | 2,080 |
| Nepal | 11 | 0.6 | 1.00 | 34,445 |
| India | 79 | 0.4 | 1.00 | 63,420 |
| Thailand | 22 | 0.1 | 1.00 | 65,518 |
| Sri Lanka | 5 | 0.0 | 1.00 | 216,144 |

## Read with care
- **A gap in GBIF is not always a gap in knowledge.** Almost all bird records
  here come from one dataset, eBird (70.9 of 71.7 million records in
  `data/gbif_derived_dataset/dataset_counts.csv`). Where eBird is little used,
  as appears to be the case for the Chinese cells, birdwatching records may sit
  on platforms GBIF does not hold. Treat the Tibetan cells as gaps in this
  dataset first, and gaps in ornithology only possibly. (The reason for low
  eBird use there was not checked.)
- **Coverage near 1 does not mean every species is known.** It is weighted by
  individuals, so a cell can be 99.7% complete and still be missing rare species.
- **Coverage from a handful of records is unstable.** A cell with 18 records, all
  different species, scores 0.01; it would move a lot with ten more records.
- **One-degree cells hide local gaps.** A cell that is complete overall can still
  have unvisited forest inside it.

## What the closing section can say from this
Citizen-science bird data are close to complete at 1° across India, Nepal,
Thailand and Sri Lanka, and thin in western Pakistan, upland Myanmar and the
Tibetan margin. Effort correction handles uneven effort where there are records;
it cannot conjure data where there are none, and 46 natural cells drop out of
the analysis for that reason.
