# -*- coding: utf-8 -*-
"""Figures for the report (plan Week 6). Writes PNGs plus a CSV "table view" of
every plotted value to figures/.

Palette: reference categorical slots 1-3 (blue, orange, aqua), validated with
the dataviz validator against #ffffff (all-pairs PASS; aqua 2.82:1 contrast ->
relief rule: aqua marks are always direct-labelled). Magnitude maps use one-hue
light->dark ramps (blue; orange for the second simultaneous ramp).
"""
import os
import sys
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from matplotlib.collections import PatchCollection
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch, Rectangle
from scipy.stats import norm
from spreg import ML_Error

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "figures")
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, HERE)
from weights_sensitivity import queen_from_grid

# ---- tokens ---------------------------------------------------------------
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, AXIS, NEUTRAL = "#e1e0d9", "#c3c2b7", "#d9d8d2"
SURFACE = "#ffffff"
BLUE_RAMP = LinearSegmentedColormap.from_list(
    "blue", ["#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#184f95", "#0d366b"])
ORANGE_RAMP = LinearSegmentedColormap.from_list(
    "orange", ["#fde4d8", "#f6b496", "#eb6834", "#c24f1f", "#8f3612", "#5e2108"])

plt.rcParams.update({
    "font.family": ["Segoe UI", "DejaVu Sans"],
    "font.size": 9.5, "axes.titlesize": 11, "axes.titleweight": "bold",
    "axes.labelcolor": INK2, "axes.edgecolor": AXIS, "axes.linewidth": 0.8,
    "xtick.color": MUTED, "ytick.color": MUTED, "xtick.labelcolor": INK2,
    "ytick.labelcolor": INK2, "text.color": INK, "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE, "legend.frameon": False,
    "axes.spines.top": False, "axes.spines.right": False,
})

CASES = {"Western Ghats": (8, 16, 74, 77), "Thar Desert": (25, 30, 69, 74),
         "Eastern Himalaya": (26, 29, 88, 97)}
CTRL = ["log_effort", "temp_c", "precip_mm_yr"]
RICH = "rarefied_250"


def z(s):
    return (s - s.mean()) / s.std()


def hairline_grid(ax, axis="both"):
    ax.grid(True, axis=axis, color=GRID, linewidth=0.6, linestyle="-")
    ax.set_axisbelow(True)


def load():
    merged = pd.read_csv(os.path.join(DATA, "merged_cells.csv"))
    merged["wc_mode"] = merged.wc_mode.round()
    model = pd.read_csv(os.path.join(DATA, "model_cells.csv"))
    eco = pd.read_csv(os.path.join(DATA, "ecoregions_1p0.csv"))
    return merged, model, eco


def cell_patches(df, size=1.0):
    return [Rectangle((r.lon_c - size / 2, r.lat_c - size / 2), size, size)
            for r in df.itertuples()]


def map_axes(ax):
    ax.set_xlim(68, 102); ax.set_ylim(5, 31); ax.set_aspect("equal")
    ax.set_xlabel("Longitude (°E)"); ax.set_ylabel("Latitude (°N)")
    for s in ("top", "right"):
        ax.spines[s].set_visible(True)


def draw_cases(ax, label=True):
    for name, (a, b, c, d) in CASES.items():
        ax.add_patch(Rectangle((c, a), d - c, b - a, fill=False, edgecolor=INK,
                               linewidth=1.1))
        if label:
            ha, x = ("left", d + 0.4) if name != "Eastern Himalaya" else ("center", (c + d) / 2)
            y = (a + b) / 2 if name != "Eastern Himalaya" else b + 0.7
            # White backing: every label position sits on coloured cells.
            ax.text(x, y, name, fontsize=8.5, color=INK, ha=ha, va="center", zorder=5,
                    bbox=dict(boxstyle="round,pad=0.25", facecolor=SURFACE,
                              edgecolor="none", alpha=0.92))


