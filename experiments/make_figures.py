"""Build all figures and summary tables for the paper from results/*.csv."""
import os, sys, json, warnings
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
FIG = os.path.join(ROOT, "figures")
os.makedirs(FIG, exist_ok=True)

# Palette (categorical, fixed order; validated set from the dataviz reference palette)
C = {"blue": "#2a78d6", "orange": "#eb6834", "aqua": "#1baf7a", "yellow": "#eda100",
     "magenta": "#e87ba4", "green": "#008300", "violet": "#4a3aa7", "red": "#e34948"}
MECH_COLOR = {"inhouse": C["orange"], "pooled_greedy": C["yellow"], "central_assign": C["violet"],
              "marketplace": C["blue"], "unconstrained_bound": "#898781", "marketplace_no_team": C["magenta"]}
MECH_LABEL = {"inhouse": "In-house fleets", "pooled_greedy": "Pooled greedy", "central_assign": "Batched assignment",
              "marketplace": "Marketplace (ours)", "unconstrained_bound": "Unconstrained fleet (bound)",
              "marketplace_no_team": "Marketplace, no team lift"}
MECH_ORDER = ["inhouse", "pooled_greedy", "central_assign", "marketplace", "unconstrained_bound"]
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#898781", "#e1e0d9"

plt.rcParams.update({
    "font.family": "Times New Roman", "mathtext.fontset": "stix", "font.size": 10, "axes.titlesize": 10.5, "axes.labelsize": 10,
    "axes.edgecolor": "#c3c2b7", "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.6, "axes.axisbelow": True, "legend.frameon": False, "legend.fontsize": 8,
    "figure.dpi": 150, "savefig.dpi": 220, "savefig.bbox": "tight", "savefig.facecolor": "white",
})


def ci95(x):
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    if len(x) < 2:
        return 0.0
    return 1.96 * x.std(ddof=1) / np.sqrt(len(x))


def agg(df, by, metric):
    g = df.groupby(by)[metric].agg(["mean", ci95, "count"]).reset_index()
    g.columns = list(by) + ["mean", "ci", "n"]
    return g


def save(fig, name):
    fig.savefig(os.path.join(FIG, name + ".png"))
    fig.savefig(os.path.join(FIG, name + ".pdf"))
    plt.close(fig)
    print("saved", name)


# ---------------------------------------------------------------------------
# Fig 1: site map
# ---------------------------------------------------------------------------
def fig_sitemap():
    from lunarsim import build_default_world
    w = build_default_world()
    fig, ax = plt.subplots(figsize=(5.2, 3.9))
    ax.grid(False)
    slope_style = {"flat": ("-", 1.6, "#9ec5f4"), "moderate": ("-", 2.2, "#eda100"), "steep": ("-", 2.8, "#e34948")}
    for (a, b), d in [(k, e) for k, e in w.edges.items() if k[0] < k[1]]:
        sa, sb = w.sites[a], w.sites[b]
        ls, lw, col = slope_style[d["slope"]]
        ax.plot([sa.x_km, sb.x_km], [sa.y_km, sb.y_km], ls, lw=lw, color=col, zorder=1, solid_capstyle="round")
        mx, my = (sa.x_km + sb.x_km) / 2, (sa.y_km + sb.y_km) / 2
        ax.text(mx, my, f"{d['dist']:.1f} km", fontsize=6.5, color=MUTED, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.9))
    kind_marker = {"pad": ("s", C["orange"]), "base": ("o", C["blue"]), "depot": ("D", C["blue"]),
                   "power": ("^", C["green"]), "construction": ("P", C["violet"]), "isru": ("h", C["aqua"]),
                   "science": ("*", C["magenta"]), "psr": ("X", INK)}
    for n, s in w.sites.items():
        m, col = kind_marker[s.kind]
        ax.scatter(s.x_km, s.y_km, marker=m, s=90, color=col, edgecolor="white", linewidth=0.8, zorder=3)
        ax.annotate(n.replace("_", " "), (s.x_km, s.y_km), textcoords="offset points", xytext=(6, 6), fontsize=7.5, color=INK)
    circ = plt.Circle((0, 0), 1.0, fill=False, ls="--", lw=0.8, color=C["orange"])
    ax.add_patch(circ)
    ax.text(0.05, -1.15, "1 km plume-ejecta standoff", fontsize=6.5, color=C["orange"])
    ax.set_xlabel("km (east)")
    ax.set_ylabel("km (north)")
    ax.set_aspect("equal")
    ax.set_xlim(-1.4, 5.4)
    ax.set_ylim(-1.5, 3.6)
    from matplotlib.lines import Line2D
    handles = [Line2D([0], [0], color=slope_style[k][2], lw=slope_style[k][1], label=f"{k} slope") for k in slope_style]
    ax.legend(handles=handles, loc="upper left", fontsize=7)
    ax.set_title("Nine-site south-pole base layout used in all scenarios")
    save(fig, "fig01_sitemap")


