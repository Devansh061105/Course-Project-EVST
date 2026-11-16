# -*- coding: utf-8 -*-
"""Re-run every ANALYSIS script from cached data and check headline numbers.

Data-acquisition scripts (GBIF pulls, Earth Engine extractions) are not re-run;
everything downstream of the cached data is. Each script's output goes to
data/repro/<script>.log. Then each documented headline number is located in the
fresh logs and compared with the value recorded in the docs.

Usage: python reproduce_all.py          (prints a PASS/FAIL table at the end)
"""
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LOGS = os.path.abspath(os.path.join(HERE, "..", "data", "repro"))
os.makedirs(LOGS, exist_ok=True)

# order matters: merge_and_extA regenerates merged_cells.csv / model_cells.csv
SCRIPTS = [
    "merge_and_extA.py", "spatial_refit.py", "weights_sensitivity.py",
    "extension_b.py", "extension_c.py", "scan_contrast_region.py",
    "adjudicate_lag_error.py", "spatial_cv.py", "hawkins_subsample.py",
    "robustness_suite.py", "confounder_analysis.py", "ecoregion_analysis.py",
    "coverage_rarefaction.py", "gbif_timewindow.py", "grain_0p5_analysis.py",
    "grain_0p5_extended.py", "local_slopes.py", "extension_d_plants.py",
    "extension_d_more.py", "path_analysis.py", "effort_simulation.py",
    "shape_spline.py", "spec_curve.py", "survey_gaps.py",
    "extension_e_stability.py", "extension_f_protected.py",
    "make_figures.py", "make_figures_2.py",
]

