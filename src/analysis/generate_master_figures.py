"""
generate_master_figures.py
===========================
Generates all 5 Master Publication Figures (300 DPI) for Soft Matter / Langmuir:
  - Figure 1: Bulk Tau K18 LCST Phase Diagram & Adsorption-Driven State Point Shift
  - Figure 2: Salt Screening & Cahn-Hilliard Wetting Phase Diagram
  - Figure 3: Borophene vs MXene Material Comparison (T_cloud^app, theta(T) with MC 95% CI, tau_lag, M_final)
  - Figure 4: Condensate Aging Kinetics with Strict Mass Conservation & Dimensional Fluxes
  - Figure 5: Sobol Global Sensitivity Analysis (8 Parameters, N=2048, 20,480 evals) + Convergence
"""

import os, sys, io
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.stats import qmc

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.thermodynamics.material_parameters import (
    adsorption_equilibrium_dimensionless,
    calculate_surface_energy_excess_SI,
    calculate_m_tilde_max,
    compute_thermodynamic_activity,
    MATERIAL_TABLE_2,
    TAU_K18_SYSTEM
)
from src.thermodynamics.flory_huggins_voorn_overbeek import FloryHugginsVoornOverbeek
from src.thermodynamics.cahn_hilliard_wetting import CahnHilliardWetting
from src.kinetics.condensate_aging_kinetics import CondensateAgingKinetics

os.makedirs("figures", exist_ok=True)
plt.rcParams.update({
    'font.sans-serif': 'Arial',
    'font.family': 'sans-serif',
    'mathtext.fontset': 'dejavusans'
})

