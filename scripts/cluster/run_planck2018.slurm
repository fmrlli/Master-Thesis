#!/usr/bin/env bash
#SBATCH --job-name=p18_baseline
#SBATCH --partition=c23ms
#SBATCH --output=chains/planck2018_baseline/slurm-%j.out
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=2G
#SBATCH --time=24:00:00

set -euo pipefail #good standard practice in case of errors
source scripts/cluster/env.sh

export OMP_NUM_THREADS="$SLURM_CPUS_PER_TASK"

srun .venv/bin/cobaya-run -r inputs/planck2018_baseline.yaml

