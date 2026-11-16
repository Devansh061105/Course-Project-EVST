# -*- coding: utf-8 -*-
"""Figures 11-16 (added 2026-11-16). Same tokens and conventions as make_figures.py;
each PNG has a CSV of its plotted values beside it.

  fig11_effort_simulation   Extension A tested by thinning records
  fig12_spec_curve          960 specifications of the richness coefficient
  fig13_shape               Extension B with a flexible curve
  fig14_direction           path diagram: what the data can and cannot say
  fig15_stability           Extension E, richness and year-to-year stability
  fig16_survey_gaps         where bird records are thinnest relative to expectation

Each figure is skipped with a message if the script that makes its input has not run.
"""
import os
import sys
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import PatchCollection
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from make_figures import (AQUA, AXIS, BLUE, BLUE_RAMP, DATA, GRID, INK, INK2, MUTED, NEUTRAL,
                          ORANGE, ORANGE_RAMP, OUT, SURFACE, cell_patches, draw_cases,
                          hairline_grid, map_axes)


def need(*names):
    paths = [os.path.join(DATA, n) for n in names]
    return paths if all(os.path.exists(p) for p in paths) else None


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + ".png"), dpi=220, bbox_inches="tight")
    plt.close(fig)


# ---- Fig 11: effort simulation ----------------------------------------------
def fig11():
    p = need("effort_simulation_curves.csv", "effort_simulation_refit.csv")
    if not p:
        return print("fig11 skipped: run effort_simulation.py first", flush=True)
    cur, ref = pd.read_csv(p[0]), pd.read_csv(p[1])
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.1), gridspec_kw={"wspace": 0.3})
    ax = axes[0]
    for cid, g in cur.groupby("cell_id"):
        ax.plot(g.records_kept, g.raw_ratio, color=ORANGE, alpha=0.22, linewidth=1)
        ax.plot(g.records_kept, g.rare_ratio, color=BLUE, alpha=0.22, linewidth=1)
    m = cur.groupby("records_kept")[["raw_ratio", "rare_ratio"]].mean()
    ax.plot(m.index, m.raw_ratio, color=ORANGE, linewidth=2.4, marker="o", markersize=5)
    ax.plot(m.index, m.rare_ratio, color=BLUE, linewidth=2.4, marker="o", markersize=5)
    ax.text(m.index[2], m.raw_ratio.iloc[2] - 0.09, "Raw species count", color=ORANGE,
            fontsize=9, fontweight="bold")
    ax.text(m.index[1], 1.04, "Effort-corrected richness", color=BLUE, fontsize=9,
            fontweight="bold")
    ax.set_xscale("log"); ax.set_ylim(0, 1.15)
    ax.set_xticks([250, 1000, 10000, 100000]); ax.set_xticklabels(["250", "1,000", "10,000", "100,000"])
    ax.minorticks_off()
    ax.set_xlabel("Records kept after random thinning")
    ax.set_ylabel("Share of the full-data value")
    ax.set_title("a  One cell, less and less survey effort", loc="left", fontsize=10)
    hairline_grid(ax, "y")
    ax = axes[1]
    ax.axhline(ref.beta_full.iloc[0], color=INK, linewidth=0.9, linestyle=(0, (4, 3)))
    ax.text(ref.cap.iloc[-1], ref.beta_full.iloc[0] + 0.004, "all records: %+.3f" % ref.beta_full.iloc[0],
            ha="right", va="bottom", fontsize=8.5, color=INK2)
    ax.vlines(ref.cap, ref.beta_lo, ref.beta_hi, color=BLUE, linewidth=2)
    ax.plot(ref.cap, ref.beta_mean, "o", color=BLUE, markersize=7, markeredgecolor=SURFACE,
            markeredgewidth=1.2)
    for r in ref.itertuples():
        ax.text(r.cap, r.beta_lo - 0.006, "%+.3f" % r.beta_mean, ha="center", va="top",
                fontsize=8.2, color=INK2)
    ax.set_xscale("log"); ax.set_ylim(0.2, 0.3)
    ax.set_xticks(ref.cap); ax.set_xticklabels(["%s" % f"{c:,}" for c in ref.cap]); ax.minorticks_off()
    ax.set_xlabel("Every cell thinned to at most this many records")
    ax.set_ylabel("Richness coefficient for GPP (95% of repeats)")
    ax.set_title("b  The headline result on thinned data", loc="left", fontsize=10)
    hairline_grid(ax, "y")
    save(fig, "fig11_effort_simulation")
    cur.to_csv(os.path.join(OUT, "fig11a_thinning_curves.csv"), index=False)
    ref.to_csv(os.path.join(OUT, "fig11b_thinned_refit.csv"), index=False)


