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

## 3. Abstract  (paste as plain text — 241 words, within the 50–250 limit)

> Biomolecular condensates formed via liquid-liquid phase separation (LLPS) of the intrinsically disordered protein Tau are implicated in subcellular compartmentalization, yet dense condensates risk undergoing pathological cross-β amyloid transitions. Here, we establish a physics-based, coarse-grained statistical-thermodynamic and kinetic framework combining Flory-Huggins-Voorn-Overbeek (FH-VO) polymer theory with Langmuir interfacial adsorption, Cahn-Hilliard wetting theory, and mass-conserving master equations to investigate how two-dimensional (2D) nanomaterial biointerfaces modulate Tau LLPS and condensate aging. Calibrated against the experimental Lower Critical Solution Temperature (LCST) turbidity onset of Tau K18 (15.3 °C at 100 µM), the model demonstrates that 2D interface-mediated LLPS suppression emerges self-consistently from interfacial monomer sequestration governed by area density a_s (without empirical alterations to the intrinsic Flory parameter, ∂χ/∂a_s = 0). Using literature-informed representative parameter scenarios, a high-affinity borophene-like scenario (ΔG_ads = -7.8 kcal/mol, contact angle θ_c = 50.3°) shifts the apparent cloud point to 29.4 °C at a_s = 1.0×10⁻⁴ nm⁻¹, dissolving condensates across room and sub-physiological temperatures and depleting ~60% free monomer at 37 °C. In contrast, a moderate-affinity Ti3C2Tx MXene-like scenario (ΔG_ads = -5.2 kcal/mol, θ_c = 79.3°) produces modest depletion, maintaining stable droplet coexistence. Within a kinetic formulation that holds the intrinsic aggregation rate-law structure fixed, interfacial sequestration delays secondary-nucleation-driven aging. A converged global sensitivity analysis shows the apparent cloud point depending near-additively and comparably on the bulk-LCST parameters (β, Tc) and the interfacial parameters (ΔG_ads, a_s), whereas fibrillation arrest is governed almost entirely by area density a_s and extraction rate k_ext.

> Matches the manuscript abstract verbatim. If the portal's own counter reports >250 (some count hyphenated terms as two), drop the clause "whereas fibrillation arrest … extraction rate k_ext."

## 4. Keywords  (portal usually allows 4–8)

liquid-liquid phase separation; Tau protein; two-dimensional nanomaterials; biomolecular condensates; interfacial adsorption; Flory-Huggins-Voorn-Overbeek theory; Cahn-Hilliard wetting; global sensitivity analysis

## 5. Authors  (order, roles, affiliations)

| # | Name | Affiliation | Corresponding | ORCID |
|---|---|---|---|---|
| 1 | Andrés Monreal Hernández | Universidad Estatal de Sonora, Ley Federal del Trabajo s/n, 83100 Hermosillo, Sonora, Mexico | **YES** — andres.monreal@ues.mx | `‹FILL›` |
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

## 7. Suggested reviewers  (from the cover letter — confirm current affiliations/emails)

`‹the cover letter names 4 international suggested reviewers — copy names + emails into the portal fields; add institutional emails where the portal requires them›`

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
- **Acknowledgements / funding:** institutional support from Universidad Estatal de Sonora (UES) and Universidad de Sonora (UNISON). `‹add any CONACyT/SECIHTI scholarship or grant number here and in the manuscript Acknowledgements›`
- **Generative-AI declaration:** in the Acknowledgements — AI assistance used for code review, unit-test generation and manuscript formatting, all content verified under author responsibility; **all figures and the graphical abstract are deterministic matplotlib output with no AI-generated imagery.**

## 10. Portal confirmation checkboxes (typical RSC ScholarOne)

- [ ] The work is original and not published elsewhere
- [ ] Not under consideration by another journal
- [ ] All authors have approved the submission and agree to be listed
- [ ] Conflicts of interest declared (none)
- [ ] Data availability statement included
- [ ] Ethical statements — N/A (no human/animal subjects; purely computational)
- [ ] Generative-AI use declared
- [ ] Licence to Publish / open-access choice — `‹choose: standard Licence to Publish, or Gold open access if funded›`

## 11. Funding / open-access

Soft Matter is hybrid. `‹decide: (a) standard subscription route — free to publish; or (b) Gold OA APC — check if UNISON/UES has an RSC Read & Publish / transformative agreement that waives the APC (Mexico CONACyT consortia often do)›`
