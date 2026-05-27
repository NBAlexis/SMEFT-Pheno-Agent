# Report Writing Guide

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE — once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Purpose

Professional HEP reports follow a standardized structure. This guide defines the expected content, figures, formulas, and citations for the final report, derived from published SMEFT/aQGC phenomenology papers.

## Report Structure

All papers follow this order. Do not deviate:

```
1. Abstract
2. Introduction
3. Theoretical Framework
4. Event Generation & Data Preparation
5. Machine Learning Methodology
6. Event Selection Optimization
7. Numerical Results & Expected Constraints
8. Conclusions
9. References
```

---

## Section 1: Abstract

**Content:**
- One-paragraph summary of the entire study
- Process studied, collider energy, luminosity
- ML algorithms compared and the best-performing one
- Key result: best expected constraint(s) at a specific significance level

**Example structure:**
> "We study anomalous quartic gauge couplings in the process [process] at a [energy] TeV [collider] with [luminosity] fb⁻¹ integrated luminosity. We compare [list algorithms] for event selection optimization. The [best algorithm] achieves the tightest constraints, with [best constraint] at [S]σ."

---

## Section 2: Introduction

**Required content:**
1. **Motivation**: Why SMEFT/aQGCs are interesting (dimension-6/8 operators, electroweak symmetry breaking)
2. **Process justification**: Why this specific final state is sensitive to the operators
3. **Limitation of cut-based methods**: Traditional rectangular cuts are suboptimal for multi-dimensional kinematic distributions
4. **ML advantage**: Machine learning can exploit correlations in high-dimensional feature space
5. **Multi-algorithm comparison motivation**: Different algorithms may capture different aspects of the phase space; comparing them provides robustness
6. **Paper organization**: Brief paragraph listing the remaining sections

**Never include:**
- Detailed formulas (save for Theoretical Framework)
- Algorithm implementation details (save for Methodology)
- Numerical results (save for Results)

**Multi-run note:** If this is one of multiple `(energy, luminosity)` combinations, state this explicitly: "This section presents results for a [energy] TeV collider with [luminosity] fb⁻¹ integrated luminosity. Additional combinations are reported in companion analyses."

---

## Section 3: Theoretical Framework

**Required content:**

### 3.1 Effective Lagrangian
- Present the Lagrangian with operator definitions
- Number each operator equation (e.g., Eq. 1)
- Define each Wilson coefficient symbol clearly

### 3.2 Operator Definitions
- Table of operators with their mathematical forms
- Specify which operators are probed in this study
- Reference the UFO model name used in MG5

### 3.3 Unitarity Bounds (if applicable)
- Table of theoretical constraints on Wilson coefficients
- These are bounds from perturbative unitarity, not experimental constraints
- Present as: |c_i| < bound_value

**Example table format:**

| Operator | Unitarity Bound |
|----------|-----------------|
| o1 | |f_1| < X |
| o2 | |f_2| < Y |

---

## Section 4: Event Generation & Data Preparation

**Required content:**

### 4.1 Monte Carlo Setup
- MadGraph5 version and model name
- Collision energy in TeV
- PDF set used (if hadron collider)
- Event generation tool chain: MG5 → [Pythia/Delphes] → LHCO
- Jet algorithm and parameters (if jets involved)

**Mandatory citation when mentioning dataset generation:**
- Must cite MadGraph5: J. Alwall et al., JHEP 07 (2014) 079, arXiv:1405.0301
- Must cite FeynRules: N. D. Christensen and C. Duhr, Comput. Phys. Commun. 180, 1614 (2009), arXiv:0806.4194
- Must cite UFO: C. Degrande et al., Comput. Phys. Commun. 183, 1201 (2012), arXiv:1108.2040
- Must cite Delphes (if used): J. de Favereau et al., JHEP 02, 057 (2014), arXiv:1307.6346
- Must cite MLAnalysis: Y.-C. Guo et al., Comput. Phys. Commun. 294, 108957 (2024), arXiv:2305.00964
- Must cite Pythia (if proton initial state or hadronization): T. Sjöstrand et al., Comput. Phys. Commun. 191, 159 (2015), arXiv:1410.3012
- Must cite LHAPDF (if proton initial state): A. Buckley et al., Eur. Phys. J. C 75, 132 (2015), arXiv:1412.7420

