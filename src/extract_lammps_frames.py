#!/usr/bin/env python3
"""Sample LAMMPS dump frames and write lightweight XYZ configurations.

The default atom-type map matches the electrolyte system used for this
portfolio example. Edit TYPE_TO_ELEMENT for a different LAMMPS topology.
"""
from __future__ import annotations

import argparse
from pathlib import Path

TYPE_TO_ELEMENT = {
    1: "N", 2: "S", 3: "O", 4: "C", 5: "F",
    6: "S", 7: "N", 8: "C", 9: "C",
    10: "H", 11: "H", 12: "H", 13: "H",
    14: "N", 15: "Li",
}


def read_dump(path: Path):
    """Yield (timestep, box_lengths, atoms) from an orthorhombic LAMMPS dump."""
    with path.open() as handle:
        while True:
            line = handle.readline()
            if not line:
                return
            if not line.startswith("ITEM: TIMESTEP"):
                continue

            timestep = int(handle.readline())
            handle.readline()  # ITEM: NUMBER OF ATOMS
            n_atoms = int(handle.readline())

            handle.readline()  # ITEM: BOX BOUNDS ...
            bounds = [tuple(map(float, handle.readline().split()[:2])) for _ in range(3)]
            box = tuple(hi - lo for lo, hi in bounds)

            header = handle.readline().split()[2:]
            col = {name: i for i, name in enumerate(header)}
            required = {"type", "x", "y", "z"}
            if not required.issubset(col):
                raise ValueError(f"Dump must contain columns {sorted(required)}")

            atoms = []
            for _ in range(n_atoms):
                row = handle.readline().split()
                atoms.append((
                    int(row[col["type"]]),
                    float(row[col["x"]]),
                    float(row[col["y"]]),
                    float(row[col["z"]]),
                ))
            yield timestep, box, atoms


def write_xyz(path: Path, timestep: int, temperature: int, box, atoms):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as out:
        out.write(f"{len(atoms)}\n")
        out.write(
            f"timestep={timestep} temperature={temperature} "
            f"Box: {box[0]:.6f} {box[1]:.6f} {box[2]:.6f}\n"
        )
        for atom_type, x, y, z in atoms:
            element = TYPE_TO_ELEMENT.get(atom_type, "X")
            out.write(f"{element} {x:.8f} {y:.8f} {z:.8f}\n")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("trajectory", type=Path)
    p.add_argument("--temperature", type=int, required=True)
    p.add_argument("--stride", type=int, default=100)
    p.add_argument("--max-frames", type=int)
    p.add_argument("--output-dir", type=Path, default=Path("sampled_frames"))
    args = p.parse_args()

    written = 0
    for frame_index, (timestep, box, atoms) in enumerate(read_dump(args.trajectory)):
        if frame_index % args.stride:
            continue
        output = args.output_dir / f"T{args.temperature}_frame{frame_index:06d}.xyz"
        write_xyz(output, timestep, args.temperature, box, atoms)
        written += 1
        if args.max_frames is not None and written >= args.max_frames:
            break

    print(f"Wrote {written} sampled configurations to {args.output_dir}")


if __name__ == "__main__":
    main()