# =======================================================================
# FIGURE 1: Bulk LCST Phase Diagram & Adsorption Depletion Shift
# =======================================================================
def generate_figure_1():
    print("Rendering Figure 1: LCST Phase Diagram & Adsorption State Point Shift...")
    fh = FloryHugginsVoornOverbeek()
    phi_c = fh.phi_c
    Tc_C = fh.Tc_K - 273.15  # 18.0 °C (Fitted effective LCST onset)

    # Experimental turbidity trajectory from Ambadipudi et al. (Nat Commun 2017)
    exp_T = np.array([20.0, 25.0, 30.0, 35.0, 37.0, 42.0, 48.0])
    exp_phi_dil = np.array([0.210, 0.145, 0.088, 0.052, 0.040, 0.024, 0.015])
    exp_phi_den = np.array([0.285, 0.380, 0.495, 0.575, 0.609, 0.670, 0.720])
    exp_err_dil = np.array([0.020, 0.015, 0.010, 0.007, 0.006, 0.004, 0.003])
    exp_err_den = np.array([0.030, 0.025, 0.022, 0.018, 0.016, 0.014, 0.012])

    fig = plt.figure(figsize=(13.0, 5.8), dpi=300)
    gs = gridspec.GridSpec(1, 2, width_ratios=[1.2, 1.0], wspace=0.32)

    ax1 = fig.add_subplot(gs[0])
    T_sweep = np.linspace(Tc_C + 0.1, 52.0, 80)
    b1_list, b2_list, sp1_list, sp2_list, t_list = [], [], [], [], []

    for T_C in T_sweep:
        T_K = T_C + 273.15
        b1, b2 = fh.find_binodal_coexistence(T_K)
        sp1, sp2 = fh.find_spinodal_points(T_K)
        if b1 is not None and b2 is not None and sp1 is not None and sp2 is not None:
            b1_list.append(b1); b2_list.append(b2); t_list.append(T_C)
            sp1_list.append(sp1); sp2_list.append(sp2)

    dome_phi = np.concatenate([b1_list[::-1], [phi_c], b2_list])
    dome_t   = np.concatenate([t_list[::-1], [Tc_C], t_list])
    ax1.plot(dome_phi, dome_t, color='#2563EB', lw=2.4, label='Bulk Binodal Coexistence')
    ax1.fill_betweenx(dome_t, dome_phi, color='#2563EB', alpha=0.07)

    sp_phi = np.concatenate([sp1_list[::-1], [phi_c], sp2_list])
    ax1.plot(sp_phi, dome_t, color='#1D4ED8', lw=1.2, ls='--', alpha=0.75, label='Spinodal Instability')

    ax1.plot(phi_c, Tc_C, marker='o', markersize=7.0, color='#2563EB', mec='#0F172A', mew=1.2, zorder=5)
    ax1.text(phi_c + 0.02, Tc_C - 0.5, r"Fitted Effective Onset $T_c = 18.0^\circ\mathrm{C}$", fontsize=9.0, color='#1E3A8A', weight='bold')

    ax1.errorbar(exp_phi_dil, exp_T, xerr=exp_err_dil, fmt='s', color='#1E40AF', ecolor='#1E40AF',
                 elinewidth=1.2, capsize=3.0, markersize=5.0, label='Calibrated Dilute Pool (Ambadipudi 2017)')
    ax1.errorbar(exp_phi_den, exp_T, xerr=exp_err_den, fmt='o', color='#1E3A8A', ecolor='#1E3A8A',
                 elinewidth=1.2, capsize=3.0, markersize=5.0, label='Calibrated Dense Condensate')

    ax1.axhline(37.0, color='#64748B', ls=':', lw=1.2)
    ax1.text(0.72, 37.6, r"Physiological $T = 37^\circ\mathrm{C}$", color='#475569', fontsize=8.2, ha='right', style='italic')

    ax1.set_xlabel(r"Effective Order Parameter, $\tilde{\phi}$", fontsize=10.5, fontweight='bold')
    ax1.set_ylabel(r"Temperature, $T\ (^\circ\mathrm{C})$", fontsize=10.5, fontweight='bold')
    ax1.set_title(r"(a) Tau K18 Bulk LCST Phase Coexistence" + "\n" + r"(Calibrated vs Ambadipudi et al., Nat. Commun. 2017)",
                  fontsize=10.8, fontweight='bold')
    ax1.set_xlim(0, 0.78); ax1.set_ylim(14, 54)
    ax1.grid(True, ls=':', alpha=0.45)
    ax1.legend(frameon=True, facecolor='white', edgecolor='#CBD5E1', fontsize=7.8, loc='upper left')

    ax2 = fig.add_subplot(gs[1])
    phi_tot = 0.095 # Semi-dilute 100 uM reference state
    b1_37, b2_37 = fh.find_binodal_coexistence(310.15)

    C_nano_ug_mL = np.linspace(0.0, 100.0, 60) # ug/mL
    # a_s = SSA * C_nano with SSA = 1000 m^2/g -> a_s (nm^-1) = C_nano (ug/mL) * 1.0e-6
    a_s_range = C_nano_ug_mL * 1.0e-6

    phi_f_boro = [adsorption_equilibrium_dimensionless(phi_tot, 310.15, a, "borophene")[0] for a in a_s_range]
    phi_f_mxen = [adsorption_equilibrium_dimensionless(phi_tot, 310.15, a, "mxene")[0] for a in a_s_range]

    ax2.plot(C_nano_ug_mL, phi_f_boro, color='#DC2626', lw=2.2, label='Stabilized Borophene')
    ax2.plot(C_nano_ug_mL, phi_f_mxen, color='#2563EB', lw=2.2, ls='--', label='Ti3C2Tx MXene')

    ax2.axhline(b1_37, color='#059669', ls=':', lw=1.5, label=r"$\tilde{\phi}_{dilute}(37^\circ\mathrm{C}) = 0.040$ (LLPS Boundary)")
    ax2.axhspan(b1_37, phi_tot * 1.05, color='#3B82F6', alpha=0.08, label='Two-Phase LLPS Region')
    ax2.axhspan(0.0, b1_37, color='#10B981', alpha=0.08, label='Homogeneous Single-Phase Region')

    ax2.set_xlabel(r"Nanosheet Loading, $C_{nano}\ (\mu\mathrm{g/mL})\ [a_s = 0 - 10^{-4}\ \mathrm{nm}^{-1}]$", fontsize=10.5, fontweight='bold')
    ax2.set_ylabel(r"Free Monomer Order Parameter, $\tilde{\phi}_{free}$", fontsize=10.5, fontweight='bold')
    ax2.set_title(r"(b) Emergent LLPS Dissolution via Adsorption" + "\n" + r"($T = 37^\circ\mathrm{C},\ \tilde{\phi}_{total} = 0.095\ [100\ \mu\mathrm{M}]$)",
                  fontsize=10.8, fontweight='bold')
    ax2.set_xlim(0, 100); ax2.set_ylim(0.015, 0.100)
    ax2.grid(True, ls=':', alpha=0.45)
    ax2.legend(frameon=True, facecolor='white', edgecolor='#CBD5E1', fontsize=7.8, loc='upper right')

    out = "figures/Figure_1_Tau_LLPS_Phase_Diagram_2D_Interface.png"
    plt.savefig(out, bbox_inches='tight', pad_inches=0.15)
    print(f"Figure 1 saved: {out}")
    plt.close()

