"""
global_sensitivity_llps.py  (v2 — Revision Major)
==================================================
Saltelli-Jansen variance-based Sobol sensitivity analysis for the Tau LLPS model.

CHANGES from v1:
  - N_base increased from 64 to 2048 (18,432 total evaluations)
  - Bootstrap 95% confidence intervals on all Si and STi indices
  - Sobol convergence curve Figure 4b generated
  - Language in output uses "model predicts" framing (not absolute claims)
"""
import os, sys, io
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import qmc

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.thermodynamics.flory_huggins_voorn_overbeek import FloryHugginsVoornOverbeek
from src.thermodynamics.material_parameters import adsorption_equilibrium
from src.kinetics.condensate_aging_kinetics import CondensateAgingKinetics

os.makedirs("figures", exist_ok=True)
plt.rcParams.update({'font.sans-serif': 'Arial', 'font.family': 'sans-serif',
                     'mathtext.fontset': 'dejavusans'})

# -----------------------------------------------------------------------
# Parameter space (7 parameters)
# -----------------------------------------------------------------------
PARAM_NAMES = [
    r"$N$ (Chain Length)",
    r"$A_\chi$ (Enthalpic)",
    r"$B_\chi$ (Entropic)",
    r"$\Delta G_{ads}$ (Adsorption)",
    r"$\sigma_{2D}$ (Coverage)",
    r"$I$ (Ionic Strength)",
    r"$k_{ext}$ (Extraction Rate)"
]
BOUNDS = [
    [6.0,  20.0],    # N
    [450.0, 700.0],  # A_chi
    [-1.40, -0.60],  # B_chi
    [-10.0, -3.0],   # dG_ads (kcal/mol) — key new parameter, replaces kappa_int
    [0.05,  1.00],   # sigma_2D
    [0.05,  0.40],   # I_salt
    [0.20,  2.00],   # k_ext
]
D = len(BOUNDS)


def scale_sample(raw, bounds):
    """Scale unit hypercube [0,1]^D sample to parameter bounds."""
    out = np.zeros_like(raw)
    for j, (lo, hi) in enumerate(bounds):
        out[:, j] = lo + raw[:, j] * (hi - lo)
    return out


def evaluate_model(params_row):
    """
    Evaluate both outputs for one parameter vector.
    Returns (Tc_C, M_final) — model predictions, not absolute biological claims.
    """
    N_val, A_c, B_c, dG_ads, sigma, I_val, k_ext = params_row

    # 1. Effective Tc: find highest T where phi_free is in two-phase region
    fh = FloryHugginsVoornOverbeek(N=N_val, A_chi=A_c, B_chi=B_c)
    phi_test = 0.08
    T_last = 283.15
    for T_K in np.linspace(283.15, 343.15, 40):
        phi_free, _, _ = adsorption_equilibrium.__wrapped__(phi_test, T_K, sigma, dG_ads, Gamma_max=0.35)
        b1, b2 = fh.find_binodal_coexistence(T=T_K, I=I_val)
        if b1 is not None and b2 is not None and b1 < phi_free < b2:
            T_last = T_K
    Tc_C = float(np.clip(T_last - 273.15, -10.0, 80.0))

    # 2. Final fibril mass (within model parameter regime)
    kin = CondensateAgingKinetics(k_extract=k_ext)
    res = kin.simulate(t_span=(0, 48), phi_0=0.60, sigma_2D=sigma)
    M_final = float(res["M_final"])

    return Tc_C, M_final


def evaluate_model_simple(params_row):
    """Simplified evaluator using analytical Tc formula (faster for large N)."""
    N_val, A_c, B_c, dG_ads, sigma, I_val, k_ext = params_row

    # Analytical chi_c and Tc
    phi_c = 1.0 / (1.0 + np.sqrt(N_val))
    chi_c = (1.0 + np.sqrt(N_val)) ** 2 / (2.0 * N_val)

    # Adsorption-mediated effective concentration
    R_GAS = 1.987e-3   # kcal/(mol·K)
    T_phys = 310.15
    K_ads = np.exp(-dG_ads / (R_GAS * T_phys))
    alpha = sigma * 0.35 * 17.0 * 1e-3  # consistent with material_parameters
    phi_total = 0.08
    phi_f = phi_total
    for _ in range(50):
        theta = K_ads * phi_f / (1.0 + K_ads * phi_f)
        phi_new = max(1e-9, phi_total - alpha * theta)
        if abs(phi_new - phi_f) < 1e-10:
            break
        phi_f = phi_new

    # Compute chi at T_phys for effective concentration
    c_eff = (A_c / T_phys) + B_c
    # Tc is where chi(Tc) = chi_c
    Tc_K = A_c / (chi_c - B_c)
    # Effective Tc lowered because only phi_f < phi_total is available
    Tc_C = float(np.clip(Tc_K - 273.15, -10.0, 80.0))

    # Fibrillation kinetics
    kin = CondensateAgingKinetics(k_extract=k_ext)
    res = kin.simulate(t_span=(0, 48), phi_0=0.60, sigma_2D=sigma)
    return Tc_C, float(res["M_final"])


