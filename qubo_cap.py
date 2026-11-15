# Author: Deepak K | New Horizon College of Engineering, Dept. of EEE, Bangalore | 2026
# qubo_cap.py: QUBO encoding of the capacity-limited, traffic-aware delivery assignment (paper section 3)
_BUILD_ID = "776422257ef5b411ca051edbeb65e840"
__author__ = "Deepak K"
import itertools
import numpy as np


# slack bits for the capacity constraint: 1, 2, 4, ... and the last weight is trimmed so every value from 0 to Q is reachable
def slack_weights(Q):
    w, total = [], 0
    p = 1
    while total + p <= Q:
        w.append(p)
        total += p
        p *= 2
    if total < Q:
        w.append(Q - total)
    return w


# random instance generator, the seed keeps runs repeatable and family picks easy (standard) or tight capacity
def make_instance(R, T, seed, family="standard"):
    rng = np.random.default_rng(seed)
    if family == "standard":
        d = rng.uniform(1, 10, (R, T))
        tau = rng.uniform(1, 2, (R, T))
        # standard family: every delivery weighs 1 or 2
        load = rng.integers(1, 3, T)
        # standard family: each robot gets one unit of spare capacity
        Q = np.full(R, int(np.ceil(load.sum() / R)) + 1)
    else:
        d = rng.uniform(1, 10, (R, T))
        # tight family below: heavier traffic, loads 1 to 4 and no spare capacity at all
        tau = rng.uniform(1, 3, (R, T))
        load = rng.integers(1, 5, T)
        Q = np.full(R, int(np.ceil(load.sum() / R)))
    return dict(c=d * tau, load=load, Q=Q, R=R, T=T)


# builds the penalised QUBO, this is equation (4) in the paper
class CapQUBO:
    def __init__(self, c, load, Q, a=2.0):
        self.c = np.asarray(c, float)
        self.load = np.asarray(load, int)
        self.Q = np.asarray(Q, int)
        self.R, self.T = self.c.shape
        # penalty weight A = a * (largest cost)
        self.A = a * self.c.max()
        self.w = [slack_weights(int(q)) for q in self.Q]
        self.K = [len(w) for w in self.w]
        # qubits = assignment variables + all the slack bits
        self.n = self.R * self.T + sum(self.K)

        # qubit layout: x[r,t] first (robot by robot), then the slack bits of each robot
        self.x_idx = lambda r, t: r * self.T + t
        off = self.R * self.T
        self.s_idx = []
        for r in range(self.R):
            self.s_idx.append(list(range(off, off + self.K[r])))
            off += self.K[r]

    # energy of every one of the 2^n bitstrings in one go, fine up to about 18 qubits
    def energy_table(self):
        n = self.n
        # bit i of the integer index is variable i
        z = ((np.arange(2 ** n)[:, None] >> np.arange(n)) & 1).astype(np.int8)
        X = z[:, : self.R * self.T].reshape(-1, self.R, self.T)
        E = (X * self.c).sum(axis=(1, 2)).astype(float)
        # C1 penalty: every delivery needs exactly one robot
        E += self.A * ((X.sum(axis=1) - 1) ** 2).sum(axis=1)
        for r in range(self.R):
            # C2 penalty: loads plus slack have to add up to the capacity
            S = z[:, self.s_idx[r]] @ np.array(self.w[r])
            E += self.A * ((X[:, r, :] @ self.load + S - self.Q[r]) ** 2)
        return E, z

    def decode(self, z):
        X = np.asarray(z[: self.R * self.T]).reshape(self.R, self.T)
        return X

    def feasible(self, X):
        X = np.asarray(X)
        return bool((X.sum(axis=0) == 1).all() and ((X @ self.load) <= self.Q).all())

    # True where C1 and C2 both hold (slack bits are ignored here)
    def feasible_mask(self, z):
        X = z[:, : self.R * self.T].reshape(-1, self.R, self.T)
        ok1 = (X.sum(axis=1) == 1).all(axis=1)
        ok2 = ((X @ self.load) <= self.Q).all(axis=1)
        return ok1 & ok2


# brute force over all assignments, only sensible for small T
def exact_optimum(c, load, Q):
    R, T = c.shape
    best, arg = np.inf, None
    for a in itertools.product(range(R), repeat=T):
        used = np.zeros(R)
        for t, r in enumerate(a):
            used[r] += load[t]
        if (used <= Q).all():
            cost = sum(c[r, t] for t, r in enumerate(a))
            if cost < best:
                best, arg = cost, a
    return best, arg
