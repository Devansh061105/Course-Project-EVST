# Planet LOL: final evaluation revision plan

Prepared 18 November 2026; implementation authorised by the user. The delivered version uses 30 spoken slides and 39 total slides after adding room for readable references. See `final/README.md` for the exact named scripts and timing.

## Brief and timing

- Follow the requested sequence: background/literature, extensions, gap/motivation, hypotheses, methodology, evidence, conclusion, reproducibility and local application, claims and limits, references, repository appendix.
- Preserve the pastel sage scheme, readable text with photographs/graphs, native charts and tables, linked citations and page numbers. No presenter labels or Q&A slides.
- Target **30 spoken slides**, approximately **38 total** including references, image credits and one repository-only appendix. Allow a small reference-page adjustment if full citations need more room. The new request to add slides replaces the earlier 35-slide cap.
- Target **19 minutes of prepared speech**, not 20: five equal **3:48** sections. Reserve one minute for handovers, pauses and slower graph explanations. Q&A remains separate.
- Each person receives six slides and approximately 410–440 spoken words, adjusted for graph complexity and timed rehearsal. Exact wording, slide cues and handovers will be separate from unspoken preparation notes.
- Literature/background occupies slides 2–4 only. Application-paper discussion belongs later, not in extra literature-review slides.

## Proposed slide order

| Slide | Subject | Main content / visual |
|---:|---|---|
| 1 | Planet LOL and the research question | Team name, all five given names, forest photograph |
| 2 | Background and positive evidence | Richness, GPP and carbon stocks; compact Liang/Duffy/Oehri context |
| 3 | Why published findings differ | Shape, scale and shared environmental drivers; selected comparison table |
| 4 | Sampling bias in biodiversity records | Record effort, uneven completeness and relevance to the project |
| 5 | Extensions: what we did | A sampling; B shape; C landscapes/local windows; D taxa; E stability; F protection |
| 6 | Gap and motivation | What combining corrected records, climate adjustment and scale comparisons adds |
| 7 | Hypotheses and tests | Primary association hypothesis and extension questions; distinguish original expectations from exploratory checks |
| 8 | Data and time windows | GBIF, MOD17, MOD13, ERA5-Land, WorldCover, RESOLVE, terrain, WDPA; measurement units |
| 9 | How we coded the workflow | API queries, server-side extraction, batches, caches, joins and exported tables; software roles; no source-code blocks |
| 10 | Screening and study sample | Map and 884 → 630 → 267 → 221 selection; natural-cover definition; geography |
| 11 | Correcting richness | Species-count vectors, expected richness in 250 bird records, coverage 0.90/0.95, additional effort control |
| 12 | Model comparisons | Across/within ecoregions, straight/flexible climate controls, standardisation and uncertainty |
| 13 | Spatial methods and validation | Moran diagnostics, spatial models, held-out 4° blocks, grid checks at 2°, 1°, 0.5° |
| 14 | How robustness was implemented | Specification variants, matched years and cells, bootstrap sampling error/SIMEX, bounds and pooled ecoregion slopes |
| 15 | Sampling evidence | Thinning graph; effort correlations; what random thinning does and does not test |
| 16 | Across versus within | Coefficients and intervals; coarse uncertainty and small positive finer-grid association |
| 17 | Flexible climate evidence | Linear/random-forest/boosting comparisons; avoid presenting +0.273 as the final universal estimate |
| 18 | Spatial scale and local windows | Broad/fine decomposition plus local-window interpretation; effective information |
| 19 | Robustness and inference evidence | Specifications, matched years/coverage, sampling-error reliability, effect-size bounds and pooled slopes; concise evidence table |
| 20 | Relationship shape | Linear/flexible curves, positive upper-tail slopes; no convincing observed hump |
| 21 | Landscape contrasts | Photos plus corrected rankings and GPP; Thar substitution and small case samples |
| 22 | Other taxa | Plants/Lepidoptera graphs, weak cross-taxon agreement and completeness limits |
| 23 | Temporal stability | 2001–2023 GPP variability, adjustment sequence, mean-GPP caveat |
| 24 | Protected land | F1 record concentration, F2 raw/corrected richness, F3 interaction; data definitions and inconclusive inference |
| 25 | Recording gaps | Map, 46 excluded eligible cells and cautious monitoring implications |
| 26 | Conclusion | Answer the hypotheses and relate the results back to the opening literature |
| 27 | Reproducibility | Cached-data pipeline, codebook, figure-value tables, recorded checks and unit tests, CI; live pulls versus offline reruns |
| 28 | Telangana application | Medak forest paper, a concrete proposed adaptation and data/resolution requirements |
| 29 | What we claim | Supported associations, scale dependence, sampling correction and remaining small positive estimate |
| 30 | What we do not claim | Causation/direction diagram; no India-wide, carbon-stock or protection-effect conclusion; closing sentence |
| 31 onward | References and image credits | Complete, clickable citations; not read aloud |
| Final slide | Appendix | Repository title and clickable repository link only |

## Equal speaking and preparation responsibilities

| Speaker | Slides | Prepared-speech clock | Responsibility |
|---|---|---|---|
| Vaibhavi | 1–6 | 0:00–3:48 | Introduction, context, extensions and motivation |
| Deepraj | 7–12 | 3:48–7:36 | Hypotheses, data, implementation, screening and model setup |
| Ekansh | 13–18 | 7:36–11:24 | Spatial/robustness methods and core association evidence |
| Devansh | 19–24 | 11:24–15:12 | Robustness interpretation and ecological extensions |
| Raunak | 25–30 | 15:12–19:00 | Monitoring implications, conclusion, reproducibility, local application and claims |

