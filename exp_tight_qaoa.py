# Author: Deepak K | 2026
# exp_tight_qaoa.py: RQ6, QAOA against SA and greedy on the tight-capacity family (R=2)
_BUILD_ID = "774df408b6c848170460c6f7fa348436"
import numpy as np
from exp_common import *
from step2_qaoa import QAOASim
rows = []
# T=4 (12-14 qubits): 20 seeds, p = 1 to 3. T=5 (16-18 qubits): 8 seeds, p=2 with a smaller budget
for T, ns, ps, restarts, maxit in ((4, 20, (1, 2, 3), 4, 200), (5, 8, (2,), 2, 150)):
    for seed in range(ns):
        inst = make_instance(2, T, seed, "tight"); P = Prob(inst)
        # no feasible assignment for this seed, skip it
        if P.opt is None: print("infeasible", T, seed); continue
        g = greedy(inst["c"], inst["load"], inst["Q"]); s = sa_assign(inst["c"], inst["load"], inst["Q"], seed)
        gg = 100 * (cost_of(inst["c"], g) - P.opt) / P.opt if g else -1
        sg = 100 * (s - P.opt) / P.opt if s is not None else -1
        sim = QAOASim(P.E, P.n); rm = P.random_metrics(); rng = np.random.default_rng(6000 + seed)
        for p in ps:
            m = P.metrics(sim.probs(sim.optimize(p, restarts, maxit, rng)))
            rows.append(dict(T=T, seed=seed, p=p, n=P.n, pfeas=m["pfeas"], pasg=m["pasg"], r_pfeas=rm["pfeas"],
                             r_pasg=rm["pasg"], sa_gap=sg, greedy_gap=gg, sa_opt=int(sg < 1e-6)))
        print("tight", T, seed, flush=True)
save_csv("results_tight.csv", rows)
