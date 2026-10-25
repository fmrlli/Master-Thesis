#!/usr/bin/env python
"""
test.py -- a guided tour of the CLASS Boltzmann code through its `classy` wrapper.

Prints background cosmology, CMB spectra, the matter power spectrum, distances
and the thermal history for a Planck 2018 best-fit LCDM model, then shows a
six-panel figure.

    uv run python test.py                       # print + show the figure
    uv run python test.py --no-show             # numbers only (headless)
    uv run python test.py --save tour.png       # also write the figure
    uv run python test.py --baseline p18lb      # lensing + BAO best fit
"""

from __future__ import annotations

import argparse

import matplotlib.pyplot as plt
import numpy as np
from classy import Class

C_KM_S = 299792.458


# --------------------------------------------------------------------------- #
# printing helpers
# --------------------------------------------------------------------------- #
def section(title: str) -> None:
    print(f"\n{title}\n{'-' * len(title)}")


def kv(label: str, value, unit: str = "") -> None:
    text = (
        f"{value:.6g}" if isinstance(value, (int, float, np.floating)) else str(value)
    )
    print(f"  {label:<32}{text:>16}  {unit}")


def print_table(headers, rows) -> None:
    cols = list(zip(*([tuple(headers)] + [tuple(r) for r in rows])))
    widths = [max(len(str(c)) for c in col) for col in cols]

    def line(cells):
        print("  " + "  ".join(f"{c!s:>{w}}" for c, w in zip(cells, widths)))

    line(headers)
    print("  " + "  ".join("-" * w for w in widths))
    for row in rows:
        line(row)


def peak(ell, dls, lo, hi):
    """(l, D_l) of the maximum of dls inside the window [lo, hi]."""
    m = (ell >= lo) & (ell <= hi)
    i = int(np.argmax(dls[m]))
    return int(ell[m][i]), float(dls[m][i])


# --------------------------------------------------------------------------- #
# cosmology
# --------------------------------------------------------------------------- #
def build_cosmology(baseline: str, lmax: int) -> Class:
    cosmo = Class()
    cosmo.set_baseline(baseline)  # e.g. planck2018 / p18l / p18lb
    cosmo.set(
        {
            "non_linear": "halofit",  # P(k) non-linear correction
            "l_max_scalars": lmax,
            "P_k_max_h/Mpc": 50.0,  # k reach for sigma(R), sigma8(z)
            "z_max_pk": 5.0,  # P(k,z) tabulated up to z = 5
        }
    )
    cosmo.compute()
    return cosmo


def report_model(c: Class, baseline: str) -> None:
    section(f"1. Cosmology  [{baseline}: Planck 2018 best fit + base-LCDM]")
    kv("H0", c.h() * 100.0, "km/s/Mpc")  # note: c.H0() is H0/c in 1/Mpc
    kv("h", c.h())
    kv("T_cmb", c.T_cmb(), "K")
    kv("N_eff", c.Neff())
    kv("Omega_b", c.Omega_b())
    kv("Omega_cdm", c.Omega_cdm())
    kv("Omega_m", c.Omega_m())
    kv("Omega_Lambda", c.Omega_Lambda())
    kv("Omega_r", c.Omega_r())
    kv("Omega_nu", c.Omega_nu())
    kv("Omega_k", c.Omega_k())
    kv("n_s", c.n_s())
    kv("z_reio", c.z_reio())
    kv("tau_reio", c.tau_reio())


def report_background(c: Class) -> None:
    section("2. Background and derived quantities")
    kv("age of the universe", c.age(), "Gyr")
    kv("z_eq (matter-radiation)", c.z_eq())
    kv("k_eq", c.k_eq(), "1/Mpc")
    kv("r_s,drag", c.rs_drag(), "Mpc")
    kv("100 * theta_s", c.theta_s_100())
    kv("sigma8 (z=0)", c.sigma8())
    kv("S8", c.S8())
    knl = c.nonlinear_scale(np.array([0.0]), 1)[0]
    kv("k_nl (z=0)", knl * c.h(), "h/Mpc")


def report_cmb(c: Class, lmax: int) -> None:
    section(f"3. CMB spectra (lensed, l_max = {lmax})")
    cl = c.lensed_cl(lmax)
    ell = cl["ell"]

    # classy returns dimensionless C_l's (Delta T / T); go to muK^2
    t_muK2 = (c.T_cmb() * 1e6) ** 2

    def dl(x):
        return ell * (ell + 1.0) / (2.0 * np.pi) * x * t_muK2

    tt, ee, te, bb = dl(cl["tt"]), dl(cl["ee"]), dl(cl["te"]), dl(cl["bb"])

    rows = []
    for name, lo, hi in [
        ("1st acoustic", 150, 350),
        ("2nd acoustic", 350, 600),
        ("3rd acoustic", 600, 1000),
    ]:
        ltt, vtt = peak(ell, tt, lo, hi)
        lee, vee = peak(ell, ee, lo, hi)
        rows.append((name, ltt, f"{vtt:,.0f}", lee, f"{vee:,.1f}"))
    print_table(["peak", "l_TT", "D_TT [muK^2]", "l_EE", "D_EE [muK^2]"], rows)

    sw = tt[(ell >= 2) & (ell <= 10)].mean()
    kv("Sachs-Wolfe plateau (2<l<10)", sw, "muK^2")
    kv("D_TE at l = 200", float(np.interp(200, ell, te)), "muK^2")
    kv("D_BB (lensing) at l = 1000", float(np.interp(1000, ell, bb)), "muK^2")


