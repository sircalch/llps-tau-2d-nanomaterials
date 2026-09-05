import sys, os, time
sys.path.insert(0, '.')
import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
from SALib.sample import sobol as sobol_sample
from SALib.analyze import sobol as sobol_analyze
from src.thermodynamics.flory_huggins_voorn_overbeek import FloryHugginsVoornOverbeek
from src.thermodynamics.cahn_hilliard_wetting import CahnHilliardWetting
from src.kinetics.condensate_aging_kinetics import CondensateAgingKinetics

PARAM_NAMES = ['N_eff', 'beta', 'Tc_K', 'dG_ads', 'a_s', 'I_M', 'eta_eff', 'k_ext']
D = len(PARAM_NAMES)
N_BASE = 1024
CONV_BLOCKS = [128, 256, 512, 1024]  # nested dyadic sub-blocks for the convergence table
T_WET_K = 310.15  # physiological 37 degC, the fixed wetting evaluation temperature used throughout the paper
GAMMA_MAX_FIXED = 0.38  # nm^-2, same borophene-scale site density held fixed for a_s/dG_ads elsewhere in this GSA

BOUNDS = [
    [6.0, 18.0],
    [0.005, 0.015],
    [275.15, 287.15],
    [-10.0, -3.0],
    [5.0e-6, 1.0e-4],
    [0.05, 0.35],
    [0.10e-3, 0.35e-3],
    [0.20, 2.50]
]

problem = {
    'num_vars': D,
    'names': PARAM_NAMES,
    'bounds': BOUNDS
}

def eval_single(row):
    Nv, bv, Tv, dGv, asv, Iv, etv, kv = row
    fh = FloryHugginsVoornOverbeek(N=Nv, Tc_K=Tv, beta=bv)
    # Continuous solver: returns a smoothly extrapolated crossing when the root lies
    # outside the [Tc, 65 degC] window, so Y_Tc has no clamp-induced discontinuity.
    tc = fh.calculate_apparent_cloud_point(a_s_nm_inv=asv, dG_ads=dGv, I_M=Iv, Gamma_max=GAMMA_MAX_FIXED)
    tc_val = float(tc)

    kin = CondensateAgingKinetics(k_extract=kv)
    res = kin.simulate(t_span=(0, 24), phi_0=0.60, a_s_nm_inv=asv)

    # theta_c at the fixed physiological T = 37 degC used throughout the paper. Because
    # Tc_K in Table 3 (275.15-287.15 K) is always far below 310.15 K, the bulk binodal is
    # robustly supercritical here regardless of the other 7 sampled parameters -- no
    # near-critical fragility of the kind documented for calculate_apparent_cloud_point.
    # a_s and k_ext do not enter the wetting formula (theta_c uses the bulk binodal
    # compositions, not the adsorption-depleted state), so both are expected structural
    # zeros here, same as eta_eff/k_ext are for T_cloud and the thermodynamic block is for
    # M_final.
    phi_d, phi_dd = fh.find_binodal_coexistence(T_WET_K, I_M=Iv)
    if phi_d is None:
        theta_val = 90.0
    else:
        wetting = CahnHilliardWetting(fh_model=fh)
        gamma_LL_si = wetting.calculate_gamma_LL_SI(T_WET_K, I_M=Iv)
        if gamma_LL_si < 1e-20:
            theta_val = 90.0
        else:
            K_deg = np.exp(-dGv / (1.987e-3 * T_WET_K))
            a_dilute = (phi_d / 9.5e-4) / 1.0e6
            a_dense = (phi_dd / 9.5e-4) / 1.0e6
            ratio = (1.0 + K_deg * a_dense) / (1.0 + K_deg * a_dilute)
            delta_gamma_si = etv * (1.381e-23 * T_WET_K) * (GAMMA_MAX_FIXED * 1e18) * np.log(max(1.0, ratio))
            cos_t = np.clip(delta_gamma_si / gamma_LL_si, -1.0, 1.0)
            theta_val = float(np.degrees(np.arccos(cos_t)))

    return tc_val, res['M_final'], theta_val

