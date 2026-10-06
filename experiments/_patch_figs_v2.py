"""Patch make_figures.py: Times New Roman, label fixes, new figures for E11-E14, V&V table, design diagram."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "experiments/make_figures.py")
s = open(p, encoding="utf-8").read()


def rep(a, b):
    global s
    assert a in s, a[:90]
    s = s.replace(a, b)


rep('''    "font.family": "DejaVu Sans", "font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9,''',
    '''    "font.family": "Times New Roman", "mathtext.fontset": "stix", "font.size": 10, "axes.titlesize": 10.5, "axes.labelsize": 10,''')

# ---- architecture figure: rewrite
start = s.index("def fig_architecture():")
end = s.index("# ---------------------------------------------------------------------------\n# Fig 3")
s = s[:start] + '''def fig_architecture():
    fig, ax = plt.subplots(figsize=(8.8, 4.3))
    ax.axis("off")

    def box(x, y, w, h, title, lines, col):
        pch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.008,rounding_size=0.02", fc="white", ec=col, lw=1.6)
        ax.add_patch(pch)
        ax.text(x + w / 2, y + h - 0.03, title, ha="center", va="top", fontsize=10, color=col, fontweight="bold")
        for i, ln in enumerate(lines):
            ax.text(x + 0.02, y + h - 0.13 - 0.082 * i, ln, fontsize=8, color=INK2, va="top")

    box(0.01, 0.55, 0.30, 0.43, "Demand", ["Poisson lander arrivals by class", "Manifest sampler, 5 cargo classes",
                                            "Bulk lots (regolith, feedstock)", "Return items (trash, samples)"], C["orange"])
    box(0.01, 0.03, 0.30, 0.46, "Environment", ["9-site graph, slope classes", "Lunar night (dark share f)",
                                                 "Earth-Moon latency, fan-out", "Faults (MTBF, MTTR), other duties"], C["green"])
    box(0.355, 0.24, 0.29, 0.54, "Event engine", ["LANDING, READY, FREE,", "TICK, WAKE, REPOS, DUTY", "Prices each job: approach,",
                                                   "loading, slope, night, latency,", "faults; logs delays, km, cost"], INK)
    box(0.69, 0.55, 0.30, 0.43, "Dispatch mechanism", ["In-house (bilateral contracts)", "Pooled greedy",
                                                        "Batched assignment (Hungarian)", "Marketplace (ours)"], C["blue"])
    box(0.69, 0.03, 0.30, 0.46, "Fleet", ["LTV 1.5 t, HAUL 10 t, MICRO 0.3 t", "Owner, standards, autonomy",
                                           "Battery and night capability", "Revenue per owner"], C["violet"])
    arrows = [((0.31, 0.72), (0.355, 0.66), MUTED, "landings, lots", (0.332, 0.745), "center"),
              ((0.31, 0.30), (0.355, 0.38), MUTED, "night, delay, faults", (0.332, 0.26), "center"),
              ((0.645, 0.64), (0.69, 0.72), MUTED, "waiting cargo,\\nfree vehicles", (0.667, 0.80), "center"),
              ((0.69, 0.62), (0.645, 0.54), C["blue"], "jobs", (0.667, 0.52), "center"),
              ((0.645, 0.36), (0.69, 0.28), MUTED, "state, costs", (0.667, 0.22), "center")]
    for (p0, p1, col, lab, (lx, ly), ha) in arrows:
        ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=11, color=col, lw=1.2))
        ax.text(lx, ly, lab, fontsize=7.5, color=col if col != MUTED else INK2, ha=ha, va="center",
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    save(fig, "fig02_architecture")


''' + s[end:]

# ---- demand figure: vertical-line labels inside the axes mid-height
rep('''    for x, lab in ((800, "LTV 0.8 t"), (1600, "1.6 t"), (10000, "HAUL 10 t")):
        ax.axvline(x, color=MUTED, lw=0.8, ls="--")
        ax.text(x, ax.get_ylim()[1] * 0.95, lab, fontsize=6.5, color=MUTED, rotation=90, va="top", ha="right")''',
    '''    ymax = ax.get_ylim()[1]
    for x, lab, yf in ((800, "LTV 0.8 t", 0.62), (1600, "LTV 1.6 t", 0.78), (10000, "HAUL 10 t", 0.62)):
        ax.axvline(x, color=MUTED, lw=0.8, ls="--")
        ax.text(x * 1.06, ymax * yf, lab, fontsize=7.5, color=INK2, va="center", ha="left",
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.9))''')

# ---- latency figure labels at bottom
rep('''    for x, lab in ((2.6, "Moon,\\ndirect"), (16, "Moon,\\nrelayed"), (602.6, "Mars\\n(close)"), (1322.6, "Mars\\n(far)")):
        ax.axvline(x, color=MUTED, lw=0.7, ls=":")
        ax.text(x, ax.get_ylim()[1] * 0.9, lab, fontsize=6, color=MUTED, ha="center", va="top")
    ax.legend(fontsize=6.5, loc="lower right")''',
    '''    y0, y1 = ax.get_ylim()
    for x, lab, ha in ((2.6, "Moon\\ndirect", "left"), (16, "Moon\\nrelayed", "left"), (602.6, "Mars\\nnear", "right"), (1322.6, "Mars\\nfar", "left")):
        ax.axvline(x, color=MUTED, lw=0.7, ls=":")
        ax.text(x * (1.1 if ha == "left" else 0.9), y1 * 0.75, lab, fontsize=7, color=INK2, ha=ha, va="top")
    ax.legend(fontsize=7, loc="lower right")''')
rep('''    fig, axes = plt.subplots(1, 3, figsize=(10, 2.9))
    acol = {"teleop": C["red"], "supervised": C["yellow"], "autonomous": C["aqua"]}''',
    '''    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.1))
    fig.subplots_adjust(wspace=0.3)
    acol = {"teleop": C["red"], "supervised": C["yellow"], "autonomous": C["aqua"]}''')

# ---- standards
rep('''        ax.set_xlabel("cargo built to the common interface standard (%)")''', '''        ax.set_xlabel("common-standard cargo (%)")''')

# ---- environment spacing
rep('''    fig, axes = plt.subplots(1, 3, figsize=(10, 2.9))
    panels = [("night_fraction", "A. Dark share of the lunar cycle", "delay_prio1_p90_h", "urgent 90th-pct delay (h)"),''',
    '''    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.0))
    fig.subplots_adjust(wspace=0.36)
    panels = [("night_fraction", "A. Dark share of the lunar cycle", "delay_prio1_p90_h", "urgent 90th-pct delay (h)"),''')

# ---- tuned suptitle
rep('''    fig.suptitle(f"Auction weights searched on Phase 2 (40 random configs x 8 seeds), tested on all phases with 30 fresh seeds. "
                 f"Best: w1={p['w_p1']:.1f}, w2={p['w_p2']:.1f}, age={p['w_age']:.2f}, fill={p['fill']:.2f}, wait={p['max_wait']:.0f} h",
                 fontsize=7.5, y=1.04)''',
    '''    fig.suptitle(f"Auction weights searched on Phase 2 (40 random configurations, 8 seeds), tested on all phases with 30 fresh seeds.\\n"
                 f"Best configuration: w1 = {p['w_p1']:.1f} h, w2 = {p['w_p2']:.1f} h, age = {p['w_age']:.2f}, fill = {p['fill']:.2f}, max wait = {p['max_wait']:.0f} h",
                 fontsize=8.5, y=1.08)''')

# ---- ablation variants: include anticipation
rep('''    variants = ["marketplace", "no_bundling", "no_consolidate", "no_team_lift", "no_backhaul", "no_night_aware", "no_priority"]
    vlab = {"marketplace": "Full marketplace", "no_bundling": "- bundling", "no_consolidate": "- consolidation",
            "no_team_lift": "- team lift", "no_backhaul": "- backhaul", "no_night_aware": "- night awareness", "no_priority": "- priority credit"}''',
    '''    variants = ["marketplace", "no_bundling", "no_consolidate", "no_team_lift", "no_anticipate", "no_backhaul", "no_night_aware", "no_priority"]
    vlab = {"marketplace": "Full marketplace", "no_bundling": "without bundling", "no_consolidate": "without consolidation",
            "no_team_lift": "without team lift", "no_anticipate": "without anticipation", "no_backhaul": "without backhaul",
            "no_night_aware": "without night awareness", "no_priority": "without priority credit"}''')

# ---- new figures appended before __main__
new_funcs = '''

# ---------------------------------------------------------------------------
# Fig 15: capacity ladder (E12)
# ---------------------------------------------------------------------------
def fig_ladder():
    df = pd.read_csv(os.path.join(RES, "E12_capacity_ladder.csv"))
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    for ph, col in (("P1", C["aqua"]), ("P2", C["yellow"]), ("P3", C["violet"])):
        g = df[df.phase == ph].sort_values("capacity_kg")
        ax.plot(g.capacity_kg, 100 * g.movable_mass_share, "-o", color=col, ms=3.5, lw=1.8, label=f"Phase {ph[-1]} manifest")
    ax.set_xscale("log")
    for x, lab in ((800, "LTV, full\\nperformance"), (1600, "LTV, reduced\\nperformance"), (3000, "two LTVs\\nteam lift"), (4500, "three LTVs"), (10000, "10 t hauler"), (13000, "hauler +\\ntwo LTVs"), (15000, "largest\\nelement")):
        ax.axvline(x, color=MUTED, lw=0.7, ls=":")
        ax.text(x * 1.03, 3, lab, fontsize=7, color=INK2, rotation=90, va="bottom", ha="left")
    ax.set_xlabel("largest mass one vehicle or team can carry (kg)")
    ax.set_ylabel("landed cargo mass that is movable (%)")
    ax.set_ylim(0, 102)
    ax.legend(loc="upper left", fontsize=8)
    ax.set_title("Capacity ladder: how much of NASA's manifest a fleet can move", fontsize=10)
    save(fig, "fig15_capacity_ladder")
    piv = df.pivot(index="capacity_kg", columns="phase", values="movable_mass_share").round(3)
    piv.to_csv(os.path.join(RES, "table_E12.csv"))


# ---------------------------------------------------------------------------
# Fig 16: fragmentation law (E13)
# ---------------------------------------------------------------------------
def fig_law():
    df = pd.read_csv(os.path.join(RES, "E13_fragmentation_law.csv"))
    g = df.groupby(["N", "k", "other_duty", "mechanism"]).agg(p90=("delay_prio1_p90_h", "mean"), p90ci=("delay_prio1_p90_h", ci95),
                                                             sl=("sl24_prio1", "mean"), eff=("eff_per_owner", "first")).reset_index()
    inh = g[g.mechanism == "inhouse"]
    mkt = g[g.mechanism == "marketplace"]
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.4))
    fig.subplots_adjust(wspace=0.3)
    ncol = {4: C["aqua"], 6: C["blue"], 8: C["violet"]}
    dmark = {0.0: "o", 0.3: "s", 0.6: "^"}
    ax = axes[0]
    for _, r in inh.iterrows():
        ax.errorbar(r.eff, r.p90, yerr=r.p90ci, fmt=dmark[r.other_duty], color=ncol[r.N], ms=5, lw=0.8, capsize=2, alpha=0.9)
    # fit p90 = a + b / eff on in-house points
    x = inh.eff.values
    y = inh.p90.values
    A = np.vstack([np.ones_like(x), 1.0 / x]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    xs = np.linspace(x.min() * 0.9, x.max() * 1.1, 200)
    yhat = A @ coef
    r2 = 1 - np.sum((y - yhat) ** 2) / np.sum((y - y.mean()) ** 2)
    ax.plot(xs, coef[0] + coef[1] / xs, "-", color=INK, lw=1.5, label=f"fit: {coef[0]:.1f} + {coef[1]:.1f} / e   (R$^2$ = {r2:.2f})")
    for N, col in ncol.items():
        ax.plot([], [], "s", color=col, label=f"fleet of {N} LTVs")
    for d, mk in dmark.items():
        ax.plot([], [], mk, color=MUTED, label=f"{int(d*100)}% other duties")
    ax.set_xscale("log")
    ax.set_xlabel("effective vehicles per owner, e = N (1 - duty) / owners")
    ax.set_ylabel("in-house urgent 90th-pct delay (h)")
    ax.set_title("A. In-house service collapses onto one curve", fontsize=10)
    ax.legend(fontsize=7, ncol=1, loc="upper right")
    ax = axes[1]
    for N, col in ncol.items():
        sub = inh[inh.N == N]
        for d, mk in dmark.items():
            s2 = sub[sub.other_duty == d].sort_values("k")
            m2 = mkt[(mkt.N == N) & (mkt.other_duty == d)]
            if len(s2) and len(m2):
                gain = s2.p90.values - m2.p90.values[0]
                ax.plot(s2.k, gain, "-" + mk, color=col, ms=4, lw=1.2, alpha=0.9)
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.set_xlabel("number of owners the fleet is split among")
    ax.set_ylabel("pooling gain in urgent 90th-pct delay (h)")
    ax.set_title("B. Pooling gain grows with fragmentation", fontsize=10)
    save(fig, "fig16_fragmentation_law")
    g.to_csv(os.path.join(RES, "table_E13.csv"), index=False)
    json.dump({"a": float(coef[0]), "b": float(coef[1]), "r2": float(r2), "n_points": int(len(x))},
              open(os.path.join(RES, "E13_fit.json"), "w"), indent=1)


# ---------------------------------------------------------------------------
# Fig 17: anticipatory staging (E11)
# ---------------------------------------------------------------------------
def fig_anticipation():
    df = pd.read_csv(os.path.join(RES, "E11_anticipation.csv"))
    cells = df.groupby(["phase", "n_vehicles"]).size().reset_index()[["phase", "n_vehicles"]]
    cells = cells.sort_values(["phase", "n_vehicles"])
    labels = [f"{ph}, {n} veh." for ph, n in zip(cells.phase, cells.n_vehicles)]
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.0))
    fig.subplots_adjust(wspace=0.32)
    rows = []
    for ax, (m, title) in zip(axes, [("delay_prio1_p90_h", "A. Urgent 90th-pct delay (h)"), ("delay_prio1_mean_h", "B. Urgent mean delay (h)"), ("km_reposition", "C. Empty km driven to stage (per yr)")]):
        for i, (ph, n) in enumerate(zip(cells.phase, cells.n_vehicles)):
            a = df[(df.phase == ph) & (df.n_vehicles == n) & (df.mechanism == "marketplace")].sort_values("seed")
            b = df[(df.phase == ph) & (df.n_vehicles == n) & (df.mechanism == "marketplace_no_anticipate")].sort_values("seed")
            for j, (sub, col, lab) in enumerate(((b, C["yellow"], "without anticipation"), (a, C["blue"], "with anticipation"))):
                ax.bar(i + (j - 0.5) * 0.38, sub[m].mean(), 0.36, yerr=ci95(sub[m]), color=col, label=lab if i == 0 else None,
                       error_kw=dict(lw=0.8, capsize=2, ecolor=INK2), edgecolor="white")
            if m == "delay_prio1_p90_h":
                d = a.delay_prio1_p90_h.values - b.delay_prio1_p90_h.values
                dm = a.delay_prio1_mean_h.values - b.delay_prio1_mean_h.values
                rows.append({"phase": ph, "n_vehicles": n, "p90_with": a[m].mean(), "p90_without": b[m].mean(), "d_p90": d.mean(), "d_p90_ci": ci95(d),
                             "d_mean": dm.mean(), "d_mean_ci": ci95(dm), "repositions": a.repositions.mean(), "km_reposition": a.km_reposition.mean(),
                             "sl24_with": a.sl24_prio1.mean(), "sl24_without": b.sl24_prio1.mean()})
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, fontsize=8)
        ax.set_title(title, fontsize=10)
    axes[0].legend(fontsize=8)
    fig.suptitle("Anticipatory staging at the pad before a published landing (30 seeds, 95% CIs)", fontsize=10, y=1.03)
    save(fig, "fig17_anticipation")
    pd.DataFrame(rows).to_csv(os.path.join(RES, "table_E11.csv"), index=False)


# ---------------------------------------------------------------------------
# Fig 18: precision / sequential replication (E14)
# ---------------------------------------------------------------------------
def fig_precision():
    d = json.load(open(os.path.join(RES, "E14_precision.json")))
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.2))
    fig.subplots_adjust(wspace=0.3)
    for ax, (m, title) in zip(axes, [("delay_prio1_mean_h", "A. Mean urgent delay"), ("delay_prio1_p90_h", "B. Urgent 90th-percentile delay")]):
        for mech in MECH_ORDER[:4]:
            h = d[mech][m]["history"]
            ax.plot([r["n"] for r in h], [100 * r["rel"] for r in h], "-o", ms=3, lw=1.6, color=MECH_COLOR[mech], label=MECH_LABEL[mech])
        tgt = 100 * d["marketplace"][m]["target"]
        ax.axhline(tgt, color=MUTED, ls="--", lw=0.9)
        ax.text(ax.get_xlim()[1] * 0.98 if False else 35, tgt * 1.08, f"target {tgt:.0f}%", fontsize=8, color=INK2)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("replications")
        ax.set_ylabel("99% CI half-width (% of mean)")
        ax.set_title(title, fontsize=10)
    axes[0].legend(fontsize=8)
    fig.suptitle("Sequential replication: precision of the Phase-2 estimates as seeds are added", fontsize=10, y=1.03)
    save(fig, "fig18_precision")
    rows = []
    for mech, dd in d.items():
        for m, r in dd.items():
            rows.append({"mechanism": mech, "metric": m, "n": r["n"], "mean": r["mean"], "half_width_99": r["half_width"], "rel_half_width": r["rel_half_width"], "target": r["target"], "reached": r["reached"]})
    pd.DataFrame(rows).to_csv(os.path.join(RES, "table_E14.csv"), index=False)


# ---------------------------------------------------------------------------
# Fig 19: reference design of the marketplace service (diagram)
# ---------------------------------------------------------------------------
def fig_design():
    fig, ax = plt.subplots(figsize=(9.6, 5.2))
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    def box(x, y, w, h, title, lines, col, fs=7.8):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.006,rounding_size=0.015", fc="white", ec=col, lw=1.5))
        ax.text(x + w / 2, y + h - 0.022, title, ha="center", va="top", fontsize=9, color=col, fontweight="bold")
        for i, ln in enumerate(lines):
            ax.text(x + 0.012, y + h - 0.075 - 0.058 * i, ln, fontsize=fs, color=INK2, va="top")

    def band(y, h, label, col):
        ax.add_patch(FancyBboxPatch((0.005, y), 0.99, h, boxstyle="round,pad=0.004,rounding_size=0.01", fc=col, ec="none", alpha=0.12))
        ax.text(0.012, y + h - 0.012, label, fontsize=8.5, color=INK2, va="top", fontweight="bold")

    band(0.80, 0.19, "Customers (shippers)", C["orange"])
    box(0.03, 0.815, 0.22, 0.14, "NASA (anchor)", ["Moon Base manifests", "Service-level contracts"], C["orange"])
    box(0.27, 0.815, 0.22, 0.14, "Payload companies", ["Hosted payloads, demos", "Spot and contract orders"], C["orange"])
    box(0.51, 0.815, 0.22, 0.14, "International partners", ["ESA, JAXA, CSA elements", "Export-control screening"], C["orange"])
    box(0.75, 0.815, 0.22, 0.14, "Base operations", ["Regolith lots, trash,", "sample return, relocations"], C["orange"])

    band(0.33, 0.44, "Marketplace platform (neutral operator)", C["blue"])
    box(0.03, 0.555, 0.22, 0.19, "Order intake", ["Item: mass, interface standard,", "destination, priority, deadline", "Planetary-protection record", "Hazard class, handling needs"], C["blue"])
    box(0.27, 0.555, 0.22, 0.19, "Registries", ["Published landing schedule", "Vehicle capabilities, availability", "Interface standards (FLEX, others)", "Safety zones (Artemis Accords)"], C["blue"])
    box(0.51, 0.555, 0.22, 0.19, "Dispatch engine", ["Generalised-cost sequential auction", "Bundling, consolidation, team lift", "Night-aware acceptance", "Anticipatory staging"], C["blue"])
    box(0.75, 0.555, 0.22, 0.19, "Operator scheduler", ["Console capacity by autonomy level", "Fan-out limits, shift plans", "Latency-aware job timing"], C["blue"])
    box(0.03, 0.345, 0.30, 0.19, "Settlement and gain sharing", ["Job price = variable cost + margin", "Capacity commitments (contract layer)", "Shapley or proportional gain split", "Owner statements, audit trail"], C["blue"])
    box(0.35, 0.345, 0.30, 0.19, "Operations data", ["Telemetry, item tracking (where is it)", "Delivery confirmation, exceptions", "Replay and simulation twin", "Public performance statistics"], C["blue"])
    box(0.67, 0.345, 0.30, 0.19, "Governance", ["Neutrality rules, appeal path", "Priority classes agreed with NASA", "Safety case: NPR 8715, 7150.2", "Data rights, ITAR/EAR segregation"], C["blue"])

    band(0.03, 0.27, "Vehicle operators and surface assets", C["violet"])
    box(0.03, 0.05, 0.22, 0.17, "LTV providers", ["Astrolab, Lunar Outpost", "Crew first, cargo between missions"], C["violet"])
    box(0.27, 0.05, 0.22, 0.17, "Heavy hauler", ["10 t class, night-capable", "Shared asset, team-lift partner"], C["violet"])
    box(0.51, 0.05, 0.22, 0.17, "Small rovers, robots", ["HL-MAPP class, offloading arms", "Pad-side handling"], C["violet"])
    box(0.75, 0.05, 0.22, 0.17, "Fixed assets", ["Pads, depot, charging, standards", "Landers with cranes and ramps"], C["violet"])
    for x in (0.14, 0.38, 0.62, 0.86):
        ax.add_patch(FancyArrowPatch((x, 0.815), (x, 0.75), arrowstyle="<|-|>", mutation_scale=9, color=MUTED, lw=1))
        ax.add_patch(FancyArrowPatch((x, 0.345), (x, 0.225), arrowstyle="<|-|>", mutation_scale=9, color=MUTED, lw=1))
    ax.text(0.5, 0.775, "orders, quotes, tracking, invoices", fontsize=7.5, color=INK2, ha="center", va="center", bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))
    ax.text(0.5, 0.285, "job offers and bids, telemetry, payments", fontsize=7.5, color=INK2, ha="center", va="center", bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))
    save(fig, "fig19_reference_design")


# ---------------------------------------------------------------------------
# V&V table (runs the Python checks)
# ---------------------------------------------------------------------------
def vv_table():
    from lunarsim import vv
    rows = vv.run_all_checks()
    pd.DataFrame(rows).to_csv(os.path.join(RES, "table_vv.csv"), index=False)
    print("V&V:", sum(r["passed"] for r in rows), "of", len(rows), "passed")

'''
rep('''if __name__ == "__main__":
    which = sys.argv[1:] or ["all"]''', new_funcs + '''if __name__ == "__main__":
    which = sys.argv[1:] or ["all"]''')
rep('''             "env": fig_environment, "ablations": fig_ablations, "tuned": fig_tuned, "econ": fig_economics, "timeline": fig_timeline}''',
    '''             "env": fig_environment, "ablations": fig_ablations, "tuned": fig_tuned, "econ": fig_economics, "timeline": fig_timeline,
             "ladder": fig_ladder, "law": fig_law, "anticipation": fig_anticipation, "precision": fig_precision, "design": fig_design, "vv": vv_table}''')
rep('''            except FileNotFoundError as e:
                print("skip", k, e)''', '''            except (FileNotFoundError, KeyError) as e:
                print("skip", k, repr(e))''')
open(p, "w", encoding="utf-8").write(s)
import ast
ast.parse(s)
print("figures patched")
