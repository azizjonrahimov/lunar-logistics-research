"""Verification tests: analytic references, published anchors, invariants."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pytest

from lunarsim import vv, run, dispatch, Scenario, Simulation
from lunarsim.assign import _hungarian, min_cost_assignment


@pytest.mark.parametrize("check", vv.run_all_checks(), ids=lambda c: c["name"])
def test_verification_check(check):
    assert check["passed"], f"{check['name']}: ref={check['reference']}, sim={check['simulated']}, err={check['rel_error']:.4%}"


def test_hungarian_matches_scipy():
    scipy = pytest.importorskip("scipy")
    from scipy.optimize import linear_sum_assignment
    rng = np.random.default_rng(0)
    for _ in range(300):
        n, m = rng.integers(1, 9, 2)
        C = rng.random((n, m)) * 10
        r1, c1 = linear_sum_assignment(C)
        r2, c2 = _hungarian(C.tolist())
        assert abs(C[r1, c1].sum() - sum(C[i][j] for i, j in zip(r2, c2))) < 1e-9


def test_determinism():
    sc = Scenario(fleet=[("NASA", "LTV", "supervised", "A"), ("CoA", "HAUL", "supervised", "A")])
    a = run(sc, dispatch.marketplace, seed=4)
    b = run(sc, dispatch.marketplace, seed=4)
    import math
    for k in a:
        if isinstance(a[k], float) and math.isnan(a[k]):
            assert math.isnan(b[k]), k
        else:
            assert a[k] == b[k], k


def test_delays_non_negative_and_delivered_after_ready():
    sc = Scenario(fleet=[("NASA", "LTV", "supervised", "A"), ("CoA", "HAUL", "supervised", "A")])
    sim = Simulation(sc, dispatch.marketplace, seed=2)
    sim.run()
    for c in sim.all_cargo:
        if c.t_delivered is not None:
            assert c.t_picked >= c.t_ready - 1e-9
            assert c.t_delivered >= c.t_picked - 1e-9


def test_night_capability_respected():
    """A vehicle without night capability never starts a job in the dark."""
    sc = Scenario(fleet=[("NASA", "LTV", "supervised", "A")], night_fraction=0.3)
    sim = Simulation(sc, dispatch.pooled_greedy, seed=7, mech_kwargs={"trace": True})
    sim.run()
    for j in sim.trace:
        assert not sim.is_night(j["t0"]), f"job started at night at t={j['t0']}"


def test_team_lift_moves_oversize_items():
    sc = Scenario(landings_per_year={"CLPS": 0, "MK1": 6, "LARGE": 0},
                  fleet=[("NASA", "LTV", "autonomous", "A"), ("CoA", "LTV", "autonomous", "A")],
                  other_duty_share=0.0, failures=False)
    out_team = run(sc, dispatch.marketplace, seed=9)
    out_noteam = run(sc, dispatch.marketplace_no_team, seed=9)
    assert out_team["stranded_kg"] <= out_noteam["stranded_kg"]
    assert out_team["team_lifts"] > 0


def test_trace_export_is_json_serialisable():
    import json
    sc = Scenario(fleet=[("NASA", "LTV", "supervised", "A"), ("CoA", "HAUL", "supervised", "A")])
    sim = Simulation(sc, dispatch.marketplace, seed=1, mech_kwargs={"trace": True})
    sim.run()
    s = json.dumps(sim.trace_export())
    assert len(s) > 1000
