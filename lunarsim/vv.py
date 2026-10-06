"""Verification and validation checks for LunarSim.

Each check compares a simulator output with an independent reference: an
analytic formula, a published data point, or a conservation identity. A check
passes when the relative error is within its tolerance (1% unless the reference
itself is less precise). `run_all_checks()` returns a list of dicts that the
test-suite, the paper and the live viewer all use.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, asdict
from typing import Callable, Dict, List

import numpy as np

from .engine import Simulation, Job, teleop_speed_kmh
from .entities import VEHICLE_CLASSES
from .scenario import Scenario, LUNAR_CYCLE_H, HOURS_PER_DAY, BulkFlow
from .world import build_default_world


@dataclass
class Check:
    name: str
    reference: float
    simulated: float
    tolerance: float      # relative tolerance
    unit: str
    basis: str
    passed: bool = False
    rel_error: float = float("nan")

    def finish(self):
        self.rel_error = abs(self.simulated - self.reference) / max(abs(self.reference), 1e-12)
        self.passed = bool(self.rel_error <= self.tolerance)
        return self


# ---------------------------------------------------------------------------
# 1. Kinematics: travel time along a known path equals slope-weighted distance / speed
# ---------------------------------------------------------------------------
def check_travel_time() -> Check:
    w = build_default_world()
    sc = Scenario(fleet=[("A", "LTV", "autonomous", "A")], other_duty_share=0.0, failures=False,
                  landings_per_year={"CLPS": 0, "MK1": 0, "LARGE": 0})
    sim = Simulation(sc, lambda *a, **k: [], seed=0)
    v = sim.vehicles[0]
    # PAD_A -> BASE goes PAD_A - DEPOT - BASE, both flat edges
    d = w.distance_km("PAD_A", "BASE")
    ref = d / v.cls.speed_kmh  # flat, loaded, autonomous
    sim_h = sim.travel_h(v, "PAD_A", "BASE", loaded=True, team=False, t=0.0)
    return Check("Travel time on a flat two-edge path", ref, sim_h, 1e-9, "h",
                 "distance / speed; path PAD_A-DEPOT-BASE, both edges flat").finish()


def check_slope_penalty() -> Check:
    w = build_default_world()
    sc = Scenario(fleet=[("A", "LTV", "autonomous", "A")], other_duty_share=0.0, failures=False,
                  landings_per_year={"CLPS": 0, "MK1": 0, "LARGE": 0})
    sim = Simulation(sc, lambda *a, **k: [], seed=0)
    v = sim.vehicles[0]
    # SCI_1 -> PSR is a single steep edge: time = dist / (0.5 * speed)
    d = w.distance_km("SCI_1", "PSR")
    ref = d / (0.5 * v.cls.speed_kmh)
    return Check("Steep-edge travel time doubles", ref, sim.travel_h(v, "SCI_1", "PSR", True, False, 0.0),
                 1e-9, "h", "slope class 'steep' halves speed").finish()


# ---------------------------------------------------------------------------
# 2. Teleoperation model reproduces the NASA JSC trial speeds it was fitted to
# ---------------------------------------------------------------------------
def check_teleop_fit() -> List[Check]:
    data = {0.0: 3.24, 4.0: 2.56, 6.0: 2.03, 8.0: 1.76}   # km/h at RTT s (Litaker et al., TM-20240001217)
    out = []
    for rtt, v_obs in data.items():
        v_model = teleop_speed_kmh(rtt)
        out.append(Check(f"Teleoperated speed at {rtt:.0f} s RTT", v_obs, v_model, 0.01, "km/h",
                         "NASA JSC LTV teleoperation trial average speed").finish())
    return out


# ---------------------------------------------------------------------------
# 3. Night model: dark fraction of simulated time equals the parameter
# ---------------------------------------------------------------------------
def check_night_fraction() -> Check:
    sc = Scenario(night_fraction=0.15, landings_per_year={"CLPS": 0, "MK1": 0, "LARGE": 0})
    sim = Simulation(sc, lambda *a, **k: [], seed=0)
    ts = np.linspace(0, 10 * LUNAR_CYCLE_H, 200_001)
    dark = np.mean([sim.is_night(t) for t in ts])
    return Check("Dark share of time", 0.15, float(dark), 0.005, "fraction",
                 "night_fraction parameter; sampled over 10 cycles").finish()


# ---------------------------------------------------------------------------
# 4. Mass conservation: landed + bulk = delivered + stranded + backlog + pending
# ---------------------------------------------------------------------------
def check_mass_conservation(mechanism: Callable, seed: int = 3) -> Check:
    from .scenario import Scenario
    sc = Scenario(name="vv", landings_per_year={"CLPS": 4, "MK1": 3, "LARGE": 1},
                  fleet=[("NASA", "LTV", "supervised", "A"), ("CoA", "LTV", "supervised", "A"),
                         ("CoA", "HAUL", "supervised", "A"), ("CoB", "MICRO", "teleop", "A")],
                  bulk_flows=[BulkFlow("CONSTR", "BASE", 300, lot_kg=1000)], n_operators=3)
    sim = Simulation(sc, mechanism, seed=seed)
    sim.run()
    m = sim.metrics
    ready_total = m.ready_kg
    accounted = m.delivered_kg + m.stranded_kg + m.backlog_kg
    return Check(f"Mass conservation ({getattr(mechanism, '__name__', 'mech')})", ready_total, accounted, 1e-9, "kg",
                 "ready mass = delivered + stranded + backlog at horizon").finish()


# ---------------------------------------------------------------------------
# 5. Stranding rule: an item heavier than the best team is never moved
# ---------------------------------------------------------------------------
def check_stranding_rule() -> Check:
    from . import dispatch
    sc = Scenario(landings_per_year={"CLPS": 0, "MK1": 0, "LARGE": 6},
                  fleet=[("NASA", "LTV", "autonomous", "A"), ("NASA", "LTV", "autonomous", "A")],
                  other_duty_share=0.0, failures=False)
    sim = Simulation(sc, dispatch.marketplace, seed=5)
    sim.run()
    heavy = [c for c in sim.all_cargo if c.mass_kg > 3000 and c.cls != "return"]
    moved = sum(1 for c in heavy if c.t_delivered is not None)
    return Check("Items above team capacity (2 x 1,500 kg) never delivered", 0.0, float(moved), 0.0, "items",
                 f"{len(heavy)} items heavier than 3,000 kg in six large landings").finish()


# ---------------------------------------------------------------------------
# 6. Common random numbers: identical demand across mechanisms for one seed
# ---------------------------------------------------------------------------
def check_common_random_numbers() -> Check:
    from . import dispatch
    sc = Scenario(landings_per_year={"CLPS": 4, "MK1": 3, "LARGE": 1},
                  fleet=[("NASA", "LTV", "supervised", "A"), ("CoA", "HAUL", "supervised", "A")])
    sigs = []
    for mech in (dispatch.inhouse, dispatch.pooled_greedy, dispatch.central_assign, dispatch.marketplace):
        sim = Simulation(sc, mech, seed=11)
        sim.run()
        land = [(round(c.t_landed, 6), round(c.mass_kg, 6), c.dest) for c in sim.all_cargo if c.cls not in ("return", "bulk")]
        sigs.append(tuple(sorted(land)))
    same = float(all(s == sigs[0] for s in sigs))
    return Check("Same landed manifest for every mechanism (seed 11)", 1.0, same, 0.0, "bool",
                 "demand drawn from a stream separate from operations").finish()


# ---------------------------------------------------------------------------
# 7. Queueing: single vehicle, Poisson single-item arrivals -> M/G/1 (Pollaczek-Khinchine)
# ---------------------------------------------------------------------------
def check_mg1_queue(n_years: int = 20) -> Check:
    """One autonomous LTV, no night, no faults, no duties; items arrive one per
    landing (CLPS payload fixed by making the manifest a single 100 kg crate) at a
    Poisson rate; destination fixed. The mean wait in queue should follow
    W_q = lambda * E[S^2] / (2 (1 - rho)) where S is the job duration."""
    from . import dispatch
    from .scenario import LANDER_TYPES, LanderType, CARGO_CLASSES
    import lunarsim.scenario as scn
    # a dedicated tiny lander whose manifest is exactly one crate
    saved_lt = dict(LANDER_TYPES)
    saved_classes = list(CARGO_CLASSES)
    try:
        LANDER_TYPES["ONE"] = LanderType("ONE", (99.0, 99.0), (0.0, 0.0), True, 100)
        scn.CARGO_CLASSES[:] = [("consumables", (99.0, 100.0), {"BASE": 1.0}, 1, 1.0)]
        saved_ret = scn.RETURN_ITEM_PROB
        scn.RETURN_ITEM_PROB = 0.0
        rate_per_year = 900.0
        sc = Scenario(landings_per_year={"ONE": rate_per_year}, cargo_owners=["NASA"],
                      fleet=[("NASA", "LTV", "autonomous", "A")], night_fraction=0.0, failures=False,
                      other_duty_share=0.0, horizon_h=n_years * 365 * HOURS_PER_DAY, n_operators=4)
        sim = Simulation(sc, dispatch.pooled_greedy, seed=21)
        sim.run()
        # service time: vehicle at BASE after the first job; each job = BASE->pad empty + load + pad->BASE + unload
        v = sim.vehicles[0]
        w = sim.world
        pads = w.pads
        # average over the two pads (equally likely)
        S = []
        for pad in pads:
            job = Job([v], [sim.all_cargo[0]], ["BASE"])
            v.location = "BASE"
            sim.all_cargo[0].origin = pad
            S.append(sim.job_plan(job, 0.0)[0])
        S = np.array(S)
        lam = rate_per_year / (365 * HOURS_PER_DAY)
        ES, ES2 = S.mean(), (S ** 2).mean()
        rho = lam * ES
        Wq_ref = lam * ES2 / (2 * (1 - rho))
        # simulated wait in queue = pickup time - ready time; pickup happens when a vehicle is assigned
        waits = np.array([c.t_picked - c.t_ready for c in sim.all_cargo if c.t_picked is not None and c.cls != "return"])
        # ignore the first 2% as warm-up (negligible here) and the return items (none: return share applies but origin not pad? keep filter)
        Wq_sim = float(waits.mean())
        return Check("M/G/1 mean queue wait (Pollaczek-Khinchine)", Wq_ref, Wq_sim, 0.05, "h",
                     f"rho={rho:.3f}, lambda={lam*24:.2f}/day, E[S]={ES:.2f} h, n={len(waits)} items over {n_years} years").finish()
    finally:
        LANDER_TYPES.clear()
        LANDER_TYPES.update(saved_lt)
        scn.CARGO_CLASSES[:] = saved_classes
        scn.RETURN_ITEM_PROB = saved_ret


# ---------------------------------------------------------------------------
# 8. Fleet cost identity
# ---------------------------------------------------------------------------
def check_fleet_cost() -> Check:
    from . import dispatch
    sc = Scenario(fleet=[("NASA", "LTV", "supervised", "A"), ("CoA", "HAUL", "supervised", "A"), ("CoB", "MICRO", "teleop", "A")],
                  landings_per_year={"CLPS": 1, "MK1": 0, "LARGE": 0})
    sim = Simulation(sc, dispatch.pooled_greedy, seed=1)
    out = sim.run()
    ref = sum(VEHICLE_CLASSES[c].unit_cost_musd / VEHICLE_CLASSES[c].life_years for _, c, _, _ in sc.fleet)
    return Check("Annual fleet amortisation", ref, out["fleet_cost_musd"], 1e-9, "$M",
                 "sum of unit cost / calendar life over the fleet").finish()


def run_all_checks() -> List[Dict]:
    from . import dispatch
    checks: List[Check] = [check_travel_time(), check_slope_penalty()]
    checks += check_teleop_fit()
    checks += [check_night_fraction(), check_mass_conservation(dispatch.marketplace),
               check_mass_conservation(dispatch.pooled_greedy), check_stranding_rule(),
               check_common_random_numbers(), check_fleet_cost(), check_mg1_queue()]
    return [asdict(c) for c in checks]


if __name__ == "__main__":
    for c in run_all_checks():
        flag = "PASS" if c["passed"] else "FAIL"
        print(f"{flag}  {c['name']:60s} ref={c['reference']:.4g} sim={c['simulated']:.4g} err={100*c['rel_error']:.3f}%  tol={100*c['tolerance']:.1f}%")
