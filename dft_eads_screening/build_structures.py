"""
Build initial geometries for the epsilon_ads(borophene-PHF6) DFT screening campaign.

Residue mimics (standard cluster-model practice for amino acid-surface adsorption):
  - Tyr sidechain -> p-cresol (4-methylphenol), neutral
  - Lys sidechain -> n-butylammonium (protonated primary amine), +1
    (physiological pH ~7.4 << Lys sidechain pKa ~10.5, so it is protonated)

Substrate: existing beta12 borophene B60H24 hydrogen-passivated cluster from
../../borophene-alzheimer-tau-ai/calculations/tau/beta12_B60H24_initial.xyz
(same source used for the docking/CDFT work in that sibling project; reused
here unmodified, not recomputed).

Produces, under 00_structures/:
  cluster_B60H24.xyz
  tyr_pcresol.xyz
  lys_butylammonium.xyz
  complex_tyr_initial.xyz
  complex_lys_initial.xyz
  freeze_atoms_cluster_only.txt      (1-indexed atom numbers to freeze, cluster alone)
  freeze_atoms_complex_tyr.txt       (same list, offset for the complex file)
  freeze_atoms_complex_lys.txt
"""
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem

SRC_CLUSTER = r"C:\Users\Andre\Proyectos doctorado\borophene-alzheimer-tau-ai\calculations\tau\beta12_B60H24_initial.xyz"
OUT = r"C:\Users\Andre\Proyectos doctorado\llps-tau-2d-nanomaterials\dft_eads_screening\00_structures"

def read_xyz(path):
    atoms = []
    with open(path) as f:
        n = int(f.readline())
        f.readline()
        for _ in range(n):
            p = f.readline().split()
            atoms.append((p[0], np.array([float(p[1]), float(p[2]), float(p[3])])))
    return atoms

def write_xyz(path, atoms, comment=""):
    with open(path, "w") as f:
        f.write(f"{len(atoms)}\n{comment}\n")
        for el, xyz in atoms:
            f.write(f"{el:<2s} {xyz[0]:16.8f} {xyz[1]:16.8f} {xyz[2]:16.8f}\n")

def embed_mol(smiles, name):
    mol = Chem.AddHs(Chem.MolFromSmiles(smiles))
    cids = AllChem.EmbedMultipleConfs(mol, numConfs=20, randomSeed=42, useRandomCoords=True)
    energies = []
    for cid in cids:
        ff = AllChem.MMFFGetMoleculeForceField(mol, AllChem.MMFFGetMoleculeProperties(mol), confId=cid)
        ff.Minimize(maxIts=2000)
        energies.append((ff.CalcEnergy(), cid))
    energies.sort()
    best_cid = energies[0][1]
    conf = mol.GetConformer(best_cid)
    atoms = []
    for atom in mol.GetAtoms():
        pos = conf.GetAtomPosition(atom.GetIdx())
        atoms.append((atom.GetSymbol(), np.array([pos.x, pos.y, pos.z])))
    charge = Chem.GetFormalCharge(mol)
    print(f"{name}: {len(atoms)} atoms, formal charge {charge}, MMFF E={energies[0][0]:.3f}")
    return atoms, charge, mol

def principal_axes_align(atoms):
    """Center at centroid and align so the molecule's flattest plane -> xy (for ring stacking)."""
    coords = np.array([a[1] for a in atoms])
    centroid = coords.mean(axis=0)
    coords -= centroid
    cov = coords.T @ coords
    evals, evecs = np.linalg.eigh(cov)
    # evecs columns sorted ascending eigenvalue: evecs[:,0] = smallest-variance axis -> molecular normal.
    # Reorder so that axis becomes the new z (columns 1,2 = the two larger-variance/in-plane axes -> new x,y).
    basis = evecs[:, [1, 2, 0]]
    coords = coords @ basis  # now local x,y = in-plane-ish, z = normal (smallest spread)
    return [(a[0], c) for a, c in zip(atoms, coords)]

def orient_chain_along_z(atoms, anchor_idx, far_idx):
    """Rotate so the anchor->far vector points along +z (anchor ends up at the bottom
    once placed, far end pointing away from the surface). Used for the Lys mimic,
    where the N-H3+ head (anchor), not a ring normal, is the contact group."""
    coords = np.array([a[1] for a in atoms])
    coords -= coords[anchor_idx]
    v = coords[far_idx]
    v = v / np.linalg.norm(v)
    z = np.array([0.0, 0.0, 1.0])
    axis = np.cross(v, z)
    s = np.linalg.norm(axis)
    c = np.dot(v, z)
    if s < 1e-8:
        R = np.eye(3) if c > 0 else -np.eye(3)
    else:
        axis /= s
        K = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
        R = np.eye(3) + K + K @ K * ((1 - c) / s**2)
    coords = coords @ R.T
    return [(a[0], c) for a, c in zip(atoms, coords)]

