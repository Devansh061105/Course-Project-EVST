# Mid-Evaluation Guide: Does Biodiversity Track Ecosystem Productivity?

*This guide covers exactly what the mid evaluation asks: **what the project is,
how we are approaching it, the literature and sources we use, the impact, and
the results we expect.** The short "early indications" box in section 7 is only
for if an examiner asks how far the work has got.*

---

## 1. The project in one minute (open with this)
> "We are testing whether places with more bird species are also more productive,
> meaning their plants fix more carbon, across South and Southeast Asia. We combine
> 71.7 million citizen-science bird records from GBIF with NASA satellite
> productivity data on a grid of 884 one-degree cells. The catch is that
> citizen-science records pile up where birdwatchers go. So the core of our
> approach is correcting for that sampling bias before asking the question, and
> showing how much the answer changes once we do."

## 2. What is the project?

### 2.1 The question
**Does biodiversity track ecosystem productivity at landscape scale, once the
uneven sampling of biodiversity data is corrected?**

### 2.2 Why ask it now
- **Policy.** In December 2022 the 196 Parties to the Convention on Biological
  Diversity adopted the **Kunming–Montreal Global Biodiversity Framework**
  (Decision 15/4). Its Target 19 commits to mobilising **at least USD 200 billion
  a year by 2030** for biodiversity. Part of the case for that money is that
  biodiverse ecosystems fix and store more carbon.
- **Economics.** The World Economic Forum estimates that **over half of world GDP
  (about $44 trillion)** depends moderately or highly on nature (WEF, 2020).
- **A scale gap in the evidence.** The best evidence that biodiversity raises
  productivity comes from experiments and forest plots. Conservation, however, is
  planned over landscapes and regions, so the question needs testing at that scale.
- **A data problem.** Citizen-science data (GBIF, eBird) are increasingly used to
  monitor biodiversity targets, but they are heavily biased towards accessible,
  well-surveyed places. How much that bias distorts conclusions is itself an open
  question.

### 2.3 Hypotheses
- **H1:** effort-corrected biodiversity is positively associated with
  productivity (gross primary productivity, GPP) after controlling for climate and
  restricting to natural land cover.
- **H0:** no meaningful association remains once sampling effort, climate and
  land cover are accounted for.

*Framing note:* we test an **association**. Whether biodiversity *causes* higher
productivity, or productivity supports more species, is a question our design
can inform but not settle (section 7).

### 2.4 Three extensions
| | Question | Why it matters |
|---|---|---|
| **A** Naive vs corrected | How different is the answer with raw species counts versus effort-corrected richness? | Shows directly how much citizen-science bias changes conclusions |
| **B** Linear vs hump | Does productivity rise steadily with diversity, or peak and fall? | A live debate in the literature (section 4) |
| **C** Three case studies | Does the pattern hold in contrasting landscapes: Western Ghats (wet forest hotspot), Thar Desert (arid), Eastern Himalaya (high diversity, under-sampled)? | Tests whether a regional pattern holds on the ground |

### 2.5 Scope
| Item | Detail |
|---|---|
| Region | 5–31°N, 68–102°E: South and Southeast Asia (India, southern China, Myanmar, Thailand, Pakistan, Nepal, Bangladesh, Sri Lanka and others) |
| Unit | 1° × 1° grid cells (~111 km), 884 cells, 630 on land |
| Biodiversity | Birds (class Aves), the most consistently recorded group |
| Period | Bird records 2000–2024; satellite and climate averages 2019–2023 |

## 3. How we are approaching it