# ---- Fig 1: study area and mask -------------------------------------------
def fig1(merged, model):
    land = merged[merged.wc_mode.notna()].copy()
    modelled = set(model.cell_id)
    land["cls"] = np.where(land.cell_id.isin(modelled), "modelled",
                  np.where(land.wc_mode.isin([40, 50]), "cropland", "other"))
    colours = {"modelled": BLUE, "cropland": ORANGE, "other": NEUTRAL}
    fig, ax = plt.subplots(figsize=(7.2, 5.8))
    for cls, col in colours.items():
        sub = land[land.cls == cls]
        ax.add_collection(PatchCollection(cell_patches(sub), facecolor=col,
                                          edgecolor=SURFACE, linewidth=0.8))
    draw_cases(ax)
    map_axes(ax)
    n = land.cls.value_counts()
    # Legend below the map: inside, it covered cells at every candidate position.
    ax.legend(handles=[
        Patch(facecolor=BLUE, label="Modelled (%d)" % n["modelled"]),
        Patch(facecolor=ORANGE, label="Excluded: cropland / built-up (%d)" % n["cropland"]),
        Patch(facecolor=NEUTRAL, label="Excluded: water, < 250 identified records, or no data (%d)" % n["other"])],
        loc="upper left", bbox_to_anchor=(0.0, -0.1), ncol=3, fontsize=8.2,
        handlelength=1.2, columnspacing=1.4)
    ax.set_title("Study region: 884 one-degree cells, 630 on land, %d modelled" % n["modelled"],
                 loc="left")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig1_study_area_mask.png"), dpi=220, bbox_inches="tight")
    plt.close(fig)
    land[["cell_id", "lat_c", "lon_c", "cls", "wc_mode"]].to_csv(
        os.path.join(OUT, "fig1_study_area_mask.csv"), index=False)


