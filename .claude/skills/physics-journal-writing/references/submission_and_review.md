# LaTeX, arXiv, Submission, and Referee Response

## Contents

- [Choosing the class file](#choosing-the-class-file)
- [REVTeX 4.2 essentials](#revtex-42-essentials)
- [AASTeX v7 essentials](#aastex-v7-essentials)
- [Bibliography](#bibliography)
- [Supplemental Material vs. End Matter vs. Appendices](#supplemental-material-vs-end-matter-vs-appendices)
- [arXiv](#arxiv)
- [Cover letters](#cover-letters)
- [Responding to referees](#responding-to-referees)
- [Reviewing someone else's physics manuscript](#reviewing-someone-elses-physics-manuscript)

---

## Choosing the class file

| Publisher / journals | Class | Notes |
|---|---|---|
| APS (PRL, PRX, PRA–E, PRResearch, PRX Quantum) | `revtex4-2` with `aps` option and journal substyle (`prl`, `prb`, `prx`, …) | current release is REVTeX 4.2; submit under the `preprint` option |
| AIP (APL, JAP, RSI, PoF, PoP, JCP) | `revtex4-2` with `aip` option and substyle (`apl`, `jap`, `rsi`, `pof`, `pop`) | citations usually superscript numbers |
| AAS (ApJ, AJ, ApJS, ApJL, PSJ, RNAAS) | `aastex7` (v7.0.x) | requires an email for every author; author-contributions environment available |
| MNRAS | `mnras` | |
| A&A | `aa` | |
| IOP (NJP, J. Phys. A–D, QST, NF) | `iopart` | |
| Optica Publishing Group | Optica/OSA journal class | |
| Elsevier (Phys. Lett., NIM) | `elsarticle` | |
| Nature family | Nature LaTeX template or Word | Word is genuinely common here |
| SciPost | `SciPost` | open refereeing |
| Quantum | `quantumarticle` | arXiv-native |

Verify the current version on the publisher's site — class files are updated and old versions are
sometimes rejected by submission systems.

---

## REVTeX 4.2 essentials

```latex
\documentclass[
  aps,prl,           % society and journal substyle
  reprint,           % two-column preview; use 'preprint' for submission
  amsmath,amssymb,
  superscriptaddress % or groupedaddress
]{revtex4-2}

\usepackage{graphicx}
\usepackage{bm}          % \bm for bold math (vectors)
\usepackage{siunitx}     % units and uncertainties
\usepackage{dcolumn}     % decimal-aligned table columns
\usepackage{booktabs}
\usepackage{hyperref}

\begin{document}

\title{Declarative statement of the result}

\author{A. Author}
\email{corresponding@institution.edu}
\affiliation{Department of Physics, University, City, Country}
\author{B. Author}
\affiliation{Second Institution, City, Country}

\date{\today}

\begin{abstract}
  Single paragraph. For PRL, 600 characters including spaces. No citations,
  no undefined acronyms, no references to figures.
\end{abstract}

\maketitle          % note: after the abstract in REVTeX

\section{Introduction}
...

\begin{acknowledgments}
  ...
\end{acknowledgments}

\appendix
\section{Derivation of Eq.~(4)}
...

\bibliography{refs}
\end{document}
```

Points authors get wrong:

- **Submit with the `preprint` option**, not `twocolumn`/`reprint` — APS converts anyway, and the
  single-column form is what referees read. Use `reprint` locally to check the true page count.
- `\maketitle` comes **after** the abstract environment in REVTeX, not before.
- Use `\cite`/`\bibitem` (or BibTeX); never hand-numbered references.
- Keep author-defined macros minimal and include them in the submitted source.
- `widetext` environment for equations too wide for a column.
- For a PRL, End Matter is a specific journal feature placed after the references — check the current
  markup APS specifies rather than improvising with `\appendix`.
- `\nonumber` on unreferenced lines of an `align` block to avoid numbering clutter.

---

## AASTeX v7 essentials

```latex
\documentclass[twocolumn]{aastex7}

\begin{document}
\title{Declarative title}

\author[0000-0000-0000-0000]{A. Author}
\affiliation{Department of Astronomy, University, City, Country}
\email[show]{corresponding@institution.edu}   % email required for EVERY author in v7+

\begin{abstract}
Single paragraph.
\end{abstract}

\keywords{...}

\section{Introduction} \label{sec:intro}
Citation forms: \citet{smith2022} $\to$ ``G. Smith et al. (2022)'';
\citep{smith2022} $\to$ ``(G. Smith et al. 2022)''.

\begin{acknowledgments}
...
\end{acknowledgments}

\bibliography{refs}
\end{document}
```

- v7 **fails to compile** if any author lacks an email — this is intentional.
- Author-contribution environment is available and anonymized under dual-anonymous review.
- Large tables: publish machine-readable, with a representative excerpt shown in the article and a
  `\tablecomments{}` note saying so.
- Cite software and datasets as references (ASCL, Zenodo DOIs).
- **Dual-anonymous review**: anonymize acknowledgments, funding, facility names where they identify,
  and phrase self-citations in the third person ("Smith et al. (2022) showed", not "in our previous
  work").

---

## Bibliography

- Use BibTeX/BibLaTeX with the publisher's `.bst`; never hand-format entries and never hand-convert
  between numbered and author–year styles.
- Physics BibTeX entries should carry the **arXiv eprint number** alongside the journal reference —
  many readers will follow the preprint. INSPIRE, NASA ADS, and journal export tools produce
  correctly formatted entries; prefer these over Google Scholar exports, which are error-prone with
  physics journal abbreviations.
- Journal abbreviations follow the target's style (APS uses "Phys. Rev. B"; AAS uses ADS macros like
  `\apj`). The `.bst` handles this if the entries are complete.
- Cite the version of any software you used, with a DOI where one exists.
- Balance: introduction and discussion carry most citations; a Letter typically has 25–40 references
  (which count against nothing at PRL but consume page space), an Article 50–100, a review far more.
- **Verify every citation actually supports the sentence it's attached to.** Do not cite from memory
  or from another paper's reference list; check the source. Never invent a DOI or arXiv number.

---

## Supplemental Material vs. End Matter vs. Appendices

Getting this allocation right is what makes a Letter feasible.

| Destination | Contents | Read by |
|---|---|---|
| **Main text** | the claim, the evidence, the minimum needed to believe it | everyone |
| **End Matter** (PRL) | material specialists need: key derivation steps, essential systematic checks | specialists; peer-reviewed and typeset |
| **Appendices** (Articles) | derivations, notation tables, extended methods, secondary datasets | specialists |
| **Supplemental Material** | everything else: raw data, extended parameter sweeps, additional device data, videos, code listings | referees and interested readers |

Rules:

- Supplemental Material is **reviewed**. It must be organized, captioned, and referenced from the
  main text at specific points ("see Sec. S3 of the Supplemental Material [ref]"), not dumped.
- Nothing load-bearing goes in Supplemental Material. If the claim fails without it, it belongs in
  the main text.
- Number supplemental figures and sections separately (Fig. S1, Sec. S2).
- Include the Supplemental Material in the citation list as the journal specifies.

---

## arXiv

Physics is arXiv-first. Posting is normal and, in most subfields, expected.

- **Timing**: posting at submission is standard in HEP, astro, cond-mat, and quant-ph. A few journals
  and some collaborations have policies; check yours. No physics journal treats arXiv posting as
  prior publication.
- **Primary category** determines who sees it in the daily listing — pick the one your intended
  readers scan (e.g. `cond-mat.mes-hall`, `quant-ph`, `astro-ph.CO`, `hep-ex`, `physics.optics`), and
  cross-list to at most one or two others. Over-cross-listing is noticed and disliked by moderators.
- **Abstract**: arXiv's abstract field is plain text — convert LaTeX math to readable ASCII/Unicode.
- **Title and abstract on arXiv are permanent**; versions accumulate rather than replace.
- **License**: choose deliberately (arXiv's default non-exclusive license vs. CC-BY). CC-BY is
  required by some funders and enables reuse; it cannot be revoked.
- **Comments field**: page count, figure count, and journal reference once accepted. Update the
  journal reference after publication — it improves discoverability and citation linking.
- Post the **accepted version** as a new version if the journal's policy allows; note in the comments
  which version corresponds to the published article.

---

## Cover letters

Short, one page, addressed to the editor. Its job is to answer "why this journal, why now".

Structure:

1. One sentence: what the paper reports, with the number.
2. Two or three sentences: why it matters beyond the immediate specialty — the case for the venue's
   readership. This is the paragraph PRL's justification statement duplicates; make it a real
   argument, not an adjective ("this is of broad interest" is not an argument).
3. One or two sentences: what is new relative to the closest prior work, naming it.
4. Housekeeping: originality and non-concurrent-submission statement, suggested referees (with
   affiliations and a one-line reason), any excluded referees with a professional reason, related
   manuscripts under consideration elsewhere, arXiv identifier.

Do not summarize the abstract at length, do not list every result, do not claim significance the
paper does not establish. Editors read hundreds of these; specificity is the only thing that stands
out.

---

## Responding to referees

The response letter is a separate document and it is read closely. Most rejections after revision
come from a defensive or evasive response, not from the physics.

**Format**: point-by-point. Quote each referee comment verbatim (in italics or a shaded box), then
respond, then state the change made and where — with the revised text quoted and page/line or
section reference. Track changes or colored text in the revised manuscript.

**Structure of the letter:**

1. Brief opening thanking the referees, noting the main changes in two or three sentences.
2. Response to Referee 1, comment by comment.
3. Response to Referee 2, comment by comment.
4. List of all changes, if the journal wants one separately.

**Principles:**

- **Answer every point**, including the ones you disagree with and the ones you consider trivial.
  A skipped comment is the fastest route to a second round.
- **Change the manuscript wherever you can.** "We have clarified this in the text" with the new text
  quoted is worth more than three paragraphs of explanation in the letter alone. If a referee
  misunderstood something, the manuscript was unclear — fix the manuscript, not just the referee.
- **Disagree substantively, not defensively.** "We respectfully disagree, for the following reason:
  [physics argument, with data or a reference]. We have added a sentence in Sec. III making this
  explicit." Never dismiss a referee's competence.
- **Do new analysis when asked and when it's tractable.** A new supplementary figure answering a
  referee's question is the strongest possible response.
- **Concede clearly when the referee is right.** "The referee is correct; we had underestimated the
  radiative correction. We have recomputed the budget (Table II) and the revised value is
  κ = 40 ± 6 W m⁻¹ K⁻¹, which does not change our conclusion."
- **Keep the tone even.** Referees are anonymous colleagues doing unpaid work; editors read the
  exchange. Sarcasm ends papers.
- **Don't fabricate.** If you cannot do the requested measurement, say why (equipment, access, time)
  and offer what you can — a bound, a simulation, a literature comparison.

See `assets/referee_response_template.md`.

---

## Reviewing someone else's physics manuscript

When asked to referee or critique, structure the report as editors expect:

1. **Summary of the claim** in your own words (two or three sentences) — this demonstrates you read
   it and lets the authors see whether the claim came through.
2. **Assessment against the journal's criteria** — for PRL: impact, innovation, interest; for a
   specialist journal: correctness, completeness, and whether it advances the subfield.
3. **Major points** — numbered, each identifying a specific problem with the physics, the analysis,
   or the evidence, and stating what would resolve it. These are the points that determine the
   recommendation.
4. **Minor points** — numbered, page/line referenced: notation, missing definitions, figure
   legibility, wording.
5. **Recommendation** with a one-line reason.

Reviewing standards worth holding: attack the argument, never the authors; distinguish "this is
wrong" from "I would have done it differently"; specify what evidence would change your mind; check
whether the claimed novelty survives a literature search; check whether the uncertainties support the
claim's verb.
