#!/usr/bin/env bash
#SBATCH --job-name=act_dr6
#SBATCH --partition=c23ms
#SBATCH --output=chains/act_dr6_baseline/slurm-%j.out
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=2G
#SBATCH --time=24:00:00

source scripts/cluster/env.sh

export OMP_NUM_THREADS="$SLURM_CPUS_PER_TASK"

srun .venv/bin/cobaya-run -r inputs/act_dr6_baseline.yaml
