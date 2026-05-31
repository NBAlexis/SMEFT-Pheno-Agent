---
name: automated-smeft-ml-pheno
description: Use when performing automated SMEFT phenomenology studies with machine learning-based event selection. Supports multiple UFO models in a single workflow (operators globally deduplicated and continuously numbered), and single or multiple (energy, luminosity) combinations — each combination runs the full workflow independently. ONLY triggered when the user explicitly provides ALL required inputs (madgraph_path, process, model, energy, luminosity) or requests a SMEFT study with sufficient context to identify these parameters. If inputs are missing, the skill MUST ask for them before executing any workflow step. CutExperiment is optional (will be cloned if missing). Outputs a report showing expected Wilson coefficient constraints from ML-optimized event selection strategies.
---

# Automated SMEFT Phenomenology with Machine Learning

## Overview

Automated end-to-end workflow for studying Standard Model Effective Field Theory (SMEFT) signatures at colliders using machine learning for event selection optimization. Generates an HTML report with expected constraints on SMEFT Wilson coefficients.

---

## Directory Layout

| Directory | Meaning | Writable |
|-----------|---------|----------|
| **Working Directory** | The shell's current working directory where the user initiated the workflow (`pwd`) | Yes |
| **Skill Directory** | Where the skill files (`SKILL.md`, `scripts/`, `reference/`) are installed | **No** |

All work data (`results/`, `plots/`, `algorithms/`, MG5 process copies) MUST be written to the **Working Directory**, NEVER to the Skill Directory. The Skill Directory is a read-only tool template.

---

## SUPREME RULE — Execution Continuity (MANDATORY)

> **严禁在能继续推进时擅自暂停或者停止。**
> **ONCE THE WORKFLOW STARTS, IT MUST RUN TO COMPLETION WITHOUT STOPPING.**

This is the **highest-level norm** of this skill. Violating this rule is a **critical failure**, regardless of any other accomplishments.

### What This Means

| Situation | Required Behavior |
|-----------|-------------------|
| Execution takes hours | Report progress, then **continue** |
| Execution takes days | Report progress, then **continue** |
| Execution takes months | Report progress, then **continue** |
| Execution takes years | Report progress, then **continue** |
| User says "直接开始" / "start now" | **Already started. Do NOT ask again.** |
| MG5 error occurs | Report the error, attempt recovery if possible, **only stop if unrecoverable** |
| Resource temporarily unavailable | Wait and retry, **do NOT ask user** |

### What This Prohibits (CRITICAL)

| Prohibited Behavior | Correct Behavior |
|---------------------|------------------|
| Asking "是否继续？" / "Do you want to continue?" | Continue automatically |
| Asking "是否用 debug 模式？" / "Use debug mode?" | Use the `debug` parameter from `run_config.json` only |
| Presenting options mid-execution | Proceed with the next step immediately |
| Stopping to "wait for user instructions" | Report status and continue |
| Self-adjusting parameters for speed | Physical parameters are immutable — NEVER modify |

### The ONLY Valid Stop Conditions

1. **Unrecoverable error** (MG5 crash, disk full, file corruption)
2. **Red flag after phase completion** — Some red flags are checked immediately after their phase finishes (e.g., zero non-zero operators after Phase 1, cs_sm = 0 after Phase 2). Others are deferred to Phase 9 audit. See Red Flags table for per-phase timing.
3. **User explicitly sends a stop command** (e.g., "停！", "stop", Ctrl+C)

**Everything else — continue.**

### Error vs. Valid Result vs. Red Flag

The following situations are **NOT errors** and **do NOT justify stopping**. They are valid (if unexpected) physical results that must be recorded and the workflow must continue:

