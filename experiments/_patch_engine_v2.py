"""One-off patch: landing schedule with pads, anticipatory repositioning hooks, trace export."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rep(path, pairs):
    p = os.path.join(ROOT, path)
    s = open(p, encoding="utf-8").read()
    for a, b in pairs:
        assert a in s, (path, a[:80])
        s = s.replace(a, b)
    open(p, "w", encoding="utf-8").write(s)
    print("patched", path)


rep("lunarsim/scenario.py", [
    ('''def sample_cargo_manifest(rng: np.random.Generator, lander: LanderType, owner_pool: List[str],
                          world_pads: List[str], t_land: float, common_share: float,
                          id_start: int):
    """Draw a manifest for one landing. Items are drawn by class share until the
    lander's payload mass is used up; items heavier than the lander can carry are
    re-drawn."""
    from .entities import Cargo
    total = rng.uniform(*lander.payload_kg)
    labels = [c[0] for c in CARGO_CLASSES]
    shares = np.array([c[4] for c in CARGO_CLASSES])
    shares = shares / shares.sum()
    pad = rng.choice(world_pads)
    items = []''',
     '''def sample_cargo_manifest(rng: np.random.Generator, lander: LanderType, owner_pool: List[str],
                          world_pads: List[str], t_land: float, common_share: float,
                          id_start: int, pad: Optional[str] = None):
    """Draw a manifest for one landing. Items are drawn by class share until the
    lander's payload mass is used up; items heavier than the lander can carry are
    re-drawn. The landing pad is given (it is part of the published schedule) or
    drawn here."""
    from .entities import Cargo
    total = rng.uniform(*lander.payload_kg)
    labels = [c[0] for c in CARGO_CLASSES]
    shares = np.array([c[4] for c in CARGO_CLASSES])
    shares = shares / shares.sum()
    if pad is None:
        pad = rng.choice(world_pads)
    items = []'''),
    ('''def sample_landings(rng: np.random.Generator, sc: Scenario) -> List[Tuple[float, LanderType]]:
    """Landing times. Each lander type arrives as a Poisson process with the
    given annual rate; large landers additionally cluster in daylight because
    missions target lit landing windows."""
    out = []
    years = sc.horizon_h / (365 * HOURS_PER_DAY)
    for lt_name, rate in sc.landings_per_year.items():
        n = rng.poisson(rate * years)
        times = np.sort(rng.uniform(0, sc.horizon_h, n))
        lt = LANDER_TYPES[lt_name]
        for t in times:
            out.append((float(t), lt))
    out.sort(key=lambda x: x[0])
    return out''',
     '''def sample_landings(rng: np.random.Generator, sc: Scenario, pads: List[str]) -> List[Tuple[float, LanderType, str]]:
    """Landing schedule: (time, lander type, pad). Each lander type arrives as a
    Poisson process with the given annual rate. The schedule is known to the
    dispatcher in advance (landings are published months ahead), which the
    anticipatory component of the marketplace uses."""
    out = []
    years = sc.horizon_h / (365 * HOURS_PER_DAY)
    for lt_name, rate in sc.landings_per_year.items():
        n = rng.poisson(rate * years)
        times = np.sort(rng.uniform(0, sc.horizon_h, n))
        lt = LANDER_TYPES[lt_name]
        for t in times:
            out.append((float(t), lt, str(rng.choice(pads))))
    out.sort(key=lambda x: x[0])
    return out'''),
])

rep("lunarsim/entities.py", [
    ("    duty_pending: bool = False\n", "    duty_pending: bool = False\n    repos_target: Optional[str] = None\n"),
])

rep("lunarsim/engine.py", [
    ('''        self.carrier_of: Dict[str, str] = {}
        self._cid = 0
        self._build_fleet()
        self._schedule_demand()''',
     '''        self.carrier_of: Dict[str, str] = {}
        self._cid = 0
        self.record_trace = bool(self.mech_kwargs.pop("trace", False))
        self.trace: List[dict] = []            # per-job movement records for the live viewer
        self.landing_schedule: List[Tuple[float, object, str]] = []
        self.repositions = 0
        self.km_reposition = 0.0
        self._last_segments: Dict[int, list] = {}
        self._build_fleet()
        self._schedule_demand()'''),
    ('''    def _schedule_demand(self):
        for t_land, lt in sample_landings(self.rng, self.sc):
            self._push(t_land, "LANDING", lt)''',
     '''    def _schedule_demand(self):
        self.landing_schedule = sample_landings(self.rng, self.sc, self.world.pads)
        for t_land, lt, pad in self.landing_schedule:
            self._push(t_land, "LANDING", (lt, pad))'''),
    ('''            if kind == "LANDING":
                self._landing(payload)''',
     '''            if kind == "LANDING":
                self._landing(*payload)'''),
    ('''            elif kind == "WAKE":
                pass
''',
     '''            elif kind == "WAKE":
                pass
            elif kind == "REPOS":
                v, pad = payload
                v.repos_target = None
                if (v.busy_until <= self.t and not v.duty_pending and v.location != pad
                        and not (self.is_night(self.t) and not v.cls.night_ops)):
                    self._reposition(v, pad)
'''),
    ('''    def _landing(self, lt):
        items, self._cid = sample_cargo_manifest(self.rng, lt, self.sc.cargo_owners,
                                                 self.world.pads, self.t,
                                                 self.sc.common_standard_share, self._cid)''',
     '''    def _landing(self, lt, pad):
        items, self._cid = sample_cargo_manifest(self.rng, lt, self.sc.cargo_owners,
                                                 self.world.pads, self.t,
                                                 self.sc.common_standard_share, self._cid, pad=pad)'''),
    ('''    def _dispatch(self):
        candidates = [c for c in self.waiting if not c.stranded]''',
     '''    def upcoming_landings(self, within_h: float) -> List[Tuple[float, object, str]]:
        """Published landings between now and now + within_h (known in advance)."""
        return [(t, lt, pad) for (t, lt, pad) in self.landing_schedule if self.t < t <= self.t + within_h]

    def schedule_reposition(self, v: Vehicle, pad: str, depart_t: float):
        """Ask a free vehicle to drive empty to a pad at depart_t (anticipatory staging)."""
        if v.repos_target is not None:
            return
        v.repos_target = pad
        self._push(max(self.t, depart_t), "REPOS", (v, pad))

    def _reposition(self, v: Vehicle, pad: str):
        h = self.travel_h(v, v.location, pad, False, False, self.t)
        d = self.world.distance_km(v.location, pad)
        if not v.cls.night_ops and self.t + h > self.next_night_start(self.t):
            return
        t_end = self.t + h
        if self.record_trace:
            self.trace.append({"kind": "reposition", "veh": v.id, "team": [v.id], "t0": self.t, "t1": t_end,
                               "segments": [[v.location, pad, self.t, t_end, 0.0]], "items": []})
        v.busy_until = t_end
        v.location = pad
        v.km_total += d
        v.km_empty += d
        v.hours_driving += h
        v.hours_busy += h
        self.repositions += 1
        self.km_reposition += d
        self.metrics.km_total += d
        self.metrics.km_empty += d
        self.metrics.veh_hours_busy += h
        self._push(t_end, "FREE", None)

    def _dispatch(self):
        candidates = [c for c in self.waiting if not c.stranded]'''),
    # job_plan with segments
    ('''        team = len(job.vehicles) > 1
        pad = job.items[0].origin if job.items else job.backhaul[0].origin
        dur_max = 0.0
        km_sum = km_empty_sum = e_sum = 0.0
        for v in job.vehicles:
            t = t_start
            # empty approach
            d0 = self.world.distance_km(v.location, pad)
            h = self.travel_h(v, v.location, pad, False, False, t)
            e = self.world.energy_km(v.location, pad) * v.cls.energy_wh_per_km
            t += h
            if team:
                t += TEAM_SETUP_H
            # loading
            hm = self.handling_mult(v)
            t += v.cls.load_h * hm * max(1, len(job.items))
            # loaded legs
            prev = pad
            km = d0
            load_kg = sum(c.mass_kg for c in job.items) / len(job.vehicles)
            for stop in job.route:
                dk = self.world.distance_km(prev, stop)
                t += self.travel_h(v, prev, stop, True, team, t)
                e += self.world.energy_km(prev, stop) * v.cls.energy_wh_per_km * (1.0 + 0.6 * load_kg / max(v.cls.capacity_kg, 1))
                t += v.cls.unload_h * hm * sum(1 for c in job.items if c.dest == stop)
                km += dk
                prev = stop
            if job.backhaul:
                t += v.cls.load_h * hm * len(job.backhaul)
                dest = job.backhaul[0].dest
                dk = self.world.distance_km(prev, dest)
                t += self.travel_h(v, prev, dest, True, False, t)
                e += self.world.energy_km(prev, dest) * v.cls.energy_wh_per_km * 1.3
                t += v.cls.unload_h * hm * len(job.backhaul)
                km += dk
                prev = dest
            dur = t - t_start
            dur_max = max(dur_max, dur)
            km_sum += km
            km_empty_sum += d0
            e_sum += e
        return dur_max, km_sum, km_empty_sum, e_sum, False''',
     '''        team = len(job.vehicles) > 1
        pad = job.items[0].origin if job.items else job.backhaul[0].origin
        dur_max = 0.0
        km_sum = km_empty_sum = e_sum = 0.0
        self._last_segments = {}
        for v in job.vehicles:
            t = t_start
            segs = []
            # empty approach
            d0 = self.world.distance_km(v.location, pad)
            h = self.travel_h(v, v.location, pad, False, False, t)
            e = self.world.energy_km(v.location, pad) * v.cls.energy_wh_per_km
            segs.append([v.location, pad, t, t + h, 0.0])
            t += h
            if team:
                t += TEAM_SETUP_H
            # loading
            hm = self.handling_mult(v)
            t_load = v.cls.load_h * hm * max(1, len(job.items))
            segs.append([pad, pad, t, t + t_load, 0.0])
            t += t_load
            # loaded legs
            prev = pad
            km = d0
            load_kg = sum(c.mass_kg for c in job.items) / len(job.vehicles)
            onboard = load_kg
            for stop in job.route:
                dk = self.world.distance_km(prev, stop)
                h = self.travel_h(v, prev, stop, True, team, t)
                segs.append([prev, stop, t, t + h, onboard])
                t += h
                e += self.world.energy_km(prev, stop) * v.cls.energy_wh_per_km * (1.0 + 0.6 * load_kg / max(v.cls.capacity_kg, 1))
                t_un = v.cls.unload_h * hm * sum(1 for c in job.items if c.dest == stop)
                segs.append([stop, stop, t, t + t_un, onboard])
                t += t_un
                onboard -= sum(c.mass_kg for c in job.items if c.dest == stop) / len(job.vehicles)
                km += dk
                prev = stop
            if job.backhaul:
                t_l = v.cls.load_h * hm * len(job.backhaul)
                segs.append([prev, prev, t, t + t_l, 0.0])
                t += t_l
                dest = job.backhaul[0].dest
                dk = self.world.distance_km(prev, dest)
                h = self.travel_h(v, prev, dest, True, False, t)
                bh_kg = sum(c.mass_kg for c in job.backhaul)
                segs.append([prev, dest, t, t + h, bh_kg])
                t += h
                e += self.world.energy_km(prev, dest) * v.cls.energy_wh_per_km * 1.3
                t_un = v.cls.unload_h * hm * len(job.backhaul)
                segs.append([dest, dest, t, t + t_un, bh_kg])
                t += t_un
                km += dk
                prev = dest
            dur = t - t_start
            dur_max = max(dur_max, dur)
            km_sum += km
            km_empty_sum += d0
            e_sum += e
            self._last_segments[v.id] = segs
        return dur_max, km_sum, km_empty_sum, e_sum, False'''),
    ('''        t_end = self.t + dur
        last_stop = job.backhaul[0].dest if job.backhaul else job.route[-1]
        for v in job.vehicles:
            v.busy_until = t_end
            v.location = last_stop''',
     '''        t_end = self.t + dur
        last_stop = job.backhaul[0].dest if job.backhaul else job.route[-1]
        if self.record_trace:
            segs = self._last_segments.get(job.vehicles[0].id, [])
            plan_end = segs[-1][3] if segs else self.t
            extra = t_end - plan_end
            if extra > 1e-9:  # fault recovery or night hibernation at the last stop
                segs = segs + [[last_stop, last_stop, plan_end, t_end, 0.0]]
            self.trace.append({"kind": "team" if len(job.vehicles) > 1 else (job.note or "job"),
                               "veh": job.vehicles[0].id, "team": [u.id for u in job.vehicles],
                               "t0": self.t, "t1": t_end, "segments": segs,
                               "items": [[c.id, round(c.mass_kg, 1), c.priority, c.cls, c.dest] for c in job.items + job.backhaul]})
        for v in job.vehicles:
            v.repos_target = None
            v.busy_until = t_end
            v.location = last_stop'''),
    ('''    unmet_operator_waits: int = 0

    def summary''',
     '''    unmet_operator_waits: int = 0
    repositions: int = 0
    km_reposition: float = 0.0

    def summary'''),
    ('''            "unmet_operator_waits": self.unmet_operator_waits,
        })
        return out''',
     '''            "unmet_operator_waits": self.unmet_operator_waits,
            "repositions": self.repositions,
            "km_reposition": self.km_reposition,
        })
        return out'''),
    ('''        m.operator_cost_musd += m.operator_hours * self.sc.operator_cost_per_h / 1e6
''',
     '''        m.operator_cost_musd += m.operator_hours * self.sc.operator_cost_per_h / 1e6
        m.repositions = self.repositions
        m.km_reposition = self.km_reposition

    # ------------------------------------------------------------- export
    def trace_export(self) -> dict:
        """Everything the live viewer needs to replay this run."""
        nights = []
        t = 0.0
        while t < self.sc.horizon_h:
            ns = self.next_night_start(t)
            ne = self.night_end(ns)
            nights.append([ns, min(ne, self.sc.horizon_h)])
            t = ne + 1e-6
        clean = {}
        for k, v in self.metrics.summary().items():
            clean[k] = None if (isinstance(v, float) and np.isnan(v)) else (float(v) if isinstance(v, (np.floating, float)) else int(v) if isinstance(v, (np.integer,)) else v)
        return {
            "world": self.world.to_dict(),
            "horizon_h": self.sc.horizon_h,
            "nights": nights,
            "landings": [[t, lt.name, pad] for (t, lt, pad) in self.landing_schedule],
            "vehicles": [{"id": v.id, "owner": v.owner, "cls": v.cls.name, "autonomy": v.autonomy,
                          "capacity": v.cls.capacity_kg, "night_ops": v.cls.night_ops} for v in self.vehicles],
            "jobs": self.trace,
            "cargo": [[c.id, c.owner, round(c.mass_kg, 1), c.origin, c.dest, round(c.t_ready, 2),
                       None if c.t_picked is None else round(c.t_picked, 2),
                       None if c.t_delivered is None else round(c.t_delivered, 2), c.priority, c.cls, int(c.stranded)]
                      for c in self.all_cargo],
            "summary": clean,
        }
'''),
])
print("done")
