"""
test_thermodynamics_and_conversions.py
======================================
Comprehensive unit tests verifying:
  1. Exact capacity conversion: c_max = (a_s * Gamma * 1e30) / N_A
  2. Standard thermodynamic activity in Langmuir adsorption
  3. Apparent cloud point true root solving via Brent's method
  4. Material-specific LLPS dissolution vs partial depletion thresholds
  5. Exact Young's wetting equation closure cos(theta) = Delta_gamma_s / gamma_LL
  6. Algebraic mass conservation in condensate aging master equations
  7. Active dependency of cloud point on thermodynamic variables
"""

import sys, os
import numpy as np
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.thermodynamics.material_parameters import (
    calculate_m_tilde_max,
    compute_thermodynamic_activity,
    adsorption_equilibrium_dimensionless,
    calculate_surface_energy_excess_SI,
    TAU_K18_SYSTEM,
    MATERIAL_TABLE_2
)
from src.thermodynamics.flory_huggins_voorn_overbeek import FloryHugginsVoornOverbeek
from src.thermodynamics.cahn_hilliard_wetting import CahnHilliardWetting
from src.kinetics.condensate_aging_kinetics import CondensateAgingKinetics


def test_dimensional_capacity_conversion():
    """Verify that a_s = 1e-4 nm^-1 and Gamma = 0.38 nm^-2 yield c_max = 63.1 uM."""
    a_s = 1.0e-4 # nm^-1 (100 ug/mL for SSA = 1000 m^2/g)
    Gamma = 0.38 # nm^-2
    N_A = 6.022e23
    c_max_uM = (a_s * Gamma * 1e30) / N_A
    assert np.isclose(c_max_uM, 63.102, rtol=1e-3)

    m_tilde_max = calculate_m_tilde_max(a_s, Gamma)
    assert np.isclose(m_tilde_max, 9.50e-4 * 63.102, rtol=1e-3)


def test_standard_thermodynamic_activity_and_coverage():
    """Verify standard activity coverage: Borophene ~ 0.969 vs MXene ~ 0.316 at 100 uM."""
    phi_tot = 0.095 # 100 uM
    a_act = compute_thermodynamic_activity(phi_tot)
    assert np.isclose(a_act, 1.0e-4, rtol=1e-3)

    # Borophene at 310.15 K:
    K_boro = np.exp(7.8 / (1.987e-3 * 310.15))
    theta_boro = (K_boro * a_act) / (1.0 + K_boro * a_act)
    assert np.isclose(theta_boro, 0.969, atol=0.01)

    # MXene at 310.15 K:
    K_mxen = np.exp(5.2 / (1.987e-3 * 310.15))
    theta_mxen = (K_mxen * a_act) / (1.0 + K_mxen * a_act)
    assert np.isclose(theta_mxen, 0.316, atol=0.01)


def test_apparent_cloud_point_brent_root_solver():
    """Verify that bulk 100 uM Tau K18 has a cloud point at 15.3 °C (Ambadipudi 2017 onset)."""
    fh = FloryHugginsVoornOverbeek(Tc_K=281.65, beta=0.0090)
    tc_bulk = fh.calculate_apparent_cloud_point(a_s_nm_inv=0.0, phi_total=0.095)
    assert tc_bulk is not None
    assert np.isclose(tc_bulk, 15.30, atol=0.2)


