"""Replace hard-coded settled Phase-2 numbers in the paper text with placeholders filled by build.py."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "paper/part3_results.html")
s = open(p, encoding="utf-8").read()
pairs = [
    ("Section 6.14 replicates the Phase-2 cells 4,000 times: the settled mean urgent delays are 14.58 &plusmn; 0.40 h in-house, 7.38 &plusmn; 0.26 h pooled greedy, 7.54 &plusmn; 0.25 h batched assignment and 6.31 &plusmn; 0.22 h marketplace (99% CIs), so the marketplace is 14% faster than greedy pooling on the mean and on the 90th percentile (15.1 against 17.5 h), with a same-day service level of 0.938 against 0.921.",
     "Section 6.14 replicates the Phase-2 cells until their 99% confidence intervals settle ({N_LONG_WORDS}): the settled mean urgent delays are {INH_MEAN} &plusmn; {INH_MEAN_HW} h in-house, {GRD_MEAN} &plusmn; {GRD_MEAN_HW} h pooled greedy, {BAT_MEAN} &plusmn; {BAT_MEAN_HW} h batched assignment and {MKT_MEAN} &plusmn; {MKT_MEAN_HW} h marketplace (99% CIs), so the marketplace is {MKT_VS_GRD_PCT}% faster than greedy pooling on the mean and {MKT_VS_GRD_P90_PCT}% on the 90th percentile ({MKT_P90} against {GRD_P90} h), with a same-day service level of {MKT_SL} against {GRD_SL}."),
    ("The mean urgent delay needs far more: at 4,000 replications its 99% half-width is 2.8% in-house and 3.3&ndash;3.5% for the pooled rules, and the 90th-percentile delay is at 3.2&ndash;4.8%, inside its 5% target. The heavy tail of delays, driven by the few items that wait through a night, is what makes the mean slow to settle; a longer run that continues to the 1% target is reported in Table 7 and in the repository. {{E14_LONG}}",
     "The mean urgent delay needs far more: at 4,000 replications its 99% half-width is still 2.8% in-house and 3.3&ndash;3.5% for the pooled rules, while the 90th-percentile delay is at 3.2&ndash;4.8%, inside its 5% target. The heavy tail of delays, driven by the few items that wait through a night, is what makes the mean slow to settle. {{E14_LONG}} Table 7 lists the settled estimates."),
    ("The settled Phase-2 estimates are the ones quoted in Section 6.1: mean urgent delay 14.58 &plusmn; 0.40 h in-house, 7.38 &plusmn; 0.26 h pooled greedy, 7.54 &plusmn; 0.25 h batched assignment and 6.31 &plusmn; 0.22 h marketplace; 90th percentiles 38.9 &plusmn; 1.2, 17.5 &plusmn; 0.8, 17.1 &plusmn; 0.8 and 15.1 &plusmn; 0.7 h; same-day service levels 0.819 &plusmn; 0.006, 0.921 &plusmn; 0.005, 0.924 &plusmn; 0.005 and 0.938 &plusmn; 0.004 (all 99% CIs, 4,000 replications). At that precision every pairwise difference among the four rules is distinguishable from zero, including the marketplace's 14% advantage over greedy pooling that the 30-seed cells left in doubt.",
     "The settled Phase-2 estimates are the ones quoted in Section 6.1: mean urgent delay {INH_MEAN} &plusmn; {INH_MEAN_HW} h in-house, {GRD_MEAN} &plusmn; {GRD_MEAN_HW} h pooled greedy, {BAT_MEAN} &plusmn; {BAT_MEAN_HW} h batched assignment and {MKT_MEAN} &plusmn; {MKT_MEAN_HW} h marketplace; 90th percentiles {INH_P90} &plusmn; {INH_P90_HW}, {GRD_P90} &plusmn; {GRD_P90_HW}, {BAT_P90} &plusmn; {BAT_P90_HW} and {MKT_P90} &plusmn; {MKT_P90_HW} h; same-day service levels {INH_SL} &plusmn; {INH_SL_HW}, {GRD_SL} &plusmn; {GRD_SL_HW}, {BAT_SL} &plusmn; {BAT_SL_HW} and {MKT_SL} &plusmn; {MKT_SL_HW} (all 99% CIs). At that precision every pairwise difference among the four rules is distinguishable from zero, including the marketplace's {MKT_VS_GRD_PCT}% advantage over greedy pooling that the 30-seed cells left in doubt."),
]
for a, b in pairs:
    assert a in s, a[:80]
    s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)

p = os.path.join(ROOT, "paper/build.py")
s = open(p, encoding="utf-8").read()
a = '''    html = html.replace("{E3_GAIN}", f"{gain:.0f}")'''
b = '''    html = html.replace("{E3_GAIN}", f"{gain:.0f}")
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
    html = html.replace("{N_LONG_WORDS}", (f"{ns[0]:,} replications per cell" if len(ns) == 1 else f"{ns[0]:,}&ndash;{ns[-1]:,} replications per cell"))'''
assert a in s
s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)

p = os.path.join(ROOT, "paper/style.css")
s = open(p, encoding="utf-8").read()
s += "\n.appendix table { break-inside: auto; }\n.appendix tr { break-inside: avoid; }\n"
open(p, "w", encoding="utf-8").write(s)
print("ok")