### 3.1 The pipeline
<div class="flow">
<div class="step"><b>1 · Grid</b><span>884 one-degree cells over the study region</span></div>
<div class="step"><b>2 · Bird data</b><span>GBIF records per cell: total records and the species list with counts</span></div>
<div class="step"><b>3 · Bias correction</b><span>Rarefaction: expected species in an equal sample of 250 records; effort kept as a covariate</span></div>
<div class="step"><b>4 · Satellite &amp; climate</b><span>MODIS productivity, ERA5-Land temperature and rainfall, ESA land cover, via Google Earth Engine</span></div>
<div class="step"><b>5 · Mask &amp; merge</b><span>Drop cropland, built-up and water cells; join everything per cell</span></div>
<div class="step"><b>6 · Models</b><span>Naive vs corrected regression (A); linear vs quadratic (B)</span></div>
<div class="step"><b>7 · Spatial checks</b><span>Moran's I, spatial models, clustering by ecoregion, other grid sizes</span></div>
<div class="step"><b>8 · Case studies</b><span>Western Ghats, Thar Desert, Eastern Himalaya (C)</span></div>
<div class="step"><b>9 · Write-up</b><span>Report, policy implications, presentation</span></div>
</div>

### 3.2 Data sources
| Data | Provider | Resolution | Role |
|---|---|---|---|
| Bird occurrences | GBIF (98.8% of records come from eBird) | point records | Species richness and survey effort |
| GPP and NPP | NASA MODIS MOD17A3HGF v061 | 463 m, yearly | **Productivity** (the response variable) |
| NDVI and EVI | NASA MODIS MOD13Q1 v061 | 232 m, 16-day | Alternative productivity measures |
| Temperature, rainfall | ECMWF ERA5-Land | ~11 km, monthly | Climate controls |
| Land cover | ESA WorldCover v200 (2021) | 10 m | Removing cropland, cities and water |
| Elevation | NASA SRTM | 30 m | Topography as a control |
| Ecoregions | RESOLVE Ecoregions 2017 | polygons | Biogeographic units for clustering |

### 3.3 Methods, and why each one
| Method | What it does | Why we use it | Source |
|---|---|---|---|
| **Rarefaction** | Expected species count in a random sample of 250 records | Compares cells at equal survey effort, so heavily birded cells do not look richer just because they are watched more | Hurlbert (1971) |
| **Effort covariate** | Log of record count included in the regression | Current practice combines rarefaction with explicit effort | El-Gabbas (2026); Hughes et al. (2021) |
| **Coverage standardisation** (robustness) | Compares cells at equal sample completeness | Size-based rarefaction can distort differences between rich and poor communities | Chao & Jost (2012) |
| **Land-cover mask** | Keeps only natural-cover cells | Farm productivity reflects irrigation and fertiliser, not ecology | Plan, Step 4 |
| **Climate controls** | Temperature and rainfall in the model | Climate drives both diversity and productivity | Grace et al. (2016) |
| **Regression with robust errors** | OLS with heteroskedasticity-robust standard errors | Ecological data rarely have constant variance | Plan, Step 6 |
| **Linear vs quadratic (AIC)** | Compares a straight line with a curve | Tests the hump-shaped hypothesis directly | Fraser et al. (2015); Liang et al. (2016) |
| **Spatial autocorrelation checks** | Moran's I; spatial lag and spatial error models | Neighbouring cells are not independent; ignoring this inflates significance | Ploton et al. (2020); Kissling & Carl (2008) |
| **Clustering by ecoregion** | Standard errors that allow correlation within biogeographic units | The plan asks for clustering "by biogeographic sub-region" | Dinerstein et al. (2017) |
| **Spatial block cross-validation** | Tests prediction on whole held-out regions | Random cross-validation is over-optimistic for spatial data | Roberts et al. (2017) |
| **Grid-size robustness** | Repeats at 0.5° and 2° | Results should not hinge on one grid | Plan, Step 8; Gonzalez et al. (2020) |

### 3.4 Tools
| Tool | Used for | Why |
|---|---|---|
| Python (pandas, numpy) | All data handling | Standard and readable by the whole team |
| GBIF occurrence API | Bird records per cell | Free, global, no login. One request per cell returns the full species list with counts. |
| Google Earth Engine | Satellite, climate and land-cover values per cell | Processes terabytes of imagery on Google's servers; free for academic use |
| statsmodels | Regression, robust and clustered errors | Standard statistics library |
| PySAL (libpysal, esda, spreg) | Neighbour matrices, Moran's I, spatial regression | The standard Python spatial statistics toolkit |
| matplotlib | Maps and figures | Print-quality static figures |

