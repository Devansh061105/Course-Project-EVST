# Planet LOL: five-person speaking split

**35 slides total. No Q&A section and no hidden slides.** Slides 1–28 form the spoken presentation. Slides 29–34 contain the linked references and slide 35 credits the images. Display references after the conclusion without reading every entry.

**Target: 22 minutes 30 seconds**, leaving 2 minutes 30 seconds within the 25-minute slot for pauses or slower explanations. Q&A is separate. Every person receives **4 minutes 30 seconds**. The first three sections contain six slides, and the last two contain five slides with more interpretation.

## Division of speaking and preparation

| Person | Slides | Clock | Responsibility |
|---|---|---|---|
| 1 | 1–6 | 0:00–4:30 | Introduction and literature review |
| 2 | 7–12 | 4:30–9:00 | Objectives, data and methods |
| 3 | 13–18 | 9:00–13:30 | Core results and robustness |
| 4 | 19–23 | 13:30–18:00 | Shape, landscapes and ecological extensions |
| 5 | 24–28 | 18:00–22:30 | Protection, interpretation and conclusion |

Assign names to these five roles before rehearsing. These are presentation and preparation responsibilities; describe research contributions according to the team’s actual work.

Each person should check the sources for their section, practise every graph explanation, and rehearse to the section boundary. Use the slide text as prompts, with the PowerPoint notes for fuller detail. Do not try to read every note aloud.

## Person 1: Introduction and literature review

**Slides 1–6. 4 minutes 30 seconds.**

Define the question and key terms; compare supportive, conflicting and regional literature; explain the sampling-bias gap.

### Slide 1: Biodiversity and ecosystem productivity

Target **18 seconds**. Talk clock **0:00–0:18**.

