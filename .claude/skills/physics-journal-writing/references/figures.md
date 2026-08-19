# Figures and Tables in Physics Papers

In physics, figures are the argument. A referee reads the abstract, then the figures and captions,
then decides whether to read the text. Design accordingly: the figure sequence should be a complete
proof sketch on its own.

## Contents

- [Plan the figure sequence first](#plan-the-figure-sequence-first)
- [Sizing for journal columns](#sizing-for-journal-columns)
- [Multi-panel figures](#multi-panel-figures)
- [Data presentation](#data-presentation)
- [Color and accessibility](#color-and-accessibility)
- [Axes, labels, and legends](#axes-labels-and-legends)
- [Captions](#captions)
- [Tables](#tables)
- [File formats and technical specs](#file-formats-and-technical-specs)
- [Checklist](#checklist)

---

## Plan the figure sequence first

Before drafting prose, write the figure list as a sequence of questions:

```
Fig. 1  What is the system?          schematic + sample characterization
Fig. 2  What did we observe?         raw signal vs. control
Fig. 3  How does it depend on X?     parameter sweep with model overlay
Fig. 4  What does it mean?           scaling collapse / phase diagram / comparison to prior work
```

If two figures answer the same question, merge them. If a figure answers no question, cut it — at
PRL every figure costs word budget (roughly 170 words for a single-column figure, more for a
two-column one), so a decorative figure directly displaces argument.

**Figure 1 conventions by subfield**: optics and instrument papers open with a setup schematic;
condensed matter often opens with sample structure plus a characterization panel; theory papers open
with the model geometry or phase diagram; astronomy often opens with an image or sky map.

---

## Sizing for journal columns

Design at final printed size. This is the single most common figure failure: a figure drawn at
20 cm wide and shrunk to 8.6 cm has 4 pt axis labels.

| Layout | Typical width | Where |
|---|---|---|
| Single column | ~8.6 cm (3.4 in) | PRL, PRB, most two-column journals |
| Double column | ~17.8 cm (7.0 in) | full-width figures in two-column journals |
| Nature-family single/double | ~89 mm / ~183 mm | Nature journals |
| AAS single/double | ~3.5 in / ~7.3 in | ApJ, AJ (verify against AASTeX guide) |

Rules that follow from this:

- **Fonts inside the figure must match the caption size at final scale** — roughly 7–9 pt. Set the
  figure's font size explicitly rather than scaling.
- **Line weights ≥ 0.5 pt** at final size; data lines heavier than axis lines.
- **Marker sizes** large enough to distinguish shapes at print size; distinguish by *shape*, not only
  by color.
- Print the figure at actual size on paper and read it before submitting. If you squint, the referee
  will too.

---

## Multi-panel figures

Standard in physics and usually preferable to several separate figures.

- Label panels **(a), (b), (c)** in the same position in each panel (top-left is conventional), in
  bold or plain per journal style, at the same size.
- Reference panels in text as "Fig. 2(a)" or "Figs. 2(a) and 2(b)".
- **Share axes where possible** — a common x-axis with stacked panels and no repeated tick labels
  saves space and makes the comparison visible.
- Keep panel aspect ratios and font sizes identical across panels; mismatched panels read as
  assembled rather than designed.
- **Insets** are physics-standard for showing a zoom, a schematic, or a derived quantity. Give the
  inset its own axis labels, keep them legible, and describe it in the caption.
- Align panels on a grid; ragged edges and inconsistent margins are the visual signature of a rushed
  figure.

---

## Data presentation

**Show the data.** Physics referees are suspicious of figures that show only fits or only binned
means. Plot points with error bars, then overlay the model as a line.

- **Distinguish data from theory unambiguously**: markers for data, lines for models/fits, stated in
  the caption and in the legend. Theory curves overlaid on data must be distinguishable by line style
  as well as color.
- **Error bars on every data point** (or a statement in the caption that errors are smaller than the
  markers), with their meaning defined.
- **Log axes** when the data span decades — and label them so the decades are readable. Log-log plots
  with a fitted power law should show the fitted exponent in the panel or caption.
- **Residuals panel** below the main panel when a fit's quality is part of the claim.
- **Normalization and offsets**: if curves are offset for clarity, say so in the caption and mark the
  zero of each.
- **Don't manipulate images.** Adjustments to brightness/contrast must be linear and applied to the
  whole image; any non-linear or region-specific processing must be disclosed. Splicing gel/image
  lanes or micrograph regions without a visible divider is misconduct.
- **Show controls and null results** in the same figure as the signal wherever possible; a signal
  panel without its control is the most common referee complaint about a results figure.

---

## Color and accessibility

Roughly 1 in 12 male readers has a red–green color vision deficiency, and many readers print in
grayscale.

- **Never encode information by color alone.** Pair color with line style, marker shape, or direct
  labeling.
- **Avoid the rainbow/jet colormap.** It introduces false perceptual boundaries and fails in
  grayscale. Use perceptually uniform maps: viridis, magma, cividis, or for diverging data a
  balanced map like coolwarm/RdBu with a clearly marked midpoint.
- **Avoid red/green pairs.** Blue/orange, blue/red, and black/orange are safe defaults.
- **Check in grayscale** and with a color-vision simulator before submitting.
- **Colorbars** need a label with units and, for log scales, explicit decade ticks.
- Keep the palette consistent across all figures in the paper: if blue means "theory" in Fig. 2, blue
  means "theory" in Fig. 4.

---

## Axes, labels, and legends

- **Every axis labeled with a quantity and a unit**, in the same notation as the text. If the text
  calls it $\kappa$, the axis says $\kappa$ (W m⁻¹ K⁻¹), not "thermal conductivity (W/m/K)".
- Use **quantity/unit** style consistently: `T (K)` or `T / K` — one or the other across the paper.
- **Tick labels**: enough to read the scale, not so many they crowd. Avoid tick labels with more
  significant digits than the data justify.
- **Legends** inside the plotting area when space allows, without obscuring data; or direct labeling
  of curves, which is often clearer than a legend box.
- **Arrows and annotations** to point at the feature you discuss in the text — this actively guides
  the reader and costs no words.
- Match figure notation exactly to manuscript notation. A symbol mismatch between text and figure is
  a guaranteed referee comment.

---

## Captions

A physics caption is a self-contained paragraph. Assume the reader has not read the text.

**Structure:**

1. **Title phrase** — a noun phrase stating what the figure shows (APS style puts this first, in the
   same font; Nature style often bolds it).
2. **What is plotted** — panel by panel, with symbols and conditions.
3. **What the lines/markers mean** — data vs. model, parameter values.
4. **What the error bars mean** — always.
5. **Experimental conditions** needed to interpret the panel — temperature, field, wavelength, etc.
6. *(Optional)* the take-away, if the journal's style permits interpretation in captions.

**Example:**

> FIG. 2. Temperature dependence of the in-plane thermal conductivity. (a) $\kappa$ measured on three
> monolayer WSe₂ devices (circles, squares, triangles) from 30 to 300 K at $10^{-6}$ mbar. Solid line:
> first-principles prediction including only phonon–phonon scattering [12]; dashed line: same
> calculation with point-defect scattering at the measured density $n_d = 4\times10^{12}$ cm⁻². (b)
> Ratio of measured to predicted $\kappa$ versus $n_d$ for twelve devices. Error bars denote one
> standard deviation over five thermal cycles; where not visible they are smaller than the markers.

**Common caption failures**: "Thermal conductivity vs. temperature." (tells the reader nothing the
axes don't); undefined symbols; no error-bar definition; interpretation in the caption that
contradicts the text.

---

## Tables

Use a table when exact values matter, when the reader will compare specific numbers, or when
presenting a systematic budget or a comparison to prior work. Use a figure for trends.

- **APS numbers tables with Roman numerals** (Table I, Table II); Nature and AAS use Arabic.
- Caption goes **above** the table in most physics styles (below for figures).
- **Column headers carry units**: `T (K)`, `κ (W m⁻¹ K⁻¹)`.
- **Align on the decimal point** (`\usepackage{dcolumn}` with REVTeX, or `siunitx`'s `S` column).
- **Minimal rules**: `booktabs` (`\toprule`, `\midrule`, `\bottomrule`); no vertical rules; no
  gridlines.
- **Uncertainties in the cell**, using one consistent form: `42(5)` or `42 ± 5`.
- **Footnotes** for per-cell qualifications; define abbreviations in the caption or a footnote.
- A **comparison-to-prior-work table** is one of the most persuasive elements available in a physics
  paper: your value alongside the best previous values, with references and methods. If you claim an
  improvement, show it in a table.
- Large tables belong in an appendix, Supplemental Material, or — for astronomy — a machine-readable
  table with a representative excerpt in the article.

---

## File formats and technical specs

- **Vector formats for line art**: PDF or EPS. Never a screenshot, never a rasterized plot.
- **Raster only for images** (micrographs, camera frames, sky images): TIFF or PNG at ≥ 300 dpi at
  final size; 600 dpi for line-heavy raster content. JPEG artifacts are visible on scientific images
  and should be avoided.
- **Fonts embedded** in PDFs; use Type 1 or TrueType outlines. `matplotlib`: set
  `pdf.fonttype = 42` to embed properly.
- **One figure per file**, named `fig1.pdf`, `fig2a.pdf`, matching the manuscript numbering.
- Keep the **generating script** with the paper source so the figure can be regenerated when a
  referee asks for a changed axis range. This is also what makes the data-availability statement
  honest.
- Check the compiled PDF at 100% zoom and at print size before submitting; check that no figure
  overflows the column.

---

## Checklist

- [ ] Figure sequence tells the story without the text
- [ ] Each figure answers one question; no decorative figures
- [ ] Designed at final printed width; fonts 7–9 pt at that size
- [ ] Panels labeled (a), (b), … consistently; referenced correctly in text
- [ ] Data as markers, models as lines, distinguishable in grayscale
- [ ] Error bars present and their meaning stated in the caption
- [ ] No rainbow colormap; no information encoded by color alone
- [ ] Axis labels carry quantity and unit, matching manuscript notation
- [ ] Captions self-contained: what, how, conditions, error bars
- [ ] Tables use booktabs rules, decimal alignment, units in headers
- [ ] Comparison-to-prior-work table included if novelty is claimed
- [ ] Vector PDF/EPS for line art, ≥300 dpi raster for images, fonts embedded
- [ ] Every figure referenced in the text, in order