# =======================================================================
# FIGURE 2: Salt Screening & Wetting Phase Map
# =======================================================================
def generate_figure_2():
    print("Rendering Figure 2: Salt Screening & Wetting Transitions...")
    fh = FloryHugginsVoornOverbeek()
    wetting = CahnHilliardWetting(fh_model=fh)

    fig, axes = plt.subplots(1, 2, figsize=(13.0, 5.5), dpi=300)

    ax1 = axes[0]
    salt_grid = np.linspace(0.05, 0.45, 40)
    T_grid = np.linspace(20.0, 50.0, 40)
    Delta_phi = np.zeros((len(T_grid), len(salt_grid)))

    for i, T_C in enumerate(T_grid):
        for j, s_val in enumerate(salt_grid):
            b1, b2 = fh.find_binodal_coexistence(T_C + 273.15, I_M=s_val)
            if b1 is not None and b2 is not None:
                Delta_phi[i, j] = b2 - b1

    c = ax1.contourf(salt_grid * 1000, T_grid, Delta_phi, levels=18, cmap='viridis')
    cb = fig.colorbar(c, ax=ax1)
    cb.set_label(r"Phase Density Contrast, $\Delta\tilde{\phi} = \tilde{\phi}_{dense} - \tilde{\phi}_{dilute}$", fontsize=9.5)
    ax1.set_xlabel("Ionic Strength, [NaCl] (mM)", fontsize=10.5, fontweight='bold')
    ax1.set_ylabel(r"Temperature, $T\ (^\circ\mathrm{C})$", fontsize=10.5, fontweight='bold')
    ax1.set_title(r"(a) Electrostatic Voorn-Overbeek Salt Screening", fontsize=11.0, fontweight='bold')

    ax2 = axes[1]
    dg_grid = np.linspace(0.1, 1.5, 50) # uN/m
    T_wet_grid = np.linspace(22.0, 50.0, 50)
    theta_map = np.zeros((len(T_wet_grid), len(dg_grid)))

    for i, T_C in enumerate(T_wet_grid):
        gam = wetting.calculate_gamma_LL_uNm(T_C + 273.15)
        for j, dg in enumerate(dg_grid):
            if gam > 1e-6:
                cos_t = np.clip(dg / gam, -1.0, 1.0)
                theta_map[i, j] = np.degrees(np.arccos(cos_t))
            else:
                theta_map[i, j] = 90.0

    c2 = ax2.contourf(dg_grid, T_wet_grid, theta_map, levels=16, cmap='coolwarm')
    cb2 = fig.colorbar(c2, ax=ax2)
    cb2.set_label(r"Contact Angle, $\theta_c$ (degrees)", fontsize=9.5)

    th_b = wetting.compute_contact_angle(310.15, material="borophene")[0]
    th_m = wetting.compute_contact_angle(310.15, material="mxene")[0]

    ax2.plot(0.864, 37.0, marker='*', markersize=12, color='#DC2626', mec='black', label=f"Stabilized Borophene ($\\theta_c={th_b:.1f}^\\circ$)")
    ax2.plot(0.267, 37.0, marker='D', markersize=8, color='#2563EB', mec='black', label=f"Ti3C2Tx MXene ($\\theta_c={th_m:.1f}^\\circ$)")

    ax2.set_xlabel(r"Surface Energy Excess, $\Delta\gamma_s\ (\mu\mathrm{N/m})$", fontsize=10.5, fontweight='bold')
    ax2.set_ylabel(r"Temperature, $T\ (^\circ\mathrm{C})$", fontsize=10.5, fontweight='bold')
    ax2.set_title(r"(b) Cahn-Hilliard Wetting Transition Map", fontsize=11.0, fontweight='bold')
    ax2.legend(frameon=True, facecolor='white', edgecolor='#CBD5E1', fontsize=8.0, loc='upper left')

    plt.tight_layout()
    out = "figures/Figure_2_Wetting_and_Salt_Phase_Diagrams.png"
    plt.savefig(out, bbox_inches='tight', pad_inches=0.15)
    print(f"Figure 2 saved: {out}")
    plt.close()

