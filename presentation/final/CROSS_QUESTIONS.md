# Planet LOL: cross-question preparation

**75 demanding questions**, limited to the methods, evidence, application and claims shown in the presentation. This file supports the viva; it does not add a Q&A slide section. Read the short answer first, then practise the follow-up without looking.

The assigned lead owns the relevant presentation section, but every member should prepare the core finding, association/causation distinction and local-application limits. The final synthesis questions deliberately cross section boundaries.

## Category map

| Category | Questions |
|---|---|
| Background, literature and motivation | 1–6 |
| Hypotheses, study scope and source data | 7–12 |
| Coding workflow and richness standardisation | 13–20 |
| Models, uncertainty and spatial methodology | 21–27 |
| Core results and graph interpretation | 28–34 |
| Robustness and inference | 35–41 |
| Shape, landscapes, taxa, stability and protection | 42–51 |
| Monitoring, conclusion and reproducibility | 52–58 |
| Telangana application and its practical limits | 59–64 |
| Claims, alternative explanations and final defence | 65–69 |
| Integrated mock-viva challenges | 70–73 |
| Robustness follow-ups within the displayed checks | 74–75 |

## Background, literature and motivation

### 1. Why use birds if the proposed mechanism is plant complementarity?

**Slide 2 · lead: Vaibhavi.**

**Short answer:** Birds provide the strongest occurrence-record base in this project. Their richness is an indicator associated with environmental conditions; the main analysis does not test a direct producer-diversity mechanism. The plant extension is a complementary check.

**Follow-up / hypothetical:** If the plant result is similar, have you proved the mechanism? No. Similar observational patterns do not identify a plant-diversity treatment effect.

**Evidence / preparation:** [RESULTS_EXTENSION_D.md](../../docs/RESULTS_EXTENSION_D.md).

### 2. Can you compare GPP with carbon storage in the literature?

**Slide 2 · lead: Vaibhavi.**

**Short answer:** Compare the ecological questions and mechanisms, not their numerical values. GPP is annual gross carbon uptake; carbon stock is an accumulated amount. Stocks also reflect respiration, turnover, disturbance and history.

**Follow-up / hypothetical:** What if a site has high GPP but low stocks? That is possible: fast turnover or disturbance can prevent accumulation.

**Evidence / preparation:** [CODEBOOK.md](../../data/final/CODEBOOK.md).

### 3. Do Adler and Fraser contradict your result?

**Slide 3 · lead: Vaibhavi.**

**Short answer:** Their systems, sampling designs and prediction directions differ. They motivate testing shape and allowing weak relationships rather than requiring one universal curve. Our regional bird-richness/GPP analysis is a different comparison.

**Follow-up / hypothetical:** Could reversing a regression settle the disagreement? No. Reversing axes changes the conditional question and does not reproduce another study.

**Evidence / preparation:** [LITERATURE_NOTES.md](../../docs/LITERATURE_NOTES.md).

### 4. Which literature finding directly shaped your design?

**Slide 3 · lead: Vaibhavi.**

**Short answer:** Chase and the scaling literature motivate across/within and grain comparisons; Grace motivates environmental adjustment; sampling-bias papers motivate effort correction; Fraser motivates the curve test.

**Follow-up / hypothetical:** Which is closest to your remote-sensing design? Oehri offers a landscape comparison, but uses finer systematic plots and satellite proxies rather than identical data.

**Evidence / preparation:** [LITERATURE_NOTES.md](../../docs/LITERATURE_NOTES.md).

### 5. Does sampling bias mean citizen-science records cannot be used?

**Slide 4 · lead: Vaibhavi.**

**Short answer:** No. It means the observed list depends on recording as well as ecology. Standardisation, effort adjustment, completeness checks and transparent exclusions make comparisons more defensible without making them random surveys.

**Follow-up / hypothetical:** If effort correlation fell to exactly zero, would all bias disappear? No. Habitat and species preferences can remain without a simple marginal effort correlation.

**Evidence / preparation:** [RESULTS_EXTENSION_A.md](../../docs/RESULTS_EXTENSION_A.md).

### 6. What is new here, beyond combining familiar datasets?

**Slide 6 · lead: Vaibhavi.**

**Short answer:** The contribution is a traceable regional assessment that tests how sampling correction, flexible environment adjustment and spatial comparison alter the interpretation, with extensions and explicit limits. We make no first-ever claim.

**Follow-up / hypothetical:** Why are all extensions part of one project? Each challenges a specific part of the same richness–productivity interpretation.

**Evidence / preparation:** [DELIVERABLES_MAP.md](../../docs/DELIVERABLES_MAP.md).

## Hypotheses, study scope and source data

### 7. What exactly would count as support for your hypothesis?

**Slide 7 · lead: Deepraj.**

**Short answer:** A positive adjusted richness coefficient under the stated comparison, assessed with its uncertainty and robustness. Support is qualified because the estimate changes with scale and controls. It is not a claim that every model rejects a zero coefficient.

**Follow-up / hypothetical:** What is the null? Zero richness coefficient in the specified model. A directional alternative does not justify retrospectively choosing a favourable test.

**Evidence / preparation:** [RESULTS_ADJUDICATION.md](../../docs/RESULTS_ADJUDICATION.md).

### 8. Were all later checks original hypotheses?

**Slide 7 · lead: Deepraj.**

**Short answer:** No. The deck distinguishes the primary association expectation and extension questions from later exploratory inference checks. A transparent follow-up can be useful without calling it preregistered confirmation.

