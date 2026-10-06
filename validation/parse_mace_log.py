#!/usr/bin/env python3
"""Extract epoch-wise energy/force RMSE from a MACE training log."""
import argparse
import csv
import re

PATTERN = re.compile(
    r"Epoch\s+(?P<epoch>\d+):.*?RMSE_E_per_atom=\s*(?P<energy>[0-9.]+)\s*meV,"
    r"\s*RMSE_F=\s*(?P<force>[0-9.]+)\s*meV\s*/\s*A"
)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("log")
    p.add_argument("-o", "--output", default="training_history.csv")
    args = p.parse_args()

    records = []
    with open(args.log, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            match = PATTERN.search(line)
            if match:
                records.append(match.groupdict())

    with open(args.output, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["epoch", "energy", "force"])
        writer.writeheader()
        writer.writerows(records)
    print(f"Wrote {len(records)} epochs to {args.output}")


if __name__ == "__main__":
    main()