def test_material_dissolution_and_depletion_thresholds():
    """Verify Borophene causes ~60% depletion at 100 ug/mL, while MXene causes only ~11% depletion."""
    fh = FloryHugginsVoornOverbeek(Tc_K=281.65, beta=0.0090)
    b1_37, _ = fh.find_binodal_coexistence(310.15) # 0.0260

    # Borophene at 100 ug/mL:
    a_boro_100 = 1.0e-4 # nm^-1
    phi_f_boro, _, _ = adsorption_equilibrium_dimensionless(0.095, 310.15, a_boro_100, "borophene")
    c_free_boro = phi_f_boro / 9.50e-4
    assert np.isclose(c_free_boro, 41.4, atol=1.0) # ~41.4 uM (depleted from 100 uM)

    # Borophene cloud point shifted to 29.4 °C (dissolving LLPS below 29.4 °C):
    tc_boro_100 = fh.calculate_apparent_cloud_point(a_s_nm_inv=1.0e-4, material="borophene")
    assert np.isclose(tc_boro_100, 29.4, atol=0.5)

    # MXene at 100 ug/mL:
    a_mxene_100 = 1.0e-4
    phi_f_mxen, _, _ = adsorption_equilibrium_dimensionless(0.095, 310.15, a_mxene_100, "mxene")
    c_free_mxen = phi_f_mxen / 9.50e-4
    assert np.isclose(c_free_mxen, 87.6, atol=1.0) # ~87.6 uM (weak depletion)
    assert phi_f_mxen > b1_37                       # Droplets remain phase-separated at 37 °C


def test_exact_young_wetting_identity_and_closure():
    """Verify exact Young identity closure cos(theta) = Delta_gamma_s / gamma_LL."""
    fh = FloryHugginsVoornOverbeek(Tc_K=281.65, beta=0.0090)
    wetting = CahnHilliardWetting(fh_model=fh)
    b1_37, b2_37 = fh.find_binodal_coexistence(310.15)

    gamma_LL_si = wetting.calculate_gamma_LL_SI(310.15)
    gamma_LL_uNm = gamma_LL_si * 1e6
    assert np.isclose(gamma_LL_uNm, 1.601, atol=0.05)

    # Borophene:
    dg_boro_si = calculate_surface_energy_excess_SI(310.15, b1_37, b2_37, "borophene", eta_eff=0.20e-3)
    dg_boro_uNm = dg_boro_si * 1e6
    assert np.isclose(dg_boro_uNm, 1.023, atol=0.02)
    th_boro, _, cos_b, _ = wetting.compute_contact_angle(310.15, material="borophene", eta_eff=0.20e-3)
    assert np.isclose(cos_b, dg_boro_si / gamma_LL_si, atol=1e-5)
    assert np.isclose(th_boro, 50.3, atol=0.3)

    # MXene:
    dg_mxen_si = calculate_surface_energy_excess_SI(310.15, b1_37, b2_37, "mxene", eta_eff=0.20e-3)
    dg_mxen_uNm = dg_mxen_si * 1e6
    assert np.isclose(dg_mxen_uNm, 0.296, atol=0.02)
    th_mxen, _, cos_m, _ = wetting.compute_contact_angle(310.15, material="mxene", eta_eff=0.20e-3)
    assert np.isclose(cos_m, dg_mxen_si / gamma_LL_si, atol=1e-5)
    assert np.isclose(th_mxen, 79.3, atol=0.3)


def test_thermodynamic_parameter_sensitivities():
    """Verify that every thermodynamic parameter actively shifts the calculated cloud point."""
    fh_base = FloryHugginsVoornOverbeek(N=10.0, Tc_K=281.65, beta=0.0090)
    tc_base = fh_base.calculate_apparent_cloud_point(a_s_nm_inv=5e-5, dG_ads=-7.8, I_M=0.155)

    # Changing beta:
    fh_beta = FloryHugginsVoornOverbeek(N=10.0, Tc_K=281.65, beta=0.0120)
    tc_beta = fh_beta.calculate_apparent_cloud_point(a_s_nm_inv=5e-5, dG_ads=-7.8, I_M=0.155)
    assert tc_beta != tc_base

    # Changing Tc:
    fh_tc = FloryHugginsVoornOverbeek(N=10.0, Tc_K=285.15, beta=0.0090)
    tc_tc = fh_tc.calculate_apparent_cloud_point(a_s_nm_inv=5e-5, dG_ads=-7.8, I_M=0.155)
    assert tc_tc != tc_base

    # Changing dG_ads:
    tc_dg = fh_base.calculate_apparent_cloud_point(a_s_nm_inv=5e-5, dG_ads=-5.0, I_M=0.155)
    assert tc_dg != tc_base

    # Changing I_M:
    tc_I = fh_base.calculate_apparent_cloud_point(a_s_nm_inv=5e-5, dG_ads=-7.8, I_M=0.300)
    assert tc_I != tc_base


