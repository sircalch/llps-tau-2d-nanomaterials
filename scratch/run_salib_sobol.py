import sys, os, time
sys.path.insert(0, '.')
import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
from SALib.sample import sobol as sobol_sample
from SALib.analyze import sobol as sobol_analyze
from src.thermodynamics.flory_huggins_voorn_overbeek import FloryHugginsVoornOverbeek
from src.kinetics.condensate_aging_kinetics import CondensateAgingKinetics

PARAM_NAMES = ['N_eff', 'beta', 'Tc_K', 'dG_ads', 'a_s', 'I_M', 'eta_eff', 'k_ext']
D = len(PARAM_NAMES)
N_BASE = 512

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
    tc = fh.calculate_apparent_cloud_point(a_s_nm_inv=asv, dG_ads=dGv, I_M=Iv, Gamma_max=0.38)
    tc_val = tc if tc is not None else 65.0
    kin = CondensateAgingKinetics(k_extract=kv)
    res = kin.simulate(t_span=(0, 24), phi_0=0.60, a_s_nm_inv=asv)
    return tc_val, res['M_final']

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

    Y_Tc = np.array([r[0] for r in results])
    Y_M  = np.array([r[1] for r in results])

    os.makedirs('data', exist_ok=True)
    np.savez_compressed('data/sobol_evaluations_N512.npz', param_values=param_values, Y_Tc=Y_Tc, Y_M=Y_M)
    print('Saved raw evaluations to data/sobol_evaluations_N512.npz')

    print('Running SALib Sobol sensitivity analysis for N_base=512 (1000 bootstrap resamples, 95% CI)...')
    si_Tc = sobol_analyze.analyze(problem, Y_Tc, calc_second_order=False, num_resamples=1000, conf_level=0.95, seed=42)
    si_M  = sobol_analyze.analyze(problem, Y_M,  calc_second_order=False, num_resamples=1000, conf_level=0.95, seed=42)

    df_main = pd.DataFrame({
        'parameter':       PARAM_NAMES,
        'S1_Tcloud':       np.round(si_Tc['S1'], 4),
        'S1_conf_Tcloud':  np.round(si_Tc['S1_conf'], 4),
        'ST_Tcloud':       np.round(si_Tc['ST'], 4),
        'ST_conf_Tcloud':  np.round(si_Tc['ST_conf'], 4),
        'S1_M_final':      np.round(si_M['S1'], 4),
        'S1_conf_M_final': np.round(si_M['S1_conf'], 4),
        'ST_M_final':      np.round(si_M['ST'], 4),
        'ST_conf_M_final': np.round(si_M['ST_conf'], 4),
    })
    df_main.to_csv('data/sobol_indices_N512.csv', index=False)
    print('\n=== SALIB SOBOL INDICES (N_base=512, D=8, N_eval=5120) ===')
    print(df_main.to_string(index=False))

    print('\nComputing rigorous block convergence curves for N in [64, 128, 256, 512] from real evaluations...')
    conv_rows = []
    n_blocks = [64, 128, 256, 512]
    step = D + 2
    for n in n_blocks:
        n_rows = n * step
        sub_Y_Tc = Y_Tc[:n_rows]
        sub_Y_M  = Y_M[:n_rows]

        sub_si_Tc = sobol_analyze.analyze(problem, sub_Y_Tc, calc_second_order=False, num_resamples=500, conf_level=0.95, seed=42)
        sub_si_M  = sobol_analyze.analyze(problem, sub_Y_M,  calc_second_order=False, num_resamples=500, conf_level=0.95, seed=42)

        for j, p_name in enumerate(PARAM_NAMES):
            conv_rows.append({
                'N_base':           n,
                'parameter':         p_name,
                'S1_Tcloud':         round(float(sub_si_Tc['S1'][j]), 4),
                'S1_conf_Tcloud':    round(float(sub_si_Tc['S1_conf'][j]), 4),
                'ST_Tcloud':         round(float(sub_si_Tc['ST'][j]), 4),
                'ST_conf_Tcloud':    round(float(sub_si_Tc['ST_conf'][j]), 4),
                'S1_M_final':        round(float(sub_si_M['S1'][j]), 4),
                'S1_conf_M_final':   round(float(sub_si_M['S1_conf'][j]), 4),
                'ST_M_final':        round(float(sub_si_M['ST'][j]), 4),
                'ST_conf_M_final':   round(float(sub_si_M['ST_conf'][j]), 4),
            })

    df_conv = pd.DataFrame(conv_rows)
    df_conv.to_csv('data/sobol_convergence_N512.csv', index=False)
    print('Successfully generated data/sobol_convergence_N512.csv from actual sub-block analysis.')
    print(f'Total rows in convergence CSV: {len(df_conv)}')

if __name__ == '__main__':
    main()
