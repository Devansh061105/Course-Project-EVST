// Builds presentation/Project9_Biodiversity_Productivity.pptx from the figures in figures/.
//
//   npm install pptxgenjs
//   node presentation/build_deck.js
//
// Every number on the slides is taken from the docs/RESULTS_*.md files; if a result
// changes, change it here too. Optional: set PPTX_APPLY_THEME to the path of an
// apply_theme.js helper to write the palette into the deck's theme (so the colours
// can be restyled in PowerPoint); without it the same colours are written directly.
const path = require("path");
const pptxgen = require("pptxgenjs");

const ROOT = path.resolve(__dirname, "..");
const FIG = n => path.join(ROOT, "figures", n + ".png");
const SIZE = { // pixel sizes of the figures, for aspect-correct placement
  fig1_study_area_mask: [1572, 1176], fig6_case_study_spreads: [1848, 858],
  fig8_linear_vs_quadratic: [1628, 990], fig11_effort_simulation: [1924, 871],
  fig12_spec_curve: [2117, 922], fig13_shape: [1801, 837], fig14_direction: [1510, 823],
  fig15_stability: [2013, 888], fig16_survey_gaps: [2237, 990], fig17_three_taxa: [1981, 837],
  fig18_ecoregion_slopes: [2145, 1735], fig19_scale_bands: [2055, 897],
  fig21_flexible_controls: [1883, 863],
};
const THEME = {
  name: "Project 9", headFontFace: "Cambria", bodyFontFace: "Calibri",
  colors: { dk1: "14261C", lt1: "FFFFFF", dk2: "46524B", lt2: "EDF2EE", accent1: "2A78D6",
            accent2: "EB6834", accent3: "1BAF7A", accent4: "0D366B", accent5: "8F3612",
            accent6: "7A3FB8", hlink: "2A78D6", folHlink: "7A3FB8" },
};
let applyTheme = null;
try { if (process.env.PPTX_APPLY_THEME) applyTheme = require(process.env.PPTX_APPLY_THEME).applyTheme; } catch (e) { applyTheme = null; }

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 in
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Biodiversity and Ecosystem Productivity";
pres.author = "Course Project 9";
const S = pres.SchemeColor, T = THEME.colors;
const C = applyTheme
  ? { ink: S.text1, ink2: S.text2, bg: S.background1, tint: S.background2, blue: S.accent1, orange: S.accent2, green: S.accent3 }
  : { ink: T.dk1, ink2: T.dk2, bg: T.lt1, tint: T.lt2, blue: T.accent1, orange: T.accent2, green: T.accent3 };

pres.defineSlideMaster({
  title: "COVER", background: { color: C.ink },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.9, y: 2.0, w: 11.5, h: 1.9, fontSize: 44, bold: true, color: C.bg, align: "left", valign: "bottom", margin: 0 }, text: "Title" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.9, y: 4.15, w: 10.6, h: 1.6, fontSize: 20, color: C.tint, align: "left", valign: "top", margin: 0 }, text: "Subtitle" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENT", background: { color: C.bg },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.4, w: 12.1, h: 1.0, fontSize: 30, bold: true, color: C.ink, align: "left", valign: "middle", margin: 0 }, text: "Title" } },
    { text: { text: "Course Project 9 · Biodiversity and Ecosystem Productivity", options: { x: 0.6, y: 7.0, w: 9, h: 0.3, fontSize: 10, color: C.ink2, margin: 0, isTextBox: true } } },
  ],
  slideNumber: { x: 12.2, y: 7.0, w: 0.6, h: 0.3, fontSize: 10, color: C.ink2, align: "right" },
});

function slide(section, title, notes, master) {
  const s = pres.addSlide({ masterName: master || "CONTENT", sectionTitle: section });
  s.addText(title, { placeholder: "title" });
  if (notes) s.addNotes(notes);
  return s;
}
function figure(s, name, x, y, w, h) { // fit inside the box, centred, aspect kept
  const [pw, ph] = SIZE[name], r = Math.min(w / pw, h / ph), fw = pw * r, fh = ph * r;
  s.addImage({ path: FIG(name), x: x + (w - fw) / 2, y: y + (h - fh) / 2, w: fw, h: fh, altText: name.replace(/_/g, " ") });
}
function stat(s, x, y, w, big, label, color) {
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h: 1.55, fill: { color: C.tint }, line: { color: C.tint }, rectRadius: 0.08, objectName: "stat card" });
  s.addText(big, { x: x + 0.2, y: y + 0.1, w: w - 0.4, h: 0.75, fontSize: big.length > 9 ? 25 : 34, bold: true, color: color || C.blue, margin: 0, valign: "middle", fontFace: THEME.headFontFace, isTextBox: true });
  s.addText(label, { x: x + 0.2, y: y + 0.85, w: w - 0.4, h: 0.62, fontSize: 14, color: C.ink2, margin: 0, valign: "top", isTextBox: true });
}
function points(s, items, x, y, w, h, size) {
  s.addText(items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1 } })),
    { x, y, w, h, fontSize: size || 16, color: C.ink, paraSpaceAfter: 10, valign: "top", margin: 0, isTextBox: true });
}

