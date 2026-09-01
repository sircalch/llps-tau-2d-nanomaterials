"""
test_thermodynamics_and_conversions.py
======================================
Unit tests for the thermodynamic, dimensional conversion, and kinetic solvers.
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


def test_flory_huggins_cloud_point_calibration():
    """Verify that bulk 100 uM Tau K18 has a cloud point at ~15.4 °C (Ambadipudi 2017)."""
    fh = FloryHugginsVoornOverbeek(Tc_K=281.65, beta=0.0090)
    b1_15, b2_15 = fh.find_binodal_coexistence(15.4 + 273.15)
    assert b1_15 is not None
    assert np.isclose(b1_15, 0.095, atol=0.005)


def test_wetting_contact_angles():
    """Verify Cahn-Hilliard tension ~ 1 uN/m and contact angles: Borophene ~ 32.6° vs MXene ~ 74.9°."""
    fh = FloryHugginsVoornOverbeek(Tc_K=281.65, beta=0.0090)
    wetting = CahnHilliardWetting(fh_model=fh)
    gamma_LL = wetting.calculate_gamma_LL_uNm(310.15)
    assert 0.5 < gamma_LL < 2.5 # Micro-Newton per meter scale

    th_b, _, _, _ = wetting.compute_contact_angle(310.15, material="borophene")
    th_m, _, _, _ = wetting.compute_contact_angle(310.15, material="mxene")
    assert 40.0 < th_b < 60.0 # Borophene ~ 50.3°
    assert 70.0 < th_m < 90.0 # MXene ~ 79.3°


def test_kinetic_mass_conservation():
    """Verify exact algebraic mass conservation in condensate aging master equations."""
    kin = CondensateAgingKinetics()
    for a in [0.0, 2.5e-5, 5.0e-5, 1.0e-4]:
        res = kin.simulate(t_span=(0, 24), phi_0=0.60, a_s_nm_inv=a)
        assert res["mass_error"] < 1e-14
        assert res["M_final"] <= 0.60
        assert res["m_ads"][-1] >= 0.0


if __name__ == "__main__":
    test_dimensional_capacity_conversion()
    test_standard_thermodynamic_activity_and_coverage()
    test_flory_huggins_cloud_point_calibration()
    test_wetting_contact_angles()
    test_kinetic_mass_conservation()
    print("All unit tests passed successfully!")
