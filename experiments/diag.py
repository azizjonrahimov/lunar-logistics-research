import sys; sys.path.insert(0, ".")
import numpy as np, warnings; warnings.filterwarnings("ignore")
from lunarsim import run, dispatch
from experiments.scenarios import PHASES
sc = PHASES["P3"].with_(other_duty_share=0.5, fleet=[("NASA","LTV","supervised","A"),("CoA","HAUL","supervised","A"),("CoB","LTV","autonomous","A"),("CoC","LTV","teleop","A")], n_operators=2)
keys=["delay_prio1_mean_h","delay_prio1_p90_h","sl24_prio1","delay_mean_consumables","delay_mean_bulk","delay_mean_return","night_strandings","jobs","operator_hours"]
print(f"{'config':34s}"+"".join(f"{k[:14]:>15s}" for k in keys))
cfgs=[("central b0",dispatch.central_assign,{}),("central b2",dispatch.central_assign,{"batch_h":2.0}),
      ("mkt b0",dispatch.marketplace,{}),("mkt b0.5",dispatch.marketplace,{"batch_h":0.5}),("mkt b1",dispatch.marketplace,{"batch_h":1.0}),("mkt b2",dispatch.marketplace,{"batch_h":2.0}),
      ("mkt b2 no night",dispatch.marketplace_no_night,{"batch_h":2.0}),("mkt b2 no prio",dispatch.marketplace_no_priority,{"batch_h":2.0}),
      ("mkt b2 no bundling",dispatch.marketplace_no_bundling,{"batch_h":2.0}),("pooled greedy",dispatch.pooled_greedy,{})]
for name,m,kw in cfgs:
    outs=[run(sc,m,seed=s,**kw) for s in range(3)]
    print(f"{name:34s}"+"".join(f"{np.mean([o[k] for o in outs]):15.2f}" for k in keys))
