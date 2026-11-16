# Literature notes for the analysis (verified 2026-10-06)

These are **in addition to** the 20 references in the submitted literature review
(`C:\downloads\Literature_Review_Biodiversity_Ecosystem_Productivity_v3.docx`).
Every entry below was checked against Crossref (existence, authors, venue, DOI)
**and** its abstract was read via Crossref, Semantic Scholar or Europe PMC. The
"claim used" column is limited to what the abstract supports. Do not cite these
for anything beyond that without reading the paper.

## Spatial modelling and inference
| reference | claim used |
|---|---|
| Hawkins, Diniz-Filho, Bini, De Marco & Blackburn (2007) Red herrings revisited: spatial autocorrelation and parameter estimation in geographical ecology. *Ecography* 30(3):375–384. doi:10.1111/j.0906-7590.2007.05117.x | Bird richness, 110×110 km cells: OLS coefficients statistically indistinguishable from those from spatially independent subsamples (22/22); OLS is unbiased; OLS–SAR shifts are expected when small-scale patterns make broad-scale coefficients weaker and unstable; interpret with explicit awareness of spatial scale. |
| Kissling & Carl (2008) Spatial autocorrelation and the selection of simultaneous autoregressive models. *Global Ecology and Biogeography* 17(1):59–71. doi:10.1111/j.1466-8238.2007.00334.x | SAR-error models the most reliable across all simulated autocorrelation structures; OLS, SAR-lag and SAR-mixed showed weak type I error control and/or unpredictable bias. Crossref lists the issue as 2007 online; volume 17 is 2008. |
| Bini, Diniz-Filho, Rangel, Akre et al. (2009; 46 authors) Coefficient shifts in geographical ecology: an empirical evaluation of spatial and non-spatial regression. *Ecography* 32(2):193–204. doi:10.1111/j.1600-0587.2009.05717.x | 97 datasets, 8 spatial methods: coefficient shifts between OLS and spatial models are common but tended to be small; no strong predictors of shifts identified. |
| Halleck Vega & Elhorst (2015) The SLX model. *Journal of Regional Science* 55(3):339–363. doi:10.1111/jors.12188 | Advocate the SLX (local-spillover) model as point of departure when no well-founded theory indicates which spatial model is appropriate. |
| Roberts, Bahn, Ciuti, Boyce, Elith, Guillera-Arroita et al. (2017) Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography* 40(8):913–929. doi:10.1111/ecog.02881 | Random CV seriously underestimates predictive error for structured data; structured data invite overfitting with non-causal predictors, which can persist even under autoregressive models; blocked CV addresses this, but blocking can induce extrapolation. |
| Ploton et al. (2020) — already in the literature review. | |

## Biodiversity–productivity theory and scale
| reference | claim used |
|---|---|
| Chase & Leibold (2002) Spatial scale dictates the productivity–biodiversity relationship. *Nature* 416:427–430. doi:10.1038/416427a | Ponds: the productivity–diversity relationship was hump-shaped at a local scale (among ponds) and positive linear at a regional scale (among watersheds), from the same data. |
| Ricklefs (1987) Community diversity: relative roles of local and regional processes. *Science* 235(4785):167–171. doi:10.1126/science.235.4785.167 | Local diversity depends demonstrably on regional diversity; regional and historical processes profoundly influence local community structure. |
| Cornell & Harrison (2014) What are species pools and when are they important? *Annual Review of Ecology, Evolution, and Systematics* 45:45–67. doi:10.1146/annurev-ecolsys-120213-091759 | Regional species pool = species available to colonise a site; the concept links large-scale effects (area, evolutionary age, immigration, diversification) to local communities. |
| Stein, Gerstner & Kreft (2014) Environmental heterogeneity as a universal driver of species richness across taxa, biomes and spatial scales. *Ecology Letters* 17(7):866–880. doi:10.1111/ele.12277 | Meta-analysis, 1148 data points / 192 studies: heterogeneity in land cover, vegetation, climate, soil and topography all significantly positive for richness; vegetation and topographic heterogeneity especially strong; scale influences strength. |