# ---------------------------------------------------------------------------
# Fig 2: architecture diagram
# ---------------------------------------------------------------------------
def fig_architecture():
    fig, ax = plt.subplots(figsize=(8.8, 4.3))
    ax.axis("off")

    def box(x, y, w, h, title, lines, col):
        pch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.008,rounding_size=0.02", fc="white", ec=col, lw=1.6)
        ax.add_patch(pch)
        ax.text(x + w / 2, y + h - 0.03, title, ha="center", va="top", fontsize=10, color=col, fontweight="bold")
        for i, ln in enumerate(lines):
            ax.text(x + 0.02, y + h - 0.13 - 0.082 * i, ln, fontsize=8, color=INK2, va="top")

    box(0.01, 0.55, 0.25, 0.43, "Demand", ["Poisson lander arrivals by class", "Manifest sampler, 5 classes",
                                            "Bulk lots (regolith, feedstock)", "Return items (trash, samples)"], C["orange"])
    box(0.01, 0.03, 0.25, 0.46, "Environment", ["9-site graph, slope classes", "Lunar night (dark share f)",
                                                 "Earth-Moon latency, fan-out", "Faults (MTBF, MTTR), duties"], C["green"])
    box(0.375, 0.14, 0.25, 0.72, "Event engine", ["LANDING, READY, FREE,", "TICK, WAKE, REPOS, DUTY", "Prices each job: approach,",
                                                   "loading, slope, night,", "latency, faults", "Logs delays, km, energy,", "cost, revenue"], INK)
    box(0.74, 0.55, 0.25, 0.43, "Dispatch mechanism", ["In-house (bilateral contracts)", "Pooled greedy",
                                                        "Batched assignment", "Marketplace (ours)"], C["blue"])
    box(0.74, 0.03, 0.25, 0.46, "Fleet", ["LTV 1.5 t, HAUL 10 t,", "MICRO 0.3 t; owner, standards,", "autonomy, battery, night", "capability; revenue per owner"], C["violet"])
    gl, gr = 0.3175, 0.6825
    arrows = [((0.26, 0.70), (0.375, 0.62), MUTED, "landings,\nlots", (gl, 0.75)),
              ((0.26, 0.30), (0.375, 0.38), MUTED, "night, delay,\nfaults", (gl, 0.25)),
              ((0.625, 0.62), (0.74, 0.70), MUTED, "waiting cargo,\nfree vehicles", (gr, 0.77)),
              ((0.74, 0.60), (0.625, 0.52), C["blue"], "jobs", (gr, 0.49)),
              ((0.625, 0.36), (0.74, 0.28), MUTED, "state,\ncosts", (gr, 0.23))]
    for (p0, p1, col, lab, (lx, ly)) in arrows:
        ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=11, color=col, lw=1.2))
        ax.text(lx, ly, lab, fontsize=7.5, color=col if col != MUTED else INK2, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none"))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    save(fig, "fig02_architecture")


# ---------------------------------------------------------------------------
# Fig 3: demand - landed mass by year and simulated cargo mass distribution
# ---------------------------------------------------------------------------
def fig_demand():
    years = [2026, 2027, 2028, 2029, 2030, 2031, 2032]
    low = [0.0, 0.2, 1.0, 1.5, 3, 3, 5]
    base = [0.5, 0.8, 4.5, 6, 20, 12, 25]
    high = [0.7, 3.5, 12, 15, 35, 30, 45]
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 2.9))
    fig.subplots_adjust(wspace=0.3)
    ax = axes[0]
    ax.fill_between(years, low, high, color="#cde2fb", label="low to high")
    ax.plot(years, base, "-o", color=C["blue"], ms=4, lw=2, label="base case")
    ax.set_ylabel("landed payload at south pole (t / yr)")
    ax.set_title("A. Landed mass from the mission manifest", fontsize=8.5)
    ax.legend(loc="upper left")
    ax.set_xticks(years)
    # simulated manifests
    from lunarsim import Simulation, dispatch
    from experiments.scenarios import PHASES
    ax = axes[1]
    bins = np.logspace(1, 4.2, 20)
    for ph, col in (("P1", C["aqua"]), ("P2", C["yellow"]), ("P3", C["violet"])):
        masses = []
        for s in range(10):
            sim = Simulation(PHASES[ph], dispatch.pooled_greedy, seed=s)
            # pull manifests by executing landings only
            import heapq
            from lunarsim.scenario import sample_cargo_manifest
            for t, lt, pad in sim.landing_schedule:
                items, _ = sample_cargo_manifest(sim.rng, lt, sim.sc.cargo_owners, sim.world.pads, t, 1.0, 0, pad=pad)
                masses += [c.mass_kg for c in items]
        ax.hist(masses, bins=bins, histtype="step", lw=1.8, color=col, label=f"{ph} ({len(masses)//10} items/yr)")
    ymax = ax.get_ylim()[1]
    for x, lab, yf in ((800, "LTV 0.8 t", 0.62), (1600, "LTV 1.6 t", 0.78), (10000, "HAUL 10 t", 0.62)):
        ax.axvline(x, color=MUTED, lw=0.8, ls="--")
        ax.text(x * 1.06, ymax * yf, lab, fontsize=7.5, color=INK2, va="center", ha="left",
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.9))
    ax.set_xscale("log")
    ax.set_xlabel("item mass (kg)")
    ax.set_ylabel("items (10 seeds pooled)")
    ax.set_title("B. Simulated item masses by phase", fontsize=8.5)
    ax.legend(loc="upper right", fontsize=8)
    save(fig, "fig03_demand")