### 3.5 Decisions made so far, and why
- **Birds, not plants:** a live check across the three case-study regions found
  about **200× more records per cell** for birds (e.g. Deccan median 29,642 vs 145).
  Plant richness could not be corrected reliably in most cells.
- **Thar Desert replaces the Deccan Plateau:** all 25 Deccan land cells are
  dominated by cropland (77% converted), so none remain after removing farmland.
  The Thar was chosen by a systematic scan as the driest region that is still
  largely natural. The Deccan's conversion is itself a finding about land use.
- **Water also removed:** the plan removed cropland and cities. Sea and lake cells
  were added to the mask, because they would otherwise enter as "natural" cells
  with near-zero productivity and create a false signal.
- **Ecoregions as the biogeographic units** for the plan's Step 8 clustering.

## 4. The literature we have used

### 4.1 How the literature is organised, and what it means for us
| Theme | Key studies | What they show | What it means for our design |
|---|---|---|---|
| **From experiments to real ecosystems** | Liang et al. 2016; Duffy et al. 2017; Chen et al. 2023; Deng et al. 2025 | Biodiversity is positively linked to productivity and carbon in real forests, not just experiments; canopy complexity is one mechanism | Our H1 expects a positive association |
| **The shape is disputed** | Adler et al. 2011; Fraser et al. 2015; Grace et al. 2016; Gonzalez et al. 2020 | Null, linear and hump-shaped results all exist; shared environmental drivers and spatial scale explain much of the disagreement | Extension B; climate controls; grid-size checks |
| **What "productivity" means** | Running et al. 2004; Liang et al. 2016; Chen et al. 2023; Kothandaraman et al. 2020 | Studies mix fluxes (GPP), growth rates and carbon stocks, which need not move together | We use a flux (GPP) and say so; NPP as a check |
| **Satellite productivity at landscape scale** | Running et al. 2004; Oehri et al. 2017, 2020 | Satellite productivity works as a biodiversity-study response, so far only with evenly sampled national inventories | Our design uses it with *unevenly* sampled data, which is the novelty |
| **Sampling bias in occurrence data** | Beck et al. 2014; Engemann et al. 2015; Hughes et al. 2021; Hurlbert 1971; El-Gabbas 2026; Ploton et al. 2020 | GBIF is strongly biased; raw richness tracks sampling intensity; corrections exist; spatial validation matters | Extension A; rarefaction plus effort covariate; spatial checks |
| **Regional evidence (Western Ghats)** | Kothandaraman et al. 2020; Najeeb et al. 2025; Ramachandra & Bharath 2020 | Diversity is linked to carbon storage, but stand structure matters more; all plot-based | Extension C; a grid-based regional test |

### 4.2 The gap we address
No study for this region combines **effort-corrected, citizen-science biodiversity**
with **satellite productivity** at grid-cell resolution, restricted to natural land
cover, while reporting **spatial diagnostics**. (The literature review states this
for South Asia; our grid also covers Southeast Asia.)

### 4.3 Theory and methods literature used in the approach
- **Spatial statistics:** Hawkins et al. (2007), Kissling & Carl (2008), Bini et
  al. (2009), Halleck Vega & Elhorst (2015), Roberts et al. (2017). They tell us how
  to model spatial dependence and how to validate predictions honestly.
- **Scale and species pools:** Chase & Leibold (2002), Ricklefs (1987), Cornell &
  Harrison (2014). The same relationship can look different between and within
  regions, because regional species pools differ.
- **Species–energy theory:** Evans et al. (2005), Hurlbert (2004), Coops et al.
  (2009). The leading *alternative* explanation: productive places support more
  bird species, rather than the reverse.
- **Habitat heterogeneity:** Stein et al. (2014). Topographic variety raises
  richness, so it is a control.