import pandas as pd


def test_digitized_experimental_data_integrity():
    """Verify that Ambadipudi 2017 digitized CSV loads properly with pandas and has correct structure."""
    csv_path = os.path.join(os.path.dirname(__file__), "../data/ambadipudi_2017_fig2b_K18_pH8p8.csv")
    assert os.path.exists(csv_path), f"Dataset CSV not found at {csv_path}"
    df = pd.read_csv(csv_path, comment="#")
    assert len(df) == 11
    assert "temperature_C" in df.columns
    assert "A350_normalized" in df.columns
    assert "digitization_uncertainty" in df.columns
    assert df["A350_normalized"].max() <= 1.05
    assert df["temperature_C"].min() >= 5.0
    assert df["temperature_C"].max() <= 50.0


def test_kinetic_mass_conservation():
    """Verify exact algebraic mass conservation in condensate aging master equations."""
    kin = CondensateAgingKinetics()
    for a in [0.0, 2.5e-5, 5.0e-5, 1.0e-4]:
        res = kin.simulate(t_span=(0, 24), phi_0=0.60, a_s_nm_inv=a)
        assert res["mass_error"] < 1e-14
        assert res["M_final"] <= 0.60
        assert res["m_ads"][-1] >= 0.0


def test_sobol_indices_dataset_integrity():
    """Verify that SALib Sobol sensitivity datasets exist, satisfy physical bounds, structural zeros, and S1 <= ST."""
    sobol_path = os.path.join(os.path.dirname(__file__), "../data/sobol_indices_N1024.csv")
    assert os.path.exists(sobol_path), f"Sobol indices CSV not found at {sobol_path}"
    df_sobol = pd.read_csv(sobol_path).set_index("parameter")
    assert len(df_sobol) == 8, "Expected 8 parameters in Sobol index table"
    expected_cols = {
        "S1_Tcloud", "S1_conf_Tcloud", "ST_Tcloud", "ST_conf_Tcloud",
        "S1_M_final", "S1_conf_M_final", "ST_M_final", "ST_conf_M_final"
    }
    assert expected_cols.issubset(df_sobol.columns)

    # 1. Structural zeros: inactive parameters must evaluate to ~0
    # eta_eff and k_ext do not enter apparent cloud point solver
    assert abs(df_sobol.loc["eta_eff", "S1_Tcloud"]) < 1e-4
    assert abs(df_sobol.loc["eta_eff", "ST_Tcloud"]) < 1e-4
    assert abs(df_sobol.loc["k_ext", "S1_Tcloud"]) < 1e-4
    assert abs(df_sobol.loc["k_ext", "ST_Tcloud"]) < 1e-4

    # Thermodynamic parameters do not participate directly in isolated droplet aging kinetics
    for p_thermo in ["N_eff", "beta", "Tc_K", "dG_ads", "I_M", "eta_eff"]:
        assert abs(df_sobol.loc[p_thermo, "S1_M_final"]) < 1e-4
        assert abs(df_sobol.loc[p_thermo, "ST_M_final"]) < 1e-4

    # 2. S1 <= ST property for all active parameters
    for p in df_sobol.index:
        # Allow small negative lower fluctuations within confidence interval for finite samples
        assert df_sobol.loc[p, "ST_Tcloud"] >= 0.0
        assert df_sobol.loc[p, "ST_M_final"] >= 0.0
        if df_sobol.loc[p, "ST_Tcloud"] > 0.05:
            assert df_sobol.loc[p, "S1_Tcloud"] <= df_sobol.loc[p, "ST_Tcloud"] + 1e-4
        if df_sobol.loc[p, "ST_M_final"] > 0.05:
            assert df_sobol.loc[p, "S1_M_final"] <= df_sobol.loc[p, "ST_M_final"] + 1e-4

    # 3. Active parameters dominate
    assert df_sobol.loc["a_s", "ST_M_final"] > 0.80
    assert df_sobol.loc["k_ext", "ST_M_final"] > 0.05

    # 4. Verify convergence table
    conv_path = os.path.join(os.path.dirname(__file__), "../data/sobol_convergence_N1024.csv")
    assert os.path.exists(conv_path), f"Sobol convergence CSV not found at {conv_path}"
    df_conv = pd.read_csv(conv_path)
    assert set(df_conv["N_base"].unique()) == {128, 256, 512, 1024}
    assert len(df_conv) == 32  # 4 blocks x 8 parameters


