# HANDOFF — read this first if you are picking the project up

Course Project 9, **Biodiversity and Ecosystem Productivity** (5-person team, 8-week
timeline). This file gives a new person the full context and
the exact current status, so work can restart where it stopped.

**Snapshot date: 2026-11-16** (previous: 2026-10-07). The analysis phase is complete,
including three additions made on 2026-11-16: a second taxon (Extension D), local
slopes for every cell, and two interactive maps. The mid
evaluation is a *talk about the project* (what it is, approach, literature and
citations, impact, expected results). The written mid-submission report has **not**
been drafted yet; the team asked for the analysis to come first.

---

## 1. The project in one paragraph
We ask whether biodiversity tracks ecosystem productivity once the sampling bias in
citizen-science occurrence data is corrected. Unit of analysis: 1° x 1° grid cells over
South and Southeast Asia (5-31°N, 68-102°E; 884 cells, 630 on land, **221 modelled**
after restricting to natural land cover; 36% India, 22% China, 17% Myanmar, 10% Thailand).
Response: effort-corrected bird richness (GBIF, rarefied to 250 records, plus a
log10(survey effort) covariate). Predictor: MODIS GPP (MOD17A3HGF), with ERA5-Land
climate controls. **H1:** corrected richness is positively associated with GPP after
climate controls on natural land cover.

Six extensions, **scope-locked, do not add a seventh** (the plan locked at three; the
user lifted the lock twice on 2026-11-16, for D and then for E and F — see
`docs/DECISIONS.md`):
- **A** naive (raw richness) vs corrected (rarefied + effort + climate + mask)
- **B** linear vs quadratic fit, compared by AIC
- **C** three case studies: Western Ghats, Thar Desert (replaced the Deccan, which has
  no natural-cover cells), Eastern Himalaya; plus local slopes for every cell
