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
     parameterized to reproduce the experimental turbidity onset at 15.0 - 15.4 °C for 100 uM Tau K18
     (phi_total = 0.095) reported in Ambadipudi et al. (Nat. Commun. 2017).
  4. Apparent cloud point T_cloud^app is solved via true 1D root-finding (Brent's method)
     on the thermodynamic condition:
       phi_free(T, a_s, dG_ads) - phi_dilute(T, N, Tc, beta, I) = 0.
"""

import numpy as np
from scipy.optimize import minimize_scalar, fsolve, root_scalar, root

try:
    from .material_parameters import (
        adsorption_equilibrium_dimensionless,
        calculate_m_tilde_max,
        compute_thermodynamic_activity,
        MATERIAL_TABLE_2,
        TAU_K18_SYSTEM,
        KB_J,
        R_GAS_KCAL
    )
except ImportError:
    from material_parameters import (
        adsorption_equilibrium_dimensionless,
        calculate_m_tilde_max,
        compute_thermodynamic_activity,
        MATERIAL_TABLE_2,
        TAU_K18_SYSTEM,
        KB_J,
        R_GAS_KCAL
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
        Calculates common-tangent binodal coexistence boundaries (phi_dilute, phi_dense).
        Uses high-speed 2D algebraic solver with grand-potential minimization fallback.
        """
        c = self.chi(T_K)
        if c <= self.chi_c + 1e-6:
            return None, None

        # Ultra-fast 2D root solve with analytical critical-point scaling:
        d_chi = c - self.chi_c
        eps = np.sqrt(max(1e-6, d_chi))
        p1_init = max(1e-4, self.phi_c * (1.0 - np.tanh(eps)))
        p2_init = min(0.98, self.phi_c + (1.0 - self.phi_c) * np.tanh(eps))

        def eq_2d(p):
            p1, p2 = p
            if p1 <= 1e-9 or p2 >= 1.0 - 1e-9 or p1 >= p2:
                return [1e4, 1e4]
            mu1 = self.chemical_potential(p1, T_K, I_M)
            mu2 = self.chemical_potential(p2, T_K, I_M)
            pi1 = self.osmotic_pressure(p1, T_K, I_M)
            pi2 = self.osmotic_pressure(p2, T_K, I_M)
            return [mu1 - mu2, pi1 - pi2]

        sol = root(eq_2d, [p1_init, p2_init], method='hybr', tol=1e-8)
        if sol.success and 0.0 < sol.x[0] < self.phi_c < sol.x[1] < 1.0:
            return float(sol.x[0]), float(sol.x[1])

        # Secondary search around robust anchor point:
        sol2 = root(eq_2d, [0.03, 0.65], method='hybr', tol=1e-8)
        if sol2.success and 0.0 < sol2.x[0] < self.phi_c < sol2.x[1] < 1.0:
            return float(sol2.x[0]), float(sol2.x[1])

        # Robust grand-potential secant fallback:
        def grand_potential(p, mu_val):
            return self.free_energy_density(p, T_K, I_M) - mu_val * p

        def diff_omega(mu_val):
            r1 = minimize_scalar(lambda p: grand_potential(p, mu_val), bounds=(1e-7, self.phi_c), method='bounded')
            r2 = minimize_scalar(lambda p: grand_potential(p, mu_val), bounds=(self.phi_c, 0.9999), method='bounded')
            return r1.fun - r2.fun

        mu_min = self.chemical_potential(1e-4, T_K, I_M)
        mu_max = self.chemical_potential(0.999, T_K, I_M)
        mu_grid = np.linspace(mu_min, mu_max, 40)
        vals = [diff_omega(m) for m in mu_grid]
        sign_changes = np.where(np.diff(np.sign(vals)))[0]
        if len(sign_changes) == 0:
            return None, None

        idx = sign_changes[0]
        m1, m2 = mu_grid[idx], mu_grid[idx + 1]
        for _ in range(25):
            f1, f2 = diff_omega(m1), diff_omega(m2)
            if abs(f2 - f1) < 1e-14:
                break
            m_next = m2 - f2 * (m2 - m1) / (f2 - f1)
            m1, m2 = m2, m_next
            if abs(f2) < 1e-10:
                break

        r1 = minimize_scalar(lambda p: grand_potential(p, m2), bounds=(1e-7, self.phi_c), method='bounded')
        r2 = minimize_scalar(lambda p: grand_potential(p, m2), bounds=(self.phi_c, 0.9999), method='bounded')
        return float(r1.x), float(r2.x)

    def find_spinodal_points(self, T_K=310.15, I_M=0.155):
        """
        Spinodal instability roots (d2f/dphi2 = 0) on each side of the critical point.
        The zero crossing is linearly interpolated within the bracketing grid cell so the
        spinodal curve is smooth in T (a coarse grid alone quantises the root and produces
        stair-step / vertical artefacts in the phase-diagram figure).
        """
        if self.chi(T_K) <= self.chi_c:
            return None, None

        def branch_root(lo, hi):
            g = np.linspace(lo, hi, 400)
            v = np.array([self.spinodal_derivative(p, T_K, I_M) for p in g])
            idx = np.where(np.diff(np.sign(v)) != 0)[0]
            if len(idx) == 0:
                return None
            i = int(idx[0]); v0, v1 = float(v[i]), float(v[i + 1])
            if v1 == v0:
                return float(g[i])
            return float(g[i] - v0 * (g[i + 1] - g[i]) / (v1 - v0))

        return branch_root(1e-4, self.phi_c), branch_root(self.phi_c, 0.999)

    def calculate_apparent_cloud_point(self, a_s_nm_inv=0.0, material="borophene", phi_total=0.095,
                                       I_M=0.155, dG_ads=None, Gamma_max=None,
                                       t_max=65.0, extrapolate=True):
        """
        Solves the thermodynamic apparent cloud point T_cloud^app (in °C) from
          g(T) = phi_dilute(T, N, Tc, beta, I) - phi_free(T, a_s, dG_ads) = 0

        g(T) is strictly monotone decreasing in T (the dilute binodal falls and the
        adsorption-limited free monomer rises with T), so there is exactly one root.
        Inside [Tc + 0.1 degC, t_max] the root is bracketed and refined with Brent's method.

        When the root lies outside that window the function does NOT clamp to a constant
        (which injected an artificial discontinuity into the variance-based sensitivity
        analysis). With ``extrapolate=True`` (default) it linearly extends g(T) from its
        two nearest evaluated points and returns the extrapolated crossing:
          * g < 0 across the whole window  -> condensate stable even at Tc: root below the window
          * g > 0 across the whole window  -> fully dissolved up to t_max: root above the window
        The returned value is therefore a smooth, monotone function of every input
        parameter. ``extrapolate=False`` restores the legacy behaviour (returns t_min or None).
        """
        if dG_ads is None:
            dG_ads = MATERIAL_TABLE_2[material]["dG_ads_kcal_mol"] if material in MATERIAL_TABLE_2 else -7.8
        if Gamma_max is None:
            Gamma_max = MATERIAL_TABLE_2[material]["Gamma_max_nm2"] if material in MATERIAL_TABLE_2 else 0.38

        c_max_uM = (a_s_nm_inv * Gamma_max * 1e30) / 6.022e23
        m_max = 9.5e-4 * c_max_uM

        def phi_free(T_K):
            K_deg = np.exp(-dG_ads / (R_GAS_KCAL * T_K))
            pf = phi_total
            for _ in range(60):
                af = (pf / 9.5e-4) / 1e6
                th = (K_deg * af) / (1.0 + K_deg * af)
                pf_new = max(1e-12, phi_total - m_max * th)
                if abs(pf_new - pf) < 1e-14:
                    break
                pf = pf_new
            return pf

        def has_binodal(T_C):
            return self.find_binodal_coexistence(T_C + 273.15, I_M=I_M)[0] is not None

        def obj(T_C):
            b1, _ = self.find_binodal_coexistence(T_C + 273.15, I_M=I_M)
            if b1 is None:
                return 1.0  # below the LCST: homogeneous, cloud point not yet reached
            return b1 - phi_free(T_C + 273.15)

        t_min = self.Tc_K - 273.15 + 0.1

        T_grid = np.linspace(t_min, t_max, 40)
        g_grid = np.array([obj(t) for t in T_grid])
        sign_change = np.where(np.diff(np.sign(g_grid)) != 0)[0]

        if len(sign_change) > 0:
            i = int(sign_change[0])
            sol = root_scalar(obj, bracket=[T_grid[i], T_grid[i + 1]], method='brentq', xtol=5e-3)
            return float(sol.root)

        if not extrapolate:
            return float(t_min) if g_grid[0] < 0 else None

        if g_grid[-1] < 0:
            # Condensate stable throughout the window: extrapolate backward from the two
            # lowest-T points that still possess a defined binodal.
            valid = [k for k in range(len(T_grid)) if has_binodal(T_grid[k])]
            i0, i1 = valid[0], valid[1]
        else:
            # Fully dissolved throughout the window: extrapolate forward from the top two points.
            i0, i1 = len(T_grid) - 2, len(T_grid) - 1

        T0, T1 = float(T_grid[i0]), float(T_grid[i1])
        g0, g1 = obj(T0), obj(T1)
        slope = (g1 - g0) / (T1 - T0)
        if abs(slope) < 1e-12:
            return float(t_min - 50.0) if g_grid[-1] < 0 else float(t_max + 50.0)
        return float(np.clip(T1 - g1 / slope, -80.0, 400.0))

