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

## Data products (cite in methods)
| product | citation |
|---|---|
| MOD17A3HGF v061 (GPP, NPP) | Running, S., Zhao, M. (2021). MODIS/Terra Net Primary Production Gap-Filled Yearly L4 Global 500m SIN Grid V061. NASA EOSDIS Land Processes DAAC. doi:10.5067/MODIS/MOD17A3HGF.061 |
| MOD13Q1 v061 (NDVI, EVI) | Didan, K. (2021). MODIS/Terra Vegetation Indices 16-Day L3 Global 250m SIN Grid V061. NASA EOSDIS Land Processes DAAC. doi:10.5067/MODIS/MOD13Q1.061 |
| ERA5-Land | Muñoz-Sabater, J. et al. (2021). ERA5-Land: a state-of-the-art global reanalysis dataset for land applications. *Earth System Science Data* 13(9):4349–4383. doi:10.5194/essd-13-4349-2021 |
| ESA WorldCover v200 | Zanaga, D. et al. (2022). ESA WorldCover 10 m 2021 v200. Zenodo. doi:10.5281/zenodo.7254221 |
| RESOLVE Ecoregions 2017 | Dinerstein, E. et al. (2017). An ecoregion-based approach to protecting half the terrestrial realm. *BioScience* 67(6):534–545. doi:10.1093/biosci/bix014. Abstract read: the paper's map of Earth's 846 terrestrial ecoregions is the layer used (Earth Engine `RESOLVE/ECOREGIONS/2017`); the paper's own subject is conservation targets, so cite it as the source of the ecoregion map only. |
| SRTM (elevation) | NASA JPL (2013). NASA Shuttle Radar Topography Mission Global 1 arc second. NASA EOSDIS Land Processes DAAC. doi:10.5067/MEaSUREs/SRTM/SRTMGL1.003 (Earth Engine asset `USGS/SRTMGL1_003`) |
| GBIF occurrences | **No citable DOI exists for our data.** We used live faceted API queries, not a download. GBIF requires a DOI for published use: register a *derived dataset* listing the contributing datasets (API endpoint `api.gbif.org/v1/derivedDataset` confirmed to exist 2026-10-06 — it answers GET with 405, i.e. POST-only; registration needs a GBIF account, so this is the user's step), or re-run as a formal occurrence download. Must be done before the final report. |

## Considered and dropped
- Hawkins et al. (2003) *Ecology* 84:3105, energy/water and richness — abstract
  unavailable through all three sources; not cited.
