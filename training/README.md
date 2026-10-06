# MACE training on Stampede3

`train_stampede3.slurm` is a sanitized version of the production TACC Stampede3 training job. User-specific paths and allocation identifiers are replaced by placeholders.

Key production hyperparameters:

- cutoff (`r_max`): 5.0 Å
- hidden irreps: `64x0e + 64x1o`
- batch size: 8
- epochs: 300
- learning rate: 0.005
- energy weight: 1.0
- force weight: 10.0
- SWA enabled from epoch 150
- CPU training with 112 OpenMP threads