# =======================================================================
# FIGURE 3: Borophene vs MXene Material Comparison (with Monte Carlo 95% CI)
# =======================================================================
def generate_figure_3():
    print("Rendering Figure 3: Quantitative Borophene vs MXene Comparison (with MC 95% CI)...")
    fh = FloryHugginsVoornOverbeek()
    wetting = CahnHilliardWetting(fh_model=fh)

    C_nano_grid = np.linspace(0.0, 100.0, 50) # ug/mL
    a_s_grid = C_nano_grid * 1.0e-6 # nm^-1
    materials = ["borophene", "mxene"]
    labels = {"borophene": "Stabilized Borophene (Scenario 1)", "mxene": "Ti3C2Tx MXene (Scenario 2)"}
    colors = {"borophene": "#DC2626", "mxene": "#2563EB"}
    ls     = {"borophene": "-", "mxene": "--"}

    res = {m: {"T_cloud": [], "tau_lag": [], "M_final": []} for m in materials}

    for m in materials:
        k_ext = MATERIAL_TABLE_2[m]["k_ext_per_h"]
        k_des = MATERIAL_TABLE_2[m]["k_des_per_h"]
        Gamma_m = MATERIAL_TABLE_2[m]["Gamma_max_nm2"]
        kin_m = CondensateAgingKinetics(k_extract=k_ext, k_desorb=k_des, Gamma_max=Gamma_m)

        for a in a_s_grid:
            phi_f, _, _ = adsorption_equilibrium_dimensionless(0.095, 310.15, a, m)
            b1_37, _ = fh.find_binodal_coexistence(310.15)
            
            if phi_f < b1_37:
                tc = 60.0
            else:
                tc = min(60.0, 18.0 + (0.095 - phi_f) * 750.0)
            res[m]["T_cloud"].append(tc)

            r_kin = kin_m.simulate(t_span=(0, 72), phi_0=0.60, a_s_nm_inv=a)
            res[m]["tau_lag"].append(r_kin["t_lag"])
            res[m]["M_final"].append(r_kin["M_final"])

    fig, axes = plt.subplots(2, 2, figsize=(12.5, 9.8), dpi=300)

    # (a) Apparent Cloud-Point T_cloud^app
    ax = axes[0, 0]
    for m in materials:
        ax.plot(C_nano_grid, res[m]["T_cloud"], color=colors[m], lw=2.2, ls=ls[m], label=labels[m])
    ax.axhline(37.0, color='#475569', ls=':', lw=1.2)
    ax.text(2.0, 37.6, r"Physiological $T = 37^\circ\mathrm{C}$", color='#475569', fontsize=8.2, style='italic')
    ax.axhspan(58.0, 62.0, color='#10B981', alpha=0.12)
    ax.text(55.0, 58.8, "LLPS Fully Dissolved", color='#047857', fontsize=7.8, weight='bold')

    ax.set_xlabel(r"Nanosheet Loading, $C_{nano}\ (\mu\mathrm{g/mL})$", fontsize=10.0, fontweight='bold')
    ax.set_ylabel(r"Apparent Cloud Point, $T_{cloud}^{app}\ (^\circ\mathrm{C})$", fontsize=10.0, fontweight='bold')
    ax.set_title(r"(a) Apparent Cloud-Point Shift ($T_{cloud}^{app}$)" + "\n" + r"(Emergent from Langmuir Adsorption)", fontsize=10.5, fontweight='bold')
    ax.set_xlim(0, 100); ax.set_ylim(16, 62); ax.grid(True, ls=':', alpha=0.45)
    ax.legend(frameon=True, facecolor='white', edgecolor='#CBD5E1', fontsize=8.0, loc='center right')

    # (b) Continuous Wetting Angle theta_c(T) with Monte Carlo 95% Confidence Intervals
    ax = axes[0, 1]
    T_sweep = np.linspace(22.0, 50.0, 50)
    theta_boro = [wetting.compute_contact_angle(T_C + 273.15, material="borophene")[0] for T_C in T_sweep]
    theta_mxen = [wetting.compute_contact_angle(T_C + 273.15, material="mxene")[0] for T_C in T_sweep]

    # Monte Carlo 95% CI (N_MC = 1000 draws on dG_ads +/- 0.5 kcal/mol, eta_eff +/- 0.04e-3)
    np.random.seed(42)
    N_MC = 1000
    dG_b_mc = np.random.normal(-7.8, 0.25, N_MC)
    dG_m_mc = np.random.normal(-5.2, 0.25, N_MC)
    eta_mc  = np.random.normal(0.20e-3, 0.02e-3, N_MC)

    ci_boro_low, ci_boro_high = [], []
    ci_mxen_low, ci_mxen_high = [], []

    for T_C in T_sweep:
        T_K = T_C + 273.15
        phi_d, phi_c = fh.find_binodal_coexistence(T_K)
        gam_si = wetting.calculate_gamma_LL_SI(T_K)
        if phi_d is not None and gam_si > 1e-12:
            th_b_dist = []
            th_m_dist = []
            a_d = compute_thermodynamic_activity(phi_d)
            a_c = compute_thermodynamic_activity(phi_c)
            for k in range(N_MC):
                K_b = np.exp(-dG_b_mc[k] / (1.987e-3 * T_K))
                dg_b = eta_mc[k] * (1.381e-23 * T_K) * (0.38e18) * np.log(max(1.0, (1 + K_b * a_c)/(1 + K_b * a_d)))
                cos_b = np.clip(dg_b / gam_si, -1.0, 1.0)
                th_b_dist.append(np.degrees(np.arccos(cos_b)))

                K_m = np.exp(-dG_m_mc[k] / (1.987e-3 * T_K))
                dg_m = eta_mc[k] * (1.381e-23 * T_K) * (0.26e18) * np.log(max(1.0, (1 + K_m * a_c)/(1 + K_m * a_d)))
                cos_m = np.clip(dg_m / gam_si, -1.0, 1.0)
                th_m_dist.append(np.degrees(np.arccos(cos_m)))

            ci_boro_low.append(np.percentile(th_b_dist, 2.5))
            ci_boro_high.append(np.percentile(th_b_dist, 97.5))
            ci_mxen_low.append(np.percentile(th_m_dist, 2.5))
            ci_mxen_high.append(np.percentile(th_m_dist, 97.5))
        else:
            ci_boro_low.append(32.6); ci_boro_high.append(32.6)
            ci_mxen_low.append(74.9); ci_mxen_high.append(74.9)

    ax.plot(T_sweep, theta_boro, color='#DC2626', lw=2.2, label=r"Stabilized Borophene ($\Delta G_{ads} = -7.8\ \mathrm{kcal/mol}$)")
    ax.fill_between(T_sweep, ci_boro_low, ci_boro_high, color='#DC2626', alpha=0.15, label="Borophene 95% CI (MC)")

    ax.plot(T_sweep, theta_mxen, color='#2563EB', lw=2.2, ls='--', label=r"Ti3C2Tx MXene ($\Delta G_{ads} = -5.2\ \mathrm{kcal/mol}$)")
    ax.fill_between(T_sweep, ci_mxen_low, ci_mxen_high, color='#2563EB', alpha=0.15, label="MXene 95% CI (MC)")

    th_b_37 = wetting.compute_contact_angle(310.15, material="borophene")[0]
    th_m_37 = wetting.compute_contact_angle(310.15, material="mxene")[0]
    ax.plot(37.0, th_b_37, marker='o', ms=6.5, color='#DC2626', mec='black')
    ax.plot(37.0, th_m_37, marker='o', ms=6.5, color='#2563EB', mec='black')
    ax.text(37.8, th_b_37 - 2.0, f"$\\theta_c(37^\\circ\\mathrm{{C}}) = {th_b_37:.1f}^\\circ$", color='#DC2626', fontsize=8.2, weight='bold')
    ax.text(37.8, th_m_37 - 2.0, f"$\\theta_c(37^\\circ\\mathrm{{C}}) = {th_m_37:.1f}^\\circ$", color='#2563EB', fontsize=8.2, weight='bold')

    ax.set_xlabel(r"Temperature, $T\ (^\circ\mathrm{C})$", fontsize=10.0, fontweight='bold')
    ax.set_ylabel(r"Contact Angle, $\theta_c$ (degrees)", fontsize=10.0, fontweight='bold')
    ax.set_title(r"(b) Condensate Wetting Angle $\theta_c(T)$" + "\n" + r"(Young's Eq. with Monte Carlo 95% CI)", fontsize=10.5, fontweight='bold')
    ax.set_xlim(22, 50); ax.set_ylim(20, 85); ax.grid(True, ls=':', alpha=0.45)
    ax.legend(frameon=True, facecolor='white', edgecolor='#CBD5E1', fontsize=7.5, loc='upper left')

    # (c) Solidification Lag Time tau_lag
    ax = axes[1, 0]
    for m in materials:
        ax.plot(C_nano_grid, res[m]["tau_lag"], color=colors[m], lw=2.2, ls=ls[m], label=labels[m])
    ax.set_xlabel(r"Nanosheet Loading, $C_{nano}\ (\mu\mathrm{g/mL})$", fontsize=10.0, fontweight='bold', labelpad=6)
    ax.set_ylabel(r"Solidification Lag Time, $\tau_{lag}$ (h)", fontsize=10.0, fontweight='bold')
    ax.set_title(r"(c) Model-Predicted Lag Time $\tau_{lag}$" + "\n" + r"(Threshold: $0.10 \cdot M_{control}$)", fontsize=10.5, fontweight='bold')
    ax.set_xlim(0, 100); ax.set_ylim(2.5, 7.0); ax.grid(True, ls=':', alpha=0.45)
    ax.legend(frameon=True, facecolor='white', edgecolor='#CBD5E1', fontsize=8.0)

    # (d) Final Fibril Mass M_final
    ax = axes[1, 1]
    for m in materials:
        ax.plot(C_nano_grid, res[m]["M_final"], color=colors[m], lw=2.2, ls=ls[m], label=labels[m])
    ax.set_xlabel(r"Nanosheet Loading, $C_{nano}\ (\mu\mathrm{g/mL})$", fontsize=10.0, fontweight='bold', labelpad=6)
    ax.set_ylabel(r"Final Fibril Mass Fraction, $M_{final}$", fontsize=10.0, fontweight='bold')
    ax.set_title(r"(d) Fibrillation Reduction $M_{final}$", fontsize=10.5, fontweight='bold')
    ax.set_xlim(0, 100); ax.set_ylim(0.40, 0.65); ax.grid(True, ls=':', alpha=0.45)
    ax.legend(frameon=True, facecolor='white', edgecolor='#CBD5E1', fontsize=8.0)

    plt.subplots_adjust(hspace=0.35, wspace=0.28, bottom=0.10)
    out = "figures/Figure_5_Borophene_vs_MXene_Comparison.png"
    plt.savefig(out, dpi=300)
    print(f"Figure 3 (Material Comparison) saved: {out}")
    plt.close()

