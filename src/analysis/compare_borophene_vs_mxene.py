"""
compare_borophene_vs_mxene.py
=============================
Generate Figure 5: Side-by-side comparison of Borophene vs MXene across
all four observables: Tc (emergent), contact angle theta_c, tau_lag, M_final.

This figure directly demonstrates that the two materials produce different
quantitative predictions, addressing the reviewer's central criticism.
"""
import os, sys, io
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.thermodynamics.material_parameters import adsorption_equilibrium, MATERIAL_PARAMS
from src.thermodynamics.flory_huggins_voorn_overbeek import FloryHugginsVoornOverbeek
from src.thermodynamics.cahn_hilliard_wetting import CahnHilliardWetting
from src.kinetics.condensate_aging_kinetics import CondensateAgingKinetics

os.makedirs("figures", exist_ok=True)

plt.rcParams.update({'font.sans-serif': 'Arial', 'font.family': 'sans-serif',
                     'mathtext.fontset': 'dejavusans'})

def run_comparison():
    print("Generating Borophene vs MXene quantitative comparison (Figure 5)...")
    fh = FloryHugginsVoornOverbeek()
    wetting = CahnHilliardWetting(fh_model=fh)
    kin = CondensateAgingKinetics()

    sigma_grid = np.linspace(0.0, 1.0, 40)
    materials = ["borophene", "mxene"]
    mat_labels = {"borophene": "Borophene (alpha-B, DFT-calib.)", 
                  "mxene": "MXene (Ti3C2Tx, MD-calib.)"}
    mat_colors = {"borophene": MATERIAL_PARAMS["borophene"]["color"],
                  "mxene": MATERIAL_PARAMS["mxene"]["color"]}
    mat_ls = {"borophene": "-", "mxene": "--"}

    results = {mat: {"sigma": sigma_grid,
                     "Tc_C": [], "theta_deg": [],
                     "tau_lag": [], "M_final": []}
               for mat in materials}

    phi_test = 0.08   # total protein concentration representative of experiments
    T_phys = 310.15   # 37 °C

    # Universal binodal (bulk, no surface) for reference
    b1_bulk, b2_bulk = fh.find_binodal_coexistence(T=T_phys, I=0.155)
    gamma_LL_ref = wetting.gamma_LL_SI(T=T_phys)
    print(f"Bulk: phi_dilute={b1_bulk:.4f}, phi_dense={b2_bulk:.4f}, "
          f"gamma_LL={gamma_LL_ref*1e6:.3f} uN/m")

    for mat in materials:
        print(f"\nComputing {mat_labels[mat]} sigma sweep...")
        for sigma in sigma_grid:
            # 1. Emergent Tc: highest T at which phi_free is still in two-phase region
            # Scan T from 15C to 60C, find last T with b1 < phi_free < b2
            T_last_coex = 283.15  # 10 C
            for T_K in np.linspace(283.15, 333.15, 60):
                phi_free, _, _ = adsorption_equilibrium(phi_test, T_K, sigma, mat)
                b1, b2 = fh.find_binodal_coexistence(T=T_K, I=0.155)
                if b1 is not None and b2 is not None and b1 < phi_free < b2:
                    T_last_coex = T_K
            results[mat]["Tc_C"].append(T_last_coex - 273.15)

            # 2. Contact angle from Young's equation (derived)
            theta, _, _, _ = wetting.young_contact_angle(T=T_phys, I=0.155, material=mat)
            results[mat]["theta_deg"].append(theta)

            # 3. Kinetics: use k_ext and k_des from material params
            k_ext = MATERIAL_PARAMS[mat]["k_ext_per_h"]
            k_des = MATERIAL_PARAMS[mat]["k_des_per_h"]
            kin_mat = CondensateAgingKinetics(k_extract=k_ext, k_desorb=k_des)
            res = kin_mat.simulate(t_span=(0, 72), phi_0=0.60, sigma_2D=sigma)
            results[mat]["tau_lag"].append(res["t_lag"])
            results[mat]["M_final"].append(res["M_final"])

    # ----------------------------------------------------------------
    # Figure 5: 2x2 panel comparison
    # ----------------------------------------------------------------
    fig = plt.figure(figsize=(12.5, 10.5), dpi=300)
    gs = gridspec.GridSpec(2, 2, hspace=0.40, wspace=0.38)

    ax_Tc  = fig.add_subplot(gs[0, 0])
    ax_th  = fig.add_subplot(gs[0, 1])
    ax_lag = fig.add_subplot(gs[1, 0])
    ax_Mf  = fig.add_subplot(gs[1, 1])

    for mat in materials:
        lbl = mat_labels[mat]
        col = mat_colors[mat]
        ls  = mat_ls[mat]
        s   = results[mat]["sigma"]

        ax_Tc.plot(s, results[mat]["Tc_C"], color=col, lw=2.4, ls=ls, label=lbl)
        ax_th.plot(s, results[mat]["theta_deg"], color=col, lw=2.4, ls=ls, label=lbl)
        ax_lag.plot(s, results[mat]["tau_lag"], color=col, lw=2.4, ls=ls, label=lbl)
        ax_Mf.plot(s, results[mat]["M_final"], color=col, lw=2.4, ls=ls, label=lbl)

    # Panel (a) — Tc
    ax_Tc.axhline(37.0, color='#475569', ls=':', lw=1.2)
    ax_Tc.text(0.02, 37.6, r"$T_{phys} = 37^\circ\mathrm{C}$", color='#475569', fontsize=8.2, style='italic')
    ax_Tc.set_xlabel(r"Surface Coverage, $\sigma_{2D}$", fontsize=10.5, fontweight='bold')
    ax_Tc.set_ylabel(r"Effective $T_c\ (^\circ\mathrm{C})$", fontsize=10.5, fontweight='bold')
    ax_Tc.set_title(r"(a) Emergent Critical Temperature $T_c$"+"\n(from adsorption equilibrium, not algebraic)",
                    fontsize=10.5, fontweight='bold')
    ax_Tc.set_xlim(0, 1); ax_Tc.grid(True, ls=':', alpha=0.5)
    ax_Tc.legend(frameon=True, facecolor='white', edgecolor='#CBD5E1', fontsize=8.5, loc='upper right')

    # Panel (b) — Contact angle (theta)
    ax_th.axhline(90.0, color='#94A3B8', ls=':', lw=1.0)
    ax_th.text(0.02, 91.5, r"Hydrophilic limit ($\theta=90°$)", color='#94A3B8', fontsize=8.0, style='italic')
    ax_th.set_xlabel(r"Surface Coverage, $\sigma_{2D}$", fontsize=10.5, fontweight='bold')
    ax_th.set_ylabel(r"Contact Angle, $\theta_c$ (degrees)", fontsize=10.5, fontweight='bold')
    ax_th.set_title(r"(b) Condensate Contact Angle $\theta_c$"+"\n(derived from Young's equation)",
                    fontsize=10.5, fontweight='bold')
    ax_th.set_xlim(0, 1); ax_th.set_ylim(0, 120)
    ax_th.grid(True, ls=':', alpha=0.5)
    ax_th.legend(frameon=True, facecolor='white', edgecolor='#CBD5E1', fontsize=8.5, loc='upper right')

    # Panel (c) — tau_lag
    ax_lag.axhline(72, color='#94A3B8', ls=':', lw=1.0)
    ax_lag.text(0.02, 73, "Observation window (72 h)", color='#94A3B8', fontsize=8.0, style='italic')
    ax_lag.set_xlabel(r"Surface Coverage, $\sigma_{2D}$", fontsize=10.5, fontweight='bold')
    ax_lag.set_ylabel(r"Solidification Lag Time, $\tau_{lag}$ (h)", fontsize=10.5, fontweight='bold')
    ax_lag.set_title(r"(c) Model-predicted Kinetic Arrest Onset $\tau_{lag}$"+"\n(predicted suppression of secondary nucleation)",
                     fontsize=10.5, fontweight='bold')
    ax_lag.set_xlim(0, 1); ax_lag.grid(True, ls=':', alpha=0.5)
    ax_lag.legend(frameon=True, facecolor='white', edgecolor='#CBD5E1', fontsize=8.5, loc='upper left')

    # Panel (d) — M_final
    ax_Mf.set_xlabel(r"Surface Coverage, $\sigma_{2D}$", fontsize=10.5, fontweight='bold')
    ax_Mf.set_ylabel(r"Final Fibril Mass Fraction, $M_{final}$", fontsize=10.5, fontweight='bold')
    ax_Mf.set_title(r"(d) Final Fibril Conversion $M_{final}$"+"\n(within explored parameter regime)",
                    fontsize=10.5, fontweight='bold')
    ax_Mf.set_xlim(0, 1); ax_Mf.set_ylim(-0.02, 0.65)
    ax_Mf.grid(True, ls=':', alpha=0.5)
    ax_Mf.legend(frameon=True, facecolor='white', edgecolor='#CBD5E1', fontsize=8.5, loc='upper right')

    # Material parameter annotation box
    box_txt = (
        "Material Parameters (literature-derived):\n"
        r"$\Delta G_{ads}^{Boro}= -8.2\ \mathrm{kcal/mol}$" + "\n"
        r"$\Delta G_{ads}^{MXene}= -5.6\ \mathrm{kcal/mol}$" + "\n"
        r"$h_s^{Boro}=15.1\ \mathrm{\mu N/m},\quad h_s^{MXene}=7.1\ \mathrm{\mu N/m}$"
    )
    fig.text(0.50, 0.01, box_txt, ha='center', va='bottom', fontsize=8.2,
             bbox=dict(boxstyle='round,pad=0.4', fc='#F8FAFC', ec='#3B82F6', lw=1.0))

    fig.suptitle("Figure 5: Borophene vs MXene — Quantitative Differentiation\n"
                 "of LLPS Modulation, Wetting, and Condensate Aging Kinetics",
                 fontsize=12.5, fontweight='bold', y=1.01)

    out = "figures/Figure_5_Borophene_vs_MXene_Comparison.png"
    plt.savefig(out, bbox_inches='tight', pad_inches=0.18)
    print(f"\nFigure 5 saved: {out}")

    # Print quantitative comparison table
    print("\n" + "="*65)
    print("KEY RESULTS: Borophene vs MXene at sigma_2D = 0.5")
    print("="*65)
    for mat in materials:
        idx = np.argmin(np.abs(sigma_grid - 0.5))
        Tc = results[mat]["Tc_C"][idx]
        th = results[mat]["theta_deg"][idx]
        tl = results[mat]["tau_lag"][idx]
        mf = results[mat]["M_final"][idx]
        print(f"{mat_labels[mat]}:")
        print(f"  Tc = {Tc:.1f} C  |  theta = {th:.1f} deg  |  tau_lag = {tl:.1f} h  |  M_final = {mf:.3f}")
    print("="*65)

if __name__ == "__main__":
    run_comparison()