# ---------------------------------------------------------------------------
# Fig 4: main results E1
# ---------------------------------------------------------------------------
def fig_main():
    df = pd.read_csv(os.path.join(RES, "E1_phases.csv"))
    df["stranded_share"] = df.stranded_kg / df.landed_kg
    metrics = [("delay_prio1_p90_h", "A. Urgent cargo:\n90th-percentile delay (h)"), ("sl24_prio1", "B. Urgent cargo\ndelivered within 24 h"),
               ("stranded_share", "C. Landed cargo mass that\nis immovable (%)"), ("night_strandings", "D. Vehicles caught by\nnight (per year)")]
    fig, axes = plt.subplots(1, 4, figsize=(11, 3.1))
    fig.subplots_adjust(wspace=0.32)
    phases = ["P1", "P2", "P3"]
    width = 0.16
    for ax, (m, title) in zip(axes, metrics):
        g = agg(df, ["phase", "mechanism"], m)
        for i, mech in enumerate(MECH_ORDER):
            sub = g[g.mechanism == mech].set_index("phase").reindex(phases)
            x = np.arange(len(phases)) + (i - 2) * width
            sc_ = 100 if m == "stranded_share" else 1
            ax.bar(x, sc_ * sub["mean"], width * 0.92, yerr=sc_ * sub["ci"], color=MECH_COLOR[mech], label=MECH_LABEL[mech],
                   error_kw=dict(lw=0.8, capsize=2, ecolor=INK2), edgecolor="white", linewidth=0.5)
        ax.set_xticks(np.arange(len(phases)))
        ax.set_xticklabels(["Phase 1\n3 t/yr", "Phase 2\n32 t/yr", "Phase 3\n74 t/yr"], fontsize=7.5)
        ax.set_title(title, fontsize=8.5)
        if m == "sl24_prio1":
            ax.set_ylim(0.6, 1.02)
    axes[0].legend(loc="upper right", fontsize=6.5)
    fig.suptitle("Main comparison across phases (mean and 95% CI over 30 seeds; default fleets)", fontsize=9, y=1.04)
    save(fig, "fig04_main")
    # table
    cols = ["delivered_share", "stranded_share", "delay_prio1_mean_h", "delay_prio1_p90_h", "sl24_prio1",
            "delay_mean_bulk", "jobs", "utilisation", "empty_km_share", "operator_hours", "night_strandings", "cost_per_kg_usd"]
    rows = []
    for ph in phases:
        for mech in MECH_ORDER:
            sub = df[(df.phase == ph) & (df.mechanism == mech)]
            r = {"phase": ph, "mechanism": MECH_LABEL[mech]}
            for c in cols:
                r[c] = f"{sub[c].mean():.3g} ± {ci95(sub[c]):.2g}"
            rows.append(r)
    pd.DataFrame(rows).to_csv(os.path.join(RES, "table_main.csv"), index=False)
    # paired differences vs pooled greedy
    out = []
    for ph in phases:
        for m in ("delay_prio1_p90_h", "delay_prio1_mean_h", "jobs", "operator_hours", "stranded_share", "night_strandings"):
            a = df[(df.phase == ph) & (df.mechanism == "marketplace")].sort_values("seed")[m].values
            b = df[(df.phase == ph) & (df.mechanism == "pooled_greedy")].sort_values("seed")[m].values
            d = a - b
            out.append({"phase": ph, "metric": m, "mkt_minus_greedy": d.mean(), "ci95": ci95(d),
                        "rel_%": 100 * d.mean() / max(abs(b.mean()), 1e-9)})
    pd.DataFrame(out).to_csv(os.path.join(RES, "table_paired_E1.csv"), index=False)


# ---------------------------------------------------------------------------
# Fig 5: fleet-size sweep E2
# ---------------------------------------------------------------------------
def fig_fleet():
    df = pd.read_csv(os.path.join(RES, "E2_fleet_size.csv"))
    fig, axes = plt.subplots(1, 3, figsize=(10, 2.9))
    for ax, (m, title) in zip(axes, [("delay_prio1_p90_h", "Urgent cargo: 90th-pct delay (h)"),
                                     ("sl24_prio1", "Urgent cargo delivered within 24 h"),
                                     ("cost_per_kg_usd", "Surface logistics cost per kg delivered ($)")]):
        g = agg(df, ["n_vehicles", "mechanism"], m)
        for mech in MECH_ORDER[:4]:
            sub = g[g.mechanism == mech].sort_values("n_vehicles")
            ax.plot(sub.n_vehicles, sub["mean"], "-o", color=MECH_COLOR[mech], ms=4, lw=1.8, label=MECH_LABEL[mech])
            ax.fill_between(sub.n_vehicles, sub["mean"] - sub.ci, sub["mean"] + sub.ci, color=MECH_COLOR[mech], alpha=0.15, lw=0)
        ax.set_xlabel("vehicles in fleet")
        ax.set_title(title, fontsize=8.5)
        ax.set_xticks(sorted(df.n_vehicles.unique()))
        if m == "sl24_prio1":
            ax.axhline(0.9, color=MUTED, ls="--", lw=0.8)
            ax.text(2.1, 0.905, "90% target", fontsize=6.5, color=MUTED)
        if m == "cost_per_kg_usd":
            ax.set_yscale("log")
    axes[0].legend(fontsize=7)
    fig.suptitle("Phase-2 demand with fleets of 2 to 8 vehicles (30 seeds, 95% CI bands)", fontsize=9, y=1.02)
    save(fig, "fig05_fleet_size")
    g = df.groupby(["n_vehicles", "mechanism"])[["delay_prio1_p90_h", "sl24_prio1", "cost_per_kg_usd", "stranded_share", "backlog_kg"]].mean().round(3)
    g.to_csv(os.path.join(RES, "table_E2.csv"))


# ---------------------------------------------------------------------------
# Fig 6: market thickness E3
# ---------------------------------------------------------------------------
def fig_thickness():
    df = pd.read_csv(os.path.join(RES, "E3_thickness.csv"))
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9))
    duties = sorted(df.other_duty.unique())
    cols = [C["aqua"], C["blue"], C["violet"]]
    for ax, (m, title) in zip(axes, [("delay_prio1_p90_h", "Urgent cargo: 90th-pct delay (h)"),
                                     ("sl24_prio1", "Urgent cargo delivered within 24 h")]):
        for d, col in zip(duties, cols):
            for mech, ls in (("inhouse", "--"), ("marketplace", "-")):
                g = agg(df[(df.other_duty == d) & (df.mechanism == mech)], ["n_companies"], m).sort_values("n_companies")
                ax.plot(g.n_companies, g["mean"], ls, marker="o" if mech == "marketplace" else "s", ms=4, lw=1.6, color=col,
                        label=f"{MECH_LABEL[mech]}, {int(d*100)}% other duties")
                ax.fill_between(g.n_companies, g["mean"] - g.ci, g["mean"] + g.ci, color=col, alpha=0.12, lw=0)
        ax.set_xlabel("companies sharing the same 6-vehicle fleet")
        ax.set_title(title, fontsize=8.5)
        ax.set_xticks(sorted(df.n_companies.unique()))
    axes[1].legend(fontsize=6, loc="lower left", ncol=1)
    fig.suptitle("Market thickness: pooling gain grows with fragmentation and with vehicles' other duties", fontsize=9, y=1.02)
    save(fig, "fig06_thickness")
    # pooling gain table
    rows = []
    for d in duties:
        for n in sorted(df.n_companies.unique()):
            a = df[(df.other_duty == d) & (df.n_companies == n) & (df.mechanism == "inhouse")].sort_values("seed")
            b = df[(df.other_duty == d) & (df.n_companies == n) & (df.mechanism == "marketplace")].sort_values("seed")
            for m in ("delay_prio1_p90_h", "delay_prio1_mean_h", "sl24_prio1", "backlog_kg"):
                diff = a[m].values - b[m].values
                rows.append({"other_duty": d, "n_companies": n, "metric": m, "inhouse": a[m].mean(), "marketplace": b[m].mean(),
                             "gain": diff.mean(), "ci95": ci95(diff)})
    pd.DataFrame(rows).to_csv(os.path.join(RES, "table_E3.csv"), index=False)


