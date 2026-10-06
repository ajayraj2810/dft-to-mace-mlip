#!/bin/bash
#SBATCH -J mace_train
#SBATCH -o mace_train.%j.out
#SBATCH -p <PARTITION>
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -c 112
#SBATCH -t 48:00:00
#SBATCH -A <TACC_ALLOCATION>

module purge
module load python
source <PATH_TO_MACE_ENV>/bin/activate

export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-112}

srun mace_run_train \
  --name mace_model \
  --train_file train.xyz \
  --valid_file val.xyz \
  --test_file test.xyz \
  --model MACE \
  --r_max 5.0 \
  --hidden_irreps '64x0e + 64x1o' \
  --batch_size 8 \
  --max_num_epochs 300 \
  --lr 0.005 \
  --energy_weight 1.0 \
  --forces_weight 10.0 \
  --device cpu \
  --E0s average \
  --swa \
  --start_swa 150 \
  --results_dir results \
  --save_cpu
