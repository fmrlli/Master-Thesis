# Thesis – unified Python env (MacOS / WSL)

## 0. System deps (once per machine)

Mac:
```bash
brew install uv gcc libomp open-mpi pkg-config
```

Windows PC: work inside WSL2-Ubuntu only:
```bash
sudo apt update && sudo apt install -y build-essential gfortran pkg-config openmpi-bin libopenmpi-dev
curl -LsSf astral.sh/uv/install.sh | sh
```

## 1. Sync env
```bash
git pull
uv sync --locked
```
Always run via `uv run ...` (`uv run python`, `uv run jupyter lab`).

## Use the venv

No manual activation needed – `uv run` auto-syncs `.venv` from `uv.lock`.

If you need a shell with it:
```bash
source .venv/bin/activate  # same on Mac + WSL
```

VS Code picks `.venv/bin/python` via `.vscode/settings.json` automatically.

## 2. CLASS + Cobaya (once)

```bash
uv run cobaya-install cosmo -p ~/cosmo-packages
```

## 3. Add a new package (on one machine)
```bash
uv add <package>
git add pyproject.toml uv.lock
git commit -m "add <package>"
git push
```
Other machine: `git pull && uv sync --locked`.

## 4. Checks
```bash
uv lock --check    # lock up to date?
uv sync --check    # .venv == lock?
uv tree            # what pulls in what?
uv lock --upgrade-package numpy  # targeted update, then test + commit
```