| Situation | Classification | Required Action |
|-----------|---------------|-----------------|
| Single operator has σ = 0 | **Valid result** | Record it, continue testing remaining operators |
| All operators have σ = 0 | **Red flag** (after Phase 1 completes) | STOP after Phase 1 finishes. No operators are sensitive — there is nothing to study. |
| A scan point times out or fails | **Recoverable issue** | Retry or skip the point, continue remaining points |
| ML AUC ≤ 0.5 | **Red flag** (after Phase 5 completes) | Report in Phase 9 audit |
| Quadratic fit fails | **Red flag** (after Phase 6 completes) | Report in Phase 9 audit |
| MG5 returns warning (not crash) | **Valid execution** | Log the warning, continue |

**True errors** (unrecoverable, may stop):
- MG5 segfault / process killed / out of memory
- Disk full
- Required model file missing or corrupted
- Python dependency import failure
- Network failure preventing required clone/download

**If in doubt whether something is an error: assume it is NOT an error and continue.** Only stop when the system physically cannot proceed.

---

## When to Use

- SMEFT operator sensitivity studies at lepton or hadron colliders
- Comparing cut-based vs ML-based event selection strategies
- Generating publishable constraint plots and summary reports

**Do NOT use when:**
- Only Standard Model kinematic distributions are needed (no EFT interpretation)
- Full detector simulation is required (uses truth-level or fast simulation)

## Required Inputs

| Parameter | Description | Example |
|-----------|-------------|---------|
| `madgraph_path` | Absolute path to MadGraph5 installation | `/opt/MG5_aMC_v3_5_4` |
| `process` | Physics process only (no `NP=`, `QED=`, `QCD=` suffixes) | `p p > l+ l- j j` |
| `model` | SMEFT model name(s). Single model or list of models | `SMEFTsim_U35_MwScheme_UFO` or `["AQGCm_UFO", "AQGCs_UFO"]` |
| `energy` | Center-of-mass energy in TeV (single value or list) | `13.6` or `[10, 14, 30]` |
| `luminosity` | Integrated luminosity in fb⁻¹ (single value or list) | `3000` or `[1000, 3000, 10000]` |

### CutExperiment

`cutexperiment_path` is **not strictly required**:

- If the user provides it: validate the path exists
- If missing: ask the user "Do you already have CutExperiment installed? If so, provide the path. If not, I will clone it from the Gitee repository."
- If the user does not have it: clone from `https://gitee.com/NBAlexis/CutExperiment.git` into the working directory (e.g., `./CutExperiment`) and use that path
- **Clone command**: `git clone https://gitee.com/NBAlexis/CutExperiment.git`

## Phase -1: Input Collection

**This is Step 1 of the workflow. Do NOT skip. Do NOT proceed to Phase 0 until completed.**

**CRITICAL: Phase -1 is the ONLY interactive stage.** Once it completes, ALL subsequent phases (0–9) execute **FULLY AUTOMATICALLY** without any user interaction.

When this skill is invoked, immediately execute input collection. Detailed steps: [`reference/phase-minus1-input-collection.md`](reference/phase-minus1-input-collection.md).

### Phase -1 Output: `run_config.json`

Phase -1 writes all validated inputs to `{workdir}/results/run_config.json`. This file is the **single source of truth** for the entire workflow. All subsequent phases (0–9) read their configuration from this file. No phase should reference Phase -1 directly, re-ask the user, or infer parameters from history.

**Load the configuration:**
```bash
python scripts/load_run_config.py results/run_config.json
```

```python
from scripts.load_run_config import load_run_config
config = load_run_config("results/run_config.json")
print(config.madgraph_path, config.delphes_card)
```

**After Phase -1 completes, the interactive portion of the workflow is OVER.** From this point forward, do NOT wait for user confirmation, do NOT ask "是否继续？" / "Shall I proceed?". Immediately execute Phase 0, then sequentially execute Phases 1–9 without stopping.

## Physical Parameter Immutability

The following are **immutable** and must NEVER be modified for any reason, including speed:

- Event counts (`nev_phase1`, `nev_phase2`, `nev_sm`, `nev_np`, `nev_scan`)
- `luminosity`, `energy`
- Any coefficient values or scan ranges from previous phases

