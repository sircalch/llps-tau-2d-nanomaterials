"""
run_pipeline.py
===============
Master reproducibility pipeline for:
'Thermodynamic modulation of Tau liquid-liquid phase separation and condensate wetting
by two-dimensional nanomaterial interfaces: emergent suppression via adsorption equilibrium'

Executes:
  1. Unit tests for thermodynamic conversions and kinetic mass conservation
  2. Master figure generation (Figures 1-5, 300 DPI)
  3. Rebuilding of the official Word manuscript and ZIP distribution package
"""

import os, sys, subprocess, zipfile

def run_step(cmd, desc):
    print(f"\n{'='*70}\n>> {desc}\n{'='*70}")
    res = subprocess.run([sys.executable] + cmd.split(), capture_output=True, text=True)
    print(res.stdout)
    if res.returncode != 0:
        print(f"ERROR:\n{res.stderr}")
        sys.exit(1)

def main():
    # 1. Run unit tests
    run_step("tests/test_thermodynamics_and_conversions.py", "Step 1: Running unit tests and dimensional verification")

    # 2. Generate publication figures
    run_step("src/analysis/generate_master_figures.py", "Step 2: Generating all 5 Master Publication Figures (300 DPI)")

    # 3. Compile Master Manuscript
    run_step("scratch/build_single_master_manuscript.py", "Step 3: Compiling single master DOCX manuscript")

    # 4. Package distribution archive
    print(f"\n{'='*70}\n>> Step 4: Building distribution ZIP package\n{'='*70}")
    zip_name = 'PAQUETE_PROYECTO_LLPS_TAU_2D_NANOMATERIALS.zip'
    files_to_pack = [
        'manuscript/manuscript_LLPS_Tau_2D_Nanomaterials.docx',
        'figures/Graphical_Abstract.png',
        'figures/Figure_1_Tau_LLPS_Phase_Diagram_2D_Interface.png',
        'figures/Figure_2_Wetting_and_Salt_Phase_Diagrams.png',
        'figures/Figure_3_Condensate_Aging_and_Fibrillation_Arrest.png',
        'figures/Figure_4_Sobol_Sensitivity_LLPS.png',
        'figures/Figure_5_Borophene_vs_MXene_Comparison.png',
        'src/thermodynamics/material_parameters.py',
        'src/thermodynamics/flory_huggins_voorn_overbeek.py',
        'src/thermodynamics/cahn_hilliard_wetting.py',
        'src/kinetics/condensate_aging_kinetics.py',
        'src/analysis/generate_master_figures.py',
        'tests/test_thermodynamics_and_conversions.py',
        'data/ambadipudi_2017_fig2b_K18_pH8p8.csv',
        'README.md',
        'requirements.txt',
        'LICENSE',
        'CITATION.cff'
    ]

    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in files_to_pack:
            if os.path.exists(f):
                zf.write(f)

    print(f"Master ZIP Package built: {zip_name} ({os.path.getsize(zip_name)/(1024*1024):.2f} MB)")
    print(f"\nAll pipeline stages completed successfully!")

if __name__ == "__main__":
    main()