def main():
    print(f'Generating SALib Sobol sample (D={D}, N_base={N_BASE}, calc_second_order=False, scramble=True, seed=42)...')
    param_values = sobol_sample.sample(problem, N_BASE, calc_second_order=False, scramble=True, seed=42)
    total_evals = param_values.shape[0]
    print(f'Total physical evaluations to execute: {total_evals}')

    t0 = time.time()
    # Execute in parallel
    workers = min(12, os.cpu_count() or 4)
    print(f'Executing across {workers} parallel workers...')
    with ProcessPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(eval_single, param_values, chunksize=32))
    t1 = time.time()
    print(f'All {total_evals} physical evaluations completed in {t1 - t0:.2f} s ({(t1 - t0)/total_evals:.4f} s/eval)')

    Y_Tc    = np.array([r[0] for r in results])
    Y_M     = np.array([r[1] for r in results])
    Y_theta = np.array([r[2] for r in results])

    os.makedirs('data', exist_ok=True)
    np.savez_compressed('data/sobol_evaluations_N1024.npz', param_values=param_values, Y_Tc=Y_Tc, Y_M=Y_M, Y_theta=Y_theta)
    print('Saved raw evaluations to data/sobol_evaluations_N1024.npz')

    print(f'Running SALib Sobol sensitivity analysis for N_base={N_BASE} (1000 bootstrap resamples, 95% CI)...')
    si_Tc    = sobol_analyze.analyze(problem, Y_Tc,    calc_second_order=False, num_resamples=1000, conf_level=0.95, seed=42)
    si_M     = sobol_analyze.analyze(problem, Y_M,     calc_second_order=False, num_resamples=1000, conf_level=0.95, seed=42)
    si_theta = sobol_analyze.analyze(problem, Y_theta, calc_second_order=False, num_resamples=1000, conf_level=0.95, seed=42)

    df_main = pd.DataFrame({
        'parameter':         PARAM_NAMES,
        'S1_Tcloud':         np.round(si_Tc['S1'], 4),
        'S1_conf_Tcloud':    np.round(si_Tc['S1_conf'], 4),
        'ST_Tcloud':         np.round(si_Tc['ST'], 4),
        'ST_conf_Tcloud':    np.round(si_Tc['ST_conf'], 4),
        'S1_M_final':        np.round(si_M['S1'], 4),
        'S1_conf_M_final':   np.round(si_M['S1_conf'], 4),
        'ST_M_final':        np.round(si_M['ST'], 4),
        'ST_conf_M_final':   np.round(si_M['ST_conf'], 4),
        'S1_theta':          np.round(si_theta['S1'], 4),
        'S1_conf_theta':     np.round(si_theta['S1_conf'], 4),
        'ST_theta':          np.round(si_theta['ST'], 4),
        'ST_conf_theta':     np.round(si_theta['ST_conf'], 4),
    })
    df_main.to_csv('data/sobol_indices_N1024.csv', index=False)
    print(f'\n=== SALIB SOBOL INDICES (N_base={N_BASE}, D={D}, N_eval={param_values.shape[0]}) ===')
    print(df_main.to_string(index=False))

    print(f'\nComputing rigorous block convergence curves for N in {CONV_BLOCKS} from real evaluations...')
    conv_rows = []
    n_blocks = CONV_BLOCKS
    step = D + 2
    for n in n_blocks:
        n_rows = n * step
        sub_Y_Tc    = Y_Tc[:n_rows]
        sub_Y_M     = Y_M[:n_rows]
        sub_Y_theta = Y_theta[:n_rows]

        sub_si_Tc    = sobol_analyze.analyze(problem, sub_Y_Tc,    calc_second_order=False, num_resamples=500, conf_level=0.95, seed=42)
        sub_si_M     = sobol_analyze.analyze(problem, sub_Y_M,     calc_second_order=False, num_resamples=500, conf_level=0.95, seed=42)
        sub_si_theta = sobol_analyze.analyze(problem, sub_Y_theta, calc_second_order=False, num_resamples=500, conf_level=0.95, seed=42)

        for j, p_name in enumerate(PARAM_NAMES):
            conv_rows.append({
                'N_base':            n,
                'parameter':         p_name,
                'S1_Tcloud':         round(float(sub_si_Tc['S1'][j]), 4),
                'S1_conf_Tcloud':    round(float(sub_si_Tc['S1_conf'][j]), 4),
                'ST_Tcloud':         round(float(sub_si_Tc['ST'][j]), 4),
                'ST_conf_Tcloud':    round(float(sub_si_Tc['ST_conf'][j]), 4),
                'S1_M_final':        round(float(sub_si_M['S1'][j]), 4),
                'S1_conf_M_final':   round(float(sub_si_M['S1_conf'][j]), 4),
                'ST_M_final':        round(float(sub_si_M['ST'][j]), 4),
                'ST_conf_M_final':   round(float(sub_si_M['ST_conf'][j]), 4),
                'S1_theta':          round(float(sub_si_theta['S1'][j]), 4),
                'S1_conf_theta':     round(float(sub_si_theta['S1_conf'][j]), 4),
                'ST_theta':          round(float(sub_si_theta['ST'][j]), 4),
                'ST_conf_theta':     round(float(sub_si_theta['ST_conf'][j]), 4),
            })

    df_conv = pd.DataFrame(conv_rows)
    df_conv.to_csv('data/sobol_convergence_N1024.csv', index=False)
    print('Successfully generated data/sobol_convergence_N1024.csv from actual sub-block analysis.')
    print(f'Total rows in convergence CSV: {len(df_conv)}')

if __name__ == '__main__':
    main()
