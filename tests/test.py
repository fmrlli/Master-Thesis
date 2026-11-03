#!/usr/bin/env python3
"""
test.py -- Practical Guide to CLASS for CMB Data Analysis (Planck, ACT, SPT)
=============================================================================

This tutorial script introduces the core CLASS (`classy`) functions and physics
routines essential for CMB data analysis and cosmological parameter estimation.

Key topics covered:
1. Standard CMB parameterization (omega_b, omega_cdm, 100*theta_s, ln10^10A_s, n_s, tau).
2. Lensed and unlensed temperature & polarization spectra (TT, TE, EE, BB).
3. CMB lensing potential and convergence spectra (phi-phi, kappa-kappa).
4. Multipole coverage of primary experiments:
   - Planck: full sky, l in [2, 2500]
   - ACT (DR4/DR6): ground-based high-res, l in [350, 4500+]
   - SPT (SPT-3G): deep southern patch, l in [300, 4000+]
5. Physics of parameter sensitivities (Silk damping, N_eff, baryon loading).

Run with:
    uv run python test.py                      # Print summaries & show 4-panel figure
    uv run python test.py --no-show            # Print numbers only (headless)
    uv run python test.py --save cmb_tour.png  # Save figure to disk
"""

from __future__ import annotations

import argparse
from typing import Any, Dict, Tuple

import matplotlib.pyplot as plt
import numpy as np
from classy import Class

# Physical constants
T_CMB_K = 2.7255  # Mean CMB temperature in Kelvin (FIRAS)
T_CMB_MUK = T_CMB_K * 1e6  # CMB temperature in microKelvin [muK]

# Multipole ranges for key CMB experiments
EXPERIMENTS = {
    "Planck": {"lmin": 2, "lmax": 2500, "color": "#00a8ff", "alpha": 0.12},
    "SPT-3G": {"lmin": 300, "lmax": 4000, "color": "#fbc531", "alpha": 0.15},
    "ACT DR6": {"lmin": 350, "lmax": 4500, "color": "#9c85ff", "alpha": 0.12},
}


def get_planck2018_baseline() -> Dict[str, Any]:
    """
    Standard Planck 2018 base-LCDM parameters (TT,TE,EE+lowE+lensing).
    CMB analyses typically parameterize cosmology via {omega_b, omega_cdm, 100*theta_s}
    rather than {Omega_m, H0} because theta_s is directly observed with ~0.03% precision.
    """
    return {
        "output": "tCl,pCl,lCl",  # Temperature, Polarization, and Lensing spectra
        "lensing": "yes",  # Compute lensed CMB spectra
        "l_max_scalars": 4500,  # Reach ACT / SPT damping tail
        # Primordial & background parameters
        "omega_b": 0.02237,  # Omega_b * h^2
        "omega_cdm": 0.1200,  # Omega_cdm * h^2
        "100*theta_s": 1.04092,  # 100 * angular sound horizon at decoupling
        "ln10^{10}A_s": 3.044,  # Primordial amplitude log(10^10 A_s)
        "n_s": 0.9649,  # Scalar spectral index
        "tau_reio": 0.0544,  # Optical depth to reionization
        # Neutrino baseline: 1 massive eigenstate (0.06 eV) + 2 massless
        "N_ur": 2.0328,
        "N_ncdm": 1,
        "m_ncdm": 0.06,
        "T_ncdm": 0.71611,
    }


