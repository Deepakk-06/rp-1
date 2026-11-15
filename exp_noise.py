# Author: Deepak K | 2026
# exp_noise.py: RQ7, depolarizing noise (p=2, 60 trajectories, 20 instances)
import numpy as np
from exp_common import *
from step2_qaoa import QAOASim
rows = []
for seed in range(20):
    P = Prob(make_instance(2, 4, seed)); sim = QAOASim(P.E, P.n); rm = P.random_metrics()
    # angles are optimised without noise and only evaluated under noise, no re-optimising
    rng = np.random.default_rng(7000 + seed); x = sim.optimize(2, 4, 200, rng)
    for eps in (0, 0.002, 0.005, 0.01, 0.02, 0.05):
        m = P.metrics(sim.noisy_probs(x, eps, 60, rng))
        rows.append(dict(seed=seed, eps=eps, pfeas=m["pfeas"], ratio=m["ratio"], r_pfeas=rm["pfeas"]))
    print("noise", seed, flush=True)
save_csv("results_noise.csv", rows)