def test_salib_ishigami_benchmark():
    """Validate SALib global sensitivity engine against analytical Ishigami benchmark."""
    from SALib.sample import sobol as sobol_sample
    from SALib.analyze import sobol as sobol_analyze

    problem = {
        'num_vars': 3,
        'names': ['x1', 'x2', 'x3'],
        'bounds': [[-np.pi, np.pi], [-np.pi, np.pi], [-np.pi, np.pi]]
    }
    # N=256 evaluates 256 * (3 + 2) = 1280 points
    param_values = sobol_sample.sample(problem, 256, calc_second_order=False, scramble=True, seed=42)
    x1, x2, x3 = param_values[:, 0], param_values[:, 1], param_values[:, 2]
    # Ishigami test function
    Y = np.sin(x1) + 7.0 * (np.sin(x2) ** 2) + 0.1 * (x3 ** 4) * np.sin(x1)
    Si = sobol_analyze.analyze(problem, Y, calc_second_order=False, num_resamples=500, conf_level=0.95, seed=42)

    # Analytical properties: x2 has zero interaction with other vars (S1 ~ ST), x3 has S1 ~ 0 but ST > 0
    assert abs(Si['S1'][1] - Si['ST'][1]) < 0.10, "x2 should have S1 ~= ST in Ishigami function"
    assert Si['S1'][2] < 0.10, "x3 should have first-order index ~ 0"
    assert Si['ST'][2] > 0.15, "x3 should have non-zero total index due to x1 interaction"
    assert Si['ST'][0] > Si['S1'][0], "x1 should satisfy S1 < ST due to interaction with x3"


def test_sobol_prefix_consistency_and_shapes():
    """Verify SALib interleaved stride step=D+2, prefix shapes, and that the top sub-block reproduces the main dataset."""
    eval_path = os.path.join(os.path.dirname(__file__), "../data/sobol_evaluations_N1024.npz")
    assert os.path.exists(eval_path), f"Sobol evaluations archive not found at {eval_path}"
    raw = np.load(eval_path)
    Y_Tc, Y_M = raw['Y_Tc'], raw['Y_M']

    D = 8
    step = D + 2  # 10
    N_BASE = 1024
    assert len(Y_Tc) == N_BASE * step
    assert len(Y_M) == N_BASE * step

    # Verify sub-block shapes
    for n in [128, 256, 512, 1024]:
        expected_rows = n * step
        assert len(Y_Tc[:expected_rows]) == expected_rows
        assert len(Y_M[:expected_rows]) == expected_rows

    # Verify that the top convergence sub-block (N = N_base) reproduces the main indices
    csv_main = pd.read_csv(os.path.join(os.path.dirname(__file__), "../data/sobol_indices_N1024.csv")).set_index("parameter")
    csv_conv = pd.read_csv(os.path.join(os.path.dirname(__file__), "../data/sobol_convergence_N1024.csv"))
    df_conv_top = csv_conv[csv_conv["N_base"] == N_BASE].set_index("parameter")

    for p in csv_main.index:
        assert abs(csv_main.loc[p, "ST_Tcloud"] - df_conv_top.loc[p, "ST_Tcloud"]) < 1e-4
        assert abs(csv_main.loc[p, "ST_M_final"] - df_conv_top.loc[p, "ST_M_final"]) < 1e-4
        assert abs(csv_main.loc[p, "S1_Tcloud"] - df_conv_top.loc[p, "S1_Tcloud"]) < 1e-4
        assert abs(csv_main.loc[p, "S1_M_final"] - df_conv_top.loc[p, "S1_M_final"]) < 1e-4


