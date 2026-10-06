"""build.py: merge the extended precision run (where it finished) with the 4,000-replication run."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "paper/build.py")
s = open(p, encoding="utf-8").read()

old_settled = s[s.index("def settled_numbers():"):s.index("def main():")]
new_settled = '''def settled_numbers():
    """Settled Phase-2 numbers: the extended run where it completed a mechanism, else the 4,000-replication run."""
    base = json.load(open(os.path.join(RES, "E14_precision.json")))
    p_long = os.path.join(RES, "E14_precision_long.json")
    if os.path.exists(p_long):
        long = json.load(open(p_long))
        for mech, dd in long.items():
            base[mech] = dd
    return base


'''
s = s.replace(old_settled, new_settled)

old_t14 = s[s.index("def table_e14():"):s.index("def settled_numbers():")]
new_t14 = '''def table_e14():
    d = settled_numbers()
    mlab = {"delay_prio1_mean_h": "Urgent mean delay (h)", "delay_prio1_p90_h": "Urgent p90 delay (h)", "sl24_prio1": "Urgent within 24 h",
            "delivered_share": "Delivered share", "cost_per_kg_usd": "Cost $/kg moved"}
    out = ['<p class="tabcap"><b>Table 7.</b> Settled Phase-2 estimates from sequential replication (99% confidence intervals). '
           '<i>n</i> is the number of replications when the run stopped; a target is reached when the half-width is within the stated share of the mean.</p>',
           "<table class=\\"small\\"><tr><th>Mechanism</th><th>Metric</th><th class='num'>n</th><th class='num'>Mean</th><th class='num'>99% half-width</th><th class='num'>Half-width / mean</th><th class='num'>Target</th><th>Reached</th></tr>"]
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
    return "\\n".join(out), " ".join(parts)


'''
s = s.replace(old_t14, new_t14)
open(p, "w", encoding="utf-8").write(s)
import ast
ast.parse(s)
print("ok")
