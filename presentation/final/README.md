# Planet LOL: presentation script and preparation guide

This is the **authoritative ready-to-talk script** for the final evaluation.

- [Editable PowerPoint](Final_Evaluation_Biodiversity_Productivity.pptx)
- [Matching PDF](Final_Evaluation_Biodiversity_Productivity.pdf)
- [Categorised cross-questions and answers](CROSS_QUESTIONS.md)

**39 slides total:** 1–30 spoken content; 31–37 linked references; 38 image credits; 39 repository-only appendix. All slides are visible. Finish the prepared speech on slide 30, then leave the references available without reading every entry. No Q&A slide section.

## Timing and equal work split

The prepared speech totals **19:00**. Each person receives **six slides and 3:48**, with closely matched script lengths. This leaves **1:00 within the 20-minute limit** for pauses and small overruns. Handovers are already included in the words below. Q&A is separate.

| Speaker | Slides | Prepared-speech clock | Spoken words | Responsibility |
|---|---|---|---:|---|
| Vaibhavi | 1–6 | 0:00–3:48 | 442 | Introduction, literature, extensions and motivation |
| Deepraj | 7–12 | 3:48–7:36 | 445 | Hypotheses, data, coding workflow and model setup |
| Ekansh | 13–18 | 7:36–11:24 | 446 | Spatial/robustness methods and the core findings |
| Devansh | 19–24 | 11:24–15:12 | 448 | Robustness evidence and ecological extensions |
| Raunak | 25–30 | 15:12–19:00 | 444 | Monitoring, conclusion, reproducibility, local application and claims |

The scripts contain about 116–118 words per minute of allocated time, including brief visual pauses. The first section has a short cover and more time for context; other sections allow longer on key evidence. Rehearse aloud with slide changes. Use the one-minute reserve rather than adding new examples or reading all table rows.

Each speaker prepares their assigned sources and answers for cross-questioning as well as their spoken section. These assignments balance presentation responsibility; they do not invent attribution for the original research. Everyone should know the primary question, main result, association/causation distinction and the Telangana proposal.

**Reading rule:** speak only text under **Exact spoken script**. Preparation notes, visual cues, source links and timing labels are unspoken. The scripts already include the transitions.

## Vaibhavi: Introduction, literature, extensions and motivation

**Slides 1–6. Allocation 3:48. Target 0:00–3:48. 442 spoken words.**

### Mini preparation guide — do not read aloud

- Your job is to establish why the question is worth asking and why the design needs correction and scale checks. Give the literature context without reading every table row.
- Know richness, annual GPP and stored carbon. Explain why producer-diversity experiments differ from bird-richness observations.
- Mention Liang/Duffy/Oehri for supportive evidence, Adler/Fraser for differing findings, and Grace/Chase/Gonzalez for mechanisms and scale.
- Explain sampling bias without calling citizen-science records useless. Describe the six extensions briefly and hand over the primary hypothesis to Deepraj.
- Avoid claiming a first-ever study or saying that birds cause plant productivity.

### Exact spoken script

#### Slide 1: Biodiversity and ecosystem productivity

**25 seconds. Talk clock 0:00–0:25.**

Good morning. We are Planet LOL: Vaibhavi, Deepraj, Ekansh, Devansh and Raunak. Our project asks whether places with more species are more productive after accounting for uneven recording effort. We combine citizen-science records with satellite observations across South and Southeast Asia. I will introduce the context and motivation before we explain the methods and evidence.

