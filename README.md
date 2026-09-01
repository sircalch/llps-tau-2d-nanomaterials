[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This repository contains the statistical-thermodynamic, Cahn-Hilliard interfacial gradient, and chemical master equation code supporting the manuscript:

> **Thermodynamic modulation of Tau liquid-liquid phase separation and condensate wetting by two-dimensional nanomaterial interfaces: emergent suppression via adsorption equilibrium**  
> Andrés Monreal Hernández, Jesús Martín Muñoz Bautista, Sara Lizbeth Franco Amaya, and Carlos Ivanhoe Martínez Osorio.

---

## 🔬 Scientific Summary

* **Bulk LCST Thermodynamics:** Calibrated Flory-Huggins-Voorn-Overbeek (FH-VO) engine matching the Lower Critical Solution Temperature (LCST) and turbidity onset of Tau K18 ($100\ \mu\text{M} \leftrightarrow T_{\text{cloud}} = 15.0^\circ\text{C}$; Ambadipudi et al., *Nat. Commun.* 2017).
* **Adsorption Mass Balance:** Standard thermodynamic activity formulation ($a = c / c^\circ$) with exact surface capacity $c_{\max} = \frac{a_s \Gamma_{\max} \cdot 10^{30}}{N_A}\ [\mu\text{M}]$.
* **Emergent LLPS Dissolution:** Stabilized Borophene ($\Delta G_{\text{ads}} = -7.8\text{ kcal/mol}$) suppresses LLPS near $C_{\text{nano}}^{\text{crit}} \approx 98.6\ \mu\text{g/mL}$ at $37^\circ\text{C}$, whereas $\text{Ti}_3\text{C}_2\text{T}_x$ MXene ($\Delta G_{\text{ads}} = -5.2\text{ kcal/mol}$) produces partial depletion ($c_{\text{free}} \approx 88\ \mu\text{M}$ at $100\ \mu\text{g/mL}$), maintaining stable droplets.
* **Cahn-Hilliard Wetting:** Derived Young contact angles ($\theta_c = 50.3^\circ$ for Borophene vs $79.3^\circ$ for MXene) under a unified continuum energy-density scale $f_0 = 1.50\times 10^4\text{ J/m}^3$ ($\gamma_{LL} = 1.60\ \mu\text{N/m}$).
* **Condensate Aging Kinetics:** Mass-conserving master equations ($\max |\Delta M| < 10^{-14}$) evaluating secondary nucleation retardation under dimensional fluxes.
* **Global Sensitivity Analysis:** Saltelli-Jansen Sobol variance decomposition ($N_{\text{base}} = 2048$, $20,480$ evaluations) with block-correct convergence.

---

## 📁 Repository Structure

```
llps-tau-2d-nanomaterials/
├── manuscript/
│   └── manuscript_LLPS_Tau_2D_Nanomaterials.docx  # Official master Word manuscript
├── figures/
│   ├── Graphical_Abstract.png                      # Graphical abstract
│   ├── Figure_1_Tau_LLPS_Phase_Diagram_2D_Interface.png
│   ├── Figure_2_Wetting_and_Salt_Phase_Diagrams.png
│   ├── Figure_3_Condensate_Aging_and_Fibrillation_Arrest.png
│   ├── Figure_4_Sobol_Sensitivity_LLPS.png
│   └── Figure_5_Borophene_vs_MXene_Comparison.png
├── src/
│   ├── thermodynamics/
│   │   ├── material_parameters.py                  # Audited biological & material constants
│   │   ├── flory_huggins_voorn_overbeek.py         # FH-VO thermodynamic solver & binodals
│   │   └── cahn_hilliard_wetting.py                # Interfacial gradient & Young contact angles
│   ├── kinetics/
│   │   └── condensate_aging_kinetics.py            # Mass-conserving master equations
│   └── analysis/
│       └── generate_master_figures.py              # 300 DPI master figure renderer
├── tests/
│   └── test_thermodynamics_and_conversions.py     # Unit test suite
├── run_pipeline.py                                 # Single master reproducibility script
├── requirements.txt
├── LICENSE
└── README.md
```

---

## 🚀 Quick Start & Full Reproduction

### 1. Installation

Clone this repository and install dependencies:

```bash
git clone https://github.com/sircalch/llps-tau-2d-nanomaterials.git
cd llps-tau-2d-nanomaterials
pip install -r requirements.txt
```

### 2. Run the Full Pipeline

Execute the master reproduction pipeline (runs unit tests, generates all 5 figures at 300 DPI, and recompiles the master DOCX):

```bash
python run_pipeline.py
```

### 3. Run Unit Tests Only

```bash
pytest tests/
```

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
