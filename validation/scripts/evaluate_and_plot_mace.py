#!/usr/bin/env python3
"""Evaluate a trained MACE model on a held-out extxyz test set and plot validation."""
import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from ase.io import read
from mace.calculators import MACECalculator


def rmse(a, b):
    return float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2)))


def mae(a, b):
    return float(np.mean(np.abs(np.asarray(a) - np.asarray(b))))


def ref_energy(atoms):
    if "REF_energy" in atoms.info:
        return float(atoms.info["REF_energy"])
    if atoms.calc is not None and "energy" in atoms.calc.results:
        return float(atoms.calc.results["energy"])
    if "energy" in atoms.info:
        return float(atoms.info["energy"])
    raise KeyError("No reference energy found.")


def ref_forces(atoms):
    if "REF_forces" in atoms.arrays:
        return np.asarray(atoms.arrays["REF_forces"], float).copy()
    if atoms.calc is not None and "forces" in atoms.calc.results:
        return np.asarray(atoms.calc.results["forces"], float).copy()
    if "forces" in atoms.arrays:
        return np.asarray(atoms.arrays["forces"], float).copy()
    raise KeyError("No reference forces found.")


def parity(x, y, xlabel, ylabel, title, text, outfile, max_points=None):
    x, y = np.asarray(x), np.asarray(y)
    if max_points and len(x) > max_points:
        ids = np.random.default_rng(42).choice(len(x), max_points, replace=False)
        xp, yp = x[ids], y[ids]
    else:
        xp, yp = x, y

    lo, hi = min(x.min(), y.min()), max(x.max(), y.max())
    pad = 0.03 * (hi - lo if hi > lo else 1.0)

    plt.figure(figsize=(6, 6))
    plt.scatter(xp, yp, s=10, alpha=0.25, edgecolors="none")
    plt.plot([lo - pad, hi + pad], [lo - pad, hi + pad], linestyle="--")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.text(0.04, 0.96, text, transform=plt.gca().transAxes, va="top")
    plt.tight_layout()
    plt.savefig(outfile, dpi=300)
    plt.close()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--test", required=True)
    p.add_argument("--model", required=True)
    p.add_argument("--device", default="cuda", choices=["cpu", "cuda"])
    p.add_argument("--dtype", default="float64", choices=["float32", "float64"])
    p.add_argument("--output-dir", default="validation_output")
    p.add_argument("--max-force-points", type=int, default=60000)
    args = p.parse_args()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    configs = read(args.test, index=":")
    calc = MACECalculator(
        model_paths=args.model,
        device=args.device,
        default_dtype=args.dtype,
    )

    ref_e, pred_e, ref_f, pred_f, rows = [], [], [], [], []

    for i, atoms in enumerate(configs):
        e0 = ref_energy(atoms)
        f0 = ref_forces(atoms)
        n_atoms = len(atoms)
        temperature = atoms.info.get("temperature", np.nan)

        atoms.calc = calc
        e1 = float(atoms.get_potential_energy())
        f1 = np.asarray(atoms.get_forces(), float)

        ref_e.append(e0 / n_atoms)
        pred_e.append(e1 / n_atoms)
        ref_f.append(f0.reshape(-1))
        pred_f.append(f1.reshape(-1))
        rows.append([
            i, temperature, n_atoms, e0, e1, e0 / n_atoms, e1 / n_atoms,
            (e1 - e0) / n_atoms * 1000,
        ])

    ref_e, pred_e = np.asarray(ref_e), np.asarray(pred_e)
    ref_f, pred_f = np.concatenate(ref_f), np.concatenate(pred_f)

    energy_rmse = rmse(ref_e, pred_e) * 1000
    energy_mae = mae(ref_e, pred_e) * 1000
    force_rmse = rmse(ref_f, pred_f) * 1000
    force_mae = mae(ref_f, pred_f) * 1000

    parity(
        ref_e, pred_e,
        "DFT energy (eV/atom)", "MACE energy (eV/atom)",
        "Energy parity: test set",
        f"RMSE = {energy_rmse:.3f} meV/atom\nMAE = {energy_mae:.3f} meV/atom",
        out / "energy_parity.png",
    )
    parity(
        ref_f, pred_f,
        r"DFT force (eV/$\AA$)", r"MACE force (eV/$\AA$)",
        "Force parity: test set",
        f"RMSE = {force_rmse:.1f} meV/$\\AA$\nMAE = {force_mae:.1f} meV/$\\AA$",
        out / "force_parity.png",
        args.max_force_points,
    )

    for values, xlabel, title, filename in [
        ((pred_e - ref_e) * 1000, "MACE - DFT energy error (meV/atom)",
         "Energy-error distribution", "energy_error_distribution.png"),
        ((pred_f - ref_f) * 1000, r"MACE - DFT force-component error (meV/$\AA$)",
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

    with (out / "configuration_predictions.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "configuration", "temperature_K", "n_atoms",
            "DFT_energy_eV", "MACE_energy_eV",
            "DFT_energy_eV_atom", "MACE_energy_eV_atom",
            "energy_error_meV_atom",
        ])
        writer.writerows(rows)

    with (out / "metrics.txt").open("w") as handle:
        handle.write(f"Energy RMSE: {energy_rmse:.6f} meV/atom\n")
        handle.write(f"Energy MAE: {energy_mae:.6f} meV/atom\n")
        handle.write(f"Force RMSE: {force_rmse:.6f} meV/Angstrom\n")
        handle.write(f"Force MAE: {force_mae:.6f} meV/Angstrom\n")

    print(f"Energy RMSE = {energy_rmse:.3f} meV/atom")
    print(f"Force RMSE  = {force_rmse:.1f} meV/Angstrom")


if __name__ == "__main__":
    main()
