import time, sys
sys.path.insert(0, ".")
from lunarsim import Scenario, run, dispatch
sc = Scenario()
for name, mech in [("inhouse", dispatch.inhouse), ("pooled_greedy", dispatch.pooled_greedy),
                   ("central_assign", dispatch.central_assign), ("marketplace", dispatch.marketplace)]:
    t0 = time.time()
    out = run(sc, mech, seed=1)
    keys = ["landed_kg","ready_kg","delivered_kg","delivered_share","stranded_share","backlog_kg","delay_mean_h","delay_p90_h","utilisation","empty_km_share","jobs","bundled_jobs","team_lifts","backhaul_kg","night_strandings","faults","cost_per_kg_usd","operator_hours"]
    print(f"\n== {name}  ({time.time()-t0:.1f}s)")
    for k in keys:
        print(f"  {k:22s} {out[k]:12.2f}")
