"""
Load converged MCMC chains for Planck 2018, SPT-3G D1, and ACT DR6,
produce a joint GetDist triangle plot, and compare parameter values
against the official published paper tables.

Usage (from Code/):
    .venv/bin/python scripts/plot_chains.py
"""

from pathlib import Path
import matplotlib.pyplot as plt
from getdist import loadMCSamples
from getdist.types import ResultTable
import getdist.plots as gdplt

CODE_DIR = Path(__file__).resolve().parent.parent
CHAINS_DIR = CODE_DIR / "chains"

# Chains to look for (in order of plotting)
EXPERIMENTS = [
    ("Planck 2018 (TT,TE,EE+lowE+lens)", CHAINS_DIR / "planck2018_baseline" / "chain"),
    ("SPT-3G D1 (TT,TE,EE SPTlite)", CHAINS_DIR / "spt3g_d1_baseline" / "chain"),
    ("ACT DR6 (TT,TE,EE CMB-only)", CHAINS_DIR / "act_dr6_baseline" / "chain"),
]

# Published reference values (mean +/- 1 sigma) from the official papers:
#  - Planck 2018 VI (arXiv:1807.06209), Table 2, "TT,TE,EE+lowE+lensing"
#  - SPT-3G D1 (Camphuis et al. 2025, arXiv:2502.19475), LCDM TT,TE,EE + tau prior
#  - ACT DR6 (Louis et al. 2025, arXiv:2503.14452), Table 5, "ACT" (CMB-only + tau prior)
PAPER_REFERENCES = {
    "Planck 2018 (TT,TE,EE+lowE+lens)": {
        "omega_b": (0.02237, 0.00015),
        "omega_cdm": (0.1200, 0.0012),
        "theta_s_100": (1.04110, 0.00031),
        "tau_reio": (0.0544, 0.0073),
        "logA": (3.044, 0.014),
        "n_s": (0.9649, 0.0042),
        "H0": (67.36, 0.54),
        "Omega_m": (0.3153, 0.0073),
        "sigma8": (0.8111, 0.0060),
        "S8": (0.832, 0.013),
    },
    "SPT-3G D1 (TT,TE,EE SPTlite)": {
        "omega_b": (0.02221, 0.00020),
        "omega_cdm": (0.1222, 0.0030),
        "theta_s_100": (1.04067, 0.00060),
        "tau_reio": (0.0510, 0.0058),
        "logA": (3.056, 0.016),
        "n_s": (0.949, 0.013),
        "H0": (66.66, 1.20),
    },
    "ACT DR6 (TT,TE,EE CMB-only)": {
        "omega_b": (0.02259, 0.00017),
        "omega_cdm": (0.1238, 0.0021),
        "theta_s_100": (1.04075, 0.00031),
        "tau_reio": (0.0562, 0.0058),
        "logA": (3.053, 0.013),
        "n_s": (0.9666, 0.0077),
        "H0": (66.11, 0.79),
        "Omega_m": (0.337, 0.013),
        "sigma8": (0.8263, 0.0074),
        "S8": (0.875, 0.023),
    },
}

PLOT_PARAMS = [
    "omega_b",
    "omega_cdm",
    "theta_s_100",
    "tau_reio",
    "logA",
    "n_s",
    "H0",
    "sigma8",
    "S8",
]


def main():
    loaded_samples = []
    loaded_labels = []

    for label, prefix in EXPERIMENTS:
        chain_files = list(prefix.parent.glob(f"{prefix.name}.*.txt"))
        if not chain_files:
            print(f"[skip] No chain files found yet at {prefix}.*.txt")
            continue
        print(f"[load] Loading {label} from {prefix} ...")
        samples = loadMCSamples(str(prefix), settings={"ignore_rows": 0.3})
        loaded_samples.append(samples)
        loaded_labels.append(label)

    if not loaded_samples:
        print("No chains found in chains/{planck2018_baseline,spt3g_d1_baseline,act_dr6_baseline}/.")
        return

    # 1. Joint triangle plot
    gdplot = gdplt.get_subplot_plotter(width_inch=12)
    gdplot.settings.legend_fontsize = 12
    gdplot.settings.axes_labelsize = 12

    # Overlay Planck 2018 official central values as dashed reference markers
    planck_markers = {
        k: v[0]
        for k, v in PAPER_REFERENCES["Planck 2018 (TT,TE,EE+lowE+lens)"].items()
    }

    gdplot.triangle_plot(
        loaded_samples,
        PLOT_PARAMS,
        filled=True,
        legend_labels=loaded_labels,
        legend_loc="upper right",
        markers=planck_markers,
    )
    out_fig = CHAINS_DIR / "comparison_triangle_plot.png"
    plt.savefig(out_fig, dpi=200, bbox_inches="tight")
    print(f"\nSaved triangle plot to: {out_fig}")

    # 2. Side-by-side comparison against published paper values
    for label, smp in zip(loaded_labels, loaded_samples):
        print(f"\n{'=' * 72}")
        print(f"  {label}")
        print(f"{'=' * 72}")
        print(f"  {'Parameter':<14} | {'Your MCMC (68% CI)':<28} | {'Paper Reference':<22}")
        print(f"  {'-' * 14}-+-{'-' * 28}-+-{'-' * 22}")
        refs = PAPER_REFERENCES.get(label, {})
        for p in PLOT_PARAMS:
            if smp.getParamNames().parWithName(p) is None:
                continue
            mcmc_str = smp.getInlineLatex(p, limit=1)
            if p in refs:
                ref_mean, ref_std = refs[p]
                ref_str = f"{ref_mean} +/- {ref_std}"
            else:
                ref_str = "—"
            print(f"  {p:<14} | {mcmc_str:<28} | {ref_str:<22}")

    # 3. LaTeX table for thesis
    latex_out = CHAINS_DIR / "comparison_table.tex"
    table_tex = ResultTable(
        ncol=1,
        results=loaded_samples,
        limit=1,
        titles=loaded_labels,
        paramList=PLOT_PARAMS,
    ).tableTex()
    latex_out.write_text(table_tex)
    print(f"\nSaved LaTeX parameter table to: {latex_out}")


if __name__ == "__main__":
    main()
