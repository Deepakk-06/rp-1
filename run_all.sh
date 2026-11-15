#!/bin/bash
# Author: Deepak K | 2026
# run_all.sh: runs every experiment one after another (about 50 minutes on one CPU core)
# id: e9aa03d21ff40c7ce99c453cea3620df
cd "$(dirname "$0")"
# the file each script writes, used to skip experiments that already finished
declare -A OUT=( [exp_classical]=results_quboSA.csv [exp_hard]=results_hard.csv [exp_depth_sweep]=results_penalty.csv \
 [exp_xy]=results_xy.csv [exp_noise]=results_noise.csv [exp_tight_qaoa]=results_tight.csv [exp_scaling10]=results_budget.csv )
for s in exp_classical exp_hard exp_depth_sweep exp_xy exp_noise exp_tight_qaoa exp_scaling10; do
  # already done, don't redo it
  if [ -f results/${OUT[$s]} ]; then echo "skip $s"; continue; fi
  echo "=== $s $(date)"; python3 $s.py
done
echo ALLDONE