# ---------------------------------------------------------------------------
# Fig 7: heavy cargo E4
# ---------------------------------------------------------------------------
def fig_heavy():
    df = pd.read_csv(os.path.join(RES, "E4_heavy_cargo.csv"))
    df["strand_landed"] = df.stranded_kg / df.landed_kg
    fleets = ["LTVs only", "LTVs + 1 hauler", "LTVs + 2 haulers"]
    mechs = ["pooled_greedy", "marketplace_no_team", "marketplace"]
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.0), sharey=False)
    fig.subplots_adjust(wspace=0.3)
    for ax, ph in zip(axes, ["P2", "P3"]):
        g = agg(df[df.phase == ph], ["fleet", "mechanism"], "strand_landed")
        w = 0.25
        for i, mech in enumerate(mechs):
            sub = g[g.mechanism == mech].set_index("fleet").reindex(fleets)
            x = np.arange(len(fleets)) + (i - 1) * w
            ax.bar(x, 100 * sub["mean"], w * 0.92, yerr=100 * sub.ci, color=MECH_COLOR[mech], label=MECH_LABEL[mech],
                   error_kw=dict(lw=0.8, capsize=2, ecolor=INK2), edgecolor="white")
        ax.set_xticks(np.arange(len(fleets)))
        ax.set_xticklabels(["4 LTVs\nonly", "3 LTVs +\n1 hauler", "2 LTVs +\n2 haulers"], fontsize=7.5)
        ax.set_ylabel("landed cargo mass that is immovable (%)")
        ax.set_title(f"Phase {ph[-1]} demand", fontsize=8.5)
    axes[0].legend(fontsize=7)
    fig.suptitle("The heavy-cargo gap: stranded share by fleet composition and team-lift capability", fontsize=9, y=1.02)
    save(fig, "fig07_heavy_cargo")
    df.groupby(["phase", "fleet", "mechanism"])[["stranded_share", "stranded_kg", "delay_mean_element", "delay_mean_infrastructure", "team_lifts", "delay_prio1_p90_h"]].mean().round(3).to_csv(os.path.join(RES, "table_E4.csv"))


# ---------------------------------------------------------------------------
# Fig 8: autonomy and latency E5
# ---------------------------------------------------------------------------
def fig_latency():
    df = pd.read_csv(os.path.join(RES, "E5_autonomy_latency.csv"))
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.1))
    fig.subplots_adjust(wspace=0.3)
    acol = {"teleop": C["red"], "supervised": C["yellow"], "autonomous": C["aqua"]}
    alab = {"teleop": "Teleoperated from Earth", "supervised": "Supervised autonomy", "autonomous": "Full autonomy"}
    # panel A: p90 delay vs RTT at 2 operators
    ax = axes[0]
    for a in ("teleop", "supervised", "autonomous"):
        g = agg(df[(df.autonomy == a) & (df.n_operators == 2)], ["rtt_s"], "delay_prio1_p90_h").sort_values("rtt_s")
        ax.plot(g.rtt_s, g["mean"], "-o", color=acol[a], ms=4, lw=1.8, label=alab[a])
        ax.fill_between(g.rtt_s, g["mean"] - g.ci, g["mean"] + g.ci, color=acol[a], alpha=0.15, lw=0)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("round-trip control latency (s)")
    ax.set_title("A. Urgent cargo: 90th-pct delay (h), 2 operators", fontsize=8.5)
    y0, y1 = ax.get_ylim()
    for x, lab, ha in ((2.6, "Moon\ndirect", "left"), (16, "Moon\nrelayed", "left"), (602.6, "Mars\nnear", "right"), (1322.6, "Mars\nfar", "left")):
        ax.axvline(x, color=MUTED, lw=0.7, ls=":")
        ax.text(x * (1.1 if ha == "left" else 0.9), y1 * 0.75, lab, fontsize=7, color=INK2, ha=ha, va="top")
    ax.legend(fontsize=7, loc="lower right")
    # panel B: delivered share vs RTT
    ax = axes[1]
    for a in ("teleop", "supervised", "autonomous"):
        g = agg(df[(df.autonomy == a) & (df.n_operators == 2)], ["rtt_s"], "delivered_share").sort_values("rtt_s")
        ax.plot(g.rtt_s, g["mean"], "-o", color=acol[a], ms=4, lw=1.8, label=alab[a])
        ax.fill_between(g.rtt_s, g["mean"] - g.ci, g["mean"] + g.ci, color=acol[a], alpha=0.15, lw=0)
    ax.set_xscale("log")
    ax.set_xlabel("round-trip control latency (s)")
    ax.set_title("B. Share of mass delivered within the year", fontsize=8.5)
    # panel C: operator pool at Moon latency (RTT 5 s)
    ax = axes[2]
    sub = df[np.isclose(df.rtt_s, 5.0)]
    w = 0.25
    for i, a in enumerate(("teleop", "supervised", "autonomous")):
        g = agg(sub[sub.autonomy == a], ["n_operators"], "operator_hours").sort_values("n_operators")
        x = np.arange(len(g)) + (i - 1) * w
        ax.bar(x, g["mean"], w * 0.92, yerr=g.ci, color=acol[a], label=alab[a], error_kw=dict(lw=0.8, capsize=2, ecolor=INK2), edgecolor="white")
    ax.set_xticks(np.arange(3))
    ax.set_xticklabels(["1 operator", "2 operators", "4 operators"])
    ax.set_title("C. Operator console hours per year (RTT 5 s)", fontsize=8.5)
    fig.suptitle("Autonomy level and control latency (Phase-2 demand, 5-vehicle fleet, 20 seeds)", fontsize=9, y=1.02)
    save(fig, "fig08_latency")
    df.groupby(["autonomy", "rtt_s", "n_operators"])[["delay_prio1_p90_h", "delivered_share", "operator_hours", "backlog_kg", "unmet_operator_waits"]].mean().round(3).to_csv(os.path.join(RES, "table_E5.csv"))