def place_above_cluster(mol_atoms, cluster_atoms, height, anchor_idx=None):
    """Translate mol so it sits `height` A above the cluster centroid (cluster is planar, z~0).
    If anchor_idx is given, that atom (already at local z=0 after orient_chain_along_z) is the
    one placed at `height`; otherwise the molecule's own centroid is used (ring-type ligands)."""
    cluster_xy = np.array([a[1][:2] for a in cluster_atoms if a[0] == "B"])
    site = cluster_xy.mean(axis=0)  # central adsorption site, away from the frozen perimeter
    coords = np.array([a[1] for a in mol_atoms])
    coords[:, 0] += site[0] - coords[:, 0].mean()
    coords[:, 1] += site[1] - coords[:, 1].mean()
    z_ref = coords[anchor_idx, 2] if anchor_idx is not None else coords[:, 2].mean()
    coords[:, 2] += height - z_ref
    return [(a[0], c) for a, c in zip(mol_atoms, coords)]

def freeze_list(cluster_atoms, relax_radius):
    """Return 0-indexed atom numbers to FREEZE (ORCA %geom Constraints atom numbering is
    0-based -- verified against C:\\orca_workspace\\flake_bare\\input.out, where explicit
    indices 1,2,3,6,8,... left atoms 0,4,5,7,... free): all H (edge passivation) + B atoms
    farther than relax_radius (in-plane) from the cluster centroid. Mirrors the flake_bare
    precedent (freeze rim + passivating H, relax a central patch). Cluster atoms are always
    written first (indices 0..N_cluster-1), both in the bare-cluster file and in the
    complex files, so this same list applies unmodified in both cases."""
    freeze = []
    for i, (el, xyz) in enumerate(cluster_atoms):
        r = np.hypot(xyz[0], xyz[1])
        if el == "H" or r > relax_radius:
            freeze.append(i)
    return freeze

def main():
    cluster = read_xyz(SRC_CLUSTER)
    write_xyz(f"{OUT}\\cluster_B60H24.xyz", cluster, "beta12 borophene B60H24 cluster (source: borophene-alzheimer-tau-ai, unmodified)")

    tyr_raw, tyr_q, _ = embed_mol("Cc1ccc(O)cc1", "p-cresol (Tyr mimic)")
    lys_raw, lys_q, lys_mol = embed_mol("CCCC[NH3+]", "n-butylammonium (Lys mimic)")

    n_idx = next(a.GetIdx() for a in lys_mol.GetAtoms() if a.GetSymbol() == "N")
    # terminal methyl carbon = the carbon farthest (graph distance) from N
    dmat = Chem.GetDistanceMatrix(lys_mol)
    c_idx = int(np.argmax([dmat[n_idx][i] if lys_mol.GetAtomWithIdx(i).GetSymbol() == "C" else -1
                            for i in range(lys_mol.GetNumAtoms())]))

    tyr_aligned = principal_axes_align(tyr_raw)          # ring plane -> parallel to xy, for pi-stacking on the surface
    lys_aligned = orient_chain_along_z(lys_raw, n_idx, c_idx)  # N-H3+ head down, alkyl tail pointing away from surface

    write_xyz(f"{OUT}\\tyr_pcresol.xyz", tyr_aligned, f"p-cresol, Tyr sidechain mimic, charge {tyr_q}")
    write_xyz(f"{OUT}\\lys_butylammonium.xyz", lys_aligned, f"n-butylammonium, Lys sidechain mimic, charge {lys_q}")

    tyr_placed = place_above_cluster(tyr_aligned, cluster, height=3.3)
    lys_placed = place_above_cluster(lys_aligned, cluster, height=3.2, anchor_idx=n_idx)  # N atom at the contact height

    complex_tyr = cluster + tyr_placed
    complex_lys = cluster + lys_placed
    write_xyz(f"{OUT}\\complex_tyr_initial.xyz", complex_tyr,
              f"beta12 B60H24 + p-cresol (Tyr mimic), initial guess, total charge {tyr_q}")
    write_xyz(f"{OUT}\\complex_lys_initial.xyz", complex_lys,
              f"beta12 B60H24 + n-butylammonium (Lys mimic), initial guess, total charge {lys_q}")

    RELAX_RADIUS = 4.6  # A, central patch left free (~24 B, ~40% of B60); rest of flake + all edge H frozen (flake_bare precedent)
    fz_cluster = freeze_list(cluster, RELAX_RADIUS)
    with open(f"{OUT}\\freeze_atoms_cluster_only.txt", "w") as f:
        f.write(f"# {len(fz_cluster)} of {len(cluster)} atoms frozen (relax_radius={RELAX_RADIUS} A)\n")
        f.write(",".join(str(i) for i in fz_cluster) + "\n")
    with open(f"{OUT}\\freeze_atoms_complex_tyr.txt", "w") as f:
        f.write(f"# same {len(fz_cluster)} cluster atoms frozen; ligand atoms ({len(tyr_placed)}) always free\n")
        f.write(",".join(str(i) for i in fz_cluster) + "\n")
    with open(f"{OUT}\\freeze_atoms_complex_lys.txt", "w") as f:
        f.write(f"# same {len(fz_cluster)} cluster atoms frozen; ligand atoms ({len(lys_placed)}) always free\n")
        f.write(",".join(str(i) for i in fz_cluster) + "\n")

    print(f"cluster: {len(cluster)} atoms, {len(fz_cluster)} frozen, {len(cluster)-len(fz_cluster)} free B in central patch")
    print(f"complex_tyr: {len(complex_tyr)} atoms total, charge {tyr_q}")
    print(f"complex_lys: {len(complex_lys)} atoms total, charge {lys_q}")

if __name__ == "__main__":
    main()
