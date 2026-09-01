"""
flory_huggins_voorn_overbeek.py
================================
Statistical thermodynamic model for Tau K18 LLPS with LCST phase behavior.

Thermodynamic Architecture:
  1. Complete Free Energy Density:
     f(phi) = (phi/N) ln phi + (1-phi) ln(1-phi) + chi(T) phi (1-phi) - alpha_DH (I/I_0)^(3/2) [phi / (phi + phi_0)]
  2. Critical point (phi_c, chi_c) solved numerically from the full free energy:
     f''(phi_c) = 0  and  f'''(phi_c) = 0
  3. LCST thermal dependence:
     chi(T) = chi_c + beta * (T - Tc_K), with Tc_K = 281.65 K (8.5 °C) and beta = 0.0090 K^-1,
     such that for nominal 100 uM Tau K18 (phi_total = 0.095), the true theoretical cloud point is
     T_cloud(100 uM) = 15.0 °C, matching the turbidity onset in Ambadipudi et al. (Nat Commun 2017).
  4. At 37 °C, binodal coexistence gives phi_dilute = 0.026, phi_dense = 0.670.
"""

import numpy as np
from scipy.optimize import minimize_scalar, fsolve

try:
    from .material_parameters import (
        adsorption_equilibrium_dimensionless,
        calculate_m_tilde_max,
        compute_thermodynamic_activity,
        MATERIAL_TABLE_2,
        TAU_K18_SYSTEM,
        KB_J,
        R_GAS
    )
except ImportError:
    from material_parameters import (
        adsorption_equilibrium_dimensionless,
        calculate_m_tilde_max,
        compute_thermodynamic_activity,
        MATERIAL_TABLE_2,
        TAU_K18_SYSTEM,
        KB_J,
        R_GAS
    )