**If execution is long, report progress periodically but CONTINUE execution automatically.** Do NOT stop to ask whether to proceed. Do NOT self-adjust parameters. The only valid reasons to stop are: (1) an error/red flag occurs, (2) the user explicitly interrupts.

## Optional Inputs

| Parameter | Description | Default |
|-----------|-------------|---------|
| `debug` | Divide all event counts by 10. **This is the ONLY permitted modification.** | `false` |
| `delphes_card` | Delphes detector card `.tcl` file name (e.g., `delphes_card_CEPC.tcl`). Auto-selected if not specified. | Auto-recommended from `{mg5path}/Delphes/cards/` |
| `ebeam_proton` | Proton beam energy in GeV. **Required** for `e- p` / `e+ p` colliders. | None (must ask for ep) |
| `polarization` | Beam polarization as `polbeam1,polbeam2` in range [-1, 1] | No polarization |
| `custom_card` | Absolute path to a custom Delphes `.tcl` card outside `{mg5path}/Delphes/cards/` | None |

### Event Count Scaling

| Symbol | Normal | Debug |
|--------|--------|-------|
| `nev_phase1` | 10,000 | 1,000 |
| `nev_phase2` | 10,000 | 1,000 |
| `nev_sm` | 500,000 | 50,000 |
| `nev_np` | 100,000 | 10,000 |
| `nev_scan` | 1,000,000 | 100,000 |

**Warning**: These are the ONLY valid event counts. Do not invent other scaling factors.

## Unit Convention

All cross-sections from MG5 banners are in **pb**. All luminosities in formulas are in **pb⁻¹**.

| Quantity | Unit | Conversion |
|----------|------|------------|
| Cross-section (`cs_sm`, `cs_np`) | pb | MG5 native output |
| User luminosity input | fb⁻¹ | `luminosity` parameter |
| Physics luminosity `L` (Phase 6/7) | pb⁻¹ | `L = luminosity * 1000` |
| Effective luminosity `L'` (Phase 2) | pb⁻¹ | `L' = n_scan / cs_sm` |

## Execution Workflow

**CRITICAL: Phase -1 is the ONLY interactive stage. Once Phase -1 completes, Phases 0–9 execute FULLY AUTOMATICALLY and sequentially without stopping.** Do NOT pause to ask the user whether to continue, whether to use debug mode, or to present options. Report progress at natural phase boundaries, then immediately proceed to the next phase. The only valid stop conditions are errors, red flags, or explicit user interrupt.

### Phase Completion Rule (MANDATORY)

**Every phase MUST run to completion before any red flag check is applied.**

| Situation | Correct Behavior | Wrong Behavior |
|-----------|------------------|----------------|
| Phase 1: first few operators have σ = 0 | **Continue** testing ALL remaining operators. Complete Phase 1 fully. | Stop mid-phase and declare red flag |
| Phase 4: first scan point has issues | **Continue** processing ALL 11 scan points. Complete Phase 4 fully. | Stop after partial scan |
| Phase 5: first algorithm performs poorly | **Continue** testing ALL configured algorithms. Complete Phase 5 fully. | Skip remaining algorithms |

**Red flags are checked AFTER the phase completes, NEVER during execution.** A zero cross-section for an individual operator is a valid Phase 1 result, not a reason to abort. The red flag "Zero non-zero operators after Phase 1" means **ALL operators tested returned σ = 0 after the entire phase finished** — at that point the workflow STOPS because there is no sensitive operator to study. But you MUST NOT stop early because the first few were zero.

> **执行锁 — 最高优先级规则：如果有 10 个算符，哪怕 9 个为 0 也必须测完 10 个算符。中途停止是严格禁止的。**

### Phase Workflow Reference

The following table summarizes the MG5 invocation for every phase that runs MadGraph. This is the canonical reference — all details in per-phase documents must match this table.

