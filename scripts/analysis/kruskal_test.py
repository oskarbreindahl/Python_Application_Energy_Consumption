#!/usr/bin/env python3
"""
Statistical analysis of energy consumption across Raspberry Pi benchmarks.

This script performs a Kruskal-Wallis test followed by pairwise Mann-Whitney U tests
(with Bonferroni correction) to compare energy consumption grouped by one of:

    --factor python   Compare across Python versions
    --factor os       Compare across operating systems
    --factor rpi      Compare across Raspberry Pi models

Usage:
    python3 script.py --factor <python|os|rpi>

Input:
    - CSV files named as: results_<rpi>_<os>_python<version>.csv
    - Located in ../../results/

Output:
    - Statistical test results printed to stdout
"""

import glob
import os
import re
import argparse

import numpy as np
import pandas as pd
from scipy.stats import kruskal, mannwhitneyu, rankdata
from statsmodels.stats.multitest import multipletests


def parse_filename(fname):
    m = re.match(r"../../results/results_(.+?)_(.+?)_python(\d+\.\d+)\.csv$", fname)
    return m.groups() if m else None


def main():
    parser = argparse.ArgumentParser(description='Kruskal-Wallis test for energy consumption data')
    parser.add_argument('--factor', required=True,
                        choices=['python', 'os', 'rpi'],
                        help='Grouping factor: python, os, or rpi')
    args = parser.parse_args()
    factor = args.factor

    # Collect data
    records = []
    for path in glob.glob("../../results/results_*_python*.csv"):
        parsed = parse_filename(path)
        if not parsed:
            continue
        pi, os_name, pyver = parsed
        df = pd.read_csv(path)
        values = df.iloc[:, -1]  # Energy consumption
        label = {'python': pyver, 'os': os_name, 'rpi': pi}[factor]
        for v in values.dropna():
            records.append({'value': v, factor: label})

    data = pd.DataFrame(records)
    if data.empty:
        print(f"No data found for factor={factor}")
        return

    # Prepare groups
    grouped = data.groupby(factor)
    groups = [grp['value'].values for _, grp in grouped]
    names = [name for name, _ in grouped]

    # Kruskal-Wallis
    h_stat, p_val = kruskal(*groups)
    print("\n=== Kruskal-Wallis Test ===")
    print(f"H = {h_stat:.4f}, p = {p_val:.4g}")

    # Pairwise Mann-Whitney U tests
    print("\n=== Pairwise Mann-Whitney U Tests (Bonferroni corrected) ===")
    comparisons = []
    pvals = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            group1 = groups[i]
            group2 = groups[j]
            combined = np.concatenate([group1, group2])
            ranks = rankdata(combined)
            r1 = ranks[:len(group1)]
            r2 = ranks[len(group1):]
            mean_rank1 = np.mean(r1)
            mean_rank2 = np.mean(r2)
            u_stat, p = mannwhitneyu(group1, group2, alternative='two-sided')
            comparisons.append((names[i], names[j], u_stat, mean_rank1, mean_rank2))
            pvals.append(p)

    reject, p_adj, _, _ = multipletests(pvals, method='bonferroni')
    for (n1, n2, u, mr1, mr2), p0, p1, rej in zip(comparisons, pvals, p_adj, reject):
        better = n1 if mr1 < mr2 else n2  # lower mean rank is better
        print(f"{n1} vs {n2}: U={u:.2f}, p_adj={p1:.4g}, significant={rej}, "
              f"mean_ranks=({n1}: {mr1:.2f}, {n2}: {mr2:.2f}), better={better}")


if __name__ == '__main__':
    main()
 