### 4.1a Feynman Diagrams

Include representative Feynman diagrams from both the SM (`NP=0`) and NP (`NP>0`) process directories. These diagrams illustrate the underlying physics and the EFT vertices introduced by the model.

**Required:**
- 2–4 SM diagrams showing the process without EFT contributions
- 2–4 NP diagrams showing the same process with EFT vertices
- Each diagram set labeled clearly: "SM (NP=0)" and "NP (NP>0)"
- Brief caption explaining the difference (e.g., "The NP diagrams include additional vertices from the `{model}` dimension-6/8 operators")

**Source:** MG5 generates diagrams in `SubProcesses/P*/diagrams.html` and `matrix*.jpg`/`matrix*.png`/`matrix*.eps`.

### 4.2 Dataset Composition (Must Be Explicit)

Every paper explicitly states what each dataset contains. Follow this standard:

**SM Sample (Pure Standard Model)**
- Purpose: training background distribution / baseline cross-section
- Events generated: [actual count]
- Events after cuts: [count]
- Composition: **SM only** (no NP, no interference)

**NP Samples (Pure New Physics)**
- Purpose: training signal distribution / computing discrimination power
- For each operator: NP=2 at $c = c_0$
- Events generated per operator: [actual count]
- Events after cuts: [count]
- Composition: **NP only** (SM contributions set to zero via NP=2)

**Scan Samples (SM + NP + Interference)**
- Purpose: fitting cross-section vs coefficient and computing constraints
- Number of scan points: 11 (including $c = 0$)
- Scan coefficient values: explicitly list (e.g., $f = 0, \pm 0.1c_1, \pm 0.2c_1, \dots, \pm c_1$)
- Events generated per scan point: [actual count]
- Composition: **SM + NP + interference** (generated with NP=2 and rescaled)

**Example dataset table:**

| Dataset | Purpose | Events Generated | Events After Cuts | Composition |
|---------|---------|------------------|-------------------|-------------|
| SM | Training background / baseline | 1,000,000 | 832,056 | SM only |
| NP (o1) | Training signal | 300,000 | 245,000 | NP only |
| Scan (o1) | Cross-section fit | 100,000 × 11 | 83,000 × 11 | SM + NP + int. |

**Dataset definition requirements (must appear in report):**

1. **Final-state particle multiplicity requirement**: State explicitly how many of each particle type are required (e.g., "at least 2 leptons and 2 jets").
2. **Events after selection**: Report the exact number of events surviving the multiplicity cut for each dataset.
3. **Feature definitions**: For every feature used in the ML classifier, provide:
   - The physical quantity (e.g., transverse momentum, pseudorapidity, invariant mass)
   - The symbol or name
   - Which particle(s) it corresponds to (e.g., "leading lepton pT")
   - The formula if it is a derived quantity (e.g., missing transverse energy = sqrt(px² + py²))

**Example feature table:**

| Feature | Symbol | Description | Formula |
|---------|--------|-------------|---------|
| Leading lepton energy | E_l1 | Energy of highest-E lepton | — |
| Leading lepton pT | pT_l1 | Transverse momentum of highest-E lepton | sqrt(px² + py²) |
| Subleading lepton energy | E_l2 | Energy of second-highest-E lepton | — |
| Missing momentum x | miss_px | x-component of missing momentum | — |
| Missing momentum y | miss_py | y-component of missing momentum | — |
| Missing ET | MET | Missing transverse energy | sqrt(miss_px² + miss_py²) |

### 4.3 Scan Coefficient List

Present the scan points in a table:

| Point | Coefficient Value |
|-------|-------------------|
| 0 | $f = 0$ |
| 1 | $f = -c_1$ |
| 2 | $f = -0.8c_1$ |
| ... | ... |
| 10 | $f = +c_1$ |

### 4.4 Feature Extraction
- List all kinematic observables used as ML features
- Justify why these observables are sensitive to new physics
- Include: pT, eta, phi, invariant masses, angular separations, MET, etc.
- Present in a table:

| Feature | Symbol | Description |
|---------|--------|-------------|
| Leading lepton pT | pT_l1 | Transverse momentum of highest-pT lepton |

