#!/usr/bin/env python3
"""
Compute average percent decrease in energy consumption across benchmarks:
1. From worst to best Python version per (pi, distro).
2. From worst to best OS per (pi, python).
3. From RPi3B+ to RPi4B per (distro, python).
"""

import glob
import os
import re
import pandas as pd
import numpy as np


def parse_filename(fname):
    m = re.match(r"../../results/results_(.+?)_(.+?)_python(\d+\.\d+)\.csv$", fname)
    return m.groups() if m else None


def compute_average_energy(path):
    df = pd.read_csv(path)
    return df.iloc[:, -1].mean()


def percent_decrease(worst, best):
    return 100 * (worst - best) / worst if worst > 0 else 0


def main():
    files = glob.glob("../../results/results_*_python*.csv")
    data = []

    for path in files:
        parsed = parse_filename(path)
        if not parsed:
            continue
        pi, distro, pyver = parsed
        energy = compute_average_energy(path)
        data.append({'pi': pi, 'distro': distro, 'python': pyver, 'energy': energy})

    df = pd.DataFrame(data)

    # 1. Python version decrease per (pi, distro)
    dec_py = []
    for (pi, distro), group in df.groupby(['pi', 'distro']):
        if len(group) > 1:
            worst = group['energy'].max()
            best = group['energy'].min()
            dec_py.append(percent_decrease(worst, best))
    avg_dec_py = np.mean(dec_py)

    # 2. OS decrease per (pi, python)
    dec_os = []
    for (pi, pyver), group in df.groupby(['pi', 'python']):
        if len(group) > 1:
            worst = group['energy'].max()
            best = group['energy'].min()
            dec_os.append(percent_decrease(worst, best))
    avg_dec_os = np.mean(dec_os)

    # 3. RPi3B+ to RPi4B per (distro, python)
    dec_rpi = []
    for (distro, pyver), group in df.groupby(['distro', 'python']):
        group = group.set_index('pi')
        if 'RPi3B+' in group.index and 'RPi4B' in group.index:
            energy_rpi3 = group.loc['RPi3B+', 'energy']
            energy_rpi4 = group.loc['RPi4B', 'energy']
            if isinstance(energy_rpi3, pd.Series):
                energy_rpi3 = energy_rpi3.mean()
            if isinstance(energy_rpi4, pd.Series):
                energy_rpi4 = energy_rpi4.mean()
            dec_rpi.append(percent_decrease(energy_rpi3, energy_rpi4))
    avg_dec_rpi = np.mean(dec_rpi) if dec_rpi else 0

    print(f"Avg % decrease (Python version, per Pi+OS): {avg_dec_py:.2f}%")
    print(f"Avg % decrease (OS, per Pi+Python): {avg_dec_os:.2f}%")
    print(f"Avg % decrease (RPi3B+ to RPi4B, per OS+Python): {avg_dec_rpi:.2f}%")


if __name__ == '__main__':
    main()
