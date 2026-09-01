"""
material_parameters.py
======================
Audited physical, biological, and material parameters for Tau K18 LLPS
and 2D nanomaterial biointerfaces (Stabilized Borophene vs Ti3C2Tx MXene).

Key Physical and Dimensional Architecture:
-----------------------------------------
1. Order Parameter vs Experimental Concentration:
   phi_tilde is the effective coarse-grained order parameter:
     phi_tilde = s_phi * c
   where:
     - s_phi = 0.950 mM^-1 = 9.50e-4 uM^-1 (calibrated so that c = 100 uM -> phi_tilde = 0.095)
     - Reference lattice volume: v_ref = 0.95 / N_A = 1.58e-24 m³ = 1580 nm³
     - Hydrodynamic radius: R_h = 3.4 ± 0.6 nm (SAXS/DLS, JACS Au 2021, 1:1007)
     - Molar overlap concentration: c*_molar = 3 / (4 * pi * N_A * Rh³) ~ 10.1 mM
     - Mass overlap concentration: c*_mass ~ 141 g/L

2. Thermodynamic Activity in Langmuir Adsorption:
   Standard state: c_deg = 1.0 M = 1.0e6 uM.
   Thermodynamic activity: a_thermo = c / c_deg = (phi_tilde / s_phi) / 1.0e6 = phi_tilde / (s_phi * 1.0e6) = phi_tilde / 950.0.
   Adsorption coverage:
     theta_ads = (K_deg * a_thermo) / (1.0 + K_deg * a_thermo)
   where K_deg = exp(-dG_deg / (R * T)).

3. Nanosheet Loading Translation & Consistent Capacity:
   a_s = SSA * C_nano
   For SSA = 1000 m²/g:
     C_nano = 1 ug/mL = 1 g/m³ -> a_s = 1000 m^-1 = 1.0e-6 nm^-1.
     C_nano = 100 ug/mL -> a_s = 1.0e-4 nm^-1.
   Adsorption capacity in molar terms:
     c_max_ads = (a_s * Gamma_max * 1e27) / N_A  [uM]
   Dimensionless capacity on order-parameter scale:
     m_tilde_max = s_phi * c_max_ads = s_phi * (a_s * Gamma_max * 1e27) / N_A
   Exact order-parameter mass balance:
     phi_tilde_total = phi_tilde_free + m_tilde_max * theta_ads
"""

import numpy as np

# -----------------------------------------------------------------------
# Fundamental Constants
# -----------------------------------------------------------------------
R_GAS_KCAL = 1.987e-3   # kcal / (mol·K)
R_GAS      = 1.987e-3   # kcal / (mol·K)
R_GAS_J    = 8.314      # J / (mol·K)
N_AVO      = 6.022e23   # mol⁻¹
KB_J       = 1.381e-23  # J / K
C_STANDARD_UM = 1.0e6   # 1.0 M standard state = 1.0e6 uM

# -----------------------------------------------------------------------
# Biological Reference System: Tau K18 (Ambadipudi et al., Nat Commun 2017)
# -----------------------------------------------------------------------
TAU_K18_SYSTEM = {
    "construct": "Tau K18 (4-repeat microtubule-binding domain, Q244-E372)",
    "molecular_weight_Da": 14000.0,
    "N_eff": 10.0,                        # Effective Flory polymerization index
    "bare_molecular_volume_nm3": 17.2,    # Dry molecular volume MW / (rho * N_A)
    "hydrodynamic_radius_nm": 3.4,        # Experimental Rh from SAXS/DLS (Ramis et al., JACS Au 2021, 1:1007)
    "swollen_coil_volume_nm3": 164.6,     # 4/3 * pi * Rh³
    "c_star_molar_mM": 10.1,              # Molar overlap concentration: 3 / (4 pi N_A Rh³)
    "c_star_mass_g_L": 141.0,             # Mass overlap concentration: 3 MW / (4 pi N_A Rh³)
    "s_phi_per_uM": 9.50e-4,              # Calibrated order-parameter scale factor: 0.950 mM^-1
    "reference_c_uM": 100.0,              # Nominal experimental concentration (100 uM -> phi_tilde = 0.095)
    "experimental_buffer": "100 uM Tau K18, 50 mM sodium phosphate, pH 8.8, 0.5 mM TCEP",
    "fitted_effective_Tc_C": 8.5,         # Calibrated critical temperature Tc (cloud point at 100 uM = 15.0 °C)
    "fitted_effective_beta": 0.0090,      # Calibrated LCST slope beta [K^-1]
    "reference_volume_m3": 2.85e-25,      # Phenomenological energy-density scale volume v_ref (f0 = 1.50e4 J/m³)
    "eta_eff_nominal": 0.20e-3,           # Phenomenological interfacial coupling factor (xi / R ~ 10^-3)
}