---

## Section 5: Machine Learning Methodology

**Required content:**

### 5.1 Algorithms Overview
- List **all** algorithms tested (e.g., {alg1}, {alg2}, {alg3} from the user-specified or default candidate set)
- Brief explanation of each algorithm's principle
- Why each is suitable for this problem

### 5.2 Score Function Definitions

For **each algorithm**, give the explicit mathematical definition of its score function. This is required for reproducibility.

**Algorithm 1: {alg1}**

Define the score function for {alg1} generically. For example, if {alg1} is a gradient-boosted tree ensemble, its additive model is:

$$
F_M(\mathbf{x}) = \sum_{m=1}^{M} \gamma_m h_m(\mathbf{x})
$$

where $h_m(\mathbf{x})$ is the $m$-th weak learner and $\gamma_m$ is its weight. The classification score is then:

$$
s(\mathbf{x}) = \frac{1}{1 + \exp(-F_M(\mathbf{x}))}
$$

**Algorithm 2: {alg2}**

Define the score function for {alg2} generically. For example, if {alg2} is a kernel-based classifier, its decision function is:

$$
f(\mathbf{x}) = \sum_{i=1}^{N} \alpha_i y_i K(\mathbf{x}_i, \mathbf{x}) + b
$$

where $K(\cdot, \cdot)$ is the kernel function, $\alpha_i$ are the Lagrange multipliers, and $b$ is the bias. The probability score is computed via Platt scaling:

$$
s(\mathbf{x}) = \frac{1}{1 + \exp(A \cdot f(\mathbf{x}) + B)}
$$

where $A$ and $B$ are fitted parameters.

**Algorithm 3: {alg3}**

Define the score function for {alg3} generically. For example, if {alg3} is an anomaly-detection-based algorithm, its score is derived from the average path length $E(h(\mathbf{x}))$:

$$
s(\mathbf{x}, n) = 2^{-\frac{E(h(\mathbf{x}))}{c(n)}}
$$

where $c(n) = 2H(n-1) - 2(n-1)/n$ is the average path length of unsuccessful search in a binary search tree, and $H(i)$ is the $i$-th harmonic number. Higher scores indicate more anomalous (NP-like) events.

### 5.3 Training Setup
- Training sample composition (SM vs NP events)
- Feature scaling/normalization method
- Hyperparameter values per algorithm (table format)
- Cross-validation strategy if used

### 5.4 AUC Comparison
- Present ROC curves for all algorithms (combined plot or individual)
- Table of AUC values:

| Algorithm | o1 AUC | o2 AUC | ... |
|-----------|--------|--------|-----|
| Algorithm 1 | 0.987 | 0.965 | ... |
| Algorithm 2 | 0.954 | 0.943 | ... |
| Algorithm 3 | 0.912 | 0.901 | ... |

### 5.5 Score Distributions
- Show score distributions for **all algorithms** (SM vs NP)
- Explain: higher scores = more NP-like
- Can be arranged as a multi-panel figure

---

## Section 6: Event Selection Optimization

**Required content:**

### 6.1 Per-Algorithm Threshold Optimization

For **each algorithm** independently:
1. Scan threshold $t$ on $[0, 1]$
2. For each $t$: apply cut, fit quadratic cross-section, compute expected constraint width $f_{\max} - f_{\min}$ at $S=2$
3. Select $t$ that **minimizes constraint width**

**Optimization metric is constraint width, NOT significance.** Significance is used only for computing the constraints after threshold selection.

### 6.2 Threshold Comparison Plot
- Multi-panel or overlay plot showing constraint width vs threshold for all algorithms
- Mark each algorithm's optimal threshold

### 6.3 Cut Efficiency Table (Per Algorithm)
- Present efficiencies before and after selection for each algorithm:

| Algorithm | $\varepsilon_{\mathrm{SM}}$ | $\varepsilon_{\mathrm{NP}}$ (o1) | $\varepsilon_{\mathrm{NP}}$ (o2) | ... |
|-----------|------------------------------|-------------------------------------|-------------------------------------|-----|
| Algorithm 1 | X% | Y% | Z% | ... |
| Algorithm 2 | ... | ... | ... | ... |

