"""One-off patch: dependency-free assignment, anticipatory staging component, dispatch hook."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "lunarsim/dispatch.py")
s = open(p, encoding="utf-8").read()


def rep(a, b):
    global s
    assert a in s, a[:80]
    s = s.replace(a, b)


rep('''import numpy as np
from scipy.optimize import linear_sum_assignment

from .engine import Job, Simulation, TEAM_SETUP_H
from .entities import Cargo, Vehicle
''', '''import numpy as np

from .assign import min_cost_assignment
from .engine import Job, Simulation, TEAM_SETUP_H
from .entities import Cargo, Vehicle
''')
rep('''    rows, cols = linear_sum_assignment(cost)
    jobs = []
    for i, j in zip(rows, cols):
        if cost[i, j] < BIG / 2:''', '''    rows, cols = min_cost_assignment(cost)
    jobs = []
    for i, j in zip(rows, cols):
        if cost[i, j] < BIG / 2:''')

rep('''def marketplace(sim, waiting, free, bundling=True, team_lift=True, backhaul=True,
                night_aware=True, priority=True, consolidate=True, max_items=10,
                batch_h=0.0, w_p1=None, w_p2=None, w_age=None, fill=None, max_wait=None,
                vot_scale=None, **kw):
    jobs: List[Job] = []
    used = set()
    pool = list(waiting)''', '''ANTICIPATE_WINDOW_H = 48.0    # look this far ahead in the published landing schedule
ANTICIPATE_MARGIN_H = 1.0     # arrive at the pad this long before the first item is ready


def _anticipate(sim: Simulation, free: List[Vehicle], used: set, pool: List[Cargo]) -> None:
    """Anticipatory staging. Landings are published in advance; when a landing is
    due within the window and no vehicle is at (or heading to) its pad, send the
    nearest idle, compatible vehicle so that it arrives just before offloading
    finishes. Repositioning never pre-empts waiting cargo: only vehicles that the
    auction left idle are used, and only outside the night for vehicles that
    cannot work in the dark."""
    for t_land, lt, pad in sim.upcoming_landings(ANTICIPATE_WINDOW_H):
        staged = any((v.location == pad and v.busy_until <= sim.t) or v.repos_target == pad for v in sim.vehicles)
        if staged:
            continue
        t_first = t_land + lt.offload_h[0]
        cands = [v for v in free if v.id not in used and v.repos_target is None and v.location != pad]
        if not cands:
            continue
        v = min(cands, key=lambda u: sim.travel_h(u, u.location, pad, False, False, sim.t))
        h = sim.travel_h(v, v.location, pad, False, False, sim.t)
        depart = max(sim.t, t_first - ANTICIPATE_MARGIN_H - h)
        sim.schedule_reposition(v, pad, depart)
        used.add(v.id)


def marketplace(sim, waiting, free, bundling=True, team_lift=True, backhaul=True,
                night_aware=True, priority=True, consolidate=True, anticipate=True, max_items=10,
                batch_h=0.0, w_p1=None, w_p2=None, w_age=None, fill=None, max_wait=None,
                vot_scale=None, **kw):
    jobs: List[Job] = []
    used = set()
    pool = list(waiting)''')

# call anticipation at the end of the marketplace, after the auction has used what it needs
rep('''        used.add(v.id)
        jobs.append(job)
        for c in bundle + job.backhaul:
            pool.remove(c)
    return jobs
''', '''        used.add(v.id)
        jobs.append(job)
        for c in bundle + job.backhaul:
            pool.remove(c)
    # 4. anticipatory staging with whatever is still idle
    if anticipate:
        _anticipate(sim, free, used, pool)
    return jobs
''')

rep('''def marketplace_no_consolidate(sim, w, f, **kw):
    kw.pop("consolidate", None)
    return marketplace(sim, w, f, consolidate=False, **kw)
''', '''def marketplace_no_consolidate(sim, w, f, **kw):
    kw.pop("consolidate", None)
    return marketplace(sim, w, f, consolidate=False, **kw)


def marketplace_no_anticipate(sim, w, f, **kw):
    kw.pop("anticipate", None)
    return marketplace(sim, w, f, anticipate=False, **kw)
''')
rep('''marketplace_no_consolidate.supports_team = True''', '''marketplace_no_consolidate.supports_team = True
marketplace_no_anticipate.supports_team = True''')
rep('''MECHANISMS = {
    "inhouse": inhouse,
    "pooled_greedy": pooled_greedy,
    "central_assign": central_assign,
    "marketplace": marketplace,
}''', '''MECHANISMS = {
    "inhouse": inhouse,
    "pooled_greedy": pooled_greedy,
    "central_assign": central_assign,
    "marketplace": marketplace,
    "marketplace_no_bundling": marketplace_no_bundling,
    "marketplace_no_team": marketplace_no_team,
    "marketplace_no_backhaul": marketplace_no_backhaul,
    "marketplace_no_night": marketplace_no_night,
    "marketplace_no_priority": marketplace_no_priority,
    "marketplace_no_consolidate": marketplace_no_consolidate,
    "marketplace_no_anticipate": marketplace_no_anticipate,
}''')
open(p, "w", encoding="utf-8").write(s)

# engine: the dispatcher must also be called when there is no waiting cargo but a landing is near,
# otherwise anticipation never triggers in quiet periods. We add a LANDING_SOON event.
p = os.path.join(ROOT, "lunarsim/engine.py")
s = open(p, encoding="utf-8").read()
rep2 = lambda a, b: None
assert '''        for t_land, lt, pad in self.landing_schedule:
            self._push(t_land, "LANDING", (lt, pad))''' in s
s = s.replace('''        for t_land, lt, pad in self.landing_schedule:
            self._push(t_land, "LANDING", (lt, pad))''', '''        for t_land, lt, pad in self.landing_schedule:
            self._push(t_land, "LANDING", (lt, pad))
            # a wake-up before each landing lets anticipatory mechanisms stage a vehicle
            self._push(max(0.0, t_land - 48.0), "WAKE", None)
            self._push(max(0.0, t_land - 12.0), "WAKE", None)''')
# _dispatch: allow mechanisms to run with empty candidate list when they support anticipation
s = s.replace('''    def _dispatch(self):
        candidates = [c for c in self.waiting if not c.stranded]
        if not candidates or not self.free_vehicles():
            return
        jobs: List[Job] = self.mechanism(self, candidates, self.free_vehicles(), **self.mech_kwargs)''',
'''    def _dispatch(self):
        candidates = [c for c in self.waiting if not c.stranded]
        free = self.free_vehicles()
        if not free:
            return
        if not candidates and not getattr(self.mechanism, "anticipates", False):
            return
        jobs: List[Job] = self.mechanism(self, candidates, free, **self.mech_kwargs)''')
open(p, "w", encoding="utf-8").write(s)

p = os.path.join(ROOT, "lunarsim/dispatch.py")
s = open(p, encoding="utf-8").read()
s = s.replace('''marketplace_no_anticipate.supports_team = True''', '''marketplace_no_anticipate.supports_team = True
for _f in (marketplace, marketplace_no_bundling, marketplace_no_backhaul, marketplace_no_night,
           marketplace_no_priority, marketplace_no_team, marketplace_no_consolidate):
    _f.anticipates = True
marketplace_no_anticipate.anticipates = False''')
open(p, "w", encoding="utf-8").write(s)
print("done")