# ---- Fig 2: maps of corrected richness and GPP ------------------------------
def fig2(merged, model):
    land = merged[merged.wc_mode.notna()]
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.9))
    panels = [(RICH, "Effort-corrected bird richness\n(expected species in 250 records)",
               BLUE_RAMP, "species"),
              ("gpp", "Gross primary productivity\n(MODIS MOD17, 2019–2023 mean)",
               ORANGE_RAMP, "kg C m⁻² yr⁻¹")]
    for ax, (col, title, cmap, unit) in zip(axes, panels):
        ax.add_collection(PatchCollection(cell_patches(land), facecolor=NEUTRAL,
                                          edgecolor=SURFACE, linewidth=0.6))
        pc = PatchCollection(cell_patches(model), cmap=cmap, edgecolor=SURFACE,
                             linewidth=0.6)
        pc.set_array(model[col].values)
        ax.add_collection(pc)
        draw_cases(ax, label=False)
        map_axes(ax)
        ax.set_title(title, loc="left", fontsize=10.5)
        cb = fig.colorbar(pc, ax=ax, shrink=0.78, pad=0.02)
        cb.set_label(unit, color=INK2); cb.outline.set_visible(False)
        cb.ax.tick_params(colors=MUTED, labelcolor=INK2)
    fig.text(0.01, 0.01, "Grey: land cells excluded from the model. Boxes: the three "
             "case-study regions.", fontsize=8, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(os.path.join(OUT, "fig2_maps_richness_gpp.png"), dpi=220)
    plt.close(fig)
    model[["cell_id", "lat_c", "lon_c", RICH, "gpp"]].to_csv(
        os.path.join(OUT, "fig2_maps_richness_gpp.csv"), index=False)


# ---- Fig 3: attenuation through successive corrections ---------------------
def attenuation_rows(d, y):
    rows = []

    def clustered(xcols, fe=None):
        dd = d.copy()
        cols = list(dict.fromkeys([y] + xcols))
        for c in cols:
            dd[c] = z(dd[c].astype(float))
        X = dd[xcols]
        if fe:
            X = pd.concat([X, pd.get_dummies(dd[fe], drop_first=True, dtype=float)], axis=1)
        m = sm.OLS(dd[y], sm.add_constant(X)).fit(cov_type="cluster",
                                                  cov_kwds={"groups": dd.eco_name})
        return m.params[xcols[0]], m.bse[xcols[0]], m.pvalues[xcols[0]]

    # Rows are NOT cumulative, so they are labelled by exactly what each model
    # contains rather than with "+" steps. Grouped: measure / controls / spatial.
    rows.append(("Raw richness · no controls",) + clustered(["obs_richness"]))
    rows.append(("Corrected richness · no controls",) + clustered([RICH]))
    rows.append(("Corrected · effort, climate",) + clustered([RICH] + CTRL))
    rows.append(("Corrected · effort, climate, biome",)
                + clustered([RICH] + CTRL, "biome"))
    rows.append(("Corrected · effort, climate, ecoregion",)
                + clustered([RICH] + CTRL, "eco_name"))
    dd = d.copy()
    for c in [y, RICH] + CTRL:
        dd[c] = z(dd[c].astype(float))
    w = queen_from_grid(dd.lat_c.values, dd.lon_c.values, 1.0); w.transform = "r"
    s = ML_Error(dd[y].values.reshape(-1, 1), dd[[RICH] + CTRL].values, w=w)
    b, se = float(s.betas[1][0]), float(np.sqrt(s.vm[1, 1]))
    rows.append(("Corrected · effort, climate, spatial error",)
                + (b, se, 2 * (1 - norm.cdf(abs(b / se)))))
    return pd.DataFrame(rows, columns=["step", "beta", "se", "p"])


def fig3(model, eco):
    d = model.merge(eco, on="cell_id").dropna(subset=["eco_name"]).reset_index(drop=True)
    tab = []
    # y positions with a gap between the three groups (measure | controls | spatial)
    base_y = np.array([7.4, 6.4, 4.8, 3.8, 2.8, 1.2])
    fig, ax = plt.subplots(figsize=(8.8, 5.0))
    for k, (y, col, lab) in enumerate((("gpp", BLUE, "GPP"), ("npp", ORANGE, "NPP"))):
        r = attenuation_rows(d, y)
        r["response"] = lab
        tab.append(r)
        ypos = base_y + (0.14 if k == 0 else -0.14)
        ax.errorbar(r.beta, ypos, xerr=1.96 * r.se, fmt="o", color=col, ms=6,
                    elinewidth=1.6, capsize=0, label=lab, zorder=3,
                    markeredgecolor=SURFACE, markeredgewidth=1.0)
        ax.text(r.beta.iloc[0] + 1.96 * r.se.iloc[0] + 0.02, ypos[0], lab,
                color=INK2, fontsize=8.5, va="center")
    steps = tab[0].step.tolist()
    ax.set_yticks(base_y); ax.set_yticklabels(steps, color=INK)
    for yy in (5.6, 2.0):
        ax.axhline(yy, color=GRID, linewidth=0.8)
    for yy, txt in ((7.95, "Richness measure"), (5.35, "Corrected richness, adding controls"),
                    (1.75, "Alternative spatial treatment")):
        ax.text(1.0, yy, txt, transform=ax.get_yaxis_transform(), ha="right",
                fontsize=8, color=MUTED, style="italic")
    ax.set_ylim(0.6, 8.2)
    ax.axvline(0, color=AXIS, linewidth=1.0, zorder=1)
    hairline_grid(ax, "x")
    ax.set_xlabel("Standardised richness coefficient, 95% CI")
    ax.set_title("Climate and biogeography account for most of the association",
                 loc="left")
    ax.legend(loc="lower right", fontsize=8.5)
    ax.tick_params(axis="y", length=0)
    fig.text(0.01, 0.005, "Biome and ecoregion enter as fixed effects. SEs clustered by "
             "ecoregion (56 clusters), except the spatial error row (maximum-likelihood SEs). "
             "n = 220 cells.", fontsize=7.5, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(os.path.join(OUT, "fig3_attenuation.png"), dpi=220)
    plt.close(fig)
    pd.concat(tab).to_csv(os.path.join(OUT, "fig3_attenuation.csv"), index=False)


# ---- Fig 4: between vs within ecoregions -----------------------------------
def fwl(d, y, x, controls):
    X = sm.add_constant(controls)
    ry = sm.OLS(d[y].astype(float), X).fit().resid
    rx = sm.OLS(d[x].astype(float), X).fit().resid
    return rx, ry


def fig4(model, eco):
    d = model.merge(eco, on="cell_id").dropna(subset=["eco_name"]).reset_index(drop=True)
    multi = d.groupby("eco_name").cell_id.transform("size") >= 2
    dm = d[multi].reset_index(drop=True)
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.4))

    # Both panels are net of effort and climate, so the ONLY difference between
    # them is between- vs within-ecoregion variation. (An earlier version plotted
    # raw means on the left, which confounded the contrast with the climate control.)
    ax = axes[0]
    bx, by = fwl(dm, "gpp", RICH, dm[CTRL].astype(float))
    means = pd.DataFrame({"eco_name": dm.eco_name, "rich_adj": bx, "gpp_adj": by,
                          "n": 1}).groupby("eco_name").agg(
        rich_adj=("rich_adj", "mean"), gpp_adj=("gpp_adj", "mean"), n=("n", "sum"))
    mb = sm.OLS(means.gpp_adj, sm.add_constant(means.rich_adj)).fit(cov_type="HC3")
    ax.scatter(means.rich_adj, means.gpp_adj, s=34, color=BLUE, edgecolor=SURFACE,
               linewidth=1.0, zorder=3)
    xs = np.linspace(means.rich_adj.min(), means.rich_adj.max(), 50)
    ax.plot(xs, mb.params.iloc[0] + mb.params.iloc[1] * xs, color=INK2, linewidth=1.4)
    ax.axhline(0, color=AXIS, linewidth=0.9, zorder=1)
    ax.set_xlabel("Ecoregion mean richness, adjusted (species)")
    ax.set_ylabel("Ecoregion mean GPP, adjusted (kg C m⁻² yr⁻¹)")
    ax.set_title("Between ecoregions: positive", loc="left", fontsize=10.5)
    ax.text(0.03, 0.95, "%d ecoregions\nslope %.4f per species, p = %.3f, R² = %.2f"
            % (len(means), mb.params.iloc[1], mb.pvalues.iloc[1], mb.rsquared),
            transform=ax.transAxes, va="top", fontsize=8.5, color=INK2)
    hairline_grid(ax)

    ax = axes[1]
    controls = pd.concat([dm[CTRL].astype(float),
                          pd.get_dummies(dm.eco_name, drop_first=True, dtype=float)], axis=1)
    rx, ry = fwl(dm, "gpp", RICH, controls)
    mw = sm.OLS(ry, sm.add_constant(rx)).fit(cov_type="cluster",
                                             cov_kwds={"groups": dm.eco_name})
    ax.scatter(rx, ry, s=20, color=BLUE, alpha=0.75, edgecolor=SURFACE,
               linewidth=0.8, zorder=3)
    xs = np.linspace(rx.min(), rx.max(), 50)
    ax.plot(xs, mw.params.iloc[0] + mw.params.iloc[1] * xs, color=INK2, linewidth=1.4)
    ax.axhline(0, color=AXIS, linewidth=0.9, zorder=1)
    ax.set_xlabel("Richness, deviation within ecoregion, adjusted (species)")
    ax.set_ylabel("GPP, deviation within ecoregion, adjusted (kg C m⁻² yr⁻¹)")
    ax.set_title("Within ecoregions: much weaker, not significant", loc="left", fontsize=10.5)
    ax.text(0.03, 0.95, "%d cells in %d ecoregions\nslope %.4f per species, p = %.2f"
            % (len(dm), dm.eco_name.nunique(), mw.params.iloc[1], mw.pvalues.iloc[1]),
            transform=ax.transAxes, va="top", fontsize=8.5, color=INK2)
    hairline_grid(ax)
    fig.text(0.01, 0.005, "Both panels: GPP and richness adjusted for survey effort, temperature "
             "and precipitation (partial residuals). Ecoregions with ≥2 modelled cells. "
             "At 0.5° (n = 671) the within-ecoregion slope is +0.058 SD, p = 0.021.",
             fontsize=7.5, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(os.path.join(OUT, "fig4_between_within.png"), dpi=220)
    plt.close(fig)
    means.reset_index().to_csv(os.path.join(OUT, "fig4a_ecoregion_means.csv"), index=False)
    pd.DataFrame({"cell_id": dm.cell_id, "eco_name": dm.eco_name,
                  "richness_within_resid": rx, "gpp_within_resid": ry}).to_csv(
        os.path.join(OUT, "fig4b_within_residuals.csv"), index=False)


# ---- Fig 5: residual correlogram -------------------------------------------
def moran_by_distance(resid, lat, lon, edges):
    zr = (resid - resid.mean()) / resid.std()
    D = np.hypot(lat[:, None] - lat[None, :], lon[:, None] - lon[None, :])
    out = []
    for a, b in zip(edges[:-1], edges[1:]):
        Wm = ((D > a) & (D <= b)).astype(float)
        out.append((len(zr) / Wm.sum()) * (zr @ Wm @ zr) / (zr @ zr))
    return np.array(out)


def fig5(model, eco):
    d = model.merge(eco, on="cell_id").dropna(subset=["eco_name"]).reset_index(drop=True)
    edges = np.arange(0, 16.5, 1.5)
    mids = (edges[:-1] + edges[1:]) / 2
    X0 = sm.add_constant(d[[RICH] + CTRL].astype(float))
    X1 = pd.concat([X0, pd.get_dummies(d.eco_name, drop_first=True, dtype=float)], axis=1)
    r0 = sm.OLS(d.gpp.astype(float), X0).fit().resid.values
    r1 = sm.OLS(d.gpp.astype(float), X1).fit().resid.values
    I0 = moran_by_distance(r0, d.lat_c.values, d.lon_c.values, edges)
    I1 = moran_by_distance(r1, d.lat_c.values, d.lon_c.values, edges)
    fig, ax = plt.subplots(figsize=(7.6, 4.1))
    ax.axhline(0, color=AXIS, linewidth=1.0)
    for I, col, lab in ((I0, BLUE, "Corrected model (effort + climate)"),
                        (I1, ORANGE, "+ ecoregion fixed effects")):
        ax.plot(mids, I, color=col, linewidth=2, marker="o", ms=6,
                markeredgecolor=SURFACE, markeredgewidth=1.0, label=lab)
    # Direct labels where the two lines are furthest apart (near the origin);
    # at the right end they converge on the zero line and collide.
    ax.text(mids[0] + 0.35, I0[0], "Corrected model", color=INK2, fontsize=8.5,
            va="center")
    ax.text(mids[0] + 0.35, I1[0] + 0.035, "+ ecoregion fixed effects", color=INK2,
            fontsize=8.5, va="bottom")
    ax.axvspan(4.5, 9.0, color="#f0efec", zorder=0)
    ax.text(6.75, 0.62, "broad plateau", ha="center", fontsize=8, color=INK2)
    ax.set_xlim(0, 15.5)
    ax.set_xlabel("Distance between cells (degrees)")
    ax.set_ylabel("Residual Moran's I")
    ax.set_title("Ecoregion identity absorbs the broad-scale residual structure", loc="left")
    hairline_grid(ax, "y")
    ax.legend(loc="upper right", fontsize=8.5)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig5_correlogram.png"), dpi=220)
    plt.close(fig)
    pd.DataFrame({"dist_lo": edges[:-1], "dist_hi": edges[1:],
                  "moranI_corrected": I0, "moranI_ecoregion_FE": I1}).to_csv(
        os.path.join(OUT, "fig5_correlogram.csv"), index=False)


# ---- Fig 6: case-study spreads ---------------------------------------------
def fig6(model):
    rows = []
    for name, (a, b, c, e) in CASES.items():
        s = model[model.lat_c.between(a, b) & model.lon_c.between(c, e)]
        rows.append({"region": name, "Survey effort (median records/cell)": s.total_records.median(),
                     "GPP (mean)": s.gpp.mean(),
                     "Raw observed richness (mean)": s.obs_richness.mean(),
                     "Effort-corrected richness (mean)": s[RICH].mean()})
    t = pd.DataFrame(rows).set_index("region")
    fold = t / t.min()
    metrics = list(t.columns)
    fig, ax = plt.subplots(figsize=(8.4, 3.9))
    cols = {"Western Ghats": BLUE, "Thar Desert": ORANGE, "Eastern Himalaya": AQUA}
    # Small vertical dodge per region: on the raw-richness row Western Ghats (456)
    # and E Himalaya (450) coincide and one dot would otherwise hide the other.
    dodge = {"Western Ghats": 0.13, "Thar Desert": 0.0, "Eastern Himalaya": -0.13}
    top = len(metrics) - 1
    for i, m in enumerate(metrics[::-1]):
        ax.plot([1, fold[m].max()], [i, i], color=GRID, linewidth=2.5, zorder=1)
        for reg in t.index:
            ax.scatter(fold.loc[reg, m], i + dodge[reg], s=60, color=cols[reg],
                       edgecolor=SURFACE, linewidth=1.2, zorder=3)
            if i == top:   # direct-label regions on the widest-spread row (relief rule)
                # the region at 1x sits next to the y-axis: left-align it so the
                # label does not run through the axis line
                at_min = fold.loc[reg, m] <= 1.0001
                ax.text(fold.loc[reg, m] * (0.93 if at_min else 1.0), i + 0.32, reg,
                        ha="left" if at_min else "center", fontsize=8, color=INK2)
        ax.text(fold[m].max() * 1.12, i, "%.1f×" % fold[m].max(), va="center",
                fontsize=9, color=INK, fontweight="bold")
    ax.set_xscale("log")
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
        lambda v, _: "%g×" % v))
    ax.set_ylim(-0.5, top + 0.65)
    ax.set_yticks(range(len(metrics))); ax.set_yticklabels(metrics[::-1], color=INK)
    ax.set_xlabel("Value relative to the lowest of the three regions (log scale)")
    ax.set_xlim(0.8, 400)
    ax.set_title("Productivity varies 10-fold across the case studies; corrected richness barely moves",
                 loc="left", fontsize=10.5)
    hairline_grid(ax, "x")
    ax.tick_params(axis="y", length=0)
    ax.legend(handles=[Patch(facecolor=c, label=r) for r, c in cols.items()],
              loc="lower right", fontsize=8.2, ncol=1)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig6_case_study_spreads.png"), dpi=220)
    plt.close(fig)
    t.join(fold.add_suffix(" (fold)")).to_csv(os.path.join(OUT, "fig6_case_study_spreads.csv"))


