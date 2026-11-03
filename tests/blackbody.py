import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, CheckButtons, Button

# Fundamental constants (SI)
h = 6.62607015e-34      # J s
c = 2.99792458e8        # m / s
k_B = 1.380649e-23      # J / K
T_CMB = 2.7255          # FIRAS / Planck mean CMB temperature [K]
x_peak_nu = 2.821439372 # Root of (3 - x)*exp(x) = 3

# Frequency grid: 5 GHz to 800 GHz
nu = np.linspace(5e9, 800e9, 1000)
nu_GHz = nu * 1e-9

def planck_nu_MJy(nu_Hz, T):
    """
    Returns spectral radiance B_nu in MJy/sr
    (1 MJy/sr = 1e-20 W sr^-1 m^-2 Hz^-1)
    """
    x = (h * nu_Hz) / (k_B * T)
    B_SI = (2.0 * h * nu_Hz**3 / c**2) / np.expm1(x)
    return B_SI * 1e20

def dB_dT_MJy(nu_Hz, T):
    """
    First derivative dB_nu / dT in MJy / (sr K)
    """
    x = (h * nu_Hz) / (k_B * T)
    prefactor = (2.0 * h**2 * nu_Hz**4) / (c**2 * k_B * T**2)
    return prefactor * (np.exp(x) / np.expm1(x)**2) * 1e20

# Figure layout: Left = B_nu(nu, T), Right = Residual Delta B_nu for small dT
fig, (ax_main, ax_diff) = plt.subplots(1, 2, figsize=(13, 5.8))
plt.subplots_adjust(bottom=0.26, wspace=0.25)

# --- LEFT PANEL: Macroscopic CMB Planck Spectrum ---
B_ref = planck_nu_MJy(nu, T_CMB)
line_ref, = ax_main.plot(nu_GHz, B_ref, 'k--', lw=1.3, alpha=0.6,
                         label=f'CMB $T_0 = {T_CMB}$ K')
line_cur, = ax_main.plot(nu_GHz, B_ref, color='#2980b9', lw=2.5,
                         label=r'Planck $B_\nu(\nu, T)$')

# Rayleigh-Jeans approximation (low-frequency limit)
RJ_cur = (2.0 * nu**2 * k_B * T_CMB / c**2) * 1e20
line_rj, = ax_main.plot(nu_GHz, RJ_cur, color='#e67e22', ls=':', lw=1.5,
                        label=r'Rayleigh-Jeans ($\propto \nu^2 T$)')

# Peak marker and Wien displacement locus
nu_p0 = (x_peak_nu * k_B * T_CMB / h) * 1e-9
peak_dot, = ax_main.plot([nu_p0], [planck_nu_MJy(nu_p0 * 1e9, T_CMB)], 'o',
                         color='#2980b9', markersize=6)

T_locus = np.linspace(1.2, 4.5, 300)
nu_locus = (x_peak_nu * k_B * T_locus / h)
ax_main.plot(nu_locus * 1e-9, planck_nu_MJy(nu_locus, T_locus),
             color='#7f8c8d', ls='-.', lw=1.0, alpha=0.6, label=r'Wien Locus ($\propto T^3$)')

ax_main.set_xlim(0, 800)
ax_main.set_ylim(0, 600)
ax_main.set_xlabel(r'Frequency $\nu$ [GHz]', fontsize=11)
ax_main.set_ylabel(r'Spectral Radiance $B_\nu$ [$\mathrm{MJy\,sr^{-1}}$]', fontsize=11)
title_main = ax_main.set_title(
    f'$T = {T_CMB:.4f}$ K  |  $\\nu_{{\\max}} = {nu_p0:.1f}$ GHz', fontsize=11
)
ax_main.legend(loc='upper right', fontsize=9)
ax_main.grid(True, linestyle=':', alpha=0.6)

# --- RIGHT PANEL: Differential Spectrum (Dipole / Small Delta T) ---
dT_init_mK = 3.3621  # Planck 2018 Solar Dipole amplitude in mK
dT_init_K = dT_init_mK * 1e-3

delta_B_exact = planck_nu_MJy(nu, T_CMB + dT_init_K) - B_ref
delta_B_linear = dB_dT_MJy(nu, T_CMB) * dT_init_K

