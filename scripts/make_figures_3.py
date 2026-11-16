# -*- coding: utf-8 -*-
"""Figures 18-21 (added 2026-11-16, inference batch). Same tokens as make_figures.py;
each PNG has a CSV of its plotted values beside it.

  fig18_ecoregion_slopes     the slope inside each ecoregion, and their pooled value
  fig19_scale_bands          the slope at each spatial scale
  fig20_within_bounds        how small the within-ecoregion effect is, five samples
  fig21_flexible_controls    the coefficient under linear and non-linear controls
"""
import os
import sys
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from make_figures import (AQUA, AXIS, BLUE, DATA, INK, INK2, MUTED, NEUTRAL, ORANGE, OUT,
                          SURFACE, hairline_grid)


def need(*names):
    paths = [os.path.join(DATA, n) for n in names]
    return paths if all(os.path.exists(p) for p in paths) else None


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + ".png"), dpi=220, bbox_inches="tight")
    plt.close(fig)


# ---- Fig 18: slopes by ecoregion ----------------------------------------------
def fig18():
    p = need("ecoregion_slopes.csv")
    if not p:
        return print("fig18 skipped: run within_effect_bounds.py first", flush=True)
    s = pd.read_csv(p[0]); s = s[np.isclose(s.grain.astype(float), 0.5)]
    pooled = s[s.eco_name.str.startswith("POOLED")].iloc[0]
    e = s[~s.eco_name.str.startswith("POOLED")].sort_values("beta").reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(8.6, 9.2))
    ax.axvspan(pooled.pi_lo, pooled.pi_hi, color=NEUTRAL, alpha=0.45, zorder=0)
    ax.axvline(0, color=INK, linewidth=0.8, zorder=1)
    ax.axvline(pooled.beta, color=BLUE, linewidth=1, linestyle=(0, (4, 3)), zorder=1)
    for i, r in e.iterrows():
        sig = (r.beta - 1.96 * r.se > 0) or (r.beta + 1.96 * r.se < 0)
        col = BLUE if sig and r.beta > 0 else ORANGE if sig else MUTED
        ax.plot([r.beta - 1.96 * r.se, r.beta + 1.96 * r.se], [i, i], color=col, linewidth=1.4)
        ax.plot(r.beta, i, "o", color=col, markersize=3.5 + 0.12 * r.n, markeredgecolor=SURFACE,
                markeredgewidth=0.8)
    y0 = len(e) + 0.6
    d = 1.96 * pooled.se
    ax.fill([pooled.beta - d, pooled.beta, pooled.beta + d, pooled.beta],
            [y0, y0 - 0.38, y0, y0 + 0.38], color=BLUE)
    ax.set_yticks(list(range(len(e))) + [y0])
    ax.set_yticklabels(["%s (%d)" % (n[:46], k) for n, k in zip(e.eco_name, e.n)]
                       + ["All 35 ecoregions, pooled"], fontsize=8.2)
    ax.get_yticklabels()[-1].set_fontweight("bold")
    ax.set_ylim(-0.8, y0 + 1.0)
    ax.set_xlim(-1.0, 1.0)
    ax.set_xlabel("Slope of GPP on richness inside the ecoregion (standardised, 95% interval)")
    ax.set_title("Inside ecoregions the slope is small, positive on average, and varies", loc="left",
                 fontsize=10)
    ax.text(pooled.beta + 0.03, y0 + 0.75, "pooled %+.3f [%+.3f, %+.3f]"
            % (pooled.beta, pooled.beta - d, pooled.beta + d), color=BLUE, fontsize=8.6,
            fontweight="bold", va="center")
    ax.text(0.985, 0.40, "Grey band: where the slope of a new ecoregion is expected to fall (95%).\n"
            "Blue and orange: individually significant. Marker size: number of cells.",
            transform=ax.transAxes, fontsize=8, color=INK2, ha="right", va="center",
            bbox=dict(boxstyle="round,pad=0.3", facecolor=SURFACE, edgecolor="none", alpha=0.9))
    hairline_grid(ax, "x")
    save(fig, "fig18_ecoregion_slopes")
    s.to_csv(os.path.join(OUT, "fig18_ecoregion_slopes.csv"), index=False)


