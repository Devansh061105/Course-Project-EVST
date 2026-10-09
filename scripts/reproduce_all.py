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
    "grain_0p5_extended.py", "make_figures.py",
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
    print("\n%d/%d checks pass; %d/%d scripts exited 0"
          % (npass, len(CHECKS), sum(v == 0 for v in status.values()), len(status)))


if __name__ == "__main__":
    main()
