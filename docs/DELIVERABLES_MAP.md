# Plan deliverables → where each one is (2026-10-06)

Maps the plan's Section 9 checklist (`C:\downloads\Project9_Comprehensive_Plan.docx`)
to the files that satisfy it, and states plainly what is not done. The plan defines
no separate mid-submission milestone; items 1-2 fall at or before the Week-4
midpoint and everything else is Week 5+, so this is also the mid-submission
inventory.

| # | Plan deliverable | Status | Where |
|---|---|---|---|
| 1 | Opening section: Kunming-Montreal GBF + recent (2023-2025) literature | **Partly.** Literature review submitted, cites 2023-2026 work (Chen 2023, Deng 2025, El-Gabbas 2026). It does **not** mention the GBF by name, and cannot add the policy source (the assignment caps references at 20, peer-reviewed). The report introduction must add it. | `C:\downloads\Literature_Review_..._v3.docx` |
| 2 | Clean merged dataset (GBIF corrected richness + MODIS + ERA5-Land + WorldCover mask) per cell | **Done** | `data/final/biodiversity_productivity_1deg.csv` (884 rows x 39 cols), `data/final/CODEBOOK.md` |
| 3 | Naive vs corrected (Extension A), both regression outputs and plots | **Done** | `RESULTS_EXTENSION_A.md`; `fig7_naive_vs_corrected`, `fig3_attenuation` |
| 4 | Linear vs quadratic (Extension B), tied to the real debate | **Done** | `RESULTS_EXTENSION_B.md`; `fig8_linear_vs_quadratic` |
| 5 | Three case studies (Extension C), Western Ghats vs published findings | **Done, with one substitution** (Thar replaces the Deccan, which had no natural-cover cells) and one limit (stock vs flux, so no like-for-like numeric comparison with Kothandaraman 2020) | `RESULTS_EXTENSION_C.md`; `fig6_case_study_spreads`, `fig1`, `fig2`; `DECISIONS.md` |
| 6 | Moran's I and VIF, reported honestly | **Done** | `RESULTS_SPATIAL.md` (Moran, spatial models), `RESULTS_EXTENSION_A.md` (VIF), `RESULTS_ADJUDICATION.md`; `fig5_correlogram` |
| 7 | Grid-size robustness | **Done** at 2.0, 1.0 and 0.5 degrees | `RESULTS_SENSITIVITY.md`, `RESULTS_ADJUDICATION.md` sections 8-9 |
| 8 | Closing section: conservation-policy and citizen-science implications | **Not written** (report prose). The evidence for it exists; see below. | to draft |

## What the policy section can honestly say (from the results)
Each claim is limited to what a specific result supports.

- **Citizen-science bias matters and is correctable.** Raw richness correlates with
  survey effort at r = 0.81; rarefaction cuts that to r = 0.24; the regional
  ranking of the three case studies flips (Western Ghats first on raw counts,
  Eastern Himalaya first once corrected). Survey effort differs 139-fold across the
  three regions. (`RESULTS_EXTENSION_C.md`, `fig7`)
- **Biodiversity-productivity link: strong between regions, weak within.**
  Effort-corrected richness is associated with productivity across ecoregions, but
  ecoregion fixed effects remove ~75-90% of the association; a small positive
  remainder (about 0.03-0.06 SD) is supported at 0.5 degree and is fragile.
  Cross-regional species-pool differences, not local biodiversity effects,
  dominate. (`RESULTS_ADJUDICATION.md`)
- **Direction is not identified.** Bird richness driving plant productivity is
  implausible; the species-energy literature has productivity driving richness.
  Any "biodiversity supports carbon uptake" reading should be avoided for this
  design. The data cannot tell conservation planners that adding bird species
  raises carbon uptake.
- **Geography of the evidence.** The study region is South *and Southeast* Asia,
  and the 221 modelled cells are only 36% India (China 22%, Myanmar 17%, Thailand
  10%), because most Indian land is cropland. Do not present the result as an
  Indian or "South Asian" one.
- **Land use is itself a result.** 217 of 630 land cells are dominated by
  cropland or built-up cover; all 25 Deccan cells are cropland-dominant (mean 77%
  converted). Natural-ecosystem comparisons at 1 degree are only possible in
  roughly a third of the land area.
- **Do not claim** anything about the $200bn GBF target, about conservation
  prioritisation by region, or about carbon storage: GPP and NPP are fluxes, not
  carbon stocks, and the results do not test any of these.

## Remaining gaps, in order of importance
1. Deliverable 8 and the report text (user has asked for analysis first).
2. GBF source for the introduction (CBD decision text; non-peer-reviewed is fine in
   the report but must be cited).
3. GBIF derived-dataset DOI (needs the user's GBIF account).
4. Not done at 0.5 degree: coverage-based richness and the 2019-23 time-window refit.
