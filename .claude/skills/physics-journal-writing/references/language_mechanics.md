# Sentence-Level Mechanics for Physics Prose

Physics writing fails at the sentence level in predictable ways. This file is the revision manual:
the grammar points that actually change meaning in a physics manuscript, each with the physics-flavored
failure mode and the fix. Work through it as a revision pass, not as a reading assignment.

## Contents

- [Wordiness: the first pass](#wordiness-the-first-pass)
- [Verbs and nominalization](#verbs-and-nominalization)
- [Tense](#tense)
- [Voice and person](#voice-and-person)
- [Modal verbs and hedging](#modal-verbs-and-hedging)
- [Noun compounds and stacking](#noun-compounds-and-stacking)
- [Articles and countability](#articles-and-countability)
- [Relative clauses and reduced relatives](#relative-clauses-and-reduced-relatives)
- [Parallelism](#parallelism)
- [Sentence structure and variety](#sentence-structure-and-variety)
- [Capitalization](#capitalization)
- [Word choice traps](#word-choice-traps)
- [Punctuation points that matter in physics](#punctuation-points-that-matter-in-physics)
- [Revision pass order](#revision-pass-order)

---

## Wordiness: the first pass

Expect to cut 15–25% of a first draft with no loss of content. Physics revision is subtraction.

**Flabby phrases and their replacements:**

| Wordy | Concise |
|---|---|
| due to the fact that | because |
| in order to | to |
| at the present time / at this point in time | now, currently |
| for the purpose of | for, to |
| it is worth noting that / it is important to note that | *(delete)* |
| it has been shown that X is | X is |
| in the event that | if |
| a total of 12 samples | 12 samples |
| in the case of | for, in |
| with regard to / in regards to | for, about |
| it is clear that / obviously | *(delete — if it were clear you wouldn't say so)* |
| in spite of the fact that | although |
| a number of | several, or the actual number |
| serves to illustrate | illustrates |
| has the ability to | can |
| in close proximity to | near |
| during the course of | during |

**`There is` / `there are` openings** displace the real subject and cost words:

> ❌ There is a strong dependence of the resistivity on temperature.
> ✅ The resistivity depends strongly on temperature.

> ❌ There are three mechanisms that can explain this behavior.
> ✅ Three mechanisms can explain this behavior.

(Exception: `there exists` in mathematical statements, where it is a quantifier, not filler.)

**Redundant pairs**: "completely eliminate", "each and every", "basic fundamentals", "final outcome",
"currently ongoing", "may possibly", "combine together", "cancel out" (in formal prose), "the reason
is because".

**Empty intensifiers**: very, quite, rather, extremely, dramatically, significantly (when not
statistical), highly, greatly, remarkably. If the number is in the sentence, the intensifier adds
nothing: "The conductance dropped dramatically, by a factor of 40" → "The conductance dropped by a
factor of 40."

---

## Verbs and nominalization

**Nominalization** — burying the action in a noun — is the single largest source of physics wordiness.
Look for `-tion`, `-ment`, `-ance`, `-ity` nouns paired with an empty verb (perform, carry out,
conduct, make, provide, undertake, achieve).

| Nominalized | Direct |
|---|---|
| We performed a measurement of the conductivity | We measured the conductivity |
| An analysis of the data was carried out | We analyzed the data |
| The application of a magnetic field resulted in a reduction of the signal | Applying a magnetic field reduced the signal |
| We made a comparison between theory and experiment | We compared theory and experiment |
| Optimization of the parameters was undertaken | We optimized the parameters |
| An investigation of the temperature dependence was conducted | We investigated the temperature dependence |

**Linking verb + adjective → action verb** (the pattern is `X is [adjective] of Y`):

| Weak | Strong |
|---|---|
| The results are reflective of the model | The results reflect the model |
| The data are indicative of a trend | The data indicate a trend |
| The signal is dependent on the field | The signal depends on the field |
| The behavior is suggestive of localization | The behavior suggests localization |
| The method is capable of resolving 1 ps | The method resolves 1 ps |

**Phrasal verbs → single formal verbs**: looked into → investigated; brought up → raised; got rid of
→ eliminated; cut down → reduced; found out → determined; go up and down → fluctuate; put forward →
proposed; brought about → caused; carried on → continued; put off → postponed; came across →
encountered.

**Choose precise verbs.** Physics has a rich vocabulary of action: *scales as*, *saturates*,
*diverges*, *collapses onto*, *tracks*, *lags*, *broadens*, *shifts*, *quenches*, *couples to*,
*hybridizes*, *decays as*, *scatters off*, *renormalizes*. Reaching for these instead of "shows a
change in" tightens and sharpens simultaneously.

---

## Tense

Physics tense usage is stable and referees notice drift.

| Content | Tense | Example |
|---|---|---|
| What you did (methods, measurements) | simple past | "We annealed the samples at 600 °C." |
| Your specific findings | simple past | "The conductance dropped by a factor of four." |
| What a figure, table, or equation shows | simple present | "Figure 3 shows…", "Equation (5) describes…" |
| Established physics, general truths | simple present | "Phonon scattering limits thermal transport." |
| Your interpretation and conclusions | simple present | "These results indicate that…" |
| Accumulated prior work (field-level) | present perfect | "Edge conduction has been observed in several systems." |
| A specific prior study | simple past + citation | "Smith et al. measured κ = 60 W m⁻¹ K⁻¹ [12]." |
| Contents of this paper | simple present | "Section III presents the analysis." |
| Future work | future / present | "These measurements will be extended to…" — use sparingly |

**The recurring error**: past tense for what a figure shows. "Figure 2 showed the temperature
dependence" is wrong; the figure is on the page now. "Figure 2 shows…"

**The second recurring error**: present tense for your own results. "We find that κ decreases" is
acceptable as a framing verb, but the finding itself is past: "κ decreased by 40% between 30 and
300 K."

**Consistency within a section** matters more than any individual choice: past throughout Methods,
present-dominant in Discussion.

---

## Voice and person

**"We" is standard in physics** and is not immodest. Active voice with a first-person subject is
shorter and clearer:

> ❌ It was found by the authors that the transition temperature was suppressed.
> ✅ We found that the transition temperature was suppressed.

**Use the passive** when the actor is genuinely irrelevant or when the object is the sentence's
topic and needs to sit in subject position for cohesion:

> "Samples were annealed at 600 °C for 2 h." *(who annealed them doesn't matter)*
> "The extracted exponent was compared with the prediction of Ref. [8]." *(topic is the exponent)*

Methods sections are naturally passive-heavy; Results and Discussion should not be. A Results section
in which every sentence is passive reads as evasive and buries agency.

**Single-author papers**: "we" remains common in physics (as an inclusive "we" with the reader); "I"
is acceptable at some journals. Avoid "the author" and "the present investigation".

**Avoid anthropomorphism.** "The sample wants to minimize its energy", "the electrons decide to
pair", "the model believes" — charming in a seminar, sloppy in print. Write "the configuration
minimizes the free energy".

---

## Modal verbs and hedging

Modals encode the confidence of a claim. In physics they are load-bearing, not decorative.

| Modal | Force | Physics use |
|---|---|---|
| **can** | ability, general possibility | "The technique can resolve 1 ps." |
| **could** | tentative possibility | "The discrepancy could arise from surface scattering." |
| **may** | moderate possibility | "The mode may be Raman-active in this symmetry." |
| **might** | weaker, more hypothetical | "Higher-order terms might contribute below 1 K." |
| **will** | strong prediction, future | "The proposed detector will operate at 4 K." |
| **would** | conditional, hypothetical | "Doubling the field would double the splitting." |
| **should** | logical expectation, recommendation | "The signal should scale as $T^{-3}$ in this regime." |
| **must** | necessity, logical conclusion | "Energy conservation requires that…" (often better than "must") |

Structural rules: modal + **base form** (no *to*, no *-s*): "The results may indicate", never "may to
indicate" or "may indicates".

**Calibration is the point.** Match the modal to the evidence:

> ❌ (over-hedged, buries a solid result) "Our data might possibly suggest a potential tendency for
> the conductivity to perhaps decrease."
> ✅ "The conductivity decreased by 40 ± 3% over this range."

> ❌ (over-claimed) "This proves that point defects are the sole limiting mechanism."
> ✅ "This identifies point defects as the dominant scattering channel in the measured range;
> we cannot exclude a boundary contribution below 40 K."

**Hedge the interpretation, not the measurement.** Measurements are stated flatly with their
uncertainties; mechanisms and implications carry the modals.

---

## Noun compounds and stacking

Physics is the worst offender in English for noun stacks, and they genuinely destroy readability.

**Formation rules:**
- Drop the plural on the modifying noun: "electron beam" (not "electrons beam"); "10 devices" but
  "device fabrication".
- Drop "of the": "production of cars" → "car production"; "density of carriers" → "carrier density".
- Pluralize only the final noun: "carrier densities", "band structures". Exception: "women drivers".
- **Hyphenate multi-word modifiers before a noun**: "high-temperature superconductor",
  "time-resolved spectroscopy", "phonon-limited mobility", "second-order transition",
  "state-of-the-art detector". No hyphen when the phrase follows the noun: "the transition is
  second order".
- **Adverb + adjective is not hyphenated**: "a highly ordered film", "a rapidly cooled sample".
- **Units in compound modifiers**: with unit *symbols*, no hyphen — "a 10 nm film", "a 5 T field";
  with spelled-out units, hyphenate — "a 10-nanometer film". Follow the journal; APS style avoids
  hyphenating symbol-based modifiers.

**The stacking limit is three.** Beyond that, unpack with prepositions:

> ❌ electron beam evaporation deposition chamber base pressure
> ✅ the base pressure of the electron-beam evaporation chamber

> ❌ time resolved pump probe reflectivity measurement setup
> ✅ the setup for time-resolved pump–probe reflectivity measurements

**Ambiguity check.** "Small particle detector" — a small detector, or a detector for small particles?
"Low temperature measurement error" — error in a low-temperature measurement, or a low error?
If more than one parse exists, hyphenate or unpack.

---

## Articles and countability

The most common error class for non-native English speakers, and it changes meaning.

**a / an** — singular count nouns, first mention or unspecified: "We used **a** superconducting
resonator." Never with non-count nouns.

**the** — specific, previously mentioned, or uniquely identifiable: "**The** resonator had a quality
factor of 10⁵." Also for unique objects ("the Sun", "the ground state"), superlatives ("the highest
value"), and specified-by-a-following-phrase nouns ("the temperature of the sample").

**zero article** — plural count nouns and non-count nouns in general statements: "Superconductors
expel magnetic flux." "Research on this system is ongoing."

**Non-count nouns common in physics** (no plural, no *a/an*): research, evidence, information,
equipment, apparatus (also count), software, hardware, work (as effort), knowledge, feedback, noise,
radiation, matter, light, energy (usually), literature (as body of work), progress, resolution (as a
property).

> ❌ "We performed **a** research on **evidences** for edge conduction."
> ✅ "We investigated evidence for edge conduction."

**Latin/Greek plurals physics uses**: spectrum/spectra, datum/**data**, criterion/criteria,
phenomenon/phenomena, maximum/maxima, minimum/minima, index/indices, matrix/matrices,
apparatus/apparatus(es), analysis/analyses, basis/bases, focus/foci, nucleus/nuclei,
vertex/vertices, formula/formulae (or formulas).

**"Data" is plural in APS and most physics house styles**: "the data **are** consistent with…",
"these data show…". Nature-family and some journals accept singular. Pick the target's convention and
be consistent — mixing "the data is" and "the data are" in one manuscript is a copy-editing flag.

**Words with count and non-count senses that differ in meaning**: work (effort) vs. works (published
outputs); time (duration) vs. times (occasions); light (illumination) vs. lights (lamps);
resistance (property) vs. resistances (values); noise (general) vs. noises (individual sounds).

---

## Relative clauses and reduced relatives

Reduced relatives are the workhorse of compressed physics prose. Learning to use them is the fastest
route to a shorter Letter.

**Defining (restrictive) — no commas**, essential to identify which thing:

> "The devices **that showed hysteresis** were excluded from the analysis."
> *(only some devices showed hysteresis; those are the excluded ones)*

**Non-defining (non-restrictive) — commas required**, adds non-essential information:

> "The devices, **which were fabricated in a single batch**, showed identical thresholds."
> *(all the devices were fabricated in one batch)*

Getting this wrong changes the physics. "The samples that were annealed showed a shift" (only some
were annealed) vs. "The samples, which were annealed, showed a shift" (all were).

**Reduction** — drop `who/which/that + be`:

| Full | Reduced |
|---|---|
| the samples **that were** grown by MBE | the samples grown by MBE |
| the data **that were** collected in 2024 | the data collected in 2024 |
| researchers **who conducted** the experiment | researchers conducting the experiment |
| the modes **that are** localized at the edge | the modes localized at the edge |
| the term **which is** proportional to $k^2$ | the term proportional to $k^2$ |

Past participle for passive meaning ("samples annealed at 600 °C"), present participle for active
("electrons occupying the lowest band").

**Caution**: reduction can create dangling or ambiguous attachment. "We measured the resistance of
the films deposited at 300 K" — were the films deposited at 300 K, or was the resistance measured at
300 K? Restore the full clause or restructure when ambiguity appears.

---

## Parallelism

Elements joined by *and*, *or*, *not only…but also*, *either…or*, *both…and*, or appearing in a list
or comparison must share grammatical form. Scan for *and* — it is where parallelism breaks.

> ❌ "We aimed to characterize the transport, measuring the optical response, and a comparison with
> theory."
> ✅ "We aimed to characterize the transport, measure the optical response, and compare the results
> with theory."

> ❌ "The method is fast, reliable, and it can be automated."
> ✅ "The method is fast, reliable, and automatable."

> ❌ "not only the accuracy but also reduced response time"
> ✅ "not only improved accuracy but also reduced response time"

**Comparisons must match on both sides:**

> ❌ "The conductivity is higher in Phase II than Phase I showed."
> ✅ "The conductivity is higher in Phase II than in Phase I."

> ❌ "Our resolution is better than Ref. [8]."   *(compares a resolution to a paper)*
> ✅ "Our resolution is better than that of Ref. [8]."

**Section headings, list items, and objectives** should share form: all noun phrases, or all
infinitives — not a mix.

---

## Sentence structure and variety

The four structures, with their physics uses:

- **Simple** (S + V + O): direct observations and method steps. "The sample melted at 1200 K."
- **Compound** (SV, *and/but/so* SV; or SV; *however/moreover*, SV): linking or contrasting results.
  "The solution dissolved in water, but it remained solid in ethanol."
- **Complex** (subordinate clause + SV): causal and conditional relationships between variables.
  "Because the current increased, the wire temperature rose."
- **Compound-complex**: layered reasoning in discussion. "The simulation predicted rapid growth, and
  although most data confirmed this, anomalies persisted below 4 K."

**Vary the length.** A paragraph of uniformly 30-word sentences is unreadable; so is a paragraph of
uniformly 8-word ones. Use a short sentence to land a key claim after a long one.

**Two structural errors that appear constantly:**

- **Comma splice** — two independent clauses joined by only a comma. ❌ "The sample was heated, the
  reaction began." Fix with a period, a semicolon, or a coordinating conjunction: "The sample was
  heated, **and** the reaction began."
- **Run-on / fused sentence** — no punctuation at all. ❌ "The solution was clear the test succeeded."
  Same three fixes.

Note that conjunctive adverbs (*however*, *therefore*, *nevertheless*, *thus*, *moreover*,
*consequently*) do **not** join clauses like *and* does. ❌ "The fit was good, however the residuals
were structured." ✅ "The fit was good; however, the residuals were structured." or "The fit was
good. However, the residuals were structured."

**Sentence length target**: 15–25 words on average in physics prose, with deliberate variation. If a
sentence exceeds ~40 words, check whether it contains two ideas.

---

## Capitalization

| Case | Form |
|---|---|
| Labeled items with a number | **Figure 3**, **Fig. 3**, **Table I**, **Eq. (4)**, **Sec. III**, **Ref. [7]**, **Appendix B** |
| Same items used generically | "the following figures", "the equation above", "in this section" |
| Paper sections referenced specifically | "the Methods section" (specific) vs. "the methods used" (general) |
| Named laws, effects, equations | proper name capitalized, the rest lowercase: "Ohm's law", "Maxwell's equations", "the Hall effect", "the Josephson effect", "Kepler's first law" |
| Named methods from proper names | "Fourier transform", "Gaussian distribution", "Raman spectroscopy", "Monte Carlo simulation", "Bragg peak" |
| General processes and terms | lowercase: "photosynthesis", "regression analysis", "control group", "phase transition", "density functional theory" (though "DFT" as an acronym) |
| Chemical elements | name lowercase, symbol capitalized: "silicon", "Si"; "sodium chloride", "NaCl" |
| Species names | *E. coli* — genus capitalized, species lowercase, both italic |
| Institutions and organizations | full official names capitalized: "the World Health Organization", "the Laboratory of Molecular Ecology"; lowercase generic reference: "the organization", "the laboratory" |
| Astronomical bodies | "the Sun", "the Earth", "the Moon" as bodies; "the solar system"; "the Universe" in cosmology (journal-dependent); lowercase "earth" as soil |
| Units from proper names | symbol capitalized, name lowercase: "5 T", "five tesla"; "300 K", "kelvin" |
| Particles and states | "photon", "electron", "muon" lowercase; symbols as defined ($\pi^+$, $Z^0$) |

Titles and headings: sentence case is standard in physics ("Thermal transport in monolayer
semiconductors"), not title case. Check the target journal.

---

## Word choice traps

| Confusion | Distinction |
|---|---|
| affect / effect | *affect* = verb (to influence); *effect* = noun (result) — or verb meaning "to bring about" |
| comprise / compose | the whole *comprises* the parts; the parts *compose* the whole; "is comprised of" is disputed — use "consists of" |
| principle / principal | *principle* = rule; *principal* = main |
| discrete / discreet | *discrete* = separate; *discreet* = tactful |
| complementary / complimentary | *complementary* = completing; *complimentary* = free or praising |
| accuracy / precision | *accuracy* = closeness to truth; *precision* = repeatability |
| significant | statistical vs. large — never use it loosely in physics |
| correlation / causation | correlation never implies causation without a mechanism or an intervention |
| less / fewer | *fewer* for count nouns (fewer samples); *less* for non-count (less noise) |
| between / among | *between* for two (or pairwise); *among* for more than two collectively |
| that / which | *that* for defining clauses (no comma); *which* for non-defining (with comma) — US style |
| its / it's | *it's* = it is; possessive *its* has no apostrophe |
| e.g. / i.e. | *e.g.* = for example; *i.e.* = that is; both followed by a comma in US style |
| compare to / compare with | *to* for likening; *with* for examining differences — physics usually wants *with* |
| alternate / alternative | *alternate* = every other; *alternative* = another option |
| continuous / continual | *continuous* = unbroken; *continual* = repeated |
| number / amount | *number* for countables; *amount* for non-count |

**Words to avoid in physics prose**: obviously, clearly, trivially, of course, as is well known
(all insult the reader who doesn't find it obvious); novel, cutting-edge, state-of-the-art (assert
without evidence); very, extremely, dramatically; utilize (use *use*); methodology when you mean
*method*; huge, tiny, enormous (give the number); prove; paradigm shift.

---

## Punctuation points that matter in physics

- **Serial (Oxford) comma** before the final *and* in a list — standard in US physics journals and
  it prevents ambiguity in coordinated technical noun phrases.
- **Em dash** for a parenthetical break — set closed in US style. En dash for ranges (5–10 nm), for
  coupled names (Bose–Einstein, Fermi–Dirac, pump–probe, Ginzburg–Landau — note these are *en*
  dashes, not hyphens, because they join two separate people or concepts) and for negative signs in
  running text where a minus is not available.
- **Hyphen vs. minus**: in math mode always use a real minus, never a hyphen.
- **Solidus (/)**: only for division of quantities, for interfaces (Ag/Cu(001)), and in "and/or".
  Between words its meaning is imprecise — use the correct conjunction.
- **Semicolon** to join closely related independent clauses, and to separate list items that already
  contain commas.
- **Commas around non-defining clauses**; none around defining ones (see above — this one changes
  meaning).
- **Reference placement** relative to punctuation follows the journal's class file; don't hand-place
  it after using `\cite`.

---

## Revision pass order

Do these as separate passes. Combining them means doing all of them badly.

1. **Structure** — are the moves present and in order? (see `structure_and_moves.md`)
2. **Claim calibration** — does every verb match its evidence?
3. **Numbers** — units, uncertainties, significant figures, consistency with figures.
4. **Notation** — every symbol defined once and used consistently everywhere.
5. **Cut** — wordiness, nominalization, throat-clearing, intensifiers.
6. **Flow** — topic sentences read alone; given–new order; cohesion devices present.
7. **Grammar** — tense, articles, parallelism, relative clauses, agreement.
8. **Mechanics** — capitalization, hyphenation, punctuation, cross-reference format.
9. **Read aloud** — the fastest detector of run-ons, missing words, and unreadable equations.