# -----------------------------------------------------------------------
# Table 2: Material-Specific Parameter Registry (Audited Literature DOIs)
# -----------------------------------------------------------------------
MATERIAL_TABLE_2 = {
    "borophene": {
        "name": "Stabilized Borophene (aqueous-passivated nanoflakes)",
        "dG_ads_kcal_mol": -7.8,
        "dG_ads_type": "Model representative scenario (Han et al., ACS Appl. Bio Mater. 2020, 3:4220, DOI: 10.1021/acsabm.0c00306)",
        "Gamma_max_nm2": 0.38,
        "Gamma_max_type": "Geometric model estimate (1 / A_footprint, A_footprint ~ 2.6 nm²)",
        "psi_s_mV": -32.4,
        "psi_s_type": "Experimental Zeta potential (Czarniewska et al., Sci. Rep. 2023, 13:11823, DOI: 10.1038/s41598-023-38595-8)",
        "k_ext_per_h": 1.25,
        "k_ext_type": "Phenomenological kinetic parameter (diffusion-collision limit)",
        "k_des_per_h": 0.04,
        "k_des_type": "Phenomenological kinetic desorption rate constant",
        "color": "#DC2626",
        "linestyle": "-",
    },
    "mxene": {
        "name": "MXene (Ti3C2Tx, mixed -O, -OH, -F terminations)",
        "dG_ads_kcal_mol": -5.2,
        "dG_ads_type": "Model representative scenario (Gouveia et al., ACS Appl. Bio Mater. 2020, 3:5913, DOI: 10.1021/acsabm.0c00621)",
        "Gamma_max_nm2": 0.26,
        "Gamma_max_type": "Geometric model estimate (1 / A_footprint, A_footprint ~ 3.8 nm²)",
        "psi_s_mV": -65.0,
        "psi_s_type": "Experimental Zeta potential of delaminated Ti3C2Tx at pH 7.4 (Alhabeb et al., Chem. Mater. 2017, 29:7633)",
        "k_ext_per_h": 0.75,
        "k_ext_type": "Phenomenological kinetic parameter",
        "k_des_per_h": 0.12,
        "k_des_type": "Phenomenological kinetic desorption rate constant",
        "color": "#2563EB",
        "linestyle": "--",
    },
    "control": {
        "name": "Bulk Solution (No Interface Control)",
        "dG_ads_kcal_mol": 0.0,
        "dG_ads_type": "Control baseline",
        "Gamma_max_nm2": 0.0,
        "Gamma_max_type": "N/A",
        "psi_s_mV": 0.0,
        "psi_s_type": "N/A",
        "k_ext_per_h": 0.0,
        "k_ext_type": "N/A",
        "k_des_per_h": 0.0,
        "k_des_type": "N/A",
        "color": "#64748B",
        "linestyle": ":",
    }
}

def calculate_m_tilde_max(a_s_nm_inv, Gamma_max_nm2=0.38):
    """
    Computes capacity on the exact order-parameter scale:
      c_max_ads = (a_s * Gamma_max * 1e30) / N_A  [uM]
      m_tilde_max = s_phi * c_max_ads
    """
    s_phi = TAU_K18_SYSTEM["s_phi_per_uM"]
    c_max_ads_uM = (a_s_nm_inv * Gamma_max_nm2 * 1e30) / N_AVO
    return float(s_phi * c_max_ads_uM)

def compute_thermodynamic_activity(phi_tilde):
    """Converts order parameter to standard thermodynamic activity a = c / c_deg."""
    s_phi = TAU_K18_SYSTEM["s_phi_per_uM"]
    c_uM = max(1e-12, phi_tilde / s_phi)
    return c_uM / C_STANDARD_UM

def adsorption_equilibrium_dimensionless(phi_total, T_K, a_s_nm_inv, material="borophene"):
    """
    Solves exact Langmuir adsorption mass balance with standard thermodynamic activity:
      a_free = c_free / c_deg = (phi_free / s_phi) / 1e6
      theta_ads = (K_deg * a_free) / (1 + K_deg * a_free)
      m_tilde_max = s_phi * (a_s * Gamma_max * 1e30) / N_A
      phi_total = phi_free + m_tilde_max * theta_ads
    """
    if material not in MATERIAL_TABLE_2 or material == "control":
        return float(phi_total), 0.0, 0.0

    mat = MATERIAL_TABLE_2[material]
    dG = mat["dG_ads_kcal_mol"]
    Gamma_max = mat["Gamma_max_nm2"]

    if a_s_nm_inv <= 0.0 or Gamma_max <= 0.0:
        return float(phi_total), 0.0, 0.0

    K_deg = np.exp(-dG / (R_GAS_KCAL * T_K))
    m_tilde_max = calculate_m_tilde_max(a_s_nm_inv, Gamma_max)

    # 1D root-finding via fixed-point iteration
    phi_f = float(phi_total)
    for _ in range(150):
        a_f = compute_thermodynamic_activity(phi_f)
        theta = (K_deg * a_f) / (1.0 + K_deg * a_f)
        phi_next = max(1e-12, phi_total - m_tilde_max * theta)
        if abs(phi_next - phi_f) < 1e-12:
            break
        phi_f = phi_next

    a_f = compute_thermodynamic_activity(phi_f)
    theta_eq = (K_deg * a_f) / (1.0 + K_deg * a_f)
    return float(phi_f), float(theta_eq), float(K_deg)

def calculate_surface_energy_excess_SI(T_K, phi_dilute, phi_dense, material="borophene", eta_eff=0.20e-3):
    """
    Derived surface free energy excess from Langmuir grand potential:
      Delta_gamma_s = eta_eff * k_B T * Gamma_max * ln((1 + K_deg * a_dense) / (1 + K_deg * a_dilute))
    
    Units: [J/m² = N/m]
    """
    if material not in MATERIAL_TABLE_2 or material == "control":
        return 0.0

    mat = MATERIAL_TABLE_2[material]
    dG = mat["dG_ads_kcal_mol"]
    Gamma_max_m2 = mat["Gamma_max_nm2"] * 1e18 # nm^-2 -> m^-2
    K_deg = np.exp(-dG / (R_GAS_KCAL * T_K))

    a_dilute = compute_thermodynamic_activity(phi_dilute)
    a_dense  = compute_thermodynamic_activity(phi_dense)

    term = (1.0 + K_deg * a_dense) / (1.0 + K_deg * a_dilute)
    delta_gamma = eta_eff * (KB_J * T_K) * Gamma_max_m2 * np.log(max(1.0, term))
    return float(delta_gamma)
