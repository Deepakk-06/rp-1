# qaqo_dk_6: QAOA benchmark for multi-robot delivery assignment

Simulation code, result files and figures for "Benchmarking QAOA for Capacity-Constrained, Traffic-Aware Multi-Robot Delivery Assignment: A Statistical Simulation Study".

The code and results were rebuilt after the original files were lost. They follow the paper's method, and the numbers are regenerated, so a few differ slightly from the first draft (see results/results_summary.md).

## Run
Needs Python 3, numpy, scipy and matplotlib.

    python3 worked_example.py   # section 3.4 check, ground energy should be 3
    bash run_all.sh             # all experiments, about 50 min on one core
    python3 analyze.py          # tables and p-values
    python3 make_figs.py        # figures 1 to 9

## Cite
Repository: https://github.com/Deepakk-06/rp-1

See CITATION.cff. Released under the MIT License (see LICENSE and NOTICE.txt).