# ---------------------------------------------------------------------------
# Fig 9: standards E6
# ---------------------------------------------------------------------------
def fig_standards():
    df = pd.read_csv(os.path.join(RES, "E6_standards.csv"))
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9))
    fig.subplots_adjust(wspace=0.3)
    for ax, (m, title, scale) in zip(axes, [("sl24_prio1", "A. Urgent cargo delivered within 24 h", 1),
                                            ("delay_prio1_p90_h", "B. Urgent cargo: 90th-pct delay (h)", 1)]):
        for mech in ("inhouse", "pooled_greedy", "marketplace"):
            g = agg(df[df.mechanism == mech], ["common_share"], m).sort_values("common_share")
            ax.plot(100 * g.common_share, scale * g["mean"], "-o", color=MECH_COLOR[mech], ms=4, lw=1.8, label=MECH_LABEL[mech])
            ax.fill_between(100 * g.common_share, scale * (g["mean"] - g.ci), scale * (g["mean"] + g.ci), color=MECH_COLOR[mech], alpha=0.15, lw=0)
        ax.set_xlabel("common-standard cargo (%)")
        ax.set_title(title, fontsize=8.5)
    axes[1].legend(fontsize=7)
    fig.suptitle("Interface standards: 3 of 5 vehicles accept only the common standard", fontsize=9, y=1.02)
    save(fig, "fig09_standards")
    df.groupby(["common_share", "mechanism"])[["stranded_share", "delay_prio1_p90_h", "sl24_prio1", "delivered_share"]].mean().round(3).to_csv(os.path.join(RES, "table_E6.csv"))


# ---------------------------------------------------------------------------
# Fig 10: environment E7
# ---------------------------------------------------------------------------
def fig_environment():
    df = pd.read_csv(os.path.join(RES, "E7_environment.csv"))
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.0))
    fig.subplots_adjust(wspace=0.36)
    panels = [("night_fraction", "A. Dark share of the lunar cycle", "delay_prio1_p90_h", "urgent 90th-pct delay (h)"),
              ("mtbf_mult", "B. Reliability (MTBF multiplier)", "delay_prio1_p90_h", "urgent 90th-pct delay (h)"),
              ("bulk_t_per_year", "C. Bulk regolith flows (t / yr)", "utilisation", "fleet utilisation")]
    for ax, (f, title, m, ylab) in zip(axes, panels):
        sub = df[df.factor == f]
        for mech in ("pooled_greedy", "marketplace"):
            g = agg(sub[sub.mechanism == mech], ["level"], m).sort_values("level")
            ax.plot(g.level, g["mean"], "-o", color=MECH_COLOR[mech], ms=4, lw=1.8, label=MECH_LABEL[mech])
            ax.fill_between(g.level, g["mean"] - g.ci, g["mean"] + g.ci, color=MECH_COLOR[mech], alpha=0.15, lw=0)
        if f == "mtbf_mult":
            ax.set_xscale("log", base=2)
            ax.set_xticks([0.25, 0.5, 1, 2])
            ax.set_xticklabels(["0.25x", "0.5x", "1x", "2x"])
        ax.set_title(title, fontsize=8.5)
        ax.set_ylabel(ylab)
    axes[0].legend(fontsize=7)
    fig.suptitle("Environment sweeps (Phase-2 demand, 5-vehicle fleet, 30 seeds)", fontsize=9, y=1.02)
    save(fig, "fig10_environment")
    df.groupby(["factor", "level", "mechanism"])[["delay_prio1_p90_h", "sl24_prio1", "night_strandings", "faults", "utilisation", "jobs", "backlog_kg"]].mean().round(3).to_csv(os.path.join(RES, "table_E7.csv"))


# ---------------------------------------------------------------------------
# Fig 11: ablations E8
# ---------------------------------------------------------------------------
def fig_ablations():
    df = pd.read_csv(os.path.join(RES, "E8_ablations.csv"))
    variants = ["marketplace", "no_bundling", "no_consolidate", "no_team_lift", "no_anticipate", "no_backhaul", "no_night_aware", "no_priority"]
    vlab = {"marketplace": "Full marketplace", "no_bundling": "without bundling", "no_consolidate": "without consolidation",
            "no_team_lift": "without team lift", "no_anticipate": "without anticipation", "no_backhaul": "without backhaul",
            "no_night_aware": "without night awareness", "no_priority": "without priority credit"}
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.0), gridspec_kw={"width_ratios": [1.25, 1, 1.1]})
    fig.subplots_adjust(wspace=0.28)
    ev = df[df.batch_h == 0]
    for ax, (m, title) in zip(axes[:2], [("delay_prio1_p90_h", "A. Urgent cargo: 90th-pct delay (h)"), ("jobs", "B. Vehicle trips per year")]):
        w = 0.38
        for i, ph in enumerate(("P2", "P3")):
            g = agg(ev[ev.phase == ph], ["variant"], m).set_index("variant").reindex(variants)
            x = np.arange(len(variants)) + (i - 0.5) * w
            col = C["blue"] if ph == "P2" else C["violet"]
            ax.barh(x, g["mean"], w * 0.9, xerr=g.ci, color=col, label=f"Phase {ph[-1]}", error_kw=dict(lw=0.8, capsize=2, ecolor=INK2), edgecolor="white")
        ax.set_yticks(np.arange(len(variants)))
        ax.set_yticklabels([vlab[v] for v in variants] if m == "delay_prio1_p90_h" else [""] * len(variants))
        ax.invert_yaxis()
        ax.set_title(title, fontsize=8.5)
    axes[0].legend(fontsize=7, loc="lower right")
    ax = axes[2]
    bt = df[df.variant == "marketplace"]
    for ph, col in (("P2", C["blue"]), ("P3", C["violet"])):
        g = agg(bt[bt.phase == ph], ["batch_h"], "delay_prio1_p90_h").sort_values("batch_h")
        ax.plot(g.batch_h, g["mean"], "-o", color=col, ms=4, lw=1.8, label=f"Phase {ph[-1]}")
        ax.fill_between(g.batch_h, g["mean"] - g.ci, g["mean"] + g.ci, color=col, alpha=0.15, lw=0)
    ax.set_xlabel("batching window (h); 0 = dispatch on every event")
    ax.set_title("C. Batching window vs urgent 90th-pct delay (h)", fontsize=8.5)
    ax.legend(fontsize=7)
    fig.suptitle("Ablations of the marketplace (one component removed at a time; 30 seeds)", fontsize=9, y=1.02)
    save(fig, "fig11_ablations")
    # paired ablation table
    rows = []
    for ph in ("P2", "P3"):
        base = ev[(ev.phase == ph) & (ev.variant == "marketplace")].sort_values("seed")
        for v in variants:
            sub = ev[(ev.phase == ph) & (ev.variant == v)].sort_values("seed")
            r = {"phase": ph, "variant": vlab[v]}
            for m in ("delay_prio1_p90_h", "delay_prio1_mean_h", "sl24_prio1", "jobs", "stranded_share", "night_strandings", "operator_hours", "delay_mean_bulk", "empty_km_share"):
                r[m] = sub[m].mean()
                r[m + "_dci"] = ci95(sub[m].values - base[m].values)
            rows.append(r)
    pd.DataFrame(rows).to_csv(os.path.join(RES, "table_E8.csv"), index=False)


