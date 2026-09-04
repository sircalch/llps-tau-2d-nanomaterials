"""
Generate the 5 ORCA 6.1.1 input decks for the epsilon_ads(borophene-PHF6) screening
campaign (Tyr and Lys sidechain mimics), following the same recipe already used and
tested on this machine for the sibling borophene-flake DFT work
(C:\\orca_workspace\\flake_bare\\input.inp): B3LYP-D3BJ/def2-SVP, RIJCOSX/def2-J,
partial constraint (freeze rim + passivating H, relax a central patch), 16 cores.

Deviation from that precedent, deliberate: adds CPCM(water). The adsorbates here
are charged/polar (butylammonium+, phenol) at a simulated physiological interface
(T=310.15 K in the kinetic model), so vacuum is not an acceptable default --
see project memory "Solvation Model Choice Criteria" (PBA bridge-collapse lesson).

Run order: cluster_opt -> tyr_opt / lys_opt -> complex_tyr_opt / complex_lys_opt
(the complex jobs read the SAME initial complex geometry already built by
build_structures.py; they do NOT depend on the isolated-cluster job finishing
first, so all 5 can in principle run in parallel if enough cores are free --
but see README for why that is a bad idea on a 16-core shared machine).
"""
import os

BASE = r"C:\Users\Andre\Proyectos doctorado\llps-tau-2d-nanomaterials\dft_eads_screening"
STRUCT = "..\\00_structures"
OUT = os.path.join(BASE, "01_orca_inputs")

KEYWORDS = "! B3LYP D3BJ def2-SVP def2/J RIJCOSX CPCM(water) TightSCF DefGrid3 Opt"

def freeze_block(freeze_indices):
    lines = ["  Constraints"]
    for i in freeze_indices:
        lines.append(f"    {{ C {i} C }}")
    lines.append("  end")
    return "\n".join(lines)

def write_input(name, xyzfile, charge, mult, nprocs=16, constraints=None):
    lines = [
        f"# {name}",
        KEYWORDS,
        f"%pal nprocs {nprocs} end",
        "%maxcore 3000",
        "%scf MaxIter 300 end",
    ]
    if constraints:
        lines.append("%geom")
        lines.append("  MaxIter 300")
        lines.append(freeze_block(constraints))
        lines.append("end")
    lines.append("")
    lines.append(f"* xyzfile {charge} {mult} {STRUCT}\\{xyzfile}")
    path = os.path.join(OUT, f"{name}.inp")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote", path)

def main():
    with open(os.path.join(BASE, "00_structures", "freeze_atoms_cluster_only.txt")) as f:
        f.readline()  # comment line
        freeze = [int(x) for x in f.readline().strip().split(",")]

    # 1. Bare cluster reference, partially relaxed (same freeze scheme as the complexes,
    #    so E_cluster,opt is on a consistent footing with the "far" atoms in the complex jobs).
    write_input("01_cluster_opt", "cluster_B60H24.xyz", charge=0, mult=1, constraints=freeze)

    # 2. Isolated ligand references, fully relaxed, no constraints.
    write_input("02_tyr_pcresol_opt", "tyr_pcresol.xyz", charge=0, mult=1)
    write_input("03_lys_butylammonium_opt", "lys_butylammonium.xyz", charge=1, mult=1)

    # 3. Complexes: same frozen cluster atoms as (1); central patch + full ligand relax freely.
    write_input("04_complex_tyr_opt", "complex_tyr_initial.xyz", charge=0, mult=1, constraints=freeze)
    write_input("05_complex_lys_opt", "complex_lys_initial.xyz", charge=1, mult=1, constraints=freeze)

if __name__ == "__main__":
    main()
