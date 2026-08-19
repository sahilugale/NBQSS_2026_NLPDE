# Units, Uncertainty, Significance, and Data Statements

Physics has no CONSORT or PRISMA. What plays that role is the discipline's expectation that every
number is accompanied by an honest uncertainty, that systematic effects are enumerated and bounded,
and that the data and code behind the figures are available. This file covers those obligations.

## Contents

- [Units and quantities](#units-and-quantities)
- [Numbers and significant figures](#numbers-and-significant-figures)
- [Reporting uncertainty](#reporting-uncertainty)
- [Systematic uncertainty budgets](#systematic-uncertainty-budgets)
- [Statistical significance and limits](#statistical-significance-and-limits)
- [Language calibrated to evidence](#language-calibrated-to-evidence)
- [Reproducibility content by subfield](#reproducibility-content-by-subfield)
- [Data, code, and availability statements](#data-code-and-availability-statements)
- [Checklist](#checklist)

---

## Units and quantities

**SI is the default**, with well-established exceptions that are correct in their subfields and
should not be "corrected": eV and its multiples, Å (surface science, crystallography, astronomy),
barn (nuclear/particle), Gauss and CGS (plasma, astronomy, some magnetism), parsec, $M_\odot$,
Jansky, magnitudes (astronomy), atomic units (quantum chemistry), natural units (HEP).

Rules that copy editors enforce:

- **Thin space between value and unit**: 5 K, 10 nm, 3.2 T. Exceptions: percent (5%) and degree of
  angle (30°) take no space; °C takes a space before the degree sign (25 °C).
- **Unit symbols are roman, never italic, never pluralized, never followed by a period**: 5 kg, not
  5 kgs., not 5 *kg*.
- **Spell out or symbolize consistently**: "5 tesla" or "5 T", not "5 Tesla" (unit names derived from
  proper names are lowercase when spelled out; their symbols are capitalized).
- **Compound units** use a middle dot or space and negative exponents: W m⁻¹ K⁻¹, or W/(m·K). Avoid
  stacked solidi: W/m/K is ambiguous.
- **Quantity calculus for axis labels and table headers**: the label should be a pure number.
  Either `B (T)` or `B / T` — pick one style and hold it across all figures. `B [T]` is common but
  discouraged by ISO; several journals convert it.
- **Prefixes**: one prefix per unit (nm, not mμm); prefer prefixes that keep the mantissa between
  0.1 and 1000.
- **Ranges**: repeat the unit or place it once at the end unambiguously — "from 30 to 300 K",
  "5–10 nm". Do not write "5 nm–10 nm" and "5–10 nm" in the same paper.
- **Non-dimensionalized quantities**: state the scaling explicitly when introducing reduced units.

In LaTeX, `siunitx` handles almost all of this automatically: `\qty{5}{\kelvin}`,
`\qtyrange{30}{300}{\kelvin}`, `\qty{42(5)}{\watt\per\meter\per\kelvin}`, `\unit{\micro\meter}`.
Using it eliminates most unit typography errors.

---

## Numbers and significant figures

- **Precision must match measurement capability.** "Mean temperature 45.237 K" from a sensor with
  0.1 K resolution advertises carelessness.
- **Match the value's last digit to the uncertainty's last digit**: $1.234 \pm 0.005$, not
  $1.2342 \pm 0.005$ or $1.23 \pm 0.005$.
- **Round the uncertainty to one or two significant figures.** The Particle Data Group convention: if
  the three highest-order digits of the uncertainty are between 100 and 354, use two significant
  digits; between 355 and 949, use one; between 950 and 999, round up to 1000 and use two.
- **Numerals vs. words**: use numerals with units and in all quantitative contexts. Spell out a
  number that opens a sentence, or restructure the sentence to avoid it ("Twelve devices were
  measured" or "We measured 12 devices").
- **Exponent notation**: $3.2 \times 10^{-4}$, not 3.2E-4 in prose. Keep one convention.
- **Decimal marker**: point, not comma, in English-language physics journals. Digit grouping uses a
  thin space (1 234 567) or nothing; the comma is acceptable at many journals — follow the target.

---

## Reporting uncertainty

**Every quoted value carries an uncertainty.** A number without one is not a measurement.

Standard forms, all acceptable, one per paper:

| Form | Example | Notes |
|---|---|---|
| Explicit ± | $\kappa = 42 \pm 5$ W m⁻¹ K⁻¹ | clearest; unit factored outside a parenthesis if long: $(1.234 \pm 0.005) \times 10^{-3}$ m |
| Concise (parenthetic) | $\kappa = 42(5)$ W m⁻¹ K⁻¹ | the digits in parentheses apply to the last digits of the value; standard in metrology and HEP |
| Separated stat/syst | $m = 125.3 \pm 0.4\,(\mathrm{stat}) \pm 0.6\,(\mathrm{syst})$ GeV | required when both exist and differ in origin |
| Asymmetric | $r = 0.42^{+0.08}_{-0.05}$ | common for likelihood-derived intervals |
| Confidence interval | 95% CI [1.2, 1.8] | state the level and the construction method |

**Always state what the uncertainty means.** One standard deviation? Standard error of the mean? A
68% credible interval? A conservative bound? Put it in the text at first use and in every figure
caption that shows error bars. "Error bars denote one standard error of the mean over 12 devices"
takes eleven words and prevents a referee report.

**Distinguish precision from accuracy.** Small statistical scatter with an uncalibrated instrument is
precise and wrong. If the accuracy is limited by a calibration standard, say so and quote the
standard's uncertainty.

**Propagate correctly and say how.** Linear propagation, Monte Carlo, or bootstrap — name the method.
If uncertainties are correlated, say so; quadrature addition of correlated errors understates the
total.

---

## Systematic uncertainty budgets

For any measurement claiming precision, a systematic budget is expected — often as a table:

| Source | Contribution to $\kappa$ (%) |
|---|---|
| Thermometer calibration | 4.0 |
| Radiative loss correction | 2.5 |
| Sample geometry | 3.1 |
| Contact resistance | 1.2 |
| **Total (quadrature)** | **5.8** |

Include: how each was estimated (independent measurement, variation of a parameter, comparison of
methods), whether the sources are independent, and how they were combined. A budget with a single
line reading "systematic uncertainty: 5%" and no derivation invites the referee to ask where it came
from.

---

## Statistical significance and limits

- **σ conventions**: in particle physics, 3σ is "evidence for", 5σ is "observation of". Do not use
  the words *evidence* or *observation* in a title without the corresponding significance.
- **State the test and the null hypothesis.** "Significant" without a test, a statistic, and a
  p-value or CL is meaningless.
- **The look-elsewhere effect** must be addressed in any search over a parameter range; report both
  local and global significance.
- **Upper limits**: state the confidence level and the construction (CLs, Feldman–Cousins, Bayesian
  with a stated prior). "We set an upper limit of $10^{-9}$" is incomplete; "…at 90% CL using the
  CLs method" is complete.
- **Goodness of fit**: report $\chi^2$/dof or the equivalent, and the number of degrees of freedom.
- **Blind analysis**: if the analysis was blinded, say so and describe the unblinding criteria — this
  is a strong claim of methodological control and referees weight it.
- **Don't confuse a p-value with a probability that the hypothesis is true**, and don't report
  "p < 0.05" as a physics result; physics generally wants effect sizes with uncertainties, not
  significance thresholds.

---

## Language calibrated to evidence

Verb choice encodes claim strength. Referees read this ladder precisely; mismatches read as
over-claiming or as hedging away a real result.

| Strength | Verbs and phrases | Warranted when |
|---|---|---|
| Strongest | *establishes*, *demonstrates*, *shows*, *rules out* | direct, well-controlled measurement with systematics bounded; ≥5σ for a discovery claim |
| Strong | *indicates*, *provides evidence for*, *is consistent with … and inconsistent with …* | clear signal, alternatives addressed; ~3σ |
| Moderate | *suggests*, *supports*, *points to* | correlation or partial evidence |
| Weak / speculative | *may*, *might*, *could*, *is possibly attributable to* | mechanism proposed but not tested |

Notes:

- **"Consistent with" is not "confirms".** Data consistent with a model may also be consistent with
  three others; say which alternatives you excluded.
- **Avoid "prove"** in experimental physics. Avoid "significant" as a synonym for "large".
- **Under-hedging and over-hedging are both errors.** "The data may possibly suggest a potential
  tendency towards…" buries a real 5σ result. Match the modal verb to the evidence, then stop.
- **Attribute correctly**: "we observe X" (your data) vs. "X has been observed" (the field's) vs.
  "X is expected" (theory). Physics referees track this distinction closely.

---

## Reproducibility content by subfield

There is no universal physics checklist, so use the one your subfield's referees carry in their
heads:

**Condensed matter / materials**: growth or synthesis method and source, composition and
stoichiometry with the characterization that establishes it, crystal orientation, thickness,
substrate, contact fabrication, device dimensions, annealing history, storage/handling,
number of devices measured and device-to-device spread.

**Optics / photonics**: wavelength, bandwidth, pulse duration (and whether FWHM or $1/e^2$),
repetition rate, average and peak power, beam waist, NA, polarization state, detector type and
responsivity, integration time, alignment tolerances.

**AMO / quantum**: trap frequencies, atom or ion number, temperature, coherence times ($T_1$, $T_2$,
$T_2^*$) and how measured, pulse sequences with timings, magnetic field stability, state-preparation
and measurement (SPAM) fidelities, calibration cadence.

**HEP / nuclear**: dataset and integrated luminosity, trigger and selection criteria, detector
configuration and running period, simulation generators with versions and tunes, background
estimation method, blinding, unfolding procedure.

**Astronomy**: telescope and instrument, program/proposal ID, observation dates, exposure times,
filters/gratings, seeing, airmass, reduction pipeline with version, calibration frames, archival
data DOIs, assumed cosmology, adopted solar abundances.

**Plasma / fluids**: geometry and dimensions, working gas and pressure, discharge or drive
parameters, diagnostics and their spatial/temporal resolution, shot numbers.

**Computation / numerics**: code name, version or commit hash, compiler and flags where performance
matters, discretization and resolution, convergence study, boundary and initial conditions,
functionals/pseudopotentials/basis sets, timestep, random seeds, total compute cost, hardware.

---

## Data, code, and availability statements

Most physics journals now require or strongly encourage these. Write them properly; boilerplate that
promises data "on reasonable request" and nothing else is increasingly rejected by editors.

**Data availability statement** — name the repository and give a DOI:

> The data that support the findings of this study are openly available in Zenodo at
> https://doi.org/10.5281/zenodo.XXXXXXX. Raw detector files are available from the corresponding
> author on reasonable request owing to their size (2.4 TB).

**Code availability statement**:

> The analysis code is available at https://github.com/… (archived at
> https://doi.org/10.5281/zenodo.XXXXXXX, version v1.2.0). Simulation input files are included in the
> repository under `inputs/`.

Practical guidance:

- Archive a **versioned snapshot** (Zenodo, Software Heritage) rather than citing a bare GitHub URL —
  repositories move and mutate.
- Include the data *behind the figures* (the plotted arrays), not only the raw acquisition files.
  Astronomy journals formalize this; other subfields increasingly expect it.
- Cite software and datasets as **references**, with version numbers, not only in acknowledgments.
- Include a README stating what each file contains, the units, and how to regenerate each figure.
- Author contributions (CRediT-style) and competing-interests statements are required at Nature-family
  journals and AAS journals and are good practice everywhere.

---

## Checklist

- [ ] Every number has a unit (or is explicitly dimensionless) and an uncertainty
- [ ] Unit system declared; symbols roman, correctly spaced, not pluralized
- [ ] Axis labels and table headers use consistent quantity/unit style
- [ ] Significant figures matched to uncertainty; uncertainty rounded to 1–2 sig figs
- [ ] Meaning of every uncertainty and every error bar stated (in text and in captions)
- [ ] Statistical and systematic uncertainties separated where both exist
- [ ] Systematic budget itemized with estimation method
- [ ] Significance tests, confidence levels, and limit-setting methods named
- [ ] Claim verbs calibrated to the evidence strength
- [ ] Subfield reproducibility parameters present
- [ ] Data and code availability statements with archived DOIs
- [ ] Software and datasets cited as references with versions