# ---- Fig 19: slope by spatial scale ---------------------------------------------
def fig19():
    p = need("scale_bands.csv")
    if not p:
        return print("fig19 skipped: run scale_decomposition.py first", flush=True)
    s = pd.read_csv(p[0]); s = s[~s.band.str.startswith("effective")]
    order = ["1 broadest", "2", "3", "4 finest", "no spatial structure"]
    labels = ["Broadest\npatterns", "Broad", "Fine", "Finest\npatterns", "No spatial\nstructure"]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3), gridspec_kw={"wspace": 0.25})
    ax = axes[0]
    for grain, col, off, name in ((1.0, BLUE, -0.12, "1° grid"), (0.5, ORANGE, 0.12, "0.5° grid")):
        g = s[np.isclose(s.grain.astype(float), grain)].set_index("band").loc[order]
        x = np.arange(len(order)) + off
        ax.vlines(x, g.slope - 1.96 * g.se, g.slope + 1.96 * g.se, color=col, linewidth=1.8)
        ax.plot(x, g.slope, "o", color=col, markersize=7, markeredgecolor=SURFACE, markeredgewidth=1)
        ax.text(x[0] + (0.1 if off > 0 else -0.1), g.slope.iloc[0], name, color=col, fontsize=9,
                fontweight="bold", va="center", ha="left" if off > 0 else "right")
    ax.axhline(0, color=INK, linewidth=0.8)
    ax.set_xticks(range(len(order))); ax.set_xticklabels(labels)
    ax.set_xlim(-0.75, len(order) - 0.5)
    ax.set_ylabel("Slope of GPP on richness in that band (95% interval)")
    ax.set_title("a  The link is in the broadest spatial patterns", loc="left", fontsize=10)
    hairline_grid(ax, "y")
    ax = axes[1]
    g = s[np.isclose(s.grain.astype(float), 0.5)].set_index("band").loc[order]
    x = np.arange(len(order)); w = 0.36
    ax.bar(x - w / 2 - 0.02, 100 * g.share_gpp, w, color=ORANGE)
    ax.bar(x + w / 2 + 0.02, 100 * g.share_richness, w, color=BLUE)
    ax.text(x[0] - w / 2 - 0.02, 100 * g.share_gpp.iloc[0] + 1.5, "Productivity", color=ORANGE,
            fontsize=9, fontweight="bold", ha="center")
    ax.text(x[-1] + w / 2 + 0.02, 100 * g.share_richness.iloc[-1] + 1.5, "Richness", color=BLUE,
            fontsize=9, fontweight="bold", ha="center")
    for xi, a, b in zip(x, 100 * g.share_gpp, 100 * g.share_richness):
        if xi != 0:
            ax.text(xi - w / 2 - 0.02, a + 1.2, "%.0f" % a, ha="center", fontsize=8.2, color=INK2)
        if xi != len(order) - 1:
            ax.text(xi + w / 2 + 0.02, b + 1.2, "%.0f" % b, ha="center", fontsize=8.2, color=INK2)
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_ylim(0, 86)
    ax.set_ylabel("Share of the variation left after climate (%)")
    ax.set_title("b  Where each variable varies (0.5° grid)", loc="left", fontsize=10)
    hairline_grid(ax, "y")
    save(fig, "fig19_scale_bands")
    s.to_csv(os.path.join(OUT, "fig19_scale_bands.csv"), index=False)


