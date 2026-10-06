"""Cargo items and vehicles."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Set


@dataclass
class VehicleClass:
    name: str
    capacity_kg: float          # payload mass a single vehicle can carry
    speed_kmh: float            # nominal driving speed on flat regolith, loaded
    empty_speed_mult: float     # speed multiplier when empty
    energy_wh_per_km: float     # driving energy, empty
    battery_wh: float
    charge_kw: float
    night_ops: bool             # can it drive during the lunar night?
    can_team_lift: bool         # can it carry an oversize item together with others?
    unit_cost_musd: float       # delivered-to-Moon cost of one vehicle (built + landed)
    life_hours: float           # design operating hours (sets the per-operating-hour price)
    mtbf_h: float               # mean operating hours between faults
    mttr_h: float               # mean hours to recover from a fault
    load_h: float               # hours to load one item (crane / interface mate)
    unload_h: float
    life_years: float = 10.0    # calendar life over which the unit cost is amortised


# Provisional parameters. See notes/02 and the paper's parameter table for sources
# and for which values are documented, inferred, or assumed.
VEHICLE_CLASSES = {
    # LTV-class rover (Astrolab FLEX / CLV-1, Lunar Outpost Pegasus). Uncrewed cargo
    # 800 kg at full performance, ~1,500-1,600 kg at reduced performance (NASA ACR24;
    # 2025 workshop slides); design speed 10 km/h, modelled autonomous average 6 km/h.
    # Cost: $219-220M Phase-1 task order + ~$234M Blue Moon MK1 delivery = ~$450M.
    "LTV": VehicleClass("LTV", 1500, 6.0, 1.2, 350, 40_000, 5.0, False, True,
                        450.0, 10 * 8760 * 0.25, 500, 24, 0.5, 0.5, life_years=10.0),
    # Heavy hauler: the >1,600 kg relocation capability NASA says does not exist.
    # 10 t payload, 4 km/h, built to work through the night. Cost is an assumption:
    # ~$200M build + ~4 t landed at Starship's published $100k/kg = ~$600M.
    "HAUL": VehicleClass("HAUL", 10_000, 4.0, 1.2, 900, 120_000, 10.0, True, True,
                         600.0, 10 * 8760 * 0.25, 400, 36, 1.5, 1.5, life_years=10.0),
    # Small utility rover (Lunar Outpost HL-MAPP class: 250 kg rover, 200 kg payload,
    # up to 3 m/s). Modelled 300 kg payload, 3 km/h, ~$60M delivered on a MK1-class lander.
    "MICRO": VehicleClass("MICRO", 300, 3.0, 1.3, 120, 8_000, 1.0, False, False,
                          60.0, 5 * 8760 * 0.25, 300, 12, 0.3, 0.3, life_years=5.0),
}


@dataclass
class Cargo:
    id: int
    owner: str                 # company / agency that owns the cargo
    mass_kg: float
    origin: str                # landing pad
    dest: str
    t_landed: float            # hour the lander touched down
    t_ready: float             # hour the item is offloaded and available for pickup
    priority: int              # 1 = urgent (crew consumables), 2 = normal, 3 = deferrable
    standard: str              # cargo interface standard ("A" = common standard)
    cls: str                   # cargo class label
    t_picked: Optional[float] = None
    t_delivered: Optional[float] = None
    stranded: bool = False     # no feasible vehicle or team could ever move it
    carrier: Optional[int] = None
    team_size: int = 1
    return_mass_kg: float = 0.0   # mass that comes back to the pad later (0 = none)
    return_lag_h: float = 0.0


@dataclass
class Vehicle:
    id: int
    owner: str
    cls: VehicleClass
    location: str
    standards: Set[str]
    autonomy: str              # "teleop" | "supervised" | "autonomous"
    busy_until: float = 0.0
    battery_wh: float = 0.0
    load: List[Cargo] = field(default_factory=list)
    km_total: float = 0.0
    km_empty: float = 0.0
    hours_driving: float = 0.0
    hours_busy: float = 0.0
    hours_failed: float = 0.0
    hours_duty: float = 0.0
    duty_pending: bool = False
    repos_target: Optional[str] = None
    hours_operator: float = 0.0
    jobs: int = 0
    revenue_musd: float = 0.0
    next_fault_h: float = 0.0
    alive: bool = True

    def __post_init__(self):
        self.battery_wh = self.cls.battery_wh

    @property
    def capacity(self) -> float:
        return self.cls.capacity_kg

    def compatible(self, c: Cargo) -> bool:
        return c.standard in self.standards
