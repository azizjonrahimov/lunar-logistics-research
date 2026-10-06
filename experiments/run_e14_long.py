"""E14 extended: replicate the Phase-2 default cells until the 99% CI of the mean urgent delay is within 1%.

Resumable: mechanisms already recorded as 'reached' in results/E14_precision_long.json are skipped, so an
interrupted run can be continued with the same command. Uses a smaller worker pool than the main suite to
keep memory use modest.
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lunarsim.precision import run_until_precise
from experiments.run_all import MECHS, PHASES, RESULTS

OUT = os.path.join(RESULTS, "E14_precision_long.json")

if __name__ == "__main__":
    sc = PHASES["P2"]
    out = json.load(open(OUT)) if os.path.exists(OUT) else {}
    for mn, (mf, kw) in MECHS.items():
        if mn in out and out[mn]["delay_prio1_mean_h"]["reached"]:
            print(f"[E14 long] {mn}: already settled at n={out[mn]['delay_prio1_mean_h']['n']}, skipping", flush=True)
            continue
        res, df = run_until_precise(sc, mf, {"delay_prio1_mean_h": 0.01, "sl24_prio1": 0.01, "delivered_share": 0.01,
                                              "cost_per_kg_usd": 0.01, "delay_prio1_p90_h": 0.05},
                                    confidence=0.99, block=500, n_min=30, n_max=60000, procs=6, mech_kwargs=kw, verbose=False)
        out[mn] = {m: {"n": r.n, "mean": r.mean, "half_width": r.half_width, "rel_half_width": r.rel_half_width,
                       "target": r.target_rel, "reached": r.reached, "history": r.history} for m, r in res.items()}
        df["mechanism"] = mn
        df.to_csv(os.path.join(RESULTS, f"E14_precision_{mn}.csv"), index=False)
        json.dump(out, open(OUT, "w"), indent=1)
        print(f"[E14 long] {mn}: n={res['delay_prio1_mean_h'].n} " + " ".join(f"{m}={r.rel_half_width:.4f}" for m, r in res.items()), flush=True)
    print("[E14 long] done", flush=True)
