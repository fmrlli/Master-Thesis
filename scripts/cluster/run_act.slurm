#!/usr/bin/env bash
#SBATCH --job-name=act_dr6
#SBATCH --partition=c23ms
#SBATCH --output=chains/act_dr6_baseline/slurm-%j.out
#SBATCH --ntasks=4                # 4 MCMC chains (cobaya uses them for the R-1 test)
#SBATCH --cpus-per-task=8         # OpenMP threads for CLASS per chain
#SBATCH --mem-per-cpu=2G
#SBATCH --time=24:00:00           # job resumes from checkpoint if resubmitted
##SBATCH --account=<project>      # uncomment if you were given a compute project
##SBATCH --mail-type=END,FAIL
##SBATCH --mail-user=<you>@rwth-aachen.de
#
# Submit from the project directory on the cluster (~/thesis_code/Code):
#   mkdir -p chains/act_dr6_baseline && sbatch scripts/cluster/run_act.slurm
set -euo pipefail
source scripts/cluster/env.sh

export OMP_NUM_THREADS="$SLURM_CPUS_PER_TASK"
export OMP_PROC_BIND=close OMP_PLACES=cores

# -r / --resume: continue an existing chain instead of failing if output exists
srun --cpu-bind=cores .venv/bin/cobaya-run -r inputs/act_dr6_baseline.yaml
