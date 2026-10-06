import os, ast
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "experiments/make_figures.py")
lines = open(p, encoding="utf-8").read().split("\n")
# repair string literals split across physical lines (artefact of an earlier patch)
out, i = [], 0
while i < len(lines):
    ln = lines[i]
    while ln.count('"') % 2 == 1 and '"""' not in ln and i + 1 < len(lines):
        i += 1
        ln = ln + "\\n" + lines[i]
    out.append(ln)
    i += 1
s = "\n".join(out)

# demand legend position
s = s.replace('''    ax.set_title("B. Simulated item masses by phase", fontsize=8.5)
    ax.legend(loc="upper left", fontsize=7)''', '''    ax.set_title("B. Simulated item masses by phase", fontsize=8.5)
    ax.legend(loc="upper right", fontsize=8)''')

# rewrite fig_design with a computed grid
start = s.index("def fig_design():")
end = s.index("# ---------------------------------------------------------------------------\n# V&V table")
new = '''def fig_design():
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


'''
s = s[:start] + new + s[end:]
ast.parse(s)
open(p, "w", encoding="utf-8").write(s)
print("ok")
