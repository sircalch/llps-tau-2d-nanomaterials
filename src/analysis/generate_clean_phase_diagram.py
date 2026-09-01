import os, sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import root

def compute_clean_publication_phase_diagram():
    print("Generating clean, high-precision analytical phase diagram for Tau LLPS...")
    
    N = 10.0 # Effective segment length of Tau amyloidogenic domain
    phi_c = 1.0 / (1.0 + np.sqrt(N)) # ~ 0.2403
    chi_c = ((1.0 + np.sqrt(N)) ** 2) / (2.0 * N) # ~ 0.8662
    
    A_chi = 580.0
    B_chi = -0.92
    kappa_int = 0.32
    
    sigma_configs = [
        {"sigma": 0.0, "color": "#2563EB", "name": "Bulk Tau (σ_2D = 0.0)"},
        {"sigma": 0.35, "color": "#059669", "name": "Moderate 2D (σ_2D = 0.35)"},
        {"sigma": 0.70, "color": "#DC2626", "name": "High 2D (σ_2D = 0.70)"}
    ]
    
    # Universal Binodal in terms of delta_chi
    delta_chi_vals = np.linspace(0.0001, 0.65, 120)
    
    phi1_univ = [phi_c]
    phi2_univ = [phi_c]
    chi_univ = [chi_c]
    
    def mu(p, c):
        return (1.0 / N) * (np.log(p) + 1.0) - np.log(1.0 - p) - 1.0 + c * (1.0 - 2.0 * p)
    
    def Pi(p, c):
        return - np.log(1.0 - p) - (1.0 - 1.0 / N) * p - c * (p ** 2)
    
    curr_p1 = phi_c - 0.005
    curr_p2 = phi_c + 0.005
    
    for d_chi in delta_chi_vals:
        c = chi_c + d_chi
        
        def res(p):
            p1, p2 = p[0], p[1]
            if p1 <= 1e-7 or p2 >= 1.0 - 1e-7:
                return [10.0, 10.0]
            return [mu(p1, c) - mu(p2, c), Pi(p1, c) - Pi(p2, c)]
        
        sol = root(res, [curr_p1, curr_p2], method='hybr', tol=1e-10)
        if sol.success and 0 < sol.x[0] < phi_c < sol.x[1] < 1:
            curr_p1 = sol.x[0]
            curr_p2 = sol.x[1]
            phi1_univ.append(curr_p1)
            phi2_univ.append(curr_p2)
            chi_univ.append(c)

    phi1_univ = np.array(phi1_univ)
    phi2_univ = np.array(phi2_univ)
    chi_univ = np.array(chi_univ)
    
    fig, ax = plt.subplots(figsize=(8.5, 6.2), dpi=300)
    
    for cfg in sigma_configs:
        sigma = cfg["sigma"]
        color = cfg["color"]
        name = cfg["name"]
        
        chi_eff_crit = chi_c - B_chi + kappa_int * sigma
        Tc_K = A_chi / chi_eff_crit
        Tc_C = Tc_K - 273.15
        
        T_K = A_chi / (chi_univ - B_chi + kappa_int * sigma)
        T_C = T_K - 273.15
        
        valid_idx = np.where(T_C >= 8.0)[0]
        p1_plot = phi1_univ[valid_idx]
        p2_plot = phi2_univ[valid_idx]
        t_plot = T_C[valid_idx]
        
        dome_phi = np.concatenate([p1_plot[::-1], [phi_c], p2_plot])
        dome_t = np.concatenate([t_plot[::-1], [Tc_C], t_plot])
        
        # Plot Binodal
        line, = ax.plot(dome_phi, dome_t, color=color, lw=2.4, label=f"Binodal: {name}")
        ax.fill_betweenx(dome_t, dome_phi, color=color, alpha=0.07)
        
        # Mark Critical Point
        ax.plot(phi_c, Tc_C, marker='o', markersize=6.5, color=color, mec='#0F172A', mew=1.0, zorder=5)
        ax.text(phi_c + 0.018, Tc_C, f"$T_c = {Tc_C:.1f}^\\circ\\mathrm{{C}}$", 
                fontsize=8.5, color=color, weight='bold', va='center')
        
        # Spinodal curve
        phi_sp_range = np.linspace(p1_plot[-1] * 1.05, p2_plot[-1] * 0.98, 100)
        chi_sp = 0.5 * (1.0 / (N * phi_sp_range) + 1.0 / (1.0 - phi_sp_range))
        T_sp_K = A_chi / (chi_sp - B_chi + kappa_int * sigma)
        T_sp_C = T_sp_K - 273.15
        valid_sp = np.where(T_sp_C >= 8.0)[0]
        if len(valid_sp) > 2:
            ax.plot(phi_sp_range[valid_sp], T_sp_C[valid_sp], color=color, lw=1.2, ls='--', alpha=0.75)

    ax.set_xlabel(r"Protein Volume Fraction, $\phi$", fontsize=11, fontweight='bold', labelpad=8)
    ax.set_ylabel(r"Temperature, $T\ (^\circ\mathrm{C})$", fontsize=11, fontweight='bold', labelpad=8)
    ax.set_title("Liquid-Liquid Phase Separation (LLPS) Phase Diagram of Tau\nExact Binodal & Spinodal Modulation by 2D Nanomaterials", 
                 fontsize=11.5, fontweight='bold', pad=12)
    
    ax.set_xlim(0, 0.70)
    ax.set_ylim(8, 62)
    ax.grid(True, ls=':', color='#94A3B8', alpha=0.45)
    
    ax.legend(frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1', fontsize=8.5, loc='upper right', framealpha=0.95)
    
    ax.text(0.38, 16, r"$\mathbf{Two\text{-}Phase\ Coexistence\ (LLPS)}$" + "\n" + r"$\mathrm{Condensate\ Droplets\ +\ Dilute\ Monomer}$", 
            ha='center', va='center', fontsize=9.0, color='#1E293B', bbox=dict(boxstyle='round,pad=0.4', fc='#EFF6FF', ec='#3B82F6', lw=1.2))
    
    ax.text(0.38, 56, r"$\mathbf{Single\text{-}Phase\ Homogeneous\ Fluid\ (Dispersed)}$", 
            ha='center', va='center', fontsize=9.0, color='#1E293B', bbox=dict(boxstyle='round,pad=0.4', fc='#F8FAFC', ec='#94A3B8', lw=1.0))
    
    ax.axhline(37.0, color='#64748B', ls=':', lw=1.2)
    ax.text(0.68, 37.8, r"Physiological $T = 37^\circ\mathrm{C}$", color='#475569', fontsize=8.0, ha='right', style='italic')

    os.makedirs("figures", exist_ok=True)
    out_fig = "figures/Figure_1_Tau_LLPS_Phase_Diagram_2D_Interface.png"
    plt.savefig(out_fig, bbox_inches='tight', pad_inches=0.15)
    print(f"Figure 1 successfully regenerated and saved to {out_fig}")

if __name__ == "__main__":
    compute_clean_publication_phase_diagram()