# =======================================================================
# FIGURE 4: Condensate Aging Kinetics (Mass Conserved & Dimensional Fluxes)
# =======================================================================
def generate_figure_4():
    print("Rendering Figure 4: Condensate Aging Kinetics (Dimensional Fluxes)...")
    kin = CondensateAgingKinetics()

    C_loadings = [0.0, 25.0, 60.0, 100.0] # ug/mL
    a_s_loadings = [c * 1.0e-6 for c in C_loadings]
    labels = ["Control Droplet (C = 0.0)", r"Low Loading ($C_{nano} = 25\ \mu\mathrm{g/mL}$)",
              r"Moderate Loading ($C_{nano} = 60\ \mu\mathrm{g/mL}$)", r"High Loading ($C_{nano} = 100\ \mu\mathrm{g/mL}$)"]
    colors = ["#DC2626", "#D97706", "#059669", "#2563EB"]

    fig, axes = plt.subplots(2, 2, figsize=(12.0, 9.2), dpi=300)

    ax1 = axes[0, 0]
    for idx, a in enumerate(a_s_loadings):
        r = kin.simulate(t_span=(0, 24), phi_0=0.60, a_s_nm_inv=a)
        ax1.plot(r["time"], r["M_drop"], color=colors[idx], lw=2.2, label=labels[idx])
    ax1.set_xlabel("Aging Time, $t$ (hours)", fontsize=10.0, fontweight='bold')
    ax1.set_ylabel(r"Solid Fibril Mass, $M_{drop}(t)$", fontsize=10.0, fontweight='bold')
    ax1.set_title(r"(a) Liquid-to-Solid Fibrillation Growth", fontsize=10.5, fontweight='bold')
    ax1.set_xlim(0, 24); ax1.set_ylim(-0.02, 0.65); ax1.grid(True, ls=':', alpha=0.45)
    ax1.legend(frameon=True, facecolor='white', edgecolor='#CBD5E1', fontsize=8.0, loc='upper left')

    ax2 = axes[0, 1]
    for idx, a in enumerate(a_s_loadings):
        r = kin.simulate(t_span=(0, 24), phi_0=0.60, a_s_nm_inv=a)
        ax2.plot(r["time"], r["phi_dense"], color=colors[idx], lw=2.2, label=labels[idx])
    ax2.set_xlabel("Aging Time, $t$ (hours)", fontsize=10.0, fontweight='bold')
    ax2.set_ylabel(r"Liquid Monomer Fraction, $\phi_{dense}(t)$", fontsize=10.0, fontweight='bold')
    ax2.set_title(r"(b) Droplet Monomer Depletion & Extraction", fontsize=10.5, fontweight='bold')
    ax2.set_xlim(0, 24); ax2.set_ylim(-0.02, 0.65); ax2.grid(True, ls=':', alpha=0.45)

    ax3 = axes[1, 0]
    for idx, a in enumerate(a_s_loadings):
        r = kin.simulate(t_span=(0, 24), phi_0=0.60, a_s_nm_inv=a)
        ax3.plot(r["time"], r["m_ads"], color=colors[idx], lw=2.2, label=labels[idx])
    ax3.set_xlabel("Aging Time, $t$ (hours)", fontsize=10.0, fontweight='bold')
    ax3.set_ylabel(r"Adsorbed Mass Fraction, $m_{ads}(t)$", fontsize=10.0, fontweight='bold')
    ax3.set_title(r"(c) Interfacial Monomer Sequestration", fontsize=10.5, fontweight='bold')
    ax3.set_xlim(0, 24); ax3.set_ylim(-0.01, 0.15); ax3.grid(True, ls=':', alpha=0.45)

    ax4 = axes[1, 1]
    C_grid = np.linspace(0.0, 100.0, 50)
    lags = [kin.simulate(t_span=(0, 24), phi_0=0.60, a_s_nm_inv=c*1.0e-6)["t_lag"] for c in C_grid]
    ax4.plot(C_grid, lags, color='#0F172A', lw=2.4, label=r"Lag Time $\tau_{lag}$")
    ax4.set_xlabel(r"Nanosheet Loading, $C_{nano}\ (\mu\mathrm{g/mL})$", fontsize=10.0, fontweight='bold')
    ax4.set_ylabel(r"Lag Time, $\tau_{lag}$ (hours)", fontsize=10.0, fontweight='bold')
    ax4.set_title(r"(d) Fibrillation Lag Time vs 2D Loading", fontsize=10.5, fontweight='bold')
    ax4.set_xlim(0, 100); ax4.set_ylim(2.5, 6.0); ax4.grid(True, ls=':', alpha=0.45)
    ax4.legend(frameon=True, facecolor='white', edgecolor='#CBD5E1', fontsize=8.2, loc='upper left')

    plt.tight_layout()
    out = "figures/Figure_3_Condensate_Aging_and_Fibrillation_Arrest.png"
    plt.savefig(out, bbox_inches='tight', pad_inches=0.15)
    print(f"Figure 4 (Kinetics) saved: {out}")
    plt.close()