**Follow-up / hypothetical:** Does exploratory mean invalid? No, but interpretation should acknowledge model search and shared data.

**Evidence / preparation:** [DECISIONS.md](../../docs/DECISIONS.md).

### 9. Why combine occurrence records from 2000–2024 with 2019–2023 GPP?

**Slide 8 · lead: Deepraj.**

**Short answer:** The longer occurrence pool improves available records, while the environmental mean reduces single-year noise. This creates a mismatch, so matched-year refits are an important check rather than proof of perfect temporal alignment.

**Follow-up / hypothetical:** What changes when years are matched? Both measurement and sample eligibility can change; same-cell comparisons help separate them.

**Evidence / preparation:** [RESULTS_ADJUDICATION.md](../../docs/RESULTS_ADJUDICATION.md).

### 10. Why do 884 cells become only 221?

**Slide 10 · lead: Deepraj.**

**Short answer:** The stages are grid coverage, land availability, the dominant land-cover screen, and adequate species-identified records plus complete environmental data. The final sample is not a random selection of the original region.

**Follow-up / hypothetical:** Could exclusions change the answer? Yes. They define the target population and can change environmental support; the inference concerns retained cells.

**Evidence / preparation:** [RESULTS_EXTENSION_A.md](../../docs/RESULTS_EXTENSION_A.md).

### 11. Can you call this an India study?

**Slide 10 · lead: Deepraj.**

**Short answer:** Only 36% of modelled cells are in India. The full scope is South and Southeast Asia. Neither the regional coefficient nor the Medak proposal supplies a completed India-wide result.

**Follow-up / hypothetical:** Why does a Telangana application still make sense? It is a specific future adaptation of methods, not a geographical reinterpretation of the existing estimate.

**Evidence / preparation:** [HANDOFF.md](../../HANDOFF.md).

### 12. Does your natural-cover screen guarantee undisturbed forests?

**Slide 10 · lead: Deepraj.**

**Short answer:** No. It excludes cells dominated by cropland, built-up cover or water. Retained cells can include mixed habitats, disturbance and land use. It is a screen at the cell scale, not a forest-condition certificate.

**Follow-up / hypothetical:** What if a small intact forest lies in a crop-dominated cell? It can be excluded, illustrating why coarse screening can miss local forests.

**Evidence / preparation:** [merge_and_extA.py](../../scripts/merge_and_extA.py).

## Coding workflow and richness standardisation

### 13. How did the code obtain richness without downloading every record?

**Slide 9 · lead: Deepraj.**

**Short answer:** GBIF species-key facets return a vector of occurrence counts per species within each cell. That vector supports raw species counts and expected richness at a fixed number of records. The workflow checks facet limits rather than silently trusting a truncated list.

**Follow-up / hypothetical:** Are these biological abundances? No. They are recorded occurrences and can include uneven observation practices.

**Evidence / preparation:** [gbif_lib.py](../../scripts/gbif_lib.py).

### 14. Why use batches and caches instead of making all requests at once?

**Slide 9 · lead: Deepraj.**

**Short answer:** Batches limit payload and timeout problems; caches preserve completed work and make the subsequent analysis independent of repeated live requests. This improves recoverability and traceability.

**Follow-up / hypothetical:** Does a cached run refresh GBIF automatically? No. It reproduces the saved snapshot. Refreshing requires new queries and can change the data.

**Evidence / preparation:** [gee_extract_chunked.py](../../scripts/gee_extract_chunked.py).

### 15. How could a data-cleaning bug create a false ecological pattern?

**Slide 9 · lead: Deepraj.**

**Short answer:** Unmasked fill values can contaminate environmental means; wrong unit conversions alter scales; missing or mislabelled land-cover classes can admit inappropriate cells. The workflow checks these before joining and modelling.

**Follow-up / hypothetical:** Why not trust a visually plausible map? A plausible map does not verify valid values, units or correct joins.

**Evidence / preparation:** [VERIFICATION.md](../../docs/VERIFICATION.md).

### 16. What does a one-to-one cell-ID join protect against?

**Slide 9 · lead: Deepraj.**

**Short answer:** It checks that the input tables contribute one record per analytical cell. Duplicated keys can multiply rows and create false sample size or wrong associations. It does not itself verify geographic extraction quality.

**Follow-up / hypothetical:** What if keys match but coordinate systems differ? Matching keys would not fix a wrong extraction; the grid and spatial support still need validation.

**Evidence / preparation:** [merge_and_extA.py](../../scripts/merge_and_extA.py).

### 17. Why rarefy to 250 bird records?

**Slide 11 · lead: Deepraj.**

**Short answer:** A fixed count makes expected richness comparable across cells with different recording volumes. It is a design trade-off between retaining cells and retaining species information, rather than a universal ecological threshold.

**Follow-up / hypothetical:** What if the threshold rises? More information per cell but fewer eligible cells; changing the sample may alter the result.

**Evidence / preparation:** [gbif_lib.py](../../scripts/gbif_lib.py).

### 18. Why control effort after you already rarefied?

**Slide 11 · lead: Deepraj.**

**Short answer:** Rarefaction handles record-count differences in the observed pool. Observer preferences and remaining recording structure can persist, so the model retains log record count as an additional covariate. Neither adjustment guarantees all bias is removed.

**Follow-up / hypothetical:** Could effort adjustment remove ecological information? Yes. Effort can correlate with real richness; the interpretation is conditional on the chosen adjustment.

