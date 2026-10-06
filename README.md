# DFT-to-MACE MLIP Workflow

An end-to-end scientific machine-learning workflow for constructing and validating a **MACE machine-learned interatomic potential (MLIP)** from molecular-dynamics configurations and first-principles reference calculations.

The repository demonstrates a practical atomistic-ML pipeline:

**LAMMPS trajectory sampling → Quantum ESPRESSO DFT labelling → extended-XYZ dataset construction → temperature-stratified train/validation/test split → MACE training on TACC Stampede3 → independent energy/force validation.**

> This is a sanitized research-software portfolio. Large trajectories, complete production DFT datasets, pseudopotentials, trained checkpoints, account identifiers, and user-specific HPC paths are intentionally not redistributed.

## Highlights

- **931** Quantum ESPRESSO output calculations processed
- **875** accepted DFT-labelled configurations after parsing/quality filtering
- Sampling temperatures: **300, 350, 400, 450, and 500 K**
- Temperature-stratified split: **698 train / 85 validation / 92 test**
- MACE stage-two model with stochastic weight averaging (SWA)
- Final test RMSE: **0.6 meV/atom** for energy and **33.3 meV/Å** for forces
- Reusable Python utilities for trajectory sampling, QE parsing, dataset splitting, training-log analysis, and model validation

## Workflow

```text
Classical MD trajectories (300–500 K)
            │
            ▼
    Configuration sampling
       EQ + nEQ structures
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

The final stage-two/SWA model produced the following errors on the production splits:

| Split | Energy RMSE (meV/atom) | Force RMSE (meV/Å) | Relative force RMSE |
|---|---:|---:|---:|
| Train | 0.6 | 31.7 | 2.37% |
| Validation | 0.6 | 33.9 | 2.54% |
| **Test** | **0.6** | **33.3** | **2.47%** |

The similar train, validation, and test errors provide a useful check against strong train/test divergence for this dataset.

### Energy parity

![MACE energy parity](figures/energy_parity_mace_actual.png)

### Force parity

![MACE force parity](figures/force_parity_mace_actual.png)

### Training convergence

![Energy RMSE versus epoch](figures/energy_rmse_vs_epoch.png)

![Force RMSE versus epoch](figures/force_rmse_vs_epoch.png)

## Dataset construction

Configurations were sampled at **300, 350, 400, 450, and 500 K**. The workflow includes both equilibrated (**EQ**) and non-equilibrated (**nEQ**) structures to broaden configurational coverage before first-principles labelling.

| Temperature (K) | Accepted | Train | Validation | Test |
|---:|---:|---:|---:|---:|
| 300 | 126 | 100 | 12 | 14 |
| 350 | 192 | 153 | 19 | 20 |
| 400 | 188 | 150 | 18 | 20 |
| 450 | 189 | 151 | 18 | 20 |
| 500 | 180 | 144 | 18 | 18 |
| **Total** | **875** | **698** | **85** | **92** |

The complete production dataset is intentionally omitted. A small representative structure is included under `data/sample/` so the repository remains lightweight.

## DFT reference calculations

The Quantum ESPRESSO workflow prepares periodic single-point calculations for reference **energies and atomic forces**. The supplied project inputs use **PBE**, **Grimme-D3 dispersion**, **PAW pseudopotentials**, and **Gamma-point sampling** for the large simulation cells.

The DFT utilities include:

```text
dft/
├── generate_qe_inputs.py     # build QE single-point inputs
├── parse_qe_outputs.py       # extract converged energies/forces into extxyz
├── example_qe_input.in       # representative sanitized QE input
└── README.md
```

## MACE training

The included sanitized Stampede3 workflow uses the following principal settings:

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

The production HPC allocation, username-specific paths, raw checkpoints, and complete logs have been removed from the public copy.

## Repository structure

```text
dft-to-mace-mlip/
├── src/                  # LAMMPS configuration-sampling utility
├── dft/                  # QE input generation and output parsing
├── data/                 # dataset statistics, sample structure, split utility
├── training/             # sanitized Stampede3 MACE training job
├── validation/           # evaluation, metrics, and log-analysis tools
├── figures/              # parity and convergence figures
├── docs/                  # workflow notes
├── requirements.txt
└── README.md
```

## Quick start

Install the Python dependencies:

```bash
python -m pip install -r requirements.txt
```

Parse completed QE calculations into a MACE-ready extended-XYZ dataset:

```bash
python dft/parse_qe_outputs.py qe_outputs --output dataset_all.xyz
```

Create a reproducible temperature-stratified split:

```bash
python data/split_dataset.py dataset_all.xyz --seed 42
```

Submit the sanitized training job after replacing the Stampede3 placeholders with your own environment and allocation information:

```bash
sbatch training/train_stampede3.slurm
```

Evaluate a trained MACE model directly from Python:

```bash
python validation/scripts/evaluate_and_plot_mace.py \
    --test test.xyz \
    --model mace_model_stagetwo.model \
    --device cuda \
    --output-dir validation_output
```

Alternatively, run the MACE evaluation CLI and then generate standalone plots:

```bash
mace_eval_configs \
    --configs=test.xyz \
    --model=mace_model_stagetwo.model \
    --output=test_mace_predictions.xyz \
    --device=cuda \
    --default_dtype=float64 \
    --batch_size=8 \
    --info_prefix=MACE_

python validation/scripts/plot_from_mace_eval.py \
    test_mace_predictions.xyz \
    --output-dir validation_output
```

## Skills demonstrated

**Python · MACE · PyTorch · ASE · Quantum ESPRESSO · LAMMPS · SLURM · TACC Stampede3 · HPC · Scientific machine learning · Atomistic simulation · Data processing · Model validation**

## Reproducibility and data-sharing note

This repository focuses on the **workflow and reusable analysis code** rather than redistribution of a full research dataset. The included scripts, sample structure, dataset statistics, sanitized HPC job, and validation figures document how the model-development pipeline was constructed while avoiding publication of large or research-restricted artifacts.
