"""
Seed-robustness check for the canonical Sobol GSA (not part of run_pipeline.py;
kept as a documented validation artifact, run on demand). Re-runs the exact same
N_base=1024 design with seed=123 and compares against the archived seed=42
results in data/sobol_indices_N1024.csv, to confirm the reported T_cloud/M_final
conclusions are not an artifact of the declared seed.

Result at the time this was last run (see git history for the full comparison
table): identical parameter-importance ranking for T_cloud^app under both
seeds, all total-effect indices agreeing within the already-reported bootstrap
CIs (max difference 0.023). Predates the theta_c GSA output added later to
run_salib_sobol.py; extend eval_single here the same way if re-checking theta_c
seed-robustness is ever wanted.
"""
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
N_BASE = 1024
SEED = 123  # canonical run used seed=42

BOUNDS = [
    [6.0, 18.0], [0.005, 0.015], [275.15, 287.15],
    [-10.0, -3.0], [5.0e-6, 1.0e-4], [0.05, 0.35],
    [0.10e-3, 0.35e-3], [0.20, 2.50]
]
problem = {'num_vars': D, 'names': PARAM_NAMES, 'bounds': BOUNDS}

def eval_single(row):
    Nv, bv, Tv, dGv, asv, Iv, etv, kv = row
    fh = FloryHugginsVoornOverbeek(N=Nv, Tc_K=Tv, beta=bv)
    tc = fh.calculate_apparent_cloud_point(a_s_nm_inv=asv, dG_ads=dGv, I_M=Iv, Gamma_max=0.38)
    kin = CondensateAgingKinetics(k_extract=kv)
    res = kin.simulate(t_span=(0, 24), phi_0=0.60, a_s_nm_inv=asv)
    return float(tc), res['M_final']

def main():
    print(f'Sampling with seed={SEED} (canonical run used seed=42)...')
    param_values = sobol_sample.sample(problem, N_BASE, calc_second_order=False, scramble=True, seed=SEED)
    t0 = time.time()
    workers = min(12, os.cpu_count() or 4)
    with ProcessPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(eval_single, param_values, chunksize=32))
    print(f'{len(results)} evals in {time.time()-t0:.1f}s')

    Y_Tc = np.array([r[0] for r in results])
    Y_M = np.array([r[1] for r in results])
    si_Tc = sobol_analyze.analyze(problem, Y_Tc, calc_second_order=False, num_resamples=1000, conf_level=0.95, seed=SEED)
    si_M = sobol_analyze.analyze(problem, Y_M, calc_second_order=False, num_resamples=1000, conf_level=0.95, seed=SEED)

    df_new = pd.DataFrame({
        'parameter': PARAM_NAMES,
        'S1_Tcloud': np.round(si_Tc['S1'], 4), 'ST_Tcloud': np.round(si_Tc['ST'], 4),
        'S1_M_final': np.round(si_M['S1'], 4), 'ST_M_final': np.round(si_M['ST'], 4),
    }).set_index('parameter')

    df_canonical = pd.read_csv('data/sobol_indices_N1024.csv').set_index('parameter')

    print('\n=== seed=123 (this run) vs seed=42 (canonical, archived) ===')
    cmp = pd.DataFrame({
        'ST_Tcloud_seed42': df_canonical['ST_Tcloud'],
        'ST_Tcloud_seed123': df_new['ST_Tcloud'],
        'diff_Tcloud': (df_new['ST_Tcloud'] - df_canonical['ST_Tcloud']).round(4),
        'ST_Mfinal_seed42': df_canonical['ST_M_final'],
        'ST_Mfinal_seed123': df_new['ST_M_final'],
        'diff_Mfinal': (df_new['ST_M_final'] - df_canonical['ST_M_final']).round(4),
    })
    print(cmp.to_string())
    print(f'\nmax |diff| T_cloud ST: {cmp["diff_Tcloud"].abs().max():.4f}')
    print(f'max |diff| M_final ST: {cmp["diff_Mfinal"].abs().max():.4f}')

    # ranking stability check
    rank42 = df_canonical['ST_Tcloud'].rank(ascending=False)
    rank123 = df_new['ST_Tcloud'].rank(ascending=False)
    print('\nT_cloud ST ranking, seed42:', rank42.sort_values().index.tolist())
    print('T_cloud ST ranking, seed123:', rank123.sort_values().index.tolist())

if __name__ == '__main__':
    main()
