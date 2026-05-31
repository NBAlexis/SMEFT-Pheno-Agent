# Automated SMEFT Phenomenology with Machine Learning

> **Skill for Claude Code** — Automated end-to-end workflow for studying Standard Model Effective Field Theory (SMEFT) signatures at colliders using machine learning for event selection optimization.

---

## Overview

This skill provides a fully automated pipeline that:

1. **Generates MC events** with MadGraph5_aMC@NLO for SM and NP (SMEFT) processes
2. **Identifies active operators** by scanning Wilson coefficients in the chosen model
3. **Trains and compares ML algorithms** (Gradient Boosting, Random Forest, XGBoost, etc.) for event selection
4. **Optimizes selection thresholds** per algorithm to maximize sensitivity
5. **Computes expected constraints** on Wilson coefficients at significance levels S = 2, 3, 5
6. **Produces a publication-quality report** (PDF or HTML) with constraint tables, ROC curves, and comparison plots

Supports single or multiple `(energy, luminosity)` combinations — each runs the full workflow independently in its own subdirectory.

---

## Required Inputs

| Parameter | Description | Example |
|-----------|-------------|---------|
| `madgraph_path` | Absolute path to MadGraph5 installation | `/opt/MG5_aMC_v3_5_4` |
| `process` | Physics process (no NP=/QED=/QCD= suffixes) | `p p > l+ l- j j` |
| `model` | SMEFT UFO model name | `SMEFTsim_U35_MwScheme_UFO` |
| `energy` | Center-of-mass energy in TeV (single or list) | `13.6` or `[10, 14, 30]` |
| `luminosity` | Integrated luminosity in fb⁻¹ (matching energy length) | `3000` or `[1000, 3000, 10000]` |

Optional inputs include `debug` (10x fewer events for testing), `algorithms` (custom ML pool), and `delphes_card` (detector simulation card).

---

## Workflow Phases

| Phase | Purpose |
|-------|---------|
| **-1** | Input collection and validation |
| **0** | Environment validation (MG5, model, packages, Delphes card selection) |
| **1** | Identify non-zero SMEFT operators |
| **2** | Estimate coefficient scan range `[-c1, c1]` |
| **3** | Generate pure SM and pure NP samples |
| **4** | Generate 11-point coefficient scan samples |
| **5** | Train and compare ML event selection algorithms |
| **6** | Optimize threshold and fit cross-section per algorithm |
| **7** | Compute expected constraints at S = 2, 3, 5 |
| **8** | Generate publication-quality report |
| **Cleanup** | Collect MG5 process folders to working directory |
| **9** | Self-consistency audit |

---

## Key Design Principles

- **Execution continuity**: Once started, the workflow runs to completion without stopping (only unrecoverable errors or explicit user interrupt are valid stop conditions)
- **Physical parameter immutability**: Event counts, energy, luminosity, and scan ranges are never modified for speed
- **Multi-run mode**: Each `(energy, luminosity)` pair gets its own `results/E{e}_L{l}/` subdirectory
- **Flexible Delphes card selection**: Auto-recommends detector cards based on the actual files in `mg5path/Delphes/cards/`, with user override
- **Robust banner parsing**: Supports multiple MG5 banner formats for cross-section extraction

---

## File Structure

```
automated-smeft-ml-pheno/
├── SKILL.md                          # Main skill definition
├── README.md                         # This file
└── reference/                        # Phase-by-phase implementation references
    ├── phase-minus1-input-collection.md  # Interactive input collection
    ├── phase0-env.md                     # Environment validation
    ├── phase1-validation.md              # Operator identification
    ├── phase2-range.md                   # Coefficient range estimation
    ├── phase3-pure-samples.md            # SM/NP sample generation
    ├── phase4-scan.md                    # Scan sample generation
    ├── phase5-ml-training.md             # ML training and comparison
    ├── phase6-selection.md               # Threshold optimization
    ├── phase7-constraints.md             # Constraint computation
    ├── phase8-report.md                  # Report generation
    ├── phase9-audit.md                   # Self-consistency audit
    ├── cleanup.md                        # MG5 process cleanup
    ├── madgraph-reference.md             # MG5 invocation conventions
    ├── madgraph-installation.md          # MG5 auto-installation
    ├── cutexperiment-reference.md        # LHCO-to-CSV pipeline
    ├── model-dependencies.md             # UFO model dependency handling
    └── report-writing-guide.md           # Report content guidelines
```

---

## Dependencies

- **MadGraph5_aMC@NLO** (v3.5+)
- **Python 3** with `numpy`, `scipy`, `scikit-learn`, `joblib`, `matplotlib`
- **CutExperiment** (auto-cloned from Gitee if not provided)
- **Delphes** (bundled with MG5)

---

## Credits

This skill was developed with assistance from **Kimi k2.6** (Moonshot AI).

---

## License

MIT License — see LICENSE file for details.