# ---- Fig 12: specification curve --------------------------------------------
def fig12():
    p = need("spec_curve.csv")
    if not p:
        return print("fig12 skipped: run spec_curve.py first", flush=True)
    d = pd.read_csv(p[0]).sort_values("beta").reset_index(drop=True)
    cols = {"OLS": BLUE, "ecoregion FE": ORANGE, "spatial error": AQUA}
    names = {"OLS": "Across regions (OLS)", "ecoregion FE": "Within ecoregions (fixed effects)",
             "spatial error": "Spatial error model"}
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.4), gridspec_kw={"width_ratios": [1.7, 1],
                                                                    "wspace": 0.22})
    ax = axes[0]
    x = np.arange(len(d))
    ax.vlines(x, d.beta - 1.96 * d.se, d.beta + 1.96 * d.se, color=NEUTRAL, linewidth=0.5, zorder=1)
    for k, c in cols.items():
        s = d[d.estimator == k]
        ax.scatter(s.index, s.beta, s=5, color=c, zorder=2, linewidth=0)
    ax.axhline(0, color=INK, linewidth=0.8)
    ax.set_xlabel("960 model specifications, sorted by coefficient")
    ax.set_ylabel("Richness coefficient (standardised, 95% interval)")
    ax.set_title("a  Every combination of response, richness measure, mask, controls and estimator",
                 loc="left", fontsize=10)
    hairline_grid(ax, "y")
    ax = axes[1]
    for i, (k, c) in enumerate(cols.items()):
        s = d[d.estimator == k].beta
        yy = np.random.default_rng(5 + i).uniform(-0.28, 0.28, len(s)) + i
        ax.scatter(s, yy, s=5, color=c, alpha=0.55, linewidth=0)
        ax.plot([s.median()] * 2, [i - 0.38, i + 0.38], color=INK, linewidth=1.6)
        ax.text(s.max() + 0.02, i, "median %+.2f" % s.median(), va="center", fontsize=8.5, color=INK2)
        ax.text(-0.06, i - 0.46, names[k], color=c, fontsize=9, fontweight="bold", va="bottom")
    ax.axvline(0, color=INK, linewidth=0.8)
    ax.set_yticks([]); ax.set_ylim(2.6, -0.75); ax.set_xlim(-0.08, 0.72)
    ax.set_xlabel("Richness coefficient")
    ax.set_title("b  The split is by estimator, not by data choice", loc="left", fontsize=10)
    hairline_grid(ax, "x")
    save(fig, "fig12_spec_curve")
    d.to_csv(os.path.join(OUT, "fig12_spec_curve.csv"), index=False)


# ---- Fig 13: flexible shape ---------------------------------------------------
def fig13():
    p = need("shape_spline_curves.csv")
    if not p:
        return print("fig13 skipped: run shape_spline.py first", flush=True)
    c = pd.read_csv(p[0])
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.9), sharey=True, gridspec_kw={"wspace": 0.08})
    for ax, grain, title in zip(axes, (1.0, 0.5), ("a  1° grid (221 cells)", "b  0.5° grid (672 cells)")):
        s = c[np.isclose(c.grain, grain)]
        ax.plot(s.rich_z, s.line, color=INK2, linewidth=1.6, linestyle=(0, (4, 3)))
        ax.plot(s.rich_z, s.spline, color=BLUE, linewidth=2.4)
        ax.text(s.rich_z.iloc[-1], s.line.iloc[-1] + 0.03, "Straight line", color=INK2, fontsize=8.8,
                ha="right", va="bottom")
        ax.text(s.rich_z.iloc[8], s.spline.iloc[8] - 0.05, "Flexible curve", color=BLUE, fontsize=8.8,
                fontweight="bold", va="top")
        ax.axhline(0, color=AXIS, linewidth=0.8)
        ax.set_xlabel("Effort-corrected richness (SD units)")
        ax.set_title(title, loc="left", fontsize=10)
        hairline_grid(ax)
    axes[0].set_ylabel("GPP, net of effort and climate (SD units)")
    save(fig, "fig13_shape")
    c.to_csv(os.path.join(OUT, "fig13_shape.csv"), index=False)