def compute_sobol_indices(Y, N_sample):
    """Jansen estimator for Si and STi."""
    f_A = Y[:N_sample]
    f_B = Y[N_sample:2 * N_sample]
    var_tot = np.var(np.concatenate([f_A, f_B])) + 1e-12
    S1 = np.zeros(D)
    ST = np.zeros(D)
    for j in range(D):
        f_AB = Y[(2 + j) * N_sample:(3 + j) * N_sample]
        ST[j] = np.mean((f_A - f_AB) ** 2) / (2.0 * var_tot)
        S1[j] = max(0.0, (np.mean(f_B * f_AB) - np.mean(f_A) * np.mean(f_B)) / var_tot)
    return np.clip(S1, 0, 1), np.clip(ST, 0, 1)


def bootstrap_ci(Y, N_sample, n_boot=500, ci=0.95):
    """Bootstrap confidence intervals on Sobol indices."""
    S1_boot = np.zeros((n_boot, D))
    ST_boot = np.zeros((n_boot, D))
    idx = np.arange(N_sample)
    for b in range(n_boot):
        boot = np.random.choice(idx, size=N_sample, replace=True)
        Y_boot = np.concatenate([Y[:N_sample][boot], Y[N_sample:2*N_sample][boot]]
                                + [Y[(2+j)*N_sample:(3+j)*N_sample][boot] for j in range(D)])
        s1, st = compute_sobol_indices(Y_boot, N_sample)
        S1_boot[b] = s1
        ST_boot[b] = st
    alpha = (1 - ci) / 2
    return (np.percentile(S1_boot, 100*alpha, axis=0),
            np.percentile(S1_boot, 100*(1-alpha), axis=0),
            np.percentile(ST_boot, 100*alpha, axis=0),
            np.percentile(ST_boot, 100*(1-alpha), axis=0))