# (script, regex on its log, documented value, tolerance, what it is)
CHECKS = [
    ("merge_and_extA.py", r"corrected n = (\d+)", 221, 0, "model cells"),
    ("merge_and_extA.py", r"corrected richness coef = \+([\d.]+)", 0.0109704, 1e-6, "corrected OLS coef (raw units)"),
    ("spatial_refit.py", r"spatial error\s+beta=\+([\d.]+)", 0.00069, 1e-5, "SEM richness beta (raw units)"),
    ("spatial_refit.py", r"spatial error\s+beta=\+[\d.]+\s+se=[\d.]+\s+p=([\d.]+)", 0.5059, 1e-3, "SEM richness p"),
    ("weights_sensitivity.py", r"richness significant \(p<0.05\) under: \['(\w+)'\]", "knn12", None, "only significant weights spec"),
    ("extension_b.py", r"OLS\s+linear AIC=\s+([\d.]+)", 342.32, 0.01, "Ext B primary linear AIC"),
    ("extension_c.py", r"effort spread: (\d+)x", 139, 0, "case-study effort spread"),
    ("extension_c.py", r"GPP spread:\s+([\d.]+)x", 10.03, 0.01, "case-study GPP spread"),
    ("extension_c.py", r"rarefied-richness spread: ([\d.]+)x", 1.29, 0.01, "case-study corrected-richness spread"),
    ("scan_contrast_region.py", r"25-30N\s+69-74E\s+\d+\s+(\d+)", 241, 0, "Thar precipitation (mm)"),
    ("adjudicate_lag_error.py", r"SDEM\s+-?[\d.]+\s+([\d.]+)", 128.67, 0.01, "SDEM AIC at 1 deg"),
    ("adjudicate_lag_error.py", r"SDM\s+vs SAR\s+LR=\s+([\d.]+)", 78.60, 0.01, "LR SDM vs SAR"),
    ("spatial_cv.py", r"leave-block-out 4 deg.*?\(\+([\d.]+)%\)", 9.4, 0.05, "4-deg block CV gain %"),
    ("hawkins_subsample.py", r"spaced >= 3.0 deg[\s\S]*?median \+([\d.]+)", 0.268, 0.001, "Hawkins median beta @3 deg"),
    ("robustness_suite.py", r"response = NPP.*?SEM \+([\d.]+) \(p=([\d.]+)\)", 0.093, 0.001, "NPP SEM beta"),
    ("confounder_analysis.py", r"\+ all confounders\s+OLS \+([\d.]+)", 0.242, 0.001, "GPP OLS + all confounders"),
    ("ecoregion_analysis.py", r"C  \+ ecoregion fixed effects.*?beta \+([\d.]+)", 0.030, 0.001, "within-ecoregion GPP beta"),
    ("ecoregion_analysis.py", r"C  \+ ecoregion fixed effects.*?p=([\d.]+)", 0.5865, 1e-3, "within-ecoregion GPP p"),
    ("ecoregion_analysis.py", r"C  \+ ecoregion fixed effects.*?plateau I=([-+][\d.]+)", -0.027, 0.001, "plateau after ecoregion FE"),
    ("coverage_rarefaction.py", r"rarefied_250\s+within-ecoregion share of variance:\s+([\d.]+)%", 38.5, 0.05, "richness variance within ecoregions %"),
    ("gbif_timewindow.py", r"GPP 2019-23:.*within-ecoregion \+([\d.]+)", 0.003, 0.001, "2019-23 within-ecoregion GPP beta"),
    ("grain_0p5_analysis.py", r"A  baseline\s+beta \+([\d.]+)", 0.228, 0.001, "0.5 deg baseline beta"),
    ("grain_0p5_analysis.py", r"C  \+ ecoregion fixed effects \(within\)\s+beta \+([\d.]+)", 0.058, 0.001, "0.5 deg within-ecoregion beta"),
    ("grain_0p5_analysis.py", r"C  \+ ecoregion fixed effects \(within\)\s+beta \+[\d.]+\s+se [\d.]+\s+p=([\d.]+)", 0.0212, 0.0005, "0.5 deg within-ecoregion p"),
    ("grain_0p5_analysis.py", r"spatial error \(queen, \d+ island cells\): beta \+([\d.]+)", 0.090, 0.001, "0.5 deg spatial error beta"),
    ("grain_0p5_extended.py", r"\+ both  \(full within model\)\s+beta \+([\d.]+)", 0.051, 0.001, "0.5 deg full within model, GPP"),
    ("grain_0p5_extended.py", r"64 refits: beta range \+([\d.]+)", 0.046, 0.001, "leave-one-ecoregion-out min beta"),
    ("local_slopes.py", r"GWR 1\.0: k = (\d+) neighbours", 32, 0, "GWR 1 deg window (neighbours)"),
    ("local_slopes.py", r"GWR 1\.0: local richness beta .*?median \+([\d.]+)", 0.026, 0.001, "GWR 1 deg median local slope"),
    ("local_slopes.py", r"GWR 0\.5: local richness beta .*?median \+([\d.]+)", 0.036, 0.001, "GWR 0.5 deg median local slope"),
    ("local_slopes.py", r"GWR 1\.0: stationarity Monte Carlo.*?p = ([\d.]+)", 0.918, 0.001, "GWR 1 deg stationarity p"),
    ("extension_d_plants.py", r"PLANTS corrected GPP beta = \+([\d.]+)", 0.264, 0.001, "Ext D plant corrected beta"),
    ("extension_d_plants.py", r"plants, response GPP[\s\S]*?ecoregion fixed effects \(within\)\s+n=\d+\s+beta ([-+][\d.]+)", -0.027, 0.001, "Ext D plant within-ecoregion beta"),
    ("extension_d_plants.py", r"birds \(same cells\), response GPP[\s\S]*?corrected: \+ effort \+ temp \+ precip \(HC3\)\s+n=\d+\s+beta \+([\d.]+)", 0.277, 0.001, "Ext D birds on shared cells beta"),
    ("extension_d_plants.py", r"effort-corrected: r = \+([\d.]+)", 0.299, 0.001, "Ext D bird-plant congruence r"),
    ("extension_d_more.py", r"M1 plants 4-degree block CV: adding richness cuts out-of-sample MSE by ([\d.]+)%", 15.4, 0.1, "Ext D plant block CV gain %"),
    ("extension_d_more.py", r"M2 plants 0\.5 deg: corrected beta = \+([\d.]+)", 0.228, 0.001, "Ext D plants 0.5 deg beta"),
    ("extension_d_more.py", r"M3 lepidoptera: corrected beta = \+([\d.]+)", 0.512, 0.001, "Ext D Lepidoptera beta"),
    ("path_analysis.py", r"PATH 1\.0: richness -> GPP \| climate, effort\s+beta = \+([\d.]+)", 0.273, 0.001, "path richness -> GPP"),
    ("path_analysis.py", r"PATH 1\.0: GPP -> richness \| climate, effort\s+beta = \+([\d.]+)", 0.378, 0.001, "path GPP -> richness"),
    ("path_analysis.py", r"IV 1\.0 VERDICT: not (valid)", "valid", None, "IV instrument rejected"),
    ("effort_simulation.py", r"SIM at 250 records kept: raw richness falls to ([\d.]+)%", 23.1, 0.2, "thinning: raw richness % kept"),
    ("effort_simulation.py", r"rarefied richness stays at ([\d.]+)%", 99.8, 0.2, "thinning: corrected richness % kept"),
    ("effort_simulation.py", r"REFIT cap 1,000\s+beta = \+([\d.]+)", 0.268, 0.002, "beta with cells thinned to 1,000"),
    ("shape_spline.py", r"SPLINE 1\.0: 3-parameter spline vs line: dAIC = ([-+][\d.]+)", -6.66, 0.02, "spline dAIC at 1 deg"),
    ("shape_spline.py", r"SPLINE 0\.5: 3-parameter spline vs line: dAIC = ([-+][\d.]+)", 3.40, 0.02, "spline dAIC at 0.5 deg"),
    ("shape_spline.py", r"TAIL 1\.0: slope among the richest quarter \+([\d.]+)", 0.440, 0.001, "slope in richest quarter, 1 deg"),
    ("shape_spline.py", r"TAIL 0\.5: slope among the richest quarter \+([\d.]+)", 0.295, 0.001, "slope in richest quarter, 0.5 deg"),
    ("spec_curve.py", r"SPEC OLS\s+\d+\s+\+([\d.]+)", 0.240, 0.001, "spec curve median, OLS"),
    ("spec_curve.py", r"SPEC ecoregion FE\s+\d+\s+\+([\d.]+)", 0.039, 0.001, "spec curve median, within"),
    ("spec_curve.py", r"significantly negative models: (\d+)", 0, 0, "spec curve negative models"),
    ("survey_gaps.py", r"leave-one-4-degree-block-out R2 ([\d.]+)", 0.464, 0.001, "survey-gap model CV R2"),
    ("survey_gaps.py", r"too few records: (\d+)", 46, 0, "natural cells not modelled"),
    ("extension_e_stability.py", r"STAB birds: richness coefficient for instability, full controls: \+([\d.]+)", 0.144, 0.001, "Ext E birds instability beta"),
    ("extension_e_stability.py", r"STAB plants:.*?within ecoregions \+([\d.]+)", 0.002, 0.001, "Ext E plants within beta"),
    ("extension_f_protected.py", r"PROT 1\.0: effort ~ strict protection beta = \+([\d.]+)", 0.010, 0.001, "Ext F effort ~ protection"),
    ("extension_f_protected.py", r"PROT 0\.5 excl\. India and China:.*?interaction = \+([\d.]+)", 0.064, 0.001, "Ext F interaction, subset"),
]