---

## Section 7: Numerical Results

**Required content:**

### 7.1 Cross-Section Fitting
- State the fitting formula explicitly in LaTeX:

$$
\sigma(f) = \sigma_{\mathrm{SM}} + f \cdot \sigma_{\mathrm{int}} + f^{2} \cdot \sigma_{\mathrm{NP}}
$$

- Show fit parameters per algorithm per operator in tables (or appendix for brevity)
- Plot: fitted cross-section vs coefficient value with data points
- Mark the 11 scan points on the plot
- Include fit plots for **all algorithms** (can place some in appendix)

### 7.2 Signal Significance

State the formula used in LaTeX. Use ONE of:

**Standard formula (simpler):**
$$
S_{\mathrm{stat}} = \frac{N_{\mathrm{sig}}}{\sqrt{N_{\mathrm{SM}} + N_{\mathrm{sig}}}}
$$

**Asimov formula (more accurate for low stats, preferred):**
$$
S_{\mathrm{stat}} = \sqrt{2 \left[ (N_{\mathrm{bg}} + N_{\mathrm{s}}) \ln\left(1 + \frac{N_{\mathrm{s}}}{N_{\mathrm{bg}}}\right) - N_{\mathrm{s}} \right]}
$$

**Symbol definitions (mandatory — every symbol must be defined):**

| Symbol | Definition | Formula |
|--------|------------|---------|
| $L$ | Integrated luminosity | $L = \ell \times 1000$ (fb$^{-1}$ → pb$^{-1}$) |
| $\sigma_{\mathrm{SM}}$ | SM cross-section after cuts | From fit: $\sigma_{\mathrm{SM}} = \mathrm{csfit}_{\mathrm{sm}}$ |
| $\sigma(f)$ | Total cross-section at coefficient $f$ | $\sigma(f) = \sigma_{\mathrm{SM}} + f \cdot \sigma_{\mathrm{int}} + f^{2} \cdot \sigma_{\mathrm{NP}}$ |
| $N_{\mathrm{bg}}$ | Number of background (SM) events | $N_{\mathrm{bg}} = \sigma_{\mathrm{SM}} \cdot L$ |
| $N_{\mathrm{s}}$ | Number of signal events | $N_{\mathrm{s}} = [\sigma(f) - \sigma_{\mathrm{SM}}] \cdot L$ |
| $N_{\mathrm{sig}}$ | Alternative notation for $N_{\mathrm{s}}$ | $N_{\mathrm{sig}} = N_{\mathrm{s}}$ |
| $N_{\mathrm{all}}$ | Total number of events | $N_{\mathrm{all}} = N_{\mathrm{bg}} + N_{\mathrm{s}} = \sigma(f) \cdot L$ |

**Important**: Define these symbols **in the text** on first use, not just in a table. Example:
> "The statistical significance is computed using the Asimov formula, where $N_{\mathrm{bg}} = \sigma_{\mathrm{SM}} L$ is the number of SM background events and $N_{\mathrm{s}} = (\sigma - \sigma_{\mathrm{SM}})L$ is the number of signal events, with $L$ the integrated luminosity in pb$^{-1}$."

### 7.3 Expected Constraints (Main Result)

**Final constraint table** (best algorithm only — this is the physical result):

| Operator | $S = 2$ | $S = 3$ | $S = 5$ |
|----------|---------|---------|---------|
| o1 | $[f^{-}, f^{+}]$ | $[f^{-}, f^{+}]$ | $[f^{-}, f^{+}]$ |
| o2 | $[f^{-}, f^{+}]$ | $[f^{-}, f^{+}]$ | $[f^{-}, f^{+}]$ |

**Algorithm comparison table** (main text — justifies algorithm selection):

| Operator | $S$ | Algorithm 1 | Algorithm 2 | Algorithm 3 | Best |
|----------|-----|-------------|-------------|-------------|------|
| o1 | 2 | $[-0.045, 0.048]$ | $[-0.062, 0.065]$ | $[-0.089, 0.092]$ | Algorithm 1 |
| o1 | 3 | $[-0.032, 0.034]$ | $[-0.044, 0.046]$ | $[-0.063, 0.066]$ | Algorithm 1 |