**Evidence / preparation:** [RESULTS_EXTENSION_A.md](../../docs/RESULTS_EXTENSION_A.md).

### 19. What does 95% sample coverage mean here?

**Slide 11 · lead: Deepraj.**

**Short answer:** It estimates the record-frequency mass belonging to already detected species under the sample model. It does not mean 95% of all species, habitats or individuals are known. Rare species can remain undetected.

**Follow-up / hypothetical:** What if a never-recorded species exists? The record-vector calculation cannot directly discover it.

**Evidence / preparation:** [coverage_rarefaction.py](../../scripts/coverage_rarefaction.py).

### 20. Are equal-size and equal-coverage comparisons equivalent?

**Slide 11 · lead: Deepraj.**

**Short answer:** No. Communities with different frequency distributions can have different completeness at the same number of records. Equal coverage addresses this difference, but cells unable to reach the chosen coverage without extrapolation are excluded.

**Follow-up / hypothetical:** Why use same-cell comparisons? To avoid attributing a change caused by sample selection entirely to the richness definition.

**Evidence / preparation:** [grain_0p5_sensitivity.py](../../scripts/grain_0p5_sensitivity.py).

## Models, uncertainty and spatial methodology

### 21. What does beta +0.07 mean?

**Slide 12 · lead: Deepraj.**

**Short answer:** Within its stated model, a one-standard-deviation richness difference is associated with about 0.07 standard deviations of GPP difference. It is not a 7% increase, a per-species gain or a causal treatment effect.

**Follow-up / hypothetical:** Can you compare standardised betas across unrelated samples directly? Only cautiously; outcome variance, support and data quality differ.

**Evidence / preparation:** [RESULTS_INFERENCE.md](../../docs/RESULTS_INFERENCE.md).

### 22. What do ecoregion fixed effects remove?

**Slide 12 · lead: Deepraj.**

**Short answer:** They remove differences in ecoregion means, leaving a comparison among cells within regions after the remaining controls. They do not remove all environmental variation or establish local causation.

**Follow-up / hypothetical:** Could a true broad-scale biological pathway also be removed? Yes. The estimand changes; the across and within coefficients answer different questions.

**Evidence / preparation:** [ecoregion_analysis.py](../../scripts/ecoregion_analysis.py).

### 23. How do random forests enter an association analysis?

**Slide 12 · lead: Deepraj.**

**Short answer:** They predict GPP and richness from controls in held-out folds. Regressing the two residuals estimates the remaining partially linear association. They permit nonlinear control responses rather than automatically discovering a causal relationship.

**Follow-up / hypothetical:** What if the learners underfit? Residual confounding can remain; a flexible label does not guarantee complete adjustment.

**Evidence / preparation:** [dml_flexible.py](../../scripts/dml_flexible.py).

### 24. Do robust or clustered standard errors change the ecological coefficient?

**Slide 12 · lead: Deepraj.**

**Short answer:** For a fixed OLS fit they change estimated uncertainty, not the point coefficient. Clustering permits dependence within groups under its assumptions. Spatial models or different covariates can change the point estimate because the model changes.

**Follow-up / hypothetical:** Why is this distinction important? A coefficient becoming non-significant after a different SE is not proof that its point association disappeared.

**Evidence / preparation:** [ecoregion_analysis.py](../../scripts/ecoregion_analysis.py).

### 25. Are spatial lag and spatial error models interchangeable?

**Slide 13 · lead: Ekansh.**

**Short answer:** No. A lag model includes spatial dependence in the outcome; an error model represents dependence in unexplained components. They impose different structures and can yield different richness estimates. The project uses further scale and validation checks to interpret the contrast.

**Follow-up / hypothetical:** Can the better AIC model prove the physical process? No. Relative fit under the tested candidates is not causal identification.

**Evidence / preparation:** [RESULTS_ADJUDICATION.md](../../docs/RESULTS_ADJUDICATION.md).

### 26. Why hold out geographic blocks rather than random cells?

**Slide 13 · lead: Ekansh.**

**Short answer:** Randomly separated cells can still be near environmental look-alikes in training data, giving optimistic transfer estimates. Blocked validation makes prediction geographically harder. It reduces leakage without proving total geographic independence.

**Follow-up / hypothetical:** What if block size doubles? Transfer becomes a different and often harder test, with fewer blocks and potentially wider uncertainty.

**Evidence / preparation:** [spatial_cv.py](../../scripts/spatial_cv.py).

### 27. Does the finer grid merely manufacture more independent observations?

**Slide 13 · lead: Ekansh.**

**Short answer:** More cells do not imply proportional independent information. Finer resolution changes mixtures and can help resolve a small association, while spatial dependence remains. We report uncertainty and compare patterns rather than treating all cells as independent.

**Follow-up / hypothetical:** Do overlapping intervals at 1° and 0.5° imply contradiction? No. One significant estimate and one non-significant estimate need not differ significantly.

**Evidence / preparation:** [RESULTS_ADJUDICATION.md](../../docs/RESULTS_ADJUDICATION.md).

## Core results and graph interpretation

### 28. Is the nearly flat corrected thinning curve partly built into the method?

**Slide 15 · lead: Ekansh.**

**Short answer:** Yes. Random thinning from the same observed pool is exactly a setting where fixed-size rarefaction should behave consistently. It is a useful implementation and count-sensitivity check, but not an independent test of real observer behaviour.