# ---------------------------------------------------------------------------
# Fig 12: tuned weights E9
# ---------------------------------------------------------------------------
def fig_tuned():
    df = pd.read_csv(os.path.join(RES, "E9_test.csv"))
    best = json.load(open(os.path.join(RES, "E9_best.json")))
    fig, axes = plt.subplots(1, 3, figsize=(9.5, 2.8))
    for ax, (m, title) in zip(axes, [("delay_prio1_p90_h", "Urgent cargo: 90th-pct delay (h)"), ("sl24_prio1", "Urgent cargo within 24 h"),
                                     ("operator_hours", "Operator hours per year")]):
        g = agg(df, ["phase", "weights"], m)
        w = 0.35
        for i, lab in enumerate(("hand-set", "tuned")):
            sub = g[g.weights == lab].set_index("phase").reindex(["P1", "P2", "P3"])
            x = np.arange(3) + (i - 0.5) * w
            ax.bar(x, sub["mean"], w * 0.9, yerr=sub.ci, color=[C["yellow"], C["blue"]][i], label=f"{lab} weights",
                   error_kw=dict(lw=0.8, capsize=2, ecolor=INK2), edgecolor="white")
        ax.set_xticks(np.arange(3))
        ax.set_xticklabels(["Phase 1", "Phase 2\n(search set)", "Phase 3"])
        ax.set_title(title, fontsize=8.5)
        if m == "sl24_prio1":
            ax.set_ylim(0.6, 1.02)
    axes[0].legend(fontsize=7)
    p = best["params"]
    fig.suptitle(f"Auction weights searched on Phase 2 (40 random configurations, 8 seeds), tested on all phases with 30 fresh seeds.\n"
                 f"Best configuration: w1 = {p['w_p1']:.1f} h, w2 = {p['w_p2']:.1f} h, age = {p['w_age']:.2f}, fill = {p['fill']:.2f}, max wait = {p['max_wait']:.0f} h",
                 fontsize=8.5, y=1.08)
    save(fig, "fig12_tuned")
    df.groupby(["phase", "weights"])[["delay_prio1_p90_h", "delay_prio1_mean_h", "sl24_prio1", "operator_hours", "jobs", "delay_mean_bulk", "cost_per_kg_usd"]].mean().round(3).to_csv(os.path.join(RES, "table_E9.csv"))