# ---- Fig 7: Extension A scatter, naive vs corrected -------------------------
def fig7(model):
    d = model.copy()
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.3), sharey=True)
    specs = [("obs_richness", "Observed species richness (raw, effort-dependent)",
              "Naive: raw richness"),
             (RICH, "Effort-corrected richness (expected species in 250 records)",
              "Corrected: rarefied richness")]
    for ax, (col, xl, title) in zip(axes, specs):
        x, y = d[col].astype(float), d.gpp.astype(float)
        ax.scatter(x, y, s=22, color=BLUE, alpha=0.75, edgecolor=SURFACE, linewidth=0.8, zorder=3)
        ols = sm.OLS(y, sm.add_constant(x)).fit(cov_type="HC3")
        xs = np.linspace(x.min(), x.max(), 50)
        ax.plot(xs, ols.params.iloc[0] + ols.params.iloc[1] * xs, color=INK2, linewidth=1.4)
        r = np.corrcoef(x, d.log_effort)[0, 1]
        ax.set_xlabel(xl); ax.set_title(title, loc="left", fontsize=10.5)
        ax.text(0.03, 0.95, "R² = %.2f\ncorrelation with survey effort r = %.2f" % (ols.rsquared, r),
                transform=ax.transAxes, va="top", fontsize=8.5, color=INK2, zorder=5,
                bbox=dict(boxstyle="round,pad=0.3", facecolor=SURFACE, edgecolor="none",
                          alpha=0.92))
        hairline_grid(ax)
    axes[0].set_ylabel("GPP (kg C m⁻² yr⁻¹)")
    fig.text(0.01, 0.005, "n = 221 cells, same cells in both panels. Bivariate fits, no controls: "
             "the correction removes the effort signal from richness (r 0.81 → 0.24).",
             fontsize=7.5, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(os.path.join(OUT, "fig7_naive_vs_corrected.png"), dpi=220)
    plt.close(fig)
    d[["cell_id", "obs_richness", RICH, "log_effort", "gpp"]].to_csv(
        os.path.join(OUT, "fig7_naive_vs_corrected.csv"), index=False)


# ---- Fig 8: Extension B, linear vs quadratic --------------------------------
def fig8(model):
    d = model.copy()
    x = d[RICH].astype(float); xc = x - x.mean()
    # partial out effort and climate so the curve shows the richness term only
    C = sm.add_constant(d[CTRL].astype(float))
    ry = sm.OLS(d.gpp.astype(float), C).fit().resid
    rx = sm.OLS(xc, C).fit().resid
    fig, ax = plt.subplots(figsize=(7.4, 4.5))
    ax.scatter(rx, ry, s=22, color=BLUE, alpha=0.7, edgecolor=SURFACE, linewidth=0.8, zorder=3)
    xs = np.linspace(rx.min(), rx.max(), 100)
    lin = sm.OLS(ry, sm.add_constant(rx)).fit()
    X2 = np.column_stack([np.ones(len(rx)), rx, rx ** 2])
    b2 = np.linalg.lstsq(X2, ry.values, rcond=None)[0]
    ax.plot(xs, lin.params.iloc[0] + lin.params.iloc[1] * xs, color=INK2, linewidth=1.6)
    ax.plot(xs, b2[0] + b2[1] * xs + b2[2] * xs ** 2, color=ORANGE, linewidth=1.8)
    ax.text(xs[-1], lin.params.iloc[0] + lin.params.iloc[1] * xs[-1], "  linear", color=INK2,
            fontsize=8.5, va="center")
    ax.text(xs[-1], b2[0] + b2[1] * xs[-1] + b2[2] * xs[-1] ** 2 + 0.03, "  quadratic",
            color=INK, fontsize=8.5, va="center")
    ax.axhline(0, color=AXIS, linewidth=0.9, zorder=1)
    ax.set_xlim(rx.min() - 2, rx.max() + 22)
    ax.set_xlabel("Effort-corrected richness, adjusted for effort and climate (species)")
    ax.set_ylabel("GPP, adjusted (kg C m⁻² yr⁻¹)")
    ax.set_title("No evidence of a hump: the two fits are indistinguishable (ΔAIC +1.9)",
                 loc="left", fontsize=10.5)
    hairline_grid(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig8_linear_vs_quadratic.png"), dpi=220)
    plt.close(fig)
    pd.DataFrame({"cell_id": d.cell_id, "richness_adj": rx, "gpp_adj": ry}).to_csv(
        os.path.join(OUT, "fig8_linear_vs_quadratic.csv"), index=False)


def main():
    merged, model, eco = load()
    fig1(merged, model); print("fig1 done", flush=True)
    fig2(merged, model); print("fig2 done", flush=True)
    fig3(model, eco); print("fig3 done", flush=True)
    fig4(model, eco); print("fig4 done", flush=True)
    fig5(model, eco); print("fig5 done", flush=True)
    fig6(model); print("fig6 done", flush=True)
    fig7(model); print("fig7 done", flush=True)
    fig8(model); print("fig8 done", flush=True)


if __name__ == "__main__":
    main()
