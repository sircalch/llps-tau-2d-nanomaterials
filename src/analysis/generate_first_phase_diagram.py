import sys, os
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import root_scalar, minimize

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.thermodynamics.flory_huggins_voorn_overbeek import FloryHugginsVoornOverbeek

def compute_smooth_phase_diagram():
    print("Computing exact analytical and smooth phase diagram for Tau LLPS...")
    model = FloryHugginsVoornOverbeek(N=50, A_chi=980.0, B_chi=-1.85, kappa_int=0.35)
    
    # Critical point analytical coordinates
    phi_c = 1.0 / (1.0 + np.sqrt(model.N))
    chi_c = ((1.0 + np.sqrt(model.N)) ** 2) / (2.0 * model.N)
    
    sigma_vals = [0.0, 0.35, 0.70]
    labels = [
        "Pure Bulk Tau (σ_2D = 0.0)",
        "Moderate 2D Interface (σ_2D = 0.35)",
        "High 2D Interface (σ_2D = 0.70)"
    ]
    colors = ["#2563EB", "#059669", "#DC2626"]
    
    fig, ax = plt.subplots(figsize=(8.5, 6.2), dpi=300)
    
    for s_idx, sigma in enumerate(sigma_vals):
        # Calculate exact Tc for this sigma_2D
        chi_eff_base = chi_c - model.B_chi + model.kappa_int * sigma
        Tc = model.A_chi / chi_eff_base
        Tc_degC = Tc - 273.15
        
        # Temperature sweep below Tc
        T_min = 280.15 # 7 C
        if Tc < T_min:
            continue
            
        T_points = np.linspace(T_min, Tc - 0.05, 120)
        
        phi_dilute = []
        phi_dense = []
        t_valid = []
        
        # Spinodal curves
        sp_dilute = []
        sp_dense = []
        t_sp_valid = []
        
        for T in T_points:
            # 1. Spinodal calculation (analytical zero crossing of d2f/dphi2)
            def d2f(p):
                return model.spinodal_derivative(p, T=T, I=0.15, sigma_2D=sigma)
            
            try:
                # Root 1 (dilute branch: 0 < phi < phi_c)
                res_sp1 = root_scalar(d2f, bracket=[1e-5, phi_c - 1e-4], method='brentq')
                # Root 2 (dense branch: phi_c < phi < 0.999)
                res_sp2 = root_scalar(d2f, bracket=[phi_c + 1e-4, 0.995], method='brentq')
                if res_sp1.converged and res_sp2.converged:
                    sp_dilute.append(res_sp1.root)
                    sp_dense.append(res_sp2.root)
                    t_sp_valid.append(T - 273.15)
            except Exception:
                pass
            
            # 2. Binodal calculation via exact grand canonical potential minimization
            b1, b2 = model.find_binodal_coexistence(T=T, I=0.15, sigma_2D=sigma)
            if b1 is not None and b2 is not None and b1 < phi_c < b2:
                phi_dilute.append(b1)
                phi_dense.append(b2)
                t_valid.append(T - 273.15)

        # Append critical point to smoothly close the binodal dome
        phi_dilute = np.array(phi_dilute)
        phi_dense = np.array(phi_dense)
        t_valid = np.array(t_valid)
        
        if len(t_valid) > 5:
            # Build closed dome curve
            binodal_phi = np.concatenate([phi_dilute, [phi_c], phi_dense[::-1]])
            binodal_t = np.concatenate([t_valid, [Tc_degC], t_valid[::-1]])
            
            # Plot Binodal Dome
            ax.plot(binodal_phi, binodal_t, color=colors[s_idx], lw=2.4, label=f"Binodal: {labels[s_idx]}")
            ax.fill_betweenx(binodal_t, binodal_phi, color=colors[s_idx], alpha=0.06)
            
            # Mark Critical Point with circle
            ax.plot(phi_c, Tc_degC, marker='o', markersize=6.5, color=colors[s_idx], mec='#0F172A', mew=1.0)
            ax.text(phi_c + 0.015, Tc_degC, f"$T_c = {Tc_degC:.1f}^\\circ\\mathrm{{C}}$", 
                    fontsize=8.5, color=colors[s_idx], weight='bold', va='center')

        # Plot Spinodal Dome
        if len(t_sp_valid) > 5:
            sp_phi = np.concatenate([sp_dilute, [phi_c], sp_dense[::-1]])
            sp_t = np.concatenate([t_sp_valid, [Tc_degC], t_sp_valid[::-1]])
            ax.plot(sp_phi, sp_t, color=colors[s_idx], lw=1.2, ls='--', alpha=0.75, label=f"Spinodal: {labels[s_idx]}")

    ax.set_xlabel(r"Protein Volume Fraction, $\phi$", fontsize=11, fontweight='bold')
    ax.set_ylabel(r"Temperature, $T\ (^\circ\mathrm{C})$", fontsize=11, fontweight='bold')
    ax.set_title("Liquid-Liquid Phase Separation (LLPS) Phase Diagram of Tau\nExact Thermodynamic Binodal and Spinodal Modulation by 2D Nanomaterials", 
                 fontsize=11.5, fontweight='bold', pad=12)
    
    ax.set_xlim(0, 0.75)
    ax.set_ylim(8, 62)
    ax.grid(True, ls=':', alpha=0.5)
    
    # Legend
    ax.legend(frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1', fontsize=8.2, loc='upper right', framealpha=0.95)
    
    # Annotate Thermodynamic Regions
    ax.text(0.32, 18, r"$\mathbf{Two\text{-}Phase\ Coexistence\ Region\ (LLPS)}$" + "\n" + r"$\mathrm{Condensate\ Droplets\ +\ Dilute\ Monomer}$", 
            ha='center', va='center', fontsize=9.2, color='#1E293B', bbox=dict(boxstyle='round,pad=0.5', fc='#EFF6FF', ec='#3B82F6', lw=1.2))
    
    ax.text(0.32, 57, r"$\mathbf{Single\text{-}Phase\ Homogeneous\ Solution\ (Dispersed)}$", 
            ha='center', va='center', fontsize=9.2, color='#1E293B', bbox=dict(boxstyle='round,pad=0.5', fc='#F8FAFC', ec='#94A3B8', lw=1.0))
    
    # Draw physiological temperature line
    ax.axhline(37.0, color='#64748B', ls=':', lw=1.2)
    ax.text(0.68, 37.8, r"Physiological $T = 37^\circ\mathrm{C}$", color='#475569', fontsize=8.0, ha='right', style='italic')

    plt.tight_layout()
    out_fig = "figures/Figure_1_Tau_LLPS_Phase_Diagram_2D_Interface.png"
    plt.savefig(out_fig)
    print(f"Smooth, publication-grade phase diagram saved to {out_fig}!")

if __name__ == "__main__":
    compute_smooth_phase_diagram()