- **Coverage-based rarefaction:** Chao & Jost (2012).

*Every reference in this guide was checked against Crossref for existence and
details, and its abstract was read.*

## 5. Sources and full citations

### 5.1 Literature review (the 20 submitted references)
1. Adler, P. B., Seabloom, E. W., Borer, E. T., Hillebrand, H., Hautier, Y., Hector, A., … Yang, L. H. (2011). Productivity is a poor predictor of plant species richness. *Science, 333*(6050), 1750–1753. https://doi.org/10.1126/science.1204498
2. Beck, J., Böller, M., Erhardt, A., & Schwanghart, W. (2014). Spatial bias in the GBIF database and its effect on modeling species' geographic distributions. *Ecological Informatics, 19*, 10–15. https://doi.org/10.1016/j.ecoinf.2013.11.002
3. Chen, X., Taylor, A. R., Reich, P. B., Hisano, M., Chen, H. Y. H., & Chang, S. X. (2023). Tree diversity increases decadal forest soil carbon and nitrogen accrual. *Nature, 618*(7963), 94–101. https://doi.org/10.1038/s41586-023-05941-9
4. Deng, X., Schmid, B., Bruelheide, H., Chen, C., Li, Y., Li, S., … Liu, X. (2025). Forest biodiversity increases productivity via complementarity from greater canopy structural complexity. *Proceedings of the National Academy of Sciences, 122*(40), e2506750122. https://doi.org/10.1073/pnas.2506750122
5. Duffy, J. E., Godwin, C. M., & Cardinale, B. J. (2017). Biodiversity effects in the wild are common and as strong as key drivers of productivity. *Nature, 549*(7671), 261–264. https://doi.org/10.1038/nature23886
6. El-Gabbas, A. (2026). A global, taxon-stratified, high-resolution sampling-effort dataset from GBIF for bias-aware ecological modelling. *Diversity and Distributions, 32*(5), e70205. https://doi.org/10.1111/ddi.70205
7. Engemann, K., Enquist, B. J., Sandel, B., Boyle, B., Jørgensen, P. M., Morueta-Holme, N., Peet, R. K., & Violle, C. (2015). Limited sampling hampers "big data" estimation of species richness in a tropical biodiversity hotspot. *Ecology and Evolution, 5*(3), 807–820. https://doi.org/10.1002/ece3.1405
8. Fraser, L. H., Pither, J., Jentsch, A., Sternberg, M., Zobel, M., Askarizadeh, D., … Zupo, T. (2015). Worldwide evidence of a unimodal relationship between productivity and plant species richness. *Science, 349*(6245), 302–305. https://doi.org/10.1126/science.aab3916
9. Gonzalez, A., Germain, R. M., Srivastava, D. S., Filotas, E., Dee, L. E., Gravel, D., … Isbell, F. (2020). Scaling-up biodiversity-ecosystem functioning research. *Ecology Letters, 23*(4), 757–776. https://doi.org/10.1111/ele.13456
10. Grace, J. B., Anderson, T. M., Seabloom, E. W., Borer, E. T., Adler, P. B., Harpole, W. S., … Smith, M. D. (2016). Integrative modelling reveals mechanisms linking productivity and plant species richness. *Nature, 529*(7586), 390–393. https://doi.org/10.1038/nature16524
11. Hughes, A. C., Orr, M. C., Ma, K., Costello, M. J., Waller, J., Provoost, P., Yang, Q., Zhu, C., & Qiao, H. (2021). Sampling biases shape our view of the natural world. *Ecography, 44*(9), 1259–1269. https://doi.org/10.1111/ecog.05926
12. Hurlbert, S. H. (1971). The nonconcept of species diversity: A critique and alternative parameters. *Ecology, 52*(4), 577–586. https://doi.org/10.2307/1934145
13. Kothandaraman, S., Dar, J. A., Sundarapandian, S., Dayanandan, S., & Khan, M. L. (2020). Ecosystem-level carbon storage and its links to diversity, structural and environmental drivers in tropical forests of Western Ghats, India. *Scientific Reports, 10*, 13444. https://doi.org/10.1038/s41598-020-70313-6
14. Liang, J., Crowther, T. W., Picard, N., Wiser, S., Zhou, M., Alberti, G., … Reich, P. B. (2016). Positive biodiversity-productivity relationship predominant in global forests. *Science, 354*(6309), aaf8957. https://doi.org/10.1126/science.aaf8957
15. Najeeb, N., Jose, K., Sreejith, K., Pulla, S., Suresh, H., Ratnam, J., Raghavendra, H., & Chakravarthy, D. (2025). Presence of large trees and tree diversity enhances carbon storage in the Western Ghats. *Biological Conservation, 308*, 111250. https://doi.org/10.1016/j.biocon.2025.111250
16. Oehri, J., Schmid, B., Schaepman-Strub, G., & Niklaus, P. A. (2017). Biodiversity promotes primary productivity and growing season lengthening at the landscape scale. *Proceedings of the National Academy of Sciences, 114*(38), 10160–10165. https://doi.org/10.1073/pnas.1703928114
17. Oehri, J., Schmid, B., Schaepman-Strub, G., & Niklaus, P. A. (2020). Terrestrial land-cover type richness is positively linked to landscape-level functioning. *Nature Communications, 11*, 154. https://doi.org/10.1038/s41467-019-14002-7
18. Ploton, P., Mortier, F., Réjou-Méchain, M., Barbier, N., Picard, N., Rossi, V., Dormann, C., & Cornu, G. (2020). Spatial validation reveals poor predictive performance of large-scale ecological mapping models. *Nature Communications, 11*, 4540. https://doi.org/10.1038/s41467-020-18321-y
19. Ramachandra, T. V., & Bharath, S. (2020). Carbon sequestration potential of the forest ecosystems in the Western Ghats, a global biodiversity hotspot. *Natural Resources Research, 29*(4), 2753–2771. https://doi.org/10.1007/s11053-019-09588-0
20. Running, S. W., Nemani, R. R., Heinsch, F. A., Zhao, M., Reeves, M., & Hashimoto, H. (2004). A continuous satellite-derived measure of global terrestrial primary production. *BioScience, 54*(6), 547–560. https://doi.org/10.1641/0006-3568(2004)054[0547:ACSMOG]2.0.CO;2