# ---------------------------------------------------------------------------
# Fig 13: economics - tornado and cost context
# ---------------------------------------------------------------------------
def fig_economics():
    df = pd.read_csv(os.path.join(RES, "E10_tornado_sim.csv"))
    base = df[df.factor == "base"]
    base_cost = base.cost_per_kg_usd.mean()
    deliv = base.delivered_kg.mean()
    fleet_cost = base.fleet_cost_musd.mean()
    op_cost = base.operator_cost_musd.mean()
    rows = []
    for f in ("demand", "operator_cost", "other_duty", "night_fraction", "mtbf"):
        lo = df[(df.factor == f) & (df.level == "low")].cost_per_kg_usd.mean()
        hi = df[(df.factor == f) & (df.level == "high")].cost_per_kg_usd.mean()
        rows.append((f, lo, hi))
    # analytic sensitivities on the cost model itself (fleet cost is deterministic)
    for f, lo_m, hi_m in (("vehicle unit cost", 0.5, 1.5), ("vehicle calendar life", 1.5, 1 / 1.5)):
        rows.append((f, 1e6 * (fleet_cost * lo_m + op_cost) / deliv, 1e6 * (fleet_cost * hi_m + op_cost) / deliv))
    labels = {"demand": "Landed demand (x0.5 / x1.5)", "operator_cost": "Operator cost ($200 / $5,000 per h)",
              "other_duty": "Vehicles' other duties (0% / 60%)", "night_fraction": "Dark share of cycle (10% / 30%)",
              "mtbf": "Reliability (MTBF x0.5 / x2)", "vehicle unit cost": "Vehicle unit cost (-50% / +50%)",
              "vehicle calendar life": "Vehicle calendar life (15 yr / 6.7 yr)"}
    rows.sort(key=lambda r: -abs(r[2] - r[1]))
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.2), gridspec_kw={"width_ratios": [1.15, 1]})
    fig.subplots_adjust(wspace=0.25)
    ax = axes[0]
    for i, (f, lo, hi) in enumerate(rows):
        ax.barh(i, lo - base_cost, left=base_cost, color=C["aqua"], height=0.6)
        ax.barh(i, hi - base_cost, left=base_cost, color=C["orange"], height=0.6)
        ax.text(max(lo, hi) + 5, i, "\\$" + f"{min(lo,hi):,.0f} to " + "\\$" + f"{max(lo,hi):,.0f}", va="center", fontsize=6.5, color=INK2)
    ax.axvline(base_cost, color=INK, lw=1)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([labels[r[0]] for r in rows])
    ax.invert_yaxis()
    ax.set_xlabel(f"system cost per kg of all mass moved (USD); base = {base_cost:,.0f}")
    ax.set_title("A. Sensitivity of cost per kg moved (Phase 2, 4-vehicle fleet)", fontsize=8.5)
    ax.set_xlim(0, max(max(r[1], r[2]) for r in rows) * 1.45)
    # panel B: cost context
    ax = axes[1]
    e1 = pd.read_csv(os.path.join(RES, "E1_phases.csv"))
    p3 = e1[(e1.phase == "P3") & (e1.mechanism == "marketplace")]
    p3_all = p3.cost_per_kg_usd.mean()
    p3_landed = 1e6 * (p3.fleet_cost_musd + p3.operator_cost_musd).mean() / (p3.delivered_kg - p3.bulk_kg).mean()
    base_landed = 1e6 * (fleet_cost + op_cost) / (deliv - base.bulk_kg.mean())
    items = [("CLPS lander\n(Blue Ghost M1)", 1.08e6, C["orange"]), ("Blue Moon MK1\n(if full, 3 t)", 7.8e4, C["yellow"]),
             ("Starship\n(published)", 1.0e5, C["violet"]),
             ("Surface move, P2\nper landed kg", base_landed, C["blue"]), ("Surface move, P3\nper landed kg", p3_landed, C["blue"]),
             ("Surface move, P2\nper kg incl. regolith", base_cost, "#86b6ef"), ("Surface move, P3\nper kg incl. regolith", p3_all, "#86b6ef")]
    ax.bar(range(len(items)), [v for _, v, _ in items], color=[c for _, _, c in items], edgecolor="white")
    ax.set_yscale("log")
    ax.set_ylim(1e2, 3e6)
    ax.set_xticks(range(len(items)))
    ax.set_xticklabels([n for n, _, _ in items], fontsize=6, rotation=30, ha="right")
    for i, (_, v, _) in enumerate(items):
        ax.text(i, v * 1.2, "\\$" + f"{v:,.0f}", ha="center", fontsize=6.2, color=INK2)
    ax.set_ylabel("USD per kg")
    ax.set_title("B. Landing a kilogram vs. moving it on the surface", fontsize=8.5)
    pd.DataFrame({"item": [n.replace("\n", " ") for n, _, _ in items], "usd_per_kg": [v for _, v, _ in items]}).to_csv(
        os.path.join(RES, "table_cost_context.csv"), index=False)
    save(fig, "fig13_economics")
    pd.DataFrame(rows, columns=["factor", "low", "high"]).assign(base=base_cost).to_csv(os.path.join(RES, "table_E10.csv"), index=False)