// ---------------------------------------------------------------- 1. cover
pres.addSection({ title: "Question" });
{
  const s = slide("Question", "Biodiversity and Ecosystem Productivity",
    "One-line version: across South and Southeast Asia, places with more species are more productive, but almost all of that is a difference between regions, not something you see inside a region.", "COVER");
  s.addText("Does biodiversity track ecosystem productivity once the uneven effort behind citizen-science records is corrected? South and Southeast Asia, one-degree grid.", { placeholder: "body" });
  s.addText("Course Project 9", { x: 0.9, y: 6.6, w: 6, h: 0.4, fontSize: 14, color: C.tint, margin: 0, isTextBox: true });
}

// ---------------------------------------------------------------- 2. question
{
  const s = slide("Question", "The question, and why the data make it hard",
    "H1: effort-corrected biodiversity is positively associated with GPP after controlling for climate, on natural land cover. The difficulty: GBIF records are concentrated where birdwatchers go. The map shows which cells enter the models (blue) and which are dropped as cropland (orange). Only 36% of the modelled cells are in India; say South and Southeast Asia, not India.");
  points(s, [
    "Hypothesis: places with more species are more productive, after climate is accounted for.",
    "The catch: occurrence records come from volunteers, and volunteers are not spread evenly.",
    "Study area: 5–31°N, 68–102°E. Most of peninsular India is cropland and is left out.",
  ], 0.6, 1.65, 5.6, 2.9);
  stat(s, 0.6, 4.95, 1.6, "884", "one-degree cells");
  stat(s, 2.35, 4.95, 1.6, "221", "cells modelled");
  stat(s, 4.1, 4.95, 2.1, "71.7M", "bird records");
  figure(s, "fig1_study_area_mask", 6.6, 1.55, 6.1, 5.2);
}

// ---------------------------------------------------------------- 3. method
pres.addSection({ title: "Method" });
{
  const s = slide("Method", "How each cell gets its numbers",
    "Rarefaction: the number of species expected in a random draw of 250 records, so a cell with a million records and a cell with a thousand are compared on the same footing. Survey effort also enters the model as a covariate. Natural-cover restriction removes cropland and built-up cells so farm output is not compared with natural productivity.");
  const steps = [
    ["GBIF records", "Birds 2000–2024, one request per cell"],
    ["Effort correction", "Species expected in 250 random records"],
    ["Satellite data", "MODIS productivity, ERA5-Land climate"],
    ["Natural land only", "Cropland and built-up cells removed"],
    ["Models", "Across regions, within ecoregions, spatial"],
  ];
  const w = 2.2, gap = 0.26, x0 = 0.6, y = 2.0;
  steps.forEach(([head, body], i) => {
    const x = x0 + i * (w + gap);
    s.addShape(pres.ShapeType.roundRect, { x, y, w, h: 2.2, fill: { color: C.tint }, line: { color: C.tint }, rectRadius: 0.08, objectName: "step card" });
    s.addShape(pres.ShapeType.ellipse, { x: x + 0.2, y: y + 0.2, w: 0.5, h: 0.5, fill: { color: C.ink }, line: { color: C.ink }, objectName: "step number" });
    s.addText(String(i + 1), { x: x + 0.2, y: y + 0.2, w: 0.5, h: 0.5, fontSize: 16, bold: true, color: C.bg, align: "center", valign: "middle", margin: 0, isTextBox: true });
    s.addText(head, { x: x + 0.2, y: y + 0.85, w: w - 0.4, h: 0.45, fontSize: 16, bold: true, color: C.ink, margin: 0, isTextBox: true });
    s.addText(body, { x: x + 0.2, y: y + 1.3, w: w - 0.4, h: 0.8, fontSize: 14, color: C.ink2, margin: 0, valign: "top", isTextBox: true });
  });
  points(s, [
    "Every headline number is re-checked from cached data on each push: 33 scripts, 68 checks, 21 unit tests.",
    "Six extensions test the result from different sides; the next slides take them in turn.",
  ], 0.6, 4.75, 12.1, 1.6);
}

