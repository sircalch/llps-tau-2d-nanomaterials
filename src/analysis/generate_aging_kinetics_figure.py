import os, sys
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.kinetics.condensate_aging_kinetics import CondensateAgingKinetics

def compute_condensate_aging_kinetics():
    print("Simulating Condensate Aging and Liquid-to-Solid Fibrillation Arrest...")
    kinetics = CondensateAgingKinetics()
    
    sigma_vals = [0.0, 0.20, 0.45, 0.90]
    labels = [
        "Pure Droplet (σ_2D = 0.0)",
        "Low 2D Loading (σ_2D = 0.20)",
        "Moderate 2D Loading (σ_2D = 0.45)",
        "High 2D Loading (σ_2D = 0.90)"
    ]
    colors = ["#DC2626", "#D97706", "#059669", "#2563EB"]
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 9.5), dpi=300)
    
    # ----------------------------------------------------
    # Panel (a): Fibril Mass inside Condensate M_drop(t)
    # ----------------------------------------------------
    ax1 = axes[0, 0]
    for s_idx, sigma in enumerate(sigma_vals):
        res = kinetics.simulate(t_span=(0, 48), phi_0=0.60, sigma_2D=sigma)
        ax1.plot(res["time"], res["M_drop"], color=colors[s_idx], lw=2.2, label=labels[s_idx])
        
    ax1.set_xlabel("Aging Time, $t$ (hours)", fontsize=10.5, fontweight='bold')
    ax1.set_ylabel(r"Solid Fibril Mass Fraction, $M_{drop}(t)$", fontsize=10.5, fontweight='bold')
    ax1.set_title("(a) Liquid-to-Solid Transition (Condensate Hardening)", fontsize=11, fontweight='bold')
    ax1.set_ylim(-0.02, 0.65)
    ax1.grid(True, ls=':', alpha=0.5)
    ax1.legend(fontsize=8.2, loc='upper left', frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1')
    
    # ----------------------------------------------------
    # Panel (b): Dense Monomer Depletion / Droplet Dissolution
    # ----------------------------------------------------
    ax2 = axes[0, 1]
    for s_idx, sigma in enumerate(sigma_vals):
        res = kinetics.simulate(t_span=(0, 48), phi_0=0.60, sigma_2D=sigma)
        ax2.plot(res["time"], res["phi_dense"], color=colors[s_idx], lw=2.2, label=labels[s_idx])
        
    ax2.set_xlabel("Aging Time, $t$ (hours)", fontsize=10.5, fontweight='bold')
    ax2.set_ylabel(r"Liquid Monomer Fraction, $\phi_{dense}(t)$", fontsize=10.5, fontweight='bold')
    ax2.set_title("(b) Droplet Monomer Depletion & Interfacial Dissolution", fontsize=11, fontweight='bold')
    ax2.set_ylim(-0.02, 0.65)
    ax2.grid(True, ls=':', alpha=0.5)
    
    # ----------------------------------------------------
    # Panel (c): Monomer Adsorption on 2D Nanosheet m_ads(t)
    # ----------------------------------------------------
    ax3 = axes[1, 0]
    for s_idx, sigma in enumerate(sigma_vals):
        res = kinetics.simulate(t_span=(0, 48), phi_0=0.60, sigma_2D=sigma)
        ax3.plot(res["time"], res["m_ads"], color=colors[s_idx], lw=2.2, label=labels[s_idx])
        
    ax3.set_xlabel("Aging Time, $t$ (hours)", fontsize=10.5, fontweight='bold')
    ax3.set_ylabel(r"Adsorbed Monomer Mass, $m_{ads}(t)$", fontsize=10.5, fontweight='bold')
    ax3.set_title("(c) Interfacial Monomer Sequestration on 2D Nanosheet", fontsize=11, fontweight='bold')
    ax3.set_ylim(-0.02, 0.65)
    ax3.grid(True, ls=':', alpha=0.5)
    
    # ----------------------------------------------------
    # Panel (d): Fibrillation Lag Time vs 2D Nanosheet Capacity
    # ----------------------------------------------------
    ax4 = axes[1, 1]
    sigma_grid = np.linspace(0.0, 1.2, 50)
    t_lags = []
    final_fibs = []
    
    for s in sigma_grid:
        res = kinetics.simulate(t_span=(0, 72), phi_0=0.60, sigma_2D=s)
        t_lags.append(res["t_lag"])
        final_fibs.append(res["M_final"])
        
    ax4.plot(sigma_grid, t_lags, color='#0F172A', lw=2.4, label=r"Solidification Lag Time $\tau_{lag}$")
    ax4.axvspan(0.55, 1.2, color='#10B981', alpha=0.15, label="Complete Fibrillation Arrest")
    
    ax4.set_xlabel(r"2D Nanomaterial Capacity, $\sigma_{2D}$", fontsize=10.5, fontweight='bold')
    ax4.set_ylabel(r"Solidification Lag Time, $\tau_{lag}$ (hours)", fontsize=10.5, fontweight='bold')
    ax4.set_title(r"(d) Critical 2D Loading for Condensate Fibrillation Arrest", fontsize=11, fontweight='bold')
    ax4.set_ylim(0, 75)
    ax4.grid(True, ls=':', alpha=0.5)
    ax4.legend(fontsize=8.5, loc='upper left', frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1')
    
    plt.tight_layout()
    out_fig = "figures/Figure_3_Condensate_Aging_and_Fibrillation_Arrest.png"
    plt.savefig(out_fig, bbox_inches='tight', pad_inches=0.15)
    print(f"Condensate aging figure successfully saved to: {out_fig}")

if __name__ == "__main__":
    compute_condensate_aging_kinetics()