| Phase | `generate` line | Output folder suffix | Coefficient setting | `nevents` | Output files |
|-------|-----------------|----------------------|---------------------|-----------|--------------|
| 1 | `generate {process} NP>0` | `_{model}_p1_NP` | One at a time: target = `c_{n_{default}}`, all others = `0.0` | `nev_phase1` | `operator_claims.json`, `cross_sections.json`, `anchor.json` |
| 2 | `generate {process} NP=0` | `_{anchor_model}_p2_SM` | All `{block_name} {idx} = 0.0` | `nev_phase2` | `sm_baseline.json`, `coefficient_ranges.json` |
| 3 SM | `generate {process} NP=0` | `_{anchor_model}_p3_SM` | All `{block_name} {idx} = 0.0` | `nev_sm` | `sm_banner.txt`, `sm.lhco` |
| 3 NP | `generate {process} NP>0` | `_{anchor_model}_p3_NP` | Target = `c_{n_{scan}}` (anchor operator), others = `0.0` | `nev_np` | `np_anchor_banner.txt`, `np_anchor.lhco` |
| 4 | `generate {process}` | `_{model}_p4` | One operator: `{block_name} {idx} scan:[v0,v1,...]` on `[-c_{n_{scan}}, c_{n_{scan}}]`; all others = `0.0` | `nev_scan` | `np_o_{g_idx}_f0_banner.txt` … `np_o_{g_idx}_f10_banner.txt` and `.lhco` |

**Key rules:**
- Each phase uses a **separate process directory** (independent `output` step). Never reuse a directory from another phase.
- In multi-model mode, process directory names include the **model name** to avoid collisions (e.g., `ee_a_jj_AQGCm_UFO_p1_NP`).
- `scan:[...]` syntax is **only used in Phase 4**. Phases 1 and 3 NP test one coefficient at a time with individual `launch` commands.
- Phase 4 output uses **global index-based naming** (`o_{g_idx}`) mapped by sorted run number, not coefficient value.
- ML training (Phase 5) uses the **anchor operator only**; the trained algorithms are applied to ALL globally claimed operators.

### Multi-Model Mode

If `model` is a list of model names, the workflow operates in **multi-model mode**:

1. **Phase 1**: Iterate all models in user-provided order. Test each operator. Claim operators globally with continuous numbering (`o_1, o_2, ..., o_N`). Skip duplicates (same operator name from a later model). The first non-zero operator becomes the **anchor**.
2. **Phase 2**: Compute coefficient range using the anchor operator only. The same range applies to ALL operators.
3. **Phase 3**: Generate SM and NP samples using the **anchor model** only. NP sample is for the anchor operator only.
4. **Phase 4**: Scan ALL globally claimed operators. Each operator is scanned in its source model. Output uses global numbering (`np_o_{g_idx}_f{i}.lhco`).
5. **Phase 5**: Train ML algorithms ONCE on anchor operator's SM/NP samples.
6. **Phase 6**: Optimize threshold using anchor operator's scan data. Apply each algorithm's optimal threshold to ALL operators.
7. **Phase 7**: Compute constraints for ALL globally claimed operators.
8. **Phase 8**: Single consolidated report showing all operators with their source models.

**Key data structures:**
- `claimed`: dict mapping operator name → source model
- `operator_claims.json`: maps global index → `{model, anoinput_idx, name}`
- `anchor.json`: `{global_idx, model, anoinput_idx, name}`

### Multi-Run Mode

If `energy` and `luminosity` are both lists, execute Phases 0–9 **once per `(energy, luminosity)` pair**. Each run is independent and uses its own output subdirectory.

