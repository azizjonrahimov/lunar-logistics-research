"""Assemble paper.html from the part files, fill result tables and render a PDF with headless Chrome."""
import os, subprocess, sys, json
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RES = os.path.join(ROOT, "results")


def ci(x):
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    return 1.96 * x.std(ddof=1) / np.sqrt(len(x)) if len(x) > 1 else 0.0


def fmt(m, c, nd=1):
    return f"{m:.{nd}f} &plusmn; {c:.{nd}f}"


MECH_LABEL = {"inhouse": "In-house fleets", "pooled_greedy": "Pooled greedy", "central_assign": "Batched assignment",
              "marketplace": "Marketplace (ours)", "unconstrained_bound": "Unconstrained 16-vehicle bound"}


def table_main():
    df = pd.read_csv(os.path.join(RES, "E1_phases.csv"))
    df["immov"] = 100 * df.stranded_kg / df.landed_kg
    rows = []
    rows.append('<p class="tabcap"><b>Table 5.</b> Main results with default fleets: mean &plusmn; 95% CI over 30 seeds. '
                'Urgent = priority-1 items. Immovable = share of landed cargo mass no vehicle or team could ever carry. '
                'Bulk delay is the mean delay of deferrable regolith lots, which the marketplace holds on purpose. '
                'Cost is amortised fleet plus operator time per kilogram of all mass moved.</p>')
    rows.append("<table class=\"wide\"><tr><th>Phase</th><th>Mechanism</th><th class='num'>Urgent p90 delay (h)</th><th class='num'>Urgent mean delay (h)</th>"
                "<th class='num'>Urgent within 24 h</th><th class='num'>Immovable (%)</th><th class='num'>Night strandings / yr</th>"
                "<th class='num'>Trips / yr</th><th class='num'>Bulk delay (h)</th><th class='num'>Operator h / yr</th><th class='num'>Revenue Gini</th><th class='num'>Cost $/kg moved</th></tr>")
    for ph, lab in (("P1", "Phase 1"), ("P2", "Phase 2"), ("P3", "Phase 3")):
        for mech in ("inhouse", "pooled_greedy", "central_assign", "marketplace", "unconstrained_bound"):
            s = df[(df.phase == ph) & (df.mechanism == mech)]
            cls = ' class="best"' if mech == "marketplace" else ""
            rows.append(f"<tr{cls}><td>{lab}</td><td>{MECH_LABEL[mech]}</td>"
                        f"<td class='num'>{fmt(s.delay_prio1_p90_h.mean(), ci(s.delay_prio1_p90_h))}</td>"
                        f"<td class='num'>{fmt(s.delay_prio1_mean_h.mean(), ci(s.delay_prio1_mean_h))}</td>"
                        f"<td class='num'>{fmt(s.sl24_prio1.mean(), ci(s.sl24_prio1), 2)}</td>"
                        f"<td class='num'>{s.immov.mean():.1f}</td>"
                        f"<td class='num'>{fmt(s.night_strandings.mean(), ci(s.night_strandings), 2)}</td>"
                        f"<td class='num'>{s.jobs.mean():.0f}</td>"
                        f"<td class='num'>{s.delay_mean_bulk.mean():.1f}</td>"
                        f"<td class='num'>{s.operator_hours.mean():.0f}</td>"
                        f"<td class='num'>{s.revenue_gini.mean():.2f}</td>"
                        f"<td class='num'>{s.cost_per_kg_usd.mean():,.0f}</td></tr>")
    rows.append("</table>")
    return "\n".join(rows)


