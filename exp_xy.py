# Author: Deepak K | 2026
# exp_xy.py: RQ5, XY mixer against the standard mixer (R=2, T=4, 30 instances)
import numpy as np
from exp_common import *
from step2_qaoa import QAOASim
rows = []
for seed in range(30):
    P = Prob(make_instance(2, 4, seed)); T = P.q.T
    # the two qubits of each delivery (x0,t and x1,t) form one XY pair
    pairs = [(t, T + t) for t in range(T)]
    sx = QAOASim(P.E, P.n, pairs); ss = QAOASim(P.E, P.n)
    # two baselines: uniform over the full space and uniform over the one-hot subspace (the fair one)
    rs = P.random_metrics(sx.reach); rf = P.random_metrics()
    rng = np.random.default_rng(3000 + seed)
    for p in (1, 2, 3):
        ms = P.metrics(ss.probs(ss.optimize(p, 4, 200, rng)))
        mx = P.metrics(sx.probs(sx.optimize(p, 4, 200, rng)))
        rows.append(dict(seed=seed, p=p, std_pfeas=ms["pfeas"], std_pasg=ms["pasg"], xy_pfeas=mx["pfeas"], xy_pasg=mx["pasg"],
                         sub_pfeas=rs["pfeas"], sub_pasg=rs["pasg"], full_pfeas=rf["pfeas"], full_pasg=rf["pasg"]))
    print("xy", seed, flush=True)
save_csv("results_xy.csv", rows)
