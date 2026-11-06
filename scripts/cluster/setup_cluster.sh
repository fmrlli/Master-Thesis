#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_DIR"
source scripts/cluster/env.sh

echo ">>> Modules loaded:"; module list 2>&1 | sed 's/^/    /'
echo ">>> mpicc: $(command -v mpicc || echo 'NOT FOUND - check module names in env.sh')"


if ! command -v uv >/dev/null 2>&1; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi
uv --version

uv sync --locked --no-dev
MPICC="$(command -v mpicc)" uv pip install --python .venv/bin/python \
    --reinstall --no-binary mpi4py --no-cache mpi4py
.venv/bin/python -c "import cobaya, classy, candl, spt_candl_data; from mpi4py import MPI; print('Env & mpi4py OK:', MPI.Get_library_version().splitlines()[0])"

mkdir -p "$COBAYA_PACKAGES_PATH"
.venv/bin/cobaya-install inputs/planck2018_baseline.yaml \
    -p "$COBAYA_PACKAGES_PATH" --skip classy

#test
.venv/bin/cobaya-run inputs/planck2018_baseline.yaml --test -o "/tmp/$USER-p18test/chain"

echo ">>> Setup done. Submit with:"
echo "    cd $PROJECT_DIR && mkdir -p chains/planck2018_baseline && sbatch scripts/cluster/run_planck2018.slurm"
