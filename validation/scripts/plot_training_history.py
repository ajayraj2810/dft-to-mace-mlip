#!/usr/bin/env python3
"""Plot validation loss and RMSE vs epoch from MACE *_train.txt JSON-lines output."""
import argparse,json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

p=argparse.ArgumentParser(); p.add_argument("training_results"); p.add_argument("--stage-two-start",type=int,default=150)
p.add_argument("--output-dir",default="."); a=p.parse_args()
rows=[]
for line in open(a.training_results):
    try:r=json.loads(line)
    except json.JSONDecodeError:continue
    if r.get("mode")=="eval" and r.get("epoch") is not None: rows.append(r)
out=Path(a.output_dir); out.mkdir(parents=True,exist_ok=True)
ep=np.array([r["epoch"] for r in rows])
series=[(np.array([r["rmse_e_per_atom"] for r in rows])*1000,"Energy RMSE (meV/atom)","energy_rmse_vs_epoch.png"),
        (np.array([r["rmse_f"] for r in rows])*1000,r"Force RMSE (meV/$\AA$)","force_rmse_vs_epoch.png"),
        (np.array([r["loss"] for r in rows]),"Validation loss","validation_loss_vs_epoch.png")]
for y,ylab,fn in series:
    plt.figure(figsize=(7,5)); plt.plot(ep,y); plt.axvline(a.stage_two_start,linestyle="--")
    if "loss" in fn: plt.yscale("log")
    plt.xlabel("Epoch"); plt.ylabel(ylab); plt.tight_layout(); plt.savefig(out/fn,dpi=300); plt.close()
