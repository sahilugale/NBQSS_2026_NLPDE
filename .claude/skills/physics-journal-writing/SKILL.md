---
name: physics-journal-writing
description: Draft, structure, tighten, and review physics manuscripts for any physics venue — the full Physical Review line (PRL, PRX, PRX Quantum, PRA–E, PRApplied, PRResearch), quantum venues (Quantum, npj Quantum Information, QST, SciPost), Nature Physics/Photonics, AIP (APL, JAP, RSI), IOP (NJP, J. Phys.), Optica/Optics Letters/Express, JHEP, and astronomy journals (ApJ, MNRAS, A&A). Covers venue fit and length regimes, physics section architecture (frequently NOT IMRAD), the grammar of equations and symbols, units and uncertainty reporting, REVTeX/AASTeX markup, figures, Supplemental Material vs End Matter, arXiv, cover letters, and referee replies. Use this skill whenever the user is writing, revising, compressing, or critiquing any part of a physics paper — abstract, introduction, results, discussion, figure caption, referee response — even if they only say "my paper", "my Letter", "this draft", "cut 400 words", or name a physics journal, and even if they never use the words "writing skill".
---

# Physics Journal Writing

Physics papers are a distinct genre. Advice written for biomedical or social-science writing
misfires here: physics rarely uses labeled IMRAD headings, has no CONSORT/PRISMA-style reporting
checklists, treats equations as sentences, publishes on arXiv before (or instead of) acceptance,
counts abstract length in *characters* at PRL, and regards "we" as normal rather than immodest.
This skill encodes what actually governs acceptance at physics venues.

## How to use this skill

Read this file, then load only the reference files the current task needs. Each is self-contained.

| Reference | Load it when |
|---|---|
| `references/venues.md` | Choosing or targeting a journal; checking length/abstract limits; adapting a draft between venues |
| `references/structure_and_moves.md` | Outlining a paper; drafting or diagnosing a section; "my introduction isn't working" |
| `references/equations_and_notation.md` | Any manuscript containing math; symbol definitions; notation consistency |
| `references/units_uncertainty_data.md` | Reporting numbers, error bars, significance, limits; data/code availability statements |
| `references/figures.md` | Designing, sizing, or captioning figures; multi-panel layouts; colormaps |
| `references/language_mechanics.md` | Sentence-level revision; wordiness; flow; hedging; noun stacks; tense; capitalization |
| `references/submission_and_review.md` | REVTeX/AASTeX setup; arXiv; cover letters; referee replies; final checklist |

Assets: `assets/revtex_skeleton.tex` (annotated REVTeX 4.2 starting point),
`assets/presubmission_checklist.md` (run before every submission),
`assets/referee_response_template.md`.

## Step 0: Anchor to the real guidelines before writing anything

Journal limits, templates, and policies change. Treat every number in this skill as a strong prior,
not as fact-on-the-day. Before drafting or compressing:

1. Ask which journal is being targeted (or propose two or three candidates with the trade-offs).
2. If web access is available, fetch the journal's current author instructions and confirm word/page
   limit, abstract limit, reference style, figure specs, and required statements.
3. If web access is not available, say so plainly, state the limits from `references/venues.md`, and
   flag them as "verify against current guidelines" rather than presenting them as settled.

Getting this wrong is expensive: at PRL, over-length manuscripts are returned before review.
Never invent a limit, a template name, or a policy. Uncertainty stated up front costs nothing;
a confident wrong number costs a submission cycle.

## The physics-specific non-negotiables

These are the rules that most often separate a physics manuscript from a generic scientific one.

**Every equation is part of a sentence.** Displayed equations take the punctuation the sentence
needs — a comma if the sentence continues, a period if it ends. Every symbol is defined at or
immediately after first use. No sentence begins with a symbol. Details in
`references/equations_and_notation.md`.

**The abstract must contain the result, as a number.** Physics abstracts are single unlabeled
paragraphs (no `Background:` / `Methods:` headings — a structured abstract marks the paper as
foreign to the field). The reader should leave the abstract knowing the measured or predicted
quantity, its uncertainty, and why it matters. "We investigate the properties of…" with no number
is the single most common weak physics abstract.

**Figures carry the argument, not the text.** In a Letter, a reader who looks only at the figures
and captions should get the whole story. Plan the figure sequence before drafting prose; each figure
should answer one question and the caption should be self-contained.

**Uncertainty is not optional and error bars are never unlabeled.** Every quoted value gets an
uncertainty; every caption states what the error bars represent; statistical and systematic
contributions are separated where both exist. See `references/units_uncertainty_data.md`.

**Length constraints are structural, not cosmetic — and physics venues sit at both extremes.**
Decide which regime you are in before choosing the architecture, not after.