# ---- Fig 20: bounds on the within-ecoregion effect ------------------------------
def fig20():
    p = need("within_bounds.csv")
    if not p:
        return print("fig20 skipped: run within_effect_bounds.py first", flush=True)
    b = pd.read_csv(p[0])
    names = {"birds, 1 degree": "Birds, 1°", "birds, 0.5 degree": "Birds, 0.5°",
             "plants, 1 degree": "Plants, 1°", "plants, 0.5 degree": "Plants, 0.5°",
             "butterflies and moths, 1 degree": "Butterflies and moths, 1°"}
    fig, ax = plt.subplots(figsize=(8.8, 4.2))
    for i, r in b.iterrows():
        ax.fill_betweenx([i - 0.32, i + 0.32], -r.half_bound, r.half_bound, color=NEUTRAL,
                         alpha=0.6, linewidth=0)
        ax.plot([r.lo90, r.hi90], [i, i], color=ORANGE, linewidth=2)
        ax.plot(r.beta_within, i, "o", color=ORANGE, markersize=7, markeredgecolor=SURFACE,
                markeredgewidth=1)
        ax.plot(r.beta_across, i, "D", color=BLUE, markersize=6.5, markeredgecolor=SURFACE,
                markeredgewidth=1)
        ax.text(r.beta_across + 0.02, i, "%+.2f" % r.beta_across, va="center", fontsize=8.2,
                color=BLUE)
    ax.text(b.beta_across.iloc[0], -0.62, "Across regions", color=BLUE, fontsize=9,
            fontweight="bold", ha="center")
    ax.text(b.beta_within.iloc[0], -0.62, "Within ecoregions\n(90% interval)", color=ORANGE,
            fontsize=9, fontweight="bold", ha="center", va="center")
    ax.axvline(0, color=INK, linewidth=0.8)
    ax.set_yticks(range(len(b)))
    ax.set_yticklabels(["%s (n = %d)" % (names.get(s_, s_), n) for s_, n in zip(b["sample"], b.n)])
    ax.set_ylim(len(b) - 0.4, -1.15)
    ax.set_xlabel("Richness coefficient for GPP (standardised)")
    ax.set_title("In every sample the within-ecoregion effect is shown to be less than half "
                 "the across-region one", loc="left", fontsize=10)
    ax.text(0.99, 0.03, "Grey band: half the across-region effect, either side of zero",
            transform=ax.transAxes, fontsize=8.2, color=INK2, ha="right")
    hairline_grid(ax, "x")
    save(fig, "fig20_within_bounds")
    b.to_csv(os.path.join(OUT, "fig20_within_bounds.csv"), index=False)


# ---- Fig 21: flexible controls ----------------------------------------------------
def fig21():
    p = need("dml_estimates.csv")
    if not p:
        return print("fig21 skipped: run dml_flexible.py first", flush=True)
    d = pd.read_csv(p[0])
    learners = ["linear", "random forest", "gradient boosting"]
    labels = ["Straight-line\ncontrols", "Random forest", "Gradient\nboosting"]
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.1), sharey=True, gridspec_kw={"wspace": 0.08})
    for ax, grain, title in zip(axes, (1.0, 0.5), ("a  1° grid", "b  0.5° grid")):
        g = d[np.isclose(d.grain.astype(float), grain)]
        for controls, col, off, name in (("environment", BLUE, -0.12, "Across regions"),
                                         ("within ecoregions", ORANGE, 0.12, "Within ecoregions")):
            s = g[g.controls == controls].set_index("learner").loc[learners]
            x = np.arange(3) + off
            ax.vlines(x, s.theta - 1.96 * s.se, s.theta + 1.96 * s.se, color=col, linewidth=1.8)
            ax.plot(x, s.theta, "o", color=col, markersize=7, markeredgecolor=SURFACE,
                    markeredgewidth=1)
            for xi, t in zip(x, s.theta):
                ax.text(xi + (0.09 if off > 0 else -0.09), t, "%+.2f" % t, fontsize=8.2, color=INK2,
                        va="center", ha="left" if off > 0 else "right")
            if grain == 0.5:                 # direct labels in the empty top-right corner
                ax.text(0.97, 0.95 if off < 0 else 0.87, name, transform=ax.transAxes, color=col,
                        fontsize=9, fontweight="bold", ha="right", va="top")
        ax.axhline(0, color=INK, linewidth=0.8)
        ax.set_xticks(range(3)); ax.set_xticklabels(labels)
        ax.set_xlim(-0.6, 2.6)
        ax.set_title(title, loc="left", fontsize=10)
        hairline_grid(ax, "y")
    axes[0].set_ylabel("Richness coefficient for GPP (95% interval)")
    save(fig, "fig21_flexible_controls")
    d.to_csv(os.path.join(OUT, "fig21_flexible_controls.csv"), index=False)


def main():
    for i, f in enumerate((fig18, fig19, fig20, fig21), start=18):
        f(); print("fig%d done" % i, flush=True)


if __name__ == "__main__":
    main()
