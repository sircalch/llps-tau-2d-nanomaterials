[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This repository contains the statistical-thermodynamic, Cahn-Hilliard interfacial gradient, and chemical master equation code supporting the manuscript:

> **Thermodynamic modulation of Tau liquid-liquid phase separation and condensate wetting by two-dimensional nanomaterial interfaces: emergent suppression via adsorption equilibrium**  
> Andrés Monreal Hernández, Jesús Martín Muñoz Bautista, Sara Lizbeth Franco Amaya, and Carlos Ivanhoe Martínez Osorio.

---

## 🔬 Scientific Summary

* **Bulk LCST Thermodynamics:** Calibrated Flory-Huggins-Voorn-Overbeek (FH-VO) engine matching the Lower Critical Solution Temperature (LCST) and turbidity onset of Tau K18 ($100\ \mu\text{M} \leftrightarrow T_{\text{cloud}} = 15.3^\circ\text{C}$ via Brent's method; consistent with ~15 °C onset, Ambadipudi et al., *Nat. Commun.* 2017).
* **Adsorption Mass Balance:** Standard thermodynamic activity formulation ($a = c / c^\circ$) with exact surface capacity $c_{\max} = \frac{a_s \Gamma_{\max} \cdot 10^{30}}{N_A}\ [\mu\text{M}]$.
* **Adsorption-Driven Monomer Depletion at 37 °C:** Stabilized Borophene ($\Delta G_{\text{ads}} = -7.8\text{ kcal/mol}$, $100\ \mu\text{g/mL}$) shifts the apparent cloud point to $T_{\text{cloud}}^{\text{app}} \approx 29.4^\circ\text{C}$ and depletes free monomer to $c_{\text{free}} \approx 41.4\ \mu\text{M}$ (~60% depletion) at $37^\circ\text{C}$. LLPS is dissolved at $T \le 29.4^\circ\text{C}$ but remains active at $37^\circ\text{C}$. $\text{Ti}_3\text{C}_2\text{T}_x$ MXene ($\Delta G_{\text{ads}} = -5.2\text{ kcal/mol}$) produces partial depletion ($c_{\text{free}} \approx 87.6\ \mu\text{M}$ at $100\ \mu\text{g/mL}$, $T_{\text{cloud}}^{\text{app}} \approx 17.8^\circ\text{C}$), maintaining stable droplets.
* **Cahn-Hilliard Wetting:** Derived Young contact angles ($\theta_c = 50.3^\circ$ for Borophene vs $79.3^\circ$ for MXene) under a unified continuum energy-density scale $f_0 = 1.50\times 10^4\text{ J/m}^3$ ($\gamma_{LL} = 1.60\ \mu\text{N/m}$).
* **Condensate Aging Kinetics:** Mass-conserving master equations ($\max |\Delta M| < 10^{-14}$) evaluating secondary nucleation retardation under dimensional fluxes.
* **Global Sensitivity Analysis:** Saltelli-Jansen Sobol variance decomposition ($N_{\text{base}} = 1024$, $D = 8$, $N_{\text{eval}} = 10240$; scrambled Sobol seed=42, Jansen estimator) with block convergence verified across $N \in \{128, 256, 512, 1024\}$. The cloud-point solver extrapolates smoothly outside the thermal evaluation window so the sensitivity response carries no clamp discontinuity.

---

## 📁 Repository Structure

```
llps-tau-2d-nanomaterials/
├── manuscript/
│   ├── manuscript_LLPS_Tau_2D_Nanomaterials.docx   # Official master Word manuscript
│   ├── cover_letter_Soft_Matter.docx / .md         # Editor cover letter
├── figures/                                        # Each figure: .png (300 dpi) + .pdf (vector) + .tif (600 dpi, git-ignored)
│   ├── Figure_1_Tau_LLPS_Phase_Diagram.*           # Bulk LCST phase diagram & adsorption depletion
│   ├── Figure_2_Wetting_and_Salt_Phase_Diagrams.*  # Salt screening & Cahn-Hilliard wetting map
│   ├── Figure_3_Borophene_vs_MXene_Comparison.*    # T_cloud^app, theta_c(T), tau_lag, M_final
│   ├── Figure_4_Condensate_Aging_Kinetics.*        # Mass-conserving master-equation trajectories
│   ├── Figure_5_Sobol_Sensitivity_Analysis.*       # Saltelli-Jansen Sobol GSA & block convergence
│   └── TOC_Graphic_RSC_Soft_Matter.*              # 8 cm x 4 cm table-of-contents graphic
├── data/
│   ├── ambadipudi_2017_fig2b_K18_pH8p8.csv         # Digitized experimental turbidity (Ambadipudi 2017)
│   ├── sobol_indices_N1024.csv                      # Sobol S1 / ST with 95% bootstrap CI
│   ├── sobol_convergence_N1024.csv                  # Dyadic sub-block convergence table
│   └── sobol_evaluations_N1024.npz                  # Raw 10240 physical model evaluations
├── src/
│   ├── thermodynamics/
│   │   ├── material_parameters.py                  # Audited biological & material constants
│   │   ├── flory_huggins_voorn_overbeek.py         # FH-VO thermodynamic solver & binodals
│   │   └── cahn_hilliard_wetting.py                # Interfacial gradient & Young contact angles
│   ├── kinetics/
│   │   └── condensate_aging_kinetics.py            # Mass-conserving master equations
│   └── analysis/
│       ├── generate_master_figures.py              # Figures 1-5 (PNG 300 dpi / PDF / TIFF 600 dpi)
│       └── generate_rsc_toc.py                     # RSC TOC graphic renderer
├── scratch/
│   ├── run_salib_sobol.py                          # Regenerates data/sobol_*  (heavy: 10240 evals)
│   ├── build_single_master_manuscript.py           # Compiles the master DOCX
│   └── build_cover_letter.py                       # Compiles the cover letter
├── tests/
│   └── test_thermodynamics_and_conversions.py      # 11-test unit suite
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

Execute the master reproduction pipeline. It runs the unit test suite, regenerates all
five master figures (PNG 300 dpi + vector PDF + TIFF 600 dpi) and the RSC TOC graphic,
recompiles the master DOCX manuscript and the cover letter, and rebuilds the
distribution ZIP:

```bash
python run_pipeline.py
```

### 3. Run Unit Tests Only

```bash
pytest tests/
```

### 4. Regenerate the Global Sensitivity Analysis (optional, heavy)

The Sobol datasets in `data/` are committed so the pipeline and figures are fully
reproducible without a long recompute. To regenerate them from scratch
(10240 physical model evaluations, parallelised; several minutes):

```bash
python scratch/run_salib_sobol.py
```

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