## Species–energy theory (productivity → bird richness)
| reference | claim used |
|---|---|
| Evans, Warren & Gaston (2005) Species–energy relationships at the macroecological scale: a review of the mechanisms. *Biological Reviews* 80(1):1–25. doi:10.1017/s1464793104006517 | Macro-scale species–energy relationships are very general and typically monotonically increasing; debate centres on energy controlling the number of individuals; nine candidate mechanisms share predictions. |
| Hurlbert (2004) Species–energy relationships and habitat complexity in bird communities. *Ecology Letters* 7(8):714–720. doi:10.1111/j.1461-0248.2004.00630.x | North American birds: qualitative support for the More Individuals Hypothesis, but MIH alone inadequate; productive sites had more individuals and more even abundance; richness higher in structurally complex forests controlling for energy. |
| Coops, Waring, Wulder, Pidgeon & Radeloff (2009) Bird diversity: a predictable function of satellite-derived estimates of seasonal variation in canopy light absorbance across the United States. *Journal of Biogeography* 36(5):905–918. doi:10.1111/j.1365-2699.2008.02053.x | Bird richness across 84 US ecoregions strongly predicted by a MODIS fPAR dynamic habitat index (R² = 0.88); seasonal variation in fPAR the dominant component. |

## Methods
| reference | claim used |
|---|---|
| Chao & Jost (2012) Coverage-based rarefaction and extrapolation: standardizing samples by completeness rather than size. *Ecology* 93(12):2533–2547. doi:10.1890/11-1952.1 | Abstract: traditional rarefaction to equal-sized samples "systematically biases the degree of differences between community richnesses", because a sample of a given size may fully characterise a low-diversity community but not a richer one; comparing at equal coverage gives less biased comparisons. (Our cells span coverage 0.61–0.93 at n = 250 — the situation they describe.) Coverage-interpolation formula implemented in `scripts/coverage_rarefaction.py`. **Verified 2026-10-06 against the authors' own R package iNEXT** (`AnneChao/iNEXT`, `R/iNEXT.r` `Chat.Ind`; full-sample estimator per `R/invChat.R`): algebraically identical, max numeric difference 5×10⁻¹³ over 200 random abundance vectors, identical to 10 d.p. on a 3.76M-record cell, and coverage monotone in m (required by the bisection). |
| Hurlbert (1971) — already in the literature review. | |

## Local regression (added 2026-11-16)
Existence and details checked against Crossref. No abstract was available through
Europe PMC for these four, so they are cited **only as the source of the method**.

| reference | used for |
|---|---|
| Brunsdon, Fotheringham & Charlton (1996) Geographically weighted regression: a method for exploring spatial nonstationarity. *Geographical Analysis* 28(4):281–298. doi:10.1111/j.1538-4632.1996.tb00936.x | The GWR method in `local_slopes.py`. |
| Brunsdon, Fotheringham & Charlton (1998) Geographically weighted regression. *The Statistician* 47(3):431–443. doi:10.1111/1467-9884.00145 | The Monte Carlo test of whether local coefficients vary more than chance. |
| da Silva & Fotheringham (2016) The multiple testing issue in geographically weighted regression. *Geographical Analysis* 48(3):233–247. doi:10.1111/gean.12084 | The adjusted significance level for local t-tests. Crossref lists 2015 online; volume 48 is 2016. |
| Wheeler & Tiefelsdorf (2005) Multicollinearity and correlation among local regression coefficients in geographically weighted regression. *Journal of Geographical Systems* 7(2):161–187. doi:10.1007/s10109-005-0155-6 | Why local condition numbers are reported. |

## Second taxon: plants (added 2026-11-16)
Checked against Crossref and abstracts read via Europe PMC.

| reference | claim used |
|---|---|
| Meyer, Weigelt & Kreft (2016) Multidimensional biases, gaps and uncertainties in global plant occurrence information. *Ecology Letters* 19(8):992–1006. doi:10.1111/ele.12624 | 120 million plant occurrence records analysed for all c. 370,000 land plant species: biases, gaps and uncertainties along taxonomic, geographical and temporal dimensions "remain a central problem"; filtering to reduce uncertainty usually costs coverage. |
| Daru, Park, Primack, Willis et al. (2018) Widespread sampling biases in herbaria revealed from large-scale digitization. *New Phytologist* 217(2):939–955. doi:10.1111/nph.14855 | c. 5 million herbarium records from three floras: specimens collected close to roads and herbaria; a disproportionately large share collected by very few individuals. The three floras are Australia, South Africa and New England, none in our region. Crossref lists 2017 online. |
| Kreft & Jetz (2007) Global patterns and determinants of vascular plant diversity. *PNAS* 104(14):5925–5930. doi:10.1073/pnas.0608361104 | Across 1,032 regions, potential evapotranspiration, wet days per year and topographic and habitat heterogeneity are the core predictors of vascular plant richness; the combined model explains about 70% of global variation. Used for: energy and water drive plant richness as well as productivity. |
| Wolters, Bengtsson & Zaitsev (2006) Relationship among the species richness of different taxa. *Ecology* 87(8):1886–1895. doi:10.1890/0012-9658(2006)87[1886:RATSRO]2.0.CO;2 | Review of 237 cross-taxon richness correlations: average effect size 0.374 (95% CI ± 0.068), "positive but weak". |