- *Hard-limited* (PRL, APL, Optics Letters, ApJL, Nature Physics): the argument must be
  constructible in ~3000–3750 words with three or four figures, with derivations and supporting
  analyses displaced to End Matter, Methods, or Supplemental Material. A PRL is not a shortened PRB.
- *Effectively unlimited* (PRX, PRX Quantum, PRA–E, PRResearch, PRApplied, NJP, Quantum, JHEP,
  ApJ, MNRAS, Optics Express): length is governed by the argument, not a counter. The failure mode
  flips — padding, unmotivated appendices, and results diluted across too many figures. Editors and
  referees push back on bloat even where no limit exists.

Compressing a full Article into a Letter and expanding a Letter into an Article are both rewrites of
the argument's frame, not reformatting. See `references/venues.md`.

**LaTeX is the working format.** Physics manuscripts are prepared in REVTeX (APS/AIP), AASTeX (AAS),
`iopart`, `elsarticle`, `mnras`, or a Nature template. Producing a Word document for a physics
journal is usually the wrong deliverable — ask before assuming.

**"We" is standard.** Active voice with a first-person plural subject is normal and preferred in
physics: "We measured the transmission" beats "The transmission was measured." Reserve the passive
for cases where the actor is genuinely irrelevant or the object is the topic of the sentence.

## Workflow

### 1. Plan (before any prose)

Establish, in this order: the single claim of the paper; the target journal; the figure sequence;
the section architecture. Write the claim as one declarative sentence containing a number — this
sentence becomes the seed of the title, the last line of the abstract, and the first line of the
conclusions. If it can't be written, the paper isn't ready to draft.

Then build the outline as an ordered list of paragraph-level moves (see
`references/structure_and_moves.md`), each with: its function, the key point, the references it
needs, and its bridge to the next paragraph. This is planning scaffolding only.

### 2. Draft (outline → prose)

Convert each outline item into connected paragraphs. **The final manuscript is flowing prose, not
bullets.** Physics tolerates lists in exactly three places: enumerated experimental conditions or
sample sets in the methods, itemized contributions in a long Article's introduction roadmap, and
Supplemental Material. Never in the abstract, results, or discussion.

Draft in the order that reduces friction: figures and captions → methods/experimental →
results → discussion → introduction → conclusions → abstract → title. The introduction is written
late because you can only motivate a result you have already stated precisely.

### 3. Compress

Physics revision is mostly subtraction. Target the constructions listed in
`references/language_mechanics.md`: nominalizations ("performed a measurement of" → "measured"),
throat-clearing ("It is worth noting that"), empty intensifiers ("very", "dramatically"),
`there is/are` openings, and noun stacks longer than three words. Expect to remove 15–25% of a
first draft without losing content. When a word budget is binding, cut in this order: redundant
restatement of figure content in the text, over-hedged qualifications, background the target
audience already has, and finally whole paragraphs moved to Supplemental Material.

### 4. Revise for flow and rigor

Two passes, kept separate. A **flow pass**: read each section's topic sentences in isolation; they
should tell the story alone. Check that each sentence's opening connects to the previous sentence's
end (given-new). A **rigor pass**: every symbol defined, every number with an uncertainty and unit,
every claim's verb calibrated to the evidence, every figure referenced in the text in order, every
reference actually supporting the sentence it is attached to.

### 5. Prepare for submission

Use `assets/presubmission_checklist.md` and `references/submission_and_review.md`. Cover letter,
arXiv posting decision, data/code availability statement, author contributions, and suggested
referees are part of the deliverable, not afterthoughts.

## Section architecture by article type

Physics has no single template. Choose the architecture from the venue, then fill it.

| Type | Headings | Typical shape |
|---|---|---|
| **PRL / Letter** | Usually none, or 2–3 unnumbered | Continuous argument: context → gap → result → evidence (3–4 figures) → implications. Derivations in End Matter; extended data in Supplemental Material |
| **Physical Review Article (PRA–E, PRApplied, PRResearch)** | Numbered (I. Introduction, II. …) | Introduction → Theory/Model → Experimental/Numerical methods → Results → Discussion → Conclusions → Appendices |
| **PRX / PRX Quantum / Quantum / NJP** | Numbered, free-form depth | Same skeleton as a PR Article but sized to the argument; long derivations stay in the main text or substantial appendices. PRX-family additionally requires a popular summary / significance statement written for non-specialists |
| **Nature Physics / Nature** | Minimal or none in main text | Narrative main text with broad framing; full Methods at the end; Extended Data figures |
| **APL / Applied Physics Letters** | Usually none | Short, application-forward; device performance and benchmarking against prior art |
| **Optics Letters / Optica** | Section headings in Optica, few in OL | Compact; system schematic figure early |
| **ApJ / AJ / MNRAS / A&A** | Numbered, IMRAD-like | Introduction → Observations/Data → Methods/Analysis → Results → Discussion → Summary; author–year citations; appendices common |
| **JHEP / hep-ph, hep-th** | Numbered | Introduction → Setup/Formalism → Analysis → Results → Conclusions → lengthy appendices |

