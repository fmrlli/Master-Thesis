module purge
module load GCC OpenMPI Python/3.11.5

export PATH="$HOME/.local/bin:$PATH"
export COBAYA_PACKAGES_PATH="${HPCWORK:-$HOME}/cosmo-packages"
export UV_CACHE_DIR="${HPCWORK:-$HOME}/.cache/uv"
export UV_PYTHON="$(which python3)"