**Follow-up / hypothetical:** What if thinning selectively removed rare species? The random-thinning result would not guarantee stability under that biased removal.

**Evidence / preparation:** [RESULTS_EXTENSION_A.md](../../docs/RESULTS_EXTENSION_A.md).

### 29. Did every correction reduce the richness–GPP association?

**Slide 15 · lead: Ekansh.**

**Short answer:** No. Rarefaction and environmental adjustment are different operations. Correcting effort can improve the simple association; climate adjustment and within-region comparisons then reduce the larger regional coefficient. A single monotonic correction story would be misleading.

**Follow-up / hypothetical:** Why not compare the raw and corrected full models as a causal decomposition? Their samples and adjustments can differ; shared-cell checks are needed to isolate a change.

**Evidence / preparation:** [RESULTS_EXTENSION_A.md](../../docs/RESULTS_EXTENSION_A.md).

### 30. Does the one-degree within estimate establish no relationship?

**Slide 16 · lead: Ekansh.**

**Short answer:** No. Its uncertainty includes small effects the coarse sample cannot resolve. The finer-grid estimate is small and positive, and the intervals can be compatible across grains.

**Follow-up / hypothetical:** If p is 0.59, what can you say? The specified test does not reject zero; it does not assign a 59% probability that the null is true.

**Evidence / preparation:** [RESULTS_ADJUDICATION.md](../../docs/RESULTS_ADJUDICATION.md).

### 31. Why are +0.058 and +0.069 both on the slides?

**Slide 16 · lead: Ekansh.**

**Short answer:** The first is a finer-grid fixed-effect estimate; the second pools slopes from 35 sufficiently sampled ecoregions. They use different estimators and are not duplicate estimates required to be numerically identical.

**Follow-up / hypothetical:** Should you average them for a headline? No. Explain the estimators rather than forming an unplanned average of related fits.

**Evidence / preparation:** [RESULTS_INFERENCE.md](../../docs/RESULTS_INFERENCE.md).

### 32. Are all flexible estimates statistically significant?

**Slide 17 · lead: Ekansh.**

**Short answer:** No. At the finer grid the displayed across-region flexible estimates have borderline uncertainty; positive point estimates alone do not establish a clear sign. The slide shows intervals and the script qualifies them.

**Follow-up / hypothetical:** Can you choose the learner with the smallest p value? That would favour a selected result; report the comparison and its uncertainty.

**Evidence / preparation:** [RESULTS_INFERENCE.md](../../docs/RESULTS_INFERENCE.md).

### 33. Why does the flexible-control comparison start at +0.289 rather than +0.273?

**Slide 17 · lead: Ekansh.**

**Short answer:** It uses an expanded control set, complete-case selection and cross-fitting, rather than exactly the baseline specification. The comparison is within that analysis; it is not evidence that a coefficient was copied incorrectly.

**Follow-up / hypothetical:** What is the defensible comparison? Linear versus flexible adjustment using the same control/sample framework, while stating differences from the earlier baseline.

**Evidence / preparation:** [RESULTS_INFERENCE.md](../../docs/RESULTS_INFERENCE.md).

### 34. How can 221 cells be worth only about 36 independent observations?

**Slide 18 · lead: Ekansh.**

**Short answer:** Spatial similarity reduces independent information about the adjusted correlation. The effective-size calculation summarises that dependence under its assumptions. It does not literally discard 185 cells or supply a universal sample size for every estimator.

**Follow-up / hypothetical:** Does the 0.82 broad-band coefficient mean a large local causal effect? No. It is a band-specific comparison of broad patterns.

**Evidence / preparation:** [scale_decomposition.py](../../scripts/scale_decomposition.py).

## Robustness and inference

### 35. Are 960 fits equivalent to 960 independent replications?

**Slide 14 · lead: Ekansh.**

**Short answer:** No. They reuse the same observations across related choices. The specification curve shows sensitivity and the range of defensible modelling decisions, not independent evidence multiplied 960 times.

**Follow-up / hypothetical:** What if every model has the same omitted confounder? Agreement among them would not remove that shared bias.

**Evidence / preparation:** [RESULTS_SPEC_CURVE.md](../../docs/RESULTS_SPEC_CURVE.md).

### 36. Does reliability of 0.99 mean the richness measure is 99% ecologically correct?

**Slide 19 · lead: Devansh.**

**Short answer:** No. It estimates how much variation remains after the particular record-vector sampling-noise model. It does not quantify habitat preference, absent species, identification errors or all sources of ecological measurement error.

**Follow-up / hypothetical:** Could systematic bias coexist with high reliability? Yes. A consistently biased measure can be precise.

**Evidence / preparation:** [RESULTS_INFERENCE.md](../../docs/RESULTS_INFERENCE.md).

### 37. What does SIMEX test and what does it assume?

**Slide 14 · lead: Ekansh.**

**Short answer:** It adds simulated measurement noise, fits how the estimated slope changes, and extrapolates towards zero noise. Here it checks attenuation from estimated sampling error. Its interpretation depends on the assumed error process.

**Follow-up / hypothetical:** Would it fix observers repeatedly choosing easy habitats? Not unless that systematic selection were appropriately modelled; the current sampling-error check does not.

**Evidence / preparation:** [measurement_error.py](../../scripts/measurement_error.py).

### 38. How is an equivalence test different from a usual zero-effect test?

**Slide 19 · lead: Devansh.**

**Short answer:** It asks whether an effect is sufficiently small relative to a stated bound. Failure to reject zero does not establish smallness; the bounds procedure addresses that separate question.

