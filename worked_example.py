# Author: Deepak K | New Horizon College of Engineering, Dept. of EEE, Bangalore | 2026
# worked_example.py: the 2 robot x 2 delivery example from section 3.4
import numpy as np
from qubo_cap import CapQUBO, exact_optimum

c = np.array([[2, 4], [3, 1]]); load = [2, 1]; Q = [2, 2]
# small enough to enumerate all 256 bitstrings
q = CapQUBO(c, load, Q, a=2)
E, z = q.energy_table()
# constant left over after expanding the squares
offset = q.A * (q.T + sum(int(x) ** 2 for x in q.Q))
print("n qubits:", q.n, "| A =", q.A, "| bitstrings:", len(E))
print("diagonal x00 (excl. offset):", c[0, 0] + q.A * (1 - 2) + q.A * (load[0] ** 2 - 2 * Q[0] * load[0]))
print("constant offset:", offset)
# should be 3, equal to the best feasible assignment (cost 2 + 1)
print("ground energy:", E.min(), "| degeneracy:", int((E == E.min()).sum()))
print("exact feasible optimum:", exact_optimum(c, np.array(load), np.array(Q)))
g = z[E == E.min()]
print("ground-state feasible:", all(q.feasible(q.decode(b)) for b in g))
