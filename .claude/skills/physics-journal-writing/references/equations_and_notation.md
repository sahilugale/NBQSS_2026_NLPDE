# Equations, Symbols, and Notation

Mathematics is prose in physics papers. Referees read equations as sentences and notice broken
grammar there faster than in the text. This file covers the conventions that govern how equations
and symbols behave in a manuscript.

## Contents

- [Equations are sentences](#equations-are-sentences)
- [Displayed vs. inline](#displayed-vs-inline)
- [Numbering and cross-references](#numbering-and-cross-references)
- [Defining symbols](#defining-symbols)
- [Typographic conventions](#typographic-conventions)
- [Notation hygiene](#notation-hygiene)
- [LaTeX practice](#latex-practice)
- [Field-specific conventions](#field-specific-conventions)
- [Checklist](#checklist)

---

## Equations are sentences

A displayed equation is a grammatical element of the sentence containing it. It takes the punctuation
the sentence needs.

Sentence continues after the equation → comma:

> The energy of the mode is
> $$ E_n = \hbar\omega\left(n + \tfrac{1}{2}\right), $$
> where $n$ is the occupation number and $\omega$ the angular frequency.

Sentence ends at the equation → period:

> Substituting Eq. (2) into Eq. (3) gives the dispersion relation
> $$ \omega^2 = c^2 k^2 + \omega_p^2 . $$

Never leave a displayed equation floating with no punctuation and no lead-in sentence. An equation
dropped between two independent sentences with no grammatical connection is the mathematical
equivalent of a sentence fragment.

**Do not begin a sentence with a symbol.** Write "The quantity $\kappa$ decreases with temperature",
not "$\kappa$ decreases with temperature." A capitalized word must open the sentence; a symbol can be
confused with the end of the previous sentence and, in some symbols, capitalization carries meaning.

**Read the sentence aloud with the equation spoken.** If it does not parse as English, the connection
is broken. "We find that Eq. (5), the temperature dependence is quadratic" fails this test.

---

## Displayed vs. inline

Display an equation when it is referenced later, when it is the object of discussion, when it
contains fractions/integrals/sums that would distort line spacing, or when the journal asks
(PRL explicitly requests that all but the simplest equations be displayed).

Inline is right for short expressions that are read as part of the sentence: $E = mc^2$, $T_c = 92$ K,
$\chi^2/\mathrm{dof} = 1.04$.

Do not display an equation you never refer to again *and* that carries no argumentative weight —
it costs a word budget (at PRL, displayed equations count toward the limit as their word-equivalent)
and interrupts reading.

---

## Numbering and cross-references

- Number only equations you reference. Unnumbered displays are fine and reduce clutter.
- Reference style: **"Eq. (1)"** mid-sentence, **"Equation (1)"** at the start of a sentence. Plural:
  "Eqs. (2) and (3)". Always keep the parentheses around the number.
- In REVTeX, use `\label{eq:dispersion}` and `\eqref{eq:dispersion}` — never hand-typed numbers,
  which break the moment you insert an equation.
- Same rule for other cross-references, with journal-specific abbreviations:
  "Fig. 2", "Figs. 2 and 3", "Table I" (APS uses Roman numerals for tables), "Sec. III", "Ref. [4]",
  "Appendix B". At the start of a sentence these are spelled out: "Figure 2 shows…", "Section III
  describes…". Nature-family style differs (e.g., "Fig. 2" throughout) — check the target.
- Equations in appendices are numbered (A1), (A2), etc., automatically by the class file.

---

## Defining symbols

**Every symbol is defined at or immediately after first appearance**, in the same sentence or the
sentence that follows, using a `where` clause:

> $$ j = \sigma E - D\nabla n , $$
> where $\sigma$ is the electrical conductivity, $D$ the diffusion coefficient, and $n$ the carrier
> density.

Conventions for `where` clauses: no comma before `where`'s list items after the first if the
construction is parallel; drop the repeated verb ("$D$ the diffusion coefficient" rather than
"$D$ is the diffusion coefficient" for each item) to save words; keep the order of the symbols the
same as their order in the equation.

Symbols so standard in the field that definition is noise ($c$, $\hbar$, $k_B$, $e$, $\pi$) can be
left undefined — but state your unit conventions once (see below). Everything specific to your
system gets defined, including subscripts whose meaning is not obvious.

For a paper with heavy formalism, add a **notation table** in an appendix listing symbol, meaning,
and units. This is standard in theory-heavy and instrument papers and referees appreciate it.

---

## Typographic conventions

These follow ISO 80000-2 and IUPAP recommendations and are enforced by copy editors at most physics
journals.

| Element | Style | LaTeX | Example |
|---|---|---|---|
| Variables, physical quantities | *italic* | default math mode | $T$, $E$, $\kappa$ |
| Units | roman (upright) | `\mathrm{}` or `siunitx` | 5 K, 10 nm |
| Vectors | **bold italic** (APS) or arrow | `\bm{B}` / `\vec{B}` | $\bm{B}$ |
| Tensors | bold sans-serif or double-struck (journal-dependent) | | |
| Mathematical operators/functions | roman | `\sin`, `\exp`, `\log`, `\det`, `\Tr` | $\exp(-\beta E)$ |
| Descriptive subscripts (words/abbreviations) | roman | `T_\mathrm{c}` | $T_\mathrm{c}$, $n_\mathrm{e}$ |
| Index subscripts (variables) | italic | `x_i` | $x_i$, $a_{mn}$ |
| Chemical element symbols | roman | `\mathrm{Si}` | SiO₂ |
| Particle names | roman | | $\pi^+$, $e^-$ |
| Numerical constants, digits | roman | | 3.14 |
| Differential d, imaginary i, Euler e | ISO: upright; APS practice: often italic | | pick one, be consistent |
| Transpose, Hermitian conjugate | roman superscript | `^{\mathsf{T}}`, `^{\dagger}` | $M^{\mathsf{T}}$ |

Notes on the ambiguous cases:

- **Differential $d$**: ISO 80000-2 specifies upright ($\mathrm{d}x$); much of the physics literature
  and many APS papers use italic ($dx$). Either is accepted by most physics journals as long as it is
  consistent throughout the manuscript. Astronomy journals lean italic.
- **Vectors**: APS style is bold rather than arrows. Arrows are common in lecture notes and some
  European journals. Do not mix within one paper.
- **Bold in math** requires `\bm` (from the `bm` package, which REVTeX loads) rather than `\mathbf`
  for italic bold Greek and italic bold Latin variables.

---

## Notation hygiene

**One symbol, one meaning, one paper.** The most common notation failure is reusing a symbol —
$\gamma$ as a damping rate in Section II and a Lorentz factor in Section IV. If both are needed,
change one and say so.

**One meaning, one symbol.** The inverse failure: the same quantity written $\Gamma$ in the equations
and $\gamma$ in the figure axis labels. Before submission, grep the manuscript for each symbol and
confirm every occurrence means the same thing, then confirm every figure axis label and legend uses
the manuscript's symbol.

**Avoid symbols that collide visually**: $\nu$ vs. $v$, $\kappa$ vs. $k$, $\ell$ vs. 1, $\rho$ vs.
$p$, $\epsilon$ vs. $\varepsilon$ used for different things. If your system forces a collision, add
a distinguishing subscript rather than trusting the reader's eyesight at 9 pt.

**Declare unit conventions once, early.** "We use natural units, $\hbar = c = 1$." "We work in
Gaussian units." "Unless stated otherwise, energies are in meV." A paper that silently switches
convention between sections is unreviewable.

**Declare sign and metric conventions** where they matter: metric signature $(+,-,-,-)$, the sign of
the Fourier transform exponent, the direction of the current convention, the sign of the coupling in
the Hamiltonian. These are the source of a large fraction of the "I can't reproduce your Eq. (12)"
referee reports.

**Approximations**: use $\approx$ for approximately equal, $\sim$ for order-of-magnitude, $\simeq$
for asymptotically equal, $\propto$ for proportional. These are not interchangeable, and referees in
theory-heavy subfields treat sloppiness here as a signal.

---

## LaTeX practice

```latex
% Preferred alignment environment for multi-line equations
\begin{align}
  \mathcal{H} &= \sum_i \epsilon_i c_i^\dagger c_i
                 + \sum_{ij} t_{ij}\, c_i^\dagger c_j , \label{eq:ham} \\
  \epsilon_i  &= \epsilon_0 + \delta\epsilon_i .
\end{align}
```

- Use `align` / `aligned` / `gather` (amsmath). **Do not use `eqnarray`** — it produces wrong spacing
  around relation symbols and is deprecated.
- `\left( … \right)` for delimiters that must scale; manual `\big`, `\Big` when the automatic sizing
  looks wrong.
- Thin space before units and between a number and a symbol group: `5\,\mathrm{K}`, or use `siunitx`:
  `\qty{5}{\kelvin}`, `\qty{1.2(2)}{\micro\meter}`, `\qtyrange{30}{300}{\kelvin}`.
- `\mathrm{}` for upright text inside math; `\text{}` (amsmath) when the content is prose fragments.
- Define semantic macros for repeated composite objects and use them everywhere:
  `\newcommand{\kperp}{k_{\perp}}`. This makes late notation changes a one-line edit.
- Keep macros few and mnemonic. APS asks that author-defined macros be minimal and included in the
  submitted source; a manuscript built on 80 private macros is painful to copyedit and may be
  returned.
- Break long equations before a relation or binary operator, and align on the relation symbol.
- For equations too wide for a two-column layout, use `widetext` (REVTeX) rather than shrinking the
  font.

---

## Field-specific conventions

**High-energy physics.** Natural units ($\hbar = c = 1$) declared once; metric signature stated;
four-vectors and their index conventions defined; Feynman-diagram conventions specified; cross
sections in barns or pb; masses in GeV/$c^2$ or GeV under natural units.

**Condensed matter.** Lattice constants and Brillouin-zone paths defined ($\Gamma$–X–M); Hamiltonians
given in second quantization with the ordering convention stated; band-structure conventions
(spin-orbit included or not) explicit.

**Astronomy.** CGS and astronomical units are standard: erg, Gauss, parsec, $M_\odot$, $L_\odot$,
Jansky, magnitudes. $\log$ means $\log_{10}$ unless stated. Redshift $z$, cosmological parameters,
and the assumed cosmology ($H_0$, $\Omega_m$, $\Omega_\Lambda$) are stated in the introduction or
methods. AASTeX provides macros for common symbols.

**Quantum information and quantum optics.** Dirac notation with consistent bra-ket spacing
(`\ket{}`, `\bra{}`, `\braket{}{}` via `physics` or `braket` — define once and use throughout rather
than hand-building `|\psi\rangle`). Fix and state: the Pauli convention and whether $\sigma_z$ or
$Z$ is used; qubit ordering in tensor products ($\ket{q_1 q_0}$ vs. $\ket{q_0 q_1}$) and the
resulting matrix ordering; whether $\hbar = 1$; the rotating-frame and rotating-wave approximations
where applied. Distinguish state fidelity from process fidelity and from average gate fidelity, and
give the formula you used — the three differ by known factors and papers routinely compare
incomparable numbers. Define $T_1$, $T_2$, and $T_2^*$ and the sequence used to extract each.
Superoperators, channels, and the Kraus or Lindblad form should be given explicitly rather than
named. For circuits, state the gate set, the connectivity graph, and the compilation target.

**Optics.** Complex field conventions ($e^{-i\omega t}$ vs. $e^{+i\omega t}$) must be declared —
sign errors propagate silently. Jones/Mueller conventions, refractive index sign, and pulse-envelope
definitions (FWHM vs. $1/e^2$) all need stating.

**Plasma physics.** Gaussian units remain common; state the system. Define whether temperatures are
in eV or K and whether $T$ includes the Boltzmann factor.

**Numerics.** State the discretization, the units used internally, and any nondimensionalization
with its scaling relations.

---

## Checklist

Run before submission:

- [ ] Every displayed equation punctuated as part of its sentence
- [ ] No sentence begins with a symbol
- [ ] Every symbol defined at or immediately after first use
- [ ] Symbol usage consistent across text, equations, figures, and tables
- [ ] No symbol carries two meanings
- [ ] Units roman, variables italic, vectors bold (or arrows) consistently
- [ ] Unit system and any natural-unit convention declared once
- [ ] Sign, metric, and Fourier conventions stated where they matter
- [ ] Only referenced equations numbered; all references via `\eqref`, none hand-typed
- [ ] `align` used instead of `eqnarray`
- [ ] $\approx$, $\sim$, $\simeq$, $\propto$ used with their distinct meanings
- [ ] Wide equations handled with `widetext`, not shrunk fonts
- [ ] Author-defined macros minimal and included in the submitted source
