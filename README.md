# Lunar surface logistics marketplace: verified testbed, experiments, paper and live simulator

This folder holds everything behind the preprint **"Who Hauls the Habitat? A Verified Simulation Testbed, a
Pooled Dispatch Marketplace and a Reference Design for Lunar Surface Logistics"** (version 2:
`paper/lunar_logistics_marketplace_paper_v2.pdf`) and the browser simulator **LunarSim Live**
(https://claude.ai/artifact/4b4NMcz74BxnqPn2epaZgL, source in `web/`).

## What is here

| Path | Contents |
|---|---|
| `lunarsim/` | The discrete-event simulator. `world.py` (nine-site base graph, Floyd-Warshall), `entities.py` (cargo, vehicle classes), `scenario.py` (demand, landers, bulk flows, environment, costs), `engine.py` (event loop, job pricing, metrics, trace export), `dispatch.py` (in-house, pooled greedy, batched Hungarian assignment, marketplace with bundling / consolidation / team lift / backhaul / night awareness / anticipatory staging, and ablation variants), `assign.py` (dependency-free Hungarian algorithm), `vv.py` (13 verification checks), `precision.py` (sequential replication to a target confidence-interval width). |
| `tests/test_verification.py` | pytest suite: the 13 verification checks plus determinism, invariants, Hungarian-vs-SciPy, team lift, trace export (19 tests). |
| `experiments/scenarios.py` | Demand phases P1 (pre-2029), P2 (2029-2032), P3 (2032+). |
| `experiments/run_all.py` | Experiment suites E1-E14; `run_e14_long.py` continues the precision run to a 1% half-width. |
| `experiments/make_figures.py` | All figures (`figures/`) and summary tables (`results/table_*.csv`), including the V&V table. |
| `web/template.html`, `web/build_web.py` | The browser port of the simulator (single page, no dependencies); the build script embeds Python reference values for the cross-implementation check and writes `web/index.html`. |
| `paper/` | Paper source (`part1_front.html` ... `part4_back.html`, `style.css`), `build.py` (assembles `paper.html`, fills tables and settled numbers, prints the PDF with headless Chrome), PDFs, page previews. |
| `notes/` | Research notes compiled before modelling: methods playbook, lunar logistics literature and sourced parameters, marketplace mechanisms and simulation design, demand / supply / competitor facts. Every number carries its URL and a confidence grade. |
| `results/` | Raw per-seed results (`E*.csv`), the weight search (`E9_best.json`), precision runs (`E14_*.json`, `E14_precision_*.csv`), derived tables. |

## Reproduce

```
py -3 -m venv .venv
.venv\Scripts\python -m pip install numpy scipy matplotlib pandas pymupdf pytest
.venv\Scripts\python -m pytest tests -q                 # 19 tests, ~2 min (M/G/1 check is the slow one)
.venv\Scripts\python experiments\run_all.py              # E1-E14, ~40 min on 10 cores; pass e1 e2 ... for a subset
.venv\Scripts\python experiments\run_e14_long.py         # optional: precision run to 1% (about an hour)
.venv\Scripts\python experiments\make_figures.py         # figures/*.png and results/table_*.csv (add "vv" to run the checks)
.venv\Scripts\python web\build_web.py                    # web/index.html with embedded Python reference values
.venv\Scripts\python paper\build.py                      # paper/paper.html and the PDF (needs Chrome)
```

Seeds are 0-29 per cell (0-19 for E5, 0-7 for the E9 search, 0..n for the sequential runs). The demand stream
uses the cell seed and the operations stream the seed plus 100,003 (common random numbers). Runs are deterministic.

## Quick start in Python

```python
import sys; sys.path.insert(0, ".")
from lunarsim import run, dispatch, Simulation
from experiments.scenarios import PHASES
out = run(PHASES["P2"], dispatch.marketplace, seed=0)
print(out["delay_prio1_p90_h"], out["stranded_kg"] / out["landed_kg"], out["cost_per_kg_usd"])
sim = Simulation(PHASES["P2"], dispatch.marketplace, seed=0, mech_kwargs={"trace": True}); sim.run()
replay = sim.trace_export()   # everything the live viewer animates
```

## Verification summary

All 13 checks pass (Appendix B of the paper): kinematics and slope identities, the four NASA JSC teleoperation
speeds (exact), dark-share of time, two mass-conservation identities, the stranding rule, common random numbers,
fleet amortisation, and the M/G/1 Pollaczek-Khinchine queue (0.5% error). The browser port agrees with the
Python implementation within combined 95% CIs on all 24 Phase-2 metric cells (Verification tab of the live page).

## Caveats

Parameters marked *assumed* in Appendix A (hauler cost, bulk flows, operator cost, value of time, other-duty
share, offload delays, energy, anticipation window) are our choices and are swept in the sensitivity analysis.
Several published numbers (LTV teleoperation speeds, mining-haulage availability, LTV requirements) were only
available through secondary summaries; they are flagged in `notes/02_*.md` and `notes/03_*.md`.