- Monotonicity must hold: $|f(5)| < |f(3)| < |f(2)|$
- Include unitarity bounds for comparison

### 7.4 Algorithm Comparison (Key Section)

**Best algorithm selection criterion**: Narrowest constraint width at $S=2$, NOT highest AUC.

**Important**: When the algorithm with best AUC differs from the algorithm with best constraints, explain why. For example:
> "Although {alg1} achieves the highest AUC (0.987), {alg2} produces slightly tighter constraints for operator o2 because [reason if known]."

**Comparison plot (Band Plot)**: For each algorithm, draw a horizontal band from $f_{\min}$ to $f_{\max}$. The best algorithm has the narrowest band. This is a **constraint interval comparison**, not a bar chart of widths.

---

## Section 8: Conclusions

**Required content:**
1. **Summary of approach**: Multi-algorithm comparison for event selection
2. **Key results**: Which algorithm performs best for which operator, best constraints achieved
3. **Physical interpretation**: What these constraints mean for the model
4. **Algorithm insights**: Any interesting differences between algorithms (e.g., supervised vs unsupervised performance)
5. **Future outlook**: Higher energy/luminosity projections, additional algorithms, other processes

**Never introduce new figures or tables in conclusions.**

---

## Required Figures Checklist (All PDF Vector Format)

**All figures MUST be PDF for publication-quality vector graphics.**

| Figure | Description | Source |
|--------|-------------|--------|
| 1 | ROC curves (all algorithms, per operator) | `results/plots/roc_o*.pdf` |
| 2 | ML score distributions (all algorithms, SM vs NP) | `results/plots/score_dist_o*_*alg*.pdf` |
| 3 | Threshold optimization comparison (all algorithms) | `results/plots/threshold_comparison.pdf` |
| 4 | Cross-section fit plots (all algorithms, per operator) | `results/plots/csfit_plot_o*_*alg*.pdf` |
| 5 | Algorithm comparison **band plot** ($[f_{\min}, f_{\max}]$ intervals side-by-side) | Generate from Phase 7 `algorithm_selection.json` |

## Required Tables Checklist

| Table | Content | Source |
|-------|---------|--------|
| 1 | Operator definitions / Unitarity bounds | SKILL inputs / theoretical |
| 2 | Feature list | Phase 5 feature extraction |
| 3 | Hyperparameters per algorithm | Phase 5 training config |
| 4 | AUC comparison | Phase 5 `algorithm_comparison.json` |
| 5 | Optimal thresholds per algorithm | Phase 6 `threshold_optimization.json` |
| 6 | Cut efficiency per algorithm | Phase 6 results |
| 7 | Fit parameters per algorithm | Phase 6 fit results |
| 8 | Final constraints (best algorithm only) | Phase 7 `constraint_table.json` |
| 9 | Algorithm comparison (full intervals, justifies selection) | Phase 7 `algorithm_selection.json` |
| 10 | Best algorithm by operator | Derived from Table 9 |

## Formula Presentation Standards

1. **All formulas in LaTeX** — no plain text math
2. **Number all displayed equations** sequentially
3. **Define every symbol on first use** (e.g., "where $L$ is the integrated luminosity in pb$^{-1}$")
4. **Use consistent notation**: $\sigma$ for cross-sections, $f$ or $c$ for coefficients, $N$ for event counts
5. **Include units** with all numerical values in tables
6. **Use scientific notation** for very small or large numbers (e.g., $1.2 \times 10^{-3}$)

## Citation Requirements

### Mandatory Toolchain Citations

These references MUST appear in the bibliography. Do not omit.