- **D** other taxa: vascular plants and butterflies and moths, same model chain
- **E** richness and the year-to-year stability of productivity (2001-2023)
- **F** protected land (data-limited: India's parks are missing from the public database)

## 2. What the results say (current interpretation)
Authoritative write-up: `docs/RESULTS_ADJUDICATION.md` (it supersedes
`RESULTS_SPATIAL.md` and `RESULTS_SENSITIVITY.md`, which carry banners saying so).

- Raw richness correlates r = 0.81 with survey effort; after rarefaction r = 0.24.
- Corrected richness is positively associated with GPP: standardised beta = +0.273 (1°).
  This is not a spatial-autocorrelation artefact (Hawkins subsampling test), and it gives
  ~9% out-of-sample gain under spatial block CV.
- **But it is mostly a between-ecoregion pattern.** Ecoregion fixed effects cut it by
  ~75-90%: 1° gives +0.030 (p = 0.59); 0.5° gives +0.058 (p = 0.021), so a small positive
  within-region effect remains. The spatial-error null does *not* replicate at 0.5°.
- Linear beats quadratic (delta AIC +1.9): no hump.
- The case-study ranking flips after correction (Western Ghats 1st raw -> 2nd corrected;
  Eastern Himalaya 2nd -> 1st). Spreads: effort 139x, GPP 10x, raw richness 2.2x,
  corrected richness 1.3x.
- **Second taxon (added 2026-11-16).** Vascular plants give the same picture: corrected
  beta = +0.264 for GPP (birds on the same cells +0.277), and −0.027 (p = 0.49) within
  ecoregions. Bird and plant richness agree only weakly (r = +0.30 after correction).
  Plant samples are far from complete, so read `docs/RESULTS_EXTENSION_D.md` first.
- **Local slopes (added 2026-11-16).** Fitted around each cell, the richness slope has a
  median of +0.03, and it grows steadily as the fitting window widens to the whole region.
  No statistical evidence that the slope differs from place to place
  (`docs/RESULTS_LOCAL_SLOPES.md`).
- **Direction is not identified.** Species-energy theory has productivity driving bird
  richness, so do not claim "biodiversity raises carbon uptake".

## 3. Status: what is done
| Item | Status | Where |
|---|---|---|
| Literature review (20 verified refs, ~1500 words) | Submitted | `C:\downloads\Literature_Review_Biodiversity_Ecosystem_Productivity_v3.docx` (not in this repo) |
| Grid, taxon choice (birds), GBIF pull, Earth Engine extraction, merge | Done | `scripts/`, `data/`, `docs/DECISIONS.md` |
| Extensions A, B, C | Done | `docs/RESULTS_EXTENSION_{A,B,C}.md` |
| Moran's I, VIF, cluster-robust SEs, spatial models, 2° / 0.5° grid robustness | Done | `docs/RESULTS_ADJUDICATION.md` |
| Extra robustness (Hawkins, block CV, NPP/NDVI/EVI, mask, coverage standardisation, confounders, ecoregion FE, time window) | Done | same + `docs/RESULTS_SENSITIVITY.md` |
| Clean dataset (884 x 39) + codebook | Done | `data/final/` |
| Ten figures + CSV views | Done | `figures/`, `scripts/make_figures.py` |
| Extension D: vascular plants as a second taxon | Done 2026-11-16 (1° only) | `docs/RESULTS_EXTENSION_D.md`, Fig 10 |
| Local slopes (GWR) at 1° and 0.5° | Done 2026-11-16 | `docs/RESULTS_LOCAL_SLOPES.md`, Fig 9 |
| Interactive maps (flat atlas, 3D terrain) with species names, guided tour, overlays | Done 2026-11-16 | `docs/interactive_map.html`, `docs/interactive_map_3d.html`; hosted at https://devansh061105.github.io/Course-Project-EVST/ |
| Thinning experiment (A), flexible-curve test (B), plants at 0.5° and butterflies (D) | Done 2026-11-16 | `RESULTS_EXTENSION_{A,B,D}.md`, Figs 11, 13, 17 |
| Extension E: stability of productivity; Extension F: protected land | Done 2026-11-16 (F is data-limited) | `RESULTS_EXTENSION_{E,F}.md`, Fig 15 |
| Path analysis, 960-model specification curve, survey-gap ranking | Done 2026-11-16 | `RESULTS_DIRECTION.md`, `RESULTS_SPEC_CURVE.md`, `RESULTS_SURVEY_GAPS.md`, Figs 12, 14, 16 |
| Unit tests and continuous integration | Done 2026-11-16 | `tests/`, `.github/workflows/checks.yml` |
| Presentation deck (13 slides, speaker notes) | Done 2026-11-16 | `presentation/Project9_Biodiversity_Productivity.pptx`, built by `presentation/build_deck.js` |
| Independent verification and project review (12 errors found and fixed) | Done | `docs/VERIFICATION.md` |
| Mid-eval prep guides (full 15 pp, focused 12 pp) | Done | `docs/MID_EVAL_GUIDE_FOCUSED.{md,pdf}`, `docs/MID_EVAL_PREP_GUIDE.{md,pdf}` |

Reproducibility: `python scripts/reproduce_all.py` re-runs 28 analysis scripts from the
cached data and checks 57 headline numbers (about 12 minutes). Last run (2026-11-16):
**28/28 exit 0, 57/57 pass.** `pytest -q tests` runs 17 unit tests. Both run on every
push (`.github/workflows/checks.yml`).

## 4. Status: what is NOT done / open items (priority order)
1. **Three decisions that need the team:**
   - **H1 framing.** The plan's H1 is causal (biodiversity -> productivity); the data show
     a cross-regional association that shrinks within ecoregions. Options: (a) keep H1 and
     report the weak within-region result; (b) reframe as an association test; (c) add
     species-energy as the leading alternative. Recommendation: (b) + (c).
   - **GBIF DOI: done 2026-10-11.** Registered as a GBIF derived dataset,
     https://doi.org/10.15468/dd.jf64nx (110 contributing datasets, 71,716,026 records). The per-cell data, codebook,
     counts file and scripts are deposited on Zenodo, https://doi.org/10.5281/zenodo.23264805 (CC BY 4.0). Cite both in the
     report. Supporting files: `data/gbif_derived_dataset/`.
   - **Policy source for the introduction.** Plan deliverable 1 needs the Kunming-Montreal
     Framework cited. Verified candidates: CBD Decision 15/4
     (https://www.cbd.int/doc/decisions/cop-15/cop-15-dec-04-en.pdf; Target 19, at least
     USD 200 bn/yr) and WEF *Nature Risk Rising* (2020; "over half of world GDP",
     about USD 44 trillion). The plan's "55% of global GDP (IUCN)" is actually the WEF
     figure; the plan's Carbon Brief item and an unnamed "2025 subtropical Chinese forest
     study" were never identified and should not be cited. The 20-reference cap applies
     only to the literature review, not the report.
2. **Draft the mid-submission report** only when the team asks. Ask format (Word vs Doc),
   brief and length first.
3. **Deliverable 8** (conservation-policy and citizen-science implications) is unwritten;
   `docs/DELIVERABLES_MAP.md` lists what it can and cannot claim.
4. Literature review byline: add the four teammates' names.
4a. **Plant records need a citation.** The GBIF derived-dataset DOI covers birds only.
   Register a second derived dataset before Extension D goes into a report; the
   contributing-dataset counts are ready in
   `data/gbif_derived_dataset/dataset_counts_plants.csv`. Needs a GBIF account.
5. Not done at 0.5°: coverage-based richness and the 2019-23 time-window refit.
6. Optional: confirm Chao & Jost (2012) eq. 4a against the paper before citing the
   equation (the implementation already matches the authors' iNEXT package to 5e-13).

## 5. Map of the repo
| Path | What |
|---|---|
| `docs/DECISIONS.md` | Why each choice was made (append-only) |
| `docs/TODO.md` | Priority-ordered remaining work |
| `docs/RESULTS_ADJUDICATION.md` | Current interpretation of all results |
| `docs/RESULTS_EXTENSION_{A,B,C,D}.md` | Per-extension results (D = vascular plants, added 2026-11-16) |
| `docs/RESULTS_LOCAL_SLOPES.md` | Local slopes (GWR) for every modelled cell, part of Extension C |
| `docs/interactive_map.html` | Interactive flat atlas (open in a browser) |
| `docs/interactive_map_3d.html` | Interactive 3D terrain map (needs internet once, to load three.js) |
| `scripts/build_interactive_map.py` | Builds both maps from the per-cell tables and `data/terrain_grid_0p05.npz` |
| `scripts/gee_terrain_grid.py` | One-off Earth Engine pull of the 0.05° terrain, land-cover, NDVI and GPP grids for the 3D map |
| `scripts/gbif_pull_taxon2.py`, `scripts/extension_d_plants.py` | Plant pull (own cache) and the Extension D analysis |
| `scripts/local_slopes.py` | Geographically weighted regression, numpy only |
| `docs/VERIFICATION.md` | What was independently checked and how |
| `docs/LITERATURE_NOTES.md` | Analysis references beyond the 20, each checked against its abstract; data-product DOIs |
| `docs/DELIVERABLES_MAP.md` | Plan Section 9 checklist -> files; what the policy section may claim |
| `docs/MID_EVAL_*` | Viva prep guides (md source, rendered html and pdf) |
| `data/final/` | Clean per-cell dataset + `CODEBOOK.md` |
| `data/case_study_regions/` | Ecoregion-based case-study polygons and cell-overlap tables from the teammate Step 1 package, plus a crosswalk to our cell IDs (see its README) |
| `data/*_cache*.json` | **Frozen API results = restart state. Never delete or re-pull.** |
| `data/repro/` | Logs from `reproduce_all.py` |
| `figures/` | fig1-fig17 PNG and CSV (`make_figures.py` 1-10, `make_figures_2.py` 11-17) |
| `scripts/gbif_lib.py` | Grid, GBIF queries, Hurlbert rarefaction |
| `scripts/gee_extract_chunked.py` | The live Earth Engine extractor (`gee_extract.py` is deprecated and exits) |
| `scripts/reproduce_all.py` | Re-runs the analysis and checks headline numbers |
| `scripts/build_guide_pdf.py` | `python build_guide_pdf.py focused` or `full`; needs Microsoft Edge |

## 6. How to run things
Python 3.13 with `pip install -r requirements.txt`.

- **Re-run the analysis from cache (no network, no accounts):**
  `python scripts/reproduce_all.py`
- **Rebuild figures:** `python scripts/make_figures.py`
- **Rebuild the interactive maps:** `python scripts/build_interactive_map.py`, then open
  `docs/interactive_map.html` or `docs/interactive_map_3d.html` in a browser
- **Re-pull GBIF / Earth Engine** (rarely needed; the caches are the frozen inputs, and
  GBIF results drift slightly because it keeps ingesting records): the GBIF API needs no
  key, but Earth Engine needs your own account. Run `earthengine authenticate`, then set
  `EE_PROJECT` in `scripts/gee_*.py` to your own Cloud project (the original project ID
  belongs to another team member's account).

## 7. Rules and pitfalls (learned the hard way)
- Never add a seventh extension. Everything beyond A-F is robustness, not a new question.
- GBIF: 0.3 s between requests, cache after every cell, never re-pull cached cells.
  Per-cell richness comes from ONE faceted request (`facet=speciesKey`); if a cell
  reports `facet_truncated=1`, raise `FACET_LIMIT` rather than ignoring it.
- Earth Engine: for single-band images `reduceRegions` names the output after the reducer,
  so `setOutputs([...])` is mandatory. MODIS fill values (e.g. 65535) must be masked, not
  averaged. Water (WorldCover 80) is not "natural".
- The land-cover mask drops cells dominated by WorldCover 40 (cropland), 50 (built-up) and
  80 (water).
- Do not launch long jobs with `nohup` where the parent process can be killed: the job survives
  and a restart runs a second copy against the same cache.
- Do not trust the plan's numbers blindly: its GDP source and the "~1 ERA5 pixel per cell"
  claim (true value ~94) were wrong; the review corrected them.
- Report faithfully: failures with their output, unrun scripts as unrun. Several earlier
  conclusions were overturned by later analysis ("H0 cannot be rejected" -> adjudication ->
  "small positive within-region effect at 0.5°"); check `docs/DECISIONS.md` before
  repeating an old claim.

## 8. Not in this repo
- `Project9_Comprehensive_Plan.docx` (the authoritative plan, 10 sections) and the
  submitted literature review `.docx` live outside the repo; get them from the team.
- Google Earth Engine and GBIF credentials. Never commit them.

## 9. Suggested next steps for whoever resumes
1. Read `docs/MID_EVAL_GUIDE_FOCUSED.pdf`, then `docs/RESULTS_ADJUDICATION.md`.
2. Run `python scripts/reproduce_all.py` to confirm the environment reproduces 57/57.
3. Get the team's answers to the three open decisions in section 4.1.
4. When asked, draft the report (ask format, brief, length first), then deliverable 8.
5. Update this file, `docs/TODO.md` and `docs/DECISIONS.md` after each significant step.
