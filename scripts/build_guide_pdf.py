# -*- coding: utf-8 -*-
"""Render docs/MID_EVAL_PREP_GUIDE.md to docs/MID_EVAL_PREP_GUIDE.pdf.

Markdown -> HTML (python-markdown, tables) with print CSS, the eight report
figures appended as a figure appendix (embedded as data URIs), then printed to
PDF with headless Microsoft Edge (Chromium), which handles the Unicode the guide
uses (≥, °, ×, superscript units) and lays tables out properly.
"""
import base64
import os
import subprocess
import sys

import markdown

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
SRC = os.path.join(ROOT, "docs", "MID_EVAL_PREP_GUIDE.md")
HTML = os.path.join(ROOT, "docs", "MID_EVAL_PREP_GUIDE.html")
PDF = os.path.join(ROOT, "docs", "MID_EVAL_PREP_GUIDE.pdf")
FIG = os.path.join(ROOT, "figures")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

FIGURES = [
    ("fig1_study_area_mask.png", "Fig 1 — Study region and mask",
     "884 one-degree cells, 630 on land, 221 modelled. Orange cells are cropland or built-up "
     "dominated and excluded; the Deccan disappears entirely. Boxes: the three case studies."),
    ("fig2_maps_richness_gpp.png", "Fig 2 — Effort-corrected richness and GPP",
     "Both are highest in the wet north-east (Eastern Himalaya, Myanmar). Grey: land cells "
     "excluded from the model."),
    ("fig3_attenuation.png", "Fig 3 — The richness coefficient across models",
     "Raw vs corrected richness, then adding climate, biome and ecoregion controls, and the "
     "spatial error model. Climate and biogeography account for most of the association."),
    ("fig4_between_within.png", "Fig 4 — Between vs within ecoregions",
     "Both panels adjusted for effort and climate. Clear between ecoregions; much weaker within "
     "(not significant at 1°; +0.058 SD, p = 0.021 at 0.5°)."),
    ("fig5_correlogram.png", "Fig 5 — Residual spatial autocorrelation by distance",
     "Ecoregion fixed effects remove the broad 4.5–9° plateau: the hidden regional driver was "
     "biogeography."),
    ("fig6_case_study_spreads.png", "Fig 6 — Case-study spreads",
     "Survey effort varies 139×, GPP 10×, raw richness 2.2×, corrected richness only 1.3×."),
    ("fig7_naive_vs_corrected.png", "Fig 7 — Extension A: naive vs corrected",
     "Raw richness tracks survey effort (r = 0.81); rarefaction cuts that to 0.24."),
    ("fig8_linear_vs_quadratic.png", "Fig 8 — Extension B: linear vs quadratic",
     "The two fits are indistinguishable (ΔAIC +1.9): no evidence of a hump."),
]

CSS = """
@page { size: A4; margin: 18mm 16mm 18mm 16mm;
        @bottom-center { content: "Project 9 · Mid-evaluation prep guide · page " counter(page);
                         font: 8pt 'Segoe UI', sans-serif; color: #898781; } }
html { font-family: 'Segoe UI', system-ui, sans-serif; font-size: 10pt; color: #1b1b1a;
       line-height: 1.45; }
body { margin: 0; }
h1 { font-size: 20pt; line-height: 1.2; margin: 0 0 4mm 0; color: #0b0b0b; }
h2 { font-size: 13.5pt; margin: 7mm 0 2.5mm 0; padding-bottom: 1.2mm;
     border-bottom: 1.5px solid #2a78d6; color: #0b0b0b; break-after: avoid; }
h3 { font-size: 11pt; margin: 5mm 0 2mm 0; color: #184f95; break-after: avoid; }
p { margin: 0 0 2.4mm 0; }
ul, ol { margin: 0 0 2.6mm 0; padding-left: 6mm; }
li { margin: 0 0 1mm 0; }
strong { color: #0b0b0b; }
code { font-family: Consolas, monospace; font-size: 8.8pt; background: #f2f1ee;
       padding: 0 1mm; border-radius: 2px; }
hr { border: none; border-top: 1px solid #e1e0d9; margin: 4mm 0; }
table { border-collapse: collapse; width: 100%; margin: 1.5mm 0 3.5mm 0; font-size: 8.8pt;
        break-inside: auto; }
thead { display: table-header-group; }
tr { break-inside: avoid; }
th { background: #eef3fb; color: #0b0b0b; text-align: left; font-weight: 600;
     border: 1px solid #d6dce6; padding: 1.4mm 1.8mm; }
td { border: 1px solid #e1e0d9; padding: 1.3mm 1.8mm; vertical-align: top; }
tr:nth-child(even) td { background: #fbfbfa; }
.cover { border-left: 4px solid #2a78d6; padding: 2mm 0 2mm 5mm; margin-bottom: 6mm; }
.cover .sub { color: #52514e; font-size: 10.5pt; margin-top: 1mm; }
.qa p strong:first-child { color: #184f95; }
.figpage { break-before: page; }
.fig { break-inside: avoid; margin: 0 0 7mm 0; }
.fig img { width: 100%; border: 1px solid #e1e0d9; }
.fig .cap { font-size: 9pt; color: #52514e; margin-top: 1.5mm; }
.fig .cap b { color: #0b0b0b; }
.flow { display: grid; grid-template-columns: repeat(3, 1fr); gap: 2.2mm; margin: 2mm 0 4mm 0; }
.flow .step { border: 1px solid #b7d3f6; border-left: 3px solid #2a78d6; background: #f5f9fe;
              padding: 1.6mm 2.2mm; break-inside: avoid; }
.flow .step b { display: block; color: #184f95; font-size: 9.5pt; }
.flow .step span { font-size: 8.6pt; color: #3a3936; }
.callout { border: 1px solid #e1e0d9; border-left: 3px solid #eb6834; background: #fdf8f5;
           padding: 2.4mm 3mm; margin: 3mm 0; font-size: 9.2pt; break-inside: avoid; }
"""


