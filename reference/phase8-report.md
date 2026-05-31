# Phase 8: Generate Publication-Quality Report

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE — once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Purpose
Compile all results into a single consolidated report covering **all globally claimed operators** from **all models**.

## Step 8.1: Output Format Selection

```bash
which pdflatex
```

| Condition | Format |
|-----------|--------|
| `pdflatex` exists | LaTeX → PDF |
| Not available | HTML (self-contained, MathJax + base64 images) |

### HTML Fallback

If LaTeX is unavailable, generate a self-contained HTML file:
- Use MathJax CDN for formula rendering: `<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>`
- Embed all figures as base64-encoded PDFs (or regenerate as PNG for HTML): `<img src="data:image/png;base64,...">`
- Include all tables inline
- Structure with `<h1>`–`<h3>` matching the section numbering in Step 8.2
- CSS: minimal, readable, print-friendly

## Step 8.2: Report Structure

Follow the structure in [`reference/report-writing-guide.md`](reference/report-writing-guide.md):

1. **Abstract**: one-paragraph summary
2. **Introduction**: motivation, process, collider at `energy` TeV, `luminosity` fb⁻¹, models used
3. **Theoretical Framework**: effective Lagrangian, operator definitions, unitarity bounds
   - **Model Summary Table**: List all models used and their claimed operators
     | Model | Claimed Operators (global indices) |
     |-------|-----------------------------------|
     | AQGCm_UFO | o_1, o_2 |
     | AQGCs_UFO | o_3, o_4, o_5 |
4. **Event Generation & Data Preparation**: MC setup, dataset composition, event counts, scan points, feature list
   - Note: ML training uses the anchor operator (`o_1` from `{anchor_model}`)
   - Include **Feynman diagrams** (see Step 8.6 below)
5. **Machine Learning Methodology**: algorithms, score functions, training setup, AUC comparison, score distributions
   - Training performed on anchor operator only; algorithms applied universally
6. **Event Selection Optimization**: per-algorithm threshold optimization (using anchor operator), fit plots, threshold comparison
7. **Numerical Results & Expected Constraints**: cross-section fitting, significance formula, final constraint table (best algorithm only, ALL operators), algorithm comparison band plot
   - **Constraint table must include ALL globally claimed operators** with their source models
8. **Conclusions**: summary, physical interpretation, outlook
9. **References**: mandatory toolchain citations with DOI and arXiv

## Step 8.3: Required Figures (PDF Vector Format)

**All figures must be generated as PDF for vector quality.** Use `plt.savefig(..., format='pdf')`.

| Figure | Source |
|--------|--------|
| ROC curves | `results/plots/roc_anchor.pdf` |
| Score distributions | `results/plots/score_dist_anchor_*alg*.pdf` (all algorithms) |
| Threshold optimization comparison | `results/plots/threshold_comparison.pdf` |
| Cross-section fits | `results/plots/csfit_plot_o_*_{alg}*.pdf` (all algorithms, all operators) |
| Algorithm comparison | `results/plots/algorithm_comparison.pdf` |

## Step 8.4: Algorithm Comparison Section (Required)

### AUC Comparison Table (Top 3 Only)

**The report presents only the best 3 algorithms** (ranked by narrowest constraint width at S=2). The full pool and expansion history are recorded in `algorithm_comparison.json` but not shown in the report.

Since training is done on the anchor operator only, there is a single AUC value per algorithm:

| Algorithm | Anchor AUC |
|-----------|-----------|
| Algorithm 1 | 0.987 |
| Algorithm 2 | 0.954 |
| Algorithm 3 | 0.912 |

### Best Algorithm Selection

| Operator | Source Model | Best Algorithm | Selection Criterion | S=2 Width |
|----------|-------------|---------------|---------------------|-----------|
| o_1 | AQGCm_UFO | Algorithm 1 | Narrowest constraint width | 0.045 |
| o_2 | AQGCm_UFO | Algorithm 2 | Narrowest constraint width | 0.078 |
| o_3 | AQGCs_UFO | Algorithm 1 | Narrowest constraint width | 0.052 |
| ... | ... | ... | ... | ... |

**Important**: The best algorithm is selected by **narrowest constraint width at S=2**, NOT highest AUC. Report when these differ.

### Algorithm Comparison Plot (Top 3 Only)

