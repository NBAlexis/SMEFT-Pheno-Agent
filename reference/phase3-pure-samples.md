# Phase 3: Generate Pure SM and Pure NP Samples

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE — once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Purpose
Generate high-statistics pure samples for ML training.

## Step 3.1: Pure SM Sample

1. Create SM process directory (`NP=0`)
2. Copy Delphes card and dependencies
3. Launch with all coefficients = 0.0, `nevents = {nev_sm}`
4. Post-process (ROOT→LHCO, validate, clean large files)
5. Copy to results:
```
results/data/phase3/sm_banner.txt
results/data/phase3/sm.lhco
```

> **Multi-run note:** In multi-run mode, all `results/` paths above are prefixed with the run subdirectory (e.g., `results/E10_L1000/data/phase3/...`). See [`SKILL.md`](../SKILL.md) Rule 11.

## Step 3.2: Pure NP Samples

For each non-zero operator `oi`:
1. Create NP process directory (`NP>0`)
2. Launch with `oi = c1` (from Phase 2), others = 0.0, `nevents = {nev_np}`
3. Post-process
4. Copy to results:
```
results/data/phase3/np_oi_banner.txt
results/data/phase3/np_oi.lhco
```

> **Multi-run note:** In multi-run mode, all `results/` paths above are prefixed with the run subdirectory (e.g., `results/E10_L1000/data/phase3/...`). See [`SKILL.md`](../SKILL.md) Rule 11.

## Validation

- `sm.lhco` must exist and be non-empty (abort if missing)
- Each `np_oi.lhco` should exist (warn per operator if missing)
