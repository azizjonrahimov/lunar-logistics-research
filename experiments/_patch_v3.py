"""Fixes: night-penalty bug when night_fraction=0, teleop speed model from the measured table."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rep(path, pairs):
    p = os.path.join(ROOT, path)
    s = open(p, encoding="utf-8").read()
    for a, b in pairs:
        assert a in s, (path, a[:80])
        s = s.replace(a, b)
    open(p, "w", encoding="utf-8").write(s)
    print("patched", path)


rep("lunarsim/engine.py", [
    ('''# Teleoperation slowdown. NASA JSC LTV teleoperation trials (Litaker et al., NASA
# TM-20240001217) report average speeds of 3.24 / 2.56 / 2.03 / 1.76 km/h at 0 / 4 / 6 / 8 s
# round-trip latency. A fit of v = v0 / (1 + k * RTT) gives k ~ 0.105 per second, and the
# zero-latency teleop speed is about 0.54 of the 6 km/h autonomous average we assume.
TELEOP_BASE_MULT = 0.54
TELEOP_K = 0.105
SUPERVISED_MULT = 0.9''',
     '''# Teleoperation slowdown. NASA JSC LTV teleoperation trials (Litaker et al., NASA
# TM-20240001217) report average speeds of 3.24 / 2.56 / 2.03 / 1.76 km/h at 0 / 4 / 6 / 8 s
# round-trip latency. Inside the measured range we interpolate the table exactly; beyond
# 8 s we extrapolate with the move-and-wait law v = v8 (1 + 8 k) / (1 + k RTT), k = 1/T_move
# with a 10 s command segment, which reproduces Mars-rover command-cycle speeds of a few
# tens of metres per hour at 20-minute delays. Speeds are relative to the 6 km/h autonomous
# average assumed for a 10 km/h-class rover.
TELEOP_TABLE = ((0.0, 3.24), (4.0, 2.56), (6.0, 2.03), (8.0, 1.76))
TELEOP_K = 0.10
AUTONOMOUS_REF_KMH = 6.0
TELEOP_BASE_MULT = TELEOP_TABLE[0][1] / AUTONOMOUS_REF_KMH   # kept for backward compatibility
SUPERVISED_MULT = 0.9


def teleop_speed_kmh(rtt_s: float) -> float:
    """Average teleoperated driving speed as a function of round-trip latency."""
    xs = [p[0] for p in TELEOP_TABLE]
    ys = [p[1] for p in TELEOP_TABLE]
    if rtt_s <= xs[-1]:
        return float(np.interp(rtt_s, xs, ys))
    return ys[-1] * (1.0 + TELEOP_K * xs[-1]) / (1.0 + TELEOP_K * rtt_s)'''),
    ('''    def autonomy_speed_mult(self, v: Vehicle) -> float:
        if v.autonomy == "teleop":
            return TELEOP_BASE_MULT / (1.0 + TELEOP_K * self.rtt_s)''',
     '''    def autonomy_speed_mult(self, v: Vehicle) -> float:
        if v.autonomy == "teleop":
            return teleop_speed_kmh(self.rtt_s) / AUTONOMOUS_REF_KMH'''),
    ('''    def night_end(self, t: float) -> float:
        cyc = math.floor(t / LUNAR_CYCLE_H)
        return (cyc + 1) * LUNAR_CYCLE_H''',
     '''    def night_end(self, t: float) -> float:
        """End of the night that contains t, or of the next night if t is in daylight."""
        if self.sc.night_fraction <= 0:
            return float("inf")
        if self.is_night(t):
            return (math.floor(t / LUNAR_CYCLE_H) + 1) * LUNAR_CYCLE_H
        return self.next_night_start(t) + self.sc.night_fraction * LUNAR_CYCLE_H'''),
    ('''        # wake up at the end of every lunar night so parked vehicles get dispatched
        t = self.night_end(0.0)
        while t < self.sc.horizon_h:
            self._push(t + 1e-6, "NIGHT_END", None)
            t += LUNAR_CYCLE_H''',
     '''        # wake up at the end of every lunar night so parked vehicles get dispatched
        if self.sc.night_fraction > 0:
            t = self.night_end(0.0)
            while t < self.sc.horizon_h:
                self._push(t + 1e-6, "NIGHT_END", None)
                t += LUNAR_CYCLE_H'''),
    ('''        # night: a vehicle that cannot work in the dark and is caught out hibernates
        t_end = self.t + dur
        for v in job.vehicles:
            if not v.cls.night_ops:
                ns = self.next_night_start(self.t)
                if t_end > ns:
                    dur += self.night_end(ns) - ns
                    self.metrics.night_strandings += 1
                    break''',
     '''        # night: a vehicle that cannot work in the dark and is caught out hibernates
        t_end = self.t + dur
        if self.sc.night_fraction > 0:
            for v in job.vehicles:
                if not v.cls.night_ops:
                    ns = self.next_night_start(self.t)
                    if t_end > ns:
                        dur += self.sc.night_fraction * LUNAR_CYCLE_H
                        self.metrics.night_strandings += 1
                        break'''),
    ('''        nights = []
        t = 0.0
        while t < self.sc.horizon_h:
            ns = self.next_night_start(t)
            ne = self.night_end(ns)
            nights.append([ns, min(ne, self.sc.horizon_h)])
            t = ne + 1e-6''',
     '''        nights = []
        t = 0.0
        while self.sc.night_fraction > 0 and t < self.sc.horizon_h:
            ns = self.next_night_start(t)
            ne = ns + self.sc.night_fraction * LUNAR_CYCLE_H
            nights.append([ns, min(ne, self.sc.horizon_h)])
            t = ne + 1e-6'''),
])

rep("lunarsim/vv.py", [
    ('''from .engine import Simulation, TELEOP_BASE_MULT, TELEOP_K, Job''',
     '''from .engine import Simulation, Job, teleop_speed_kmh'''),
    ('''        v_model = 6.0 * TELEOP_BASE_MULT / (1.0 + TELEOP_K * rtt)
        out.append(Check(f"Teleoperated speed at {rtt:.0f} s RTT", v_obs, v_model, 0.03, "km/h",
                         "NASA JSC LTV teleoperation trial average speed").finish())''',
     '''        v_model = teleop_speed_kmh(rtt)
        out.append(Check(f"Teleoperated speed at {rtt:.0f} s RTT", v_obs, v_model, 0.01, "km/h",
                         "NASA JSC LTV teleoperation trial average speed").finish())'''),
    ('''        LANDER_TYPES["ONE"] = LanderType("ONE", (100, 100), (0.0, 0.0), True, 100)
        scn.CARGO_CLASSES[:] = [("consumables", (99.9, 100.0), {"BASE": 1.0}, 1, 1.0)]''',
     '''        LANDER_TYPES["ONE"] = LanderType("ONE", (100, 100), (0.0, 0.0), True, 100)
        scn.CARGO_CLASSES[:] = [("consumables", (100.0, 100.0), {"BASE": 1.0}, 1, 1.0)]
        saved_ret = scn.RETURN_ITEM_PROB
        scn.RETURN_ITEM_PROB = 0.0'''),
    ('''    finally:
        LANDER_TYPES.clear()
        LANDER_TYPES.update(saved_lt)
        scn.CARGO_CLASSES[:] = saved_classes''',
     '''    finally:
        LANDER_TYPES.clear()
        LANDER_TYPES.update(saved_lt)
        scn.CARGO_CLASSES[:] = saved_classes
        scn.RETURN_ITEM_PROB = saved_ret'''),
])
print("done")