**Follow-up / hypothetical:** Why say less than half the linear across estimate? That is the stated relative benchmark. It does not prove the within coefficient is less than half every flexible coefficient.

**Evidence / preparation:** [within_effect_bounds.py](../../scripts/within_effect_bounds.py).

### 39. Are the five equivalence-test samples independent?

**Slide 19 · lead: Devansh.**

**Short answer:** No. They share geography and observations. The project reports their results alongside one another rather than treating them as five independent experiments to pool.

**Follow-up / hypothetical:** Could the tighter 0.10 bound be established everywhere? No. Some samples lack enough information for that tighter claim.

**Evidence / preparation:** [RESULTS_INFERENCE.md](../../docs/RESULTS_INFERENCE.md).

### 40. Does matched-year agreement solve temporal causation?

**Slide 19 · lead: Devansh.**

**Short answer:** No. It reduces one mismatch between occurrence and GPP windows while retaining an observational comparison. It does not create a biodiversity time series, random intervention or before/after design.

**Follow-up / hypothetical:** What if the sign changed only because fewer cells were retained? Compare the same cells under both record windows before attributing the change to time matching.

**Evidence / preparation:** [grain_0p5_sensitivity.py](../../scripts/grain_0p5_sensitivity.py).

### 41. Can the pooled ecoregion slope represent every region?

**Slide 19 · lead: Devansh.**

**Short answer:** No. Pooling summarises estimates from sufficiently sampled ecoregions while individual slopes and uncertainty vary. It supports an average association under that procedure, not a universal positive slope.

**Follow-up / hypothetical:** Does selecting the most positive ecoregion identify a conservation priority? No. Extremes involve uncertainty and multiple comparisons, and slope is not conservation value.

**Evidence / preparation:** [within_effect_bounds.py](../../scripts/within_effect_bounds.py).

## Shape, landscapes, taxa, stability and protection

### 42. Why reject a hump when the one-degree spline bends down?

**Slide 20 · lead: Devansh.**

**Short answer:** A bend in one fitted curve is insufficient. Direct upper-tail slopes remain positive and the finer-grid curve does not reproduce the downturn. The conclusion concerns the observed range, not every possible ecosystem or richness level.

**Follow-up / hypothetical:** What if richer places exist outside your data? The current range cannot establish their relationship shape.

**Evidence / preparation:** [RESULTS_EXTENSION_B.md](../../docs/RESULTS_EXTENSION_B.md).

### 43. Can a more flexible curve always fit better?

**Slide 20 · lead: Devansh.**

**Short answer:** It can reduce in-sample residual error by using more flexibility, so model comparison must account for complexity. The project compares fit with an information criterion and checks the pattern across grains and upper-tail fits.

**Follow-up / hypothetical:** Does AIC establish a biological law? No. It compares specified candidate fits to these data.

**Evidence / preparation:** [RESULTS_EXTENSION_B.md](../../docs/RESULTS_EXTENSION_B.md).

### 44. Why did you replace the Deccan with the Thar?

**Slide 21 · lead: Devansh.**

**Short answer:** All land cells in the original Deccan project box failed the dominant natural-cover rule. The Thar supplied a dry contrast with eligible cells. This is a declared design substitution, not evidence that the whole Deccan lacks forests.

**Follow-up / hypothetical:** Does the exclusion conflict with Medak forests existing? No. Coarse crop-dominated cells can contain local forest patches.

**Evidence / preparation:** [RESULTS_EXTENSION_C.md](../../docs/RESULTS_EXTENSION_C.md).

### 45. Does the corrected landscape ranking prove the Eastern Himalaya is more biodiverse?

**Slide 21 · lead: Devansh.**

**Short answer:** It ranks expected richness in the stated record-standardised grid-cell comparison. It does not establish total biodiversity across all taxa, habitats or unsampled species. Case samples are small and the regions differ environmentally.

**Follow-up / hypothetical:** Could a different region boundary change ranks? Yes. The boundaries and sample composition define the comparison.

**Evidence / preparation:** [RESULTS_EXTENSION_C.md](../../docs/RESULTS_EXTENSION_C.md).

### 46. Why not conclude butterflies have the strongest ecological effect?

**Slide 22 · lead: Devansh.**

**Short answer:** Their larger standardised regional coefficient comes from a different, sparse record base with residual effort correlation. Different completeness and sample support prevent a clean biological-effect ranking.

**Follow-up / hypothetical:** Does within-region imprecision establish no butterfly association? No. Wide intervals leave substantial uncertainty.

**Evidence / preparation:** [RESULTS_EXTENSION_D.md](../../docs/RESULTS_EXTENSION_D.md).

### 47. Can bird richness serve as a substitute for plant richness?

**Slide 22 · lead: Devansh.**

**Short answer:** Only imperfectly. Their corrected spatial agreement is weak in this dataset, and they represent different ecological groups and observation communities. One taxon cannot represent all biodiversity.

**Follow-up / hypothetical:** If both have the same across/within contrast, what is strengthened? Generality of that descriptive contrast, not full taxonomic equivalence or causation.

**Evidence / preparation:** [RESULTS_EXTENSION_D.md](../../docs/RESULTS_EXTENSION_D.md).

### 48. Does a positive instability coefficient mean diversity is harmful?

**Slide 23 · lead: Devansh.**

