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
scientific stack (pandas, numpy, scipy, matplotlib, scikit-learn, Jupyter), along with
cosmological Boltzmann and MCMC tools (`classy`, `cobaya`, `candl`, `clipy-like`, `getdist`).

## Layout

```
.
├── README.md
├── install.md                        # Local & cluster setup quick notes
├── pyproject.toml                    # Project metadata and dependencies (uv)
├── uv.lock                           # Exact resolved versions — commit this
├── inputs/                           # Cobaya MCMC YAML configurations
│   ├── planck2018_baseline.yaml      # Planck 2018 TT,TE,EE + lowE + lensing
│   ├── spt3g_d1_baseline.yaml        # SPT-3G D1 TT,TE,EE (SPTlite) + tau prior
│   ├── act_dr6_baseline.yaml         # ACT DR6 TT,TE,EE (CMB-only) + tau prior
│   └── example.yaml                  # Minimal quick-test Cobaya input
├── scripts/
│   ├── plot_chains.py                # GetDist joint triangle plot & paper comparison
│   ├── my_code.py                    # Local helper / exploration script
│   └── cluster/                      # RWTH CLAIX Slurm & environment scripts
│       ├── env.sh                    # Module loads (GCC, OpenMPI, Python) & $HPCWORK paths
│       ├── setup_cluster.sh          # One-time CLAIX venv + mpi4py + Planck data install
│       ├── run_planck2018.slurm      # Slurm batch job for Planck 2018
│       ├── run_spt3g.slurm           # Slurm batch job for SPT-3G D1
│       └── run_act.slurm             # Slurm batch job for ACT DR6
├── chains/                           # MCMC chain outputs (git-ignored; synced from CLAIX)
│   ├── planck2018_baseline/
│   ├── spt3g_d1_baseline/
│   └── act_dr6_baseline/
├── notebooks/                        # Exploratory notebooks
└── tests/                            # Smoke tests for CLASS, Cobaya, and candl
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

The environment also provides [`classy`](https://github.com/lesgourg/class_public),
the CLASS Boltzmann code, taken from the local `class_public/` checkout next to
this repo (`../class_public`, see `[tool.uv.sources]`). `uv sync` builds it — the
C library via `make` and then the Cython extension — so a C toolchain (`gcc`,
`make`) is required. After editing any CLASS source, rebuild with:

```bash
uv sync --reinstall-package classy
```

## Common commands

```bash
uv sync                        # install / update the environment from uv.lock
uv add pandas scipy            # add a dependency and update pyproject.toml + lock
uv add --dev pytest ruff       # add a development dependency
uv remove <package>            # drop a dependency
uv run python scripts/plot_chains.py   # plot converged MCMC chains with GetDist
uv run jupyter lab             # start Jupyter with the project kernel
uv run python -m ipykernel install --user --name thesis --display-name "Python (thesis)"  # register kernel for notebooks outside this project
uv run pytest                  # run the test suite
uv run ruff check .            # lint
```

Always go through `uv run` (or activate the venv with `source .venv/bin/activate`)
instead of calling a system `python` — the environment is `.venv/` and is never
committed.

---

## Baseline $\Lambda\text{CDM}$ MCMC Pipeline: Guide & Reference

This section explains how the Cobaya input files, Slurm scripts, and evaluation scripts are written, how they were executed on the RWTH CLAIX cluster, and how the results compare against the official published papers.

### 1. How the Cobaya Input Files (`inputs/*.yaml`) Are Structured

Every Cobaya configuration file is a YAML dictionary with **5 top-level sections**: `theory`, `likelihood`, `params`, `sampler`, and `output`.

#### A. `theory:` (The Boltzmann Solver)
```yaml
theory:
  classy:
    extra_args:
      N_ncdm: 1
      m_ncdm: 0.06
      deg_ncdm: 1
      N_ur: 2.0328
      T_cmb: 2.7255
      YHe: BBN
      non_linear: halofit
```
- **Why `classy` instead of `camb`**: Official SPT/ACT templates often default to `camb`, whereas this thesis uses **CLASS** (`classy`) to solve the Einstein–Boltzmann equations for $C_\ell^{TT,TE,EE,\phi\phi}$.
- **Why these `extra_args`**: All three baseline papers hold these standard $\Lambda\text{CDM}$ assumptions fixed:
  - **One massive neutrino with $\sum m_\nu = 0.06\text{ eV}$**: Set via `N_ncdm: 1` (number of non-cold dark matter species), `m_ncdm: 0.06`, `deg_ncdm: 1`.
  - **$N_{\text{eff}} = 3.046$**: Because 1 massive neutrino contributes $\sim 1.0132$ to $N_{\text{eff}}$, the remaining two massless ("ultra-relativistic") species are set to `N_ur: 2.0328` so $2.0328 + 1.0132 = 3.046$.
  - **`YHe: BBN` & `non_linear: halofit`**: Primordial helium abundance $Y_P$ is computed self-consistently from Big Bang Nucleosynthesis as a function of $\omega_b$, and non-linear matter power spectrum corrections use `halofit`.

#### B. `likelihood:` (The CMB Datasets)
- **Why "lite" / "CMB-only" likelihoods for SPT-3G and ACT DR6**:
  Full multi-frequency likelihoods fit individual $90/150/220\text{ GHz}$ cross-spectra and require **~35 nuisance parameters** (galactic dust, Poisson point sources, CIB, tSZ, kSZ, beam eigenmodes). Both collaborations provide official **foreground-marginalized ("lite" / "CMB-only")** likelihoods where foregrounds are analytically/numerically marginalized into the bandpower covariance matrix. This leaves only **2 calibration nuisance parameters** (`Tcal`/`Ecal` for SPT; `A_act`/`P_act` for ACT) and shifts cosmological parameters by $<0.1\sigma$.
- **Planck 2018 (`inputs/planck2018_baseline.yaml`)**:
  Uses Cobaya's built-in wrappers around the Planck 2018 `clik` files (evaluated via pure-Python `clipy-like`):
  1. `planck_2018_lowl.TT_clik` ($\ell = 2\text{–}29$ TT, Commander)
  2. `planck_2018_lowl.EE_clik` ($\ell = 2\text{–}29$ EE, SimAll — measures the low-$\ell$ reionization bump)
  3. `planck_2018_highl_plik.TTTEEE` ($\ell \ge 30$ multi-frequency TT, TE, EE; adds 21 `plik` nuisance parameters automatically)
  4. `planck_2018_lensing.clik` (CMB lensing potential power spectrum $C_\ell^{\phi\phi}$)
- **SPT-3G D1 (`inputs/spt3g_d1_baseline.yaml`) & ACT DR6 (`inputs/act_dr6_baseline.yaml`)**:
  Both use the differentiable `candl` likelihood package via Cobaya's external class hook:
  ```yaml
  likelihood:
    spt3g_d1_tne_lite:
      external: !!python/name:candl.interface.CandlCobayaLikelihood ''
      data_set_file: !!python/name:spt_candl_data.SPT3G_D1_TnE_lite ''
      clear_internal_priors: true
      feedback: true
  ```
  *(For ACT DR6, `data_set_file` is `!!python/name:candl_data.ACT_DR6_TTTEEE ''`.)*
  Setting `clear_internal_priors: true` disables `candl`'s built-in Gaussian priors so that we can define all priors explicitly in one place under Cobaya's `params:` block without double-counting them.

#### C. `params:` (Sampled, Nuisance, and Derived Parameters)
Every entry under `params:` is one of three types:
1. **Sampled parameters** (have a `prior:`):
   ```yaml
   omega_cdm:
     prior: {min: 0.001, max: 0.99}                 # flat prior [0.001, 0.99]
     ref: {dist: norm, loc: 0.12, scale: 0.001}     # initial starting distribution for chains
     proposal: 0.0005                               # fallback initial step size
     latex: \Omega_\mathrm{c} h^2
     renames: [omch2, omegach2]                     # aliases so CAMB covmats map cleanly
   ```
   - **The `logA` $\to$ `A_s` pattern**: We sample `logA` ($\ln(10^{10} A_s)$) with `drop: true` and pass `A_s: value: 'lambda logA: 1e-10*np.exp(logA)'` into CLASS, because the CMB posterior is Gaussian in $\ln A_s$.
   - **Why `theta_s_100` instead of `H0` (and not `100*theta_s`)**: Sampling the acoustic angular scale $100\theta_s$ instead of $H_0$ avoids strong geometric degeneracies and speeds up mixing. In Cobaya, parameter keys must be valid Python variable names (no `*`), so we use `theta_s_100`, which Cobaya's `classy` wrapper translates to CLASS's `100*theta_s`.
   - **Why $\tau_{\text{reio}}$ has a flat prior in Planck, but a Gaussian prior in SPT-3G and ACT**:
     - Planck includes `lowl.EE_clik` ($\ell < 30$), so it constrains $\tau_{\text{reio}}$ directly from the large-scale polarization bump (`prior: {min: 0.01, max: 0.8}`).
     - Ground-based telescopes (SPT-3G at $\ell \ge 400$, ACT DR6 at $\ell \ge 600$) only observe smaller angular scales where $A_s$ and $\tau$ are degenerate via $A_s e^{-2\tau}$. Both papers therefore apply a Planck-informed Gaussian prior on $\tau_{\text{reio}}$:
       - SPT-3G D1: `prior: {dist: norm, loc: 0.051, scale: 0.006}`
       - ACT DR6: `prior: {dist: norm, loc: 0.0566, scale: 0.0058}` (from Planck `Sroll2`)
   - **Calibration nuisance parameters**:
     - SPT-3G D1 `lite`: `Tcal` ($\mathcal{N}(1.0, 0.0036)$) and `Ecal` ($\mathcal{U}(0.8, 1.2)$).
     - ACT DR6 `CMB-only`: `A_act` ($\mathcal{N}(1.0, 0.003)$) and `P_act` ($\mathcal{U}(0.9, 1.1)$).
2. **Derived parameters computed by CLASS** (`H0`, `Omega_m`, `Omega_Lambda`, `sigma8`, `z_reio`, `YHe`, `age`, `rs_drag`):
   Listed with just `{latex: ...}` so Cobaya asks CLASS for them at each step and writes them to the chain.
3. **Derived parameters computed via Python expressions** (`omegamh2`, `s8h5`, `S8`):
   Defined with `derived: 'lambda sigma8, Omega_m: sigma8*(Omega_m/0.3)**0.5'`.
   Using **identical parameter names** across all three YAML files allows `GetDist` to plot all three experiments together without any post-hoc column renaming.

#### D. `sampler:` (Metropolis–Hastings MCMC Configuration)
```yaml
sampler:
  mcmc:
    covmat: auto            # or ../spt_candl_data/cobaya/SPT3G_D1_TnE/input_ttteee.covmat
    drag: true
    oversample_power: 0.4
    proposal_scale: 1.9
    Rminus1_stop: 0.01
    Rminus1_cl_stop: 0.2
    learn_proposal: true
    max_tries: 10000
```
- **`covmat`**: Provides an initial proposal covariance matrix so chains immediately step along the true parameter degeneracy directions.
- **`drag: true` & `oversample_power: 0.4`**: Enables Neal's fast/slow dragging. Because running CLASS takes $\sim 0.5\text{ s}$ ("slow" cosmological parameters) while re-evaluating the likelihood for calibration/foreground parameters takes $\sim 1\text{ ms}$ ("fast" nuisance parameters), Cobaya drags the fast parameters across many intermediate steps for each slow CLASS evaluation.
- **`Rminus1_stop: 0.01` & `Rminus1_cl_stop: 0.2`**: Stops when the Gelman–Rubin statistic across the 4 parallel MPI chains reaches $R - 1 < 0.01$ on parameter means and $< 0.2$ on the 95% credible interval bounds.

---

### 2. Cluster Scripts (`scripts/cluster/`) & Execution on RWTH CLAIX

1. **[`scripts/cluster/env.sh`](scripts/cluster/env.sh)**:
   Loads `GCC`, `OpenMPI`, and `Python/3.11.5`, and points `COBAYA_PACKAGES_PATH` and `UV_CACHE_DIR` to `$HPCWORK` (CLAIX's fast Lustre filesystem with large quota) rather than `$HOME`.
2. **[`scripts/cluster/setup_cluster.sh`](scripts/cluster/setup_cluster.sh)**:
   - Syncs the locked Python environment (`uv sync --locked --no-dev`).
   - Rebuilds `mpi4py` from source against CLAIX's OpenMPI (`MPICC="$(command -v mpicc)" uv pip install --reinstall --no-binary mpi4py mpi4py`) so multi-chain Slurm runs communicate properly.
   - Downloads the Planck 2018 `clik` data and covariance matrices into `$HPCWORK/cosmo-packages` via `cobaya-install`.
3. **[`run_planck2018.slurm`](scripts/cluster/run_planck2018.slurm), [`run_spt3g.slurm`](scripts/cluster/run_spt3g.slurm), [`run_act.slurm`](scripts/cluster/run_act.slurm)**:
   - Uses **hybrid MPI + OpenMP parallelization**:
     - `#SBATCH --ntasks=4` spawns **4 MPI ranks** (= 4 independent MCMC chains `chain.1.txt` … `chain.4.txt`).
     - `#SBATCH --cpus-per-task=8` gives each MPI rank **8 OpenMP threads** for CLASS's internal parallel perturbation solver (32 CPU cores total per job).
     - `srun --cpu-bind=cores .venv/bin/cobaya-run -r inputs/<name>.yaml` pins threads to physical cores and passes `-r` (`--resume`) so interrupted jobs continue from `chain.checkpoint`.

#### Syncing Chains from CLAIX to Local Machine
Because `chains/` is ~65 MB, it is excluded from git via `.gitignore`. To download the chains and plots from CLAIX on any machine:
```bash
rsync -avz claix:~/thesis_code/Code/chains/ chains/
```

---

### 3. Cluster Run Summary & Posterior Verification (`scripts/plot_chains.py`)

All three jobs converged on the `c23ms` partition (`R-1 < 0.01`):

| Run | Runtime | Accepted Steps (4 chains) | Acceptance Rate | $R - 1$ (means) | $R - 1$ (95% bounds) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Planck 2018** (`planck2018_baseline`) | `17h 21m` | `52,039` | `0.358` | `0.00967` | `0.0450` |
| **SPT-3G D1** (`spt3g_d1_baseline`) | `04h 32m` | `14,665` | `0.369` | `0.00929` | `0.0630` |
| **ACT DR6** (`act_dr6_baseline`) | `17h 03m` | `27,006` | `0.370` | `0.00790` | `0.0674` |

Running `uv run python scripts/plot_chains.py` loads all 4 chains per experiment via `GetDist` (discarding the first 30% as burn-in), saves `chains/comparison_triangle_plot.png` and `chains/comparison_table.tex`, and compares the 68% credible intervals against the published papers:

#### Planck 2018 (`TT,TE,EE+lowE+lensing`) vs. Planck 2018 VI (arXiv:1807.06209, Table 2)
| Parameter | This Work ($68\%$ CI) | Planck 2018 VI | Agreement |
| :--- | :--- | :--- | :--- |
| $\Omega_b h^2$ | $0.02236 \pm 0.00015$ | $0.02237 \pm 0.00015$ | $< 0.1\sigma$ |
| $\Omega_c h^2$ | $0.1199 \pm 0.0012$ | $0.1200 \pm 0.0012$ | $< 0.1\sigma$ |
| $100\theta_s$ | $1.04185 \pm 0.00029$ | $1.04110 \pm 0.00031^\dagger$ | Expected ($100\theta_s$ vs. $100\theta_{\mathrm{MC}}$) |
| $\tau_{\mathrm{reio}}$ | $0.0542 \pm 0.0074$ | $0.0544 \pm 0.0073$ | $< 0.1\sigma$ |
| $\log(10^{10} A_s)$ | $3.044 \pm 0.014$ | $3.044 \pm 0.014$ | Exact |
| $n_s$ | $0.9647 \pm 0.0041$ | $0.9649 \pm 0.0042$ | $< 0.1\sigma$ |
| $H_0$ | $67.37 \pm 0.54$ | $67.36 \pm 0.54$ | $< 0.1\sigma$ |
| $\Omega_m$ | $0.3150 \pm 0.0075$ | $0.3153 \pm 0.0073$ | $< 0.1\sigma$ |
| $\sigma_8$ | $0.8104 \pm 0.0059$ | $0.8111 \pm 0.0060$ | $0.1\sigma$ |
| $S_8$ | $0.830 \pm 0.013$ | $0.832 \pm 0.013$ | $0.15\sigma$ |

#### SPT-3G D1 (`TT,TE,EE SPTlite`) vs. Camphuis et al. (2025)
| Parameter | This Work ($68\%$ CI) | SPT-3G D1 Paper | Agreement |
| :--- | :--- | :--- | :--- |
| $\Omega_b h^2$ | $0.02218 \pm 0.00022$ | $0.02221 \pm 0.00020$ | $0.15\sigma$ |
| $\Omega_c h^2$ | $0.1218 \pm 0.0031$ | $0.1222 \pm 0.0030$ | $0.13\sigma$ |
| $100\theta_s$ | $1.04170 \pm 0.00062$ | $1.04067 \pm 0.00060^\dagger$ | Expected ($100\theta_s$ vs. $100\theta_{\mathrm{MC}}$) |
| $\tau_{\mathrm{reio}}$ | $0.0509 \pm 0.0061$ | $0.0510 \pm 0.0058$ | $< 0.1\sigma$ |
| $\log(10^{10} A_s)$ | $3.057 \pm 0.016$ | $3.056 \pm 0.016$ | $< 0.1\sigma$ |
| $n_s$ | $0.949 \pm 0.013$ | $0.949 \pm 0.013$ | Exact |
| $H_0$ | $66.5 \pm 1.2$ | $66.66 \pm 1.20$ | $0.1\sigma$ |
| $\sigma_8$ | $0.818 \pm 0.012$ | — | — |
| $S_8$ | $0.854 \pm 0.035$ | — | — |

#### ACT DR6 (`TT,TE,EE CMB-only`) vs. Louis et al. (2025, arXiv:2503.14452, Table 5 `ACT` column)
| Parameter | This Work ($68\%$ CI) | Louis et al. 2025 (`ACT` alone) | Agreement |
| :--- | :--- | :--- | :--- |
| $\Omega_b h^2$ | $0.02253 \pm 0.00017$ | $0.02259 \pm 0.00017$ | $0.35\sigma$ |
| $\Omega_c h^2$ | $0.1238 \pm 0.0021$ | $0.1238 \pm 0.0021$ | Exact |
| $100\theta_s$ | $1.04155 \pm 0.00031$ | $1.04075 \pm 0.00031^\dagger$ | Expected ($100\theta_s$ vs. $100\theta_*$) |
| $\tau_{\mathrm{reio}}$ | $0.0565 \pm 0.0057$ | $0.0562^{+0.0053}_{-0.0063}$ | $< 0.1\sigma$ |
| $\log(10^{10} A_s)$ | $3.053 \pm 0.013$ | $3.053 \pm 0.013$ | Exact |
| $n_s$ | $0.9683 \pm 0.0074$ | $0.9666 \pm 0.0077$ | $0.2\sigma$ |
| $H_0$ | $66.11 \pm 0.77$ | $66.11 \pm 0.79$ | Exact |
| $\Omega_m$ | $0.336 \pm 0.013$ | $0.337 \pm 0.013$ | $< 0.1\sigma$ |
| $\sigma_8$ | $0.8263 \pm 0.0077$ | $0.8263 \pm 0.0074$ | Exact |
| $S_8$ | $0.875 \pm 0.023$ | $0.875 \pm 0.023$ | Exact |

*($^\dagger$The $\sim 0.0008\text{–}0.0010$ shift in $100\theta_s$ is the standard definition offset between CLASS's exact sound-horizon angle `theta_s_100` and CAMB/CosmoMC's `theta_MC_100` / $\theta_*$ conventions reported in the paper tables.)*

---

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
