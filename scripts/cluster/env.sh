# Shared environment for CLAIX (sourced by setup_cluster.sh and the Slurm scripts).
module purge >/dev/null 2>&1 || true
module load GCC OpenMPI Python/3.11.5

export PATH="$HOME/.local/bin:$PATH"
# Large data / caches on $HPCWORK (fast Lustre, big quota) instead of $HOME
export COBAYA_PACKAGES_PATH="${HPCWORK:-$HOME}/cosmo-packages"
export UV_CACHE_DIR="${HPCWORK:-$HOME}/.cache/uv"
export UV_PYTHON="$(which python3)"

