# Author: Deepak K | 2026
# make_figs.py: regenerates Figures 1 to 9 from the csv files in results/
import os, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from exp_common import load_csv, boot_ci

# pngs land in figures/ next to the scripts
FIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures"); os.makedirs(FIG, exist_ok=True)
plt.rcParams.update({"font.family": "serif", "font.size": 8, "axes.titlesize": 9, "figure.dpi": 150, "savefig.bbox": "tight"})
BLUE, ORANGE, GREEN, RED = "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"
col = lambda rows, k, **f: np.array([r[k] for r in rows if all(r[a] == b for a, b in f.items())])
def save(n): plt.savefig(os.path.join(FIG, n + ".png")); plt.close()

# load every result file once at the top
d, pen, sc = load_csv("results_depth.csv"), load_csv("results_penalty.csv"), load_csv("results_scaling.csv")
xy, tg, nz, hd, bd = load_csv("results_xy.csv"), load_csv("results_tight.csv"), load_csv("results_noise.csv"), load_csv("results_hard.csv"), load_csv("results_budget.csv")


# Fig 2: the pipeline boxes
fig, ax = plt.subplots(figsize=(7, 0.9)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 1)
labels = ["Random\ninstance", "QUBO\nencoding", "QAOA / SA /\ngreedy / exact", "Decode,\ncheck C1-C2"]
for i, t in enumerate(labels):
    x0 = 0.1 + i * 2.5
    ax.add_patch(FancyBboxPatch((x0, 0.15), 1.9, 0.7, boxstyle="round,pad=0.02", fc="white", ec="black"))
    ax.text(x0 + 0.95, 0.5, t, ha="center", va="center")
    if i < 3: ax.annotate("", xy=(x0 + 2.45, 0.5), xytext=(x0 + 1.95, 0.5), arrowprops=dict(arrowstyle="->"))
save("fig2_pipeline")


# Fig 3: gap to the exact optimum on the hard family
fig, ax = plt.subplots(figsize=(4.6, 3.2)); sizes = [(4, 8), (6, 12), (8, 16), (10, 20)]
for j, (key, c) in enumerate([("greedy_gap", ORANGE), ("sa_gap", GREEN)]):
    # > -0.5 drops the -1 'no solution' marker but keeps the tiny negatives that come from float rounding
    data = [[r[key] for r in hd if r["R"] == R and r["feasible"] == 1 and r[key] > -0.5] for R, T in sizes]
    bp = ax.boxplot(data, positions=np.arange(4) + (j - 0.5) * 0.32, widths=0.28, patch_artist=True, showfliers=False)
    for b in bp["boxes"]: b.set_facecolor(c); b.set_alpha(0.7)
    ax.plot([], [], color=c, lw=6, label=["Greedy", "SA"][j])
ax.set_xticks(range(4)); ax.set_xticklabels([f"{R}x{T}" for R, T in sizes]); ax.set_xlabel("Robots x deliveries")
ax.set_ylabel("Gap to exact optimum (%)"); ax.legend(loc="upper left"); save("fig3_hard_gap")


# Fig 4: QAOA vs depth, grey lines are single instances and blue is the mean with a 95% interval
fig, axs = plt.subplots(1, 3, figsize=(7.4, 2.4))
for ax, (k, ttl) in zip(axs, [("ratio", "Approximation ratio"), ("pfeas", "P(feasible)"), ("popt", "P(optimal)")]):
    seeds = sorted({r["seed"] for r in d})
    for s in seeds: ax.plot([1, 2, 3], [col(d, k, seed=s, p=p)[0] for p in (1, 2, 3)], color="0.8", lw=0.7)
    m = [col(d, k, p=p).mean() for p in (1, 2, 3)]; ci = [boot_ci(col(d, k, p=p)) for p in (1, 2, 3)]
    ax.errorbar([1, 2, 3], m, yerr=[[a - c[0] for a, c in zip(m, ci)], [c[1] - a for a, c in zip(m, ci)]], color=BLUE, marker="o", capsize=3, label="mean, 95% CI")
    if k != "ratio": ax.axhline(col(d, "r_" + k, p=1).mean(), color="0.4", ls="--", lw=1, label="random sampling")
    ax.set_title(ttl); ax.set_xticks([1, 2, 3]); ax.set_xlabel("QAOA depth p")
    if k == "pfeas": ax.legend(fontsize=6)
plt.tight_layout(); save("fig4_depth")


