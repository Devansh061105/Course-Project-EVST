# Course Project 9: Biodiversity and Ecosystem Productivity

Does effort-corrected bird richness (GBIF) track ecosystem productivity (MODIS GPP) across
South and Southeast Asia on a 1-degree grid? Python (statsmodels, spreg) for the analysis,
Google Earth Engine for the environmental layers.

**New to the project or resuming work? Start with [HANDOFF.md](HANDOFF.md).** It has the full
context, what is done, what is still open, and how to run everything.

## Look at the data
- `docs/interactive_map_3d.html`: the study region as 3D terrain. The ground is coloured
  by land cover, greenness, productivity or elevation; columns show bird or plant richness
  per one-degree cell; click any place for its record.
- `docs/interactive_map.html`: a flat atlas with more layers (model residuals, local
  slopes, which cells are modelled) and a linked richness-against-GPP scatter.

Download either file and open it in a browser. Both are rebuilt by
`python scripts/build_interactive_map.py`.

## Results, in order of reading
1. `docs/RESULTS_ADJUDICATION.md`: the current interpretation.
2. `docs/RESULTS_EXTENSION_A.md`, `_B.md`, `_C.md`: naive vs corrected, linear vs
   hump-shaped, three case studies.
3. `docs/RESULTS_LOCAL_SLOPES.md`: the slope fitted around every cell (part of Extension C).
4. `docs/RESULTS_EXTENSION_D.md`: the same analysis for vascular plants.