A combined "Results and Discussion" is common and acceptable in physics — but only if the
interpretation is unmistakably separated from the observation at the sentence level. If the two
blur, split them.

## Diagnosing a weak physics manuscript

When asked to review, improve, or "make this better", check these in order. Most rejections trace
to the top of this list, not the bottom.

1. **No claim.** The paper reports activity, not a result. Fix by writing the one-sentence claim first.
2. **Claim not matched to venue.** Solid work with no case for broad interest sent to PRL; or a broad
   result buried in a specialist journal's house style.
3. **Novelty asserted, not demonstrated.** "For the first time" without an explicit comparison to
   the best prior value, method, or bound. Physics referees check this immediately.
4. **Numbers without uncertainties**, unstated error-bar meaning, or a systematic budget that
   doesn't exist.
5. **Undefined or inconsistent notation.** The same quantity called $\Gamma$ in Eq. (3) and $\gamma$
   in Fig. 4.
6. **Figures that fail at print size** — 6 pt axis labels, colormaps that collapse in grayscale, or
   panels indistinguishable to a colorblind reader.
7. **Over-claiming verbs.** "Proves", "confirms", "demonstrates conclusively" where the data support
   "is consistent with" or "indicates".
8. **Methods too thin to reproduce.** Missing sample provenance, instrument model, calibration
   procedure, simulation parameters, convergence criteria, or code version.
9. **Introduction that reviews the field instead of building a gap.** Physics introductions are
   short and argumentative, not comprehensive.
10. **Prose problems** — wordiness, noun stacks, tense drift, broken cohesion. Real, but last.

Report findings in this order and be specific: quote the sentence, name the problem, offer the
rewrite. Vague encouragement is not review.

## Writing the abstract (physics conventions)

Build it in five sentences, then compress to the character or word limit:

1. **Context** — the phenomenon or system, one sentence, no history.
2. **Gap or tension** — what was unknown, unresolved, or in conflict.
3. **What was done** — the approach, named concretely (technique, system, regime).
4. **The result, with a number and its uncertainty** — the load-bearing sentence.
5. **Consequence** — what this enables, constrains, or rules out.

Constraints vary sharply and are worth checking rather than assuming: PRL allows 600 characters
*including spaces* (roughly 90–100 words) — count characters, not words. Most Physical Review
Articles, PRX Quantum, and NJP allow ~500 words or more but read better far shorter. Nature-family
abstracts are ~150–200 words and pitched at a broader readership. Across all of them: no citations,
no undefined acronyms, no figure references, and no labeled headings unless the journal demands them.

**Weak:** "We investigate the thermal transport properties of a novel two-dimensional material using
various experimental techniques and discuss the implications of our findings."

**Strong:** "We measure the in-plane thermal conductivity of monolayer WSe₂ from 30 to 300 K and find
κ = 42 ± 5 W m⁻¹ K⁻¹ at room temperature, a factor of three below the value predicted by first-principles
calculations that neglect phonon–defect scattering. The discrepancy scales with measured defect
density, identifying point defects as the dominant limit to heat flow in this system."

## Titles

Physics titles are frequently declarative claims rather than topic labels, and this is a feature:
"Observation of gravitational waves from a binary black hole merger" tells the reader the result.
Prefer specific over general; avoid "novel", "study of", "investigation into", "towards"; avoid
introducing new terminology or unfamiliar acronyms in the title (PRL explicitly asks for this);
keep it parseable on one line. Common effective openers: *Observation of*, *Evidence for*,
*Direct measurement of*, *Absence of*, *Constraints on*, *Emergence of*, *Anomalous*.

## Working style when helping

Ask which journal and which article type before drafting — the answer changes the architecture, the
length, the citation style, and the tone. If the user hasn't decided, offer two or three candidates
with the trade-offs rather than picking silently.

Preserve the author's voice and notation. When rewriting, change what is broken and leave what
works; don't relabel their symbols or restructure their argument without saying so and why.

Show the rewrite, not just the rule. "Tighten this sentence" is less useful than the tightened
sentence next to the original with a one-line reason.

Flag anything you can't verify — a limit, a template version, whether a specific journal accepts a
given article type, whether a cited paper says what the sentence claims. Say "I'd check this against
the current author guidelines" rather than asserting.

Never fabricate references, DOIs, arXiv identifiers, or numerical values. If a draft needs a citation
you can't confirm, mark it `[CITATION NEEDED: prior measurement of κ in monolayer TMDs]` and say so.
