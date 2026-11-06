#!/usr/bin/env bash
#SBATCH --job-name=spt3g_d1
#SBATCH --partition=c23ms
#SBATCH --output=chains/spt3g_d1_baseline/slurm-%j.out
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=2G
#SBATCH --time=24:00:00

set -euo pipefail
source scripts/cluster/env.sh

export OMP_NUM_THREADS="$SLURM_CPUS_PER_TASK"

srun .venv/bin/cobaya-run -r inputs/spt3g_d1_baseline.yaml
