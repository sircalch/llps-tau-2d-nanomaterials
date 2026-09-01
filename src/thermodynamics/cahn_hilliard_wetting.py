"""
cahn_hilliard_wetting.py
========================
Fully dimensionalized Cahn-Hilliard interfacial gradient theory and
thermodynamically derived Young's wetting contact angle engine.

Thermodynamic Architecture:
--------------------------
1. Liquid-Liquid Interfacial Tension:
   gamma_LL = integral_[phi_dilute]^[phi_dense] sqrt(2 kappa_grad f_0 Omega_excess(phi)) dphi
   where f_0 = k_B T / v_ref [J / m³] with v_ref = 2.85e-25 m³, and kappa_grad = (1/6) f_0 b_eff² [J / m].
   The resulting gamma_LL has units [J / m² = N / m].

2. Derived Solid-Liquid Surface Energy Excess:
   From the Langmuir surface grand potential:
   Delta_gamma_s = eta_eff * k_B T * Gamma_max * ln((1 + K_deg * a_dense) / (1 + K_deg * a_dilute))
   
3. Young's Equation:
   cos(theta_c) = Delta_gamma_s / gamma_LL  (Strictly dimensionless)
"""

import numpy as np
from scipy.integrate import quad

try:
    from .material_parameters import (
        MATERIAL_TABLE_2,
        TAU_K18_SYSTEM,
        KB_J,
        calculate_surface_energy_excess_SI
    )
    from .flory_huggins_voorn_overbeek import FloryHugginsVoornOverbeek
except ImportError:
    from material_parameters import (
        MATERIAL_TABLE_2,
        TAU_K18_SYSTEM,
        KB_J,
        calculate_surface_energy_excess_SI
    )
    from flory_huggins_voorn_overbeek import FloryHugginsVoornOverbeek


class CahnHilliardWetting:
    """
    Cahn-Hilliard interfacial gradient and Young's wetting engine.
    """

    def __init__(self, fh_model=None, segment_length_b_nm=3.4, lambda_grad=1.0/6.0):
        if fh_model is None:
            fh_model = FloryHugginsVoornOverbeek()
        self.fh = fh_model
        self.v0_m3 = TAU_K18_SYSTEM["reference_volume_m3"]
        self.b_m = float(segment_length_b_nm) * 1e-9
        self.lambda_grad = float(lambda_grad)

    def bulk_energy_scale(self, T_K=310.15):
        """Energy density scale f_0 = k_B T / v_ref [J / m³]."""
        return (KB_J * T_K) / self.v0_m3

    def gradient_energy_coefficient(self, T_K=310.15):
        """Gradient energy coefficient kappa_grad = lambda * f_0 * b² [J / m]."""
        return self.lambda_grad * self.bulk_energy_scale(T_K) * (self.b_m ** 2)

    def grand_potential_excess(self, phi, T_K=310.15, I_M=0.155, phi_d=None, phi_c=None):
        """Dimensionless excess grand potential Omega_excess(phi)."""
        if phi_d is None or phi_c is None:
            phi_d, phi_c = self.fh.find_binodal_coexistence(T_K, I_M)
            if phi_d is None:
                return 0.0
        mu_coex = self.fh.chemical_potential(phi_d, T_K, I_M)
        Pi_coex = self.fh.osmotic_pressure(phi_d, T_K, I_M)
        f_val = self.fh.free_energy_density(phi, T_K, I_M)
        return max(0.0, f_val - mu_coex * phi + Pi_coex)

    def calculate_gamma_LL_SI(self, T_K=310.15, I_M=0.155):
        """
        Calculates liquid-liquid surface tension gamma_LL in SI units [J / m² = N / m].
        """
        phi_d, phi_c = self.fh.find_binodal_coexistence(T_K, I_M)
        if phi_d is None:
            return 0.0

        kappa_si = self.gradient_energy_coefficient(T_K)
        energy_scale = self.bulk_energy_scale(T_K)

        def integrand(p):
            omega_ex = self.grand_potential_excess(p, T_K, I_M, phi_d, phi_c)
            return np.sqrt(max(0.0, 2.0 * kappa_si * energy_scale * omega_ex))

        res, _ = quad(integrand, phi_d + 1e-6, phi_c - 1e-6, limit=80, epsabs=1e-12, epsrel=1e-8)
        return float(res)

    def calculate_gamma_LL_uNm(self, T_K=310.15, I_M=0.155):
        """Liquid-liquid surface tension in [uN / m] (condensate scale)."""
        return self.calculate_gamma_LL_SI(T_K, I_M) * 1e6

    def compute_contact_angle(self, T_K=310.15, I_M=0.155, material="borophene", eta_eff=0.20e-3):
        """
        Computes contact angle theta_c from Young's equation:
        cos(theta_c) = Delta_gamma_s / gamma_LL
        """
        phi_d, phi_c = self.fh.find_binodal_coexistence(T_K, I_M)
        if phi_d is None:
            return 90.0, "no_phase_separation", 0.0, 0.0

        gamma_LL_si = self.calculate_gamma_LL_SI(T_K, I_M)
        if gamma_LL_si < 1e-20:
            return 90.0, "undefined", 0.0, 0.0

        if material not in MATERIAL_TABLE_2 or material == "control":
            return 90.0, "control_no_interface", 0.0, float(gamma_LL_si * 1e6)

        # Derived surface energy excess in SI [J / m²]
        delta_gamma_s = calculate_surface_energy_excess_SI(T_K, phi_d, phi_c, material, eta_eff)

        # Derived Young expression
        cos_theta = delta_gamma_s / gamma_LL_si
        cos_theta_clamped = np.clip(cos_theta, -1.0, 1.0)
        theta_deg = float(np.degrees(np.arccos(cos_theta_clamped)))

        if theta_deg < 5.0:
            regime = "complete_wetting"
        elif theta_deg > 120.0:
            regime = "dewetting"
        else:
            regime = "partial_wetting"

        return theta_deg, regime, float(cos_theta_clamped), float(gamma_LL_si * 1e6)
