import time, sys
sys.path.insert(0, ".")
import numpy as np
from lunarsim import run, dispatch
from experiments.scenarios import PHASES
keys = ["landed_kg","ready_kg","delivered_share","stranded_share","backlog_kg","delay_mean_h","delay_p90_h","delay_prio1_mean_h","utilisation","empty_km_share","jobs","bundled_jobs","team_lifts","backhaul_kg","night_strandings","faults","cost_per_kg_usd","operator_hours","unmet_operator_waits"]
mechs = [("inhouse", dispatch.inhouse, {}), ("pooled_greedy", dispatch.pooled_greedy, {}),
         ("central_assign", dispatch.central_assign, {"batch_h": 2.0}),
         ("marketplace_b0", dispatch.marketplace, {}), ("marketplace_b2", dispatch.marketplace, {"batch_h": 2.0}),
         ("marketplace_b6", dispatch.marketplace, {"batch_h": 6.0})]
for ph, sc in PHASES.items():
    print(f"\n######## {ph}")
    print(f"{'metric':24s}" + "".join(f"{m[0]:>16s}" for m in mechs))
    rows = {k: [] for k in keys}
    times = []
    for name, mech, kw in mechs:
        t0 = time.time()
        outs = [run(sc, mech, seed=s, **kw) for s in range(3)]
        times.append(time.time() - t0)
        for k in keys:
            rows[k].append(np.mean([o[k] for o in outs]))
    for k in keys:
        print(f"{k:24s}" + "".join(f"{v:16.3f}" for v in rows[k]))
    print(f"{'seconds(3 seeds)':24s}" + "".join(f"{v:16.1f}" for v in times))
