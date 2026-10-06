#!/usr/bin/env python3
"""Plot final MACE train/validation/test RMSE values from final_metrics.csv."""
from pathlib import Path
import csv
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
rows = list(csv.DictReader((HERE / "final_metrics.csv").open()))
rows = [r for r in rows if r["stage"] == "stage_two_swa"]

labels = [r["split"].title() for r in rows]
energy = [float(r["energy_rmse_meV_per_atom"]) for r in rows]
forces = [float(r["force_rmse_meV_per_A"]) for r in rows]

fig = plt.figure(figsize=(5.4, 3.8))
ax = fig.add_subplot(111)
x = list(range(len(labels)))
ax.bar([i - 0.18 for i in x], energy, width=0.36, label="Energy RMSE (meV/atom)")
ax.bar([i + 0.18 for i in x], forces, width=0.36, label="Force RMSE (meV/Å)")
ax.set_xticks(x, labels)
ax.set_ylabel("RMSE")
ax.set_title("MACE Stage-Two (SWA) Validation")
ax.legend(frameon=False, fontsize=8)
fig.tight_layout()

output = HERE.parent / "figures"
output.mkdir(exist_ok=True)
fig.savefig(output / "final_rmse.png", dpi=300)
