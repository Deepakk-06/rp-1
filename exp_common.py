# Author: Deepak K | 2026
# exp_common.py: shared helpers (MILP optimum, greedy, both SA versions, metrics, stats, csv)
_BUILD_ID = "2b779667621f12e568df40b0010be039"
__author__ = "Deepak K"
import csv, math, os, random
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy import stats
from qubo_cap import CapQUBO, make_instance

# every csv goes into a results/ folder next to the scripts
RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(RES, exist_ok=True)


def save_csv(name, rows):
    path = os.path.join(RES, name)
    keys = list(rows[0].keys())
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)


def load_csv(name):
    with open(os.path.join(RES, name)) as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k, v in r.items():
            try: r[k] = float(v)
            except ValueError: pass
    return rows


# exact optimum from a MILP (HiGHS), returns None when the instance has no feasible assignment
def milp_opt(c, load, Q):
    R, T = c.shape; n = R * T
    A1 = np.zeros((T, n)); A2 = np.zeros((R, n))
    for t in range(T):
        for r in range(R):
            A1[t, r * T + t] = 1; A2[r, r * T + t] = load[t]
    res = milp(c.reshape(-1), constraints=[LinearConstraint(A1, 1, 1), LinearConstraint(A2, -np.inf, Q)],
               integrality=np.ones(n), bounds=Bounds(0, 1))
    return None if res.status == 2 or res.fun is None else float(res.fun)


# biggest deliveries first, each one goes to the cheapest robot that still has room
def greedy(c, load, Q):
    R, T = c.shape
    rem = list(Q); a = [-1] * T
    for t in sorted(range(T), key=lambda t: -load[t]):
        ok = [r for r in range(R) if rem[r] >= load[t]]
        # nobody has room left, so greedy fails on this instance
        if not ok: return None
        r = min(ok, key=lambda r: c[r, t]); a[t] = r; rem[r] -= load[t]
    return a


def cost_of(c, a):
    return float(sum(c[r, t] for t, r in enumerate(a)))


# simulated annealing on the assignment itself: start from greedy, try reassign and swap moves, never accept an infeasible one
def sa_assign(c, load, Q, seed, restarts=5, iters=4000, T0=5.0):
    rng = random.Random(seed)
    R, T = c.shape; load = [int(x) for x in load]; Q = [int(x) for x in Q]
    start = greedy(c, load, Q)
    # greedy got stuck, so try random first-fit a few hundred times to find any feasible starting point
    if start is None:
        for _ in range(500):
            rem = list(Q); a = [-1] * T; ok = True
            for t in rng.sample(range(T), T):
                rs = [r for r in range(R) if rem[r] >= load[t]]
                if not rs: ok = False; break
                r = rng.choice(rs); a[t] = r; rem[r] -= load[t]
            if ok: start = a; break
    if start is None: return None
    cl = c.tolist(); best = cost_of(c, start)
    for _ in range(restarts):
        a = list(start); used = [0] * R
        for t, r in enumerate(a): used[r] += load[t]
        cur = cost_of(c, a)
        for it in range(iters):
            # temperature falls linearly from T0 down to almost zero
            temp = T0 * (1 - it / iters) + 1e-9
            # half the moves reassign one delivery, the other half swap two deliveries
            if rng.random() < 0.5:
                t = rng.randrange(T); rn = rng.randrange(R); ro = a[t]
                if rn == ro or used[rn] + load[t] > Q[rn]: continue
                d = cl[rn][t] - cl[ro][t]
                if d <= 0 or rng.random() < math.exp(-d / temp):
                    used[ro] -= load[t]; used[rn] += load[t]; a[t] = rn; cur += d
            else:
                t1 = rng.randrange(T); t2 = rng.randrange(T); r1, r2 = a[t1], a[t2]
                if r1 == r2: continue
                if used[r1] - load[t1] + load[t2] > Q[r1] or used[r2] - load[t2] + load[t1] > Q[r2]: continue
                d = cl[r2][t1] + cl[r1][t2] - cl[r1][t1] - cl[r2][t2]
                if d <= 0 or rng.random() < math.exp(-d / temp):
                    used[r1] += load[t2] - load[t1]; used[r2] += load[t1] - load[t2]
                    a[t1], a[t2] = r2, r1; cur += d
            if cur < best: best = cur
    return best


# SA on the penalised QUBO: flip one random bit at a time, energies come from the precomputed table
def sa_qubo(E_list, n, A, seed, restarts=5, iters=4000):
    rng = random.Random(seed); best, bz = float("inf"), 0
    for _ in range(restarts):
        z = rng.getrandbits(n); e = E_list[z]
        for it in range(iters):
            temp = A * (1 - it / iters) + 1e-9
            z2 = z ^ (1 << rng.randrange(n)); e2 = E_list[z2]; d = e2 - e
            if d <= 0 or rng.random() < math.exp(-d / temp): z, e = z2, e2
            if e < best: best, bz = e, z
    return best, bz


# one instance with its energy table and the masks for feasible, ground state and optimal assignment
class Prob:
    def __init__(self, inst, a=2.0):
        self.inst = inst
        q = self.q = CapQUBO(inst["c"], inst["load"], inst["Q"], a)
        E, z = q.energy_table()
        self.E, self.z, self.n = E, z, q.n
        self.feas = q.feasible_mask(z)
        X = z[:, : q.R * q.T].reshape(-1, q.R, q.T)
        self.cost = (X * q.c).sum(axis=(1, 2))
        self.opt = milp_opt(q.c, q.load, q.Q)
        # an assignment counts as optimal if it is feasible and costs exactly the MILP optimum (slack bits ignored)
        self.asg_opt = self.feas & (np.abs(self.cost - self.opt) < 1e-7) if self.opt is not None else None
        self.ground = E <= E.min() + 1e-7
        self.Emean, self.Emin = E.mean(), E.min()
        self.gs_feasible = bool(self.feas[self.ground].all())

    # turns a probability vector over bitstrings into the four numbers reported in the paper
    def metrics(self, probs):
        Eq = probs @ self.E
        return dict(ratio=(self.Emean - Eq) / (self.Emean - self.Emin), pfeas=float(probs[self.feas].sum()),
                    popt=float(probs[self.ground].sum()), pasg=float(probs[self.asg_opt].sum()))

    # uniform random sampling baseline, optionally limited to a subset like the one-hot subspace
    def random_metrics(self, mask=None):
        m = np.ones(len(self.E), bool) if mask is None else mask
        return dict(pfeas=float(self.feas[m].mean()), popt=float(self.ground[m].mean()),
                    pasg=float(self.asg_opt[m].mean()))


# paired two-sided Wilcoxon signed-rank test
def wilcoxon_p(a, b):
    d = np.asarray(a) - np.asarray(b)
    if np.all(d == 0): return 1.0
    return float(stats.wilcoxon(a, b, alternative="two-sided").pvalue)


# 95% bootstrap interval for the mean
def boot_ci(x, n=5000, seed=0):
    x = np.asarray(x, float); rng = np.random.default_rng(seed)
    m = rng.choice(x, size=(n, len(x))).mean(axis=1)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))