def report_pk(c: Class) -> None:
    section("4. Matter power spectrum P(k, z)")
    h = c.h()

    rows = []
    for k_h in [1e-3, 1e-2, 1e-1, 5e-1, 1.0]:
        k = k_h * h  # 1/Mpc
        p_lin = c.pk_lin(k, 0.0) * h**3  # (Mpc/h)^3
        p_nl = c.pk(k, 0.0) * h**3
        rows.append(
            (f"{k_h:g}", f"{p_lin:,.4g}", f"{p_nl:,.4g}", f"{p_nl / p_lin:.3f}")
        )
    print("  z = 0")
    print_table(
        ["k [h/Mpc]", "P_lin [(Mpc/h)^3]", "P_nl [(Mpc/h)^3]", "P_nl/P_lin"], rows
    )

    zs = np.array([0.0, 0.5, 1.0, 2.0])
    knl = c.nonlinear_scale(zs, len(zs)) * h  # h/Mpc
    print()
    rows = [
        (f"{z:g}", f"{c.sigma(8.0, z, h_units=True):.4f}", f"{knl[i]:.4f}")
        for i, z in enumerate(zs)
    ]
    print_table(["z", "sigma8(z)", "k_nl(z) [h/Mpc]"], rows)


def report_distances(c: Class) -> None:
    section("5. Distances, expansion rate and growth")
    rows = []
    for z in [0.1, 0.5, 1.0, 2.0, 5.0, 1089.0]:
        rows.append(
            (
                f"{z:g}",
                f"{c.comoving_distance(z):,.1f}",
                f"{c.angular_distance(z):,.1f}",
                f"{c.luminosity_distance(z):,.1f}",
                f"{c.Hubble(z) * C_KM_S:,.1f}",
                f"{c.scale_independent_growth_factor(z):.4f}",
                f"{c.scale_independent_growth_factor_f(z):.4f}",
            )
        )
    print_table(
        ["z", "D_C [Mpc]", "D_A [Mpc]", "D_L [Mpc]", "H(z) [km/s/Mpc]", "D(z)", "f(z)"],
        rows,
    )


def report_thermo(c: Class) -> None:
    section("6. Thermal history")
    th = c.get_thermodynamics()
    z, x_e = np.asarray(th["z"]), np.asarray(th["x_e"])  # both ascending
    kv("x_e (z=0)", float(np.interp(0.0, z, x_e)))
    kv("x_e (z=1100)", float(np.interp(1100.0, z, x_e)))
    zz = np.linspace(900.0, 1600.0, 4000)  # x_e falls from 1 to ~0 here
    xe_zz = np.interp(zz, z, x_e)
    kv("z at which x_e = 0.5", float(zz[int(np.argmin(np.abs(xe_zz - 0.5)))]))
    kv("T_baryon (z=1100)", c.baryon_temperature(1100.0), "K")


