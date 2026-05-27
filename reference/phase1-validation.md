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

**Critical: parser must handle Block boundaries.**

```python
def parse_anoinputs(param_card_path):
    coefficients = {}
    in_block = False
    with open(param_card_path) as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith("Block"):
                in_block = stripped.lower().startswith("block anoinputs")
                continue
            if not in_block or not stripped or stripped.startswith("#"):
                continue
            parts = stripped.split()
            if len(parts) >= 2:
                idx, val = parts[0], parts[1]
                coefficients[idx] = float(val)
    return coefficients
```

**Validation:** If parsed names include `MZ`, `MW`, `WT` or values ~90, the parser leaked into `Block mass`. The state machine failed to exit on the next `Block` header.

## Step 1.3: Scan Each Coefficient

For each coefficient `fi`:
1. Determine `c0`: default from param_card, or `1.0` if default is `0.0`
2. Write launch order with `fi = c0`, all others = 0.0, `nevents = {nev_phase1}`
3. Run MG5, check return code
4. Post-process: find latest `run_XX`, convert ROOT→LHCO, validate
5. Extract `sigma_i` from banner using the canonical parser in [`madgraph-reference.md`](madgraph-reference.md). **Any positive cross-section** — even `1e-10 pb` — indicates the operator couples to the process. Only `sigma_i == 0` (or parse failure) should exclude an operator.
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