**Short answer:** Not as a causal claim. The sign describes a conditional association under the stated outcome and adjustment sequence. Negative values mean steadier GPP; controls and conditioning affect what variation remains.

**Follow-up / hypothetical:** Could adjusting mean GPP remove a diversity pathway? Yes. The deck explicitly carries that qualification.

**Evidence / preparation:** [RESULTS_EXTENSION_E.md](../../docs/RESULTS_EXTENSION_E.md).

### 49. Are you contradicting diversity–stability experiments?

**Slide 23 · lead: Devansh.**

**Short answer:** No. Those experiments manipulate communities at different scales. Our coarse-cell outcome uses modelled GPP and a pooled richness estimate, with climate and mean-GPP adjustment. Its unclear within association does not refute experimental insurance mechanisms.

**Follow-up / hypothetical:** Do you measure biodiversity stability each year? No. Richness is pooled; annual observations concern GPP.

**Evidence / preparation:** [RESULTS_EXTENSION_E.md](../../docs/RESULTS_EXTENSION_E.md).

### 50. Why exclude India and China, and can you generalise that subset back to India?

**Slide 24 · lead: Devansh.**

**Short answer:** The protection extract has serious completeness/comparability concerns. The subset tests are a limited diagnostic, with 93 cells at 1° and 289 at 0.5°. They cannot identify an Indian protection effect.

**Follow-up / hypothetical:** Is 0.2% versus 5.69% a direct estimate of missing parks? No. Definitions and spatial coverage differ; the mismatch is a warning requiring closer data checks.

**Evidence / preparation:** [RESULTS_EXTENSION_F.md](../../docs/RESULTS_EXTENSION_F.md).

### 51. What do F1, F2 and F3 jointly show?

**Slide 24 · lead: Devansh.**

**Short answer:** F1 suggests recording concentration under some definitions, F2 shows a raw richness association that weakens after correction, and F3 finds no clear interaction. These are suggestive, data-limited patterns rather than a causal protection result.

**Follow-up / hypothetical:** If F3 is non-significant, does protection not matter? No. An imprecise interaction and database problems do not establish no ecological benefit.

**Evidence / preparation:** [RESULTS_EXTENSION_F.md](../../docs/RESULTS_EXTENSION_F.md).

## Monitoring, conclusion and reproducibility

### 52. Is a high survey-priority score a conservation priority?

**Slide 25 · lead: Raunak.**

**Short answer:** No. The score combines incomplete record coverage with expected richness as a sampling aid. Conservation priority requires additional objectives and information not tested here.

**Follow-up / hypothetical:** Could high coverage hide unvisited habitats? Yes. Record-frequency completeness at the cell level does not guarantee spatial or rare-species completeness.

**Evidence / preparation:** [RESULTS_SURVEY_GAPS.md](../../docs/RESULTS_SURVEY_GAPS.md).

### 53. Why not predict richness for the 46 missing cells and include those values in the main regression?

**Slide 25 · lead: Raunak.**

**Short answer:** Doing so would substitute model predictions for independent biodiversity observations and could mechanically reproduce environmental relationships used in prediction. The map is an aid for further sampling, not a replacement outcome or predictor dataset.

**Follow-up / hypothetical:** Could predictions still be useful? Yes, for directing independent validation or surveys, with prediction uncertainty.

**Evidence / preparation:** [RESULTS_SURVEY_GAPS.md](../../docs/RESULTS_SURVEY_GAPS.md).

### 54. What is your one-sentence answer?

**Slide 26 · lead: Raunak.**

**Short answer:** There is a positive regional association, but its magnitude falls with effort-aware comparison, flexible climate adjustment and spatial scale checks; several finer-grid bird analyses retain a small positive association whose direction is unidentified.

**Follow-up / hypothetical:** Which number should you avoid giving alone? The +0.273 linear regional estimate, because it omits the qualifications central to the finding.

**Evidence / preparation:** [RESULTS_INFERENCE.md](../../docs/RESULTS_INFERENCE.md).

### 55. What exactly can someone reproduce without an Earth Engine account?

**Slide 27 · lead: Raunak.**

**Short answer:** The analysis from committed cached inputs: joined tables, model fits and figure outputs. Live source extraction is different and needs network access plus the appropriate Earth Engine setup.

**Follow-up / hypothetical:** Will rerunning cached analysis refresh protected-area boundaries? No. It reuses the stored extract.

**Evidence / preparation:** [reproduce_all.py](../../scripts/reproduce_all.py).

### 56. What do 73 checks and 23 unit tests prove?

**Slide 27 · lead: Raunak.**

**Short answer:** The checks compare recorded headline outputs and the tests exercise selected computational behaviour. They catch specified failures; they do not prove ecological assumptions, absence of bias or every possible bug. Counts are from the documented workflow, not an accuracy score.

**Follow-up / hypothetical:** Could every test pass with the wrong causal interpretation? Yes. Statistical and ecological interpretation needs separate review.

**Evidence / preparation:** [test_core.py](../../tests/test_core.py).

### 57. Why might a flexible estimate differ slightly on another computer?

**Slide 27 · lead: Raunak.**

**Short answer:** Tree-learner implementation and package versions can change results. The reproduction check gives some learner outputs a wider tolerance; data snapshots, versions and the overall inference should be documented.

**Follow-up / hypothetical:** Is a large unexpected difference acceptable? No. It should trigger investigation of versions, inputs, seeds and the model specification.

**Evidence / preparation:** [reproduce_all.py](../../scripts/reproduce_all.py).