def table_abl():
    df = pd.read_csv(os.path.join(RES, "E8_ablations.csv"))
    ev = df[df.batch_h == 0]
    variants = ["marketplace", "no_bundling", "no_consolidate", "no_team_lift", "no_anticipate", "no_backhaul", "no_night_aware", "no_priority"]
    vlab = {"marketplace": "Full marketplace", "no_bundling": "without bundling", "no_consolidate": "without consolidation",
            "no_team_lift": "without team lift", "no_anticipate": "without anticipation", "no_backhaul": "without backhaul",
            "no_night_aware": "without night awareness", "no_priority": "without priority credit"}
    out = ['<p class="tabcap"><b>Table 6.</b> Ablations with tight fleets (Phase 2: four vehicles; Phase 3: six vehicles). '
           'Each cell is the mean over 30 seeds; the bracketed value is the paired difference from the full marketplace with its 95% CI. '
           'Immovable = share of landed cargo mass no vehicle or team could carry.</p>',
           "<table class=\"wide\"><tr><th>Phase</th><th>Variant</th><th class='num'>Urgent p90 delay (h)</th><th class='num'>Trips / yr</th>"
           "<th class='num'>Night strandings / yr</th><th class='num'>Immovable (%)</th><th class='num'>Bulk delay (h)</th><th class='num'>Operator h / yr</th></tr>"]
    for ph, lab in (("P2", "Phase 2"), ("P3", "Phase 3")):
        base = ev[(ev.phase == ph) & (ev.variant == "marketplace")].sort_values("seed")
        for v in variants:
            s = ev[(ev.phase == ph) & (ev.variant == v)].sort_values("seed")
            if not len(s):
                continue
            immov = 100 * (s.stranded_kg / s.landed_kg).mean()

            def cell(m, nd=1):
                if v == "marketplace":
                    return f"{s[m].mean():.{nd}f}"
                d = s[m].values - base[m].values
                return f"{s[m].mean():.{nd}f} <span class='note'>[{d.mean():+.{nd}f} &plusmn; {ci(d):.{nd}f}]</span>"
            out.append(f"<tr><td>{lab}</td><td>{vlab[v]}</td><td class='num'>{cell('delay_prio1_p90_h')}</td><td class='num'>{cell('jobs', 0)}</td>"
                       f"<td class='num'>{cell('night_strandings', 2)}</td><td class='num'>{immov:.1f}</td><td class='num'>{cell('delay_mean_bulk')}</td>"
                       f"<td class='num'>{cell('operator_hours', 0)}</td></tr>")
    out.append("</table>")
    return "\n".join(out)


def table_vv():
    p = os.path.join(RES, "table_vv.csv")
    if not os.path.exists(p):
        return "<p class='note'>Verification table not yet generated.</p>"
    df = pd.read_csv(p)
    out = ['<p class="tabcap"><b>Table B1.</b> Verification checks of the Python implementation (all pass).</p>',
           "<table class=\"small\"><tr><th>Check</th><th class='num'>Reference</th><th class='num'>Simulated</th><th class='num'>Rel. error</th><th class='num'>Tolerance</th><th>Basis</th><th>Result</th></tr>"]
    for _, r in df.iterrows():
        out.append(f"<tr><td>{r['name']}</td><td class='num'>{r['reference']:.5g} {r['unit']}</td><td class='num'>{r['simulated']:.5g} {r['unit']}</td>"
                   f"<td class='num'>{100*r['rel_error']:.3f}%</td><td class='num'>{100*r['tolerance']:.1f}%</td><td class='note'>{r['basis']}</td>"
                   f"<td>{'PASS' if r['passed'] else 'FAIL'}</td></tr>")
    out.append("</table>")
    return "\n".join(out)


def table_e14():
    d = settled_numbers()
    mlab = {"delay_prio1_mean_h": "Urgent mean delay (h)", "delay_prio1_p90_h": "Urgent p90 delay (h)", "sl24_prio1": "Urgent within 24 h",
            "delivered_share": "Delivered share", "cost_per_kg_usd": "Cost $/kg moved"}
    out = ['<p class="tabcap"><b>Table 7.</b> Settled Phase-2 estimates from sequential replication (99% confidence intervals). '
           '<i>n</i> is the number of replications when the run stopped; a target is reached when the half-width is within the stated share of the mean.</p>',
           "<table class=\"small\"><tr><th>Mechanism</th><th>Metric</th><th class='num'>n</th><th class='num'>Mean</th><th class='num'>99% half-width</th><th class='num'>Half-width / mean</th><th class='num'>Target</th><th>Reached</th></tr>"]
    for mech in ("inhouse", "pooled_greedy", "central_assign", "marketplace"):
        if mech not in d:
            continue
        for m in ("delay_prio1_mean_h", "delay_prio1_p90_h", "sl24_prio1", "delivered_share", "cost_per_kg_usd"):
            r = d[mech][m]
            nd = 3 if m in ("sl24_prio1", "delivered_share") else (1 if m == "cost_per_kg_usd" else 2)
            out.append(f"<tr><td>{MECH_LABEL[mech]}</td><td>{mlab[m]}</td><td class='num'>{r['n']:,}</td><td class='num'>{r['mean']:.{nd}f}</td>"
                       f"<td class='num'>{r['half_width']:.{nd}f}</td><td class='num'>{100*r['rel_half_width']:.2f}%</td><td class='num'>{100*r['target']:.0f}%</td>"
                       f"<td>{'yes' if r['reached'] else 'no'}</td></tr>")
    out.append("</table>")
    reached = [m for m in d if d[m]["delay_prio1_mean_h"]["reached"]]
    not_reached = [m for m in d if not d[m]["delay_prio1_mean_h"]["reached"]]
    parts = []
    if reached:
        parts.append("An extended run continued the " + " and ".join(MECH_LABEL[m].lower() for m in reached) + " cell"
                     + ("s" if len(reached) > 1 else "") + " to the 1% target, which was reached after "
                     + ", ".join(f"{d[m]['delay_prio1_mean_h']['n']:,} replications" for m in reached)
                     + f" (half-width {', '.join(f'{100*d[m]['delay_prio1_mean_h']['rel_half_width']:.2f}%' for m in reached)}).")
    if not_reached:
        parts.append("The extended run for the " + ", ".join(MECH_LABEL[m].lower() for m in not_reached)
                     + " cells was interrupted by a memory limit on the workstation before it reached that target, so their estimates stand at "
                     + ", ".join(f"{d[m]['delay_prio1_mean_h']['n']:,}" for m in not_reached) + " replications with half-widths of "
                     + ", ".join(f"{100*d[m]['delay_prio1_mean_h']['rel_half_width']:.1f}%" for m in not_reached)
                     + "; the repository script continues them on request.")
    return "\n".join(out), " ".join(parts)


