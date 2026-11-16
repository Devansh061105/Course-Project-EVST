# Local slopes — Extension C for every cell (2026-11-16)

Reproduce: `python scripts/local_slopes.py` (about 40 s; writes
`data/local_slopes_1p0.csv`, `data/local_slopes_0p5.csv`,
`data/local_slopes_profile.csv`). Figure: `figures/fig9_local_slopes.png`.

Extension C asks whether the richness–productivity relationship "holds in every
landscape" and answers with three hand-picked boxes. This analysis asks the same
question of every modelled cell. It is part of Extension C, not a new extension.

## Method
Geographically weighted regression (GWR; Brunsdon, Fotheringham & Charlton 1996)
of the corrected model, `gpp ~ rarefied richness + log10(effort) + temperature +
precipitation`, all standardised over the whole sample so a local slope is on the
same scale as the global β. One weighted regression is fitted around each cell,
with an adaptive bisquare kernel over the k nearest modelled cells; k is chosen
by AICc. Implemented directly in numpy (`local_slopes.py`); no GWR package.

GWR is easy to over-read, so four checks are reported with it:

| check | what it guards against |
|---|---|
| AICc against the global OLS | paying for local parameters that add nothing |
| Monte Carlo stationarity test (499 shuffles of cell locations; Brunsdon et al. 1998) | reading noise in the local slopes as geography |
| local t-tests at the da Silva & Fotheringham (2016) adjusted α | hundreds of dependent local tests |
| local condition numbers (Wheeler & Tiefelsdorf 2005) | slope patterns manufactured by local collinearity |

## Results

| | 1° (primary) | 0.5° (replication) |
|---|---|---|
| cells | 221 | 672 |
| chosen window | 32 neighbours, median radius 541 km | 40 neighbours, 319 km |
| AICc, OLS → GWR | 458.3 → 98.0 | 1585.2 → 253.0 |
| global OLS β | +0.273 | +0.226 |
| **median local slope** | **+0.026** | **+0.036** |
| middle half of local slopes | −0.021 to +0.112 | −0.004 to +0.098 |
| full range | −0.354 to +0.467 | −0.266 to +0.573 |
| local slope > 0 | 57.9% of cells | 73.1% |
| adjusted α (critical t) | 0.0039 (2.93) | 0.0015 (3.18) |
| significant positive / negative | 12 / 6 | 39 / 2 |
| Monte Carlo stationarity p | 0.918 | 1.000 |
| local condition number, median / max | 8.1 / 30.6 (1 cell > 30) | 9.1 / 41.4 (7 cells > 30) |
| local-slope variance between ecoregions | 70.7% | 64.7% |

The 0.5° sample here is 672 cells; the ecoregion models in
`RESULTS_ADJUDICATION.md` section 8 use 671 because one cell has no ecoregion label.

### 1. The typical local slope is the within-ecoregion slope
The median local slope is +0.026 at 1° and +0.036 at 0.5°. The ecoregion
fixed-effects estimates were +0.030 and +0.058. Two different methods — one
that removes named ecoregions, one that knows nothing about ecoregions and only
looks at neighbourhoods of a few hundred kilometres — land in the same place:
**locally the slope is about a tenth of the region-wide +0.27.**

### 2. The slope grows with the size of the window (Fig 9c)
At 1°, the median local slope is +0.01 with a ~400 km window, +0.08 at ~800 km,
+0.11 at ~1,100 km, +0.17 at ~1,750 km and +0.26 once the window spans the whole
region (~3,000 km). The 0.5° curve follows the same path. The association is
built up from differences between places hundreds to thousands of kilometres
apart, which is the between-region reading of `RESULTS_ADJUDICATION.md` shown
without any reference to ecoregion boundaries.

### 3. No statistical evidence that the richness slope varies in space
The Monte Carlo test does not reject stationarity at either grain (p = 0.92 and
1.00): the spread of the local richness slopes (SD 0.136 at 1°) is no larger than
the spread obtained when cell locations are shuffled (median SD 0.177). GWR beats
OLS by a wide AICc margin, but that gain comes from the local intercepts and
climate slopes — the same regional structure the ecoregion fixed effects
absorbed — not from a richness slope that differs from place to place.
**The map in Fig 9 is therefore descriptive.** It should not be used to rank
regions by "where biodiversity matters most".

### 4. What does survive the multiple-testing threshold
- **Eastern Himalaya and the hills south and east of it**: a positive cluster at
  both grains (5 of 24 case-study cells at 1°, 14 of 70 at 0.5°). This is the one
  local pattern that replicates.
- **Northern Indochina**: a negative cluster of 6 cells at 1° that does **not**
  replicate at 0.5° (2 scattered negative cells). Treat it as unconfirmed.
- **Sri Lanka dry zone** (0.5° only, median local slope +0.49 over 15 cells): the
  1° grid has too few modelled cells there to test it. One grain only.

### 5. The three case-study regions

| region | 1°: cells, median local slope (range), significant | 0.5°: cells, median, significant |
|---|---|---|
| Western Ghats | 7, +0.147 (+0.061 to +0.321), 0 | 27, +0.058, 0 |
| Thar Desert | 8, +0.078 (+0.012 to +0.117), 0 | 18, +0.027, 0 |
| Eastern Himalaya | 24, +0.172 (+0.014 to +0.369), 5 | 70, +0.083, 14 |

All three regions have positive median local slopes at both grains, with the
Thar the weakest and the Eastern Himalaya the strongest. Only the Eastern
Himalaya has individually significant cells. The plan (Section 4) expected the
relationship to hold "strongly in the Western Ghats but weakly on the Deccan";
what the data show is the same ordering between a wet and a dry region, but with
too few Western Ghats cells (7) to call its slope distinguishable from zero.

## Limits
- GWR is an exploratory method. Each local fit uses 32 (or 40) cells for five
  parameters, and neighbouring fits share most of their data, so local slopes are
  smooth by construction.
- Local collinearity is low here (condition number above 30 in 1 of 221 cells at
  1°, 7 of 672 at 0.5°), so the Wheeler & Tiefelsdorf artefact is not driving the map.
- As everywhere in this project, a slope is an association. A positive local
  slope does not say bird richness raises productivity there.

## References (existence and details checked against Crossref, 2026-11-16)
- Brunsdon, Fotheringham & Charlton (1996) Geographical Analysis 28: 281–298. doi:10.1111/j.1538-4632.1996.tb00936.x
- Brunsdon, Fotheringham & Charlton (1998) The Statistician 47: 431–443. doi:10.1111/1467-9884.00145
- da Silva & Fotheringham (2016) Geographical Analysis 48: 233–247. doi:10.1111/gean.12084
- Wheeler & Tiefelsdorf (2005) Journal of Geographical Systems 7: 161–187. doi:10.1007/s10109-005-0155-6
