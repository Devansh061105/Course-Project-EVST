# TODO — priority order (updated 2026-10-06)

Plan reference: `C:\downloads\Project9_Comprehensive_Plan.docx`, Section 6 (Steps 1–10).
Timeline: 8 weeks; midpoint passed. Literature review submitted.
Current interpretation lives in `docs/RESULTS_ADJUDICATION.md`.

## TEAM ACTIONS (need an account or a team decision)

1. ~~Finish the 0.5° robustness grid.~~ **Done 2026-10-06** in bounded
   chunks (`MAX_PULLS`). Results: `RESULTS_ADJUDICATION.md` section 8. Remaining gap:
   0.5° has GPP only (no NPP, no time-window refit).
2. **Register a GBIF derived dataset before the final report.** Our richness comes
   from live API queries, so no citable DOI exists. GBIF requires one. Needs a
   GBIF account (yours to create). See `docs/LITERATURE_NOTES.md`, data products.
3. **Decide the report framing** (see "Open question" below).

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

## NEXT
4. ~~NPP at 0.5°~~ Done (section 9 of RESULTS_ADJUDICATION). Still not done at 0.5°: coverage-based richness and the 2019-23 time-window refit.
5. **Draft the mid submission / report** when the team asks. Confirm format, brief and
   length first.
6. Optional: confirm Chao & Jost (2012) eq. 4a against the paper before citing
   the equation itself (formula implemented from memory; boundary checks pass).

## DO NOT DO
- Do not add a fourth extension. The plan scope-locks at three; everything above
  is robustness for the existing three, not new questions.
- Do not re-pull cached GBIF cells; do not delete `data/*_cache*.json`.
- Do not launch long jobs with `nohup` where the parent process can be killed: the
  job survives the kill, and a restart then runs two copies against the same
  cache (happened 2026-10-06).
- Do not add references to the literature review beyond its 20.
