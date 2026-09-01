import sys, os
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.thermodynamics.flory_huggins_voorn_overbeek import FloryHugginsVoornOverbeek
from src.thermodynamics.cahn_hilliard_wetting import CahnHilliardWetting

def compute_wetting_and_salt_maps():
    print("Computing Wetting Transitions and Salt-Dependent Phase Maps...")
    model = FloryHugginsVoornOverbeek(N=50, A_chi=980.0, B_chi=-1.85, kappa_int=0.40)
    ch = CahnHilliardWetting(model)
    
    os.makedirs("figures", exist_ok=True)
    os.makedirs("results", exist_ok=True)
    
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), dpi=300)
    
    # -------------------------------------------------------------------
    # Panel (a): Ionic Strength / Salt Phase Diagram ([NaCl] vs T)
    # -------------------------------------------------------------------
    ax1 = axes[0]
    salt_concs = np.linspace(0.05, 0.50, 40) # 50 mM to 500 mM NaCl
    T_range = np.linspace(283.15, 333.15, 45) # 10 C to 60 C
    
    # Grid of Binodal width (phi_dense - phi_dilute)
    binodal_gap = np.zeros((len(T_range), len(salt_concs)))
    
    for i, T in enumerate(T_range):
        for j, I_salt in enumerate(salt_concs):
            b1, b2 = model.find_binodal_coexistence(T=T, I=I_salt, sigma_2D=0.0)
            if b1 is not None and b2 is not None:
                binodal_gap[i, j] = b2 - b1
            else:
                binodal_gap[i, j] = 0.0

    X, Y = np.meshgrid(salt_concs * 1000, T_range - 273.15)
    c1 = ax1.contourf(X, Y, binodal_gap, levels=20, cmap='Spectral_r')
    cbar1 = plt.colorbar(c1, ax=ax1)
    cbar1.set_label(r"Phase Density Contrast, $\Delta\phi = \phi_{dense} - \phi_{dilute}$", fontsize=9.5, fontweight='bold')
    
    # Boundary contour
    ax1.contour(X, Y, binodal_gap, levels=[0.01], colors='#1E293B', linewidths=2.0)
    
    ax1.set_xlabel(r"Ionic Strength / $[\mathrm{NaCl}]\ (\mathrm{mM})$", fontsize=10.5, fontweight='bold')
    ax1.set_ylabel(r"Temperature, $T\ (^\circ\mathrm{C})$", fontsize=10.5, fontweight='bold')
    ax1.set_title("(a) Salt Screening & Electrostatic LLPS Boundary", fontsize=11, fontweight='bold')
    ax1.grid(True, ls=':', alpha=0.4)
    
    # -------------------------------------------------------------------
    # Panel (b): Wetting Transition on 2D Interface (h_s vs T)
    # -------------------------------------------------------------------
    ax2 = axes[1]
    h_surface_vals = np.linspace(0.0, 0.30, 40) # Interfacial affinity parameter
    T_wetting = np.linspace(285.15, 320.15, 35)
    
    wetting_state = np.zeros((len(T_wetting), len(h_surface_vals)))
    
    for i, T in enumerate(T_wetting):
        gamma_LL = ch.calculate_liquid_liquid_surface_tension(T=T, I=0.15, sigma_2D=0.0)
        b1, b2 = model.find_binodal_coexistence(T, 0.15, 0.0)
        for j, h_s in enumerate(h_surface_vals):
            if b1 is None or b2 is None or gamma_LL <= 1e-9:
                wetting_state[i, j] = 0.0 # Homogeneous (No Droplets)
            else:
                delta_gamma = h_s * (b2 - b1)
                cos_th = delta_gamma / (gamma_LL * 1e-3 + 1e-6)
                if cos_th >= 1.0:
                    wetting_state[i, j] = 2.0 # Complete Wetting (Film / Dissolution)
                elif cos_th <= -1.0:
                    wetting_state[i, j] = -1.0 # Dewetting
                else:
                    wetting_state[i, j] = 1.0 # Partial Wetting (Sessile Droplet)

    X_w, Y_w = np.meshgrid(h_surface_vals, T_wetting - 273.15)
    cmap_w = plt.get_cmap('coolwarm', 3)
    c2 = ax2.contourf(X_w, Y_w, wetting_state, levels=[-0.5, 0.5, 1.5, 2.5], cmap=cmap_w, alpha=0.85)
    
    cbar2 = plt.colorbar(c2, ax=ax2, ticks=[0, 1, 2])
    cbar2.ax.set_yticklabels(['Homogeneous / Dispersed', 'Partial Wetting (Droplet)', 'Complete Wetting (Film)'])
    
    ax2.set_xlabel(r"2D Interfacial Affinity Parameter, $h_s\ (\mathrm{kcal/mol})$", fontsize=10.5, fontweight='bold')
    ax2.set_ylabel(r"Temperature, $T\ (^\circ\mathrm{C})$", fontsize=10.5, fontweight='bold')
    ax2.set_title(r"(b) 2D Wetting Transition Regimes $(\mathrm{Borophene/MXene})$", fontsize=11, fontweight='bold')
    ax2.grid(True, ls=':', alpha=0.4)
    
    plt.tight_layout()
    out_fig = "figures/Figure_2_Wetting_and_Salt_Phase_Diagrams.png"
    plt.savefig(out_fig)
    print(f"Wetting and salt phase diagrams successfully saved to {out_fig}!")

if __name__ == "__main__":
    compute_wetting_and_salt_maps()
