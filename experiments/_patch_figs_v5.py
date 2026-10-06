import os, ast
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "experiments/make_figures.py")
s = open(p, encoding="utf-8").read()
pairs = [
    # fig_main: immovable share relative to landed cargo
    ('''    df = pd.read_csv(os.path.join(RES, "E1_phases.csv"))
    metrics = [("delay_prio1_p90_h", "A. Urgent cargo:\\n90th-percentile delay (h)"), ("sl24_prio1", "B. Urgent cargo\\ndelivered within 24 h"),
               ("stranded_share", "C. Landed mass no vehicle\\ncould move (%)"), ("night_strandings", "D. Vehicles caught by\\nnight (per year)")]''',
     '''    df = pd.read_csv(os.path.join(RES, "E1_phases.csv"))
    df["stranded_share"] = df.stranded_kg / df.landed_kg
    metrics = [("delay_prio1_p90_h", "A. Urgent cargo:\\n90th-percentile delay (h)"), ("sl24_prio1", "B. Urgent cargo\\ndelivered within 24 h"),
               ("stranded_share", "C. Landed cargo mass that\\nis immovable (%)"), ("night_strandings", "D. Vehicles caught by\\nnight (per year)")]'''),
    # fig15 labels: alternate heights
    ('''    for x, lab in ((800, "LTV, full\\nperformance"), (1600, "LTV, reduced\\nperformance"), (3000, "two LTVs\\nteam lift"), (4500, "three LTVs"), (10000, "10 t hauler"), (13000, "hauler +\\ntwo LTVs"), (15000, "largest\\nelement")):
        ax.axvline(x, color=MUTED, lw=0.7, ls=":")
        ax.text(x * 1.03, 3, lab, fontsize=7, color=INK2, rotation=90, va="bottom", ha="left")''',
     '''    for x, lab, y in ((800, "LTV, full performance", 3), (1600, "LTV, reduced performance", 3), (3000, "two LTVs (team lift)", 3), (4500, "three LTVs", 3), (10000, "10 t hauler", 3), (13000, "hauler + two LTVs", 3), (15000, "largest element", 40)):
        ax.axvline(x, color=MUTED, lw=0.7, ls=":")
        ax.text(x * 1.03, y, lab, fontsize=7.5, color=INK2, rotation=90, va="bottom", ha="left")'''),
    # fig17 two-line labels
    ('''    labels = [f"{ph}, {n} veh." for ph, n in zip(cells.phase, cells.n_vehicles)]''',
     '''    labels = [f"{ph}\\n{n} vehicles" for ph, n in zip(cells.phase, cells.n_vehicles)]'''),
]
for a, b in pairs:
    assert a in s, a[:80]
    s = s.replace(a, b)
ast.parse(s)
open(p, "w", encoding="utf-8").write(s)
print("ok")