### 5.2 Theory and methods references
21. Bini, L. M., Diniz-Filho, J. A. F., Rangel, T. F. L. V. B., Akre, T. S. B., Albaladejo, R. G., Albuquerque, F. S., et al. (2009). Coefficient shifts in geographical ecology: An empirical evaluation of spatial and non-spatial regression. *Ecography, 32*(2), 193–204. https://doi.org/10.1111/j.1600-0587.2009.05717.x
22. Chao, A., & Jost, L. (2012). Coverage-based rarefaction and extrapolation: Standardizing samples by completeness rather than size. *Ecology, 93*(12), 2533–2547. https://doi.org/10.1890/11-1952.1
23. Chase, J. M., & Leibold, M. A. (2002). Spatial scale dictates the productivity–biodiversity relationship. *Nature, 416*(6879), 427–430. https://doi.org/10.1038/416427a
24. Coops, N. C., Waring, R. H., Wulder, M. A., Pidgeon, A. M., & Radeloff, V. C. (2009). Bird diversity: A predictable function of satellite-derived estimates of seasonal variation in canopy light absorbance across the United States. *Journal of Biogeography, 36*(5), 905–918. https://doi.org/10.1111/j.1365-2699.2008.02053.x
25. Cornell, H. V., & Harrison, S. P. (2014). What are species pools and when are they important? *Annual Review of Ecology, Evolution, and Systematics, 45*, 45–67. https://doi.org/10.1146/annurev-ecolsys-120213-091759
26. Evans, K. L., Warren, P. H., & Gaston, K. J. (2005). Species–energy relationships at the macroecological scale: A review of the mechanisms. *Biological Reviews, 80*(1), 1–25. https://doi.org/10.1017/s1464793104006517
27. Halleck Vega, S., & Elhorst, J. P. (2015). The SLX model. *Journal of Regional Science, 55*(3), 339–363. https://doi.org/10.1111/jors.12188
28. Hawkins, B. A., Diniz-Filho, J. A. F., Bini, L. M., De Marco, P., & Blackburn, T. M. (2007). Red herrings revisited: Spatial autocorrelation and parameter estimation in geographical ecology. *Ecography, 30*(3), 375–384. https://doi.org/10.1111/j.0906-7590.2007.05117.x
29. Hurlbert, A. H. (2004). Species–energy relationships and habitat complexity in bird communities. *Ecology Letters, 7*(8), 714–720. https://doi.org/10.1111/j.1461-0248.2004.00630.x
30. Kissling, W. D., & Carl, G. (2008). Spatial autocorrelation and the selection of simultaneous autoregressive models. *Global Ecology and Biogeography, 17*(1), 59–71. https://doi.org/10.1111/j.1466-8238.2007.00334.x
31. Ricklefs, R. E. (1987). Community diversity: Relative roles of local and regional processes. *Science, 235*(4785), 167–171. https://doi.org/10.1126/science.235.4785.167
32. Roberts, D. R., Bahn, V., Ciuti, S., Boyce, M. S., Elith, J., Guillera-Arroita, G., et al. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography, 40*(8), 913–929. https://doi.org/10.1111/ecog.02881
33. Stein, A., Gerstner, K., & Kreft, H. (2014). Environmental heterogeneity as a universal driver of species richness across taxa, biomes and spatial scales. *Ecology Letters, 17*(7), 866–880. https://doi.org/10.1111/ele.12277

