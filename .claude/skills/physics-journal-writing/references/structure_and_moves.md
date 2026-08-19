# Section Architecture and Rhetorical Moves in Physics Papers

Every section of a physics paper performs a predictable sequence of rhetorical jobs — "moves" in the
Swales/Glasman-Deal sense. Referees read for these moves whether or not they name them. This file
gives the move sequence for each section, the language that signals each move, and the failure mode
that follows from skipping it.

## Contents

- [How to use moves](#how-to-use-moves)
- [Introduction](#introduction)
- [Theory / Model section](#theory--model-section)
- [Experimental and computational methods](#experimental-and-computational-methods)
- [Results](#results)
- [Discussion](#discussion)
- [Conclusions](#conclusions)
- [Paragraph-level flow](#paragraph-level-flow)
- [Diagnosing a section that isn't working](#diagnosing-a-section-that-isnt-working)

---

## How to use moves

Two-stage drafting. **Stage 1**: write the outline as a list of moves — one line per paragraph
stating the move, the content, the references needed, and the bridge to the next paragraph.
**Stage 2**: expand each line into connected prose. The bullets are scaffolding and never appear in
the manuscript.

Example Stage 1 outline for a Letter introduction:

```
P1  M1 Importance: topological insulators promise dissipationless edge transport
    M2 What's established: quantized conductance seen in HgTe [refs], Bi2Se3 [refs]
P2  M2 Narrowing: but all measurements below 10 K; theory predicts survival to 100 K [ref]
    M3 Gap: no measurement of edge-state coherence above liquid-He temperatures
    Bridge: "This regime is exactly where..."
P3  M4 Present work: we measure coherence length to 80 K in device X
    M4' Headline number: L_phi = 1.2 ± 0.2 um at 80 K, 5x prior best
    M5 Consequence: sets the ceiling for room-temperature operation
```

Stage 2 turns this into three paragraphs of prose with citations integrated into sentences.

---

## Introduction

Physics introductions are short and argumentative. A Letter's introduction is two to three
paragraphs; an Article's is four to six. It is not a literature review; it is the construction of a
gap and the announcement that this paper fills it.

### Move 1 — Establish the phenomenon or system and why it matters

Present tense, general statements, few or no hedges. One or two sentences. Avoid opening with
"In recent years, there has been growing interest in…" — it is the most-used and least informative
opening in physics.

*Signal language:* "X governs…", "X sets the fundamental limit on…", "The behavior of X underlies…",
"X is central to proposals for…"

**Weak:** "Two-dimensional materials have attracted considerable attention in recent years."
**Better:** "Heat flow in monolayer semiconductors sets the thermal ceiling on any device built from
them, yet the phonon scattering channels that limit it remain unresolved."

### Move 2 — State what is established, with specifics

Present perfect for accumulated knowledge ("has been observed", "have shown"); past simple when
attributing a specific result to a specific study. Cite *numbers*, not just papers: physics
introductions establish the state of the art quantitatively, because the gap is usually quantitative.

*Signal language:* "Measurements in [system] have established…", "Theory predicts…", "The best
reported value is …", "Previous work has been limited to…"

Cite selectively. Ten references supporting one uncontroversial sentence signals padding; a claim of
priority resting on one reference signals carelessness.

### Move 3 — Open the gap

This is the load-bearing move. In physics the gap almost always takes one of five forms; naming
which one you have sharpens the sentence:

| Gap type | Typical phrasing |
|---|---|
| No measurement exists | "…has not been measured directly." |
| Regime unexplored | "…measurements remain confined to T < 10 K." |
| Theory–experiment discrepancy | "…exceeds the predicted value by a factor of three." |
| Conflicting results | "…while [refs] report X, [refs] find the opposite." |
| Method limitation | "…existing techniques cannot resolve timescales below 1 ps." |

*Signal language:* "However,", "Despite this progress,", "It remains unclear whether…",
"No direct measurement of … has been reported.", "This discrepancy has not been explained."

**Common failure:** the gap is stated as "little is known about X". That is a statement about the
literature, not about physics, and reviewers read it as an admission that the authors could not find
a real question.

### Move 4 — Announce the present work, with the result

Past tense for what was done, present for what it means. **State the number here** — physics
introductions do not withhold the result for suspense.

*Signal language:* "Here we report…", "In this Letter we measure…", "We show that…",
"We demonstrate … , obtaining … ."

**Weak:** "In this work, we investigate thermal transport in monolayer WSe₂ and discuss our results."
**Better:** "Here we measure the in-plane thermal conductivity of monolayer WSe₂ from 30 to 300 K,
finding κ = 42 ± 5 W m⁻¹ K⁻¹ at 300 K — three times below first-principles predictions — and show
that the deficit scales linearly with point-defect density."

### Move 5 — Roadmap (Articles only; omit in Letters)

"Section II presents the model; Section III describes the measurement; Section IV…". Useful in a long
Article, dead weight in a four-page Letter.

---

## Theory / Model section

Present in most theoretical papers and many experimental ones. Move sequence:

1. **State the physical setting and assumptions** — geometry, degrees of freedom, approximations,
   and their validity range. Assumptions stated late read as excuses; stated up front they read as
   control.
2. **Introduce the Hamiltonian, action, or governing equations**, defining every symbol.
3. **Derive or state the key result**, showing the steps a competent reader cannot reconstruct and
   deferring the rest to an appendix.
4. **Give limits and checks** — known limiting cases recovered, dimensional analysis, symmetry
   constraints, comparison to exactly solvable cases. Referees look for these.
5. **State what is predicted and how it could be falsified**, connecting to the experimental section.

Tense: present for what the theory *says* ("Equation (4) describes…", "The model predicts…"), past
for what *you did* ("We solved Eq. (4) numerically…").

---

## Experimental and computational methods

The single criterion is reproducibility by a competent stranger. Structure it in the order the work
was done, with subsection headings in an Article.

**Move 1 — General overview.** One or two sentences framing the whole approach before any detail:
"We measured thermal conductivity using a suspended-microbridge platform on 12 devices fabricated
from three growth batches." This paragraph lets the reader build a mental model before receiving
parameters.

**Move 2 — Specific parameters.** Quantities, temperatures, durations, sequences, conditions,
geometries, purities, instrument models with manufacturer and location where the field expects it.

**Move 3 — Justify choices.** Why this substrate, this temperature range, this basis set, this
integration scheme. *Signal language:* "…was chosen because…", "…to avoid…", "…following the
procedure of [ref], which has been shown to…"

**Move 4 — Indicate care taken.** Calibration, controls, blind analysis, repeated measurements,
convergence tests, independent cross-checks. This move is what distinguishes a methods section from
a parts list.

**Move 5 — Acknowledge limitations of the method.** Contamination risk, resolution floor, finite-size
effects, systematic drift — with the estimated magnitude of each. Stating a limitation with a bound
is strong; hiding it and having a referee find it is fatal.

Physics-specific content checklist:

- **Samples**: source or growth method, composition, dimensions, thickness, orientation, defect
  density, and how each was characterized.
- **Apparatus**: model, manufacturer, key specifications, modifications.
- **Measurement**: excitation amplitudes and frequencies, integration times, averaging, temperature
  stability, vacuum or field conditions.
- **Calibration**: reference standards, procedure, residual uncertainty.
- **Simulation/numerics**: code name and version, discretization, mesh or basis-set size,
  convergence criteria, boundary conditions, pseudopotentials/functionals, random seeds, hardware
  and runtime where relevant.
- **Analysis**: fitting function and its justification, weighting, uncertainty propagation, outlier
  criteria decided *before* seeing the data.

Tense: past throughout for what was done ("Samples were annealed at 600 °C"), present for what
equipment or code does in general ("The cryostat maintains 10 mK base temperature").

---

## Results

Physics results sections are organized around figures. Each figure gets a block of prose following
the same internal sequence:

1. **Invitation** — direct the reader to the display item. "Figure 2 shows the temperature dependence
   of…" (present tense; the figure *shows*, it did not *showed*).
2. **Describe the salient feature** — what the reader should see, in words. Not a redescription of
   every curve; the one or two features that matter.
3. **Quantify** — the numbers, with uncertainties. This is the sentence that carries the evidence.
4. **Compare** — to the model, to prior measurements, to the control. Present tense for the
   comparison itself.
5. *(Optionally)* **Bridge** to the next figure.

**Reporting vs. interpreting.** The boundary is a verb choice. Reporting: "The germination rate
*was* highest after two days." Interpreting: "The results *suggest* that two days is optimal." If the
journal or your architecture uses a combined Results and Discussion, keep the boundary visible
within each paragraph rather than abandoning it.

**Do not narrate the figure.** Text that says "Figure 3(a) shows the blue curve rising, then falling,
while the red curve stays flat" wastes the word budget the figure already spent. Say what it means:
"The mobility peaks near 60 K and falls as T⁻³ above it, consistent with acoustic-phonon scattering
[ref]."

**Order.** Choose one logic and hold it: most important first (usual for Letters), simple to complex,
chronological by method, or general to specific. State the logic implicitly through topic sentences.

Tense: past for your findings ("The conductance dropped by a factor of four"), present for what
figures and equations show ("Figure 3 shows…", "The fit yields…"), present for established physics.

---

## Discussion

1. **Restate the principal finding** in one sentence, without repeating the results verbatim.
2. **Explain the mechanism** — this is the intellectual core in physics. What physical process
   produces the observation? What model reproduces it, and with what parameters?
3. **Compare with prior work quantitatively** — agreement, disagreement, and the reason for
   disagreement (different regime, different sample quality, different systematic treatment).
4. **Address alternative explanations and rule them out.** Physics referees supply these if you
   don't. Naming and dismissing the two most plausible alternatives with evidence is the strongest
   move available in a discussion.
5. **State limitations with bounds** — not "our sample size was small" but "the 15% scatter across
   devices limits the extracted exponent to −3.0 ± 0.4".
6. **Implications and outlook** — what this constrains, enables, or predicts. Keep it to what
   follows from the data; speculation is permitted if it is labeled as speculation.

Tense: present for interpretation and established knowledge, past for what you and others did,
present perfect for the accumulated state of the field.

---

## Conclusions

Short — one paragraph in a Letter, two at most in an Article. Restate the claim with the number,
state the significance in one sentence, and point to the next question. Do not introduce new
results, new figures, or new references. Avoid ending on "further work is needed", which is true of
every paper ever written.

---

## Paragraph-level flow

Cohesion in physics prose is built from four devices. A paragraph that fails to flow is almost always
missing one of them.

**1. Lexical overlap** — repeat a key term from the end of one sentence at the start of the next.
Physics tolerates and rewards repetition of technical terms; do not reach for synonyms to avoid it.
Calling the same quantity "conductivity", "conduction", and "transport coefficient" in three
consecutive sentences creates ambiguity, not variety.

> The samples were annealed to reduce **defect density**. Lowering the **defect density** shifted the
> mobility peak to 45 K.

**2. Pro-forms with an explicit noun** — "this approach", "these devices", "such behavior". Never a
bare "this" pointing at a whole preceding sentence; the referent must be nameable.

> ❌ The conductance dropped while the field increased. This was unexpected.
> ✅ The conductance dropped while the field increased. **This inverse dependence** was unexpected.

**3. Extension by relative or reduced-relative clause**, which packs subordinate information without
a new sentence: "…using a cryostat, **which reaches** 10 mK", or the reduced form "…the samples
**grown** by MBE" (shortened from "the samples that were grown by MBE"). Reduced relatives are the
workhorse of compressed physics prose — see `language_mechanics.md`.

**4. Signaling connectors** — however, therefore, in contrast, consequently, by comparison,
nevertheless. Use them to mark logical turns, not as decoration. One per two or three sentences is
plenty; a connector at the start of every sentence signals that the underlying order is arbitrary.

**Given–new ordering.** Each sentence should open with information the reader already has and close
with what is new. Long, heavy, and unfamiliar material goes at the end of the sentence where it can
be picked up by the next one.

**Topic-sentence test.** Extract the first sentence of every paragraph in a section and read them in
sequence. They should form a coherent summary of the section. If they don't, the paragraphs are
mis-ordered or under-topicalized — fix the structure, not the transitions.

**Paragraph shapes that work in physics:** general → specific; chronological (procedure, timeline);
categorical (three mechanisms, each in turn); comparison/contrast (theory vs. measurement);
cause–effect (defects → scattering → reduced κ); evidence → analysis. Choose one per paragraph and
signal it in the topic sentence.

---

## Diagnosing a section that isn't working

| Symptom | Likely missing move | Fix |
|---|---|---|
| Introduction reads as a review | Move 3 (gap) | Write the gap sentence first, then keep only the citations that build to it |
| Referee asks "what's new here?" | Move 4 without a number, or no quantitative comparison to prior best | State the result and the improvement factor explicitly |
| Referee asks "how do you know it isn't X?" | Discussion move 4 | Name and eliminate the two leading alternatives |
| Reader can't reproduce the work | Methods moves 2 and 4 | Add parameters and calibration/controls |
| Results read as figure narration | Results steps 3–4 | Replace description with quantification and comparison |
| Paragraphs feel disconnected | Cohesion devices 1–2 | Add lexical overlap and named pro-forms; check given–new order |
| Conclusion adds nothing | Restating results instead of stating significance | One sentence claim + one sentence consequence + one sentence next question |
