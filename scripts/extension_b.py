# -*- coding: utf-8 -*-
"""Extension B (plan Step 7): is the richness-productivity relationship linear
or hump-shaped?

Adds a squared rarefied-richness term to the corrected model and compares fit by
AIC. Three things beyond the plan's spec, all necessary here:

1. Richness is MEAN-CENTRED before squaring. Without centring, x and x^2 are
   near-collinear and the quadratic term's standard error is meaningless.
2. The turning point is reported and checked against the observed richness
   range. A quadratic can win on AIC with its vertex far outside the data, which
   is a curved slope, not a hump - that distinction decides which side of the
   literature debate the result lands on.
3. The comparison is repeated under the spatial lag and spatial error models,
   because OLS inference on this data is known to be unreliable
   (docs/RESULTS_SPATIAL.md).

Literature anchor (from the review): a supported linear fit aligns with the
complementarity studies (Liang 2016, Deng 2025); a supported quadratic with a
negative squared term aligns with the unimodal/selection-effect studies
(Fraser 2015) and with saturation at scale (Gonzalez 2020).
"""
import os
import sys
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm
from spreg import ML_Error, ML_Lag

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
sys.path.insert(0, HERE)
from weights_sensitivity import queen_from_grid

CTRL = ["log_effort", "temp_c", "precip_mm_yr"]


def analyse(d, rich_col, cell_deg, label):
    d = d.copy()
    r = d[rich_col].astype(float)
    d["rich_c"] = r - r.mean()
    d["rich_c2"] = d.rich_c ** 2
    y = d.gpp.astype(float)

    lin_cols = ["rich_c"] + CTRL
    qua_cols = ["rich_c", "rich_c2"] + CTRL

    print("\n" + "=" * 74)
    print("%s   n=%d   richness range %.1f - %.1f (mean %.1f)"
          % (label, len(d), r.min(), r.max(), r.mean()))
    print("=" * 74)

    # ---- OLS, as the plan specifies -------------------------------------
    m_lin = sm.OLS(y, sm.add_constant(d[lin_cols])).fit(cov_type="HC3")
    m_qua = sm.OLS(y, sm.add_constant(d[qua_cols])).fit(cov_type="HC3")
    daic = m_qua.aic - m_lin.aic
    print("\nOLS      linear AIC=%8.2f   quadratic AIC=%8.2f   dAIC=%+7.2f  -> %s"
          % (m_lin.aic, m_qua.aic, daic,
             "QUADRATIC better" if daic < -2 else
             "linear better" if daic > 2 else "indistinguishable"))
    b1 = m_qua.params["rich_c"]
    b2 = m_qua.params["rich_c2"]
    print("         rich_c  = %+.6f (p=%.4g)" % (b1, m_qua.pvalues["rich_c"]))
    print("         rich_c2 = %+.8f (p=%.4g)  %s"
          % (b2, m_qua.pvalues["rich_c2"],
             "concave (hump)" if b2 < 0 else "convex (upturn)"))

    if abs(b2) > 1e-12:
        vertex_c = -b1 / (2 * b2)
        vertex = vertex_c + r.mean()
        inside = r.min() <= vertex <= r.max()
        # A vertex inside the data range is only a HUMP if the quadratic is
        # concave (b2 < 0). With b2 > 0 that same vertex is a MINIMUM, which is
        # not the hump-backed model at all - it is a U shape.
        if not inside:
            shape = "OUTSIDE observed range (curved slope, not a turning point)"
        elif b2 < 0:
            shape = "INSIDE range and concave -> a genuine HUMP"
        else:
            shape = "INSIDE range but convex -> a MINIMUM (U shape), not a hump"
        print("         turning point at richness = %.1f  -> %s" % (vertex, shape))

    # ---- spatial models --------------------------------------------------
    w = queen_from_grid(d.lat_c.values, d.lon_c.values, cell_deg)
    w.transform = "r"
    yv = y.values.reshape(-1, 1)

    for Model, mlabel in ((ML_Lag, "ML_Lag"), (ML_Error, "ML_Error")):
        a = Model(yv, d[lin_cols].astype(float).values, w=w)
        b = Model(yv, d[qua_cols].astype(float).values, w=w)
        da = b.aic - a.aic
        i2 = qua_cols.index("rich_c2") + 1
        bq = float(b.betas[i2][0])
        seq = float(np.sqrt(b.vm[i2, i2]))
        pq = 2 * (1 - norm.cdf(abs(bq / seq)))
        i1 = qua_cols.index("rich_c") + 1
        b1s = float(b.betas[i1][0])
        verdict = ("QUADRATIC better" if da < -2 else
                   "linear better" if da > 2 else "indistinguishable")
        extra = ""
        if abs(bq) > 1e-12:
            v = -b1s / (2 * bq) + r.mean()
            extra = "  vertex=%.1f %s" % (
                v, "(inside)" if r.min() <= v <= r.max() else "(OUTSIDE)")
        print("%-8s linear AIC=%8.2f   quadratic AIC=%8.2f   dAIC=%+7.2f  -> %s"
              % (mlabel, a.aic, b.aic, da, verdict))
        print("         rich_c2 = %+.8f (p=%.4g)%s" % (bq, pq, extra))


def main():
    d1 = pd.read_csv(os.path.join(DATA, "model_cells.csv"))
    analyse(d1, "rarefied_250", 1.0, "1.0 deg grid, rarefied at n=250")

    # rarefaction-level sensitivity: does the shape depend on the standardisation?
    for col in ("rarefied_50", "rarefied_100"):
        if col in d1.columns:
            sub = d1[d1[col].notna()]
            if len(sub) > 40:
                analyse(sub, col, 1.0, "1.0 deg grid, %s" % col)

    p2 = os.path.join(DATA, "merged_cells_2p0.csv")
    if os.path.exists(p2):
        d2 = pd.read_csv(p2)
        d2["log_effort"] = np.log10(d2.total_records.clip(lower=1))
        d2 = d2[d2.gpp.notna() & d2.wc_mode.notna()
                & (~d2.wc_mode.isin([40, 50, 80]))
                & (d2.total_records >= 20) & d2.rarefied.notna()
                & d2.temp_c.notna() & d2.precip_mm_yr.notna()]
        analyse(d2, "rarefied", 2.0, "2.0 deg grid, rarefied at n=250")


if __name__ == "__main__":
    main()
