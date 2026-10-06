#!/usr/bin/env python3
"""Generate Quantum ESPRESSO single-point inputs from sampled XYZ structures."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from ase.data import atomic_masses, atomic_numbers
from ase.io import read

PSEUDOS = {
    "C": "C.pbe-n-kjpaw_psl.1.0.0.UPF",
    "F": "F.pbe-n-kjpaw_psl.1.0.0.UPF",
    "H": "H.pbe-kjpaw_psl.1.0.0.UPF",
    "Li": "Li.pbe-s-kjpaw_psl.1.0.0.UPF",
    "N": "N.pbe-n-kjpaw_psl.1.0.0.UPF",
    "O": "O.pbe-n-kjpaw_psl.1.0.0.UPF",
    "S": "S.pbe-n-kjpaw_psl.1.0.0.UPF",
}


def box_from_comment(path: Path):
    with path.open() as handle:
        handle.readline()
        comment = handle.readline()
    match = re.search(r"Box:\s*([0-9.+-]+)\s+([0-9.+-]+)\s+([0-9.+-]+)", comment)
    if not match:
        raise ValueError(f"No 'Box: Lx Ly Lz' entry found in {path}")
    return tuple(float(match.group(i)) for i in range(1, 4))


def render_qe(atoms, box, prefix, pseudo_dir, ecutwfc, ecutrho):
    species = sorted(set(atoms.get_chemical_symbols()))
    lines = [
        "&CONTROL",
        "  calculation = 'scf'",
        f"  prefix = '{prefix}'",
        f"  pseudo_dir = '{pseudo_dir}'",
        "  outdir = './tmp'",
        "  tstress = .true.",
        "  tprnfor = .true.",
        "/",
        "&SYSTEM",
        "  ibrav = 0",
        f"  nat = {len(atoms)}",
        f"  ntyp = {len(species)}",
        f"  ecutwfc = {ecutwfc}",
        f"  ecutrho = {ecutrho}",
        "  occupations = 'smearing'",
        "  smearing = 'gaussian'",
        "  degauss = 0.01",
        "  input_dft = 'PBE'",
        "  vdw_corr = 'grimme-d3'",
        "/",
        "&ELECTRONS",
        "  electron_maxstep = 100000",
        "  conv_thr = 1.0d-4",
        "  mixing_beta = 0.3",
        "  mixing_mode = 'plain'",
        "  diagonalization = 'david'",
        "/",
        "CELL_PARAMETERS angstrom",
        f"  {box[0]:.8f} 0.0 0.0",
        f"  0.0 {box[1]:.8f} 0.0",
        f"  0.0 0.0 {box[2]:.8f}",
        "",
        "ATOMIC_SPECIES",
    ]
    for symbol in species:
        mass = atomic_masses[atomic_numbers[symbol]]
        pseudo = PSEUDOS.get(symbol, f"{symbol}.pbe-kjpaw.UPF")
        lines.append(f"  {symbol} {mass:.6f} {pseudo}")

    lines += ["", "ATOMIC_POSITIONS angstrom"]
    for symbol, (x, y, z) in zip(atoms.get_chemical_symbols(), atoms.positions):
        lines.append(f"  {symbol} {x:.8f} {y:.8f} {z:.8f}")

    lines += ["", "K_POINTS gamma", ""]
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("input", type=Path, help="XYZ file or directory containing XYZ files")
    p.add_argument("--output-dir", type=Path, default=Path("qe_inputs"))
    p.add_argument("--pseudo-dir", default="./pseudopotential")
    p.add_argument("--ecutwfc", type=float, default=60.0)
    p.add_argument("--ecutrho", type=float, default=400.0)
    args = p.parse_args()

    xyz_files = [args.input] if args.input.is_file() else sorted(args.input.glob("*.xyz"))
    args.output_dir.mkdir(parents=True, exist_ok=True)

    for xyz in xyz_files:
        atoms = read(xyz)
        box = box_from_comment(xyz)
        text = render_qe(atoms, box, xyz.stem, args.pseudo_dir, args.ecutwfc, args.ecutrho)
        (args.output_dir / f"{xyz.stem}.in").write_text(text)

    print(f"Wrote {len(xyz_files)} QE input files to {args.output_dir}")


if __name__ == "__main__":
    main()