## Stability, robustness and direction (added 2026-11-16, second batch)
Checked against Crossref; abstracts read via Europe PMC except where noted.

| reference | claim used |
|---|---|
| Tilman, Reich & Knops (2006) Biodiversity and ecosystem stability in a decade-long grassland experiment. *Nature* 441:629–632. doi:10.1038/nature04742 | Experiment controlling the number of perennial prairie species: more species led to greater temporal stability of annual aboveground production. A plot experiment with plants, not a regional pattern. |
| Isbell et al. (2015) Biodiversity increases the resistance of ecosystem productivity to climate extremes. *Nature* 526:574–577. doi:10.1038/nature15374 | 46 grassland experiments: productivity of communities with 1–2 species changed by about 50% during climate events, communities with 16–32 species by about 25%. |
| Oehri, Schmid, Schaepman-Strub & Niklaus (2017) Biodiversity promotes primary productivity and growing season lengthening at the landscape scale. *PNAS* 114:10160–10165. doi:10.1073/pnas.1703928114 | 447 1-km² plots with remotely sensed productivity 2000–2015: "landscape-scale productivity and its temporal stability increase with the diversity of plants and other taxa". The closest published design to Extension E, at a far finer grain. |
| Loreau & de Mazancourt (2013) Biodiversity and ecosystem stability: a synthesis of underlying mechanisms. *Ecology Letters* 16:106–115. doi:10.1111/ele.12073 | Mechanisms behind diversity–stability effects (asynchrony of species' responses, differences in response speed, reduced competition). Background only. |
| Simonsohn, Simmons & Nelson (2020) Specification curve analysis. *Nature Human Behaviour* 4:1208–1214. doi:10.1038/s41562-020-0912-z | Results hinge on analytic decisions that are "defensible, arbitrary and motivated"; fit all justified specifications and show them. Method for `spec_curve.py`. |
| Steegen, Tuerlinckx, Gelman & Vanpaemel (2016) Increasing transparency through a multiverse analysis. *Perspectives on Psychological Science* 11:702–712. doi:10.1177/1745691616658637 | Perform all analyses across the set of reasonable data-processing choices. |
| Shipley (2000) A new inferential test for path models based on directed acyclic graphs. *Structural Equation Modeling* 7:206–218. doi:10.1207/S15328007SEM0702_4 | Source of the d-separation test only; **no abstract available**. |
| Boakes et al. (2010) Distorted views of biodiversity: spatial and temporal bias in species occurrence data. *PLoS Biology* 8:e1000385. doi:10.1371/journal.pbio.1000385 | 170,000 bird sightings over two centuries; changing data-gathering trends may confound the picture of biodiversity change. Summary read, not the full abstract. |

## Inference methods (added 2026-11-16, inference batch)
Checked against Crossref. Abstract read for the three marked; the others have none
in Europe PMC and are cited as the source of a method only.

| reference | used for |
|---|---|
| Chernozhukov, Chetverikov, Demirer, Duflo, Hansen, Newey & Robins (2018) Double/debiased machine learning for treatment and structural parameters. *The Econometrics Journal* 21:C1–C68. doi:10.1111/ectj.12097 | The residual-on-residual estimator with cross-fitting in `dml_flexible.py`. |
| Cook & Stefanski (1994) Simulation-extrapolation estimation in parametric measurement error models. *JASA* 89:1314–1328. doi:10.1080/01621459.1994.10476871 | SIMEX in `measurement_error.py`. |
| Lakens (2017) Equivalence tests. *Social Psychological and Personality Science* 8:355–362. doi:10.1177/1948550617697177 | **Abstract read:** researchers "often incorrectly conclude an effect is absent based on a nonsignificant result"; the two one-sided tests procedure can "statistically reject the presence of effects large enough to be considered worthwhile". |
| DerSimonian & Laird (1986) Meta-analysis in clinical trials. *Controlled Clinical Trials* 7:177–188. doi:10.1016/0197-2456(86)90046-2 | **Abstract read:** a random-effects approach to combining evidence that "incorporates the heterogeneity of effects". Used for the slopes by ecoregion. |
| Dray, Legendre & Peres-Neto (2006) Spatial modelling: a comprehensive framework for principal coordinate analysis of neighbour matrices (PCNM). *Ecological Modelling* 196:483–493. doi:10.1016/j.ecolmodel.2006.02.015 | Moran's eigenvector maps in `scale_decomposition.py`. |
| Engle (1974) Band spectrum regression. *International Economic Review* 15:1–11. doi:10.2307/2526084 | Fitting a separate slope in each band of scales. DOI found by title search after a remembered DOI proved wrong. |
| Clifford, Richardson & Hémon (1989) Assessing the significance of the correlation between two spatial processes. *Biometrics* 45:123–134. doi:10.2307/2532039 | **Abstract read:** tests "based on the evaluation of an effective sample size that takes into account the spatial structure"; for positively autocorrelated processes the effective sample size is reduced. |
| Dutilleul (1993) Modifying the t test for assessing the correlation between two spatial processes. *Biometrics* 49:305–314. doi:10.2307/2532625 | The modified t-test on the effective sample size. |

## Data products (cite in methods)
| product | citation |
|---|---|
| MOD17A3HGF v061 (GPP, NPP) | Running, S., Zhao, M. (2021). MODIS/Terra Net Primary Production Gap-Filled Yearly L4 Global 500m SIN Grid V061. NASA EOSDIS Land Processes DAAC. doi:10.5067/MODIS/MOD17A3HGF.061 |
| MOD13Q1 v061 (NDVI, EVI) | Didan, K. (2021). MODIS/Terra Vegetation Indices 16-Day L3 Global 250m SIN Grid V061. NASA EOSDIS Land Processes DAAC. doi:10.5067/MODIS/MOD13Q1.061 |
| ERA5-Land | Muñoz-Sabater, J. et al. (2021). ERA5-Land: a state-of-the-art global reanalysis dataset for land applications. *Earth System Science Data* 13(9):4349–4383. doi:10.5194/essd-13-4349-2021 |
| ESA WorldCover v200 | Zanaga, D. et al. (2022). ESA WorldCover 10 m 2021 v200. Zenodo. doi:10.5281/zenodo.7254221 |
| RESOLVE Ecoregions 2017 | Dinerstein, E. et al. (2017). An ecoregion-based approach to protecting half the terrestrial realm. *BioScience* 67(6):534–545. doi:10.1093/biosci/bix014. Abstract read: the paper's map of Earth's 846 terrestrial ecoregions is the layer used (Earth Engine `RESOLVE/ECOREGIONS/2017`); the paper's own subject is conservation targets, so cite it as the source of the ecoregion map only. |
| SRTM (elevation) | NASA JPL (2013). NASA Shuttle Radar Topography Mission Global 1 arc second. NASA EOSDIS Land Processes DAAC. doi:10.5067/MEaSUREs/SRTM/SRTMGL1.003 (Earth Engine asset `USGS/SRTMGL1_003`) |
| ETOPO1 (terrain in the 3D map only) | Amante, C. & Eakins, B.W. (2009). ETOPO1 1 Arc-Minute Global Relief Model. NOAA National Geophysical Data Center. doi:10.7289/V5C8276M (Earth Engine asset `NOAA/NGDC/ETOPO1`). Citation written from memory and **not yet checked against the Earth Engine catalogue or the DOI**; check before citing. Used for display, not for any analysis. |
| WDPA (Extension F, map overlay) | UNEP-WCMC and IUCN, Protected Planet: The World Database on Protected Areas. Earth Engine asset `WCMC/WDPA/current/polygons`, accessed 2026-11-16. **Version month not recorded; get it from protectedplanet.net before citing.** |
| GBIF butterfly and moth occurrences | **No DOI yet.** Lepidoptera (taxonKey 797), 560,818 records in the 884 cells, 2000-2024. |
| GBIF plant occurrences | **No DOI yet.** 1,362,316 records from 435 datasets (Tracheophyta, 5-31N 68-102E, 2000-2024), counts in `data/gbif_derived_dataset/dataset_counts_plants.csv`. Register a derived dataset before citing (TODO). |
| GBIF occurrences | GBIF.org (11 October 2026) Filtered export of GBIF occurrence data. https://doi.org/10.15468/dd.jf64nx (GBIF derived dataset: Aves, 5-31N 68-102E, 2000-2024; 110 datasets, 71,716,026 records; registered 2026-10-11 because the data came from API queries, not a download). Per-cell data, codebook, counts and scripts: Zenodo doi:10.5281/zenodo.23264805. |

## Considered and dropped
- Hawkins et al. (2003) *Ecology* 84:3105, energy/water and richness — abstract
  unavailable through all three sources; not cited.
