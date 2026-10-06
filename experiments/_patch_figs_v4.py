import os, ast
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "experiments/make_figures.py")
s = open(p, encoding="utf-8").read()
pairs = [
    ('''    box(0.01, 0.55, 0.26, 0.43, "Demand",''', '''    box(0.01, 0.55, 0.25, 0.43, "Demand",'''),
    ('''    box(0.01, 0.03, 0.26, 0.46, "Environment",''', '''    box(0.01, 0.03, 0.25, 0.46, "Environment",'''),
    ('''    box(0.365, 0.22, 0.27, 0.56, "Event engine", ["LANDING, READY, FREE,", "TICK, WAKE, REPOS, DUTY", "Prices each job: approach,",
                                                   "loading, slope, night,", "latency, faults; logs delays,", "km, energy, cost"], INK)''',
     '''    box(0.375, 0.14, 0.25, 0.72, "Event engine", ["LANDING, READY, FREE,", "TICK, WAKE, REPOS, DUTY", "Prices each job: approach,",
                                                   "loading, slope, night,", "latency, faults", "Logs delays, km, energy,", "cost, revenue"], INK)'''),
    ('''    box(0.73, 0.55, 0.26, 0.43, "Dispatch mechanism",''', '''    box(0.74, 0.55, 0.25, 0.43, "Dispatch mechanism",'''),
    ('''    box(0.73, 0.03, 0.26, 0.46, "Fleet",''', '''    box(0.74, 0.03, 0.25, 0.46, "Fleet",'''),
    ('''    gl, gr = 0.3175, 0.6825
    arrows = [((0.27, 0.70), (0.365, 0.62), MUTED, "landings,\\nlots", (gl, 0.74)),
              ((0.27, 0.30), (0.365, 0.38), MUTED, "night, delay,\\nfaults", (gl, 0.26)),
              ((0.635, 0.62), (0.73, 0.70), MUTED, "waiting cargo,\\nfree vehicles", (gr, 0.76)),
              ((0.73, 0.60), (0.635, 0.52), C["blue"], "jobs", (gr, 0.50)),
              ((0.635, 0.36), (0.73, 0.28), MUTED, "state,\\ncosts", (gr, 0.24))]''',
     '''    gl, gr = 0.3175, 0.6825
    arrows = [((0.26, 0.70), (0.375, 0.62), MUTED, "landings,\\nlots", (gl, 0.75)),
              ((0.26, 0.30), (0.375, 0.38), MUTED, "night, delay,\\nfaults", (gl, 0.25)),
              ((0.625, 0.62), (0.74, 0.70), MUTED, "waiting cargo,\\nfree vehicles", (gr, 0.77)),
              ((0.74, 0.60), (0.625, 0.52), C["blue"], "jobs", (gr, 0.49)),
              ((0.625, 0.36), (0.74, 0.28), MUTED, "state,\\ncosts", (gr, 0.23))]'''),
]
for a, b in pairs:
    assert a in s, a[:70]
    s = s.replace(a, b)
ast.parse(s)
open(p, "w", encoding="utf-8").write(s)
print("ok")