# ---------------------------------------------------------------------------
# Fig 14: one simulated year - timeline of one seed (mechanistic exhibit)
# ---------------------------------------------------------------------------
def fig_timeline():
    from lunarsim import Simulation, dispatch
    from experiments.scenarios import PHASES
    from experiments.run_all import FLEETS
    sc = PHASES["P2"].with_(fleet=FLEETS[4], n_operators=3)
    fig, axes = plt.subplots(2, 1, figsize=(7.5, 4.2), sharex=True)
    for ax, (mech, lab, col) in zip(axes, [(dispatch.pooled_greedy, "Pooled greedy", C["yellow"]), (dispatch.marketplace, "Marketplace", C["blue"])]):
        sim = Simulation(sc, mech, seed=3)
        sim.run()
        days = np.array([c.t_ready for c in sim.all_cargo if c.t_delivered is not None]) / 24
        delays = np.array([c.t_delivered - c.t_ready for c in sim.all_cargo if c.t_delivered is not None])
        prio = np.array([c.priority for c in sim.all_cargo if c.t_delivered is not None])
        cls = np.array([c.cls for c in sim.all_cargo if c.t_delivered is not None])
        # night shading
        from lunarsim.scenario import LUNAR_CYCLE_H
        t = 0.0
        while t < sc.horizon_h:
            ns = (np.floor(t / LUNAR_CYCLE_H) + 1 - sc.night_fraction) * LUNAR_CYCLE_H
            ne = (np.floor(t / LUNAR_CYCLE_H) + 1) * LUNAR_CYCLE_H
            ax.axvspan(ns / 24, ne / 24, color="#eeeeea", lw=0)
            t = ne + 1
        for p, c_, m_, l_ in ((3, "#c3c2b7", ".", "deferrable / bulk"), (2, C["aqua"], "o", "normal"), (1, C["red"], "o", "urgent")):
            sel = prio == p
            ax.scatter(days[sel], delays[sel], s=8 if p == 3 else 14, color=c_, marker=m_, label=l_, alpha=0.8, edgecolor="none")
        # landings
        for t_land in sorted(set(c.t_landed for c in sim.all_cargo if c.cls not in ("bulk", "return"))):
            ax.axvline(t_land / 24, color=C["orange"], lw=0.6, alpha=0.6)
        ax.set_yscale("log")
        ax.set_ylabel("delay (h)")
        ax.set_title(f"{lab}: {sim.metrics.jobs} trips, urgent 90th-pct delay {np.percentile(delays[prio==1],90):.1f} h, "
                     f"{sim.metrics.night_strandings} night strandings, {sim.metrics.team_lifts} team lifts", fontsize=8, color=col)
    axes[1].set_xlabel("day of simulated year (grey = lunar night at the base; orange lines = landings)")
    axes[0].legend(fontsize=6.5, loc="upper right", ncol=3)
    save(fig, "fig14_timeline")




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
    for x, lab, y in ((800, "LTV, full performance", 3), (1600, "LTV, reduced performance", 3), (3000, "two LTVs (team lift)", 3), (4500, "three LTVs", 3), (10000, "10 t hauler", 3), (13000, "hauler + two LTVs", 3), (15000, "largest element", 40)):
        ax.axvline(x, color=MUTED, lw=0.7, ls=":")
        ax.text(x * 1.03, y, lab, fontsize=7.5, color=INK2, rotation=90, va="bottom", ha="left")
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
    labels = [f"{ph}\n{n} vehicles" for ph, n in zip(cells.phase, cells.n_vehicles)]
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
        ax.text(300, tgt * 1.12, f"target {tgt:.0f}%", fontsize=8, color=INK2, ha="center")
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
    fig, ax = plt.subplots(figsize=(10, 6.6))
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    LS = 0.042  # line spacing in axes units

    def box(x, y, w, h, title, lines, col):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.005,rounding_size=0.012", fc="white", ec=col, lw=1.5))
        ax.text(x + w / 2, y + h - 0.018, title, ha="center", va="top", fontsize=9, color=col, fontweight="bold")
        for i, ln in enumerate(lines):
            ax.text(x + 0.012, y + h - 0.062 - LS * i, ln, fontsize=7.6, color=INK2, va="top")

    def band(y, h, label, col):
        ax.add_patch(FancyBboxPatch((0.005, y), 0.99, h, boxstyle="round,pad=0.004,rounding_size=0.01", fc=col, ec="none", alpha=0.11))
        ax.text(0.012, y + h - 0.008, label, fontsize=8.5, color=INK2, va="top", fontweight="bold")

    xs4 = [0.03, 0.27, 0.51, 0.75]
    w4 = 0.22
    # customers band
    band(0.815, 0.18, "Customers (shippers)", C["orange"])
    for x, t, ls in zip(xs4, ["NASA (anchor)", "Payload companies", "International partners", "Base operations"],
                        [["Moon Base manifests", "Service-level contracts"], ["Hosted payloads, demos", "Spot and contract orders"],
                         ["ESA, JAXA, CSA elements", "Export-control screening"], ["Regolith lots, trash,", "sample return, relocations"]]):
        box(x, 0.83, w4, 0.13, t, ls, C["orange"])
    # platform band
    band(0.285, 0.50, "Marketplace platform (neutral operator)", C["blue"])
    row1 = 0.56
    h1 = 0.21
    for x, t, ls in zip(xs4, ["Order intake", "Registries", "Dispatch engine", "Operator scheduler"],
                        [["Item: mass, interface standard,", "destination, priority, deadline", "Planetary-protection record", "Hazard class, handling needs"],
                         ["Published landing schedule", "Vehicle capabilities, availability", "Interface standards (FLEX, others)", "Safety zones (Artemis Accords)"],
                         ["Generalised-cost sequential auction", "Bundling, consolidation, team lift", "Night-aware acceptance", "Anticipatory staging"],
                         ["Console capacity by autonomy", "Fan-out limits, shift plans", "Latency-aware job timing"]]):
        box(x, row1, w4, h1, t, ls, C["blue"])
    row2 = 0.31
    h2 = 0.22
    xs3 = [0.03, 0.355, 0.68]
    w3 = 0.29
    for x, t, ls in zip(xs3, ["Settlement and gain sharing", "Operations data", "Governance"],
                        [["Job price = variable cost + margin", "Capacity commitments (contract layer)", "Shapley or proportional gain split", "Owner statements, audit trail"],
                         ["Telemetry and item tracking", "Delivery confirmation, exceptions", "Replay and simulation twin", "Public performance statistics"],
                         ["Neutrality rules, appeal path", "Priority classes agreed with NASA", "Safety case: NPR 8715.1, NPR 7150.2", "Data rights, ITAR/EAR segregation"]]):
        box(x, row2, w3, h2, t, ls, C["blue"])
    # operators band
    band(0.02, 0.235, "Vehicle operators and surface assets", C["violet"])
    for x, t, ls in zip(xs4, ["LTV providers", "Heavy hauler", "Small rovers, robots", "Fixed assets"],
                        [["Astrolab, Lunar Outpost", "Crew first, cargo in between"], ["10 t class, night-capable", "Shared asset, team-lift partner"],
                         ["HL-MAPP class, offloading arms", "Pad-side handling"], ["Pads, depot, charging", "Landers with cranes and ramps"]]):
        box(x, 0.035, w4, 0.17, t, ls, C["violet"])
    for x in [xx + w4 / 2 for xx in xs4]:
        ax.add_patch(FancyArrowPatch((x, 0.83), (x, 0.77), arrowstyle="<|-|>", mutation_scale=9, color=MUTED, lw=1))
        ax.add_patch(FancyArrowPatch((x, 0.31), (x, 0.205), arrowstyle="<|-|>", mutation_scale=9, color=MUTED, lw=1))
    ax.text(0.5, 0.80, "orders, quotes, tracking, invoices", fontsize=7.6, color=INK2, ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))
    ax.text(0.5, 0.258, "job offers and bids, telemetry, payments", fontsize=7.6, color=INK2, ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))
    save(fig, "fig19_reference_design")


# ---------------------------------------------------------------------------
# V&V table (runs the Python checks)
# ---------------------------------------------------------------------------
def vv_table():
    from lunarsim import vv
    rows = vv.run_all_checks()
    pd.DataFrame(rows).to_csv(os.path.join(RES, "table_vv.csv"), index=False)
    print("V&V:", sum(r["passed"] for r in rows), "of", len(rows), "passed")

if __name__ == "__main__":
    which = sys.argv[1:] or ["all"]
    funcs = {"sitemap": fig_sitemap, "arch": fig_architecture, "demand": fig_demand, "main": fig_main, "fleet": fig_fleet,
             "thickness": fig_thickness, "heavy": fig_heavy, "latency": fig_latency, "standards": fig_standards,
             "env": fig_environment, "ablations": fig_ablations, "tuned": fig_tuned, "econ": fig_economics, "timeline": fig_timeline,
             "ladder": fig_ladder, "law": fig_law, "anticipation": fig_anticipation, "precision": fig_precision, "design": fig_design, "vv": vv_table}
    for k, f in funcs.items():
        if "all" in which or k in which:
            try:
                f()
            except (FileNotFoundError, KeyError) as e:
                print("skip", k, repr(e))