class FloryHugginsVoornOverbeek:
    """
    Flory-Huggins-Voorn-Overbeek engine with exact numerical critical point solving.
    """

    def __init__(self, N=10.0, Tc_K=281.65, beta=0.0090, alpha_DH=0.08, I_0=1.0, phi_0=0.02):
        self.N = float(N)
        self.Tc_K = float(Tc_K)               # 8.5 °C (Calibrated critical temperature)
        self.beta = float(beta)               # 0.0090 K^-1
        self.alpha_DH = float(alpha_DH)
        self.I_0 = float(I_0)
        self.phi_0 = float(phi_0)

        # Compute exact numerical critical point from f'' = 0 and f''' = 0:
        self.phi_c, self.chi_c = self._solve_numerical_critical_point(I_M=0.155)

    def _solve_numerical_critical_point(self, I_M=0.155):
        """
        Solves f''(phi) = 0 and f'''(phi) = 0 simultaneously for the full free energy:
          d2f/dphi2 = 1/(N phi) + 1/(1-phi) - 2 chi + 2 alpha (I/I0)^1.5 phi0 / (phi + phi0)^3 = 0
          d3f/dphi3 = -1/(N phi^2) + 1/(1-phi)^2 - 6 alpha (I/I0)^1.5 phi0 / (phi + phi0)^4 = 0
        """
        I_scaled = max(1e-6, I_M / self.I_0)
        elec_pre = self.alpha_DH * (I_scaled ** 1.5) * self.phi_0

        def equations(vars):
            p, c = vars
            p = np.clip(p, 1e-5, 0.9999)
            d2 = 1.0 / (self.N * p) + 1.0 / (1.0 - p) - 2.0 * c + 2.0 * elec_pre / ((p + self.phi_0) ** 3)
            d3 = - 1.0 / (self.N * (p ** 2)) + 1.0 / ((1.0 - p) ** 2) - 6.0 * elec_pre / ((p + self.phi_0) ** 4)
            return [d2, d3]

        p_guess = 1.0 / (1.0 + np.sqrt(self.N))
        c_guess = ((1.0 + np.sqrt(self.N)) ** 2) / (2.0 * self.N)
        sol = fsolve(equations, [p_guess, c_guess])
        return float(sol[0]), float(sol[1])

    def chi(self, T_K):
        """Effective LCST interaction parameter."""
        return self.chi_c + self.beta * (T_K - self.Tc_K)

    def free_energy_density(self, phi, T_K=310.15, I_M=0.155):
        """Dimensionless free energy density f(phi)."""
        phi = np.clip(phi, 1e-12, 1.0 - 1e-12)
        f_mix = (phi / self.N) * np.log(phi) + (1.0 - phi) * np.log(1.0 - phi)
        f_int = self.chi(T_K) * phi * (1.0 - phi)
        I_scaled = max(1e-6, I_M / self.I_0)
        f_elec = - self.alpha_DH * (I_scaled ** 1.5) * (phi / (phi + self.phi_0))
        return f_mix + f_int + f_elec

    def chemical_potential(self, phi, T_K=310.15, I_M=0.155):
        """mu(phi) = df/dphi."""
        phi = np.clip(phi, 1e-12, 1.0 - 1e-12)
        d_mix = (1.0 / self.N) * (np.log(phi) + 1.0) - np.log(1.0 - phi) - 1.0
        d_int = self.chi(T_K) * (1.0 - 2.0 * phi)
        I_scaled = max(1e-6, I_M / self.I_0)
        d_elec = - self.alpha_DH * (I_scaled ** 1.5) * (self.phi_0 / ((phi + self.phi_0) ** 2))
        return d_mix + d_int + d_elec

    def osmotic_pressure(self, phi, T_K=310.15, I_M=0.155):
        """Pi(phi) = phi * mu(phi) - f(phi)."""
        return phi * self.chemical_potential(phi, T_K, I_M) - self.free_energy_density(phi, T_K, I_M)

    def spinodal_derivative(self, phi, T_K=310.15, I_M=0.155):
        """d2f/dphi2 for spinodal condition."""
        phi = np.clip(phi, 1e-12, 1.0 - 1e-12)
        d2_mix = 1.0 / (self.N * phi) + 1.0 / (1.0 - phi)
        d2_int = - 2.0 * self.chi(T_K)
        I_scaled = max(1e-6, I_M / self.I_0)
        d2_elec = 2.0 * self.alpha_DH * (I_scaled ** 1.5) * self.phi_0 / ((phi + self.phi_0) ** 3)
        return d2_mix + d2_int + d2_elec

    def find_binodal_coexistence(self, T_K=310.15, I_M=0.155):
        """
        Numerically determined common-tangent binodal coexistence boundaries.
        """
        c = self.chi(T_K)
        if c <= self.chi_c:
            return None, None

        def grand_potential(p, mu_val):
            return self.free_energy_density(p, T_K, I_M) - mu_val * p

        def diff_omega(mu_val):
            r1 = minimize_scalar(lambda p: grand_potential(p, mu_val), bounds=(1e-7, self.phi_c), method='bounded')
            r2 = minimize_scalar(lambda p: grand_potential(p, mu_val), bounds=(self.phi_c, 0.9999), method='bounded')
            return r1.fun - r2.fun

        mu_min = self.chemical_potential(1e-4, T_K, I_M)
        mu_max = self.chemical_potential(0.999, T_K, I_M)

        mu_grid = np.linspace(mu_min, mu_max, 100)
        vals = [diff_omega(m) for m in mu_grid]

        sign_changes = np.where(np.diff(np.sign(vals)))[0]
        if len(sign_changes) == 0:
            return None, None

        idx = sign_changes[0]
        m1, m2 = mu_grid[idx], mu_grid[idx + 1]

        # Secant method:
        for _ in range(40):
            f1, f2 = diff_omega(m1), diff_omega(m2)
            if abs(f2 - f1) < 1e-14:
                break
            m_next = m2 - f2 * (m2 - m1) / (f2 - f1)
            m1, m2 = m2, m_next
            if abs(f2) < 1e-10:
                break

        mu_star = m2
        r1 = minimize_scalar(lambda p: grand_potential(p, mu_star), bounds=(1e-7, self.phi_c), method='bounded')
        r2 = minimize_scalar(lambda p: grand_potential(p, mu_star), bounds=(self.phi_c, 0.9999), method='bounded')
        return float(r1.x), float(r2.x)

    def find_spinodal_points(self, T_K=310.15, I_M=0.155):
        """Numerically determined spinodal instability roots."""
        if self.chi(T_K) <= self.chi_c:
            return None, None
        grid1 = np.linspace(1e-4, self.phi_c, 100)
        grid2 = np.linspace(self.phi_c, 0.999, 100)
        v1 = [self.spinodal_derivative(p, T_K, I_M) for p in grid1]
        v2 = [self.spinodal_derivative(p, T_K, I_M) for p in grid2]
        idx1 = np.where(np.diff(np.sign(v1)))[0]
        idx2 = np.where(np.diff(np.sign(v2)))[0]
        sp1 = float(grid1[idx1[0]]) if len(idx1) > 0 else None
        sp2 = float(grid2[idx2[0]]) if len(idx2) > 0 else None
        return sp1, sp2

    def calculate_apparent_cloud_point(self, a_s_nm_inv, material="borophene", phi_total=0.095, I_M=0.155):
        """
        Calculates the TRUE thermodynamic apparent cloud point T_cloud^app (in °C) by solving:
          phi_free(T, a_s) = phi_dilute(T)
        """
        for t_c in np.linspace(9.0, 60.0, 511):
            t_k = t_c + 273.15
            b1, b2 = self.find_binodal_coexistence(t_k, I_M=I_M)
            if b1 is not None:
                phi_f, _, _ = adsorption_equilibrium_dimensionless(phi_total, t_k, a_s_nm_inv, material)
                if phi_f >= b1:
                    return float(t_c)
        return None # Fully dissolved across temperature window