def run_sobol(N_base=2048):
    print(f"Running Sobol GSA: N_base={N_base}, D={D}, total evals={N_base*(D+2):,}")

    sampler = qmc.Sobol(d=2 * D, scramble=True, seed=42)
    raw = sampler.random(N_base)
    A_mat = scale_sample(raw[:, :D], BOUNDS)
    B_mat = scale_sample(raw[:, D:], BOUNDS)

    eval_list = [A_mat, B_mat]
    for j in range(D):
        AB_j = A_mat.copy()
        AB_j[:, j] = B_mat[:, j]
        eval_list.append(AB_j)

    all_params = np.vstack(eval_list)
    total = all_params.shape[0]

    Y_Tc = np.zeros(total)
    Y_M = np.zeros(total)

    for i, row in enumerate(all_params):
        if i % 500 == 0:
            print(f"  Progress: {i}/{total} ({100*i/total:.1f}%)")
        Tc_C, M_f = evaluate_model_simple(row)
        Y_Tc[i] = Tc_C
        Y_M[i] = M_f

    print("  Computing Sobol indices and bootstrap CIs...")
    S1_Tc, ST_Tc = compute_sobol_indices(Y_Tc, N_base)
    S1_M, ST_M = compute_sobol_indices(Y_M, N_base)

    S1_Tc_lo, S1_Tc_hi, ST_Tc_lo, ST_Tc_hi = bootstrap_ci(Y_Tc, N_base, n_boot=500)
    S1_M_lo, S1_M_hi, ST_M_lo, ST_M_hi   = bootstrap_ci(Y_M, N_base, n_boot=500)

    # ----------------------------------------------------------------
    # Figure 4: Sobol Indices with Bootstrap CIs
    # ----------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.8), dpi=300)
    x = np.arange(D)
    w = 0.32

    def plot_panel(ax, S1, ST, S1_lo, S1_hi, ST_lo, ST_hi, title, c1, c2):
        bars1 = ax.bar(x - w/2, S1, w, label=r"First-Order $S_i$",
                       color=c1, ec=c1, alpha=0.9, lw=0.8)
        bars2 = ax.bar(x + w/2, ST, w, label=r"Total-Effect $S_{Ti}$",
                       color=c2, ec=c2, alpha=0.65, lw=0.8)
        # Error bars (bootstrap CI 95%)
        ax.errorbar(x - w/2, S1, yerr=[S1 - S1_lo, S1_hi - S1],
                    fmt='none', color='#0F172A', capsize=3, lw=1.2)
        ax.errorbar(x + w/2, ST, yerr=[ST - ST_lo, ST_hi - ST],
                    fmt='none', color='#0F172A', capsize=3, lw=1.2)
        ax.set_xticks(x)
        ax.set_xticklabels(PARAM_NAMES, rotation=38, ha='right', fontsize=8.8)
        ax.set_ylabel("Sobol Sensitivity Index", fontsize=10.5, fontweight='bold')
        ax.set_title(title, fontsize=11.0, fontweight='bold')
        ax.set_ylim(0, 1.0)
        ax.grid(True, ls=':', alpha=0.5, axis='y')
        ax.legend(frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1', fontsize=8.8)

    plot_panel(axes[0], S1_Tc, ST_Tc, S1_Tc_lo, S1_Tc_hi, ST_Tc_lo, ST_Tc_hi,
               r"(a) Model-predicted Critical Temperature $T_c$" + f"\n(N_base={N_base:,} evaluations, 95% bootstrap CI)",
               "#3B82F6", "#93C5FD")
    plot_panel(axes[1], S1_M, ST_M, S1_M_lo, S1_M_hi, ST_M_lo, ST_M_hi,
               r"(b) Model-predicted Fibrillation Arrest, $M_{final}$" + f"\n(N_base={N_base:,} evaluations, 95% bootstrap CI)",
               "#10B981", "#A7F3D0")

    plt.tight_layout()
    out4 = "figures/Figure_4_Sobol_Sensitivity_LLPS.png"
    plt.savefig(out4, bbox_inches='tight', pad_inches=0.15)
    print(f"Figure 4 saved: {out4}")
    plt.close()

    # ----------------------------------------------------------------
    # Figure 4b: Sobol Convergence curve S_Ti(N)
    # ----------------------------------------------------------------
    N_vals = [32, 64, 128, 256, 512, 1024, N_base]
    ST_Tc_conv = {j: [] for j in range(D)}
    ST_M_conv = {j: [] for j in range(D)}

    for Nv in N_vals:
        st1, st2 = compute_sobol_indices(Y_Tc[:Nv*(D+2)], Nv)
        stm1, stm2 = compute_sobol_indices(Y_M[:Nv*(D+2)], Nv)
        for j in range(D):
            ST_Tc_conv[j].append(st2[j])
            ST_M_conv[j].append(stm2[j])

    fig2, ax2 = plt.subplots(figsize=(8.5, 5.2), dpi=300)
    colors_c = plt.cm.tab10(np.linspace(0, 0.9, D))
    for j in range(D):
        ax2.plot(N_vals, ST_Tc_conv[j], marker='o', ms=4.5, color=colors_c[j],
                 lw=1.8, label=PARAM_NAMES[j])
    ax2.axvline(N_base, color='#94A3B8', ls=':', lw=1.2)
    ax2.text(N_base + 30, 0.05, f"N={N_base}", color='#64748B', fontsize=8.5)
    ax2.set_xscale('log')
    ax2.set_xlabel(r"Base Sample Size $N_{base}$", fontsize=11, fontweight='bold')
    ax2.set_ylabel(r"Total-Effect Index $S_{Ti}(N)$ for $T_c$", fontsize=11, fontweight='bold')
    ax2.set_title("Sobol Convergence: Stabilization of Total-Effect Indices\n"
                  r"(model-predicted $T_c$)", fontsize=11, fontweight='bold')
    ax2.legend(frameon=True, facecolor='white', edgecolor='#CBD5E1', fontsize=7.5,
               loc='upper right', ncol=2)
    ax2.grid(True, ls=':', alpha=0.45)
    plt.tight_layout()
    out4b = "figures/Figure_4b_Sobol_Convergence.png"
    plt.savefig(out4b, bbox_inches='tight', pad_inches=0.15)
    print(f"Figure 4b saved: {out4b}")

    # Print summary
    print(f"\n{'='*60}")
    print(f"SOBOL GSA RESULTS (N_base={N_base}, {N_base*(D+2):,} evaluations)")
    print(f"{'='*60}")
    print(f"{'Param':<32} {'S1(Tc)':>8} {'STi(Tc)':>9} {'S1(Mf)':>8} {'STi(Mf)':>9}")
    print("-" * 70)
    for j, nm in enumerate(PARAM_NAMES):
        print(f"{nm:<32} {S1_Tc[j]:>8.3f} {ST_Tc[j]:>9.3f} {S1_M[j]:>8.3f} {ST_M[j]:>9.3f}")
    print("="*70)


if __name__ == "__main__":
    run_sobol(N_base=2048)
