# Author: Deepak K | 2026
# analyze.py: all the statistics and tables, writes results/results_summary.md and numbers.json
import json, math, numpy as np
from exp_common import *

L = []; N = {}
def out(s=""): L.append(s); print(s)
def col(rows, _key, **f): return np.array([r[_key] for r in rows if all(r[a] == b for a, b in f.items())])
def pf(p): return f"{p:.1e}" if p < 1e-3 else f"{p:.3f}"

out("# Rebuilt results (regenerated from the rebuilt code; compare with the paper's numbers)\n")

# RQ1: classical baselines
c = load_csv("results_classical.csv")
out("## Table II - standard family, gap to exact optimum (30 instances/row)")
out("| size | greedy mean | greedy max | SA mean | SA max |\n|---|---|---|---|---|")
for R, T in [(2, 4), (4, 8)]:
    g, s = col(c, "greedy_gap", R=R), np.maximum(col(c, "sa_gap", R=R), 0)
    out(f"| {R}x{T} | {g.mean():.2f}% | {g.max():.1f}% | {s.mean():.2f}% | {s.max():.2f}% |")
    N[f"classical_{R}x{T}"] = dict(greedy_mean=g.mean(), greedy_max=g.max(), sa_mean=s.mean(), sa_max=s.max())
q = load_csv("results_quboSA.csv")
out("\nSA on the QUBO (ground state found / instances, feasible returned, mean time):")
for T in (3, 4, 5, 6):
    r = [x for x in q if x["T"] == T]
    out(f"- T={T} ({int(min(x['n'] for x in r))}-{int(max(x['n'] for x in r))} qubits): {int(sum(x['found_gs'] for x in r))}/{len(r)}, "
        f"feasible {int(sum(x['feasible'] for x in r))}/{len(r)}, {np.mean([x['time'] for x in r]):.3f} s")
tot = int(sum(x["found_gs"] for x in q)); out(f"- total ground state found: {tot}/{len(q)}")
N["quboSA_total"] = [tot, len(q)]
h = load_csv("results_hard.csv")
out("\n## Table III - hard family (gap to MILP optimum, mean (max); SA exactly optimal)")
out("| size | feasible | greedy | SA | SA optimal |\n|---|---|---|---|---|")
hard = {}
for R, T in [(4, 8), (6, 12), (8, 16), (10, 20)]:
    r = [x for x in h if x["R"] == R]; f = [x for x in r if x["feasible"] == 1]
    g = np.array([x["greedy_gap"] for x in f if x["greedy_ok"]]); s = np.array([x["sa_gap"] for x in f])
    so = int(sum(x["sa_opt"] for x in f))
    out(f"| {R}x{T} | {len(f)}/{len(r)} | {g.mean():.1f}% ({g.max():.1f}) | {s.mean():.1f}% ({s.max():.1f}) | {so}/{len(f)} |")
    hard[f"{R}x{T}"] = dict(feasible=len(f), greedy=g.mean(), sa=s.mean(), sa_opt=so,
                            greedy_fail=int(sum(1 - x["greedy_ok"] for x in f)))
N["hard"] = hard
out(f"- infeasible instances excluded: {sum(1 - x['feasible'] for x in h)} of {len(h)}")


# RQ2: QAOA vs depth
d = load_csv("results_depth.csv")
out("\n## Table IV - QAOA vs depth (30 instances, a=2): mean (sd)")
out("| p | approx ratio | Pfeas | Popt | Pasg_opt |\n|---|---|---|---|---|")
D = {}
for p in (1, 2, 3):
    r = {k: col(d, k, p=p) for k in ("ratio", "pfeas", "popt", "pasg", "r_pfeas", "r_popt", "r_pasg")}
    D[p] = r
    out(f"| {p} | {r['ratio'].mean():.3f} ({r['ratio'].std(ddof=1):.3f}) | {r['pfeas'].mean():.3f} ({r['pfeas'].std(ddof=1):.3f}) | "
        f"{r['popt'].mean():.4f} ({r['popt'].std(ddof=1):.4f}) | {r['pasg'].mean():.4f} ({r['pasg'].std(ddof=1):.4f}) |")
r0 = D[1]
out(f"| Random | 0 | {r0['r_pfeas'].mean():.3f} | {r0['r_popt'].mean():.5f} | {r0['r_pasg'].mean():.4f} |")
out("\nRatio of means to uniform random sampling, and Wilcoxon vs random (min possible p for n=30 is 1.9e-9):")
for p in (1, 2, 3):
    r = D[p]
    out(f"- p={p}: Pfeas x{r['pfeas'].mean() / r['r_pfeas'].mean():.2f}, Popt x{r['popt'].mean() / r['r_popt'].mean():.1f}, "
        f"Pfeas > random on {int((r['pfeas'] > r['r_pfeas']).sum())}/30 instances, p={pf(wilcoxon_p(r['pfeas'], r['r_pfeas']))}; "
        f"min per-instance ratio {np.min(r['pfeas'] / r['r_pfeas']):.2f}")