GUIDES = {
    "full": dict(src="MID_EVAL_PREP_GUIDE", figures=None, qa=("<h2>14.", "<h2>15."),
                 sub="Course Project 9 · Biodiversity and Ecosystem Productivity · "
                     "guide written 2026-10-06 · PDF built 2026-10-07"),
    "focused": dict(src="MID_EVAL_GUIDE_FOCUSED",
                    figures=["fig1_study_area_mask.png", "fig2_maps_richness_gpp.png"],
                    qa=("<h2>9.", "<h2>10."),
                    sub="Course Project 9 · mid evaluation: project, approach, literature, "
                        "impact, expected results · 2026-10-07"),
}


def main(which="full"):
    g = GUIDES[which]
    global SRC, HTML, PDF
    SRC = os.path.join(ROOT, "docs", g["src"] + ".md")
    HTML = os.path.join(ROOT, "docs", g["src"] + ".html")
    PDF = os.path.join(ROOT, "docs", g["src"] + ".pdf")
    md_text = open(SRC, encoding="utf-8").read()
    # The first H1 becomes the cover title; the italic note under it the subtitle.
    lines = md_text.split("\n")
    assert lines[0].startswith("# "), "guide must start with an H1"
    title = lines[0][2:].strip()
    body_md = "\n".join(lines[1:])
    body = markdown.markdown(body_md, extensions=["tables", "sane_lists"])
    # Wrap the Q&A section so its question lines can be styled.
    q0, q1 = g["qa"]
    if q0 in body and q1 in body:
        a = body.index(q0)
        b = body.index(q1)
        body = body[:a] + '<div class="qa">' + body[a:b] + "</div>" + body[b:]

    chosen = [f for f in FIGURES if g["figures"] is None or f[0] in g["figures"]]
    intro = ("All eight figures, in the order the guide refers to them." if g["figures"] is None
             else "The study area and what the two main data layers look like.")
    figs = ['<div class="figpage"><h2>Appendix — figures</h2>',
            "<p>%s Each has a CSV of its plotted values in <code>figures/</code>.</p>" % intro]
    for fname, cap, msg in chosen:
        path = os.path.join(FIG, fname)
        if not os.path.exists(path):
            sys.exit("missing figure: %s" % path)
        b64 = base64.b64encode(open(path, "rb").read()).decode("ascii")
        figs.append('<div class="fig"><img src="data:image/png;base64,%s" alt="%s">'
                    '<div class="cap"><b>%s.</b> %s</div></div>' % (b64, cap, cap, msg))
    figs.append("</div>")

    html = ("<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>"
            "<title>%s</title><style>%s</style></head><body>"
            "<div class='cover'><h1>%s</h1>"
            "<div class='sub'>%s</div></div>%s%s</body></html>"
            % (title, CSS, title, g["sub"], body, "".join(figs)))
    open(HTML, "w", encoding="utf-8").write(html)

    # Remove the previous output first: otherwise a silent Edge failure leaves the
    # old PDF in place and the existence check below reports a stale file as success.
    if os.path.exists(PDF):
        os.remove(PDF)
    url = "file:///" + HTML.replace("\\", "/").replace(" ", "%20")
    # A fresh profile per build keeps an already-open Edge window from taking over
    # the request.
    import tempfile
    import time
    profile = tempfile.mkdtemp(prefix="edge_pdf_")
    r = subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        "--no-first-run", "--user-data-dir=%s" % profile,
                        "--print-to-pdf=%s" % PDF, url],
                       capture_output=True, text=True, timeout=180)
    # msedge.exe hands the job to a child process and returns at once, so the PDF may
    # not exist yet. Wait until it appears and its size stops changing (up to 90 s).
    last, stable, t0 = -1, 0, time.time()
    while time.time() - t0 < 90 and stable < 3:
        if os.path.exists(PDF):
            size = os.path.getsize(PDF)
            stable = stable + 1 if (size == last and size > 0) else 0
            last = size
        time.sleep(0.5)
    if stable < 3:
        sys.exit("PDF not produced within 90 s (exit %s). Edge stderr:\n%s"
                 % (r.returncode, r.stderr[-1500:]))
    print("wrote %s (%.0f KB)" % (PDF, os.path.getsize(PDF) / 1024))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "full")