| Phase | Purpose | Reference |
|-------|---------|-----------|
| **-1** | **Input Collection** — verify all required inputs; ask user if any missing | [`reference/phase-minus1-input-collection.md`](reference/phase-minus1-input-collection.md) |
| 0 | Environment validation | [`reference/phase0-env.md`](reference/phase0-env.md) |
| 1 | Identify non-zero operators across all models | [`reference/phase1-validation.md`](reference/phase1-validation.md) |
| 2 | Estimate coefficient ranges `[-c_{scan}, c_{scan}]` | [`reference/phase2-range.md`](reference/phase2-range.md) |
| 3 | Generate pure SM and NP samples | [`reference/phase3-pure-samples.md`](reference/phase3-pure-samples.md) |
| 4 | Generate 11-point coefficient scans | [`reference/phase4-scan.md`](reference/phase4-scan.md) |
| 5 | Train and compare ML algorithms | [`reference/phase5-ml-training.md`](reference/phase5-ml-training.md) |
| 6 | Optimize threshold, fit cross-section | [`reference/phase6-selection.md`](reference/phase6-selection.md) |
| 7 | Compute constraints at S = 2, 3, 5 | [`reference/phase7-constraints.md`](reference/phase7-constraints.md) |
| 8 | Generate report (PDF or HTML) | [`reference/phase8-report.md`](reference/phase8-report.md) |
| Cleanup | Collect MG5 process folders from `mg5path` to working directory | [`reference/cleanup.md`](reference/cleanup.md) |
| 9 | Self-consistency audit | [`reference/phase9-audit.md`](reference/phase9-audit.md) |

### Critical Cross-Cutting Rules