out(f"\nDepth comparisons (Bonferroni threshold {0.05 / 9:.4f}):")
# 9 depth comparisons in total, so the Bonferroni threshold is 0.05/9
for k in ("ratio", "pfeas", "popt"):
    ps = {f"{a}v{b}": wilcoxon_p(D[b][k], D[a][k]) for a, b in [(1, 2), (1, 3), (2, 3)]}
    out(f"- {k}: " + ", ".join(f"{n} p={pf(v)}" for n, v in ps.items()) + f"; p3>p1 on {int((D[3][k] > D[1][k]).sum())}/30")
dd = D[3]["pfeas"] - D[1]["pfeas"]
out(f"- Pfeas p1->p3 median paired difference {100 * np.median(dd):.2f} percentage points")
N["depth"] = {p: dict(pfeas=D[p]["pfeas"].mean(), ratio=D[p]["ratio"].mean(), popt=D[p]["popt"].mean(), pasg=D[p]["pasg"].mean(),
                      r_pfeas=D[p]["r_pfeas"].mean()) for p in (1, 2, 3)}

# RQ3: penalty weight
pen = load_csv("results_penalty.csv")
out("\n## Table V - penalty sweep (20 instances, mean)")
out("| a | GS feasible | Pfeas p=1 | p=2 | p=3 | Pasg_opt (p=3) |\n|---|---|---|---|---|---|")
for a in (0.5, 1, 2, 4, 8):
    g = col(pen, "gs_feas", a=a, p=1).mean() * 100
    out(f"| {a} | {g:.0f}% | " + " | ".join(f"{col(pen, 'pfeas', a=a, p=p).mean():.3f}" for p in (1, 2, 3)) + f" | {col(pen, 'pasg', a=a, p=3).mean():.4f} |")
out(f"| Random | | {col(pen, 'r_pfeas', a=2, p=1).mean():.3f} | | | {col(pen, 'r_pasg', a=2, p=1).mean():.4f} |")
base_f, base_a = col(pen, "pfeas", a=2, p=3), col(pen, "pasg", a=2, p=3)
for a in (0.5, 1, 4, 8):
    df = col(pen, "pfeas", a=a, p=3) - base_f; da = col(pen, "pasg", a=a, p=3) - base_a
    out(f"- a={a} vs a=2 at p=3: Pfeas diff {df.mean():+.4f} (p={pf(wilcoxon_p(col(pen, 'pfeas', a=a, p=3), base_f))}), "
        f"Pasg diff {da.mean():+.5f} (p={pf(wilcoxon_p(col(pen, 'pasg', a=a, p=3), base_a))})")

# RQ4: problem size and optimizer budget
s = load_csv("results_scaling.csv")
out("\n## Table VI - scaling at p=2 (10 instances per T)")
out("| T | qubits | QAOA sim (s) | SA (s) | exact (ms) | Pfeas mean (sd) | random | ratio |\n|---|---|---|---|---|---|---|---|")
S = {}
for T in (3, 4, 5, 6):
    r = [x for x in s if x["T"] == T]; pfe = np.array([x["pfeas"] for x in r]); rr = np.array([x["r_pfeas"] for x in r])
    out(f"| {T} | {int(min(x['n'] for x in r))}-{int(max(x['n'] for x in r))} | {np.mean([x['t_qaoa'] for x in r]):.2f} | "
        f"{np.mean([x['t_sa'] for x in r]):.2f} | {1000 * np.mean([x['t_exact'] for x in r]):.2f} | {pfe.mean():.3f} ({pfe.std(ddof=1):.3f}) | "
        f"{rr.mean():.3f} | {pfe.mean() / rr.mean():.2f} |")
    S[T] = dict(pfeas=pfe.mean(), rand=rr.mean(), beat=int((pfe > rr).sum()), p=wilcoxon_p(pfe, rr))
out("- QAOA > random: " + ", ".join(f"T={T}: {v['beat']}/10 (p={pf(v['p'])})" for T, v in S.items()))
N["scaling"] = S
b = load_csv("results_budget.csv")
out("\nOptimizer-budget study (mean Pfeas after k restarts):")
for T in (4, 5):
    r = {k: col(b, "pfeas", T=T, k=k) for k in (1, 2, 4, 8, 16)}; rr = col(b, "r_pfeas", T=T, k=1)
    out(f"- T={T} (n={len(rr)}): " + ", ".join(f"k={k}: {v.mean():.3f}" for k, v in r.items()) +
        f"; random {rr.mean():.3f}; ratio k=2 {r[2].mean() / rr.mean():.2f} -> k=16 {r[16].mean() / rr.mean():.2f}; "
        f"2 vs 16 Wilcoxon p={pf(wilcoxon_p(r[16], r[2]))}")