**Band plot** showing the constraint intervals $[f_{\min}, f_{\max}]$ for the top 3 algorithms side-by-side. For each algorithm, draw a horizontal band from $f_{\min}$ to $f_{\max}$. The best algorithm (narrowest band) should be highlighted.

One plot per operator, or a combined plot showing all operators.

## Step 8.5: Required Formulas (LaTeX)

All formulas must be rendered in LaTeX. `L` denotes physics luminosity in pb⁻¹.

$$
N_{\mathrm{SM}} = L \cdot cs_{\mathrm{sm}}
$$

$$
N_{\mathrm{NP}}(c) = \frac{c^2}{c_0^2} \cdot L \cdot cs_{\mathrm{np}}
$$

$$
S_{\mathrm{stat}} = \sqrt{2 \left[ (N_{\mathrm{bg}} + N_{\mathrm{sig}}) \ln\left(1 + \frac{N_{\mathrm{sig}}}{N_{\mathrm{bg}}}\right) - N_{\mathrm{sig}} \right]}
$$

$$
\sigma(f) = \sigma_{\mathrm{SM}} + f \cdot \sigma_{\mathrm{int}} + f^{2} \cdot \sigma_{\mathrm{NP}}
$$

## Step 8.6: Feynman Diagrams (Required)

Include representative Feynman diagrams from both the SM (`NP=0`) and NP (`NP>0`) process directories to illustrate the physics process. Use the **anchor model's** process directories.

### Collecting Diagrams

MG5 stores Feynman diagrams in each process directory under `SubProcesses/`:

| Process Type | Location | Files |
|--------------|----------|-------|
| SM baseline | `{mg5path}/{folder_base}_{anchor_model}_p2_SM/SubProcesses/P*/` | `matrix*.jpg`, `matrix*.png`, `matrix*.eps`, or `matrix*.ps` |
| NP (EFT) | `{mg5path}/{folder_base}_{anchor_model}_p3_NP/SubProcesses/P*/` | `matrix*.jpg`, `matrix*.png`, `matrix*.eps`, or `matrix*.ps` |

The `diagrams.html` file in each `SubProcesses/P*/` directory is an index that lists all diagrams with their process labels (e.g., `e+ e- > a u u~ NP=0 @1`).

### Selection Criteria

Select **2–4 representative diagrams per channel** (SM and NP):

1. Open `diagrams.html` in the SM process directory to see the list of subprocesses
2. Pick one subprocess (e.g., `e+ e- > a u u~`) and copy its first 2–3 `matrix*.jpg` files
3. Repeat for the NP process directory — pick the same or a similar subprocess
4. Convert to PDF if needed for LaTeX reports: `convert matrix11.jpg matrix11.pdf` or embed JPG directly in HTML

### Report Placement

Place the diagrams in **Section 4 (Event Generation & Data Preparation)** of the report:

- Label SM diagrams as "SM process: $e^+ e^- \\to \\gamma j j$ (NP=0)"
- Label NP diagrams as "NP process: $e^+ e^- \\to \\gamma j j$ (NP>0)"
- Include a brief caption explaining that the NP diagrams include the EFT vertices from the `{anchor_model}` model

### File Collection

Copy selected diagrams to the results directory for archival:

```
results/data/feynman_diagrams/
  sm_matrix11.jpg      # SM diagram 1
  sm_matrix12.jpg      # SM diagram 2
  np_matrix11.jpg      # NP diagram 1
  np_matrix12.jpg      # NP diagram 2
```

## Output

> **Multi-run note:** In multi-run mode, all `results/` paths below are prefixed with the run subdirectory (e.g., `results/E10_L1000/report.pdf`). See [`SKILL.md`](../SKILL.md) Rule 11.

```
results/report.pdf   # if pdflatex available
results/report.html  # otherwise
```

Each report covers only its own `(energy, luminosity)` combination.

## Validation

- Report event counts must match actual debug-adjusted counts
- Report constraint table must match Phase 7 `constraint_table.json`
- Report must include ALL globally claimed operators with their source models
- Algorithm comparison data must match Phase 7 `algorithm_selection.json`
- All algorithms trained in Phase 5 must appear in the comparison section
- All figures in report must be PDF vector format
- All formulas must be LaTeX-rendered
