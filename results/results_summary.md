# Rebuilt results (regenerated from the rebuilt code; compare with the paper's numbers)

## Table II - standard family, gap to exact optimum (30 instances/row)
| size | greedy mean | greedy max | SA mean | SA max |
|---|---|---|---|---|
| 2x4 | 4.22% | 46.1% | 0.00% | 0.00% |
| 4x8 | 4.46% | 48.3% | 0.00% | 0.00% |

SA on the QUBO (ground state found / instances, feasible returned, mean time):
- T=3 (10-12 qubits): 10/10, feasible 10/10, 0.010 s
- T=4 (12-14 qubits): 30/30, feasible 30/30, 0.009 s
- T=5 (16-16 qubits): 10/10, feasible 10/10, 0.011 s
- T=6 (18-18 qubits): 5/10, feasible 10/10, 0.015 s
- total ground state found: 55/60

## Table III - hard family (gap to MILP optimum, mean (max); SA exactly optimal)
| size | feasible | greedy | SA | SA optimal |
|---|---|---|---|---|
| 4x8 | 27/30 | 15.7% (46.8) | 4.5% (40.3) | 20/27 |
| 6x12 | 24/30 | 26.2% (76.4) | 7.1% (34.6) | 13/24 |
| 8x16 | 27/30 | 22.0% (64.9) | 2.9% (14.6) | 10/27 |
| 10x20 | 27/30 | 19.4% (47.0) | 3.8% (17.4) | 4/27 |
- infeasible instances excluded: 15.0 of 120

## Table IV - QAOA vs depth (30 instances, a=2): mean (sd)
| p | approx ratio | Pfeas | Popt | Pasg_opt |
|---|---|---|---|---|
| 1 | 0.630 (0.040) | 0.073 (0.018) | 0.0009 (0.0004) | 0.0067 (0.0014) |
| 2 | 0.650 (0.043) | 0.078 (0.022) | 0.0011 (0.0006) | 0.0072 (0.0017) |
| 3 | 0.677 (0.039) | 0.086 (0.031) | 0.0013 (0.0007) | 0.0079 (0.0022) |
| Random | 0 | 0.043 | 0.00015 | 0.0039 |

Ratio of means to uniform random sampling, and Wilcoxon vs random (min possible p for n=30 is 1.9e-9):
- p=1: Pfeas x1.67, Popt x6.1, Pfeas > random on 30/30 instances, p=1.9e-09; min per-instance ratio 1.51
- p=2: Pfeas x1.79, Popt x7.1, Pfeas > random on 30/30 instances, p=1.9e-09; min per-instance ratio 1.45
- p=3: Pfeas x1.98, Popt x8.6, Pfeas > random on 30/30 instances, p=1.9e-09; min per-instance ratio 1.47

Depth comparisons (Bonferroni threshold 0.0056):
- ratio: 1v2 p=2.6e-08, 1v3 p=1.9e-09, 2v3 p=1.2e-05; p3>p1 on 30/30
- pfeas: 1v2 p=1.7e-06, 1v3 p=3.5e-08, 2v3 p=0.001; p3>p1 on 28/30
- popt: 1v2 p=2.3e-06, 1v3 p=1.9e-09, 2v3 p=1.4e-04; p3>p1 on 30/30
- Pfeas p1->p3 median paired difference 1.02 percentage points

## Table V - penalty sweep (20 instances, mean)
| a | GS feasible | Pfeas p=1 | p=2 | p=3 | Pasg_opt (p=3) |
|---|---|---|---|---|---|
| 0.5 | 20% | 0.065 | 0.070 | 0.067 | 0.0077 |
| 1 | 95% | 0.070 | 0.075 | 0.082 | 0.0081 |
| 2 | 100% | 0.072 | 0.080 | 0.083 | 0.0079 |
| 4 | 100% | 0.073 | 0.081 | 0.085 | 0.0078 |
| 8 | 100% | 0.073 | 0.081 | 0.086 | 0.0078 |
| Random | | 0.043 | | | 0.0039 |
- a=0.5 vs a=2 at p=3: Pfeas diff -0.0161 (p=2.6e-04), Pasg diff -0.00013 (p=0.674)
- a=1 vs a=2 at p=3: Pfeas diff -0.0015 (p=0.076), Pasg diff +0.00018 (p=0.165)
- a=4 vs a=2 at p=3: Pfeas diff +0.0014 (p=0.011), Pasg diff -0.00010 (p=0.430)
- a=8 vs a=2 at p=3: Pfeas diff +0.0025 (p=0.021), Pasg diff -0.00010 (p=0.546)