line_diff_exact, = ax_diff.plot(nu_GHz, delta_B_exact, color='#8e44ad', lw=2.3,
                                label=r'Exact $B_\nu(T_0 + \Delta T) - B_\nu(T_0)$')
line_diff_lin, = ax_diff.plot(nu_GHz, delta_B_linear, 'k:', lw=1.5,
                              label=r'1st-Order $(\partial B_\nu / \partial T)_{T_0} \Delta T$')

# Peak of dB_nu / dT occurs at x = 3.830016 (nu ~ 217.6 GHz for T0 = 2.7255 K)
nu_dip_peak = (3.830016 * k_B * T_CMB / h) * 1e-9
ax_diff.axvline(nu_dip_peak, color='#8e44ad', ls='--', lw=1.0, alpha=0.5,
                label=f'Dipole Peak ({nu_dip_peak:.1f} GHz)')

ax_diff.set_xlim(0, 800)
ax_diff.set_ylim(-2.5, 2.5)
ax_diff.set_xlabel(r'Frequency $\nu$ [GHz]', fontsize=11)
ax_diff.set_ylabel(r'Difference $\Delta B_\nu$ [$\mathrm{MJy\,sr^{-1}}$]', fontsize=11)
title_diff = ax_diff.set_title(
    f'Dipole / Perturbation: $\\Delta T = {dT_init_mK:+.3f}$ mK', fontsize=11
)
ax_diff.legend(loc='upper right', fontsize=9)
ax_diff.grid(True, linestyle=':', alpha=0.6)

# --- INTERACTIVE SLIDERS & BUTTONS ---
ax_slider_T = plt.axes([0.10, 0.12, 0.35, 0.035])
slider_T = Slider(ax_slider_T, 'Temp $T$ [K]', 1.5, 4.0,
                  valinit=T_CMB, valstep=0.005)

ax_slider_dT = plt.axes([0.57, 0.12, 0.33, 0.035])
slider_dT = Slider(ax_slider_dT, '$\\Delta T$ [mK]', -5.0, 5.0,
                   valinit=dT_init_mK, valstep=0.05)

ax_check = plt.axes([0.10, 0.03, 0.22, 0.06], frameon=False)
check = CheckButtons(ax_check, ['Auto-scale Y-axis'], [False])

ax_reset = plt.axes([0.35, 0.04, 0.10, 0.045])
btn_reset = Button(ax_reset, 'Reset $T_0$')

def update(val=None):
    # Update Left Panel (Macroscopic T)
    T = slider_T.val
    B_cur = planck_nu_MJy(nu, T)
    line_cur.set_ydata(B_cur)
    line_rj.set_ydata((2.0 * nu**2 * k_B * T / c**2) * 1e20)

    nu_p = (x_peak_nu * k_B * T / h) * 1e-9
    B_p = planck_nu_MJy(nu_p * 1e9, T)
    peak_dot.set_data([nu_p], [B_p])
    title_main.set_text(f'$T = {T:.4f}$ K  |  $\\nu_{{\\max}} = {nu_p:.1f}$ GHz')

    # Update Right Panel (Differential dT around T_CMB)
    dT_mK = slider_dT.val
    dT_K = dT_mK * 1e-3
    dB_ex = planck_nu_MJy(nu, T_CMB + dT_K) - B_ref
    dB_ln = dB_dT_MJy(nu, T_CMB) * dT_K
    line_diff_exact.set_ydata(dB_ex)
    line_diff_lin.set_ydata(dB_ln)
    title_diff.set_text(f'Dipole / Perturbation: $\\Delta T = {dT_mK:+.3f}$ mK')

    # Handle Y-axis scaling
    auto_scale = check.get_status()[0]
    if auto_scale:
        ax_main.set_ylim(0, max(B_p * 1.15, 10.0))
        max_diff = max(np.max(np.abs(dB_ex)) * 1.15, 0.05)
        ax_diff.set_ylim(-max_diff, max_diff)
    else:
        ax_main.set_ylim(0, 1100)
        ax_diff.set_ylim(-2.5, 2.5)

    fig.canvas.draw_idle()

def reset(event):
    slider_T.reset()
    slider_dT.reset()

slider_T.on_changed(update)
slider_dT.on_changed(update)
check.on_clicked(update)
btn_reset.on_clicked(reset)

plt.show()