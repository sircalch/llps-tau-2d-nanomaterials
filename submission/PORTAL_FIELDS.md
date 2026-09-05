# Soft Matter (RSC) — submission portal fields

Journal submission system: **RSC ScholarOne** (https://mc.manuscriptcentral.com/softmatter).
Everything below is ready to paste. Items marked `‹FILL›` need a value only you have.

Regenerate the upload bundle any time with:

```bash
python scratch/build_submission_package.py
```

Files land in `submission/upload/` (git-ignored, regenerable).

---

## 1. Article type

**Paper** (standard full research article; not a Communication).

## 2. Title

> Thermodynamic modulation of Tau liquid-liquid phase separation and condensate wetting by two-dimensional nanomaterial interfaces: emergent suppression via adsorption equilibrium

## 3. Abstract  (paste as plain text — 245 words, within the 50–250 limit)

> Biomolecular condensates formed via liquid-liquid phase separation (LLPS) of the intrinsically disordered protein Tau are implicated in subcellular compartmentalization, yet dense condensates are prone to pathological cross-β amyloid transitions. Here we establish a coarse-grained statistical-thermodynamic and kinetic framework that combines Flory-Huggins-Voorn-Overbeek (FH-VO) polymer theory with Langmuir interfacial adsorption, Cahn-Hilliard wetting theory, and mass-conserving master equations to investigate how two-dimensional (2D) nanomaterial biointerfaces modulate Tau LLPS and condensate aging. Calibrated against the experimental Lower Critical Solution Temperature (LCST) turbidity onset of Tau K18 (15.3 °C at 100 µM), the model shows that 2D interface-mediated LLPS suppression emerges self-consistently from interfacial monomer sequestration governed by area density a_s (without empirical alterations to the intrinsic Flory parameter, ∂χ/∂a_s = 0). Using literature-informed representative parameter scenarios, a high-affinity borophene-like scenario (ΔG_ads = -7.8 kcal/mol, contact angle θ_c = 50.3°) shifts the apparent cloud point to 29.4 °C at a_s = 1.0×10⁻⁴ nm⁻¹, dissolving condensates at room and sub-physiological temperatures and depleting ~60% of the free monomer at 37 °C. In contrast, a moderate-affinity Ti3C2Tx MXene-like scenario (ΔG_ads = -5.2 kcal/mol, θ_c = 79.3°) produces modest depletion, maintaining stable droplet coexistence. Within a kinetic formulation that holds the intrinsic aggregation rate-law structure fixed, interfacial sequestration delays secondary-nucleation-driven aging. A converged global sensitivity analysis shows that the apparent cloud point depends near-additively and comparably on the bulk-LCST parameters (β, Tc) and the interfacial parameters (ΔG_ads, a_s), whereas fibrillation arrest is governed almost entirely by area density a_s and extraction rate k_ext.

> Matches the manuscript abstract verbatim. If the portal's own counter reports >250 (some count hyphenated terms as two), drop the clause "whereas fibrillation arrest … extraction rate k_ext."

## 4. Keywords  (portal usually allows 4–8)

liquid-liquid phase separation; Tau protein; two-dimensional nanomaterials; biomolecular condensates; interfacial adsorption; Flory-Huggins-Voorn-Overbeek theory; Cahn-Hilliard wetting; global sensitivity analysis

## 5. Authors  (order, roles, affiliations)

| # | Name | Affiliation | Corresponding | ORCID |
|---|---|---|---|---|
| 1 | Andrés Monreal Hernández | Universidad Estatal de Sonora, Ley Federal del Trabajo s/n, 83100 Hermosillo, Sonora, Mexico | **YES** — andres.monreal@ues.mx | 0009-0009-1207-8597 |
| 2 | Jesús Martín Muñoz Bautista | Departamento de Investigación y Posgrado en Alimentos (DIPA), Universidad de Sonora, Blvd. Luis Encinas y Rosales, 83000 Hermosillo, Sonora, Mexico | no | `‹FILL / optional›` |
| 3 | Sara Lizbeth Franco Amaya | Doctorado en Nanotecnología, Departamento de Física, Universidad de Sonora, Blvd. Luis Encinas y Rosales, 83000 Hermosillo, Sonora, Mexico | no | `‹FILL / optional›` |
| 4 | Carlos Ivanhoe Martínez Osorio | Doctorado en Ciencia de Materiales, Departamento de Investigación en Polímeros y Materiales (DIPM), Universidad de Sonora, 83000 Hermosillo, Sonora, Mexico | no | `‹FILL / optional›` |

CRediT roles (also in the manuscript "Author Contributions" section):
- **A.M.H.** — Conceptualization, Methodology, Formal analysis, Software, Investigation, Writing – original draft
- **J.M.M.B.** — Methodology, Validation, Writing – review & editing
- **S.L.F.A.** — Investigation, Data curation, Validation, Writing – review & editing
- **C.I.M.O.** — Formal analysis, Supervision, Validation, Writing – review & editing

## 6. Cover letter

Upload `submission/upload/CoverLetter.docx` (or paste its text). It already contains the
required "importance and/or impact" statement, the thematic-fit argument, the four
computational milestones, the GenAI disclosure and four suggested reviewers.

## 7. Suggested reviewers  (from the cover letter)

| Name | Affiliation | Expertise | Email |
|---|---|---|---|
| Prof. Rohit V. Pappu | Washington University in St. Louis | Intrinsically disordered proteins, polymer physics of biomolecular condensates, phase behavior | pappu@wustl.edu |
| Prof. Tuomas P. J. Knowles | University of Cambridge | Protein aggregation kinetics, biomolecular phase transitions, amyloid nucleation theory | tpjk2@cam.ac.uk |
| Prof. Yury Gogotsi | Drexel University | 2D nanomaterials, MXene surface chemistry, nanomaterial-biomolecule interfaces | gogotsi@drexel.edu |
| Dr. Roland L. Knorr | Max Planck Institute of Colloids and Interfaces | Biomolecular condensate wetting, interfacial tension, membrane interactions | roland.knorr@mpikg.mpg.de |

None of the four have a known conflict of interest with the authors (no shared institution, no recent co-authorship). Confirm this yourself before submitting — that check is only reliable on your side.

Opposed reviewers: none.

## 8. Files to upload  (in `submission/upload/`)

| Portal designation | File | Notes |
|---|---|---|
| Main Document | `Manuscript.docx` | Word, figures embedded, Vancouver-numbered references |
| Figure | `Figure1.pdf` … `Figure5.pdf` | vector PDF (RSC accepts PDF/EPS instead of TIFF 600 dpi) |
| Graphical Abstract (image) | `GraphicalAbstract.tif` (600 dpi, 8 cm × 4 cm) or `GraphicalAbstract.pdf` | |
| Graphical Abstract (text) | `GraphicalAbstract_text.docx` | editable .docx, ≤250 characters |
| Cover Letter | `CoverLetter.docx` | |

High-resolution 600 dpi TIFFs of every figure are produced by `run_pipeline.py`
(`figures/*.tif`, git-ignored, ~90–185 MB each) if the editor requests TIFF instead of PDF.

## 9. Statements already inside the manuscript (portal may also ask to paste them)

- **Conflicts of interest:** "There are no conflicts to declare."
- **Data availability:** code and data openly on GitHub (https://github.com/sircalch/llps-tau-2d-nanomaterials, MIT) and permanently archived on Zenodo, DOI **10.5281/zenodo.22268507** (release v1.0.1).
- **Author contributions:** CRediT, see §5 above.
- **Acknowledgements / funding:** "This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors, and no institutional support." Leave the portal's Funder field empty / select "no funding".
- **Generative-AI declaration:** in the Acknowledgements — "Generative AI tools (large language models) were used to assist with code development, testing, and language editing; no figure, including the graphical abstract, contains AI-generated imagery. All models, analyses, results, and citations were designed, verified, and approved by the authors, who take full responsibility for the content."

## 10. Portal confirmation checkboxes (typical RSC ScholarOne)

- [ ] The work is original and not published elsewhere
- [ ] Not under consideration by another journal
- [ ] All authors have approved the submission and agree to be listed
- [ ] Conflicts of interest declared (none)
- [ ] Data availability statement included
- [ ] Ethical statements — N/A (no human/animal subjects; purely computational)
- [ ] Generative-AI use declared
- [ ] Licence to Publish / open-access choice — **Standard Licence to Publish** (subscription route, no APC)

## 11. Funding / open-access

**Decision: standard Licence to Publish, not Gold OA.** No funding to cover an APC (~$2,500–3,000 USD), so Gold OA is not an option here — the standard subscription route is free. The OA choice has zero effect on peer-review/acceptance; it only affects who can read the published PDF for free on day one. The code/data are already open via GitHub + Zenodo regardless of this choice, and RSC's standard policy allows self-archiving the accepted author manuscript after an embargo (Green OA) if open access is wanted later at no cost.
