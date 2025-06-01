#!/usr/bin/env python3
#!/usr/bin/env python3
"""
Grouped boxplot of energy consumption for Raspberry Pi benchmarks.

This script generates a boxplot of energy consumption data, grouped by one of:
    - Python version
    - Operating system
    - Raspberry Pi model

It aggregates energy values from multiple CSV files and visualizes distributions
with mean annotations.

Usage:
    python3 boxplot.py <group>

Arguments:
    group      Grouping factor for the boxplot (one of: python, os, rpi)

Input:
    - CSV files named: results_<rpi>_<os>_python<version>.csv
    - Located in ../../results/
    - Each file should contain duration and energy data in the last two columns

Output:
    - PNG image saved to ./figures/energy_boxplot_by_<group>.png
"""
import glob
import os
import re
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def parse_filename(fname):
    m = re.match(r"../../results/results_(.+?)_(.+?)_python(\d+\.\d+)\.csv$", fname)
    return m.groups() if m else None


def main():
    parser = argparse.ArgumentParser(description='Generate box plot of energy consumption.')
    parser.add_argument('group', choices=['os', 'python', 'rpi'],
                        help='Grouping for boxplot: os, python, or rpi')
    args = parser.parse_args()
    group = args.group

    files = glob.glob("../../results/results_*_python*.csv")
    if not files:
        print("No benchmark CSV files found.")
        return

    allowed_os = {'Alpine', 'Ubuntu', 'FreeBSD', 'Manjaro'}
    values = {}

    for path in files:
        parsed = parse_filename(path)
        if not parsed:
            continue
        rpi_model, os_name, pyver = parsed
        if os_name not in allowed_os:
            continue
        df = pd.read_csv(path)
        series = df.iloc[:, -1].dropna().tolist()

        if group == 'os':
            key = os_name
        elif group == 'python':
            key = pyver
        elif group == 'rpi':
            key = rpi_model
        else:
            continue

        values.setdefault(key, []).extend(series)

    if not values:
        print("No data found for the specified grouping.")
        return

    keys = sorted(values.keys(), key=lambda k: float(k) if group == 'python' else k)
    if group == 'python' and '3.9' in keys:
        keys.remove('3.9')
        keys = ['3.9'] + keys

    data = [values[k] for k in keys]
    if group == 'rpi':
        labels = [k.replace("RPi3B", "RPi3B+") for k in keys]
    else:
        labels = [f"py{k}" if group == 'python' else k for k in keys]

    xlabels = {
        'os': "Operating system",
        'python': "Python version",
        'rpi': "Raspberry Pi"
    }

    fig, ax = plt.subplots(figsize=(9, 5))
    bp = ax.boxplot(data, labels=labels, widths=0.4, patch_artist=True, showfliers=False)

    for box in bp['boxes']:
        box.set(facecolor='white', edgecolor='black', linewidth=1.5)

    ax.grid(True, axis='y', linestyle='--', linewidth=0.5, color='grey', alpha=0.6)

    for i, vals in enumerate(data, start=1):
        mean_val = np.mean(vals)
        offset = (max(vals) - min(vals)) * 0.040
        ax.text(i, mean_val + offset, f"μ={mean_val:.2f}",
                ha='center', va='bottom', fontsize='small', color='blue',
                bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.2'))

    ax.set_xlabel(xlabels[group])
    ax.set_ylabel('Energy consumption (J)')
    ax.set_title(f"Energy consumption by {xlabels[group]}")
    plt.tight_layout()

    outfn = f"./figures/energy_boxplot_by_{group}.png"
    fig.savefig(outfn, dpi=150)
    print(f"Saved box plot to {outfn}")


if __name__ == '__main__':
    main()
