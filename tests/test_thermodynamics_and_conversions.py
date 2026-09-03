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
    """Verify that Sobol global sensitivity analysis CSV datasets exist and satisfy mathematical bounds."""
    sobol_path = os.path.join(os.path.dirname(__file__), "../data/sobol_indices_N512.csv")
    assert os.path.exists(sobol_path), f"Sobol indices CSV not found at {sobol_path}"
    df_sobol = pd.read_csv(sobol_path)
    assert len(df_sobol) == 8, "Expected 8 parameters in Sobol index table"
    expected_cols = {"parameter", "S1_Tcloud", "ST_Tcloud", "S1_M_final", "ST_M_final"}
    assert expected_cols.issubset(df_sobol.columns)

    # Check bounds [0, 1]
    for col in ["S1_Tcloud", "ST_Tcloud", "S1_M_final", "ST_M_final"]:
        assert (df_sobol[col] >= 0.0).all() and (df_sobol[col] <= 1.0).all()

    # Total variance explained in first-order indices must be positive and <= 1.0
    assert 0.40 <= df_sobol["S1_Tcloud"].sum() <= 1.0
    assert 0.40 <= df_sobol["S1_M_final"].sum() <= 1.0

    # Verify convergence table
    conv_path = os.path.join(os.path.dirname(__file__), "../data/sobol_convergence_N512.csv")
    assert os.path.exists(conv_path), f"Sobol convergence CSV not found at {conv_path}"
    df_conv = pd.read_csv(conv_path)
    assert set(df_conv["N_base"].unique()) == {64, 128, 256, 512}


if __name__ == "__main__":
    test_dimensional_capacity_conversion()
    test_standard_thermodynamic_activity_and_coverage()
    test_apparent_cloud_point_brent_root_solver()
    test_material_dissolution_and_depletion_thresholds()
    test_exact_young_wetting_identity_and_closure()
    test_thermodynamic_parameter_sensitivities()
    test_digitized_experimental_data_integrity()
    test_kinetic_mass_conservation()
    test_sobol_indices_dataset_integrity()
    print("All comprehensive unit tests passed successfully!")