### 5.3 Data sources
34. Didan, K. (2021). *MODIS/Terra Vegetation Indices 16-Day L3 Global 250m SIN Grid V061* [Data set]. NASA EOSDIS Land Processes DAAC. https://doi.org/10.5067/MODIS/MOD13Q1.061
35. Dinerstein, E., Olson, D., Joshi, A., Vynne, C., Burgess, N. D., Wikramanayake, E., et al. (2017). An ecoregion-based approach to protecting half the terrestrial realm. *BioScience, 67*(6), 534–545. https://doi.org/10.1093/biosci/bix014 (source of the ecoregion map)
36. Muñoz-Sabater, J., Dutra, E., Agustí-Panareda, A., et al. (2021). ERA5-Land: A state-of-the-art global reanalysis dataset for land applications. *Earth System Science Data, 13*(9), 4349–4383. https://doi.org/10.5194/essd-13-4349-2021
37. NASA JPL. (2013). *NASA Shuttle Radar Topography Mission Global 1 arc second* [Data set]. NASA EOSDIS Land Processes DAAC. https://doi.org/10.5067/MEaSUREs/SRTM/SRTMGL1.003
38. Running, S., & Zhao, M. (2021). *MODIS/Terra Net Primary Production Gap-Filled Yearly L4 Global 500m SIN Grid V061* [Data set]. NASA EOSDIS Land Processes DAAC. https://doi.org/10.5067/MODIS/MOD17A3HGF.061
39. Zanaga, D., Van De Kerchove, R., Daems, D., De Keersmaecker, W., et al. (2022). *ESA WorldCover 10 m 2021 v200* [Data set]. Zenodo. https://doi.org/10.5281/zenodo.7254221
40. GBIF.org (2026). GBIF occurrence data, Aves, 5–31°N 68–102°E, 2000–2024. **DOI to be registered** (see 5.5).