# --------------------------------------------------------------------------- #
# figure
# --------------------------------------------------------------------------- #
def make_figure(
    c: Class, lmax: int, baseline: str, save: str | None, show: bool
) -> None:
    plt.rcParams.update({"figure.dpi": 110, "axes.grid": True, "grid.alpha": 0.3})
    fig, ax = plt.subplots(2, 3, figsize=(15.5, 8.5))
    fig.suptitle(
        f"CLASS / classy tour -- {baseline} (Planck 2018 best fit)", fontsize=13
    )

    h = c.h()
    t_muK2 = (c.T_cmb() * 1e6) ** 2
    cl = c.lensed_cl(lmax)
    ell = cl["ell"]

    def dl(x):
        return ell * (ell + 1.0) / (2.0 * np.pi) * x * t_muK2

    # (a) CMB TT / EE / BB
    a = ax[0, 0]
    a.loglog(ell[2:], dl(cl["tt"])[2:], "k-", lw=1.2, label=r"$TT$")
    a.loglog(ell[2:], dl(cl["ee"])[2:], "C0-", lw=1.2, label=r"$EE$")
    a.loglog(ell[2:], dl(cl["bb"])[2:], "C2-", lw=1.2, label=r"$BB$ (lensing)")
    a.set_xlim(2, lmax)
    a.set_ylim(1e-6, 1e4)
    a.set_xlabel(r"$\ell$")
    a.set_ylabel(r"$D_\ell = \ell(\ell+1)C_\ell/2\pi\ \ [\mu\mathrm{K}^2]$")
    a.set_title("CMB power spectra (lensed)")
    a.legend(fontsize=9)

    # (b) lensing effect on TT, as a fractional difference
    b = ax[0, 1]
    unl = c.raw_cl(lmax)
    ratio = (cl["tt"] / unl["tt"] - 1.0) * 100.0
    m = ell >= 2
    b.semilogx(ell[m], ratio[m], "C1-", lw=1.2)
    b.axhline(0.0, color="k", lw=0.8, ls=":")
    b.set_xlim(2, lmax)
    b.set_xlabel(r"$\ell$")
    b.set_ylabel(r"$C_\ell^{\rm lensed}/C_\ell^{\rm unlensed} - 1\ \ [\%]$")
    b.set_title("Lensing smoothing of TT")

    # (c) ionization history
    cc = ax[0, 2]
    th = c.get_thermodynamics()
    z, x_e = np.asarray(th["z"]), np.asarray(th["x_e"])  # both ascending
    m = (z >= 400) & (z <= 1800)
    cc.semilogy(z[m], x_e[m], "C3-", lw=1.3)
    cc.set_xlabel(r"$z$")
    cc.set_ylabel(r"$x_e$")
    cc.set_title("Ionization fraction (recombination)")

    # (d) P(k) linear vs non-linear
    d = ax[1, 0]
    k_h = np.logspace(-3, 1.0, 180)
    pl = np.array([c.pk_lin(k * h, 0.0) for k in k_h]) * h**3
    pn = np.array([c.pk(k * h, 0.0) for k in k_h]) * h**3
    d.loglog(k_h, pl, "k--", label="linear")
    d.loglog(k_h, pn, "r-", label="non-linear (halofit)")
    knl = c.nonlinear_scale(np.array([0.0]), 1)[0] * h
    d.axvline(knl, color="gray", ls=":", label=r"$k_{nl}(0)$")
    d.set_xlim(1e-3, 10)
    d.set_xlabel(r"$k\ \ [h/\mathrm{Mpc}]$")
    d.set_ylabel(r"$P(k)\ \ [(\mathrm{Mpc}/h)^3]$")
    d.set_title(r"$P(k)$ at $z=0$")
    d.legend(fontsize=9)

    # (e) distances
    e = ax[1, 1]
    bg = c.get_background()
    z_bg = np.asarray(bg["z"])
    m = (z_bg > 1e-3) & (z_bg < 1e4)
    h0 = c.Hubble(0.0)  # 1/Mpc
    for key, lab, col in [
        ("comov. dist.", "comoving", "C0"),
        ("ang.diam.dist.", "angular diameter", "C2"),
        ("lum. dist.", "luminosity", "C3"),
    ]:
        e.loglog(z_bg[m], np.asarray(bg[key])[m] * h0, col + "-", label=lab)
    e.set_xlabel(r"$z$")
    e.set_ylabel(r"$H_0\,D(z)$")
    e.set_title("Distances")
    e.legend(fontsize=9)

    # (f) growth
    f = ax[1, 2]
    zz = np.linspace(0.0, 5.0, 200)
    f.plot(zz, c.scale_independent_growth_factor(zz), "C0-", label=r"$D(z)$")
    f.set_xlabel(r"$z$")
    f.set_ylabel(r"$D(z)$", color="C0")
    twin = f.twinx()
    twin.plot(zz, c.scale_independent_growth_factor_f(zz), "C1--", label=r"$f(z)$")
    twin.set_ylabel(r"$f = \mathrm{d}\ln D/\mathrm{d}\ln a$", color="C1")
    twin.grid(False)
    f.set_title("Linear growth")

    lines = f.get_lines() + twin.get_lines()
    f.legend(lines, [ln.get_label() for ln in lines], fontsize=9, loc="center right")

    fig.tight_layout()
    if save:
        fig.savefig(save, bbox_inches="tight")
        print(f"\nfigure written to {save}")
    if show:
        plt.show()


def main() -> None:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument(
        "--baseline",
        default="planck2018",
        help="classy baseline preset: planck2018, p18l, p18lb",
    )
    p.add_argument("--lmax", type=int, default=2500, help="max multipole for CMB")
    p.add_argument("--save", metavar="PATH", help="write the figure to PATH")
    p.add_argument("--no-show", action="store_true", help="do not open a window")
    args = p.parse_args()

    cosmo = build_cosmology(args.baseline, args.lmax)
    try:
        report_model(cosmo, args.baseline)
        report_background(cosmo)
        report_cmb(cosmo, args.lmax)
        report_pk(cosmo)
        report_distances(cosmo)
        report_thermo(cosmo)
        make_figure(cosmo, args.lmax, args.baseline, args.save, not args.no_show)
    finally:
        cosmo.struct_cleanup()


if __name__ == "__main__":
    main()
