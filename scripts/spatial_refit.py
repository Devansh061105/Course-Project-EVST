# -*- coding: utf-8 -*-
"""Plan Step 8: correct the corrected model for spatial dependence.

Moran's I on the OLS residuals was 0.723 (z=15.73, p=0.001), so the HC3
p-values from Extension A are optimistic. This refits the same specification
three ways and compares what survives:

  1. OLS + HC3                  (what Extension A reported)
  2. OLS + cluster-robust SEs   (clusters = 4-degree spatial blocks)
  3. Spatial lag / spatial error ML models (spreg)

The coefficient of interest throughout is rarefied richness. The question is
not whether it changes sign - it is whether it stays significant once the
non-independence of neighbouring cells is taken seriously.
"""
import os
import sys

import numpy as np
import pandas as pd
import statsmodels.api as sm
import libpysal
import esda
from spreg import ML_Lag, ML_Error

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))

X_COLS = ["rarefied_250", "log_effort", "temp_c", "precip_mm_yr"]
Y = "gpp"
BLOCK = 4.0          # cluster size in degrees

d = pd.read_csv(os.path.join(DATA, "model_cells.csv"))
print("n = %d cells" % len(d))

X = sm.add_constant(d[X_COLS].astype(float))
y = d[Y].astype(float)

# --- 1. HC3 (as reported in Extension A) -----------------------------------
m_hc3 = sm.OLS(y, X).fit(cov_type="HC3")

# --- 2. cluster-robust by spatial block ------------------------------------
d["block"] = (np.floor(d.lat_c / BLOCK).astype(int).astype(str) + "_"
              + np.floor(d.lon_c / BLOCK).astype(int).astype(str))
nblocks = d.block.nunique()
m_cl = sm.OLS(y, X).fit(cov_type="cluster",
                        cov_kwds={"groups": d.block.values})
print("cluster-robust: %d blocks of %.0f degrees, median %.1f cells per block"
      % (nblocks, BLOCK, d.groupby("block").size().median()))

print("\n%-15s %12s %11s %9s | %11s %9s" % (
    "term", "coef", "se(HC3)", "p(HC3)", "se(clust)", "p(clust)"))
print("-" * 76)
for t in X.columns:
    print("%-15s %12.5g %11.4g %9.4f | %11.4g %9.4f" % (
        t, m_hc3.params[t], m_hc3.bse[t], m_hc3.pvalues[t],
        m_cl.bse[t], m_cl.pvalues[t]))

infl = m_cl.bse["rarefied_250"] / m_hc3.bse["rarefied_250"]
print("\nrichness SE inflates %.2fx under clustering" % infl)

# --- 3. spatial lag and spatial error models -------------------------------
coords = list(zip(d.lon_c, d.lat_c))
w = libpysal.weights.DistanceBand(coords, threshold=1.5, binary=True,
                                  silence_warnings=True)
w.transform = "r"

yv = y.values.reshape(-1, 1)
Xv = d[X_COLS].astype(float).values
names = X_COLS

lag = ML_Lag(yv, Xv, w=w, name_y=Y, name_x=names)
err = ML_Error(yv, Xv, w=w, name_y=Y, name_x=names)


def show(model, label, extra_name, extra_val):
    print("\n--- %s ---" % label)
    print("  %-15s %12s %11s %9s" % ("term", "coef", "se", "p"))
    for i, t in enumerate(["CONSTANT"] + names):
        b = float(model.betas[i][0])
        se = float(np.sqrt(model.vm[i, i]))
        z = b / se
        from scipy.stats import norm
        p = 2 * (1 - norm.cdf(abs(z)))
        print("  %-15s %12.5g %11.4g %9.4f" % (t, b, se, p))
    print("  %-15s %12.5g" % (extra_name, extra_val))
    print("  pseudo R2 = %.4f" % model.pr2)


show(lag, "SPATIAL LAG (ML)", "rho (spatial lag)", float(lag.rho))
show(err, "SPATIAL ERROR (ML)", "lambda (error corr)", float(err.lam))

# --- residual autocorrelation before vs after -------------------------------
mi_ols = esda.Moran(m_hc3.resid.values, w, permutations=999)
mi_lag = esda.Moran(lag.u.flatten(), w, permutations=999)
# For ML_Error the spatially filtered residual is e_filtered; err.u is the raw
# y - Xb and retains the autocorrelation the model has absorbed (testing u gave a
# misleading I = 0.878 before this fix, 2026-10-06 review).
mi_err = esda.Moran(np.asarray(err.e_filtered).flatten(), w, permutations=999)
print("\n--- residual Moran's I ---")
for lab, mi in (("OLS", mi_ols), ("spatial lag", mi_lag), ("spatial error", mi_err)):
    print("  %-14s I=%+.4f  z=%6.2f  p=%.4f" % (lab, mi.I, mi.z_sim, mi.p_sim))

print("\n=== VERDICT on rarefied richness ===")
b_ols = m_hc3.params["rarefied_250"]
i = names.index("rarefied_250") + 1
from scipy.stats import norm
for lab, b, se in (
        ("OLS + HC3", b_ols, m_hc3.bse["rarefied_250"]),
        ("OLS + cluster", m_cl.params["rarefied_250"], m_cl.bse["rarefied_250"]),
        ("spatial lag", float(lag.betas[i][0]), float(np.sqrt(lag.vm[i, i]))),
        ("spatial error", float(err.betas[i][0]), float(np.sqrt(err.vm[i, i])))):
    p = 2 * (1 - norm.cdf(abs(b / se)))
    print("  %-14s beta=%+.5f  se=%.5f  p=%.4f  %s"
          % (lab, b, se, p, "significant" if p < 0.05 else "NOT significant"))
