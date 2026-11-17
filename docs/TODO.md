# TODO — priority order (updated 2026-11-17)

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
   The inference batch sharpens this: the report should lead with the small, robust
   association (about 0.05-0.07 SD) and present +0.27 as what linear climate controls
   give, not as the effect size. See `PAPER_CLAIMS.md`.
4. **Cite the plant records.** The GBIF derived-dataset DOI covers birds only. Before
   Extension D appears in a report, register a second derived dataset for the plant
   records (needs a GBIF account; contributing-dataset counts are in
   `data/gbif_derived_dataset/dataset_counts_plants.csv`) and decide whether to add
   the plant tables to a new version of the Zenodo deposit.
   The butterfly and moth records need the same (run
   `python scripts/gbif_dataset_counts.py lepidoptera` for the counts file).
4a. **Before citing Extension F:** ~~record the WDPA version month~~ done 2026-11-17
   (November 2026 release, from the Earth Engine asset metadata). ~~India's
   protected-area share~~ **confirmed 2026-11-17** from the Wildlife Institute of
   India's own table: 5.69% (1,134 areas, 187,162.91 km², as on February 2025). The
   5.28% quoted earlier from Wikipedia is out of date. Extension F can now be cited.

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
- **2026-11-16 (later):** thinning experiment (A), flexible-curve test (B), plants at
  0.5° and butterflies (D), stability (E), protected land (F, data-limited), path
  analysis, 960-model specification curve, survey-gap ranking; Figures 11-17;
  species names, a guided tour and overlays in the maps; unit tests and CI; maps
  hosted on GitHub Pages. 57/57 reproducibility checks pass.
- **2026-11-16 (inference batch):** flexible-control estimate, measurement-error
  correction, equivalence bounds, slopes by ecoregion with meta-analysis, spatial
  scale decomposition and effective sample size (`RESULTS_INFERENCE.md`, Figures
  18-21); claims-to-evidence table (`PAPER_CLAIMS.md`). 68/68 checks, 21 tests.
- **2026-11-17:** coverage-based richness and the 2019-23 time-window refit at 0.5°
  (`grain_0p5_sensitivity.py`, `RESULTS_ADJUDICATION.md` section 10); WDPA release,
  ETOPO1 citation and the Chao & Jost equation numbers checked. 73 checks, 23 tests.

## NEXT
5. ~~NPP at 0.5°~~ Done (section 9 of RESULTS_ADJUDICATION). ~~Coverage-based richness and the 2019-23 time-window refit at 0.5°~~ **Done 2026-11-17** (section 10): the within-ecoregion effect holds under both (+0.071 / +0.075 and +0.062).
6. **Draft the mid submission / report** when the team asks. Confirm format, brief and
   length first.
7. ~~Confirm the Chao & Jost (2012) equation.~~ **Done 2026-11-17.** Full-sample
   coverage is eq. 4a and rarefied-sample coverage is eq. 4b; the script comment
   had the second labelled 4a and is corrected. Checked against the paper's own
   Appendix F and Chao et al. (2014) Appendix B, not the main text (paywalled).
8. ~~ETOPO1 citation.~~ **Done 2026-11-17** (`LITERATURE_NOTES.md`, data products).

## DO NOT DO
- Do not add a second study region. The user decided on 2026-11-16 that the study
  stays on this region; build on the existing area only.
- Do not add a seventh extension. The plan scope-locked at three; the user lifted
  the lock twice on 2026-11-16 (D, then E and F). Further effort belongs in the report.
- Do not re-pull cached GBIF cells; do not delete `data/*_cache*.json`.
- Do not launch long jobs with `nohup` where the parent process can be killed: the
  job survives the kill, and a restart then runs two copies against the same
  cache (happened 2026-10-06).
- Do not add references to the literature review beyond its 20.
