# -*- coding: utf-8 -*-
"""Unit tests for the pieces every result depends on. Run: pytest -q

They check the estimators against values that can be worked out by hand or that
must hold by construction, using no project data and no network.
"""
import math
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))

from gbif_lib import build_grid, cells_in_box, hurlbert_rarefy  # noqa: E402
from coverage_rarefaction import coverage_at, full_coverage  # noqa: E402
import local_slopes  # noqa: E402
import effort_simulation  # noqa: E402
from extension_e_stability import series_stats  # noqa: E402


# ---- Hurlbert rarefaction --------------------------------------------------
def test_rarefaction_hand_value():
    # Two species with 2 and 1 records, sample of 2 without replacement:
    # species A is always present; species B is missed only if both A records
    # are drawn, probability C(2,2)/C(3,2) = 1/3. Expected species = 1 + 2/3.
    assert hurlbert_rarefy([2, 1], 2) == pytest.approx(5 / 3)


def test_rarefaction_limits():
    ab = [50, 20, 10, 5, 3, 1, 1]
    assert hurlbert_rarefy(ab, sum(ab)) == pytest.approx(len(ab))   # whole sample
    assert hurlbert_rarefy(ab, 1) == pytest.approx(1.0)             # one record, one species
    assert hurlbert_rarefy(ab, sum(ab) + 1) is None                 # more than we have


def test_rarefaction_monotone_and_bounded():
    ab = [400, 120, 60, 30, 9, 4, 2, 1, 1, 1]
    vals = [hurlbert_rarefy(ab, n) for n in (5, 20, 80, 250, 600)]
    assert all(b > a for a, b in zip(vals, vals[1:]))
    assert all(1 <= v <= len(ab) for v in vals)


def test_rarefaction_survives_huge_counts():
    # eBird cells hold millions of records; the binomials must not overflow.
    v = hurlbert_rarefy([3_000_000, 500_000, 2_000, 30, 1], 250)
    assert math.isfinite(v) and 1 < v < 5


def test_rarefaction_ignores_effort():
    # Multiplying every count by 100 changes effort, not the community. (Both pools
    # must be large next to the sample: drawing 50 from a pool of 67 is nearly a
    # census and legitimately finds more species.)
    small = hurlbert_rarefy([3000, 2000, 1000, 500, 200], 50)
    big = hurlbert_rarefy([300000, 200000, 100000, 50000, 20000], 50)
    assert big == pytest.approx(small, rel=0.005)


# ---- grid ------------------------------------------------------------------
def test_grid_shape_and_ids():
    g = build_grid(1.0)
    assert len(g) == 26 * 34 == 884
    assert g[0]["cell_id"] == "r00c00" and g[-1]["cell_id"] == "r25c33"
    assert (g[0]["lat_min"], g[0]["lon_min"]) == (5.0, 68.0)
    assert (g[-1]["lat_max"], g[-1]["lon_max"]) == (31.0, 102.0)
    assert len({c["cell_id"] for c in g}) == len(g)


def test_half_degree_grid_nests():
    assert len(build_grid(0.5)) == 4 * len(build_grid(1.0))


def test_cells_in_box():
    g = build_grid(1.0)
    wg = cells_in_box(g, (8.0, 16.0, 74.0, 77.0))
    assert len(wg) == 8 * 3
    assert all(8 <= c["lat_c"] <= 16 and 74 <= c["lon_c"] <= 77 for c in wg)


# ---- sample coverage -------------------------------------------------------
def test_coverage_bounds_and_extremes():
    assert full_coverage(np.array([100.0, 80, 60, 40])) == pytest.approx(1.0)   # no singletons
    c = full_coverage(np.array([1.0] * 20))                                     # all singletons
    assert 0 <= c < 0.1
    mixed = full_coverage(np.array([50.0, 20, 5, 2, 1, 1, 1]))
    assert 0 < mixed < 1


def test_coverage_rises_with_sample_size():
    x = np.array([200.0, 90, 40, 12, 5, 2, 1, 1, 1])
    n = x.sum()
    cov = [coverage_at(x, n, m) for m in (10, 50, 150, 300)]
    assert all(b > a for a, b in zip(cov, cov[1:]))
    assert all(0 <= c <= 1 for c in cov)


# ---- geographically weighted regression ------------------------------------
def test_haversine_one_degree():
    d = local_slopes.haversine_km(np.array([0.0, 1.0]), np.array([80.0, 80.0]))
    assert d[0, 1] == pytest.approx(111.19, abs=0.1)
    assert d[0, 0] == 0 and d[0, 1] == d[1, 0]


def test_kernel_is_bisquare_and_local():
    lat = np.arange(10.0); lon = np.zeros(10)
    D = local_slopes.haversine_km(lat, lon)
    W, bw = local_slopes.kernel(D, 4)
    assert np.allclose(np.diag(W), 1.0)                 # full weight on the cell itself
    assert ((W >= 0) & (W <= 1)).all()
    assert (W[0, 4:] == 0).all() and (W[0, 1:4] > 0).all()   # nothing at or beyond the 4th neighbour
    assert bw[0] == pytest.approx(D[0, 4])