// ---------------------------------------------------------------- 4. extension A
pres.addSection({ title: "Results" });
{
  const s = slide("Results", "Raw species counts mostly map where birdwatchers go",
    "Extension A. Left panel: take a heavily surveyed cell and throw records away at random. The raw count collapses; corrected richness does not move. Right panel: thin every cell in the dataset and refit the model; the headline coefficient barely changes. Caveat to say out loud: random thinning is not how real effort differs, which is why effort is also a covariate.");
  figure(s, "fig11_effort_simulation", 0.6, 1.55, 8.6, 5.2);
  stat(s, 9.5, 1.7, 3.2, "0.81 → 0.24", "correlation of richness with survey effort, before and after correction");
  stat(s, 9.5, 3.45, 3.2, "23%", "of the raw count survives thinning a cell to 250 records", C.orange);
  stat(s, 9.5, 5.2, 3.2, "99.8%", "of corrected richness survives the same thinning", C.green);
}

// ---------------------------------------------------------------- 5. main result
{
  const s = slide("Results", "Across regions the link is clear; within a region it nearly vanishes",
    "The main result. 960 versions of the model: four productivity measures, five richness measures, four land-cover masks, four sets of controls, three estimators. Blue: comparing across the whole region. Orange and green: comparing only within an ecoregion or allowing for spatial structure. No version is significantly negative. The split is by how you compare, not by any data choice.");
  figure(s, "fig12_spec_curve", 0.6, 1.55, 9.0, 5.2);
  stat(s, 9.9, 1.7, 2.8, "+0.24", "median coefficient across regions (320 models)");
  stat(s, 9.9, 3.45, 2.8, "+0.04", "median within ecoregions (320 models)", C.orange);
  stat(s, 9.9, 5.2, 2.8, "0 of 960", "models significantly negative", C.green);
}

// ---------------------------------------------------------------- 5b. flexible controls
{
  const s = slide("Results", "About half of the across-region link is curved climate",
    "This is the correction to our own headline. All the earlier models control for temperature and rainfall with straight lines. Let the controls bend, using a random forest or gradient boosting with folds that are spatial blocks, and the across-region coefficient roughly halves. At half a degree it comes down to about the same small number we get inside ecoregions. So +0.27 is what linear controls give; the size of the association is nearer +0.07 to +0.17. Method: double machine learning, Chernozhukov and others 2018.");
  figure(s, "fig21_flexible_controls", 0.6, 1.55, 8.6, 5.2);
  stat(s, 9.5, 1.7, 3.2, "+0.29 → +0.17", "across regions at 1°, straight-line against flexible controls");
  stat(s, 9.5, 3.45, 3.2, "+0.18 → +0.07", "the same at 0.5°", C.orange);
  stat(s, 9.5, 5.2, 3.2, "+0.05", "within ecoregions at 0.5°, flexible controls", C.green);
}

// ---------------------------------------------------------------- 5c. scale
{
  const s = slide("Results", "The link lives in the broadest spatial patterns",
    "Instead of ecoregion borders, split the map into spatial patterns from continent-wide gradients down to cell-to-cell texture, and fit a slope in each band. The large slope is only in the broadest band, patches of 700 to 800 kilometres, which is also where three-quarters of the variation in productivity sits. At half a degree there is a small but clear positive slope in the part with no spatial structure at all: that is the local effect. Also worth saying: because neighbouring cells resemble each other, our 221 cells are worth about 36 independent observations.");
  figure(s, "fig19_scale_bands", 0.6, 1.55, 8.8, 5.2);
  stat(s, 9.7, 1.7, 3.0, "700–800 km", "size of the patches where the large slope sits");
  stat(s, 9.7, 3.45, 3.0, "+0.09", "slope with no spatial structure, 0.5° grid", C.orange);
  stat(s, 9.7, 5.2, 3.0, "36", "independent observations that 221 cells are worth", C.green);
}

