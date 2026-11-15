# Author: Deepak K | New Horizon College of Engineering, Dept. of EEE, Bangalore | 2026
# step2_qaoa.py: noiseless statevector QAOA, the XY-mixer variant and the Pauli noise model (paper sections 3.5 and 3.6)
_BUILD_ID = "70ce41f300614435be6d72a8f728cd09"
__author__ = "Deepak K"
import numpy as np
from scipy.optimize import minimize


# exp(-i*beta*X) on the chosen qubits, done by reshaping so each qubit becomes its own axis
def apply_x_mixer(psi, beta, qubits):
    c, s = np.cos(beta), -1j * np.sin(beta)
    for q in qubits:
        v = psi.reshape(-1, 2, 1 << q)
        psi = (c * v + s * v[:, ::-1, :]).reshape(-1)
    return psi


# pass xy_pairs to switch the XY mixer on for those qubit pairs, otherwise it is the plain X mixer
class QAOASim:
    def __init__(self, E, n, xy_pairs=None):
        self.n, self.E = n, np.asarray(E, float)
        ar = np.arange(1 << n)
        self.pairs = []
        # reach = states the circuit can reach, everything unless the XY pairs force one-hot
        reach = np.ones(1 << n, bool)
        if xy_pairs:
            for a, b in xy_pairs:
                diff = ((ar >> a) & 1) != ((ar >> b) & 1)
                reach &= diff
                idx = ar[diff]
                self.pairs.append((idx, idx ^ ((1 << a) | (1 << b))))
        self.reach = reach
        sel = self.E[reach]
        # squash the energies into [0, pi] so the gamma angles stay in a sensible range
        self.Er = np.pi * (self.E - sel.min()) / (sel.max() - sel.min())
        # start from a uniform superposition over the reachable states
        self.psi0 = reach.astype(complex) / np.sqrt(reach.sum())
        used = {q for ab in (xy_pairs or []) for q in ab}
        self.xq = [q for q in range(n) if q not in used]

    # XY mixer on the one-hot pairs, ordinary X mixer on the rest
    def _mix(self, psi, beta):
        if self.pairs:
            c, s = np.cos(beta), -1j * np.sin(beta)
            for idx, part in self.pairs:
                new = psi.copy()
                new[idx] = c * psi[idx] + s * psi[part]
                psi = new
        return apply_x_mixer(psi, beta, self.xq)

    # params = [gamma1, beta1, gamma2, beta2, ...], the hook lets the noise code touch the state after each layer
    def state(self, params, hook=None):
        psi = self.psi0
        for l in range(len(params) // 2):
            psi = psi * np.exp(-1j * params[2 * l] * self.Er)
            psi = self._mix(psi, params[2 * l + 1])
            if hook is not None:
                psi = hook(psi)
        return psi

    def probs(self, params):
        psi = self.state(params)
        return psi.real ** 2 + psi.imag ** 2

    def expect(self, params):
        return float(self.probs(params) @ self.Er)

    # a few COBYLA runs from random starting angles, gives back (value, angles) for each run
    def optimize_runs(self, p, restarts, maxiter, rng):
        out = []
        for _ in range(restarts):
            x0 = rng.uniform(0, np.pi, 2 * p)
            r = minimize(self.expect, x0, method="COBYLA", options=dict(maxiter=maxiter))
            out.append((r.fun, r.x))
        return out

    # just keep whichever restart ended lowest
    def optimize(self, p, restarts, maxiter, rng):
        runs = self.optimize_runs(p, restarts, maxiter, rng)
        return min(runs, key=lambda t: t[0])[1]

    # Monte-Carlo noise: after each layer every qubit gets a random Pauli with probability eps, averaged over trajectories
    def noisy_probs(self, params, eps, ntraj, rng):
        if eps == 0:
            return self.probs(params)
        acc = np.zeros(1 << self.n)
        qubits = [q for q in range(self.n)]

        def hook(psi):
            hit = rng.random(self.n) < eps
            for q in np.flatnonzero(hit):
                # which Pauli hit this qubit: 0 is X, 1 is Y, 2 is Z
                k = rng.integers(3)
                v = psi.reshape(-1, 2, 1 << q)
                if k == 0:
                    psi = v[:, ::-1, :].reshape(-1).copy()
                elif k == 2:
                    psi = psi.copy(); psi.reshape(-1, 2, 1 << q)[:, 1, :] *= -1
                else:
                    # Y = i*X*Z and the overall phase doesn't matter, so I leave the i out
                    w = v.copy(); w[:, 1, :] *= -1
                    psi = w[:, ::-1, :].reshape(-1).copy()
            return psi

        for _ in range(ntraj):
            psi = self.state(params, hook)
            acc += psi.real ** 2 + psi.imag ** 2
        return acc / ntraj
