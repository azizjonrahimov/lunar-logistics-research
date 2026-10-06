"""Minimum-cost assignment (Hungarian / Jonker-Volgenant style, O(n^3)).

SciPy's linear_sum_assignment is used when available; otherwise a compact
pure-Python implementation of the shortest-augmenting-path algorithm is used.
Both return the same optimal assignment cost (ties may be broken differently).
The pure implementation keeps the simulator runnable in restricted
environments such as the browser (Pyodide without SciPy).
"""
from __future__ import annotations

from typing import List, Tuple

try:  # pragma: no cover - exercised only when scipy is installed
    from scipy.optimize import linear_sum_assignment as _lsa
except Exception:  # pragma: no cover
    _lsa = None


def _hungarian(cost: List[List[float]]) -> Tuple[List[int], List[int]]:
    """Rectangular Hungarian algorithm (rows <= cols after padding).
    Returns (row_indices, col_indices) of the optimal assignment."""
    n = len(cost)
    m = len(cost[0]) if n else 0
    transposed = False
    if n > m:
        cost = [list(col) for col in zip(*cost)]
        n, m = m, n
        transposed = True
    INF = float("inf")
    u = [0.0] * (n + 1)
    v = [0.0] * (m + 1)
    p = [0] * (m + 1)       # p[j] = row assigned to column j (1-based), 0 = none
    way = [0] * (m + 1)
    for i in range(1, n + 1):
        p[0] = i
        j0 = 0
        minv = [INF] * (m + 1)
        used = [False] * (m + 1)
        while True:
            used[j0] = True
            i0 = p[j0]
            delta = INF
            j1 = 0
            for j in range(1, m + 1):
                if not used[j]:
                    cur = cost[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j] = cur
                        way[j] = j0
                    if minv[j] < delta:
                        delta = minv[j]
                        j1 = j
            for j in range(m + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while True:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
            if j0 == 0:
                break
    rows, cols = [], []
    for j in range(1, m + 1):
        if p[j] != 0:
            rows.append(p[j] - 1)
            cols.append(j - 1)
    if transposed:
        rows, cols = cols, rows
    order = sorted(range(len(rows)), key=lambda k: rows[k])
    return [rows[k] for k in order], [cols[k] for k in order]


def min_cost_assignment(cost) -> Tuple[List[int], List[int]]:
    """Return (row_idx, col_idx) minimising total cost over a rectangular matrix."""
    if _lsa is not None:
        r, c = _lsa(cost)
        return list(map(int, r)), list(map(int, c))
    return _hungarian([list(map(float, row)) for row in cost])