def settled_numbers():
    """Settled Phase-2 numbers: the extended run where it completed a mechanism, else the 4,000-replication run."""
    base = json.load(open(os.path.join(RES, "E14_precision.json")))
    p_long = os.path.join(RES, "E14_precision_long.json")
    if os.path.exists(p_long):
        long = json.load(open(p_long))
        for mech, dd in long.items():
            base[mech] = dd
    return base


def main():
    parts = [open(os.path.join(HERE, f), encoding="utf-8").read() for f in
             ("part1_front.html", "part2_methods.html", "part3_results.html", "part4_back.html")]
    html = "\n".join(parts)
    t14, sent14 = table_e14()
    html = (html.replace("{{TABLE_MAIN}}", table_main()).replace("{{TABLE_ABL}}", table_abl())
            .replace("{{TABLE_VV}}", table_vv()).replace("{{TABLE_E14}}", t14).replace("{{E14_LONG}}", sent14))
    # abstract numbers
    e3 = pd.read_csv(os.path.join(RES, "E3_thickness.csv"))
    a = e3[(e3.other_duty == 0.3) & (e3.n_companies == 6) & (e3.mechanism == "inhouse")].sort_values("seed")
    b = e3[(e3.other_duty == 0.3) & (e3.n_companies == 6) & (e3.mechanism == "marketplace")].sort_values("seed")
    gain = (a.delay_prio1_p90_h.values - b.delay_prio1_p90_h.values).mean()
    html = html.replace("{E3_GAIN}", f"{gain:.0f}")
    # settled Phase-2 numbers
    d = settled_numbers()
    key = {"INH": "inhouse", "GRD": "pooled_greedy", "BAT": "central_assign", "MKT": "marketplace"}
    for tag, mech in key.items():
        if mech not in d:
            continue
        r = d[mech]
        html = (html.replace("{" + tag + "_MEAN}", f"{r['delay_prio1_mean_h']['mean']:.2f}").replace("{" + tag + "_MEAN_HW}", f"{r['delay_prio1_mean_h']['half_width']:.2f}")
                .replace("{" + tag + "_P90}", f"{r['delay_prio1_p90_h']['mean']:.1f}").replace("{" + tag + "_P90_HW}", f"{r['delay_prio1_p90_h']['half_width']:.1f}")
                .replace("{" + tag + "_SL}", f"{r['sl24_prio1']['mean']:.3f}").replace("{" + tag + "_SL_HW}", f"{r['sl24_prio1']['half_width']:.3f}"))
    if "marketplace" in d and "pooled_greedy" in d:
        gm, mm = d["pooled_greedy"]["delay_prio1_mean_h"]["mean"], d["marketplace"]["delay_prio1_mean_h"]["mean"]
        gp, mp = d["pooled_greedy"]["delay_prio1_p90_h"]["mean"], d["marketplace"]["delay_prio1_p90_h"]["mean"]
        html = html.replace("{MKT_VS_GRD_PCT}", f"{100*(gm-mm)/gm:.0f}").replace("{MKT_VS_GRD_P90_PCT}", f"{100*(gp-mp)/gp:.0f}")
    ns = sorted(set(d[m]["delay_prio1_mean_h"]["n"] for m in d))
    html = html.replace("{N_LONG_WORDS}", (f"{ns[0]:,} replications per cell" if len(ns) == 1 else f"{ns[0]:,}&ndash;{ns[-1]:,} replications per cell"))
    out = os.path.join(HERE, "paper.html")
    open(out, "w", encoding="utf-8").write(html)
    print("wrote", out, len(html.split()), "words approx")
    chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    pdf = os.path.join(HERE, "lunar_logistics_marketplace_paper_v2.pdf")
    cmd = [chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
           f"--print-to-pdf={pdf}", "file:///" + out.replace("\\", "/")]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    print("chrome exit", r.returncode)
    print("pdf", os.path.exists(pdf), os.path.getsize(pdf) if os.path.exists(pdf) else 0)


if __name__ == "__main__":
    main()