def compute_spectra(
    param_dict: Dict[str, Any], lmax: int = 4500
) -> Tuple[Class, Dict[str, np.ndarray]]:
    """
    Run CLASS with given parameters and return the Class instance and spectra dict.
    Converts raw dimensionless CLASS C_l into D_l [muK^2] and lensing D_l^kappa.
    """
    cosmo = Class()
    cfg = dict(param_dict)
    cfg["l_max_scalars"] = lmax
    cosmo.set(cfg)
    cosmo.compute()

    # Raw (unlensed) and lensed spectra
    raw = cosmo.raw_cl(lmax)
    lensed = cosmo.lensed_cl(lmax)
    ell = lensed["ell"]

    # Prefactor to convert dimensionless C_l (Delta T / T)^2 to D_l in muK^2:
    # D_l = l * (l + 1) / (2 * pi) * C_l * T_CMB^2
    pref = ell * (ell + 1.0) / (2.0 * np.pi) * (T_CMB_MUK**2)

    data = {
        "ell": ell,
        # Lensed D_l [muK^2]
        "dl_tt": pref * lensed["tt"],
        "dl_ee": pref * lensed["ee"],
        "dl_te": pref * lensed["te"],
        "dl_bb": pref * lensed["bb"],
        # Unlensed D_l [muK^2] (to inspect lensing peak-smoothing)
        "dl_tt_unl": pref * raw["tt"],
        "dl_ee_unl": pref * raw["ee"],
        # CMB Lensing Potential C_L^phi and Convergence D_L^kappa
        # kappa_LM = L*(L+1)/2 * phi_LM  =>  C_L^kappa = [L*(L+1)]^2 / 4 * C_L^phi
        # D_L^kappa = L*(L+1)/(2*pi) * C_L^kappa = [L*(L+1)]^3 / (8*pi) * C_L^phi (dimensionless)
        "cl_pp": lensed["pp"],
        "dl_kk": (ell * (ell + 1.0)) ** 3 / (8.0 * np.pi) * lensed["pp"],
    }
    return cosmo, data


def print_cmb_summary(cosmo: Class, data: Dict[str, np.ndarray]) -> None:
    """Print key CMB quantities and acoustic peak locations."""
    h = cosmo.h()
    H0 = h * 100.0
    ell = data["ell"]
    dl_tt = data["dl_tt"]

    print("=" * 70)
    print("  CMB DATA ANALYSIS: CLASS SUMMARY & ACOUSTIC PEAKS")
    print("=" * 70)
    print(f"  Derived H0             : {H0:.2f} km/s/Mpc (h = {h:.4f})")
    print(f"  Sound horizon r_s(drag): {cosmo.rs_drag():.2f} Mpc")
    print(f"  Angular size 100*theta : {cosmo.theta_s_100():.5f} deg")
    print(f"  Reionization tau       : {cosmo.tau_reio():.4f} (z_reio = {cosmo.z_reio():.2f})")
    print("-" * 70)

    # Locate acoustic peaks in TT spectrum
    print("  Acoustic Peak Locations (TT):")
    windows = [
        ("1st peak (Compression)", 150, 320),
        ("2nd peak (Rarefaction)", 380, 650),
        ("3rd peak (Compression)", 680, 950),
        ("4th peak (Rarefaction)", 1000, 1300),
    ]
    for name, lmin, lmax in windows:
        mask = (ell >= lmin) & (ell <= lmax)
        idx = np.argmax(dl_tt[mask])
        l_peak = ell[mask][idx]
        amp = dl_tt[mask][idx]
        print(f"    {name:<24}: l = {l_peak:<4}  D_l^TT = {amp:,.1f} muK^2")

    print("-" * 70)
    print("  Experimental Multipole Coverage:")
    for exp, vals in EXPERIMENTS.items():
        print(f"    {exp:<10}: l in [{vals['lmin']}, {vals['lmax']}]")
    print("=" * 70 + "\n")