# Fig 5: penalty weight sweep
fig, axs = plt.subplots(1, 2, figsize=(6.6, 2.6)); A = [0.5, 1, 2, 4, 8]
for ax, (k, rk, ttl) in zip(axs, [("pfeas", "r_pfeas", "P(feasible)"), ("pasg", "r_pasg", "P(optimal assignment)")]):
    for p, c in zip((1, 2, 3), ["#aec7e8", "#6baed6", "#08519c"]):
        m = [col(pen, k, a=a, p=p).mean() for a in A]; se = [col(pen, k, a=a, p=p).std(ddof=1) / np.sqrt(20) for a in A]
        ax.errorbar(range(5), m, yerr=se, color=c, marker="o", capsize=2, label=f"p={p}")
    ax.axhline(col(pen, rk, a=2, p=1).mean(), color="0.4", ls="--", label="random")
    ax.set_xticks(range(5)); ax.set_xticklabels(A); ax.set_xlabel("Penalty weight a (A = a max c)"); ax.set_title(ttl)
axs[0].legend(fontsize=6); plt.tight_layout(); save("fig5_penalty")


# Fig 6: runtime on a log scale and feasibility against qubit count
fig, axs = plt.subplots(1, 2, figsize=(7, 2.7)); Ts = (3, 4, 5, 6)
nq = [col(sc, "n", T=T).mean() for T in Ts]
for k, lab, c, mk in [("t_qaoa", "QAOA (simulated)", BLUE, "o"), ("t_sa", "Simulated annealing", ORANGE, "s"), ("t_exact", "Exact enumeration", GREEN, "^")]:
    axs[0].errorbar(nq, [col(sc, k, T=T).mean() for T in Ts], yerr=[col(sc, k, T=T).std(ddof=1) for T in Ts], color=c, marker=mk, label=lab, capsize=2)
axs[0].set_yscale("log"); axs[0].set_xlabel("Number of qubits n"); axs[0].set_ylabel("Wall-clock time per instance (s)"); axs[0].set_title("Runtime"); axs[0].legend(fontsize=6)
m = [col(sc, "pfeas", T=T).mean() for T in Ts]; s_ = [col(sc, "pfeas", T=T).std(ddof=1) for T in Ts]
axs[1].plot(nq, [col(sc, "r_pfeas", T=T).mean() for T in Ts], "x--", color="0.4", label="random sampling")
axs[1].errorbar(nq, m, yerr=s_, color=BLUE, marker="o", capsize=2, label="QAOA, p=2 (mean +/- s.d.)")
axs[1].set_xlabel("Number of qubits n"); axs[1].set_ylabel("P(feasible)"); axs[1].set_title("Feasible-sample probability"); axs[1].legend(fontsize=6)
plt.tight_layout(); save("fig6_scaling")


fig, axs = plt.subplots(1, 2, figsize=(7, 2.6))
# Fig 7: standard vs XY mixer, both random baselines drawn as lines
for ax, (ks, kx, rs, rf, ttl) in zip(axs, [("std_pfeas", "xy_pfeas", "sub_pfeas", "full_pfeas", "P(feasible)"), ("std_pasg", "xy_pasg", "sub_pasg", "full_pasg", "P(optimal assignment)")]):
    for j, (k, c, lab) in enumerate([(ks, BLUE, "Standard X mixer"), (kx, RED, "XY (one-hot) mixer")]):
        m = [col(xy, k, p=p).mean() for p in (1, 2, 3)]; ci = [boot_ci(col(xy, k, p=p)) for p in (1, 2, 3)]
        ax.bar(np.arange(3) + (j - 0.5) * 0.38, m, 0.36, color=c, label=lab,
               yerr=[[a - q[0] for a, q in zip(m, ci)], [q[1] - a for a, q in zip(m, ci)]], capsize=2)
    ax.axhline(col(xy, rf, p=1).mean(), color="0.4", ls="--", label="random, full space")
    ax.axhline(col(xy, rs, p=1).mean(), color="0.2", ls=":", label="random, one-hot subspace")
    ax.set_xticks(range(3)); ax.set_xticklabels([1, 2, 3]); ax.set_xlabel("QAOA depth p"); ax.set_title(ttl)
axs[0].legend(fontsize=6); plt.tight_layout(); save("fig7_xy")


# Fig 8: ratio to random sampling per instance, the dots are the instances
def ratios(rows, key, rkey, **f):
    return np.array([r[key] / r[rkey] for r in rows if all(r[a] == b for a, b in f.items())])
groups = [("Standard,\nT=4, p=3", col(d, "pfeas", p=3) / col(d, "r_pfeas", p=3), col(d, "pasg", p=3) / col(d, "r_pasg", p=3)),
          ("Tight,\nT=4, p=3", ratios(tg, "pfeas", "r_pfeas", T=4, p=3), ratios(tg, "pasg", "r_pasg", T=4, p=3)),
          ("Tight,\nT=5, p=2", ratios(tg, "pfeas", "r_pfeas", T=5, p=2), ratios(tg, "pasg", "r_pasg", T=5, p=2))]
