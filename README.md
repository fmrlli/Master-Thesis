# Master's Thesis

> Working repository for my master's thesis: research code, data analysis and results.

- **Author:** fmrlli
- **Institution:** _university / department_
- **Supervisor:** _name_
- **Status:** work in progress

## About

This repository holds everything behind the thesis: the literature and method notes,
the analysis pipeline, generated figures and tables, and the writing itself. It is a
Python project managed with [uv](https://docs.astral.sh/uv/) and built on the usual
scientific stack (pandas, numpy, scipy, matplotlib, scikit-learn, Jupyter).

## Layout

```
.
├── README.md
├── pyproject.toml        # project metadata and dependencies (uv)
├── uv.lock               # exact resolved versions — commit this
├── src/                  # importable analysis code
│   └── thesis/
├── notebooks/            # exploratory notebooks (numbered, e.g. 01_eda.ipynb)
├── scripts/              # runnable entry points (uv run scripts/...)
├── data/
│   ├── raw/              # immutable inputs (usually not committed)
│   ├── interim/          # cleaned intermediate data (not committed)
│   └── processed/        # analysis-ready data (not committed)
├── results/
│   ├── figures/          # generated figures
│   └── tables/           # generated tables
├── docs/                 # thesis chapters, notes, references
└── tests/                # tests for src/
```

## Getting started

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/) (0.13 or newer).

```bash
git clone https://github.com/fmrlli/Master-Thesis.git
cd Master-Thesis
uv sync                 # creates .venv and installs all dependencies
```

`uv sync` creates the virtual environment at `.venv/` and installs exactly the
versions pinned in `uv.lock`. Python itself is fetched by uv if needed.

## Common commands

```bash
uv sync                        # install / update the environment from uv.lock
uv add pandas scipy            # add a dependency and update pyproject.toml + lock
uv add --dev pytest ruff       # add a development dependency
uv remove <package>            # drop a dependency
uv run python scripts/analyse.py   # run anything inside the environment
uv run jupyter lab             # start Jupyter with the project kernel
uv run pytest                  # run the test suite
uv run ruff check .            # lint
```

Always go through `uv run` (or activate the venv with `source .venv/bin/activate`)
instead of calling a system `python` — the environment is `.venv/` and is never
committed.

## Data

Raw data lives in `data/raw/` and is treated as read-only: it is never modified by
code and generally not committed (see `.gitignore`). Sources, licenses and download
instructions go in `data/README.md`. Everything downstream is regenerated from the
raw inputs by the pipeline, so no intermediate or processed file needs to be tracked.

## Reproducibility

- Pin dependencies in `uv.lock` and commit it.
- Run pipelines with `uv run` so results always come from the locked environment.
- Keep notebooks for exploration; move durable logic into `src/thesis/`.
- Regenerate figures and tables with a single entry point rather than by hand.

## Writing

The thesis text and notes live in `docs/`. Figures referenced by the text are
copied from `results/figures/` so the document always matches the current results.
