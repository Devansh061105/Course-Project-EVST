# Case-study regions from the Step 1 grid package (teammate contribution)

Provenance: copied unchanged from the team repository `vai1717/Planet-LOL`, folder
`project9_step1`, commit `7af0988` (2026-10-09), authored by `raunak-gupta-2615`. Only the
`_crosswalk` file below was derived here.

| File | What it is |
|---|---|
| `resolve_ecoregions_selected.geojson` | Source polygons: RESOLVE Ecoregions 2017 IDs 253, 254, 270, 271 (Western Ghats), 315 (Deccan thorn scrub), 233 (Himalayan subtropical broadleaf) |
| `case_study_regions.geojson` | The three case-study polygons built from them (Deccan cut at 12N and foothills at 88E) |
| `case_study_cells_{0.5,1,2}deg.csv` | Region-to-cell overlap tables: overlap area, fraction of the cell covered, fraction of the region covered, whether the cell centre is inside |
| `teammate_grid_1deg_attributes.csv` | Their 1-degree master grid (4,264 cells, window 60-142E, 12S-40N) with their `cell_id` format and ellipsoid cell areas |
| `teammate_study_config.json` | Their window, resolutions and case definitions |
| `case_study_cells_1deg_crosswalk.csv` | **Derived here.** The 1-degree overlap table joined to our `cell_id` (matched on identical cell bounds) with an `in_our_model_221` flag |

## Key facts
- All 884 of our 1-degree cells are identical rectangles in their grid; only the ID format differs.
- Their 1-degree case cells that are among our 221 modelled cells: Western Ghats 15 of 30, Deccan 4 of 47, Eastern Himalayan foothills 8 of 10. The Deccan region is mostly cropland, which is why our analysis uses the Thar Desert instead.
- Their selections are subregions defined by ecoregion and a latitude or longitude cut-off, not the full named landscapes. Cells are mixed: the foothill polygon fills under half of every selected 1-degree cell, so use the overlap fractions and do not read whole-cell values as pure foothill measurements.
- Their decisions file states the choices are not yet approved by the whole team.
- Our own case-study boxes (see `scripts/gbif_lib.py`, `CASE_STUDIES`) are unchanged. Adopting these polygons would be a design decision for the team and would need Extension C to be re-run.

## Attribution
RESOLVE Ecoregions 2017, UNEP-WCMC, CC-BY 4.0: Dinerstein et al. (2017), An Ecoregion-Based Approach to Protecting Half the Terrestrial Realm, BioScience, DOI 10.1093/biosci/bix014.
