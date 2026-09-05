# Soft Matter submission — pre-flight checklist

## Ready ✔

| Item | Status |
|---|---|
| Article type = Paper | ✔ |
| Title | ✔ |
| Abstract 50–250 words | ✔ 241 words |
| Manuscript: Word, figures embedded | ✔ `Manuscript.docx` |
| 5 figures as separate vector PDF (RSC accepts PDF/EPS vs TIFF 600 dpi) | ✔ `Figure1–5.pdf` |
| 600 dpi TIFFs available if editor asks | ✔ `figures/*.tif` from `run_pipeline.py` |
| Graphical abstract image ≤ 8 cm × 4 cm, 600 dpi TIFF | ✔ `GraphicalAbstract.tif` |
| Graphical abstract text ≤ 250 characters, editable .docx | ✔ `GraphicalAbstract_text.docx` (218 chars) |
| Cover letter with impact statement | ✔ `CoverLetter.docx` |
| Conflicts of interest statement | ✔ in manuscript ("none") |
| Data availability statement (after conflicts) | ✔ in manuscript, Zenodo DOI 10.5281/zenodo.22268507 |
| Author contributions (CRediT) | ✔ in manuscript |
| Acknowledgements + funding | ✔ (no funding, no institutional support) |
| Generative-AI declaration (incl. figures not AI-generated) | ✔ in Acknowledgements |
| References numbered and complete (RSC typesets house style on acceptance) | ✔ 31 refs, numeric |
| Ethics statements | N/A — purely computational, no human/animal data |

## Needs a value only you have ✎

- [x] ~~ORCID for the corresponding author~~ — 0009-0009-1207-8597 (Andrés Monreal Hernández), now in PORTAL_FIELDS.md / CITATION.cff / .zenodo.json. Co-authors' ORCID still optional/unfilled.
- [x] ~~Suggested reviewers: institutional emails~~ — filled in `PORTAL_FIELDS.md` §7 (from the cover letter); just double-check none has a conflict of interest with the authors
- [x] ~~Funding~~ — none; manuscript states "no specific grant ... and no institutional support"
- [x] ~~Open-access choice~~ — **standard Licence to Publish** (free, no APC). Does not affect acceptance odds or journal/quartile. Code/data already open via Zenodo regardless.
- [ ] Confirm all four co-authors have seen and approved this version

## Optional polish (not blockers)

- In-text citations are bracketed numeric `[5,6]`; RSC house style is superscript. Fine for review — RSC typesets on acceptance. Convert only if a co-author prefers.
- `figures/Graphical_Abstract.png` in the repo is an orphan (older hand-made asset, not used in the submission — the submission uses `TOC_Graphic_RSC_Soft_Matter`). Leave or delete.

## Do this in the portal

1. Log in to https://mc.manuscriptcentral.com/softmatter (RSC account / ORCID).
2. New submission → Paper → paste fields from `PORTAL_FIELDS.md`.
3. Upload the 9 files from `submission/upload/` with the designations in `PORTAL_FIELDS.md` §8.
4. Tick the confirmation checkboxes (§10).
5. Review the PDF proof the system builds, then submit.