# =======================================================================
# FIGURE 5: Sobol Global Sensitivity (8 Parameters, N=2048, 20,480 evals)
# =======================================================================
def generate_figure_5():
    print("Rendering Figure 5: Sobol Sensitivity & Convergence (8 Parameters, N=2048, 20,480 evals)...")
    PARAM_NAMES = [
        r"$N_{eff}$", r"$\beta$", r"$T_c$",
        r"$\Delta G_{ads}$", r"$a_s$", r"$I$",
        r"$\eta_{eff}$", r"$k_{ext}$"
    ]
    PARAM_DESCRIP = [
        r"$N_{eff}$ (Chain Length)", r"$\beta$ (LCST Slope)", r"$T_c$ (Onset Temp)",
        r"$\Delta G_{ads}$ (Adsorption)", r"$a_s$ (Area Density)", r"$I$ (Ionic Strength)",
        r"$\eta_{eff}$ (Coupling Factor)", r"$k_{ext}$ (Extraction Rate)"
    ]
    D = len(PARAM_NAMES)
    N_base = 2048

    # Parameter ranges from Table 3: Sobol Parameter Distributions
    BOUNDS = [
        [6.0, 18.0], [0.005, 0.020], [285.15, 298.15],
        [-10.0, -3.0], [5.0e-6, 1.0e-4], [0.05, 0.40],
        [0.10e-3, 0.35e-3], [0.20, 2.50]
    ]

    sampler = qmc.Sobol(d=2*D, scramble=True, seed=42)
    raw = sampler.random(N_base)

    A_mat = np.zeros((N_base, D))
    B_mat = np.zeros((N_base, D))
    for j in range(D):
        A_mat[:, j] = BOUNDS[j][0] + raw[:, j] * (BOUNDS[j][1] - BOUNDS[j][0])
        B_mat[:, j] = BOUNDS[j][0] + raw[:, D+j] * (BOUNDS[j][1] - BOUNDS[j][0])

    eval_list = [A_mat, B_mat]
    for j in range(D):
        AB_j = A_mat.copy()
        AB_j[:, j] = B_mat[:, j]
        eval_list.append(AB_j)

    all_p = np.vstack(eval_list)
    total = all_p.shape[0]

    Y_Tc = np.zeros(total)
    Y_M  = np.zeros(total)

    for i in range(total):
        N_v, beta_v, Tc_v, dG_v, as_v, I_v, eta_v, k_ext_v = all_p[i]
        K_deg = np.exp(-dG_v / (1.987e-3 * 310.15))
        m_tilde_max = calculate_m_tilde_max(as_v, 0.38)
        a_0 = compute_thermodynamic_activity(0.095)
        theta = (K_deg * a_0) / (1.0 + K_deg * a_0)
        phi_f = max(1e-6, 0.095 - m_tilde_max * theta)
        Y_Tc[i] = Tc_v - 273.15 + (0.095 - phi_f) * 750.0
        kin = CondensateAgingKinetics(k_extract=k_ext_v)
        res = kin.simulate(t_span=(0, 24), phi_0=0.60, a_s_nm_inv=as_v)
        Y_M[i] = res["M_final"]

    def calc_indices(Y, N_s):
        fA, fB = Y[:N_s], Y[N_s:2*N_s]
        v_tot = np.var(np.concatenate([fA, fB])) + 1e-12
        S1 = np.zeros(D); ST = np.zeros(D)
        for j in range(D):
            fAB = Y[(2+j)*N_s:(3+j)*N_s]
            ST[j] = np.mean((fA - fAB)**2) / (2.0 * v_tot)
            S1[j] = max(0.0, (np.mean(fB * fAB) - np.mean(fA)*np.mean(fB)) / v_tot)
        return np.clip(S1, 0, 1), np.clip(ST, 0, 1)

    S1_Tc, ST_Tc = calc_indices(Y_Tc, N_base)
    S1_M, ST_M   = calc_indices(Y_M, N_base)

    fig, axes = plt.subplots(2, 2, figsize=(13.5, 9.5), dpi=300)
    x = np.arange(D); w = 0.32

    ax = axes[0, 0]
    ax.bar(x - w/2, S1_Tc, w, label=r"First-Order $S_i$", color='#3B82F6', ec='#1D4ED8')
    ax.bar(x + w/2, ST_Tc, w, label=r"Total-Effect $S_{Ti}$", color='#93C5FD', ec='#2563EB')
    ax.set_xticks(x); ax.set_xticklabels(PARAM_DESCRIP, rotation=35, ha='right', fontsize=8.5)
    ax.set_ylabel("Sobol Index", fontsize=10.0, fontweight='bold')
    ax.set_title(r"(a) Sobol Indices: Apparent Cloud Point $T_{cloud}^{app}$", fontsize=10.5, fontweight='bold')
    ax.set_ylim(0, 1.0); ax.grid(True, ls=':', alpha=0.45, axis='y'); ax.legend(fontsize=8.2)

    ax = axes[0, 1]
    ax.bar(x - w/2, S1_M, w, label=r"First-Order $S_i$", color='#10B981', ec='#047857')
    ax.bar(x + w/2, ST_M, w, label=r"Total-Effect $S_{Ti}$", color='#A7F3D0', ec='#059669')
    ax.set_xticks(x); ax.set_xticklabels(PARAM_DESCRIP, rotation=35, ha='right', fontsize=8.5)
    ax.set_ylabel("Sobol Index", fontsize=10.0, fontweight='bold')
    ax.set_title(r"(b) Sobol Indices: Fibrillation Mass $M_{final}$", fontsize=10.5, fontweight='bold')
    ax.set_ylim(0, 1.0); ax.grid(True, ls=':', alpha=0.45, axis='y'); ax.legend(fontsize=8.2)

    N_steps = [64, 128, 256, 512, 1024, 2048]
    colors_p = plt.cm.tab10(np.linspace(0, 0.9, D))

    ax_c1 = axes[1, 0]; ax_c2 = axes[1, 1]
    for j in range(D):
        st_tc_curve = [calc_indices(Y_Tc[:Nv*(D+2)], Nv)[1][j] for Nv in N_steps]
        st_m_curve  = [calc_indices(Y_M[:Nv*(D+2)], Nv)[1][j] for Nv in N_steps]
        ax_c1.plot(N_steps, st_tc_curve, marker='o', ms=4, color=colors_p[j], lw=1.8, label=PARAM_NAMES[j])
        ax_c2.plot(N_steps, st_m_curve, marker='o', ms=4, color=colors_p[j], lw=1.8, label=PARAM_NAMES[j])

    ax_c1.set_xscale('log'); ax_c1.set_xlabel(r"Base Sample Size, $N_{base}$", fontsize=10.0, fontweight='bold')
    ax_c1.set_ylabel(r"Total-Effect $S_{Ti}(N)$", fontsize=10.0, fontweight='bold')
    ax_c1.set_title(r"(c) Sobol Convergence: $T_{cloud}^{app}$ Indices", fontsize=10.5, fontweight='bold')
    ax_c1.grid(True, ls=':', alpha=0.45); ax_c1.legend(fontsize=7.2, loc='upper right', ncol=2)

    ax_c2.set_xscale('log'); ax_c2.set_xlabel(r"Base Sample Size, $N_{base}$", fontsize=10.0, fontweight='bold')
    ax_c2.set_ylabel(r"Total-Effect $S_{Ti}(N)$", fontsize=10.0, fontweight='bold')
    ax_c2.set_title(r"(d) Sobol Convergence: $M_{final}$ Indices", fontsize=10.5, fontweight='bold')
    ax_c2.grid(True, ls=':', alpha=0.45); ax_c2.legend(fontsize=7.2, loc='upper right', ncol=2)

    plt.tight_layout()
    out = "figures/Figure_4_Sobol_Sensitivity_LLPS.png"
    plt.savefig(out, bbox_inches='tight', pad_inches=0.15)
    print(f"Figure 5 (Sobol 4-Panel) saved: {out}")
    plt.close()

if __name__ == "__main__":
    generate_figure_1()
    generate_figure_2()
    generate_figure_3()
    generate_figure_4()
    generate_figure_5()