# RQ5: XY mixer
x = load_csv("results_xy.csv")
out("\n## Table VII - standard vs XY mixer (30 instances, mean)")
out("| p | Pfeas std | Pfeas XY | Pasg std | Pasg XY |\n|---|---|---|---|---|")
X = {}
for p in (1, 2, 3):
    k = {n: col(x, n, p=p) for n in ("std_pfeas", "xy_pfeas", "std_pasg", "xy_pasg", "sub_pfeas", "sub_pasg", "full_pfeas", "full_pasg")}
    X[p] = k
    out(f"| {p} | {k['std_pfeas'].mean():.3f} | {k['xy_pfeas'].mean():.3f} | {k['std_pasg'].mean():.4f} | {k['xy_pasg'].mean():.4f} |")
out(f"| Random (subspace) | {X[1]['sub_pfeas'].mean():.3f} | | {X[1]['sub_pasg'].mean():.4f} | |")
out(f"| Random (full) | {X[1]['full_pfeas'].mean():.3f} | | {X[1]['full_pasg'].mean():.4f} | |")
for p in (1, 2, 3):
    k = X[p]
    out(f"- p={p}: XY vs subspace-random: Pfeas x{k['xy_pfeas'].mean() / k['sub_pfeas'].mean():.2f} "
        f"(better on {int((k['xy_pfeas'] > k['sub_pfeas']).sum())}/30, p={pf(wilcoxon_p(k['xy_pfeas'], k['sub_pfeas']))}), "
        f"Pasg x{k['xy_pasg'].mean() / k['sub_pasg'].mean():.2f} (better on {int((k['xy_pasg'] > k['sub_pasg']).sum())}/30, "
        f"p={pf(wilcoxon_p(k['xy_pasg'], k['sub_pasg']))}); XY vs standard Pfeas p={pf(wilcoxon_p(k['xy_pfeas'], k['std_pfeas']))}")
N["xy"] = {p: dict(xy=X[p]["xy_pfeas"].mean(), sub=X[p]["sub_pfeas"].mean()) for p in (1, 2, 3)}

# RQ6: tight capacity
t = load_csv("results_tight.csv")
out("\n## Table VIII - tight-capacity family (R=2)")
out("| T | p | inst | Pfeas (ratio) | Pasg (ratio) | SA optimal |\n|---|---|---|---|---|---|")
TT = {}
for T, p in [(4, 1), (4, 2), (4, 3), (5, 2)]:
    r = [y for y in t if y["T"] == T and y["p"] == p]
    pfe, rp = np.array([y["pfeas"] for y in r]), np.array([y["r_pfeas"] for y in r])
    pa, ra = np.array([y["pasg"] for y in r]), np.array([y["r_pasg"] for y in r])
    so = int(sum(y["sa_opt"] for y in r))
    out(f"| {T} | {p} | {len(r)} | {pfe.mean():.4f} ({pfe.mean() / rp.mean():.2f}) | {pa.mean():.4f} ({pa.mean() / ra.mean():.2f}) | {so}/{len(r)} |")
    out(f"  - QAOA Pfeas > random on {int((pfe > rp).sum())}/{len(r)}, Wilcoxon p={pf(wilcoxon_p(pfe, rp))}; "
        f"SA gap mean {np.mean([y['sa_gap'] for y in r]):.2f}% max {max(y['sa_gap'] for y in r):.1f}%; greedy gap mean {np.mean([y['greedy_gap'] for y in r]):.2f}%")
    TT[f"{T}_{p}"] = dict(n=len(r), ratio=pfe.mean() / rp.mean(), sa_opt=so)
    if p == 2 or (T == 4 and p == 3):
        for y in r:
            if not y["sa_opt"]:
                # shots needed to see the optimum at least once with 99% confidence
                shots = math.log(0.01) / math.log(1 - y["pasg"])
                out(f"  - SA failed on seed {int(y['seed'])} (gap {y['sa_gap']:.1f}%): QAOA Pasg={100 * y['pasg']:.2f}% vs random {100 * y['r_pasg']:.2f}%; "
                    f"~{shots:.0f} shots for 99% confidence vs 2^T={2 ** int(T)} assignments to enumerate")
N["tight"] = TT

# RQ7: noise
nz = load_csv("results_noise.csv")
out("\n## Noise study (p=2, 20 instances, 60 trajectories)")
base = col(nz, "pfeas", eps=0)
for e in (0, 0.002, 0.005, 0.01, 0.02, 0.05):
    pe, ra, rr = col(nz, "pfeas", eps=e), col(nz, "ratio", eps=e), col(nz, "r_pfeas", eps=e)
    extra = f", p vs noiseless={pf(wilcoxon_p(pe, base))}" if e else ""
    out(f"- eps={e}: Pfeas {pe.mean():.4f}, approx ratio {ra.mean():.3f}, x random {pe.mean() / rr.mean():.2f}, beats random on {int((pe > rr).sum())}/20{extra}")
N["noise"] = {e: dict(pfeas=col(nz, "pfeas", eps=e).mean(), ratio=col(nz, "pfeas", eps=e).mean() / col(nz, "r_pfeas", eps=e).mean()) for e in (0, 0.01, 0.05)}
open(os.path.join(RES, "results_summary.md"), "w").write("\n".join(L))
json.dump(N, open(os.path.join(RES, "numbers.json"), "w"), indent=1, default=float)
