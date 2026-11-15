# Author: Deepak K | New Horizon College of Engineering, Dept. of EEE, Bangalore | 2026
# exp_hard.py: RQ1 on the tight-capacity family, classical solvers only (too big to simulate)
import numpy as np
from exp_common import *
rows = []
# four sizes, 30 seeds each
for (R, T) in [(4, 8), (6, 12), (8, 16), (10, 20)]:
    for seed in range(30):
        i = make_instance(R, T, seed, "tight"); opt = milp_opt(i["c"], i["load"], i["Q"])
        # no feasible assignment exists, so skip it (marked feasible=0 in the csv)
        if opt is None:
            rows.append(dict(R=R, T=T, seed=seed, feasible=0, opt=-1, greedy_gap=-1, sa_gap=-1, greedy_ok=0, sa_opt=0)); continue
        g = greedy(i["c"], i["load"], i["Q"]); s = sa_assign(i["c"], i["load"], i["Q"], seed)
        gg = 100 * (cost_of(i["c"], g) - opt) / opt if g is not None else -1
        sg = 100 * (s - opt) / opt if s is not None else -1
        rows.append(dict(R=R, T=T, seed=seed, feasible=1, opt=opt, greedy_gap=gg, sa_gap=sg,
                         greedy_ok=int(g is not None), sa_opt=int(s is not None and sg < 1e-6)))
save_csv("results_hard.csv", rows)
print("hard done")