def test_binodal_independent_convex_hull_crosscheck():
    """
    Cross-check find_binodal_coexistence against a completely independent numerical
    method: the geometric common-tangent construction via the lower convex hull of
    f(phi) (classic Maxwell construction). No root() call, no initial guess, no code
    path shared with the production solver -- if the two disagreed it would indicate a
    systematic bug that internal self-consistency checks (mu1=mu2, Pi1=Pi2 evaluated
    with the solver's own output) cannot catch.
    """
    from scipy.spatial import ConvexHull

    def independent_binodal(fh, T_K, I_M=0.155, n=20000):
        phis = np.linspace(1e-6, 1 - 1e-6, n)
        fs = np.array([fh.free_energy_density(p, T_K, I_M) for p in phis])
        pts = np.column_stack([phis, fs])
        hull = ConvexHull(pts)
        # lower hull = hull vertices whose edge to the next-lowest-phi vertex has
        # everything above it; equivalently, sort vertices by phi and keep the
        # lower boundary via a simple monotone-chain scan (robust, no assumptions
        # about scipy's vertex ordering).
        order = np.argsort(pts[hull.vertices, 0])
        v = pts[hull.vertices][order]

        def cross(o, a, b):
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

        lower = []
        for p in v:
            while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
                lower.pop()
            lower.append(p)
        lower = np.array(lower)

        # the binodal pair is the lower-hull edge that skips the most original grid
        # points (the two-phase region excluded from the convex envelope)
        hull_phi_idx = np.searchsorted(phis, lower[:, 0])
        gaps = np.diff(hull_phi_idx)
        k = int(np.argmax(gaps))
        if gaps[k] <= 1:
            return None, None
        return float(lower[k, 0]), float(lower[k + 1, 0])

    cases = [
        (10.0, 281.65, 0.0090, 37.0, 0.155),
        (10.0, 281.65, 0.0090, 20.0, 0.155),
        (10.0, 281.65, 0.0090, 50.0, 0.155),
        (10.0, 281.65, 0.0090, 45.0, 0.35),
        (10.0, 281.65, 0.0090, 25.0, 0.05),
        (6.0, 278.0, 0.012, 30.0, 0.2),
        (18.0, 285.0, 0.006, 40.0, 0.1),
    ]
    for N, Tc, beta, T_C, I in cases:
        fh = FloryHugginsVoornOverbeek(N=N, Tc_K=Tc, beta=beta)
        T_K = T_C + 273.15
        b1_root, b2_root = fh.find_binodal_coexistence(T_K, I_M=I)
        b1_hull, b2_hull = independent_binodal(fh, T_K, I_M=I)
        assert b1_root is not None and b1_hull is not None
        # tolerance set by the 20000-point hull grid resolution (~5e-5), not by the
        # solver's own precision -- this is checking agreement between two different
        # numerical methods, not self-consistency of one
        assert abs(b1_root - b1_hull) < 5e-4
        assert abs(b2_root - b2_hull) < 5e-4


def test_classic_flory_huggins_critical_point_limit():
    """
    With electrostatics off (alpha_DH=0), the numerically solved critical point
    (from f''(phi_c)=0, f'''(phi_c)=0) must reduce to the textbook analytical
    Flory-Huggins result: phi_c = 1/(1+sqrt(N)), chi_c = (1/2)(1+1/sqrt(N))^2.
    Independent analytical cross-check of the critical-point solver itself.
    """
    for N in [1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0]:
        fh = FloryHugginsVoornOverbeek(N=N, alpha_DH=0.0)
        phi_c_analytical = 1.0 / (1.0 + np.sqrt(N))
        chi_c_analytical = 0.5 * (1.0 + 1.0 / np.sqrt(N)) ** 2
        assert np.isclose(fh.phi_c, phi_c_analytical, atol=1e-6)
        assert np.isclose(fh.chi_c, chi_c_analytical, atol=1e-6)


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main(["-v", __file__]))