# ---- Fig 14: direction (path diagram) ----------------------------------------
def fig14():
    p = need("path_analysis_estimates.csv")
    if not p:
        return print("fig14 skipped: run path_analysis.py first", flush=True)
    e = pd.read_csv(p[0])
    e1 = e[np.isclose(e.grain.astype(float), 1.0)].set_index("quantity")
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off")
    boxes = {"Climate\n(temperature, rainfall)": (5, 5.1), "Bird richness\n(effort-corrected)": (2, 2.6),
             "Productivity\n(GPP)": (8, 2.6), "Topographic\nheterogeneity": (2, 0.6)}
    for label, (x, y) in boxes.items():
        ax.add_patch(FancyBboxPatch((x - 1.25, y - 0.48), 2.5, 0.96, boxstyle="round,pad=0.04",
                                    facecolor=SURFACE, edgecolor=INK2, linewidth=1))
        ax.text(x, y, label, ha="center", va="center", fontsize=9.5, color=INK)

    def arrow(a, b, color, style="-|>", lw=1.8, ls="-"):
        ax.add_patch(FancyArrowPatch(a, b, arrowstyle=style, mutation_scale=14, color=color,
                                     linewidth=lw, linestyle=ls))
    arrow((4.0, 4.62), (2.6, 3.1), INK2); arrow((6.0, 4.62), (7.4, 3.1), INK2)
    ax.text(2.75, 4.05, "drives both", fontsize=8.5, color=INK2, ha="right")
    arrow((3.28, 2.6), (6.72, 2.6), BLUE, style="<|-|>", lw=2.4)
    ax.text(5, 3.52, "link left after climate and effort", ha="center", fontsize=8.8, color=BLUE,
            fontweight="bold")
    ax.text(5, 3.36, "richness → GPP: %+.2f      GPP → richness: %+.2f\nthe two fit equally well; "
            "the data cannot choose" % (e1.loc["richness -> GPP path", "estimate"],
                                        e1.loc["GPP -> richness path", "estimate"]),
            ha="center", va="top", fontsize=8.6, color=INK2)
    arrow((2, 1.08), (2, 2.12), INK2)
    arrow((3.28, 0.75), (7.2, 2.14), ORANGE, ls=(0, (4, 3)))
    ax.text(5.9, 0.95, "still predicts GPP with richness held fixed,\nso it cannot be used to settle "
            "the direction", fontsize=8.5, color=ORANGE, ha="left", va="top")
    ax.text(0.2, 5.75, "About %.0f%% of the raw richness–GPP correlation is shared climate"
            % (100 * e1.loc["share of raw correlation due to shared climate", "estimate"]),
            fontsize=9.5, color=INK, fontweight="bold")
    save(fig, "fig14_direction")
    e.to_csv(os.path.join(OUT, "fig14_direction.csv"), index=False)