### 58. Does the bird-data DOI cover the plant and Lepidoptera records?

**Slide 27 · lead: Raunak.**

**Short answer:** No. They need their own data citations or registered records. The presentation explicitly notes that this task remains unfinished; the existing bird DOI must not be used as if it covered all taxa.

**Follow-up / hypothetical:** Does the code archive make raw-input attribution unnecessary? No. Source data and software outputs have different citation roles.

**Evidence / preparation:** [TODO.md](../../docs/TODO.md).

## Telangana application and its practical limits

### 59. Why choose the Medak paper instead of another international example?

**Slide 28 · lead: Raunak.**

**Short answer:** It provides a specific Telangana forest-management setting involving diversity and carbon-related measurements, and the full paper is accessible. It supports a concrete adaptation of the workflow rather than proving the regional result applies locally.

**Follow-up / hypothetical:** Would proximity alone make it a good fit? No. The ecological question, available data and compatible measurements must also fit.

**Evidence / preparation:** [MS15.pdf](https://environmentandecology.com/wp-content/uploads/2024/05/MS15.pdf).

### 60. Have you reproduced the Medak paper?

**Slide 28 · lead: Raunak.**

**Short answer:** No. The slide presents a proposed follow-up. Access to raw counts, locations and suitable observations must be established before claiming a local replication or result.

**Follow-up / hypothetical:** Could published group averages replace raw plot data? Not for the proposed spatial/diversity analysis without checking the required information and independent units.

**Evidence / preparation:** [FINAL_EVAL_REVISION_PLAN.md](../../presentation/FINAL_EVAL_REVISION_PLAN.md).

### 61. How would a small field plot match a satellite GPP pixel?

**Slide 28 · lead: Raunak.**

**Short answer:** It does not automatically match. A defensible design would align adequate sampling with suitable forest patches/pixels, verify habitat mixtures and boundaries, and avoid treating repeated plots assigned one pixel value as independent GPP observations.

**Follow-up / hypothetical:** What if several plots fall in one pixel? Aggregate or model the shared support appropriately; do not multiply the independent productivity sample size.

**Evidence / preparation:** [FINAL_EVAL_REVISION_PLAN.md](../../presentation/FINAL_EVAL_REVISION_PLAN.md).

### 62. Can you reuse the existing one-degree coefficient for individual Medak plots?

**Slide 28 · lead: Raunak.**

**Short answer:** No. That would transfer a different-scale association to local units without validation. A local adaptation needs appropriate sampling support, sufficient independent patches and its own uncertainty analysis.

**Follow-up / hypothetical:** Does using 0.5° solve the mismatch? It remains far coarser than small plots or 500-m productivity pixels.

**Evidence / preparation:** [FINAL_EVAL_REVISION_PLAN.md](../../presentation/FINAL_EVAL_REVISION_PLAN.md).

### 63. Why account for stand age and structure in the proposed follow-up?

**Slide 28 · lead: Raunak.**

**Short answer:** Forest history and structure can relate to both diversity and productivity/carbon outcomes. The adaptation would measure them and define the intended conditional comparison. Conditioning choices still need ecological justification.

**Follow-up / hypothetical:** Could controlling a mediator hide a pathway? Yes. State whether the aim is a total relationship or one conditional on structure rather than adding controls mechanically.

**Evidence / preparation:** [FINAL_EVAL_REVISION_PLAN.md](../../presentation/FINAL_EVAL_REVISION_PLAN.md).

### 64. Could the proposed comparison prove assisted regeneration causes higher GPP?

**Slide 28 · lead: Raunak.**

**Short answer:** Not simply from observing primary and regenerating forests. Non-random site selection, history and shared drivers remain. A stronger repeated or comparative design and independent outcomes would be needed for a causal claim.

**Follow-up / hypothetical:** Can carbon-stock numbers validate GPP numerically? No. Accumulated stock and annual gross uptake are different quantities.

**Evidence / preparation:** [FINAL_EVAL_REVISION_PLAN.md](../../presentation/FINAL_EVAL_REVISION_PLAN.md).

## Claims, alternative explanations and final defence

### 65. If climate explains much of the pattern, is the biodiversity project pointless?

**Slide 29 · lead: Raunak.**

**Short answer:** No. Quantifying how the interpretation changes is useful evidence. It prevents an inflated universal claim, identifies a remaining small association under several comparisons and improves monitoring practice.

**Follow-up / hypothetical:** What would be misleading? Advertising only the largest coefficient or calling a smaller association proof of no biodiversity relevance.

**Evidence / preparation:** [PAPER_CLAIMS.md](../../docs/PAPER_CLAIMS.md).

### 66. Why can the two causal directions fit equally well?

**Slide 30 · lead: Raunak.**

**Short answer:** In this observational setup the fitted associations do not identify direction. Shared climate and other drivers can generate the same relationship; a reverse regression is not an independent causal experiment.

**Follow-up / hypothetical:** Does plant complementarity theory settle the bird direction? No. Biological plausibility informs hypotheses but does not identify this observational estimate.

**Evidence / preparation:** [RESULTS_DIRECTION.md](../../docs/RESULTS_DIRECTION.md).

### 67. Why did the proposed topographic instrument fail?

**Slide 30 · lead: Raunak.**

**Short answer:** It still predicted GPP with richness held fixed, contradicting the required exclusion condition that it affect the outcome only through richness in this design. Its relevance for richness alone was insufficient.

**Follow-up / hypothetical:** Can you report its estimate as suggestive causation anyway? No. A failed validity condition prevents that interpretation.

**Evidence / preparation:** [RESULTS_DIRECTION.md](../../docs/RESULTS_DIRECTION.md).

### 68. What new evidence would most improve the conclusion?

**Slide 30 · lead: Raunak.**

**Short answer:** Independent productivity observations and repeated biodiversity measurements, combined with a stronger design for direction. The proposed local study would also need appropriate spatial support and accessible data before it could contribute.

**Follow-up / hypothetical:** Would another cross-sectional map automatically solve causation? No. It could test generality while leaving direction unresolved.

**Evidence / preparation:** [PAPER_CLAIMS.md](../../docs/PAPER_CLAIMS.md).

### 69. Why refuse an India-wide or protection-effect claim when these topics appear in the deck?

**Slide 30 · lead: Raunak.**

**Short answer:** The analytical sample is regional and selected, and the protection comparison has incomplete/non-comparable inputs. Including a topic and finding limits does not mean the data support the stronger policy claim.

**Follow-up / hypothetical:** What is the positive practical claim? The workflow makes sampling and interpretation more transparent and identifies where independent monitoring is needed.

**Evidence / preparation:** [PAPER_CLAIMS.md](../../docs/PAPER_CLAIMS.md).

## Integrated mock-viva challenges

### 70. Your estimates change with every method. Why should we trust any conclusion?

**Slide 29 · lead: Raunak.**

**Short answer:** The methods deliberately change the comparison and assumptions. The stable conclusion is the reduction of the large linear regional association and the small positive bird association under several finer-grid checks, with uncertainty. We do not promise one invariant coefficient.

**Follow-up / hypothetical:** Which change is a contradiction rather than a different estimand? Check whether the same sample, outcome, controls and estimator are being compared before deciding.

**Evidence / preparation:** [RESULTS_INFERENCE.md](../../docs/RESULTS_INFERENCE.md).

### 71. You have a significant finer-grid slope and high reliability. Why not claim a precise biological effect?

**Slide 19 · lead: Devansh.**

**Short answer:** Sampling precision and a nonzero conditional coefficient do not establish validity of all controls, absence of selection bias or causal direction. High reliability addresses one noise model; the effect-size bounds and design limits remain essential.

**Follow-up / hypothetical:** What if the omitted driver operates inside ecoregions? Fixed effects would not remove its within-region variation.

**Evidence / preparation:** [RESULTS_INFERENCE.md](../../docs/RESULTS_INFERENCE.md).

### 72. Suppose the protection interaction became significant after fixing the polygons. What could you then claim?

**Slide 24 · lead: Devansh.**

**Short answer:** A clearer conditional association under the corrected data and tested model, with multiplicity, sample support and uncertainty considered. Non-random protection placement would still block a simple causal interpretation.

**Follow-up / hypothetical:** Would a changed sign mean this presentation was dishonest? No, if the present inconclusive result and input limitations were accurately stated.

**Evidence / preparation:** [RESULTS_EXTENSION_F.md](../../docs/RESULTS_EXTENSION_F.md).

### 73. Suppose Medak forests show the opposite local association. Does your regional project fail?

**Slide 28 · lead: Raunak.**

**Short answer:** Not automatically. The local system, spatial support, taxa, controls and outcome differ. It would test transfer and motivate examination of context rather than justify silently replacing the regional finding.

**Follow-up / hypothetical:** What is the first check? Verify that the local outcome is annual GPP, that sampling support is comparable and that the effective sample is independent enough for the proposed inference.

**Evidence / preparation:** [FINAL_EVAL_REVISION_PLAN.md](../../presentation/FINAL_EVAL_REVISION_PLAN.md).

## Robustness follow-ups within the displayed checks

### 74. Does the NPP sensitivity result prove species–energy causation?

**Slide 19 · lead: Devansh.**

**Short answer:** No. NPP is a different flux, net of plant respiration, and has a stronger association in the spatial-error check. MOD17 models respiration using temperature, so part of the stronger pattern can reflect product construction. NDVI/EVI instead describe greenness.

**Follow-up / hypothetical:** Can these outcomes be averaged into one effect? No. They have different meanings and models; report them as sensitivity checks.

**Evidence / preparation:** [RESULTS_ADJUDICATION.md](../../docs/RESULTS_ADJUDICATION.md).

### 75. How did you check collinearity, and does a low VIF prove no confounding?

**Slide 9 · lead: Deepraj.**

**Short answer:** VIF diagnoses linear overlap among predictors. Baseline VIFs are low, while adding temperature and elevation together creates strong collinearity between those controls. Neither low VIF nor high predictor precision rules out an omitted confounder.

**Follow-up / hypothetical:** Does high temperature/elevation VIF imply the richness coefficient is necessarily unstable? Not automatically; diagnose the relevant predictor and specification rather than applying one number to every coefficient.

**Evidence / preparation:** [RESULTS_ADJUDICATION.md](../../docs/RESULTS_ADJUDICATION.md).

## Answer discipline

- Give the answer before the qualification. Use the qualification to bound the claim, not to avoid answering.
- State which model, grid and sample you mean before quoting a number.
- A positive point estimate, a significant coefficient, predictive transfer, reliability and causation are different claims.
- If the question asks for an analysis not performed, say so and describe the evidence needed. Do not invent a result.
- Keep technical follow-ups attached to the displayed method or finding; do not introduce an unrelated algorithm or new extension.