def main():
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    status = {}
    for s in SCRIPTS:
        t0 = time.time()
        with open(os.path.join(LOGS, s.replace(".py", ".log")), "w", encoding="utf-8") as f:
            r = subprocess.run([sys.executable, "-u", s], cwd=HERE, stdout=f,
                               stderr=subprocess.STDOUT, env=env, timeout=1500)
        status[s] = r.returncode
        print("%-28s exit %d  %5.0fs" % (s, r.returncode, time.time() - t0), flush=True)

    print("\n%-38s %12s %12s  %s" % ("check", "documented", "reproduced", "result"))
    print("-" * 80)
    npass = 0
    for s, rx, want, tol, what in CHECKS:
        txt = open(os.path.join(LOGS, s.replace(".py", ".log")), encoding="utf-8").read()
        m = re.search(rx, txt)
        if not m:
            print("%-38s %12s %12s  NOT FOUND" % (what[:38], want, "-"))
            continue
        got = m.group(1)
        if tol is None:
            ok = got == want
        else:
            ok = abs(float(got) - float(want)) <= tol
        npass += ok
        print("%-38s %12s %12s  %s" % (what[:38], want, got, "PASS" if ok else "FAIL"))
    nok = sum(v == 0 for v in status.values())
    print("\n%d/%d checks pass; %d/%d scripts exited 0"
          % (npass, len(CHECKS), nok, len(status)))
    # Non-zero exit when anything fails, so a CI run goes red.
    sys.exit(0 if npass == len(CHECKS) and nok == len(status) else 1)


if __name__ == "__main__":
    main()