Every person explains a substantive analytical choice or inference, rather than receiving only housekeeping. These are equal presentation/preparation assignments, not invented claims about who originally performed the research. Equal marks cannot be guaranteed; equal speaking time, comparable scripts and balanced technical responsibility can be designed and checked.

## Methodology detail to add

Explain the actual implementation rather than generic library lists:

- Python/NumPy/SciPy for numerical calculations and rarefaction; pandas for one-to-one joins and tabular checks; statsmodels for regressions and robust uncertainty; scikit-learn for flexible climate models; PySAL packages for spatial diagnostics/models; Matplotlib for reproducible figures; Earth Engine for environmental extraction.
- GBIF coordinate/occurrence filters and species-facet counts; these are occurrence-record frequencies, not ecological censuses of individuals.
- Active chunked Earth Engine extraction, cached batches, invalid/fill-value masking, product scale factors, temperature/precipitation conversions, spatial aggregation and matching by cell ID. Do not describe the deprecated extraction script as the implementation used.
- Dominant land-cover exclusions and sample completeness; residual observer preferences remain possible.
- Why models are compared, how flexible residualisation and geographic folds work, and why cell count differs from independent information.
- Robustness choices and their limits: no automatic causal interpretation of machine learning, no treating related specifications as independent replications, no equating non-significance with zero.

## Local paper selection

Primary proposed application anchor:

Nasam, M. K., Bheemareeddyvalla, V. R., Vainala, V., Bathula, J., & Bodiga, S. (2022). **Influence of Assisted Natural Regeneration in increasing carbon stocks of Tropical deciduous forests.** Environment and Ecology, 40(1), 82–92.

- Publisher-hosted full text: https://environmentandecology.com/wp-content/uploads/2024/05/MS15.pdf
- Independent institutional listing: https://fcrihyd.in/research/publications/index.htm
- The paper compares tree richness and carbon stocks in primary and assisted-regeneration forests in the Medak Circle, Telangana, using field plots. This gives a specific local management question rather than a location mentioned only for familiarity.
- Proposed application: test whether effort-standardised diversity and matched satellite GPP show similar differences among suitable primary/regenerating forest patches, while accounting for stand age/structure, habitat, climate and spatial dependence.
- This would be a **future adaptation**, not a completed local replication. Verify access to plot coordinates/raw counts or obtain new field observations. Reconcile small plots with satellite pixels using defensible aggregation and sufficiently large forest patches; do not copy one coarse grid estimate across plots as independent data.
- The paper measures carbon stocks; our present outcome is annual GPP. Compare questions/design choices, not the two quantities numerically or as interchangeable outcomes.

Supporting local baseline, if space permits:

Chovatiya et al. (2025). **Plant Species Composition and Diversity in Tropical Dry Mixed-Deciduous Forest of Telangana, India.** Indian Journal of Ecology, 52(5), 1119–1132. DOI: https://doi.org/10.55362/IJE/2025/4624

Publisher: https://www.indianjecol.org/published-articles/8

This supplies Narsapur field-diversity context, not an existing GPP test. Keep it supporting rather than presenting a second new research extension.

Screened alternatives include northern Telangana aboveground-phytomass research (DOI 10.1080/14888386.2020.1843541; publisher full text inaccessible during this review) and Andhra Pradesh biomass/carbon research (DOI 10.1515/eje-2015-0007; based on older state-level data). Prefer the accessible Medak field study for the main application slide.

## Deliverables after “continue”

1. **Editable PowerPoint**: update `presentation/final/Final_Evaluation_Biodiversity_Productivity.pptx` with the new sequence, text, existing figures/photos, needed extra evidence and citations, all five names, and full speaker notes.
2. **Matching PDF**: update the PDF in the same folder, retaining working links.
3. **Authoritative presentation README**: replace `presentation/final/README.md` with the named workload/timing table, a mini preparation guide above each person's script, and exact ready-to-talk words for every slide, including transitions and closing. Mark unspoken cues clearly. A 19-minute total script will leave time within the 20-minute limit.
4. **Separate cross-question file**: `presentation/final/CROSS_QUESTIONS.md`, approximately 60–75 demanding questions categorised by the actual presentation sections. For each: slide/topic, assigned lead, short defensible answer, likely follow-up or hypothetical, and evidence/source. Cover design choices, alternative explanations, what-if changes, statistical interpretation, resolution, missingness, protection and the Telangana proposal. All questions stay within displayed/explained methods and claims.
5. **Update the existing speaking-guide file and root README** to point to the authoritative script and remove conflicting old timing instructions.

## Build and review

Create a slide-to-repository coverage checklist first. Prioritise current adjudication/inference and the latest finer-grid checks over superseded early conclusions. Keep all A–F strands; present secondary technical details in compact summaries and the preparation files rather than adding a Q&A deck.

Author native charts/tables and preserve current visual styling. Check evidence values, data windows, terminology, author-year citations, all external links, exact slide/script alignment, named workload balance and spoken word counts. Render and visually inspect every slide and the final PDF, especially text alongside graphs and reference readability. Rehearsal with the team remains the final test of pace.

The user authorised implementation and a GitHub push. The completed presentation adds no new local research: the Medak adaptation remains explicitly proposed. Final delivery uses seven reference pages for readability (39 slides total) and 75 cross-questions.