// ---------------------------------------------------------------- 5d. ecoregions
{
  const s = slide("Results", "Inside ecoregions the effect is small, real, and varies",
    "Fit the slope separately inside each of 35 ecoregions and combine them. The pooled slope is +0.069, clearly above zero, positive in 27 of 35. But ecoregions differ more than chance allows: about half the spread between them is real. Do not read individual ecoregions; eight are individually significant where two would be by chance. An equivalence test shows the within-ecoregion effect is less than half the across-region one in every sample, birds, plants and butterflies. And it is not measurement error: richness is 99 percent reliable even within ecoregions.");
  figure(s, "fig18_ecoregion_slopes", 0.6, 1.5, 6.6, 5.35);
  stat(s, 7.5, 1.7, 2.5, "+0.069", "pooled slope over 35 ecoregions");
  stat(s, 10.2, 1.7, 2.5, "27 of 35", "ecoregions with a positive slope", C.green);
  points(s, [
    "95% interval +0.030 to +0.108.",
    "Shown to be under half the across-region effect in all five samples.",
    "Not noise: richness estimates are 99% reliable within ecoregions.",
  ], 7.5, 3.6, 5.2, 3.0);
}

// ---------------------------------------------------------------- 6. extension B
{
  const s = slide("Results", "A straight line, not a hump",
    "Extension B. The hump-backed model says productivity should fall at very high diversity. A quadratic is indistinguishable from a line in 11 of 12 specifications. The flexible curve on the left does dip at its top end at one degree, so expect a question: that dip is the spline's shape, not the data. Fit a straight line to only the richest quarter of cells and the slope is positive at both grid sizes (+0.44 and +0.30). At half a degree the line wins outright. This sides with the complementarity literature (Liang 2016, Deng 2025).");
  figure(s, "fig13_shape", 0.6, 1.55, 8.2, 5.2);
  points(s, [
    "Quadratic against linear: 11 of 12 specifications cannot tell them apart.",
    "A flexible curve fits better at 1° only, and its dip at the top is not in the data.",
    "Among the richest quarter of cells the slope is still positive: +0.44 at 1°, +0.30 at 0.5°.",
  ], 9.1, 1.9, 3.6, 4.6);
}

// ---------------------------------------------------------------- 7. extension C
{
  const s = slide("Results", "Three landscapes: the ranking flips once effort is corrected",
    "Extension C. On raw counts the Western Ghats is the richest of the three; after correction the Eastern Himalaya is. The Ghats simply has 14 times more records per cell. The Thar Desert replaced the Deccan because every Deccan cell is cropland. Productivity differs tenfold across these regions while corrected richness differs by 1.3: climate moves productivity, diversity barely moves.");
  figure(s, "fig6_case_study_spreads", 0.6, 1.55, 8.4, 5.2);
  stat(s, 9.3, 1.7, 3.4, "139×", "difference in survey effort between the three regions");
  stat(s, 9.3, 3.45, 3.4, "10×", "difference in productivity", C.orange);
  stat(s, 9.3, 5.2, 3.4, "1.3×", "difference in corrected richness", C.green);
}

// ---------------------------------------------------------------- 8. extension D
{
  const s = slide("Results", "Plants and butterflies show the same pattern as birds",
    "Extension D. Plants come from herbaria and iNaturalist, butterflies from insect photographers, birds from eBird: three different communities of observers. Same result in all three. Caveat: plant and butterfly samples are far from complete, so their richness numbers are rougher than the birds', and the butterfly coefficient should not be read as a bigger effect.");
  figure(s, "fig17_three_taxa", 0.6, 1.55, 8.8, 5.2);
  points(s, [
    "Three groups recorded by three different communities of observers.",
    "Each is linked to productivity across regions, and none within ecoregions.",
    "They agree only weakly on where diversity is high (r = 0.12 to 0.39), so one group is a poor stand-in for another.",
  ], 9.7, 1.9, 3.0, 4.7);
}

// ---------------------------------------------------------------- 9. direction
{
  const s = slide("Results", "The data cannot say which way the link runs",
    "Our hypothesis reads as biodiversity driving productivity. Ecologists who study birds usually argue the reverse: productive places support more species. Both path models fit equally well. We tried to break the tie with topographic heterogeneity; it failed its own validity check, and we report that rather than the estimate. So we frame H1 as an association.");
  figure(s, "fig14_direction", 0.6, 1.55, 7.8, 5.2);
  points(s, [
    "About half of the raw correlation is climate acting on both.",
    "\"Richness drives productivity\" and \"productivity drives richness\" fit equally well.",
    "An attempt to settle it with an instrument failed its validity check, so we report an association, not a cause.",
  ], 8.7, 1.9, 4.0, 4.7);
}