1. **Phase -1 is Step 1**: The Input Collection steps above are the FIRST action when this skill is invoked. Never create files, run commands, or check system state before Phase -1 completes.
2. **Parameter source is the user ONLY**: `process`, `model`, `energy`, and `luminosity` must NEVER be inferred from files, logs, or historical context — they are missing unless explicitly stated in the current conversation. For `madgraph_path` and `cutexperiment_path`, you may show a suggested default in the prompt, but the user must actively confirm (press Enter) or override it. Never silently accept any default without asking.
3. **MG5 return code**: Every `subprocess.run` invoking MG5 MUST check `returncode != 0`. Never silently ignore failures.
4. **No `runs[-11:]`**: Use set-difference (`new_runs = all_runs - existing_runs`) to track exactly which runs MG5 created. See [`reference/phase4-scan.md`](reference/phase4-scan.md).
5. **No tag_2**: Never delete files from an existing `run_XX` and re-launch. If the entire process directory must be re-run, remove large temps (`*.root`, `*.lhe.gz`, `*.hepmc.gz`) and rename the **process directory** (not individual runs). See [`reference/phase4-scan.md`](reference/phase4-scan.md).
6. **Anchor operator**: Threshold optimization (Phase 6) uses the anchor operator's scan data. The anchor is the first non-zero operator found across all models, recorded in `anchor.json`. Do NOT use `nonzero_ops[0]`.
7. **Pass `nev_scan`**: Read `n_scan` from `sm_baseline.json`. Do NOT hardcode in Phase 6.
8. **param_card parser**: Match `Block` case-insensitively; handle `scan:[...]` syntax; reset `in_block` on every new `Block` header. See [`reference/phase1-validation.md`](reference/phase1-validation.md).
9. **Cleanup after Phase 8**: Move all MG5 process directories from `mg5path` to `results/mg5_processes/` using `mv` (not `cp`). This prevents `mg5path` from accumulating unmanaged folders across runs. See [`reference/cleanup.md`](reference/cleanup.md).
10. **MadGraph conventions**: All MG5 process creation, event generation, Delphes card setup, and ROOT→LHCO conversion follow [`reference/madgraph-reference.md`](reference/madgraph-reference.md). **Reusable scripts** are provided in `scripts/` — use them instead of reimplementing.
11. **Feature extraction**: LHCO→CSV conversion follows [`reference/cutexperiment-reference.md`](reference/cutexperiment-reference.md) and adapts to the actual final-state particles in `process`.
12. **Run directory prefix (multi-run mode)**: Before Phase 0, compute `RUN_DIR = f"E{energy}_L{luminosity}"` (dots replaced by underscores). ALL file paths in ALL phases MUST prefix `results/` with `RUN_DIR/`. Single-run mode uses `results/` directly. This is NOT optional — verify by checking `results/E{e}_L{l}/` exists before writing any data. See [Output Structure](#output-structure) for examples.
13. **No concurrent MG5 processes**: MadGraph5 internally uses multi-threading (OpenMP) and will saturate all CPU cores. Launching multiple MG5 processes in parallel causes CPU contention and is **slower** than sequential execution. Run MG5 invocations **one at a time** — never parallelize across operators, scan points, or phases.
14. **Phase 1 execution lock — NEVER stop mid-loop**: Testing individual operators in Phase 1 is a single uninterrupted loop over ALL coefficients in ALL models. A zero cross-section for any individual operator is a valid physical result. You MUST NOT: test SM baseline mid-phase, skip remaining coefficients, switch models early, report red flags, or ask the user. The loop completes when the last coefficient of the last model is tested — only then may red flags be evaluated. See [`reference/phase1-validation.md`](reference/phase1-validation.md).

## Scripts

The skill provides reusable Python scripts in the `scripts/` directory. **Always use the script** instead of reimplementing the logic inline. Each script is a standalone CLI tool that can also be imported as a Python module.

| Script | Purpose | Used By |
|--------|---------|---------|
| `load_run_config.py` | Load and validate `run_config.json` | Phases 0–9 |
| `extract_cross_section.py` | Parse MG5 banner → cross-section (pb) | Phases 1, 2, 4, 6 |
| `parse_param_card.py` | Parse coefficient block (auto-detects anoinputs, dim8, etc.) from `param_card.dat` | Phases 1–4 |
| `setup_delphes_card.py` | Copy Delphes card + dependencies to process dir | Phases 1–4 |
| `convert_root_to_lhco.py` | Auto-detect jet branch, run `root2lhco`, validate | Phases 1–4 |
| `run_mg5.py` | Run MG5 order file with return-code checking and stage timing | Phases 1–4 |
| `normalize_process_name.py` | Normalize `e+ e- > a a` → `ep_em_to_a_a` | All phases |
| `install_mg5.py` | Auto-install MG5 with Pythia8, LHAPDF6, and Delphes | Phase -1 |
| `timing_tracker.py` | Track phase-level and MG5 sub-step timings | All phases |

For detailed CLI and Python usage, run each script with `--help` or read its docstring. Examples:

```bash
python scripts/parse_param_card.py path/to/param_card.dat
# Output: {"block_name": "anoinputs", "coefficients": {"1": 1e-12, "2": 0.0, ...}}

python scripts/run_mg5.py /opt/MG5_aMC_v3_5_6 order_p1_20260525_01.txt
```

## Output Structure

### Single Run (one energy/luminosity pair)

```
results/
  report.pdf / report.html   # Final report
  data/                      # phase1/ ... phase9/
  plots/                     # Figures
  algorithms/                # Serialized ML models
  mg5_processes/             # Collected MG5 process directories (moved from mg5path)
  orders/                    # Collected MG5 order files (moved from mg5path)
```

### Multi-Run (multiple energy/luminosity pairs)

Each pair gets its own subdirectory named `E{energy}_L{luminosity}/`. The full workflow runs independently in each.

```
results/
  E10_L1000/
    report.pdf
    data/                    # phase1/ ... phase9/
    plots/                   # Figures
    algorithms/              # Serialized ML models
    mg5_processes/           # Collected MG5 process directories
    orders/                  # Collected MG5 order files
  E14_L3000/
    report.pdf
    data/
    plots/
    algorithms/
    mg5_processes/
    orders/
  E30_L10000/
    report.pdf
    ...
```

Directory naming: `E{energy}_L{luminosity}` with dots replaced by underscores (e.g., `E13.6_L3000` → `E13_6_L3000`).

**Path interpretation in multi-run mode:** All `results/` paths in reference files should be read as `results/E{e}_L{l}/` when executing a multi-run. For example, `results/data/phase1/` becomes `results/E10_L1000/data/phase1/` for the `(10, 1000)` run.

## Common Mistakes

| Mistake | Phase | Fix |
|---------|-------|-----|
| **Asking multiple parameters in one message** | -1 | **VIOLATION**. Always ask exactly ONE parameter per message. Never present a fill-in table. |
| **Inferring defaults from history/environment** | -1 | **CRITICAL ERROR**. example1/example2 parameters are NOT defaults. Always ask. |
| **Modifying physical parameters for speed** | All | **CRITICAL ERROR**. Never modify without explicit user instruction |
| **Wrong MG5 coefficient syntax** | 1, 3, 4 | Bare `set 1 = 0.0` is **silently ignored** in MG5 launch mode. Always use `set {block_name} {idx} {value}`. The `{block_name}` comes from `parse_param_card.py` output (e.g. `anoinputs`, `dim8`). See [`reference/madgraph-reference.md`](reference/madgraph-reference.md) |
| **Forgetting luminosity conversion** | 6, 7 | `L = luminosity * 1000` (fb⁻¹ → pb⁻¹). Phase 2 uses `L' = n_scan / cs_sm` |
| **Default coefficient = 0** | 1, 3, 4 | Use `c_{n_{default}} = 1.0` if param_card default is `0.0` |
| **Ignoring MG5 return code** | 1-4 | Always check `result.returncode != 0` |
| **Using `runs[-11:]` heuristic** | 4 | Use set-difference. See [`reference/phase4-scan.md`](reference/phase4-scan.md) |
| **param_card case sensitivity** | 1 | MG5 rewrites `Block` as `BLOCK`. Match case-insensitively. See [`reference/phase1-validation.md`](reference/phase1-validation.md) |
| **param_card scan syntax** | 1, restart | After MG5 scan, param_card retains `scan:[...]` for the scanned coefficient. Detect and skip. See [`reference/phase1-validation.md`](reference/phase1-validation.md) |
| **Hardcoding `nev_scan` in Phase 6** | 6 | Read from `sm_baseline.json` |
| **Using `nonzero_ops[0]` for ref** | 6 | Use the anchor operator from `anchor.json` |
| **Confusing `N_sig` with `N_all`** | 7 | `N_sig` excludes SM; `N_all` includes it |
| **Stopping after first zero-cross-section operator** | 1 | **CRITICAL VIOLATION.** Test ALL coefficients before any red flag check. If 10 operators, test all 10 even if 9 are zero. |
| **Forgetting model prefix in process dirs** | 1, 3, 4 | Always include model name: `{folder_base}_{model}_p1_NP` |
| **Training per-operator instead of anchor-only** | 5 | Train ONCE on anchor operator; apply to ALL operators |
| **Writing to bare `results/` in multi-run mode** | All | Compute `RUN_DIR = f"E{e}_L{l}"` in Phase 0. ALL paths must use `results/{RUN_DIR}/` |

## Red Flags — Stop and Report

| Condition | Phase | Meaning |
|-----------|-------|---------|
| `generate` fails with MG5 error | 1 | Invalid process or model mismatch |
| **Zero non-zero operators** after Phase 1 | 1 | Process insensitive to ALL provided SMEFT models |
| `cs_sm = 0` | 2 | SM process has zero cross-section |
| **ML AUC ≤ 0.5** | 5 | Classifier no better than random |
| **ML AUC > 0.9999** | 5 | Possible overfitting — flag in audit |
| **Quadratic fit fails** | 6 | Fit coefficients non-physical |
| **No real roots for S=2** | 7 | Insufficient luminosity or selection efficiency |
| **Constraint width increases with S** | 7 | Statistics violation — check fit errors |
| **Tempted to reduce events for speed** | All | STOP. Physical parameters are not tuning knobs |