### 5.4 Policy sources (for the impact argument)
41. Convention on Biological Diversity. (2022). *Decision 15/4: Kunming–Montreal Global Biodiversity Framework* (CBD/COP/DEC/15/4). https://www.cbd.int/doc/decisions/cop-15/cop-15-dec-04-en.pdf
42. World Economic Forum. (2020). *Nature risk rising: Why the crisis engulfing nature matters for business and the economy.* https://www.weforum.org/publications/nature-risk-rising-why-the-crisis-engulfing-nature-matters-for-business-and-the-economy/

### 5.5 Source notes (know these before you are asked)
- **GBIF requires a citable DOI.** Our data came from live API queries, which do
  not create one. A DOI will be registered (a GBIF download or "derived dataset")
  before the final report.
- **Corrected from the plan:** the plan attributes "~55% of global GDP" to IUCN.
  The figure is the World Economic Forum's (2020): over half of world GDP,
  about $44 trillion.
- **Not used unless verified:** the plan also mentions a Carbon Brief article
  (journalism, not peer-reviewed) and an unnamed "2025 subtropical Chinese forest
  study". We have not identified or read the latter, so neither is cited.

## 6. Impact
| Level | Impact | Honest limit |
|---|---|---|
| **Scientific** | Tests a biodiversity–productivity claim at landscape scale, with open data, in an under-studied region containing two global biodiversity hotspots (Western Ghats, Eastern Himalaya) | Correlational: it can test whether the pattern exists and at what scale, not prove cause |
| **Methodological** | A reproducible open pipeline (GBIF + Google Earth Engine) that measures how much citizen-science bias changes the answer, with a fast way to get bias-correctable data per cell | Shown for birds, the best-recorded group; other taxa are likely worse |
| **Policy** | Evidence on whether the "biodiversity helps carbon uptake" argument behind biodiversity finance holds at the scale where money is spent | We measure carbon *uptake* (a flux), not carbon storage |
| **Monitoring** | The GBF tracks progress partly with citizen-science data. Showing the size of the bias, and correcting it, matters for how that monitoring is read | — |
| **Land use** | Shows how much natural cover remains for such comparisons, e.g. the Deccan Plateau is almost entirely converted to farmland | A 1° grid is coarse for local planning |

## 7. Expected results
Each expectation comes from the literature in section 4. The plan's risk table
treats a weak or null result as a valid finding, not a failure.

| # | We expect | Because | What would surprise us |
|---|---|---|---|
| 1 | **Raw species counts mostly reflect survey effort** | GBIF bias is strong and systematic (Beck 2014; Engemann 2015; Hughes 2021) | Raw and corrected richness telling the same story |
| 2 | **A positive association after correction, but weaker than the naive one** | Positive in real forests (Liang 2016; Duffy 2017; Oehri 2017), but climate drives both variables (Grace 2016) | No association at all, or a negative one |
| 3 | **Climate explains much of the raw pattern** | Shared environmental drivers (Grace 2016) | Richness mattering more than climate |
| 4 | **A straight or levelling-off line, not a hump** | Forest studies find positive, decelerating curves (Liang 2016; Deng 2025); the hump comes mainly from grasslands (Fraser 2015) | A clear hump |
| 5 | **Strong spatial autocorrelation** | Large-scale ecological maps nearly always show it (Ploton 2020; Hawkins 2007) | Independent residuals |
| 6 | **A stronger pattern between regions than within them** | Regional species pools and scale dependence (Ricklefs 1987; Chase & Leibold 2002; Gonzalez 2020) | The same strength within and between regions |
| 7 | **Case studies:** Western Ghats productive and species-rich; Thar low on both; the **Eastern Himalaya showing the biggest naive-vs-corrected gap** (under-sampled) | The plan's predictions; Western Ghats plot evidence (Kothandaraman 2020) | The ranking unchanged by correction |
| 8 | **Direction will stay open** | Birds are consumers; species–energy theory predicts productivity → richness (Evans 2005; Hurlbert 2004; Coops 2009) | — |

**What each outcome would mean**

- *Clear positive after correction* → supports biodiversity-based conservation
  arguments at landscape scale (as an association).
- *Weak, or mostly between regions* → the policy argument holds at best regionally,
  and is driven by species pools and climate.