// ---------------------------------------------------------------- 10. E and F
{
  const s = slide("Results", "Richer cells are not steadier once climate is accounted for",
    "Extension E: 23 years of annual GPP. Richer cells vary less from year to year, but that is because they are wetter and more productive; the link is zero within ecoregions. Extension F on protected land is data-limited: India's national parks are largely missing from the public protected-area database, so the only solid statement is that the slope does not differ with protection.");
  figure(s, "fig15_stability", 0.6, 1.55, 8.6, 5.2);
  points(s, [
    "Raw correlation of richness with year-to-year variation: −0.36.",
    "It disappears once rainfall variability and mean productivity are controlled, and is zero within ecoregions.",
    "Protected land: the slope does not differ with protection, but India's parks are missing from the public database, so little more can be said.",
  ], 9.5, 1.9, 3.2, 4.7);
}

// ---------------------------------------------------------------- 11. survey gaps
pres.addSection({ title: "Meaning" });
{
  const s = slide("Meaning", "Where the records run out",
    "For the citizen-science part of the conclusion. Left: how complete each natural-cover cell's bird list is. Right: a ranking of where new surveys would add most. India, Nepal, Thailand and Sri Lanka are essentially complete at this scale. Caveat: in China the gap may be a gap in GBIF rather than in what ornithologists know.");
  figure(s, "fig16_survey_gaps", 0.6, 1.55, 9.2, 5.2);
  stat(s, 10.1, 1.7, 2.6, "46", "natural-cover cells dropped for too few records");
  points(s, [
    "Thin: western Pakistan, upland Myanmar, the Tibetan margin.",
    "Correction fixes uneven effort; it cannot replace missing data.",
  ], 10.1, 3.55, 2.6, 3.1, 14);
}

// ---------------------------------------------------------------- 12. policy
{
  const s = slide("Meaning", "What this supports, and what it does not",
    "Be exact here. We support: bias correction before citizen-science data are used; a real cross-regional association; clear gaps in coverage. We do not support: any claim that adding species raises carbon uptake, any ranking of regions for conservation spending, or anything about carbon stocks (GPP is a flux).");
  const col = (x, head, color, items) => {
    s.addShape(pres.ShapeType.roundRect, { x, y: 1.7, w: 5.9, h: 3.9, fill: { color: C.tint }, line: { color: C.tint }, rectRadius: 0.06, objectName: "column card" });
    s.addText(head, { x: x + 0.3, y: 1.9, w: 5.3, h: 0.5, fontSize: 20, bold: true, color, margin: 0, fontFace: THEME.headFontFace, isTextBox: true });
    points(s, items, x + 0.3, 2.6, 5.3, 2.8, 16);
  };
  col(0.6, "The results support", C.green, [
    "Citizen-science records need effort correction before they inform policy.",
    "Species-rich regions are more productive regions, across three groups of organisms.",
    "Bird data are near-complete over much of South Asia and thin in identifiable places.",
  ]);
  col(6.8, "The results do not support", C.orange, [
    "\"More species means more carbon uptake.\" Direction is not identified, and within a region the link is close to zero.",
    "Ranking regions for conservation spending by these slopes.",
    "Anything about carbon storage: productivity here is a yearly flux, not a stock.",
  ]);
}

// ---------------------------------------------------------------- 13. close
{
  const s = slide("Meaning", "Explore every cell yourself",
    "Close on the maps. The 3D map has a guided tour that walks through these same findings; clicking any place shows its record and its most-recorded species. Limits to mention if asked: one-degree cells, association not cause, plant and butterfly samples incomplete, protected-area data incomplete for India and China.", "COVER");
  s.addText([
    { text: "3D terrain map and flat atlas", options: { breakLine: true } },
    { text: "devansh061105.github.io/Course-Project-EVST", options: { breakLine: true, bold: true } },
    { text: "Code, data and every result: github.com/Devansh061105/Course-Project-EVST" },
  ], { placeholder: "body" });
}

const out = path.join(__dirname, "Project9_Biodiversity_Productivity.pptx");
pres.writeFile({ fileName: out }).then(async () => {
  if (applyTheme) await applyTheme(out, THEME);
  console.log("wrote " + out + (applyTheme ? " (theme applied)" : " (colours written directly)"));
});