# ---- Fig 15: stability ---------------------------------------------------------
def fig15():
    p = need("extension_e_estimates.csv", "extension_e_cells.csv", "model_cells.csv")
    if not p:
        return print("fig15 skipped: run extension_e_stability.py first", flush=True)
    est = pd.read_csv(p[0]); cells = pd.read_csv(p[1]); model = pd.read_csv(p[2])
    d = model.merge(cells[["cell_id", "gpp_cv_detrended"]], on="cell_id")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), gridspec_kw={"width_ratios": [1, 1.25],
                                                                  "wspace": 0.45})
    ax = axes[0]
    ax.scatter(d.rarefied_250, 100 * d.gpp_cv_detrended, s=16, color=BLUE, alpha=0.7,
               edgecolor=SURFACE, linewidth=0.4)
    ax.set_yscale("log"); ax.set_yticks([3, 5, 10, 20]); ax.set_yticklabels(["3", "5", "10", "20"])
    ax.minorticks_off()
    r = np.corrcoef(d.rarefied_250, np.log(d.gpp_cv_detrended))[0, 1]
    ax.text(0.96, 0.95, "r = %+.2f" % r, transform=ax.transAxes, ha="right", va="top", fontsize=10)
    ax.set_xlabel("Bird species expected in 250 records")
    ax.set_ylabel("Year-to-year variation in GPP (%, 2001–2023)")
    ax.set_title("a  Richer cells look steadier", loc="left", fontsize=10)
    hairline_grid(ax)
    ax = axes[1]
    e = est[est.response == "log_cv"]
    specs = ["S1 usual controls", "S2 + climate variability", "S3 + mean GPP", "S3 within ecoregions",
             "S3 spatial error"]
    labels = ["Effort and mean climate", "+ rainfall and temperature\nvariability", "+ mean GPP",
              "Within ecoregions", "Spatial error model"]
    for tag, name, col, off in (("birds", "Birds", BLUE, -0.15), ("plants", "Plants", AQUA, 0.15)):
        s = e[e.taxon == tag].set_index("spec")
        if s.empty:
            continue
        for i, k in enumerate(specs):
            b, se = s.loc[k, "beta"], s.loc[k, "se"]
            ax.plot([b - 1.96 * se, b + 1.96 * se], [i + off] * 2, color=col, linewidth=1.8)
            ax.plot(b, i + off, "o", color=col, markersize=6.5, markeredgecolor=SURFACE,
                    markeredgewidth=1)
        b0 = s.loc[specs[0], "beta"]
        ax.text(b0, off * 3.2 - 0.02, name, color=col, fontsize=9, fontweight="bold", ha="center",
                va="bottom" if off < 0 else "top")
    ax.axvline(0, color=INK, linewidth=0.8)
    ax.set_yticks(range(len(specs))); ax.set_yticklabels(labels)
    ax.set_ylim(len(specs) - 0.5, -0.9)
    ax.set_xlabel("Richness coefficient for instability (negative = steadier)")
    ax.set_title("b  The link does not survive the controls", loc="left", fontsize=10)
    hairline_grid(ax, "x")
    save(fig, "fig15_stability")
    e.to_csv(os.path.join(OUT, "fig15b_stability_estimates.csv"), index=False)
    d[["cell_id", "lat_c", "lon_c", "rarefied_250", "gpp_cv_detrended"]].to_csv(
        os.path.join(OUT, "fig15a_stability_cells.csv"), index=False)


# ---- Fig 16: survey gaps -------------------------------------------------------
def fig16():
    p = need("survey_gaps_1p0.csv", "merged_cells.csv")
    if not p:
        return print("fig16 skipped: run survey_gaps.py first", flush=True)
    g = pd.read_csv(p[0]); m = pd.read_csv(p[1])
    land = m[m.wc_mode.notna()]
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.9), gridspec_kw={"wspace": 0.2})
    for ax, col, cmap, title, lab in (
            (axes[0], "completeness", BLUE_RAMP, "a  How complete the bird records are",
             "Sample coverage of the cell's bird records"),
            (axes[1], "priority", ORANGE_RAMP, "b  Survey priority: rich on paper, thin on records",
             "Priority (expected richness × missing coverage, 0–100)")):
        ax.add_collection(PatchCollection(cell_patches(land), facecolor=NEUTRAL, edgecolor=SURFACE,
                                          linewidth=0.5))
        pc = PatchCollection(cell_patches(g), cmap=cmap, edgecolor=SURFACE, linewidth=0.5)
        pc.set_array(g[col].values)
        pc.set_clim(0, 1 if col == "completeness" else 100)
        ax.add_collection(pc)
        if col == "priority":
            top = g.nlargest(15, "priority")
            ax.add_collection(PatchCollection(cell_patches(top), facecolor="none", edgecolor=INK,
                                              linewidth=1.1))
        draw_cases(ax, label=False); map_axes(ax)
        cb = fig.colorbar(pc, ax=ax, orientation="horizontal", pad=0.14, fraction=0.045, aspect=38)
        cb.set_label(lab, fontsize=8.5); cb.outline.set_visible(False)
        ax.set_title(title, loc="left", fontsize=10)
    axes[1].text(68.4, 5.5, "Outlined: the 15 highest priorities", fontsize=8.3, color=INK,
                 bbox=dict(boxstyle="round,pad=0.25", facecolor=SURFACE, edgecolor="none", alpha=0.9))
    axes[0].text(68.4, 5.5, "Grey: cropland, water or no natural cover", fontsize=8.3, color=INK,
                 bbox=dict(boxstyle="round,pad=0.25", facecolor=SURFACE, edgecolor="none", alpha=0.9))
    save(fig, "fig16_survey_gaps")
    g.to_csv(os.path.join(OUT, "fig16_survey_gaps.csv"), index=False)


