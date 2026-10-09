# HANDOFF — read this first if you are picking the project up

Course Project 9, **Biodiversity and Ecosystem Productivity** (5-person team, 8-week
timeline). This file gives a new person the full context and
the exact current status, so work can restart where it stopped.

**Snapshot date: 2026-10-07.** The analysis phase is essentially complete. The mid
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

Three extensions, **scope-locked, do not add a fourth:**
- **A** naive (raw richness) vs corrected (rarefied + effort + climate + mask)
- **B** linear vs quadratic fit, compared by AIC
- **C** three case studies: Western Ghats, Thar Desert (replaced the Deccan, which has
  no natural-cover cells), Eastern Himalaya

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
| Eight figures + CSV views | Done | `figures/`, `scripts/make_figures.py` |
| Independent verification and project review (12 errors found and fixed) | Done | `docs/VERIFICATION.md` |
| Mid-eval prep guides (full 15 pp, focused 12 pp) | Done | `docs/MID_EVAL_GUIDE_FOCUSED.{md,pdf}`, `docs/MID_EVAL_PREP_GUIDE.{md,pdf}` |

Reproducibility: `python scripts/reproduce_all.py` re-runs 17 analysis scripts from the
cached data and checks 27 headline numbers. Last run: **17/17 exit 0, 27/27 pass.**

## 4. Status: what is NOT done / open items (priority order)
1. **Three decisions that need the team:**
   - **H1 framing.** The plan's H1 is causal (biodiversity -> productivity); the data show
     a cross-regional association that shrinks within ecoregions. Options: (a) keep H1 and
     report the weak within-region result; (b) reframe as an association test; (c) add
     species-energy as the leading alternative. Recommendation: (b) + (c).
   - **GBIF DOI.** Richness comes from live API queries, so there is no citable dataset
     DOI. This needs a GBIF account: either a formal download with a DOI, or a registered
     derived dataset (title, description, public persistent URL such as Zenodo, plus a
     datasetKey/count file). See `docs/LITERATURE_NOTES.md`.
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
5. Not done at 0.5°: coverage-based richness and the 2019-23 time-window refit.
6. Optional: confirm Chao & Jost (2012) eq. 4a against the paper before citing the
   equation (the implementation already matches the authors' iNEXT package to 5e-13).

## 5. Map of the repo
| Path | What |
|---|---|
| `docs/DECISIONS.md` | Why each choice was made (append-only) |
| `docs/TODO.md` | Priority-ordered remaining work |
| `docs/RESULTS_ADJUDICATION.md` | Current interpretation of all results |
| `docs/RESULTS_EXTENSION_{A,B,C}.md` | Per-extension results |
| `docs/VERIFICATION.md` | What was independently checked and how |
| `docs/LITERATURE_NOTES.md` | Analysis references beyond the 20, each checked against its abstract; data-product DOIs |
| `docs/DELIVERABLES_MAP.md` | Plan Section 9 checklist -> files; what the policy section may claim |
| `docs/MID_EVAL_*` | Viva prep guides (md source, rendered html and pdf) |
| `data/final/` | Clean per-cell dataset + `CODEBOOK.md` |
| `data/case_study_regions/` | Ecoregion-based case-study polygons and cell-overlap tables from the teammate Step 1 package, plus a crosswalk to our cell IDs (see its README) |
| `data/*_cache*.json` | **Frozen API results = restart state. Never delete or re-pull.** |
| `data/repro/` | Logs from `reproduce_all.py` |
| `figures/` | fig1-fig8 PNG and CSV |
| `scripts/gbif_lib.py` | Grid, GBIF queries, Hurlbert rarefaction |
| `scripts/gee_extract_chunked.py` | The live Earth Engine extractor (`gee_extract.py` is deprecated and exits) |
| `scripts/reproduce_all.py` | Re-runs the analysis and checks headline numbers |
| `scripts/build_guide_pdf.py` | `python build_guide_pdf.py focused` or `full`; needs Microsoft Edge |

## 6. How to run things
Python 3.13 with `pip install -r requirements.txt`.

- **Re-run the analysis from cache (no network, no accounts):**
  `python scripts/reproduce_all.py`
- **Rebuild figures:** `python scripts/make_figures.py`
- **Re-pull GBIF / Earth Engine** (rarely needed; the caches are the frozen inputs, and
  GBIF results drift slightly because it keeps ingesting records): the GBIF API needs no
  key, but Earth Engine needs your own account. Run `earthengine authenticate`, then set
  `EE_PROJECT` in `scripts/gee_*.py` to your own Cloud project (the original project ID
  belongs to another team member's account).

## 7. Rules and pitfalls (learned the hard way)
- Never add a fourth extension. Everything beyond A/B/C is robustness, not a new question.
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
2. Run `python scripts/reproduce_all.py` to confirm the environment reproduces 27/27.
3. Get the team's answers to the three open decisions in section 4.1.
4. When asked, draft the report (ask format, brief, length first), then deliverable 8.
5. Update this file, `docs/TODO.md` and `docs/DECISIONS.md` after each significant step.
