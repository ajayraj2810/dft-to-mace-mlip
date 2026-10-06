# DFT-to-MACE MLIP Workflow

An end-to-end scientific machine-learning workflow for constructing and validating a **MACE machine-learned interatomic potential (MLIP)** from molecular-dynamics configurations and first-principles reference calculations.

**LAMMPS trajectory sampling → Quantum ESPRESSO DFT labelling → extended-XYZ dataset construction → temperature-stratified train/validation/test split → MACE training on TACC Stampede3 → independent energy/force validation.**

> This is a sanitized research-software portfolio. Large trajectories, full production DFT datasets, pseudopotentials, trained checkpoints, account identifiers, and user-specific HPC paths are intentionally not redistributed.

## Highlights

- **931** Quantum ESPRESSO output calculations processed
- **875** accepted DFT-labelled configurations after parsing and quality filtering
- Sampling temperatures: **300, 350, 400, 450, and 500 K**
- Temperature-stratified split: **698 train / 85 validation / 92 test**
- MACE stage-two model with stochastic weight averaging (SWA)
- Final test RMSE: **0.6 meV/atom** for energy and **33.3 meV/Å** for forces
- Reusable Python utilities for configuration sampling, QE input generation, QE parsing, dataset splitting, training-log analysis, and model validation

## Workflow

```text
Classical MD trajectories (300–500 K)
            │
            ▼
    Configuration sampling
            │
            ▼
 Quantum ESPRESSO labelling
   energies + atomic forces
            │
            ▼
      Extended XYZ dataset
            │
     ┌──────┼──────┐
     ▼      ▼      ▼
   Train   Valid   Test
     │
     ▼
      MACE training
     │
     ▼
Stage 2 + stochastic weight averaging
     │
     ▼
 Energy / force validation
```

## Model performance

| Split | Energy RMSE (meV/atom) | Force RMSE (meV/Å) | Relative force RMSE |
|---|---:|---:|---:|
| Train | 0.6 | 31.7 | 2.37% |
| Validation | 0.6 | 33.9 | 2.54% |
| **Test** | **0.6** | **33.3** | **2.47%** |

The similar train, validation, and test errors provide a useful check against strong train/test divergence for this dataset.

## Dataset construction

| Temperature (K) | Accepted | Train | Validation | Test |
|---:|---:|---:|---:|---:|
| 300 | 126 | 100 | 12 | 14 |
| 350 | 192 | 153 | 19 | 20 |
| 400 | 188 | 150 | 18 | 20 |
| 450 | 189 | 151 | 18 | 20 |
| 500 | 180 | 144 | 18 | 18 |
| **Total** | **875** | **698** | **85** | **92** |

The complete production dataset is intentionally omitted; the repository focuses on reproducible workflow code and documented dataset statistics.

## DFT reference calculations

The Quantum ESPRESSO workflow prepares periodic single-point calculations for reference **energies and atomic forces** using **PBE**, **Grimme-D3 dispersion**, **PAW pseudopotentials**, and **Gamma-point sampling** for the large simulation cells.

```text
dft/
├── generate_qe_inputs.py
├── parse_qe_outputs.py
└── README.md
```

## MACE training

The sanitized Stampede3 workflow uses:

```text
model              MACE
r_max              5.0 Å
hidden_irreps      64x0e + 64x1o
batch_size         8
max_num_epochs     300
learning_rate      0.005
energy_weight      1.0
forces_weight      10.0
SWA start          epoch 150
```

## Repository structure

```text
dft-to-mace-mlip/
├── src/                  # LAMMPS configuration sampling
├── dft/                  # QE input generation + output parsing
├── data/                 # dataset statistics + reproducible splitting
├── training/             # sanitized Stampede3 MACE job
├── validation/           # metrics, evaluation and plotting utilities
├── docs/                  # end-to-end workflow notes
├── requirements.txt
└── README.md
```

## Quick start

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Sample a LAMMPS trajectory:

```bash
python src/extract_lammps_frames.py trajectory.lammpstrj \
    --temperature 400 \
    --stride 100 \
    --output-dir sampled_frames
```

Generate Quantum ESPRESSO inputs:

```bash
python dft/generate_qe_inputs.py sampled_frames --output-dir qe_inputs
```

Parse completed QE calculations:

```bash
python dft/parse_qe_outputs.py qe_outputs --output dataset_all.xyz
```

Create a reproducible temperature-stratified split:

```bash
python data/split_dataset.py dataset_all.xyz --seed 42
```

Submit the sanitized Stampede3 training job after replacing the placeholders:

```bash
sbatch training/train_stampede3.slurm
```

Evaluate a trained MACE model and generate parity/error plots:

```bash
python validation/scripts/evaluate_and_plot_mace.py \
    --test test.xyz \
    --model mace_model_stagetwo.model \
    --device cuda \
    --output-dir validation_output
```

Or use the MACE evaluation CLI and plot its predictions:

```bash
bash validation/run_test_evaluation.sh
```

## Skills demonstrated

**Python · MACE · PyTorch · ASE · Quantum ESPRESSO · LAMMPS · SLURM · TACC Stampede3 · HPC · Scientific machine learning · Atomistic simulation · Data processing · Model validation**

## Data-sharing note

This repository demonstrates the workflow and reusable analysis code while avoiding redistribution of large or research-restricted artifacts.
