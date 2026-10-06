"""Site graph for a south-pole Moon base.

Coordinates are in kilometres on a local tangent plane. Distances between sites
are Euclidean distance times a tortuosity factor (real traverses wind around
craters and boulders, so they are longer than the straight line). Each edge
carries a slope class that slows vehicles and raises energy use.

Default layout follows the spacing rules in NASA's 2024 white paper
"Lunar Mobility Drivers and Needs": landing pads sit more than 1 km from the
base because plume ejecta is dangerous, and some cargo travels up to about
5 km (e.g. to a permanently shadowed region).

The module has no third-party dependency: shortest paths are computed with
Floyd-Warshall on the (small) site graph.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Dict, List, Tuple


@dataclass
class Site:
    name: str
    x_km: float
    y_km: float
    kind: str  # pad | base | depot | power | isru | science | psr | construction
    night_dark: bool = True  # whether the site is dark during the local night


# Slope class -> (speed multiplier, energy multiplier)
SLOPE_FACTORS = {
    "flat": (1.00, 1.00),      # 0-5 degrees
    "moderate": (0.75, 1.35),  # 5-10 degrees
    "steep": (0.50, 1.90),     # 10-20 degrees
}


class World:
    def __init__(self, sites: List[Site], edges: List[Tuple[str, str, str]],
                 tortuosity: float = 1.3):
        self.sites: Dict[str, Site] = {s.name: s for s in sites}
        self.names: List[str] = [s.name for s in sites]
        self.tortuosity = tortuosity
        self.edges: Dict[Tuple[str, str], dict] = {}
        for a, b, slope in edges:
            d = self._euclid(a, b) * tortuosity
            sp, en = SLOPE_FACTORS[slope]
            e = {"dist": d, "slope": slope, "speed_mult": sp, "energy_mult": en, "time_cost": d / sp}
            self.edges[(a, b)] = e
            self.edges[(b, a)] = e
        self._paths: Dict[Tuple[str, str], List[str]] = {}
        self._cache: Dict[Tuple[str, str], Tuple[float, float, float]] = {}
        self._all_pairs()

    def _euclid(self, a: str, b: str) -> float:
        sa, sb = self.sites[a], self.sites[b]
        return math.hypot(sa.x_km - sb.x_km, sa.y_km - sb.y_km)

    def _all_pairs(self):
        """Floyd-Warshall on time cost; then accumulate distance and energy along paths."""
        n = len(self.names)
        idx = {name: i for i, name in enumerate(self.names)}
        INF = float("inf")
        cost = [[INF] * n for _ in range(n)]
        nxt = [[-1] * n for _ in range(n)]
        for i in range(n):
            cost[i][i] = 0.0
            nxt[i][i] = i
        for (a, b), e in self.edges.items():
            i, j = idx[a], idx[b]
            if e["time_cost"] < cost[i][j]:
                cost[i][j] = e["time_cost"]
                nxt[i][j] = j
        for k in range(n):
            for i in range(n):
                if cost[i][k] == INF:
                    continue
                for j in range(n):
                    c = cost[i][k] + cost[k][j]
                    if c < cost[i][j]:
                        cost[i][j] = c
                        nxt[i][j] = nxt[i][k]
        for a in self.names:
            for b in self.names:
                i, j = idx[a], idx[b]
                if nxt[i][j] == -1:
                    raise ValueError(f"site graph is disconnected between {a} and {b}")
                path = [a]
                cur = i
                while cur != j:
                    cur = nxt[cur][j]
                    path.append(self.names[cur])
                dist = eq = en = 0.0
                for u, v in zip(path[:-1], path[1:]):
                    e = self.edges[(u, v)]
                    dist += e["dist"]
                    eq += e["time_cost"]
                    en += e["dist"] * e["energy_mult"]
                self._cache[(a, b)] = (dist, eq, en)
                self._paths[(a, b)] = path

    def distance_km(self, a: str, b: str) -> float:
        """Path length in km."""
        return self._cache[(a, b)][0]

    def equiv_flat_km(self, a: str, b: str) -> float:
        """Distance divided by slope speed multipliers; travel time = this / speed."""
        return self._cache[(a, b)][1]

    def energy_km(self, a: str, b: str) -> float:
        """Distance weighted by slope energy multipliers."""
        return self._cache[(a, b)][2]

    def path(self, a: str, b: str) -> List[str]:
        return self._paths[(a, b)]

    @property
    def pads(self) -> List[str]:
        return [n for n, s in self.sites.items() if s.kind == "pad"]

    @property
    def destinations(self) -> List[str]:
        return [n for n, s in self.sites.items() if s.kind != "pad"]

    def to_dict(self) -> dict:
        """Serialisable description used by the live viewer."""
        return {
            "sites": [{"name": s.name, "x": s.x_km, "y": s.y_km, "kind": s.kind} for s in self.sites.values()],
            "edges": [{"a": a, "b": b, "dist": e["dist"], "slope": e["slope"]}
                      for (a, b), e in self.edges.items() if a < b],
        }


def build_default_world() -> World:
    """Nine-site base layout. Distances are chosen to reproduce NASA's stated
    spacing (pads > 1 km from the base, farthest work site about 5 km)."""
    sites = [
        Site("PAD_A", 0.0, 0.0, "pad"),
        Site("PAD_B", 1.2, -0.9, "pad"),
        Site("DEPOT", 1.1, 0.7, "depot"),          # cargo staging near base
        Site("BASE", 1.4, 1.0, "base"),            # habitat zone
        Site("POWER", 1.9, 1.6, "power"),          # power plant / solar towers
        Site("CONSTR", 1.0, 1.5, "construction"),  # roads, pads, berms
        Site("ISRU", 2.6, 0.9, "isru"),            # oxygen-from-regolith pilot
        Site("SCI_1", 3.2, 2.3, "science"),
        Site("PSR", 4.6, 3.0, "psr", night_dark=True),  # shadowed crater rim, ~5 km
    ]
    edges = [
        ("PAD_A", "DEPOT", "flat"),
        ("PAD_B", "DEPOT", "moderate"),
        ("PAD_A", "PAD_B", "flat"),
        ("DEPOT", "BASE", "flat"),
        ("BASE", "POWER", "moderate"),
        ("BASE", "CONSTR", "flat"),
        ("DEPOT", "ISRU", "moderate"),
        ("BASE", "ISRU", "moderate"),
        ("POWER", "SCI_1", "steep"),
        ("ISRU", "SCI_1", "moderate"),
        ("SCI_1", "PSR", "steep"),
        ("ISRU", "PSR", "steep"),
    ]
    return World(sites, edges)
