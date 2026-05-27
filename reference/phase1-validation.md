# Phase 1: Validate New Physics Impact

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE — once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Purpose
Identify which SMEFT operators in the model actually affect the chosen process.

## Prerequisite
Process directory must be created with `NP>0`.

## Step 1.1: Create NP Process Directory

Order file:
```
import model {model_name}
generate {process_name} NP>0
output {folder_base}_p1_NP
```

Run and check return code. Abort on any MG5 error.

## Step 1.2: Extract Coefficients from param_card.dat

Read `Block anoinputs` from `{mg5path}/{folder_base}_p1_NP/Cards/param_card.dat`.

**Use the script** (do not reimplement):

```bash
python scripts/parse_param_card.py {param_card_path}
```

Or import in Python:
```python
from scripts.parse_param_card import parse_anoinputs

coefficients = parse_anoinputs(param_card_path, scan_default=1.0e-12)
```

The script handles case-insensitive Block matching, scan syntax retention, and Block boundary detection.

**Validation:** If parsed names include `MZ`, `MW`, `WT` or values ~90, the parser leaked into `Block mass`. Report this as a parser bug.

## Step 1.3: Scan Each Coefficient

For each coefficient `fi`:
1. Determine `c0`: default from param_card, or `1.0` if default is `0.0`
2. Write launch order with `set anoinputs {idx} {c0}` for `fi`, `set anoinputs {other_idx} 0.0` for all others, `nevents = {nev_phase1}`. See [`madgraph-reference.md`](madgraph-reference.md) Coefficient Block for the exact syntax.
3. Run MG5, check return code
4. Post-process: find latest `run_XX`, convert ROOT→LHCO, validate
5. Extract `sigma_i` from the run banner using the canonical `extract_cross_section()` function defined in [`madgraph-reference.md`](madgraph-reference.md). **Any positive cross-section** — even `1e-10 pb` — indicates the operator couples to the process. Only `sigma_i == 0` (or parse failure) should exclude an operator.
6. Mark operator as non-zero if `sigma_i > 0`.

## Output

> **Multi-run note:** In multi-run mode, all `results/` paths below are prefixed with the run subdirectory (e.g., `results/E10_L1000/data/phase1/...`). See [`SKILL.md`](../SKILL.md) Rule 11.

```
results/data/phase1/
  operators.json           # List of non-zero operators
  cross_sections.json      # {fi: {sigma, c0}} for all operators
```

## Validation

| Check | Action on Failure |
|-------|-------------------|
| `generate` succeeds | Abort and report MG5 error |
| At least one `sigma_i > 0` | Abort: process insensitive to model |