- Explain: Our project asks whether places with more species are also more productive after accounting for uneven survey effort. We studied South and Southeast Asia using citizen-science records and satellite data.
- Sources to know: [GBIF](https://doi.org/10.15468/dd.jf64nx), [MOD17](https://doi.org/10.5067/MODIS/MOD17A3HGF.061).

### Slide 2: Species richness, productivity and stored carbon

Target **33 seconds**. Talk clock **0:18–0:51**.

- Explain: First, two definitions. Species richness means the number of species.
- Main point: Our response variable is annual GPP, measured in kg C per m² per year.
- Sources to know: [Running](https://doi.org/10.1641/0006-3568(2004)054[0547:ACSMOG]2.0.CO;2), [Hurlbert](https://doi.org/10.2307/1934145), [Chen](https://doi.org/10.1038/s41586-023-05941-9), [CBD](https://www.cbd.int/gbf/targets/21).

### Slide 3: Literature review: evidence for a positive link

Target **63 seconds**. Talk clock **0:51–1:54**.

- Explain: The literature gives good reasons to expect a positive relationship. Liang and colleagues analysed permanent forest plots worldwide and reported a positive relationship that becomes less steep as tree richness increases.
- Main point: These studies motivate the hypothesis. Their measures and spatial scales differ from ours.
- Sources to know: [Liang](https://doi.org/10.1126/science.aaf8957), [Duffy](https://doi.org/10.1038/nature23886), [Oehri](https://doi.org/10.1073/pnas.1703928114), [Deng](https://doi.org/10.1073/pnas.2506750122).

### Slide 4: Literature review: why findings differ

Target **63 seconds**. Talk clock **1:54–2:57**.

- Explain: The literature does not give one universal curve. Adler and colleagues used standardised sampling across herbaceous communities and found that productivity was a poor predictor of plant richness.
- Main point: Different ecosystems, response variables and comparison scales can produce different answers.
- Sources to know: [Adler](https://doi.org/10.1126/science.1204498), [Fraser](https://doi.org/10.1126/science.aab3916), [Grace](https://doi.org/10.1038/nature16524), [Chase](https://doi.org/10.1038/416427a), [Gonzalez](https://doi.org/10.1111/ele.13456).

### Slide 5: Literature review: regional carbon evidence

Target **48 seconds**. Talk clock **2:57–3:45**.

- Explain: Western Ghats studies connect carbon storage with forest structure, environmental conditions and tree diversity. Kothandaraman and colleagues show why structure and environment must be considered together.
- Main point: Our analysis measures annual GPP. Carbon-storage studies provide context, not directly comparable values.
- Sources to know: [Kothandaraman](https://doi.org/10.1038/s41598-020-70313-6), [Najeeb](https://doi.org/10.1016/j.biocon.2025.111250), [Ramachandra](https://doi.org/10.1007/s11053-019-09588-0), [Chen](https://doi.org/10.1038/s41586-023-05941-9), [Oehri2020](https://doi.org/10.1038/s41467-019-14002-7).

### Slide 6: Literature review: uneven records can mislead

Target **45 seconds**. Talk clock **3:45–4:30**.

- Explain: A second literature concerns the data themselves. Beck and colleagues document spatial bias in GBIF records.
- Main point: We combine effort correction, satellite GPP and spatial checks in one regional test.
- Sources to know: [Beck](https://doi.org/10.1016/j.ecoinf.2013.11.002), [Engemann](https://doi.org/10.1002/ece3.1405), [Hughes](https://doi.org/10.1111/ecog.05926), [ElGabbas](https://doi.org/10.1111/ddi.70205).

**Handover / close:** “The literature explains our expectations and the main sources of bias. Next, we explain how our study tests them.”

## Person 2: Objectives, data and methods

**Slides 7–12. 4 minutes 30 seconds.**

Explain the six extensions, study-area selection, source periods, rarefaction, models and spatial validation.

### Slide 7: Research question and objectives

Target **37 seconds**. Talk clock **4:30–5:07**.

- Explain: Our hypothesis is that effort-corrected richness remains positively associated with GPP after climate adjustment and screening out cells dominated by cropland, built-up land or water. Birds form the main analysis because they have the strongest record coverage.
- Main point: The study tests an association. It does not assume a causal direction.
- Sources to know: [Grace](https://doi.org/10.1038/nature16524), [Chase](https://doi.org/10.1038/416427a), [Hurlbert](https://doi.org/10.2307/1934145).

### Slide 8: Study area and sample selection

Target **41 seconds**. Talk clock **5:07–5:48**.

- Explain: The map shows our one-degree grid over South and Southeast Asia. We start with 884 cells, of which 630 contain land-cover data.
- Main point: 221 modelled cells at 1°. Only 36% are in India.
- Sources to know: [WorldCover](https://doi.org/10.5281/zenodo.7254221), [Resolve](https://doi.org/10.1093/biosci/bix014), [GBIF](https://doi.org/10.15468/dd.jf64nx).

### Slide 9: Data sources and study periods

Target **41 seconds**. Talk clock **5:48–6:29**.

- Explain: We join several sources by grid cell. GBIF provides species occurrence counts and the number of records used as an effort measure.
- Main point: Stability uses annual GPP for 2001–2023. Protection uses the November 2026 WDPA extract.
- Sources to know: [GBIF](https://doi.org/10.15468/dd.jf64nx), [MOD17](https://doi.org/10.5067/MODIS/MOD17A3HGF.061), [ERA](https://doi.org/10.5194/essd-13-4349-2021), [WorldCover](https://doi.org/10.5281/zenodo.7254221), [Resolve](https://doi.org/10.1093/biosci/bix014), [SRTM](https://doi.org/10.5067/MEaSUREs/SRTM/SRTMGL1.003), [MOD13](https://doi.org/10.5067/MODIS/MOD13Q1.061).

### Slide 10: Comparing cells at equal sampling effort

Target **63 seconds**. Talk clock **6:29–7:32**.

- Explain: Rarefaction asks a simple question: if we drew the same number of records from each cell, how many species would we expect? Imagine one place with thousands of records and another with only a few hundred.
- Main point: Equal sample size improves comparability, but it cannot remove every observer preference.
- Sources to know: [Hurlbert](https://doi.org/10.2307/1934145), [Chao](https://doi.org/10.1890/11-1952.1).

### Slide 11: Models and validation

Target **41 seconds**. Talk clock **7:32–8:13**.

- Explain: The first model compares cells across the full region while controlling effort and climate. The second compares cells within the same ecoregion, removing differences in regional averages.
- Main point: β is the change in GPP, in standard deviations, for a one-SD difference in richness. Intervals show uncertainty.
- Sources to know: [Grace](https://doi.org/10.1038/nature16524), [Roberts](https://doi.org/10.1111/ecog.02881), [Ploton](https://doi.org/10.1038/s41467-020-18321-y), [Resolve](https://doi.org/10.1093/biosci/bix014).

### Slide 12: Spatial dependence and predictive transfer

Target **47 seconds**. Talk clock **8:13–9:00**.

- Explain: Nearby cells share climate, habitats and recording patterns. The initial Moran spatial correlation is about 0.72.
- Main point: Geographic validation tests transfer to new places and gives a stricter test than random folds.
- Visual explanation: Explain that the horizontal axis is distance between cells and the vertical axis is residual spatial similarity. The ecoregion-adjusted line removes much of the broad pattern.
- Sources to know: [Hawkins](https://doi.org/10.1111/j.0906-7590.2007.05117.x), [Kissling](https://doi.org/10.1111/j.1466-8238.2007.00334.x), [Roberts](https://doi.org/10.1111/ecog.02881), [Ploton](https://doi.org/10.1038/s41467-020-18321-y).

**Handover / close:** “With that design in place, we can now see how correction, climate and scale change the results.”

## Person 3: Core results and robustness

**Slides 13–18. 4 minutes 30 seconds.**

Explain thinning, across/within comparisons, flexible climate controls, spatial scales, specification checks and matched-year results.

### Slide 13: Sampling correction reduces the effort signal

Target **41 seconds**. Talk clock **9:00–9:41**.

- Explain: This graph tests the correction by taking well-recorded cells and randomly throwing records away. The horizontal axis shows the number retained, at ordered sampling levels.
- Main point: At 250 retained records: raw richness keeps 23%, corrected richness keeps about 100%.
- Visual explanation: Read both axes. Corrected richness stays near one after thinning, while raw richness declines. Contrast effort correlations 0.81 and 0.24.
- Sources to know: [Hurlbert](https://doi.org/10.2307/1934145), [Hughes](https://doi.org/10.1111/ecog.05926).

### Slide 14: The association is weaker within ecoregions

Target **52 seconds**. Talk clock **9:41–10:33**.

- Explain: Read each bar as a coefficient and each horizontal line as its 95 percent interval. Blue represents the across-region estimate, and terracotta the within-ecoregion estimate.
- Main point: A small positive association remains within ecoregions at 0.5°.
- Visual explanation: Explain blue versus terracotta, the coefficient axis and 95% intervals. Emphasise a smaller within-region association, with a small positive result at 0.5°.
- Sources to know: [Chase](https://doi.org/10.1038/416427a), [Gonzalez](https://doi.org/10.1111/ele.13456), [Resolve](https://doi.org/10.1093/biosci/bix014).

### Slide 15: Flexible climate controls reduce the estimate

Target **52 seconds**. Talk clock **10:33–11:25**.

- Explain: Here we ask whether straight-line climate controls leave environmental structure in the richness coefficient. The graph compares a linear adjustment with two flexible learners, random forests and gradient boosting.
- Main point: Across-region estimates fall to about +0.14–0.17 at 1° and +0.07 at 0.5°.
- Visual explanation: Explain why straight-line climate controls can leave structure behind. Read the smaller flexible estimates and their uncertainty.
- Sources to know: [DML](https://doi.org/10.1111/ectj.12097), [Grace](https://doi.org/10.1038/nature16524).

### Slide 16: The largest association is at broad spatial scales

Target **44 seconds**. Talk clock **11:25–12:09**.

- Explain: This analysis separates the map into broad and fine spatial patterns without using ecoregion borders. The horizontal axis identifies the scale band, and the vertical axis shows its richness–GPP coefficient.
- Main point: The broadest spatial patterns span roughly 700–800 km.
- Visual explanation: Explain broad versus fine spatial bands. The 221 cells supply about 36 independent observations under the stated calculation.
- Sources to know: [Dray](https://doi.org/10.1016/j.ecolmodel.2006.02.015), [Clifford](https://doi.org/10.2307/2532039), [Chase](https://doi.org/10.1038/416427a).

### Slide 17: The pattern survives many analysis choices

Target **33 seconds**. Talk clock **12:09–12:42**.

- Explain: We also vary reasonable analysis choices rather than selecting one favourable model. The chart shows the median coefficient across 320 specifications for each estimator.
- Main point: Across-region coefficients remain larger across 960 related specifications.
- Visual explanation: Bars are medians from related fits, not independent replications. Explain why the across-region coefficient stays larger.
- Sources to know: [Simonsohn](https://doi.org/10.1038/s41562-020-0912-z), [Chao](https://doi.org/10.1890/11-1952.1).

### Slide 18: Robustness: coverage and matched observation years

Target **48 seconds**. Talk clock **12:42–13:30**.

- Explain: These checks address two remaining concerns. Equal record counts can still have different sample completeness, so we also compare richness at equal coverage.
- Main point: A small positive within-ecoregion association persists under alternative richness definitions.
- Visual explanation: Compare equal-coverage and matched-year rows. Use the same-cell rows to distinguish sample changes from changes in richness measurement.
- Sources to know: [Chao](https://doi.org/10.1890/11-1952.1), [Hurlbert](https://doi.org/10.2307/1934145).

**Handover / close:** “The main contrast persists across the robustness checks. Next, we examine shape, landscapes and other ecological outcomes.”

## Person 4: Shape, landscapes and ecological extensions

**Slides 19–23. 4 minutes 30 seconds.**

Explain curve shape, the three landscape examples, local windows, other taxa and temporal stability.

### Slide 19: No convincing evidence of a hump

Target **50 seconds**. Talk clock **13:30–14:20**.

- Explain: Extension B tests the shape suggested by the literature debate. The horizontal axis is adjusted richness and the vertical axis is fitted GPP, both standardised.
- Main point: The 1° curve bends, but the decline at the top does not replicate at 0.5°.
- Visual explanation: Explain adjusted richness and fitted GPP axes. A bend in a fitted curve does not establish a negative upper-tail slope.
- Sources to know: [Fraser](https://doi.org/10.1126/science.aab3916), [Liang](https://doi.org/10.1126/science.aaf8957), [Gonzalez](https://doi.org/10.1111/ele.13456).

### Slide 20: Three landscapes show why correction matters

Target **77 seconds**. Talk clock **14:20–15:37**.

- Explain: The photographs provide landscape context, while the numbers come from our grid cells. The Western Ghats have the highest annual GPP among the three case-study boxes.
- Main point: The Eastern Himalaya ranks first after correction.
- Visual explanation: Photographs illustrate habitats. Numerical ranks and GPP come from grid cells. Explain the corrected ranking and the small 7/8/24-cell samples.
- Sources to know: [Kothandaraman](https://doi.org/10.1038/s41598-020-70313-6), [Najeeb](https://doi.org/10.1016/j.biocon.2025.111250), [WorldCover](https://doi.org/10.5281/zenodo.7254221).

### Slide 21: Local estimates change with the comparison window

Target **41 seconds**. Talk clock **15:37–16:18**.

- Explain: The main graph shows the 0.5-degree grid. Instead of using named ecoregions, this analysis fits a model around each cell and changes the size of the neighbourhood.
- Main point: Local-slope maps are descriptive and cannot rank conservation benefits.
- Visual explanation: Read window radius and median coefficient. Larger windows recover a more regional comparison. Local maps do not rank conservation returns.
- Sources to know: [Brunsdon](https://doi.org/10.1111/j.1538-4632.1996.tb00936.x), [Chase](https://doi.org/10.1038/416427a), [Brunsdon](https://doi.org/10.1111/j.1538-4632.1996.tb00936.x).

### Slide 22: Other taxa show a similar across–within contrast

Target **59 seconds**. Talk clock **16:18–17:17**.

- Explain: Extension D checks whether the main pattern is specific to birds. In this graph, blue bars compare across regions and terracotta bars compare within ecoregions.
- Main point: Other taxa repeat the contrast, with greater data limitations.
- Visual explanation: Explain across/within contrasts, 95% intervals and why incomplete records limit comparisons of coefficient sizes between taxa.
- Sources to know: [Wolters](https://doi.org/10.1890/0012-9658(2006)87[1886:RATSRO]2.0.CO;2), [Meyer](https://doi.org/10.1111/ele.12624), [Daru](https://doi.org/10.1111/nph.14855), [Wolters](https://doi.org/10.1890/0012-9658(2006)87[1886:RATSRO]2.0.CO;2), [Meyer](https://doi.org/10.1111/ele.12624).

### Slide 23: The apparent stability link weakens after adjustment

Target **43 seconds**. Talk clock **17:17–18:00**.

- Explain: Earlier experiments and the Swiss landscape study motivated a stability question. Our outcome here is instability, measured as detrended year-to-year variation divided by mean GPP, so a negative coefficient indicates steadier production.
- Main point: Within ecoregions, neither bird nor plant richness shows a clear independent stability association.
- Visual explanation: Negative coefficients indicate steadier annual GPP. Explain climate/mean-GPP adjustments and the caveat that mean GPP might be part of a pathway.
- Sources to know: [Tilman](https://doi.org/10.1038/nature04742), [Isbell](https://doi.org/10.1038/nature15374), [Oehri](https://doi.org/10.1073/pnas.1703928114).

**Handover / close:** “These extensions show how context changes the interpretation. We will finish with protection, limitations and the overall answer.”

## Person 5: Protection, interpretation and conclusion

**Slides 24–28. 4 minutes 30 seconds.**

Explain protection-data limitations, causal direction, recording gaps, reproducibility and conclusions connected to the literature.

### Slide 24: Protected-area results remain inconclusive

Target **45 seconds**. Talk clock **18:00–18:45**.

- Explain: Extension F examines whether the richness–productivity relationship differs with protected land. Its main finding concerns data quality.
- Main point: The available data cannot establish a protection effect.
- Sources to know: [WDPA](https://www.protectedplanet.net/en/thematic-areas/wdpa), [WII](https://web.archive.org/web/20260113182611/https://wiienvis.nic.in/Database/Protected_Area_854.aspx).

### Slide 25: The data do not establish causal direction

Target **59 seconds**. Talk clock **18:45–19:44**.

- Explain: The literature offers two directions. Plant diversity may improve production through complementarity.
- Main point: Causal direction remains open.
- Visual explanation: Explain shared climate and the two possible directions. The attempted instrument fails its validity condition.
- Sources to know: [Evans](https://doi.org/10.1017/S1464793104006517), [Hurlbert2004](https://doi.org/10.1111/j.1461-0248.2004.00630.x), [Grace](https://doi.org/10.1038/nature16524).

### Slide 26: Recording gaps remain geographically concentrated

Target **59 seconds**. Talk clock **19:44–20:43**.

- Explain: This map shows where the records remain thin. The first panel estimates sample coverage, and the second combines incomplete coverage with environmentally predicted richness as a survey-priority aid.
- Main point: Effort correction cannot replace observations in the 46 excluded cells.
- Visual explanation: Explain coverage versus survey-priority panels. Coverage is weighted by record frequencies and is not the fraction of all species known.
- Sources to know: [Chao](https://doi.org/10.1890/11-1952.1), [Hughes](https://doi.org/10.1111/ecog.05926), [CBD](https://www.cbd.int/gbf/targets/21).

### Slide 27: Open research outputs and reproducibility

Target **41 seconds**. Talk clock **20:43–21:24**.

- Explain: The project produces more than a regression result. We provide a joined per-cell dataset, a codebook and cached inputs so analyses can run without repeating live data queries.
- Main point: Plants and Lepidoptera still need their own registered data citations.
- Visual explanation: Show the joined maps and point to the atlas and repository links. Fine terrain is a display layer rather than a finer analysis.
- Sources to know: [GBIF](https://doi.org/10.15468/dd.jf64nx), [Zenodo](https://doi.org/10.5281/zenodo.23264805).

### Slide 28: Conclusions in relation to the literature

Target **66 seconds**. Talk clock **21:24–22:30**.

- Explain: We can now answer the question. Species richness and productivity are associated in this region, but the size depends on survey correction, climate modelling and the scale of comparison.
- Main point: Use corrected records for monitoring. Stronger causal claims need a different study design.
- Sources to know: [Chase](https://doi.org/10.1038/416427a), [Grace](https://doi.org/10.1038/nature16524), [Gonzalez](https://doi.org/10.1111/ele.13456), [Hughes](https://doi.org/10.1111/ecog.05926).

**Handover / close:** “Our conclusion is a scale-dependent association, with a small positive result at the finer grid. Stronger causal claims require a different design. Thank you.”

## Rehearsal priorities

- Keep the five section boundaries at 4:30, 9:00, 13:30, 18:00 and 22:30.
- Explain axes, the main pattern and one relevant limitation on each graph.
- Mention the key author and year when interpreting published evidence. All slide citations and bibliography links are clickable.
- Use “association” for observational results. Distinguish annual GPP from carbon stocks.
- Spend longer on the across/within and flexible-climate graphs; move briskly through source tables.
- The atlases are optional links. The embedded maps allow the talk to continue without a live demonstration.
- Finish the spoken talk on slide 28, then leave the references available for questions.
