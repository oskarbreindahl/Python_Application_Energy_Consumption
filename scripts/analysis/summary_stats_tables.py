#!/usr/bin/env python3
"""
Generate summary statistics tables for Raspberry Pi benchmark data.

This script computes summary statistics (q₀–q₄, μ, σ) for three metrics:
    - duration (seconds)
    - draw (average power, derived from energy / duration)
    - consumption (energy in joules)

You can generate individual CSV files for each Pi model and metric or a combined
CSV file summarizing all models and metrics.

Usage:
    python3 summary_stats_tables.py RPi4B --metric consumption
    python3 summary_stats_tables.py RPi3B+ RPi4B --all

Input:
    - CSV files named: results_<rpi>_<os>_python<version>.csv
    - Located in ../../results/
    - Must contain columns: 'Duration' and 'Energy consumption'

Output:
    - Individual CSVs: summary_stats_<pi>_<metric>.csv
    - Or combined CSV: summary_stats_combined.csv
"""

import glob
import re
import argparse

import numpy as np
import pandas as pd
from packaging.version import parse as parse_version


def parse_filename(fname):
    m = re.match(r"../../results/results_(.+?)_(.+?)_python(\d+\.\d+)\.csv$", fname)
    return m.groups() if m else None


def compute_summary(vals):
    arr = np.array(vals)
    return [
        np.min(arr),
        np.percentile(arr, 25),
        np.median(arr),
        np.percentile(arr, 75),
        np.max(arr),
        np.mean(arr),
        np.std(arr, ddof=1)
    ]


def build_table(pi_target, metric):
    colmap = {
        'draw': ('Energy consumption', 'Duration'),
        'duration': 'Duration',
        'consumption': 'Energy consumption'
    }

    records = []
    for path in glob.glob("../../results/results_*_python*.csv"):
        parsed = parse_filename(path)
        if not parsed:
            continue
        pi, os_name, pyver = parsed
        if pi != pi_target:
            continue
        df = pd.read_csv(path)
        if isinstance(colmap[metric], tuple):
            col1, col2 = colmap[metric]
            if col1 not in df.columns or col2 not in df.columns:
                raise ValueError(f"Required columns not found in {path}")
            vals = (df[col1] / df[col2]).dropna().tolist()
        else:
            if colmap[metric] not in df.columns:
                raise ValueError(f"Column '{colmap[metric]}' not found in {path}")
            vals = df[colmap[metric]].dropna().tolist()
        records.append({'python': pyver, 'os': os_name, 'vals': vals})

    if not records:
        raise ValueError(f"No data for Pi model {pi_target}")

    grouped = {}
    for rec in records:
        key = (rec['python'], rec['os'])
        grouped.setdefault(key, []).extend(rec['vals'])

    rows = []
    for (pyver, os_name), vals in grouped.items():
        stats = compute_summary(vals)
        rows.append([pyver, os_name] + stats)

    cols = ['python','os','q0','q1','q2','q3','q4','μ','σ']
    df = pd.DataFrame(rows, columns=cols)
    df.sort_values(['python','os'], key=lambda col: col.map(lambda v: parse_version(v) if col.name=='python' else v), inplace=True)
    return df


def save_table_to_csv(pi_model, df, metric):
    df['label'] = df['python'] + '|' + df['os']
    df = df.set_index('label')[['q0','q1','q2','q3','q4','μ','σ']].T
    outfn = f'summary_stats_{pi_model}_{metric}.csv'
    df.to_csv(outfn)
    print(f"Saved CSV for {pi_model} and metric {metric} to {outfn}")


def save_combined_table_to_csv(pi_models, metrics):
    all_rows = []

    for pi_model in pi_models:
        for metric in metrics:
            try:
                df = build_table(pi_model, metric)
                df['label'] = df['python'] + '|' + df['os']
                stats_df = df.set_index('label')[['q0','q1','q2','q3','q4','μ','σ']].T
                stats_df.index = [f"{metric}|{pi_model}|{idx}" for idx in stats_df.index]
                all_rows.append(stats_df)
            except ValueError as e:
                print(f"Skipping {pi_model} {metric}: {e}")

    if not all_rows:
        print("No data collected.")
        return

    combined_df = pd.concat(all_rows)
    outfn = 'summary_stats_combined.csv'
    combined_df.to_csv(outfn)
    print(f"Saved combined CSV for all Pi models and metrics to {outfn}")


def main():
    parser = argparse.ArgumentParser(description='Generate summary tables for each Pi model and metric as CSVs')
    parser.add_argument('pi_models', nargs='*', help='Raspberry Pi models, e.g. RPi4B RPi3B+')
    parser.add_argument('--metric', choices=['duration', 'draw', 'consumption'], help='Metric to analyze')
    parser.add_argument('--all', action='store_true', help='Aggregate all metrics and Pi models into one CSV')
    args = parser.parse_args()

    if args.all:
        if not args.pi_models:
            args.pi_models = ['RPi3B+', 'RPi4B']
        save_combined_table_to_csv(args.pi_models, ['duration', 'draw', 'consumption'])
    else:
        if not args.metric:
            raise ValueError("Specify --metric when not using --all")
        for pi_model in args.pi_models:
            df = build_table(pi_model, args.metric)
            save_table_to_csv(pi_model, df, args.metric)


if __name__ == '__main__':
    main()
