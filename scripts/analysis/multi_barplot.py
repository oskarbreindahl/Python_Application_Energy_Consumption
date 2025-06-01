#!/usr/bin/env python3
"""
Generate grouped bar plot of average energy consumption across Raspberry Pi models and Python versions.

This script creates a grouped bar plot for energy consumption (in joules), grouped by (Pi model, Python version),
with OS differentiated by bar color.

Usage:
    python3 multi_barplot.py

Input:
    - CSV files named: results_<rpi>_<os>_python<version>.csv
    - Located in ../../results/

Output:
    - A PNG image saved as: ./figures/consumption_barplot_all_pis.png
"""

import glob
import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch


def parse_filename(fname):
    m = re.match(r"../../results/results_(.+?)_(.+?)_python(\d+\.\d+)\.csv$", fname)
    return m.groups() if m else None


def compute_avg_consumption(path):
    df = pd.read_csv(path)
    return df.iloc[:, -1].mean()  # Last column is energy consumption


def main():
    files = glob.glob("../../results/results_*_python*.csv")
    records = []
    for path in files:
        parsed = parse_filename(path)
        if not parsed:
            continue
        pi, distro, pyver = parsed
        val = compute_avg_consumption(path)
        records.append({'pi': pi, 'distro': distro, 'python': pyver, 'value': val})
    df = pd.DataFrame(records)

    pis = sorted(df['pi'].unique())
    pythons = sorted(df['python'].unique(), key=lambda v: float(v))
    if '3.9' in pythons:
        pythons.remove('3.9')
        pythons = ['3.9'] + pythons
    distros = ['Ubuntu', 'Alpine', 'Manjaro', 'FreeBSD']

    colors = {
        'Alpine': '#4169E1',
        'Ubuntu': '#E95420',
        'FreeBSD': '#fbbc04',
        'Manjaro': '#9900ff'
    }

    x_positions = []
    values = []
    x_groups = []
    current = 0
    gap = 1.0
    width = 0.8

    for pi in pis:
        for pv in pythons:
            distro_vals = []
            for d in distros:
                subset = df[(df['pi'] == pi) & (df['python'] == pv) & (df['distro'] == d)]
                if not subset.empty:
                    distro_vals.append((d, subset['value'].iloc[0]))
            sorted_distros = [d for d, _ in sorted(distro_vals, key=lambda x: x[1], reverse=True)]
            for d in sorted_distros:
                x_positions.append(current)
                values.append(next(v for dd, v in distro_vals if dd == d))
                x_groups.append((pi, pv))
                current += 1
            current += 0.2
        current += gap

    group_centers = {}
    for idx, (pi, pv) in enumerate(x_groups):
        group_centers.setdefault((pi, pv), []).append(x_positions[idx])

    ticks = []
    labels = []
    for pi in pis:
        for pv in pythons:
            positions = group_centers.get((pi, pv), [])
            if positions:
                ticks.append(np.mean(positions))
                labels.append(f"py{pv}")

    fig, ax = plt.subplots(figsize=(max(12, current * 0.2), 6))

    ylim = (0, max(values) * 1.15)
    ax.set_ylim(ylim)

    angle_rad = np.deg2rad(45)
    dx = -1 * np.cos(angle_rad)
    dy = 0.2 * np.sin(angle_rad) * (ylim[1] / 10)

    for idx, xpos in enumerate(x_positions):
        pi, pv = x_groups[idx]
        d = df[(df['pi'] == pi) & (df['python'] == pv) & (df['value'] == values[idx])]['distro'].iloc[0]
        ax.bar(xpos, values[idx], width=width, color=colors[d], edgecolor='black')
        ax.annotate(f"{values[idx]:.2f}",
                    xy=(xpos + width / 2, values[idx]),
                    xytext=(xpos + width / 2 + dx, values[idx] + dy),
                    textcoords='data',
                    ha='left', va='bottom',
                    fontsize=9, rotation=60,
                    bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))

    ax.set_xticks(ticks)
    ax.set_xticklabels(labels, rotation=45, ha='right')

    ax.grid(True, axis='y', linestyle='--', linewidth=0.5, color='grey', alpha=0.6)

    divider_positions = []
    pos = 0
    for pi in pis:
        count = sum(1 for g in x_groups if g[0] == pi)
        pos += count + 1.5
        divider_positions.append(pos - 0.5)
        pos += gap
    for dpos in divider_positions[:-1]:
        ax.axvline(dpos, color='grey', linestyle='--', linewidth=1)

    pi_centers = []
    pos = 0
    for pi in pis:
        count = sum(1 for g in x_groups if g[0] == pi)
        center = pos + (count - 1) / 2
        pi_centers.append((center, pi))
        pos += count + gap
    for xctr, pi in pi_centers:
        ax.text(xctr, ylim[1] * 1.02, pi, ha='center', va='bottom', fontsize='medium')

    ax.set_ylabel('Average Energy Consumption (J)')
    ax.set_title("")

    handles = [Patch(facecolor=colors[d], label=d) for d in distros]
    ax.legend(handles=handles, title='OS', loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=4)

    plt.tight_layout()
    outfn = "./figures/consumption_barplot_all_pis.png"
    fig.savefig(outfn, dpi=150)
    print(f"Saved combined bar plot to {outfn}")


if __name__ == '__main__':
    main()