fig, axs = plt.subplots(1, 2, figsize=(7, 2.6)); rng = np.random.default_rng(0)
for ax, (j, ttl) in zip(axs, [(1, "P(feasible) / random"), (2, "P(optimal assignment) / random")]):
    for i, g in enumerate(groups):
        v = g[j]; lo, hi = boot_ci(v)
        ax.bar(i, v.mean(), color=["0.5", RED, "#8b1a1a"][i], width=0.6)
        ax.errorbar(i, v.mean(), yerr=[[v.mean() - lo], [hi - v.mean()]], color="k", capsize=3)
        ax.scatter(i + rng.uniform(-0.2, 0.2, len(v)), v, s=4, color="k", alpha=0.6)
    ax.axhline(1, color="0.4", ls="--"); ax.set_xticks(range(3)); ax.set_xticklabels([g[0] for g in groups]); ax.set_ylabel("ratio to random sampling"); ax.set_title(ttl)
plt.tight_layout(); save("fig8_tight")


# Fig 9: effect of noise
E = (0, 0.002, 0.005, 0.01, 0.02, 0.05); fig, axs = plt.subplots(1, 2, figsize=(7, 2.5))
for ax, (k, ttl) in zip(axs, [("pfeas", "P(feasible)"), ("ratio", "Approximation ratio")]):
    m = [col(nz, k, eps=e).mean() for e in E]; ci = [boot_ci(col(nz, k, eps=e)) for e in E]
    ax.errorbar(range(6), m, yerr=[[a - c[0] for a, c in zip(m, ci)], [c[1] - a for a, c in zip(m, ci)]], color=BLUE, marker="o", capsize=3, label="QAOA, p=2 (mean, 95% CI)")
    ax.axhline(col(nz, "r_pfeas", eps=0).mean() if k == "pfeas" else 0, color="0.4", ls="--", label="random sampling")
    ax.set_xticks(range(6)); ax.set_xticklabels(E); ax.set_xlabel("Pauli error probability per qubit per layer"); ax.set_title(ttl); ax.legend(fontsize=6)
plt.tight_layout(); save("fig9_noise")


# Fig 1: summary panel, always ratio of means
def rom(num, den): return num.mean() / den.mean()
bars = [("Standard, 12-14 q, p=3", rom(col(d, "pfeas", p=3), col(d, "r_pfeas", p=3)), BLUE),
        ("Scaling, 18 q, p=2", rom(col(sc, "pfeas", T=6), col(sc, "r_pfeas", T=6)), "#17becf"),
        ("Tight cap., 12-14 q, p=3", rom(col(tg, "pfeas", T=4, p=3), col(tg, "r_pfeas", T=4, p=3)), RED),
        ("Tight cap., 16-18 q, p=2", rom(col(tg, "pfeas", T=5, p=2), col(tg, "r_pfeas", T=5, p=2)), ORANGE),
        ("XY mixer vs own subspace, p=2", rom(col(xy, "xy_pfeas", p=2), col(xy, "sub_pfeas", p=2)), "#9467bd"),
        ("Noise 5%/qubit/layer, p=2", rom(col(nz, "pfeas", eps=0.05), col(nz, "r_pfeas", eps=0.05)), GREEN)]
fig, axs = plt.subplots(2, 1, figsize=(4.8, 5.4)); ax = axs[0]
for i, (l, v, c) in enumerate(bars):
    ax.barh(i, v, color=c); ax.text(v + 0.03, i, f"{v:.2f}x", va="center", fontweight="bold")
ax.axvline(1, color="0.3", ls="--"); ax.set_yticks(range(len(bars))); ax.set_yticklabels([b[0] for b in bars]); ax.invert_yaxis(); ax.set_xlim(0, 2.4)
ax.set_xlabel("P(feasible): QAOA / random sampling"); ax.set_title("(a) QAOA vs random sampling", fontweight="bold")
ax = axs[1]
for j, (key, c, lab) in enumerate([("greedy_gap", ORANGE, "Greedy"), ("sa_gap", GREEN, "SA")]):
    ax.bar(np.arange(4) + (j - 0.5) * 0.38, [np.mean([r[key] for r in hd if r["R"] == R and r["feasible"] == 1 and r[key] > -0.5]) for R, T in sizes], 0.36, color=c, label=lab)
ax.set_xticks(range(4)); ax.set_xticklabels([f"{R}x{T}" for R, T in sizes]); ax.set_ylabel("mean gap to optimum (%)"); ax.set_xlabel("robots x deliveries (tight capacity)")
ax.set_title("(b) Greedy vs SA, hard family", fontweight="bold"); ax.legend()
plt.tight_layout(); save("fig1_summary")
print("figures done")
