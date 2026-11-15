# Author: Deepak K | New Horizon College of Engineering, Dept. of EEE, Bangalore | 2026
# exp_depth_sweep.py: RQ2 (depth) and RQ3 (penalty weight)
import numpy as np
from exp_common import *
from step2_qaoa import QAOASim
rows = []
# depth study: 30 instances, p = 1, 2, 3, 4 restarts of at most 200 COBYLA iterations
for seed in range(30):
    P = Prob(make_instance(2, 4, seed)); sim = QAOASim(P.E, P.n); rm = P.random_metrics()
    # separate seed streams so changing one study never shifts another
    rng = np.random.default_rng(1000 + seed)
    for p in (1, 2, 3):
        m = P.metrics(sim.probs(sim.optimize(p, 4, 200, rng)))
        rows.append(dict(seed=seed, n=P.n, p=p, **m, r_pfeas=rm["pfeas"], r_popt=rm["popt"], r_pasg=rm["pasg"]))
    print("depth", seed, flush=True)
save_csv("results_depth.csv", rows)
rows = []
# penalty sweep on the first 20 instances
for seed in range(20):
    inst = make_instance(2, 4, seed)
    for a in (0.5, 1, 2, 4, 8):
        # a changes the penalty weight, so the energy table has to be rebuilt every time
        P = Prob(inst, a); sim = QAOASim(P.E, P.n); rm = P.random_metrics()
        rng = np.random.default_rng(2000 + seed)
        for p in (1, 2, 3):
            m = P.metrics(sim.probs(sim.optimize(p, 4, 200, rng)))
            rows.append(dict(seed=seed, a=a, p=p, gs_feas=int(P.gs_feasible), **m, r_pfeas=rm["pfeas"], r_pasg=rm["pasg"]))
    print("penalty", seed, flush=True)
save_csv("results_penalty.csv", rows)
