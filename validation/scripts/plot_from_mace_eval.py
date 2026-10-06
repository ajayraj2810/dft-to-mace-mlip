#!/usr/bin/env python3
"""Make parity/error plots from extxyz written by mace_eval_configs."""
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from ase.io import read


def main():
    p = argparse.ArgumentParser()
    p.add_argument("xyz")
    p.add_argument("--output-dir", default="validation_output")
    p.add_argument("--max-force-points", type=int, default=60000)
    args = p.parse_args()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    configs = read(args.xyz, index=":")

    ref_e, pred_e, ref_f, pred_f = [], [], [], []

    for atoms in configs:
        n_atoms = len(atoms)
        ref_e.append(float(atoms.info["REF_energy"]) / n_atoms)
        pred_e.append(float(atoms.info["MACE_energy"]) / n_atoms)
        ref_f.append(np.asarray(atoms.arrays["REF_forces"]).reshape(-1))
        pred_f.append(np.asarray(atoms.arrays["MACE_forces"]).reshape(-1))

    ref_e, pred_e = np.asarray(ref_e), np.asarray(pred_e)
    ref_f, pred_f = np.concatenate(ref_f), np.concatenate(pred_f)

    de = (pred_e - ref_e) * 1000
    df = (pred_f - ref_f) * 1000

    e_rmse = np.sqrt(np.mean(de ** 2))
    e_mae = np.mean(np.abs(de))
    f_rmse = np.sqrt(np.mean(df ** 2))
    f_mae = np.mean(np.abs(df))

    plots = [
        (
            ref_e, pred_e,
            "DFT energy (eV/atom)", "MACE energy (eV/atom)",
            "Energy parity: test set",
            f"RMSE = {e_rmse:.3f} meV/atom\nMAE = {e_mae:.3f} meV/atom",
            "energy_parity.png", None,
        ),
        (
            ref_f, pred_f,
            r"DFT force (eV/$\AA$)", r"MACE force (eV/$\AA$)",
            "Force parity: test set",
            f"RMSE = {f_rmse:.1f} meV/$\\AA$\nMAE = {f_mae:.1f} meV/$\\AA$",
            "force_parity.png", args.max_force_points,
        ),
    ]

    for x, y, xlabel, ylabel, title, text, filename, max_points in plots:
        xp, yp = x, y
        if max_points and len(x) > max_points:
            ids = np.random.default_rng(42).choice(len(x), max_points, replace=False)
            xp, yp = x[ids], y[ids]

        lo, hi = min(x.min(), y.min()), max(x.max(), y.max())
        plt.figure(figsize=(6, 6))
        plt.scatter(xp, yp, s=10, alpha=0.25, edgecolors="none")
        plt.plot([lo, hi], [lo, hi], linestyle="--")
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.text(0.04, 0.96, text, transform=plt.gca().transAxes, va="top")
        plt.tight_layout()
        plt.savefig(out / filename, dpi=300)
        plt.close()

    for values, xlabel, title, filename in [
        (de, "MACE - DFT energy error (meV/atom)",
         "Energy-error distribution", "energy_error_distribution.png"),
        (df, r"MACE - DFT force error (meV/$\AA$)",
         "Force-error distribution", "force_error_distribution.png"),
    ]:
        plt.figure(figsize=(7, 5))
        plt.hist(values, bins=40)
        plt.axvline(0, linestyle="--")
        plt.xlabel(xlabel)
        plt.ylabel("Count")
        plt.title(title)
        plt.tight_layout()
        plt.savefig(out / filename, dpi=300)
        plt.close()

    print(f"Energy RMSE: {e_rmse:.3f} meV/atom")
    print(f"Energy MAE : {e_mae:.3f} meV/atom")
    print(f"Force RMSE : {f_rmse:.1f} meV/Angstrom")
    print(f"Force MAE  : {f_mae:.1f} meV/Angstrom")


if __name__ == "__main__":
    main()