| Tool | Reference | DOI | arXiv |
|------|-----------|-----|-------|
| MadGraph5 | J. Alwall et al., "The automated computation of tree-level and next-to-leading order differential cross sections, and their matching to parton shower simulations", J. High Energy Phys. **07**, 079 (2014) | 10.1007/JHEP07(2014)079 | 1405.0301 |
| FeynRules | N. D. Christensen and C. Duhr, "FeynRules — Feynman rules made easy", Comput. Phys. Commun. **180**, 1614 (2009) | 10.1016/j.cpc.2009.02.018 | 0806.4194 |
| UFO | C. Degrande et al., "UFO — The universal FeynRules output", Comput. Phys. Commun. **183**, 1201 (2012) | 10.1016/j.cpc.2012.01.022 | 1108.2040 |
| Delphes | J. de Favereau et al., "DELPHES 3: A modular framework for fast simulation of a generic collider experiment", J. High Energy Phys. **02**, 057 (2014) | 10.1007/JHEP02(2014)057 | 1307.6346 |
| MLAnalysis | Y.-C. Guo et al., "MLAnalysis: An open-source program for high energy physics analyses", Comput. Phys. Commun. **294**, 108957 (2024) | 10.1016/j.cpc.2023.108957 | 2305.00964 |
| Pythia | [If proton initial state or hadronization] T. Sjöstrand et al., "An introduction to PYTHIA 8.2", Comput. Phys. Commun. **191**, 159 (2015) | 10.1016/j.cpc.2015.01.024 | 1410.3012 |
| LHAPDF | [If proton initial state] A. Buckley et al., "LHAPDF6: parton density access in the LHC precision era", Eur. Phys. J. C **75**, 132 (2015) | 10.1140/epjc/s10052-015-3318-8 | 1412.7420 |

### Citation Placement

- **Section 4 (Event Generation)**: Cite all tools used when first mentioned
- **Section 5 (ML Methodology)**: Cite MLAnalysis when describing the analysis framework
- **Section 7 (Results)**: Cite any prior constraints from other studies when comparing

## Quality Standards

Before declaring a report complete, verify:

- [ ] Every figure is referenced in the text (e.g., "as shown in Fig. 3")
- [ ] Every table is referenced in the text
- [ ] All figures are PDF vector format
- [ ] All formulas are LaTeX-rendered
- [ ] All mandatory toolchain citations are present
- [ ] Each algorithm has its score formula defined mathematically
- [ ] Event counts match actual generated counts (debug-adjusted if applicable)
- [ ] Final constraint table matches Phase 7 `constraint_table.json` exactly
- [ ] Algorithm comparison data contains full intervals $[f_{\min}, f_{\max}]$
- [ ] Algorithm comparison plot is a **band plot**, not a bar chart
- [ ] All algorithms trained in Phase 5 appear in the comparison section
- [ ] Best algorithm is selected by constraint width, not AUC
- [ ] All operator names are consistent across all sections
- [ ] All formulas use the same symbol conventions
- [ ] No placeholder text or "TODO" markers remain
- [ ] Bibliography entries are properly formatted
- [ ] All mandatory citations include DOI and arXiv
- [ ] Dataset composition explicitly states SM-only / NP-only / SM+NP+interference
- [ ] Scan coefficient values are explicitly listed
- [ ] S_stat formula defines every symbol in the text (not just in a table)

## Red Flags

| Issue | Meaning | Action |
|-------|---------|--------|
| PNG figures | Raster images in publication | Regenerate as PDF |
| Plain text formulas | Unprofessional presentation | Convert to LaTeX |
| Missing MadGraph/FeynRules/UFO/Delphes/MLAnalysis citation | Incomplete methodology | Add mandatory citations |
| No score function definition | Algorithm not reproducible | Add mathematical definition |
| Algorithm comparison is a bar chart of widths | Wrong visualization type | Use band plot showing $[f_{\min}, f_{\max}]$ |
| Algorithm selection data only has widths | Cannot draw band plot | Re-run Phase 7 with full intervals |
| Missing dataset composition table | Incomplete methodology | Add SM/NP/Scan dataset details |
| Missing scan coefficient list | Results not reproducible | Add table of 11 scan points |
| S_stat symbols undefined | Formula unreadable | Define every symbol in text |
| Empty sections | Report is incomplete | Do not deliver |
| Missing figures | Results not visualized | Generate all required plots |
| Only one algorithm analyzed | Missing core comparison | Re-run Phase 6-7 for all algorithms |
| Best algorithm selected by AUC | Wrong criterion | Re-select by constraint width |
| Constraints don't match Phase 7 | Data inconsistency | Re-run or fix source |
| Formulas without definitions | Unreadable for non-experts | Add symbol definitions |