## Table VI - scaling at p=2 (10 instances per T)
| T | qubits | QAOA sim (s) | SA (s) | exact (ms) | Pfeas mean (sd) | random | ratio |
|---|---|---|---|---|---|---|---|
| 3 | 10-12 | 0.30 | 0.01 | 0.06 | 0.193 (0.049) | 0.100 | 1.93 |
| 4 | 12-14 | 0.68 | 0.01 | 0.08 | 0.072 (0.026) | 0.041 | 1.74 |
| 5 | 16-16 | 4.00 | 0.01 | 0.15 | 0.034 (0.009) | 0.021 | 1.67 |
| 6 | 18-18 | 17.32 | 0.01 | 0.23 | 0.017 (0.003) | 0.010 | 1.62 |
- QAOA > random: T=3: 10/10 (p=0.002), T=4: 10/10 (p=0.002), T=5: 10/10 (p=0.002), T=6: 10/10 (p=0.002)

Optimizer-budget study (mean Pfeas after k restarts):
- T=4 (n=20): k=1: 0.077, k=2: 0.077, k=4: 0.079, k=8: 0.080, k=16: 0.080; random 0.043; ratio k=2 1.80 -> k=16 1.88; 2 vs 16 Wilcoxon p=0.035
- T=5 (n=5): k=1: 0.040, k=2: 0.041, k=4: 0.041, k=8: 0.041, k=16: 0.042; random 0.022; ratio k=2 1.89 -> k=16 1.90; 2 vs 16 Wilcoxon p=0.625

## Table VII - standard vs XY mixer (30 instances, mean)
| p | Pfeas std | Pfeas XY | Pasg std | Pasg XY |
|---|---|---|---|---|
| 1 | 0.073 | 0.857 | 0.0067 | 0.0808 |
| 2 | 0.078 | 0.879 | 0.0072 | 0.0839 |
| 3 | 0.088 | 0.878 | 0.0079 | 0.0853 |
| Random (subspace) | 0.696 | | 0.0625 | |
| Random (full) | 0.043 | | 0.0039 | |
- p=1: XY vs subspace-random: Pfeas x1.23 (better on 30/30, p=1.9e-09), Pasg x1.29 (better on 21/30, p=3.9e-05); XY vs standard Pfeas p=1.9e-09
- p=2: XY vs subspace-random: Pfeas x1.26 (better on 30/30, p=1.9e-09), Pasg x1.34 (better on 24/30, p=1.1e-05); XY vs standard Pfeas p=1.9e-09
- p=3: XY vs subspace-random: Pfeas x1.26 (better on 30/30, p=1.9e-09), Pasg x1.37 (better on 24/30, p=1.1e-05); XY vs standard Pfeas p=1.9e-09

## Table VIII - tight-capacity family (R=2)
| T | p | inst | Pfeas (ratio) | Pasg (ratio) | SA optimal |
|---|---|---|---|---|---|
| 4 | 1 | 17 | 0.0276 (1.47) | 0.0057 (1.46) | 16/17 |
  - QAOA Pfeas > random on 17/17, Wilcoxon p=1.5e-05; SA gap mean 1.45% max 24.6%; greedy gap mean 5.43%
| 4 | 2 | 17 | 0.0268 (1.42) | 0.0055 (1.41) | 16/17 |
  - QAOA Pfeas > random on 17/17, Wilcoxon p=1.5e-05; SA gap mean 1.45% max 24.6%; greedy gap mean 5.43%
  - SA failed on seed 8 (gap 24.6%): QAOA Pasg=0.44% vs random 0.39%; ~1043 shots for 99% confidence vs 2^T=16 assignments to enumerate
| 4 | 3 | 17 | 0.0276 (1.46) | 0.0056 (1.44) | 16/17 |
  - QAOA Pfeas > random on 17/17, Wilcoxon p=1.5e-05; SA gap mean 1.45% max 24.6%; greedy gap mean 5.43%
  - SA failed on seed 8 (gap 24.6%): QAOA Pasg=0.50% vs random 0.39%; ~917 shots for 99% confidence vs 2^T=16 assignments to enumerate
| 5 | 2 | 7 | 0.0079 (1.36) | 0.0013 (1.35) | 6/7 |
  - QAOA Pfeas > random on 7/7, Wilcoxon p=0.016; SA gap mean 3.75% max 26.2%; greedy gap mean 3.75%
  - SA failed on seed 1 (gap 26.2%): QAOA Pasg=0.13% vs random 0.10%; ~3464 shots for 99% confidence vs 2^T=32 assignments to enumerate

## Noise study (p=2, 20 instances, 60 trajectories)
- eps=0: Pfeas 0.0777, approx ratio 0.659, x random 1.83, beats random on 20/20
- eps=0.002: Pfeas 0.0773, approx ratio 0.653, x random 1.81, beats random on 20/20, p vs noiseless=2.3e-04
- eps=0.005: Pfeas 0.0769, approx ratio 0.648, x random 1.81, beats random on 20/20, p vs noiseless=1.9e-06
- eps=0.01: Pfeas 0.0761, approx ratio 0.638, x random 1.79, beats random on 20/20, p vs noiseless=1.9e-06
- eps=0.02: Pfeas 0.0742, approx ratio 0.615, x random 1.74, beats random on 20/20, p vs noiseless=1.9e-06
- eps=0.05: Pfeas 0.0690, approx ratio 0.544, x random 1.62, beats random on 20/20, p vs noiseless=1.9e-06