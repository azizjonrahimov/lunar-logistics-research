"""Scenario serialisation: Scenario <-> JSON, plus the named scenario library.

A scenario file is plain JSON so that the same inputs can be loaded by the
Python engine, the browser port and any other tool. Example:

    {
      "name": "P2-four-vehicles",
      "landings_per_year": {"CLPS": 4, "MK1": 3, "LARGE": 1},
      "cargo_owners": ["NASA", "NASA", "NASA", "NASA", "CoA", "CoA", "CoB", "CoC"],
      "bulk_flows": [{"origin": "CONSTR", "dest": "BASE", "tonnes_per_year": 300, "lot_kg": 1000}],
      "fleet": [["NASA", "LTV", "supervised", "A"], ["CoA", "HAUL", "supervised", "A"]],
      "night_fraction": 0.15, "n_operators": 3
    }
"""
from __future__ import annotations

import dataclasses
import json
import os
from typing import Any, Dict, List

from .scenario import Scenario, BulkFlow


def scenario_to_dict(sc: Scenario) -> Dict[str, Any]:
    d = dataclasses.asdict(sc)
    d["bulk_flows"] = [dataclasses.asdict(b) for b in sc.bulk_flows]
    d["fleet"] = [list(v) for v in sc.fleet]
    d["vot_usd_per_h"] = {str(k): v for k, v in sc.vot_usd_per_h.items()}
    return d


def scenario_from_dict(d: Dict[str, Any]) -> Scenario:
    d = dict(d)
    d["bulk_flows"] = [BulkFlow(**b) if isinstance(b, dict) else BulkFlow(*b) for b in d.get("bulk_flows", [])]
    d["fleet"] = [tuple(v) for v in d.get("fleet", [])]
    if "vot_usd_per_h" in d:
        d["vot_usd_per_h"] = {int(k): float(v) for k, v in d["vot_usd_per_h"].items()}
    known = {f.name for f in dataclasses.fields(Scenario)}
    unknown = set(d) - known
    if unknown:
        raise ValueError(f"unknown scenario fields: {sorted(unknown)}")
    return Scenario(**d)


def save_scenario(sc: Scenario, path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(scenario_to_dict(sc), f, indent=2)


def load_scenario(path: str) -> Scenario:
    with open(path, encoding="utf-8") as f:
        return scenario_from_dict(json.load(f))


def library() -> Dict[str, Scenario]:
    """Named scenarios used in the paper (phases and the fleet-size variants)."""
    import importlib
    scen = importlib.import_module("experiments.scenarios")
    run_all = importlib.import_module("experiments.run_all")
    out: Dict[str, Scenario] = {}
    for ph, sc in scen.PHASES.items():
        out[f"{ph}-default"] = sc
    for n, fleet in run_all.FLEETS.items():
        out[f"P2-{n}-vehicles"] = scen.PHASES["P2"].with_(name=f"P2-{n}-vehicles", fleet=fleet, n_operators=max(2, n // 2))
    return out