**Preparation sources:** [GBIF](https://doi.org/10.15468/dd.jf64nx), [MOD17](https://doi.org/10.5067/MODIS/MOD17A3HGF.061).

#### Slide 2: Background: diversity and productivity

**45 seconds. Talk clock 0:25–1:10.**

Species richness means how many species a place contains. Gross primary productivity, or GPP, is the carbon plants take up each year. Carbon stocks measure carbon already stored, so these are different outcomes. Liang and Duffy report positive biodiversity–production relationships, while Oehri provides a landscape comparison using satellite proxies. Those studies motivate our question. However, much of the mechanism literature concerns plants. Our main richness indicator is birds, so we test an association rather than assuming that birds cause plant production.

**Preparation sources:** [Hurlbert](https://doi.org/10.2307/1934145), [Running](https://doi.org/10.1641/0006-3568(2004)054[0547:ACSMOG]2.0.CO;2), [Liang](https://doi.org/10.1126/science.aaf8957), [Duffy](https://doi.org/10.1038/nature23886), [Oehri](https://doi.org/10.1073/pnas.1703928114), [Deng](https://doi.org/10.1073/pnas.2506750122), [Chen](https://doi.org/10.1038/s41586-023-05941-9).

#### Slide 3: Literature review: why findings differ

**42 seconds. Talk clock 1:10–1:52.**

Published results differ for understandable reasons. Adler found that productivity poorly predicted plant richness in herbaceous communities. Fraser reported a hump-shaped relationship in grasslands. Grace emphasised several mechanisms and shared environmental drivers, while Chase and Gonzalez show why spatial scale matters. Some papers also predict richness from productivity, reversing our model direction. We therefore test relationship shape and compare regional patterns with differences inside ecoregions. Different findings do not automatically mean that one study is wrong.

**Preparation sources:** [Adler](https://doi.org/10.1126/science.1204498), [Fraser](https://doi.org/10.1126/science.aab3916), [Grace](https://doi.org/10.1038/nature16524), [Chase](https://doi.org/10.1038/416427a), [Gonzalez](https://doi.org/10.1111/ele.13456).

#### Slide 4: Literature review: uneven records can mislead

**38 seconds. Talk clock 1:52–2:30.**

The second issue is the record base. Beck, Engemann and Hughes show how uneven sampling can distort biodiversity patterns. A popular birdwatching location can have more recorded species simply because people visit it more often. Equalising record counts helps, but cannot remove preferences for particular habitats or species. Our study therefore combines a richness correction with an effort covariate, environmental controls and spatial checks. The question is how much ecological association remains after those comparisons.

**Preparation sources:** [Beck](https://doi.org/10.1016/j.ecoinf.2013.11.002), [Engemann](https://doi.org/10.1002/ece3.1405), [Hughes](https://doi.org/10.1111/ecog.05926), [ElGabbas](https://doi.org/10.1111/ddi.70205).

#### Slide 5: Extensions: what we did

**37 seconds. Talk clock 2:30–3:07.**

We investigated six extensions. A tests sampling correction and random thinning. B compares straight and curved relationships. C examines landscapes and changing neighbourhood size. D checks plants and butterflies and moths. E tests stability of productivity through time. F asks about protected land, while recognising database limitations. These are connected questions within the same regional project. They let us challenge the main interpretation from several directions instead of relying on one favourable regression.

**Preparation sources:** [Hurlbert](https://doi.org/10.2307/1934145), [Fraser](https://doi.org/10.1126/science.aab3916), [Wolters](https://doi.org/10.1890/0012-9658(2006)87[1886:RATSRO]2.0.CO;2), [Tilman](https://doi.org/10.1038/nature04742), [WDPA](https://www.protectedplanet.net/en/thematic-areas/wdpa).

#### Slide 6: Research gap and motivation

**41 seconds. Talk clock 3:07–3:48.**

The gap is the combination of biases and scales. An uncorrected map can confuse recording with richness, while a regional association can partly reflect climate differences between ecosystems. We bring these issues into one traceable workflow and examine where the data remain incomplete. We also report uncertainty and avoid selecting only favourable results. Our contribution is this combined regional assessment, rather than a claim of being the first biodiversity study. Deepraj will now explain the hypothesis and how we built the analysis.

**Preparation sources:** [Hughes](https://doi.org/10.1111/ecog.05926), [Chase](https://doi.org/10.1038/416427a), [Grace](https://doi.org/10.1038/nature16524), [Gonzalez](https://doi.org/10.1111/ele.13456).

## Deepraj: Hypotheses, data, coding workflow and model setup

**Slides 7–12. Allocation 3:48. Target 3:48–7:36. 445 spoken words.**

### Mini preparation guide — do not read aloud

- Your job is to make the implementation understandable and defensible. Explain what the code does and why each step exists, without displaying or reciting source code.
- Know the product names and time windows, the 884/630/267/221 sample chain, and why only 36% of modelled cells are in India.
- Explain species-facet counts, batch extraction, caches, invalid-value masking, scale factors, unit conversion and one-to-one cell-ID joins.
- Explain rarefaction versus equal coverage. Occurrence frequencies are not animal abundance, independent sightings or random field sampling.
- Define standardised beta. Distinguish robust uncertainty from changing the point estimate, and flexible adjustment from causal identification.

### Exact spoken script

#### Slide 7: Hypotheses and extension questions

**35 seconds. Talk clock 3:48–4:23.**

Our primary hypothesis is that effort-corrected richness is positively associated with GPP after climate adjustment and screening for natural land cover. The corresponding null is a zero coefficient in the stated model. The extensions ask whether this association changes with shape, landscape, taxon, stability or protection. Later robustness checks investigate explanations for the result; we do not present every follow-up as a separately preregistered hypothesis. The wording concerns association because our observations do not establish causal direction.

**Preparation sources:** [Grace](https://doi.org/10.1038/nature16524), [Chase](https://doi.org/10.1038/416427a), [Hurlbert](https://doi.org/10.2307/1934145).

#### Slide 8: Data sources and study periods

**35 seconds. Talk clock 4:23–4:58.**

We join information by grid cell. GBIF provides occurrence records from 2000 to 2024. MODIS provides GPP, and ERA5-Land provides temperature and rainfall, mainly averaged over 2019 to 2023. WorldCover supplies the land-cover screen and RESOLVE supplies ecoregions. Terrain and greenness support sensitivity checks. Stability uses annual GPP from 2001 to 2023; protection uses a November 2026 extract. We explicitly check matched occurrence years because these time windows differ.

**Preparation sources:** [GBIF](https://doi.org/10.15468/dd.jf64nx), [MOD17](https://doi.org/10.5067/MODIS/MOD17A3HGF.061), [ERA](https://doi.org/10.5194/essd-13-4349-2021), [WorldCover](https://doi.org/10.5281/zenodo.7254221), [Resolve](https://doi.org/10.1093/biosci/bix014), [SRTM](https://doi.org/10.5067/MEaSUREs/SRTM/SRTMGL1.003), [MOD13](https://doi.org/10.5067/MODIS/MOD13Q1.061).

#### Slide 9: How we coded the analytical workflow

**44 seconds. Talk clock 4:58–5:42.**

We used Python to query species-count facets from GBIF rather than download every individual record page. Earth Engine extracted environmental summaries in batches, with reusable caches. We masked invalid values, applied product scale factors and converted climate units before joining tables one-to-one by cell ID. Pandas handled tables, NumPy and SciPy handled calculations, statsmodels and scikit-learn fitted models, and PySAL supported spatial analysis. Matplotlib linked figures to saved output tables.

**Preparation sources:** [GBIF](https://doi.org/10.15468/dd.jf64nx), [MOD17](https://doi.org/10.5067/MODIS/MOD17A3HGF.061), [ERA](https://doi.org/10.5194/essd-13-4349-2021), [WorldCover](https://doi.org/10.5281/zenodo.7254221).

#### Slide 10: Study area and sample selection

**35 seconds. Talk clock 5:42–6:17.**

The study covers South and Southeast Asia, not India alone. We start with 884 grid cells. Land-cover availability leaves 630 land cells; the dominant-cover screen leaves 267, and sufficient bird records plus complete environmental data leave 221 modelled cells. Only 36 percent of these are in India. Dominant crop, built-up or water cells are excluded. Retained cells can still contain mixed habitats. The map makes both the geographic coverage and the exclusions visible.

**Unspoken visual cue:** Map and selection table: distinguish land, eligible land-cover cells and the final model sample. Mixed habitat can remain inside retained cells.

**Preparation sources:** [WorldCover](https://doi.org/10.5281/zenodo.7254221), [Resolve](https://doi.org/10.1093/biosci/bix014), [GBIF](https://doi.org/10.15468/dd.jf64nx).

#### Slide 11: Comparing cells at equal sampling effort

**39 seconds. Talk clock 6:17–6:56.**

Rarefaction asks how many species we expect in the same 250 bird records from each cell. It standardises the recording pool without treating records as independent counts of animals. We also control total recording effort. Following Chao and Jost, equal-coverage checks compare samples at similar estimated completeness, because equal record counts can still contain different information. We repeat the comparison with matched observation years. None of these steps discovers species that never entered the database or makes observer choices random.

**Preparation sources:** [Hurlbert](https://doi.org/10.2307/1934145), [Chao](https://doi.org/10.1890/11-1952.1).

#### Slide 12: Model design and flexible climate adjustment

**40 seconds. Talk clock 6:56–7:36.**

Our baseline compares adjusted cells across the whole region. Ecoregion fixed effects then remove differences in regional means. Flexible climate models allow temperature, rainfall and other controls to have curved responses. We predict both GPP and richness from controls, then relate their remaining variation. Robust or ecoregion-clustered uncertainty accompanies the relevant model. A standardised beta expresses the GPP difference associated with a one-standard-deviation richness difference. Ekansh will explain the spatial checks before showing the main evidence.

**Preparation sources:** [Grace](https://doi.org/10.1038/nature16524), [Roberts](https://doi.org/10.1111/ecog.02881), [Ploton](https://doi.org/10.1038/s41467-020-18321-y), [Resolve](https://doi.org/10.1093/biosci/bix014), [DML](https://doi.org/10.1111/ectj.12097).

## Ekansh: Spatial/robustness methods and the core findings

**Slides 13–18. Allocation 3:48. Target 7:36–11:24. 446 spoken words.**

### Mini preparation guide — do not read aloud

- Your job is to connect methods to the main evidence. Start with why neighbouring cells share information, then explain the reduction in the coefficient.
- Know Moran diagnostics, spatial lag/error model distinctions, geographic validation and grid-size sensitivity at a conceptual level.
- Explain why specification checks, bootstrap sampling uncertainty, SIMEX and equivalence tests answer different questions. SIMEX adds measurement noise, fits how estimates change, and extrapolates towards zero noise; it relies on its error assumptions.
- For every graph identify the axes, comparison, uncertainty and main finding. The ordered thinning levels are not a time series.
- Do not equate p>0.05 with zero, describe every flexible estimate as significant, or claim four-degree blocks eliminate all spatial dependence.

### Exact spoken script

#### Slide 13: Spatial methodology and geographic validation

**37 seconds. Talk clock 7:36–8:13.**

Nearby cells share environmental conditions, so treating all cells as independent can exaggerate information. We use Moran diagnostics and spatial models to examine this dependence. Geographic validation holds out four-degree blocks and asks whether richness improves prediction in unseen areas. We also compare grids of two, one and half a degree. These checks concern different questions: dependence, predictive transfer and spatial resolution. Geographic blocks reduce leakage but can still share environmental structure.

**Unspoken visual cue:** Horizontal axis: distance in degrees. Vertical axis: residual Moran similarity. Blue is the corrected linear model; orange additionally removes ecoregion means. The cited initial I≈0.72 is a separate baseline summary, not the first point of this binned correlogram.

**Preparation sources:** [Hawkins](https://doi.org/10.1111/j.0906-7590.2007.05117.x), [Kissling](https://doi.org/10.1111/j.1466-8238.2007.00334.x), [Roberts](https://doi.org/10.1111/ecog.02881), [Ploton](https://doi.org/10.1038/s41467-020-18321-y).

#### Slide 14: How we implemented robustness checks

**38 seconds. Talk clock 8:13–8:51.**

We varied reasonable analysis choices instead of selecting one specification. The workflow also compares equal coverage, matched years and shared cells. A bootstrap of record-count vectors measures sampling uncertainty in richness; reliability adjustment and SIMEX check whether that uncertainty attenuates the slope. Equivalence tests ask whether a coefficient is smaller than a stated bound, and pooled ecoregion slopes summarise regional estimates. These are complementary checks on the same data, rather than independent experiments.

**Preparation sources:** [Simonsohn](https://doi.org/10.1038/s41562-020-0912-z), [Chao](https://doi.org/10.1890/11-1952.1), [Cook](https://doi.org/10.1080/01621459.1994.10476871), [Lakens](https://doi.org/10.1177/1948550617697177), [DerSimonian](https://doi.org/10.1016/0197-2456(86)90046-2).

#### Slide 15: Sampling correction reduces the effort signal

**35 seconds. Talk clock 8:51–9:26.**

Here the horizontal axis shows records retained after random thinning, and the vertical axis shows the fraction of full-data richness. The raw count falls sharply, while corrected richness stays near one. At 250 retained records, raw richness keeps about 23 percent of its original value. The effort correlation falls from 0.81 to 0.24 after correction. This supports correction against random differences in record count, while leaving real observer preferences as a limitation.

**Unspoken visual cue:** Horizontal axis: retained records at ordered levels. Vertical axis: share of full-data richness. Blue corrected richness stays near one; terracotta raw richness drops.

**Preparation sources:** [Hurlbert](https://doi.org/10.2307/1934145), [Hughes](https://doi.org/10.1111/ecog.05926).

#### Slide 16: The association is weaker within ecoregions

**43 seconds. Talk clock 9:26–10:09.**

Blue bars compare across the region; terracotta bars compare within ecoregions. Whiskers show 95 percent intervals. At one degree, the coefficient falls from about 0.27 to 0.03, with substantial uncertainty. At half a degree, a small positive within-region estimate remains. Pooling 35 sufficiently sampled ecoregions gives about 0.069. The important pattern is the reduction in size. A non-significant coarse estimate does not establish zero, and these within-region comparisons still cannot identify causation.

**Unspoken visual cue:** Horizontal axis: standardised GPP association beta. Blue bars are across-region and terracotta bars within-ecoregion estimates. Whiskers are approximate 95% intervals. Distinguish the 0.058 single fixed-effect estimate from the 0.069 pooled slope.

**Preparation sources:** [Chase](https://doi.org/10.1038/416427a), [Gonzalez](https://doi.org/10.1111/ele.13456), [Resolve](https://doi.org/10.1093/biosci/bix014).

#### Slide 17: Flexible climate controls reduce the estimate

**40 seconds. Talk clock 10:09–10:49.**

Straight-line climate controls may leave nonlinear environmental structure in the richness coefficient. Here we compare them with random forests and gradient boosting. Across-region estimates fall to roughly 0.14 to 0.17 at one degree and about 0.07 at half a degree. Read the uncertainty as well as the positive point estimates: the finer-grid flexible results are borderline. This is why 0.27 should not be presented as the final universal effect size. The control set also differs slightly from the baseline.

**Unspoken visual cue:** Compare linear, random forest and boosting within each grain. Read the intervals. These rows use an expanded control set and cross-fitting, so their linear value differs from the baseline.

**Preparation sources:** [DML](https://doi.org/10.1111/ectj.12097), [Grace](https://doi.org/10.1038/nature16524).

#### Slide 18: Scale and neighbourhood size change the comparison

**35 seconds. Talk clock 10:49–11:24.**

The left graph separates broad and fine spatial patterns. The largest positive association occurs in the broadest band. The right graph changes the neighbourhood around each cell: wider windows recover a larger regional association. Both comparisons show that scale changes what is being contrasted. Under the effective-sample calculation, 221 cells provide information comparable to about 36 independent observations. Local slopes describe patterns and cannot rank conservation returns. Devansh will now test how this interpretation extends across other analyses.

**Unspoken visual cue:** Left: coefficient across scale bands, not a time trend. Right: median local coefficient versus window radius at 0.5°. The local curve is descriptive; the effective sample size is a calculation, not a literal replacement dataset.

**Preparation sources:** [Dray](https://doi.org/10.1016/j.ecolmodel.2006.02.015), [Clifford](https://doi.org/10.2307/2532039), [Chase](https://doi.org/10.1038/416427a), [Brunsdon](https://doi.org/10.1111/j.1538-4632.1996.tb00936.x).

## Devansh: Robustness evidence and ecological extensions

**Slides 19–24. Allocation 3:48. Target 11:24–15:12. 448 spoken words.**

### Mini preparation guide — do not read aloud

- Your job is to test the interpretation across robustness checks and ecological extensions. Give each result one finding and one relevant qualification.
- Know the difference between 960 related fits and independent replication; between 99% sampling-error reliability and absence of observer bias; between a size bound and a zero-effect test.
- Explain why a fitted curve bending is insufficient to establish a hump. Explain the raw/corrected landscape ranking, and why the Thar replaced the original Deccan box.
- For taxa, do not compare standardised coefficients as equal measures of biological importance when samples and completeness differ.
- For stability, negative instability beta means steadier GPP. For protection, cover F1 recording, F2 richness and F3 interaction; the subsets and database definitions limit inference.

### Exact spoken script

#### Slide 19: Robustness: how precise and how small?

**43 seconds. Talk clock 11:24–12:07.**

This table brings the robustness evidence together. Across-region coefficients remain larger across 960 related specifications. Sampling-error reliability is about 0.99, and correcting that noise barely changes the within-region slope. Equivalence tests support an association smaller than half the linear across-region estimate in all five samples. At half a degree, equal-coverage estimates are around 0.071 to 0.075 and matched-year records give about 0.062. These numbers support a small association under these choices, while observer bias and confounding remain possible.

**Unspoken visual cue:** The table contains several distinct estimators and tests; it is not a single pooled confidence interval. The 0.99 reliability concerns estimated sampling noise only.

**Preparation sources:** [Simonsohn](https://doi.org/10.1038/s41562-020-0912-z), [Chao](https://doi.org/10.1890/11-1952.1), [Cook](https://doi.org/10.1080/01621459.1994.10476871), [Lakens](https://doi.org/10.1177/1948550617697177), [DerSimonian](https://doi.org/10.1016/0197-2456(86)90046-2), [MOD17](https://doi.org/10.5067/MODIS/MOD17A3HGF.061), [MOD13](https://doi.org/10.5067/MODIS/MOD13Q1.061).

#### Slide 20: No convincing evidence of a hump

**32 seconds. Talk clock 12:07–12:39.**

The horizontal axis is adjusted richness and the vertical axis is fitted GPP. The solid curve is flexible and the dashed line is straight. At one degree the curve bends, but the directly fitted slope among the richest cells remains positive. At half a degree the straight line fits better. We therefore find no convincing hump over the observed range. This does not prove that every ecosystem follows a perfectly linear relationship.

**Unspoken visual cue:** Horizontal axis: adjusted richness in SD units. Vertical axis: fitted GPP in SD units. Solid is flexible and dashed is straight. The curves show fits rather than every observed point.

**Preparation sources:** [Fraser](https://doi.org/10.1126/science.aab3916), [Liang](https://doi.org/10.1126/science.aaf8957), [Gonzalez](https://doi.org/10.1111/ele.13456).

#### Slide 21: Three landscapes show why correction matters

**37 seconds. Talk clock 12:39–13:16.**

These photographs illustrate the three landscapes; the numerical comparisons come from grid cells. The Western Ghats have higher GPP and far more records. They rank first on raw richness, but the Eastern Himalaya ranks first after correction. Effort differs 139-fold while corrected richness differs only about 1.3-fold. The Thar replaces the original Deccan box because its cells failed the natural-cover screen. These are small descriptive samples. Carbon stocks remain distinct from annual GPP.

**Unspoken visual cue:** Photos illustrate habitats; values come from coarse cells. Western Ghats/Thar/Eastern Himalaya contain 7/8/24 modelled cells. The Deccan exclusion applies to the original project box, not every forest in the Deccan.

**Preparation sources:** [Kothandaraman](https://doi.org/10.1038/s41598-020-70313-6), [Najeeb](https://doi.org/10.1016/j.biocon.2025.111250), [WorldCover](https://doi.org/10.5281/zenodo.7254221).

#### Slide 22: Other taxa show a similar across–within contrast

**39 seconds. Talk clock 13:16–13:55.**

Plants and Lepidoptera show a similar across-versus-within contrast. The regional coefficients are positive, and within-ecoregion estimates are much smaller. However, plant samples are incomplete and corrected Lepidoptera richness retains an effort signal. Their coefficient sizes cannot be compared as if they measured biological importance on an equal basis. Bird and plant richness also agree only weakly about where diversity is high. One taxon remains an imperfect biodiversity indicator.

**Unspoken visual cue:** Blue is across-region and terracotta within-ecoregion. Whiskers show approximate 95% intervals. Different record pools and completeness limit comparisons of coefficient sizes.

**Preparation sources:** [Wolters](https://doi.org/10.1890/0012-9658(2006)87[1886:RATSRO]2.0.CO;2), [Meyer](https://doi.org/10.1111/ele.12624), [Daru](https://doi.org/10.1111/nph.14855), [Wolters](https://doi.org/10.1890/0012-9658(2006)87[1886:RATSRO]2.0.CO;2), [Meyer](https://doi.org/10.1111/ele.12624), [Wolters](https://doi.org/10.1890/0012-9658(2006)87[1886:RATSRO]2.0.CO;2), [Meyer](https://doi.org/10.1111/ele.12624).

#### Slide 23: The apparent stability link weakens after adjustment

**39 seconds. Talk clock 13:55–14:34.**

This graph uses instability, so a negative coefficient means steadier annual GPP. Experiments motivate this question. The raw apparent stability relationship weakens after climate variability and mean GPP adjustments; within ecoregions, neither birds nor plants show a clear independent association. There is an important qualification: adjusting for mean GPP could remove a pathway through which diversity affects stability. MODIS GPP also uses meteorological inputs. We therefore interpret this dataset and adjustment sequence, rather than reject experimental stability mechanisms.

**Unspoken visual cue:** Outcome is log instability based on detrended annual variability relative to the mean. Negative means steadier GPP. Explain each adjustment before interpreting a sign.

**Preparation sources:** [Tilman](https://doi.org/10.1038/nature04742), [Isbell](https://doi.org/10.1038/nature15374), [Oehri](https://doi.org/10.1073/pnas.1703928114).

#### Slide 24: Protected-area results remain inconclusive

**38 seconds. Talk clock 14:34–15:12.**

Protection has three questions: recording effort, richness and the richness–GPP interaction. Database concerns require smaller subsets excluding India and China. Recording concentration is suggestive, and a raw richness advantage weakens after effort correction. The interaction is unclear. The extracted strict protected share and the official broader total use different definitions, so their mismatch is a warning rather than a like-for-like estimate. We cannot conclude that protection has no ecological benefit. Raunak will finish with monitoring implications and our conclusions.

**Unspoken visual cue:** All displayed F1–F3 subset comparisons exclude India and China. At 0.5°, raw richness beta is +0.150 (p=0.015) and corrected is +0.096 (p=0.15). The strict extracted share and official broader share use different definitions.

**Preparation sources:** [WDPA](https://www.protectedplanet.net/en/thematic-areas/wdpa), [WII](https://web.archive.org/web/20260113182611/https://wiienvis.nic.in/Database/Protected_Area_854.aspx).

## Raunak: Monitoring, conclusion, reproducibility, local application and claims

**Slides 25–30. Allocation 3:48. Target 15:12–19:00. 444 spoken words.**

### Mini preparation guide — do not read aloud

- Your job is to close the argument and explain what someone can use. Start with monitoring gaps, state the conclusion, then explain reproducibility and the Telangana proposal before the final claims.
- Know the difference between record-frequency coverage, ecological completeness and conservation value. Explain why 46 eligible cells still lack observations.
- Reproducibility counts are the recorded 17 November run, not a claim that slides themselves reran the full analysis. Cached-data reproduction differs from live source extraction.
- For Medak, know what Nasam et al. measured, what our proposed adaptation would add and why plot-to-pixel alignment matters. This is future work, not a completed replication.
- Use the direction diagram to explain shared climate and the invalid instrument. Finish on supported association claims; do not infer causation, India-wide results, carbon stocks or a protection effect.

### Exact spoken script

#### Slide 25: Recording gaps remain geographically concentrated

**32 seconds. Talk clock 15:12–15:44.**

The first map describes record-frequency coverage; the second helps identify survey priorities. Forty-six natural-cover cells lack enough records for the main model, with geographic clustering. Correction improves available comparisons but cannot replace missing observations. High coverage does not mean every rare species or habitat patch is known. The priority map guides further checking and surveys; it is not a conservation-value ranking.

**Unspoken visual cue:** First panel: record-frequency-weighted coverage. Second: survey-priority aid combining estimated missing coverage and expected richness. High priority is not high conservation value.

**Preparation sources:** [Chao](https://doi.org/10.1890/11-1952.1), [Hughes](https://doi.org/10.1111/ecog.05926), [CBD](https://www.cbd.int/gbf/targets/21), [CBD](https://www.cbd.int/gbf/targets/21).

#### Slide 26: Conclusion: answer to the research question

**36 seconds. Talk clock 15:44–16:20.**

Our conclusion is qualified support for a positive association. Survey effort strongly affects raw species lists. Comparing within ecoregions and allowing flexible climate responses reduces the larger regional estimate. A small positive bird association remains in several half-degree analyses. This fits the literature on shared environmental drivers and spatial scale. It does not contradict plant-diversity experiments, which study different mechanisms. The practical outcome is a more careful comparison of occurrence data with productivity, with uncertainty attached.

**Preparation sources:** [Chase](https://doi.org/10.1038/416427a), [Grace](https://doi.org/10.1038/nature16524), [Gonzalez](https://doi.org/10.1111/ele.13456), [Hughes](https://doi.org/10.1111/ecog.05926).

#### Slide 27: Reproducibility and open research outputs

**44 seconds. Talk clock 16:20–17:04.**

The workflow is reproducible from cached inputs. The recorded November seventeenth run completed all 34 analysis scripts and passed 73 headline checks; the suite contains 23 unit tests. We provide the joined dataset, codebook, plotted-value tables and two interactive atlases. GitHub automation runs the checks on pushes. Offline reruns use saved inputs; fresh GBIF and Earth Engine pulls need network access and appropriate credentials. Plant and Lepidoptera data citations remain separate unfinished tasks, and learner versions can affect flexible estimates.

**Unspoken visual cue:** Joined maps illustrate outputs. Counts refer to the cached run on 17 November 2026. The flat and terrain atlases are optional outputs, not live-demo requirements.

**Preparation sources:** [GBIF](https://doi.org/10.15468/dd.jf64nx), [Zenodo](https://doi.org/10.5281/zenodo.23264805), [MOD17](https://doi.org/10.5067/MODIS/MOD17A3HGF.061).

#### Slide 28: A local application: Medak forests, Telangana

**44 seconds. Talk clock 17:04–17:48.**

A local follow-up could focus on Medak, Telangana. Nasam and colleagues compared tree richness and carbon stocks in primary and regenerating forests. We propose combining suitable field diversity observations with satellite GPP, controlling stand structure, age, climate and spatial dependence. This needs accessible plot data and careful aggregation to forest patches that match satellite pixels. It is a future application, not a completed replication. Carbon stocks and annual GPP remain different outcomes, so their numbers cannot be compared directly.

**Unspoken visual cue:** The map is the published study-location figure, not a new survey. Existing data access and matching field plots to appropriate satellite support remain prerequisites.

**Preparation sources:** [Nasam](https://environmentandecology.com/wp-content/uploads/2024/05/MS15.pdf), [Chao](https://doi.org/10.1890/11-1952.1), [Running](https://doi.org/10.1641/0006-3568(2004)054[0547:ACSMOG]2.0.CO;2).

#### Slide 29: What we claim

**34 seconds. Talk clock 17:48–18:22.**

We claim that recording effort affects raw species lists, and that comparison scale and climate adjustment change the apparent richness–GPP association. Several finer-grid checks support a small positive bird association. We also identify limits to database coverage and provide a transparent workflow others can inspect. These claims apply to the comparisons shown. The common lesson is to state the spatial scale, controls and uncertainty whenever interpreting the relationship.

**Preparation sources:** [Chase](https://doi.org/10.1038/416427a), [Grace](https://doi.org/10.1038/nature16524), [Gonzalez](https://doi.org/10.1111/ele.13456), [Hughes](https://doi.org/10.1111/ecog.05926).

#### Slide 30: What we do not claim

**38 seconds. Talk clock 18:22–19:00.**

Finally, we do not claim that adding bird species causes more carbon uptake. Shared climate can affect both variables, the two causal directions fit the observations, and our attempted instrument fails its validity condition. We also make no India-wide estimate, carbon-stock inference, established protection-effect claim or conservation ranking from local slopes. Stronger evidence would need independent productivity observations and repeated biodiversity measurements or a stronger design. Our contribution is a defensible association analysis and a basis for follow-up. Thank you.

**Unspoken visual cue:** The diagram uses linear-control associations. Equivalent fits of opposite directions do not mean both causal paths are established. The topographic instrument also predicts GPP after controlling richness, so its exclusion condition fails.

**Preparation sources:** [Evans](https://doi.org/10.1017/S1464793104006517), [Hurlbert2004](https://doi.org/10.1111/j.1461-0248.2004.00630.x), [Grace](https://doi.org/10.1038/nature16524).

## Rehearsal and cross-question preparation

1. Practise once to the exact wording and time boundaries, then practise again using only the slide and cue.
2. Keep the main contrast precise: the larger linear regional association shrinks with flexible climate controls and within-ecoregion comparisons. Some finer-grid bird estimates remain small and positive.
3. Explain axes and uncertainty before interpreting a graph. Describe the result as an association.
4. Have a teammate interrupt with questions from [CROSS_QUESTIONS.md](CROSS_QUESTIONS.md). Give the short answer first; add detail only for the follow-up.
5. If time slips, use the shared one-minute reserve. Do not compensate by rushing all graphs or taking time from the next speaker. Do not add an unplanned live atlas demonstration.
6. After the closing sentence, move to references only for source lookup. The final appendix points to the repository.

## Local paper and replication boundary

Nasam, M. K., Bheemareeddyvalla, V. R., Vainala, V., Bathula, J., & Bodiga, S. (2022). *Influence of Assisted Natural Regeneration in increasing carbon stocks of Tropical deciduous forests*. Environment and Ecology, 40(1), 82–92. [Publisher PDF](https://environmentandecology.com/wp-content/uploads/2024/05/MS15.pdf); [FCRI institutional publication listing](https://fcrihyd.in/research/publications/index.htm).

Use its local management setting to propose an adaptation. The project has not acquired its raw observations or reproduced its findings. The field carbon-stock outcome and our annual GPP outcome require different interpretation.