def test_gwr_recovers_a_constant_slope():
    rng = np.random.default_rng(1)
    n = 120
    lat = rng.uniform(5, 31, n); lon = rng.uniform(68, 102, n)
    x = rng.normal(size=n)
    y = 0.4 * x + rng.normal(scale=0.05, size=n)
    X = np.column_stack([np.ones(n), x])
    W, _ = local_slopes.kernel(local_slopes.haversine_km(lat, lon), 40)
    f = local_slopes.gwr(y, X, W)
    assert np.allclose(f["B"][:, 1], 0.4, atol=0.05)    # stationary truth -> flat local slopes
    assert f["enp"] > 2                                 # more effective parameters than OLS


# ---- thinning (effort simulation) ------------------------------------------
def test_thinning_keeps_exactly_m_records_and_never_invents_any():
    ab = np.array([500, 120, 30, 4, 1, 1], dtype=np.int64)
    for m in (10, 100, 600):
        s = effort_simulation.thin(ab, m)
        assert s.sum() == m
        assert (s <= ab).all() and (s >= 0).all()


def test_rarefied_richness_is_unbiased_under_thinning():
    ab = np.array([4000, 1500, 700, 300, 120, 60, 30, 12, 6, 3, 2, 1, 1, 1], dtype=np.int64)
    full = hurlbert_rarefy(ab.tolist(), 250)
    reps = []
    for _ in range(300):
        s = effort_simulation.thin(ab, 1000)
        reps.append(hurlbert_rarefy(s[s > 0].tolist(), 250))
    assert np.mean(reps) == pytest.approx(full, rel=0.02)


# ---- stability statistics --------------------------------------------------
def test_series_stats_on_a_pure_trend():
    years = np.arange(2001.0, 2024.0)
    a = (1.0 + 0.02 * (years - years.mean()))[:, None]          # +2% of the mean per year
    mean, cv, dcv, trend = series_stats(a, years)
    assert mean[0] == pytest.approx(1.0)
    assert trend[0] == pytest.approx(2.0)
    assert dcv[0] == pytest.approx(0.0, abs=1e-12)              # no scatter around the line
    assert cv[0] > 0.1                                          # but the raw CV is not zero


# ---- inference batch: measurement error, equivalence, spatial scale -----------
def test_vectorised_rarefaction_matches_the_reference_implementation():
    import measurement_error
    rng = np.random.default_rng(7)
    for _ in range(20):
        ab = rng.integers(1, 5000, size=rng.integers(20, 400))
        # the two differ only in floating-point order of summation (about 2 parts in a billion)
        assert measurement_error.rarefy(ab) == pytest.approx(hurlbert_rarefy(ab.tolist(), 250),
                                                             rel=1e-6)
    assert math.isnan(measurement_error.rarefy(np.array([100, 100])))   # fewer than 250 records


def test_equivalence_test_behaves():
    from within_effect_bounds import tost
    assert tost(0.0, 0.02, 0.10) < 0.001            # tight estimate at zero: clearly inside
    assert tost(0.10, 0.02, 0.10) == pytest.approx(0.5)   # sitting on the bound: undecided
    assert tost(0.30, 0.02, 0.10) > 0.99            # well outside: equivalence not shown
    assert tost(0.05, 0.03, 0.10) == pytest.approx(tost(-0.05, 0.03, 0.10))   # symmetric


def test_spatial_patterns_are_orthonormal_and_centred():
    import scale_decomposition as sd
    lat, lon = np.meshgrid(np.arange(10.0, 18.0), np.arange(70.0, 80.0))
    D = sd.haversine(lat.ravel(), lon.ravel())
    E, moran, thr = sd.dbmem(D)
    assert E.shape[1] > 5 and E.shape[1] < len(D)
    assert np.allclose(E.T @ E, np.eye(E.shape[1]), atol=1e-8)
    assert np.allclose(E.sum(axis=0), 0, atol=1e-8)      # each pattern has zero mean
    assert (np.diff(moran) <= 1e-9).all() and moran[-1] > 0   # ordered broad to fine, all positive


def test_effective_sample_size_shrinks_only_with_autocorrelation():
    import scale_decomposition as sd
    rng = np.random.default_rng(11)
    lat, lon = np.meshgrid(np.arange(5.0, 25.0), np.arange(70.0, 90.0))
    lat, lon = lat.ravel(), lon.ravel()
    D = sd.haversine(lat, lon)
    n = len(lat)
    _, neff_noise, _ = sd.clifford(rng.normal(size=n), rng.normal(size=n), D, 111.0)
    assert 0.6 * n < neff_noise < 1.6 * n                 # independent noise: about n
    smooth_x = lat + 0.3 * lon + rng.normal(scale=0.5, size=n)
    smooth_y = lat - 0.2 * lon + rng.normal(scale=0.5, size=n)
    _, neff_smooth, _ = sd.clifford(smooth_x, smooth_y, D, 111.0)
    assert neff_smooth < 0.2 * n                          # broad gradients: far fewer


def test_series_stats_scale_free():
    rng = np.random.default_rng(2)
    years = np.arange(2001.0, 2024.0)
    a = 1.0 + rng.normal(scale=0.05, size=(23, 1))
    _, cv1, d1, t1 = series_stats(a, years)
    _, cv2, d2, t2 = series_stats(a * 7.0, years)               # units must not matter
    assert cv1[0] == pytest.approx(cv2[0]) and d1[0] == pytest.approx(d2[0])
    assert t1[0] == pytest.approx(t2[0])
