#!/usr/bin/env python3
"""Parse Quantum ESPRESSO single-point outputs into a MACE-ready extxyz dataset."""
from pathlib import Path
import argparse
import numpy as np
from ase.io import read, write


def main():
    p = argparse.ArgumentParser()
    p.add_argument("root", nargs="?", default=".", help="Directory containing temperature folders")
    p.add_argument("-o", "--output", default="dataset_all.xyz")
    p.add_argument("--temperatures", nargs="+", type=int, default=[300, 350, 400, 450, 500])
    p.add_argument("--max-force", type=float, default=10.0, help="Reject structures above this max |force| in eV/Å")
    args = p.parse_args()

    root = Path(args.root)
    configs, failed, high_force = [], [], []

    for temp in args.temperatures:
        files = sorted((root / str(temp)).glob("*.out"))
        print(f"T={temp} K: {len(files)} QE outputs")
        for file in files:
            try:
                atoms = read(file, format="espresso-out")
                energy = atoms.get_potential_energy()
                forces = atoms.get_forces()
                max_force = float(np.abs(forces).max())
                if max_force > args.max_force:
                    high_force.append((str(file), max_force))
                    continue
                atoms.info["REF_energy"] = float(energy)
                atoms.arrays["REF_forces"] = forces
                atoms.info["temperature"] = temp
                configs.append(atoms)
            except Exception as exc:
                failed.append((str(file), str(exc)))

    if not configs:
        raise RuntimeError("No valid configurations were parsed.")
    write(args.output, configs, format="extxyz")
    print(f"Saved {len(configs)} configurations -> {args.output}")
    print(f"Rejected for high forces: {len(high_force)}")
    print(f"Failed to parse: {len(failed)}")


if __name__ == "__main__":
    main()
