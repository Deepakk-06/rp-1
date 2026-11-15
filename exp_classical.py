# Author: Deepak K | New Horizon College of Engineering, Dept. of EEE, Bangalore | 2026
# Project team: A M Likhitha, Chiranthan P, Mohammed Kaif | Guide: Vinod Kumar S
# exp_classical.py: RQ1 on the standard family (greedy, SA on assignments, SA on the QUBO)
import time, numpy as np
from exp_common import *
rows = []
# part 1: greedy and SA on assignments, gap measured against the exact MILP optimum
for (R, T) in [(2, 4), (4, 8)]:
    for seed in range(30):
        i = make_instance(R, T, seed); opt = milp_opt(i["c"], i["load"], i["Q"])
        g = greedy(i["c"], i["load"], i["Q"]); s = sa_assign(i["c"], i["load"], i["Q"], seed)
        rows.append(dict(R=R, T=T, seed=seed, opt=opt, greedy_gap=100 * (cost_of(i["c"], g) - opt) / opt,
                         sa_gap=100 * (s - opt) / opt))
save_csv("results_classical.csv", rows)
rows = []
# part 2: SA on the QUBO itself, which is what QAOA sees (T = 3 to 6)
for T, ns in [(3, 10), (4, 30), (5, 10), (6, 10)]:
    for seed in range(ns):
        i = make_instance(2, T, seed); q = CapQUBO(i["c"], i["load"], i["Q"], 2.0)
        E, z = q.energy_table(); t0 = time.time()
        # success means it found the true QUBO ground state
        best, bz = sa_qubo(E.tolist(), q.n, q.A, seed)
        rows.append(dict(T=T, seed=seed, n=q.n, found_gs=int(best <= E.min() + 1e-7),
                         feasible=int(q.feasible_mask(z[bz:bz + 1])[0]), time=time.time() - t0))
save_csv("results_quboSA.csv", rows)
print("classical done")
