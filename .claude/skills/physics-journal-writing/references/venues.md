# Physics Venues: Fit, Limits, and House Style

**Verify every number here against the journal's current author instructions before submitting.**
Limits and policies change; the figures below reflect guidelines as of mid-2026 and are given so you
can plan architecture, not so you can skip checking. When you have web access, fetch the author page.

## Contents

- [Choosing the venue](#choosing-the-venue)
- [APS: Physical Review family](#aps-physical-review-family)
- [Nature family](#nature-family)
- [AIP Publishing](#aip-publishing)
- [Optics: Optica Publishing Group](#optics-optica-publishing-group)
- [IOP Publishing](#iop-publishing)
- [High-energy physics](#high-energy-physics)
- [Astronomy and astrophysics](#astronomy-and-astrophysics)
- [Elsevier and others](#elsevier-and-others)
- [Adapting a draft between venues](#adapting-a-draft-between-venues)

---

## Choosing the venue

Three questions decide it:

1. **Who needs to read this?** If the result changes what non-specialists do, a broad venue (PRL,
   PRX, Nature Physics) is defensible. If it advances a subfield's toolkit or database, a specialist
   journal (PRB, JAP, ApJS) serves the work better and gets a fairer review.
2. **Can the argument survive compression?** A Letter must be complete in ~3750 words with three or
   four figures. If the evidence requires six figures and a derivation, either the Letter is not the
   right form or the supporting material genuinely belongs in End Matter/Supplemental Material.
3. **What is the field's default?** Cond-mat → PRB/PRL; quantum information → PRX Quantum, Quantum,
   PRL; optics → Optica/OL/OE; applied/devices → APL/JAP/ACS journals; plasma → PoP/PRL/NF;
   HEP experiment → PRL/PRD/JHEP; astro → ApJ/MNRAS/A&A. Submitting outside the default needs a
   reason you can state in the cover letter.

Aim for the venue whose readership makes the result useful, not the highest impact factor you can
plausibly reach. A well-placed PRB beats a PRL rejected twice and published a year late.

---

## APS: Physical Review family

Preferred format: **REVTeX 4.2**. Citation style: numbered, in square brackets `[1]` (superscript in
some substyles). Tables numbered with Roman numerals (Table I, Table II). Sections numbered with
Roman numerals in Articles.

### Physical Review Letters (PRL)

The most constrained physics venue and the one most often mishandled.

| Constraint | Value |
|---|---|
| Article types | Letters only |
| Main text | ~3750 words / ~4 journal pages, whichever binds first |
| Word count includes | body text, displayed equations (word-equivalent), figure captions, table text, footnotes |
| Word count excludes | title, author list, abstract, acknowledgments, references |
| Figure cost | each figure consumes word budget (~170 words for a single-column figure; larger for two-column) |
| Abstract | **600 characters including spaces** — not words |
| End Matter | up to 2 additional pages of appendices, peer-reviewed, published after the references |
| Supplemental Material | unlimited length, published online, read by referees |
| Typical figures | 3–4 |
| Justification | a short statement (~100 words) on why the result merits PRL's broad readership |

Editorial reality: PRL screens for *impact, innovation, and interest* before it screens for
correctness. A correct, careful, incremental result gets desk-rejected. The cover letter and the
justification statement must argue for generality — one sentence stating the consequence for
physicists outside the immediate specialty.

Structural implications: no room for a literature review; the introduction is two or three
paragraphs; the first figure should already be evidence for the headline claim; derivations go to
End Matter (specialist-essential) or Supplemental Material (neither general nor essential).

PRL also asks that all but the simplest equations be displayed rather than inline, that acronyms be
avoided or defined, and that new terminology not be introduced in the title.

### Physical Review X (PRX)

No hard length limit; long, thorough papers are welcome. Requires a **popular summary** written for
a general audience and a statement of significance. Selectivity is comparable to or above PRL but
the format allows the full argument. Good home for a result that is important *and* needs space.

### PRX Quantum

The APS flagship for quantum information, computing, simulation, sensing, and quantum-enabled
technology. Treat it as a distinct venue rather than "PRX for quantum":

- **No hard length limit**, like PRX. The constraint is relevance and rigor, not word count; papers
  routinely run long with substantial appendices.
- Requires a **popular summary** — a short non-technical account of why the result matters. Write it
  for a physicist's non-physicist colleague; leftover jargon here is a common revision request.
- Scope is deliberately broad across the quantum stack: hardware, architecture, algorithms, error
  correction, control, metrology, foundations, and quantum-relevant condensed matter. Systems-level
  or interdisciplinary work that falls awkwardly between PRA and PRApplied often fits here.
- Publishes **Perspectives and Tutorials** as well as research articles — an option most APS
  journals lack.
- Expectations that surface in referee reports: benchmarking against the best published numbers
  (gate and SPAM fidelities, coherence times, logical error rates, sampling-advantage claims) in an
  explicit comparison table; clear separation of measured performance from projected or simulated
  performance; honest accounting of what was calibrated, post-selected, or error-mitigated.

### Physical Review A, B, C, D, E, Applied, Materials, Fluids, Research

Full Articles with numbered sections and no restrictive length limit (though editors push back on
padding). Letters are also published in several of these journals with their own page limits
(roughly 4 pages for PRB, 5 for PRA/C/D/E/Fluids/Materials/Research — confirm current values).

House expectations: complete methods, explicit appendices for derivations, thorough referencing of
prior work in the subfield. Referees expect reproducibility, not novelty framing.

### Physical Review Research

Broad-scope open access, less stringent on "general interest" than PRL, still expects a clear
advance. Reasonable target for solid interdisciplinary work.

### Reviews of Modern Physics

Invitation-oriented, book-length reviews. Not a normal submission target.

---

## Nature family

*Nature*, *Nature Physics*, *Nature Photonics*, *Nature Materials*, *Nature Communications*,
*Communications Physics*.

- Main text is narrative and largely **without section headings**; the full experimental and
  computational detail lives in a **Methods** section after the main text, plus **Extended Data**
  figures and Supplementary Information.
- Main text typically ~2500–3000 words with 4–5 display items (confirm current limits per journal).
- Abstract is a single unstructured paragraph, written for a broad readership; the opening sentences
  must be intelligible to a physicist outside the field.
- Editorial pre-screening is heavy: a presubmission enquiry is often worthwhile.
- Style: fewer symbols in the abstract, more emphasis on why the result matters, less on formalism.
  Reference lists are capped in the main text (Nature Physics typically ~50); Methods references are
  separate.
- Required at submission: reporting summary, data availability, code availability, author
  contributions, competing interests.

Writing implication: the same result written for PRL and for Nature Physics needs genuinely
different prose. Nature-family framing leads with the phenomenon and its significance; APS framing
leads with the physics and quantifies immediately.

---

## AIP Publishing

*Applied Physics Letters* (APL), *Journal of Applied Physics* (JAP), *Review of Scientific
Instruments* (RSI), *Physics of Fluids*, *Physics of Plasmas*, *Journal of Chemical Physics*,
*APL Materials/Photonics/Quantum*.

- Format: **REVTeX 4.2 with AIP substyles** (`aip` class option plus the journal substyle, e.g.
  `apl`, `jap`, `rsi`, `pof`, `pop`). Citations are typically **superscript numbers**.
- APL: short (roughly 3500 words / ~4–5 pages including figures — confirm), applied framing,
  benchmarking against prior device performance expected.
- RSI: instrument papers. Reproducibility of the *apparatus* is the review criterion — dimensions,
  tolerances, materials, control electronics, calibration, and measured performance specs.
- JAP / PoF / PoP: full-length, numbered sections, thorough methods.

---

## Optics: Optica Publishing Group

*Optica*, *Optics Letters*, *Optics Express*, *Applied Optics*, *Photonics Research*, *JOSA A/B*.

- *Optics Letters*: very short (roughly 3.5 published pages; confirm). Compressed, system-focused.
- *Optics Express*: no strict length limit, rapid, widely read.
- *Optica*: flagship, high selectivity, longer than OL with section headings.
- Convention: a system schematic as Fig. 1 is near-universal and expected. Report source
  wavelengths, powers, pulse durations, repetition rates, NA, and detector specifications precisely.
- Templates available for LaTeX (`osajnl`/Optica class) and Word.

---

## IOP Publishing

*New Journal of Physics*, *Journal of Physics A/B/C/D*, *Reports on Progress in Physics*,
*Nuclear Fusion*, *Quantum Science and Technology*, *2D Materials*, *Plasma Physics and Controlled
Fusion*.

- Format: `iopart` LaTeX class. Numbered references in square brackets; some journals use
  author–year (`iopart-num` vs Harvard variants — check).
- NJP: broad scope, open access, no strict length limit, expects a clear statement of significance.
- J. Phys. A: mathematical physics conventions; long derivations are welcome and expected inline.

---

## Quantum information, computing, and technology

This area spans APS, Nature, IOP, and independent open-access venues, and the choice is less obvious
than in most subfields because scope overlaps heavily. Sorting by *what kind of claim you are making*
works better than sorting by prestige.

| Venue | Publisher | Length | Best fit |
|---|---|---|---|
| **PRX Quantum** | APS | unlimited | Substantial advances anywhere in the quantum stack; systems-level work; tutorials and perspectives. Popular summary required |
| **PRL** | APS | ~3750 words | A single striking quantum result with broad physics interest |
| **Physical Review A** | APS | unlimited | Core quantum optics, AMO, foundations, quantum information theory. The default specialist home for theory |
| **Physical Review Applied** | APS | unlimited | Device- and application-facing quantum engineering: qubit hardware, control electronics, sensors, materials for qubits |
| **Physical Review B** | APS | unlimited | Solid-state qubit physics, superconducting circuits and spin qubits treated as condensed matter |
| **Physical Review Research** | APS, OA | unlimited | Solid quantum work of broad scope without the PRX Quantum selectivity bar |
| **Quantum** | independent, OA | unlimited | Community-run, arXiv-native, strong in quantum information theory, algorithms, and complexity. `quantumarticle` class; overlay-journal workflow |
| **npj Quantum Information** | Nature Portfolio, OA | ~article length | Broad quantum information advances; Nature-family framing and Methods-at-end structure |
| **Quantum Science and Technology (QST)** | IOP | unlimited | Quantum technology and engineering; `iopart` class |
| **Nature Physics / Nature Photonics / Nature** | Nature | ~3000 words | Results whose significance a non-specialist physicist can be made to feel |
| **Optica / Optics Express / PRApplied** | Optica / APS | varies | Photonic quantum hardware where the optics is the contribution |
| **New Journal of Physics** | IOP, OA | unlimited | Broad-scope quantum work; established, well-read |
| **SciPost Physics** | independent, OA | unlimited | Open, named refereeing; strong reproducibility norms; growing in quantum many-body and information |

Conventions that cut across all of these:

- **arXiv `quant-ph` is the field's primary channel.** Posting at submission is the norm; the
  community reads the listing daily and papers accumulate citations before acceptance. Choose
  `quant-ph` as primary unless the work is genuinely more cond-mat or physics.optics, and cross-list
  sparingly. *Quantum* is built around this workflow explicitly.
- **Benchmarking tables are near-mandatory** when claiming hardware or algorithmic improvement.
  Report your number next to the best prior numbers with references and platform. A novelty claim
  without this table gets challenged in the first referee round.
- **Separate what was measured from what was inferred.** State plainly which fidelities are raw,
  which are post-selected, which use error mitigation, and which are extrapolated. This is the single
  most scrutinized point in quantum hardware papers.
- **Resource accounting** for algorithmic and error-correction claims: qubit counts, circuit depth,
  gate counts by type, connectivity assumptions, classical pre/post-processing cost, and the noise
  model with its parameters.
- **Foundations and interpretation papers** need extra care that the claim is operational — what
  experiment would distinguish the position — since editors at PRA and Quantum screen hard for this.

## High-energy physics

*JHEP*, *Physical Review D*, *Physics Letters B*, *European Physical Journal C*, *SciPost Physics*.

- **arXiv is the primary distribution channel**; the journal version follows. Post to `hep-ph`,
  `hep-th`, `hep-ex`, or `hep-lat` with careful primary-category selection.
- Author lists in large collaborations are alphabetical; individual contribution statements are
  usually absent. Collaboration papers list the collaboration as author with the roster in an
  appendix.
- References use `inspire`-generated BibTeX with eprint numbers; cite the arXiv identifier alongside
  the journal reference.
- Conventions: natural units (ħ = c = 1) declared once; metric signature stated; Feynman diagram
  conventions specified; blind analysis and look-elsewhere corrections described explicitly in
  experimental searches.
- SciPost uses open, named refereeing — the report and reply are public, which raises the bar on the
  response letter.

---

## Astronomy and astrophysics

*ApJ*, *ApJL*, *ApJS*, *AJ*, *PSJ*, *RNAAS* (AAS journals); *MNRAS*; *A&A*.

This subfield diverges most from the rest of physics:

- **Citations are author–year**, not numbered: `(Smith et al. 2022)` / `Smith et al. (2022)`. AAS
  journals now include first initials in inline citations (e.g., "G. Smith et al. (2022)").
- **AASTeX v7** is the current AAS class file (v7.0.x; earlier v6.3.1 still circulates). It requires
  an **email address for every author** and provides a dedicated author-contributions environment.
  MNRAS uses `mnras.cls`; A&A uses `aa.cls`.
- Structure is closest to conventional IMRAD with numbered sections, plus long appendices.
- Machine-readable tables, figure sets, and data behind figures are first-class deliverables; ApJ
  expects large tables in machine-readable format with a sample shown in the article.
- Software and datasets are cited as first-class references (with DOIs, e.g., via Zenodo/ASCL).
- Dual-anonymous review is used at AAS journals: anonymize acknowledgments and self-references in
  the submitted version.
- Units: CGS and astronomical units (erg, Gauss, parsec, M⊙, Jy, magnitudes) remain standard —
  do not "fix" these to SI.

---

## Elsevier and others

*Physics Letters A/B*, *Nuclear Instruments and Methods (NIM A/B)*, *Ultramicroscopy*,
*Journal of Magnetism and Magnetic Materials*: `elsarticle` class, numbered references, structured
abstract sometimes permitted but not typical in physics.

*Quantum* (quantum.open): open access, `quantumarticle` class, arXiv-native workflow.

*SciPost Physics*: open peer review, `SciPost` class, strong expectations on reproducibility.

---

## Adapting a draft between venues

Moving a manuscript between venues is not reformatting; it is rewriting the argument's frame.

| From → To | What actually has to change |
|---|---|
| PRB Article → PRL | Cut ~60% of text; move derivations to End Matter, extended data to Supplemental Material; rewrite the introduction to argue broad significance; compress the abstract to 600 characters; reduce to 3–4 figures |
| PRL → Nature Physics | Add a Methods section with full detail; de-emphasize formalism in the main text; rewrite the opening for a non-specialist physicist; add reporting/data/code statements and author contributions |
| Nature Physics → PRB | Reintegrate Methods into a numbered section; restore equations and derivations to the main text; expand the referencing of subfield prior work; drop the broad-significance framing |
| APS → AAS journal | Convert numbered citations to author–year and rebuild the bibliography; switch REVTeX → AASTeX; convert SI to CGS/astronomical units if that is the subfield norm; add machine-readable tables |
| Any → arXiv-only preprint | Nothing removed, but add explicit version notes, choose the primary category carefully, and pick a license |

Always rebuild the bibliography with the target's `.bst` rather than hand-editing entries; hand
conversion between numbered and author–year styles reliably introduces errors.
