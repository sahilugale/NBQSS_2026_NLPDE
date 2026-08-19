# PRX Quantum manuscript

**The Price of Linearity: Carleman–QSVT, Variational, and Analog Routes to Quantum Simulation of
Nonlinear Partial Differential Equations**

A single manuscript combining the three independent sources in this repository into one argument,
written in PRX Quantum style (REVTeX 4.2, numbered sections, popular summary, unlimited length).

```bash
export PATH=/usr/local/texlive/2026/bin/x86_64-linux:$PATH
pdflatex main.tex && pdflatex main.tex     # 14 pages, compiles clean
```

## The combining idea

The three sources answer the same question from three directions, so the paper is organized around
that question rather than around the sources:

> A quantum computer evolves states linearly. A nonlinear PDE must therefore be embedded in a linear
> problem first. **What does that embedding cost, and what happens if you decline to pay it?**

| Section | Source | Role in the argument |
|---|---|---|
| §II Shared problem | `report/` | The proofs both digital routes depend on (conservative closure, forward-Euler energy injection, Reynolds resolution) |
| §III Route 1, as built | `report/` | Carleman–QSVT **measured**: circuits built, transpiled, verified |
| §IV What Route 1 costs | `scaling_analysis/` | Carleman–QSVT **projected**: error budget, Re < π/2 threshold, 10¹² gates |
| §V Route 2 | `report/` | Variational: declines the embedding, runs on present hardware |
| §VI Route 3 | `references/Niels_Bohr_Student_Challenge.pdf` | DDCL analog: declines the digital circuit |
| §VII Comparison | all three | Where each route's cost actually sits |

Two threads tie the sources together and are not present in any one of them alone:

1. **The Cole–Hopf caveat closes a loop.** The scaling analysis notes that Burgers is linearizable in
   closed form, so a Burgers demonstration cannot by itself show a method handles nonlinearity, and
   that "the correct control experiment is a PDE with no linearising substitution, such as
   Korteweg–de Vries." The implementation report carries KdV through every stage. Stated together,
   this becomes a methodological point about benchmark choice (§IV F).
2. **The Reynolds number is the common axis.** It is the binding Carleman convergence constraint in
   the scaling analysis (Re < π/2), the grid-resolution constraint in the report (Re_Δ ≲ 2), and a
   directly tunable experimental knob in the DDCL (ν_eff = K_eff a² cos φ). Same quantity, three
   different roles.

## Provenance and honesty notes

- **Measured vs. projected is labeled throughout**, per PRX Quantum's expectations. Tables IV, VII,
  VIII are marked *Measured*; Tables V, VI and Figs. 4–6 are marked *Projected*. §V F states
  explicitly that noisy runs use no error mitigation and no post-selection, and that they take
  overlap signs from the ideal simulation.
- **Two references were taken from the companion analysis's bibliography** rather than
  independently re-verified against their original sources for this manuscript: `Wu2025` (SIAM
  J. Sci. Comput. **47**, A943) and `GonzalezConde2025` (Phys. Rev. Research **7**, 023254). Worth
  a check before submission.
- **The REVTeX substyle is `prx`, not `prxquantum`** — REVTeX 4.2 has no dedicated PRX Quantum
  substyle in this installation, and PRX Quantum shares PRX formatting. Flagged in a comment at the
  top of `main.tex`. Verify against current PRX Quantum author guidelines before submission,
  along with the popular-summary length limit.
- **`Nadav's home institution`** is still a placeholder in the author block, inherited from
  `report/report.tex`.
- **The DDCL section claims only what the source supports**: the platform, the mapping derivation,
  and the stationary `tanh` profile as the accessible observable. §VI C states plainly that no
  time-resolved analog trajectory is presented, that the phase-only reduction has stated validity
  conditions, and that the platform is not programmable across equations.

## Figures

Fig. 1 is a TikZ pipeline diagram drawn inline in `main.tex` (no external file) showing all three
routes branching off the shared discretization, with each route's cost annotated at the stage where
it accrues and marked fixable vs. fundamental.

### Unified palette

Every figure — notebooks, scaling analysis, and the TikZ schematic — draws from one palette defined
in [`../plot_style.py`](../plot_style.py), mirrored as `\definecolor` entries in `main.tex`. Hues
carry a fixed *meaning* rather than an index, so the same color means the same thing everywhere:

| Color | Hex | Means |
|---|---|---|
| gray | `#8A9199` | classical reference / exact solution |
| dark blue | `#1F4E8C` | Route 1 (Carleman–QSVT), primary — dense encoding, coherent permutation |
| light blue | `#7FA9D8` | Route 1, secondary — Pauli-LCU, sparse oracle |
| teal | `#14796B` | Route 2 (variational), ideal quantum |
| orange | `#D2691E` | real hardware / physical world — noisy readout, analog platform |
| red | `#B3261E` | reserved for the one fundamental obstruction, `Re < π/2` |

The carpet plots use a diverging colormap built from the same blue and orange.

### Regenerating

```bash
python3 ../run_notebooks.py     # 4 notebooks -> figures/ (propagation, time-marching)
python3 make_carpets.py         # -> figures/fig_*_carpet.pdf
cd ../scaling_analysis && python3 figs.py && cp fig_*.pdf ../prx_quantum/figures/
```

The notebooks now `savefig` straight into `figures/`, so they are the source of truth for the
propagation and time-marching panels. `make_carpets.py` covers the two space–time surfaces, which no
notebook produces. The DDCL images (`ddcl_1.png`, `ddcl_2.png`) were extracted from the source PDF.

## What the gate counts in Table IV do and don't mean

Worth knowing before quoting the 2.6×10⁶ figure. Our dense encoding
([`qsvt_toolkit.py:77`](../carleman_qsvt/qsvt_toolkit.py#L77)) assembles the full 2^n_w × 2^n_w
dilation explicitly and hands it to Qiskit as an opaque `UnitaryGate`, so the Carleman matrix's
sparsity and Kronecker structure are destroyed before the transpiler ever sees them; the transpiler
falls back on generic unitary synthesis, which is exactly the measured O(4^n_w). The QSVT projector
layers were deliberately *not* built this way (multi-controlled phase gates instead), so the blow-up
is localized to the block-encoding layers. §III C states this explicitly so the number isn't read as
intrinsic to Carleman–QSVT.

Relatedly, the **coherent-permutation and sparse-oracle encodings are not implemented as circuits**
anywhere in this repository. `scaling_analysis/kappa.py` computes their subnormalization constants
α directly from the assembled classical matrix (α_cp = sum of |value| over distinct
value/diagonal-offset pairs; α_sp = s·‖L‖_max). Those are exact cost-model constants, not measured
circuit resources — the Fig. 5 caption says so.