def plot_cmb_tour(
    data_fid: Dict[str, np.ndarray],
    data_neff: Dict[str, np.ndarray],
    data_baryon: Dict[str, np.ndarray],
    save_path: str | None = None,
    show: bool = True,
) -> None:
    """
    Generate a 4-panel figure illustrating CMB observables across Planck, ACT, and SPT.
    """
    plt.rcParams.update({"axes.grid": True, "grid.alpha": 0.35, "font.size": 10})
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle(
        "CLASS for CMB Analysis: Spectra, Lensing & Experiment Sensitivity (Planck / SPT / ACT)",
        fontsize=13,
        fontweight="bold",
    )

    ell = data_fid["ell"]
    m = (ell >= 2) & (ell <= 4500)

    # -------------------------------------------------------------------------
    # Panel 1: Primary Temperature and Polarization Spectra
    # -------------------------------------------------------------------------
    ax = axes[0, 0]
    ax.loglog(ell[m], data_fid["dl_tt"][m], "k-", lw=1.8, label=r"$TT$")
    ax.loglog(ell[m], data_fid["dl_ee"][m], "C0-", lw=1.4, label=r"$EE$")
    ax.loglog(ell[m], np.abs(data_fid["dl_te"][m]), "C1--", lw=1.2, label=r"$|TE|$")
    ax.loglog(ell[m], data_fid["dl_bb"][m], "C2-", lw=1.4, label=r"$BB$ (lensing)")

    # Overlay experiment coverage bands
    for exp, vals in EXPERIMENTS.items():
        ax.axvspan(
            vals["lmin"],
            vals["lmax"],
            color=vals["color"],
            alpha=vals["alpha"],
            label=f"{exp} ({vals['lmin']}-{vals['lmax']})",
        )

    ax.set_xlim(2, 4500)
    ax.set_ylim(1e-4, 8e3)
    ax.set_xlabel(r"Multipole $\ell$")
    ax.set_ylabel(r"$D_\ell = \ell(\ell+1)C_\ell / 2\pi\ \ [\mu\mathrm{K}^2]$")
    ax.set_title("1. Lensed CMB Power Spectra & Experiment Bands")
    ax.legend(loc="lower left", fontsize=8, ncol=2)

    # -------------------------------------------------------------------------
    # Panel 2: The Damping Tail (Why ACT & SPT Matter)
    # -------------------------------------------------------------------------
    ax = axes[0, 1]
    m_damp = (ell >= 800) & (ell <= 4500)
    ax.semilogy(
        ell[m_damp], data_fid["dl_tt"][m_damp], "k-", lw=1.8, label=r"$TT$ (lensed)"
    )
    ax.semilogy(
        ell[m_damp],
        data_fid["dl_tt_unl"][m_damp],
        "k:",
        lw=1.2,
        label=r"$TT$ (unlensed)",
    )
    ax.semilogy(
        ell[m_damp], data_fid["dl_ee"][m_damp], "C0-", lw=1.4, label=r"$EE$ (lensed)"
    )

    # Shaded ACT and SPT high-l coverage
    ax.axvspan(
        2500,
        4500,
        color="#9c88ff",
        alpha=0.18,
        label=r"ACT & SPT High-$\ell$ Regime (Beyond Planck)",
    )
    ax.axvline(2500, color="gray", ls="--", lw=1.0, label=r"Planck $\ell_{\max} \approx 2500$")

    ax.set_xlim(800, 4500)
    ax.set_ylim(1e-2, 3e3)
    ax.set_xlabel(r"Multipole $\ell$")
    ax.set_ylabel(r"$D_\ell\ \ [\mu\mathrm{K}^2]$")
    ax.set_title("2. Silk Damping Tail & Lensing Peak-Smoothing")
    ax.legend(loc="upper right", fontsize=8)

    # -------------------------------------------------------------------------
    # Panel 3: CMB Lensing Convergence Power Spectrum (phi-phi / kappa-kappa)
    # -------------------------------------------------------------------------
    ax = axes[1, 0]
    m_lens = (ell >= 10) & (ell <= 3000)
    ax.plot(ell[m_lens], data_fid["dl_kk"][m_lens] * 1e4, "C3-", lw=2.0, label=r"$10^4 \times D_L^{\kappa\kappa}$")
    ax.axvspan(
        100,
        1500,
        color="#2ecc71",
        alpha=0.12,
        label=r"Primary Lensing Kernel ($z \sim 1-3$)",
    )
    ax.set_xlim(10, 3000)
    ax.set_xlabel(r"Lensing Multipole $L$")
    ax.set_ylabel(r"$10^4 \times [L(L+1)]^2 C_L^{\phi\phi} / 4\pi$")
    ax.set_title(r"3. CMB Lensing Potential / Convergence ($C_L^{\kappa\kappa}$)")
    ax.legend(loc="upper right", fontsize=8)

    # -------------------------------------------------------------------------
    # Panel 4: Parameter Sensitivities (N_eff & Baryons)
    # -------------------------------------------------------------------------
    ax = axes[1, 1]
    m_sens = (ell >= 50) & (ell <= 4000)

    # Fractional differences in TT: (D_l(alt) / D_l(fid) - 1) * 100%
    with np.errstate(divide="ignore", invalid="ignore"):
        frac_neff = np.where(
            data_fid["dl_tt"] > 0,
            (data_neff["dl_tt"] / data_fid["dl_tt"] - 1.0) * 100.0,
            0.0,
        )
        frac_baryon = np.where(
            data_fid["dl_tt"] > 0,
            (data_baryon["dl_tt"] / data_fid["dl_tt"] - 1.0) * 100.0,
            0.0,
        )

    ax.plot(
        ell[m_sens],
        frac_neff[m_sens],
        color="#e84118",
        lw=1.6,
        label=r"Extra Radiation ($\Delta N_{\rm eff} = +0.5$)",
    )
    ax.plot(
        ell[m_sens],
        frac_baryon[m_sens],
        color="#273c75",
        lw=1.6,
        label=r"Baryon Density ($\Delta \omega_b / \omega_b = +5\%$)",
    )
    ax.axhline(0, color="k", ls=":", lw=0.8)

    # Highlight why ground-based CMB is sensitive to N_eff:
    # N_eff increases the damping scale, causing a larger suppression at high l (ACT/SPT)
    ax.axvspan(
        2000,
        4000,
        color="#9c88ff",
        alpha=0.12,
        label=r"ACT/SPT High-$\ell$ Lever Arm",
    )

    ax.set_xlim(50, 4000)
    ax.set_ylim(-15, 15)
    ax.set_xlabel(r"Multipole $\ell$")
    ax.set_ylabel(r"$\Delta D_\ell / D_\ell\ [\%]$")
    ax.set_title(r"4. Parameter Sensitivity (Fractional $\Delta D_\ell^{TT}$)")
    ax.legend(loc="lower left", fontsize=8)

    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches="tight")
        print(f"  [Figure saved to {save_path}]")
    if show:
        plt.show()


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--lmax", type=int, default=4500, help="Max multipole for CMB (default: 4500)"
    )
    parser.add_argument(
        "--save", metavar="PATH", help="Save the summary figure to file (e.g. cmb_tour.png)"
    )
    parser.add_argument(
        "--no-show", action="store_true", help="Run headlessly without opening window"
    )
    args = parser.parse_args()

    # 1. Base Planck 2018 LCDM
    fid_params = get_planck2018_baseline()
    cosmo_fid, data_fid = compute_spectra(fid_params, lmax=args.lmax)

    try:
        # 2. Perturbation: Extra Relativistic Species (N_eff = 3.54 instead of 3.046)
        # N_eff enhances Silk damping at l > 2000 (key ACT/SPT science target)
        neff_params = dict(fid_params)
        neff_params["N_ur"] = fid_params["N_ur"] + 0.5
        cosmo_neff, data_neff = compute_spectra(neff_params, lmax=args.lmax)
        cosmo_neff.struct_cleanup()
        cosmo_neff.empty()

        # 3. Perturbation: Baryon density (+5% omega_b)
        # Changes odd/even acoustic peak balance
        baryon_params = dict(fid_params)
        baryon_params["omega_b"] = fid_params["omega_b"] * 1.05
        cosmo_baryon, data_baryon = compute_spectra(baryon_params, lmax=args.lmax)
        cosmo_baryon.struct_cleanup()
        cosmo_baryon.empty()

        # Print educational summary
        print_cmb_summary(cosmo_fid, data_fid)

        # Plot 4-panel diagnostic figure
        plot_cmb_tour(
            data_fid,
            data_neff,
            data_baryon,
            save_path=args.save,
            show=not args.no_show,
        )

    finally:
        # Proper cleanup of CLASS internal C structures
        cosmo_fid.struct_cleanup()
        cosmo_fid.empty()


if __name__ == "__main__":
    main()
