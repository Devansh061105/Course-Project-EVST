# TODO — priority order (updated 2026-11-16)

Plan reference: `C:\downloads\Project9_Comprehensive_Plan.docx`, Section 6 (Steps 1–10).
Timeline: 8 weeks; midpoint passed. Literature review submitted.
Current interpretation lives in `docs/RESULTS_ADJUDICATION.md`.

## TEAM ACTIONS (need an account or a team decision)

1. ~~Finish the 0.5° robustness grid.~~ **Done 2026-10-06** in bounded
   chunks (`MAX_PULLS`). Results: `RESULTS_ADJUDICATION.md` section 8. Remaining gap:
   0.5° has GPP only (no NPP, no time-window refit).
2. ~~Register a GBIF derived dataset.~~ **Done 2026-10-11:** https://doi.org/10.15468/dd.jf64nx (GBIF derived
   dataset, 110 datasets, 71,716,026 records); data deposit on Zenodo https://doi.org/10.5281/zenodo.23264805.
   Cite both in the report. See `docs/LITERATURE_NOTES.md`, data products.
3. **Decide the report framing** (see "Open question" below).
4. **Cite the plant records.** The GBIF derived-dataset DOI covers birds only. Before
   Extension D appears in a report, register a second derived dataset for the plant
   records (needs a GBIF account; contributing-dataset counts are in
   `data/gbif_derived_dataset/dataset_counts_plants.csv`) and decide whether to add
   the plant tables to a new version of the Zenodo deposit.

## OPEN QUESTION FOR THE TEAM
The plan's H1 is causal in direction: biodiversity → productivity. The data show a
cross-regional association that shrinks ~75-90% within ecoregions (small positive remainder at 0.5°), and the species–energy
literature treats productivity as the driver of bird richness, not the reverse.
Options for the report:
- (a) keep H1 as written and report the much-weaker-within-regions result against it;
- (b) reframe H1 as an association test and discuss direction explicitly;
- (c) add the species–energy framing as the leading alternative explanation.
These are not exclusive. Recommendation: (b) + (c).

## DONE
- Steps 1–5: grid, taxon (birds), GBIF pull, Earth Engine extraction, merge,
  sanity check. Decisions in `DECISIONS.md`.
- Step 6 / Extension A, Step 7 / Extension B, Step 9 / Extension C.
- Step 8: Moran's I, VIF, cluster-robust SEs **by ecoregion** (as the plan
  specifies), 2° grid, weights sensitivity.
- Beyond the plan, for robustness: Spatial Durbin family, spatial block CV,
  Hawkins subsampling test, response (GPP/NPP/NDVI/EVI), mask, rarefaction level,
  coverage-based standardisation, confounders (topography, seasonality),
  ecoregion fixed effects, GBIF time-window match.
- Figures 1–8 with CSV table views (`figures/`); clean dataset + codebook (`data/final/`);
  plan-deliverables map (`docs/DELIVERABLES_MAP.md`).
- Literature for the interpretation verified with abstracts (`LITERATURE_NOTES.md`).
- **2026-11-16:** local slopes for every cell (GWR, `RESULTS_LOCAL_SLOPES.md`, Fig 9);
  Extension D, vascular plants as a second taxon (`RESULTS_EXTENSION_D.md`, Fig 10);
  interactive maps (`docs/interactive_map.html` flat, `docs/interactive_map_3d.html`
  3D terrain). 35/35 reproducibility checks pass.

## NEXT
5. ~~NPP at 0.5°~~ Done (section 9 of RESULTS_ADJUDICATION). Still not done at 0.5°: coverage-based richness and the 2019-23 time-window refit.
6. **Draft the mid submission / report** when the team asks. Confirm format, brief and
   length first.
7. Optional: confirm Chao & Jost (2012) eq. 4a against the paper before citing
   the equation itself (formula implemented from memory; boundary checks pass).

## DO NOT DO
- Do not add a fifth extension. The plan scope-locked at three; the user lifted the
  lock once, on 2026-11-16, for Extension D (plants). Everything else is robustness
  for the existing four, not new questions.
- Do not re-pull cached GBIF cells; do not delete `data/*_cache*.json`.
- Do not launch long jobs with `nohup` where the parent process can be killed: the
  job survives the kill, and a restart then runs two copies against the same
  cache (happened 2026-10-06).
- Do not add references to the literature review beyond its 20.