# ---- Fig 17: three taxa --------------------------------------------------------
def fig17():
    p = need("extension_d_estimates.csv", "extension_d_more_estimates.csv")
    if not p:
        return print("fig17 skipped: run extension_d_plants.py and extension_d_more.py first",
                     flush=True)
    a = pd.read_csv(p[0]); a = a[a.response == "gpp"]
    b = pd.read_csv(p[1])
    rows = []
    for label, src, tag, part in (
            ("Birds, 1° grid", a, "birds (same cells)", None),
            ("Plants, 1° grid", a, "plants", None),
            ("Plants, 0.5° grid", b, "plants, rarefied at 100", "M2"),
            ("Butterflies and moths, 1° grid", b, "Lepidoptera, rarefied at 100", "M3")):
        s = src[src.taxon == tag]
        if part:
            s = s[s.part == part]
        s = s.set_index("spec")
        rows.append((label, int(s.loc["corrected", "n"]), s.loc["corrected", "beta"],
                     s.loc["corrected", "se"], s.loc["within", "beta"], s.loc["within", "se"]))
    fig, ax = plt.subplots(figsize=(8.2, 3.9))
    for i, (label, n, b1, s1, b2, s2) in enumerate(rows):
        for b_, s_, col, off in ((b1, s1, BLUE, -0.14), (b2, s2, ORANGE, 0.14)):
            ax.plot([b_ - 1.96 * s_, b_ + 1.96 * s_], [i + off] * 2, color=col, linewidth=1.8)
            ax.plot(b_, i + off, "o", color=col, markersize=6.5, markeredgecolor=SURFACE,
                    markeredgewidth=1)
            ax.text(b_ + 1.96 * s_ + 0.015, i + off, "%+.2f" % (b_ + 0.0), va="center",
                    fontsize=8.2, color=INK2)
    ax.text(rows[0][2], -0.52, "Across regions", color=BLUE, fontsize=9, fontweight="bold",
            ha="center", va="bottom")
    ax.text(rows[0][4], 0.5, "Within ecoregions", color=ORANGE, fontsize=9, fontweight="bold",
            ha="center", va="top")
    ax.axvline(0, color=INK, linewidth=0.8)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(["%s (n = %d)" % (r[0], r[1]) for r in rows])
    ax.set_ylim(len(rows) - 0.4, -0.95)
    ax.set_xlabel("Richness coefficient for GPP (standardised, 95% interval)")
    ax.set_title("Three groups of organisms, one pattern", loc="left", fontsize=10)
    hairline_grid(ax, "x")
    save(fig, "fig17_three_taxa")
    pd.DataFrame(rows, columns=["sample", "n", "beta_across", "se_across", "beta_within",
                                "se_within"]).to_csv(os.path.join(OUT, "fig17_three_taxa.csv"),
                                                     index=False)


def main():
    for i, f in enumerate((fig11, fig12, fig13, fig14, fig15, fig16, fig17), start=11):
        f(); print("fig%d done" % i, flush=True)


if __name__ == "__main__":
    main()
