"""Sequential replication until a target statistical precision is reached.

Following Hoad, Robinson & Davies (2010) and Law (2007), replications are added
in blocks until the confidence-interval half-width of every target metric is
within a relative tolerance of its mean (default: 99% confidence, 1%). Returns
the number of replications used and the final estimates.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional
from multiprocessing import Pool
import math
import os

import numpy as np
from scipy import stats

from .engine import run
from .scenario import Scenario


@dataclass
class PrecisionResult:
    metric: str
    n: int
    mean: float
    half_width: float
    rel_half_width: float
    target_rel: float
    confidence: float
    reached: bool
    history: List[Dict] = field(default_factory=list)


def _one(args):
    sc, mech, seed, kw = args
    return run(sc, mech, seed=seed, **kw)


def ci_half_width(x: np.ndarray, confidence: float) -> float:
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    if len(x) < 2:
        return float("inf")
    t = stats.t.ppf(0.5 + confidence / 2.0, len(x) - 1)
    return float(t * x.std(ddof=1) / math.sqrt(len(x)))


def run_until_precise(sc: Scenario, mech: Callable, metrics: Dict[str, float], confidence: float = 0.99,
                      block: int = 50, n_min: int = 30, n_max: int = 4000, procs: Optional[int] = None,
                      seed_offset: int = 0, mech_kwargs: Optional[dict] = None, verbose: bool = False):
    """metrics: {metric_name: target relative half-width}. Returns (results dict, DataFrame of runs)."""
    import pandas as pd
    kw = mech_kwargs or {}
    rows: List[dict] = []
    histories = {m: [] for m in metrics}
    n = 0
    with Pool(procs or max(1, os.cpu_count() - 2)) as pool:
        while True:
            need = max(block, n_min - n) if n < n_min else block
            seeds = list(range(seed_offset + n, seed_offset + n + need))
            rows += pool.map(_one, [(sc, mech, s, kw) for s in seeds], chunksize=4)
            n = len(rows)
            df = pd.DataFrame(rows)
            done = True
            for m, target in metrics.items():
                x = df[m].values
                hw = ci_half_width(x, confidence)
                mean = float(np.nanmean(x))
                rel = hw / abs(mean) if mean != 0 else float("inf")
                histories[m].append({"n": n, "mean": mean, "half_width": hw, "rel": rel})
                if rel > target:
                    done = False
            if verbose:
                print(n, {m: round(h[-1]["rel"], 4) for m, h in histories.items()})
            if (done and n >= n_min) or n >= n_max:
                break
    results = {}
    for m, target in metrics.items():
        h = histories[m][-1]
        results[m] = PrecisionResult(m, n, h["mean"], h["half_width"], h["rel"], target, confidence,
                                     h["rel"] <= target, histories[m])
    return results, pd.DataFrame(rows)
