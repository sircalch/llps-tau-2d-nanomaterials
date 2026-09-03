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
    run_step("-m pytest tests/ -v", "Step 1: Running all 11 unit tests and dimensional verifications")

    # 2. Generate publication figures
    run_step("src/analysis/generate_master_figures.py", "Step 2: Generating all 5 Master Publication Figures (PNG, PDF, TIFF)")

    # 3. Generate RSC TOC Graphic
    run_step("src/analysis/generate_rsc_toc.py", "Step 3: Generating RSC TOC Entry Graphic (8 cm x 4 cm)")

    # 4. Compile Master Manuscript
    run_step("scratch/build_single_master_manuscript.py", "Step 4: Compiling single master DOCX manuscript")

    # 5. Compile Cover Letter
    run_step("scratch/build_cover_letter.py", "Step 5: Compiling official Cover Letter for Soft Matter")

    # 6. Package distribution archive
    print(f"\n{'='*70}\n>> Step 6: Building distribution ZIP package\n{'='*70}")
    zip_name = 'PAQUETE_PROYECTO_LLPS_TAU_2D_NANOMATERIALS.zip'
    files_to_pack = [
        'manuscript/manuscript_LLPS_Tau_2D_Nanomaterials.docx',
        'manuscript/cover_letter_Soft_Matter.docx',
        'manuscript/cover_letter_Soft_Matter.md',
        'figures/TOC_Graphic_RSC_Soft_Matter.png',
        'figures/TOC_Graphic_RSC_Soft_Matter.pdf',
        'figures/Figure_1_Tau_LLPS_Phase_Diagram.png',
        'figures/Figure_1_Tau_LLPS_Phase_Diagram.pdf',
        'figures/Figure_2_Wetting_and_Salt_Phase_Diagrams.png',
        'figures/Figure_2_Wetting_and_Salt_Phase_Diagrams.pdf',
        'figures/Figure_3_Borophene_vs_MXene_Comparison.png',
        'figures/Figure_3_Borophene_vs_MXene_Comparison.pdf',
        'figures/Figure_4_Condensate_Aging_Kinetics.png',
        'figures/Figure_4_Condensate_Aging_Kinetics.pdf',
        'figures/Figure_5_Sobol_Sensitivity_Analysis.png',
        'figures/Figure_5_Sobol_Sensitivity_Analysis.pdf',
        'data/sobol_indices_N1024.csv',
        'data/sobol_convergence_N1024.csv',
        'data/sobol_evaluations_N1024.npz',
        'data/ambadipudi_2017_fig2b_K18_pH8p8.csv',
        'src/thermodynamics/material_parameters.py',
        'src/thermodynamics/flory_huggins_voorn_overbeek.py',
        'src/thermodynamics/cahn_hilliard_wetting.py',
        'src/kinetics/condensate_aging_kinetics.py',
        'src/analysis/generate_master_figures.py',
        'src/analysis/generate_rsc_toc.py',
        'tests/test_thermodynamics_and_conversions.py',
        'scratch/run_salib_sobol.py',
        'scratch/build_single_master_manuscript.py',
        'scratch/build_cover_letter.py',
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
