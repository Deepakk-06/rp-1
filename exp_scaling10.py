# Author: Deepak K | 2026
# exp_scaling10.py: RQ4, scaling with problem size, plus the optimizer-budget study
_BUILD_ID = "c7da08e7aa96f4d53cbb864c6fb79984"
import time, numpy as np
from exp_common import *
from step2_qaoa import QAOASim
from qubo_cap import exact_optimum
rows = []
# T = 3 to 6 gives roughly 10 to 18 qubits
for T in (3, 4, 5, 6):
    for seed in range(10):
        inst = make_instance(2, T, seed); P = Prob(inst); sim = QAOASim(P.E, P.n); rm = P.random_metrics()
        rng = np.random.default_rng(4000 + seed)
        # QAOA time here is the cost of simulating it on a CPU, not what real hardware would take
        t0 = time.time(); x = sim.optimize(2, 2, 150, rng); tq = time.time() - t0
        m = P.metrics(sim.probs(x))
        t0 = time.time(); sa_assign(inst["c"], inst["load"], inst["Q"], seed); tsa = time.time() - t0
        t0 = time.time(); exact_optimum(inst["c"], inst["load"], inst["Q"]); tex = time.time() - t0
        rows.append(dict(T=T, seed=seed, n=P.n, pfeas=m["pfeas"], r_pfeas=rm["pfeas"], t_qaoa=tq, t_sa=tsa, t_exact=tex))
        print("scale", T, seed, flush=True)
save_csv("results_scaling.csv", rows)
rows = []
# budget study: 16 restarts in a row, then look at the best state after 1, 2, 4, 8 and 16 of them
for T, ns in ((4, 20), (5, 5)):
    for seed in range(ns):
        P = Prob(make_instance(2, T, seed)); sim = QAOASim(P.E, P.n); rm = P.random_metrics()
        runs = sim.optimize_runs(2, 16, 200, np.random.default_rng(5000 + seed))
        for k in (1, 2, 4, 8, 16):
            x = min(runs[:k], key=lambda t: t[0])[1]
            rows.append(dict(T=T, seed=seed, k=k, pfeas=P.metrics(sim.probs(x))["pfeas"], r_pfeas=rm["pfeas"]))
        print("budget", T, seed, flush=True)
save_csv("results_budget.csv", rows)
