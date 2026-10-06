#!/usr/bin/env python3
"""Create reproducible temperature-stratified train/validation/test splits."""
from collections import defaultdict
import argparse
import random
from ase.io import read, write


def main():
    p = argparse.ArgumentParser()
    p.add_argument("input", nargs="?", default="dataset_all.xyz")
    p.add_argument("--train", type=float, default=0.80)
    p.add_argument("--val", type=float, default=0.10)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--prefix", default="")
    args = p.parse_args()
    if args.train + args.val >= 1.0:
        raise ValueError("train + val must be < 1.0")

    rng = random.Random(args.seed)
    configs = read(args.input, index=":")
    groups = defaultdict(list)
    for atoms in configs:
        if "temperature" not in atoms.info:
            raise ValueError("Every configuration must contain a temperature label.")
        groups[int(atoms.info["temperature"])].append(atoms)

    train, val, test = [], [], []
    for temp in sorted(groups):
        group = groups[temp]
        rng.shuffle(group)
        n = len(group)
        n_train = int(args.train * n)
        n_val = int(args.val * n)
        train.extend(group[:n_train])
        val.extend(group[n_train:n_train+n_val])
        test.extend(group[n_train+n_val:])
        print(f"{temp} K: total={n}, train={n_train}, val={n_val}, test={n-n_train-n_val}")

    rng.shuffle(train); rng.shuffle(val); rng.shuffle(test)
    write(f"{args.prefix}train.xyz", train, format="extxyz")
    write(f"{args.prefix}val.xyz", val, format="extxyz")
    write(f"{args.prefix}test.xyz", test, format="extxyz")
    print(f"Final: train={len(train)}, val={len(val)}, test={len(test)}")


if __name__ == "__main__":
    main()