- *Null* → valid and publishable. It would match the scale-dependence literature
  and caution against blanket "biodiversity = carbon" claims.

<div class="callout"><b>Early indications — only if asked how far you have got.</b>
The data are assembled and the first analyses are run. They are consistent with
expectations 1, 4, 5, 6 and 7. Raw richness correlates 0.81 with survey effort
(0.24 after correction). The corrected association is positive but much weaker
within ecoregions than between them. There is no hump. Spatial autocorrelation is
strong (Moran's I 0.72). The case-study ranking changes after correction. These
are preliminary and will be reported in full in the final report.</div>

## 8. Progress and next steps
- **Done:** grid; bird data (71.7 million records); bias correction; satellite,
  climate and land-cover extraction; merged dataset; first models; spatial checks;
  case studies; figures; literature review (submitted).
- **Next (weeks 7–8):** the written report and policy section; the presentation;
  registering the GBIF DOI; adding the policy sources (5.4) to the introduction;
  agreeing as a team how to frame H1 (association vs cause).

## 9. Questions you may be asked
**What is your project, in one sentence?**
Whether places with more bird species are also more productive across South and
Southeast Asia, once citizen-science sampling bias is corrected.

**What is new about it?**
Earlier landscape studies used evenly sampled national inventories (Oehri 2017).
We use globally available but biased citizen-science data, correct the bias, and
measure how much that correction changes the answer, in a region where this has
not been done.

**Why birds?**
They are the best-recorded group: about 200× more records per cell than plants in
our check. 98.8% of our records come from eBird.

**What is the main methodological challenge?**
Sampling bias: records concentrate where birdwatchers go. We use rarefaction
(compare cells at an equal sample of 250 records) plus survey effort as a
covariate.

**Why satellite GPP?**
It is the standard global, consistent measure of how much carbon plants fix each
year (Running et al. 2004). It is a flux, not a carbon stock, and we are explicit
about that.

**Why a 1° grid?**
Large enough that each cell has many records to correct for bias; small enough to
give hundreds of cells. We will check 0.5° and 2° as well.

**Why remove cropland?**
Farm productivity reflects irrigation and fertiliser, not natural ecology. We also
remove water.

**Why the Thar instead of the Deccan?**
Every Deccan cell is mostly farmland, so none survive the natural-land filter. The
Thar is the driest region that is still mostly natural.

**Which literature most shaped your design?**
Liang et al. (2016) and Duffy et al. (2017) for the expected positive link; Hughes
et al. (2021) and Engemann et al. (2015) for the bias problem; Fraser et al. (2015)
vs Liang et al. (2016) for Extension B; Ploton et al. (2020) for spatial checks.

**Is the relationship causal?**
We test association. Direction is open: species–energy theory suggests
productivity may support more bird species, rather than the reverse.

**What if you find no relationship?**
That is a valid result. The plan says so explicitly, and it would match the
scale-dependence literature (Gonzalez et al. 2020; Chase & Leibold 2002).

**What is the impact?**
It tests, at the scale where conservation money is spent, an argument used to
justify biodiversity finance. It also shows how much uncorrected citizen-science
data can mislead biodiversity monitoring.

**Are your data citable?**
All satellite and climate products have DOIs (section 5.3). GBIF requires a DOI
for our bird data, which we will register before the final report.

## 10. Short glossary
- **Species richness:** number of species.
- **Rarefaction:** expected species count at a fixed sample size (here, 250 records).
- **Survey effort:** number of records in a cell.
- **GPP / NPP:** carbon fixed by plants per year, before / after plant respiration.
- **Land-cover mask:** removing cells dominated by cropland, cities or water.
- **Spatial autocorrelation / Moran's I:** nearby cells being similar; Moran's I
  measures it (0 = none).
- **Ecoregion:** a biogeographic unit with a distinctive community of species.
- **AIC:** model-fit score penalising complexity; lower is better.
- **Association vs causation:** two things varying together vs one causing the other.
