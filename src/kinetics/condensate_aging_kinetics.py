"""
condensate_aging_kinetics.py
============================
Coupled chemical master equations for biomolecular condensate aging and fibrillation
with strictly consistent order-parameter scaling and machine-precision mass conservation.

Dimensional and Physical Architecture:
--------------------------------------
1. State Variables (Strictly Dimensionless Order-Parameter Mass Fractions):
   - phi_dense(t): Soluble liquid-phase protein monomer fraction inside droplet
   - P_drop(t):    Number concentration of amyloid fibril growth ends
   - M_drop(t):    Solid cross-beta fibril mass fraction inside droplet
   - m_ads(t):     Protein mass fraction sequestered at 2D nanosheet interface

2. Dimensionless Surface Capacity on Order-Parameter Scale:
   - m_tilde_max = s_phi * (a_s * Gamma_max * 1e27) / N_A
     where s_phi = 9.50e-4 uM^-1, [a_s] = nm^-1, [Gamma_max] = nm^-2.
   - theta_sat = m_ads / (m_tilde_max + 1e-12)  (Strictly dimensionless!)

3. Microscopic Reaction Fluxes [h^-1]:
   - J_prim    = k_n * phi_dense^(n_c)
   - J_sec     = k_2 * phi_dense^(n_2) * M_drop
   - J_elong   = 2 * k_+ * phi_dense * P_drop
   - J_extract = k_ext * m_tilde_max * max(0.0, 1.0 - theta_sat) * phi_dense - k_des * m_ads

4. Master Equations:
   dphi_dense/dt = - n_c J_prim - n_2 J_sec - J_elong - J_extract
   dP_drop/dt   = J_prim + J_sec
   dM_drop/dt   = n_c J_prim + n_2 J_sec + J_elong
   dm_ads/dt    = J_extract

   Exact invariant: d/dt [ phi_dense(t) + M_drop(t) + m_ads(t) ] = 0  (to < 10^-15)
"""

import numpy as np
from scipy.integrate import solve_ivp

try:
    from src.thermodynamics.material_parameters import calculate_m_tilde_max, TAU_K18_SYSTEM
except ImportError:
    try:
        from ..thermodynamics.material_parameters import calculate_m_tilde_max, TAU_K18_SYSTEM
    except ImportError:
        from material_parameters import calculate_m_tilde_max, TAU_K18_SYSTEM


class CondensateAgingKinetics:
    """
    Mass-conserving kinetic solver for condensate aging and interfacial monomer extraction.
    """

    def __init__(self,
                 k_n=1.5e-4,       # Primary nucleation rate constant [h^-1]
                 n_c=2.0,          # Primary reaction order
                 k_2=2.8e-2,       # Secondary nucleation rate constant [h^-1]
                 n_2=2.0,          # Secondary reaction order
                 k_plus=1.2e2,     # Elongation rate constant [h^-1]
                 k_extract=1.25,   # Interfacial extraction rate constant [h^-1]
                 k_desorb=0.04,    # Phenomenological desorption rate constant [h^-1]
                 Gamma_max=0.38):  # Saturation site density [nm^-2]
        self.k_n = float(k_n)
        self.n_c = float(n_c)
        self.k_2 = float(k_2)
        self.n_2 = float(n_2)
        self.k_plus = float(k_plus)
        self.k_extract = float(k_extract)
        self.k_desorb = float(k_desorb)
        self.Gamma_max = float(Gamma_max)

    def _derivatives(self, t, y, a_s_nm_inv):
        phi_dense, P_drop, M_drop, m_ads = y
        phi_dense = max(0.0, phi_dense)
        P_drop    = max(0.0, P_drop)
        M_drop    = max(0.0, M_drop)
        m_ads     = max(0.0, m_ads)

        # Dimensionless capacity on exact order-parameter scale
        m_tilde_max = calculate_m_tilde_max(a_s_nm_inv, self.Gamma_max)
        theta_sat = min(1.0, m_ads / (m_tilde_max + 1e-12)) if m_tilde_max > 1e-9 else 1.0

        # Microscopic fluxes [h^-1]
        J_prim = self.k_n * (phi_dense ** self.n_c)
        J_sec  = self.k_2 * (phi_dense ** self.n_2) * M_drop
        J_elong = 2.0 * self.k_plus * phi_dense * P_drop

        if m_tilde_max > 1e-9:
            J_extract = self.k_extract * m_tilde_max * max(0.0, 1.0 - theta_sat) * phi_dense - self.k_desorb * m_ads
        else:
            J_extract = 0.0

        d_phi = - self.n_c * J_prim - self.n_2 * J_sec - J_elong - J_extract
        d_P   = J_prim + J_sec
        d_M   = self.n_c * J_prim + self.n_2 * J_sec + J_elong
        d_m   = J_extract

        return [d_phi, d_P, d_M, d_m]

    def simulate(self, t_span=(0.0, 72.0), phi_0=0.60, a_s_nm_inv=0.0, num_points=300):
        """
        Solves ODE system with LSODA solver and computes solidification lag time.
        """
        t_eval = np.linspace(t_span[0], t_span[1], num_points)
        y0 = [float(phi_0), 1e-6, 0.0, 0.0]

        sol = solve_ivp(
            fun=lambda t, y: self._derivatives(t, y, a_s_nm_inv),
            t_span=t_span,
            y0=y0,
            t_eval=t_eval,
            method='LSODA',
            rtol=1e-7,
            atol=1e-9
        )

        phi_dense = np.maximum(0.0, sol.y[0])
        P_drop    = np.maximum(0.0, sol.y[1])
        M_drop    = np.maximum(0.0, sol.y[2])
        m_ads     = np.maximum(0.0, sol.y[3])

        # Control simulation to define fixed absolute lag threshold: 10% of M_control(72 h)
        if a_s_nm_inv == 0.0:
            M_ctrl_72 = M_drop[-1]
        else:
            sol_ctrl = solve_ivp(
                fun=lambda t, y: self._derivatives(t, y, 0.0),
                t_span=(0.0, 72.0),
                y0=[float(phi_0), 1e-6, 0.0, 0.0],
                method='LSODA',
                rtol=1e-7,
                atol=1e-9
            )
            M_ctrl_72 = sol_ctrl.y[2][-1]

        threshold = 0.10 * M_ctrl_72
        above_idx = np.where(M_drop >= threshold)[0]
        if len(above_idx) > 0:
            t_lag = float(sol.t[above_idx[0]])
        else:
            t_lag = float(t_span[1] + 1.0)

        # Exact mass conservation check:
        total_mass = phi_dense + M_drop + m_ads
        mass_error = float(np.max(np.abs(total_mass - phi_0)))

        return {
            "time": sol.t,
            "phi_dense": phi_dense,
            "P_drop": P_drop,
            "M_drop": M_drop,
            "m_ads": m_ads,
            "t_lag": t_lag,
            "M_final": float(M_drop[-1]),
            "mass_error": mass_error
        }
