---
name: automated-smeft-ml-pheno
description: Use when performing automated SMEFT phenomenology studies with machine learning-based event selection. Supports single or multiple (energy, luminosity) combinations — each combination runs the full workflow independently. ONLY triggered when the user explicitly provides ALL required inputs (madgraph_path, process, model, energy, luminosity) or requests a SMEFT study with sufficient context to identify these parameters. If inputs are missing, the skill MUST ask for them before executing any workflow step. CutExperiment is optional (will be cloned if missing). Outputs a report showing expected Wilson coefficient constraints from ML-optimized event selection strategies.
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
| Asking "是否用 debug 模式？" / "Use debug mode?" | Use the `debug` parameter as provided in Phase -1 only |
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
| `model` | SMEFT model name | `SMEFTsim_U35_MwScheme_UFO` |
| `energy` | Center-of-mass energy in TeV (single value or list) | `13.6` or `[10, 14, 30]` |
| `luminosity` | Integrated luminosity in fb⁻¹ (single value or list) | `3000` or `[1000, 3000, 10000]` |

### CutExperiment

`cutexperiment_path` is **not strictly required**:

- If the user provides it: validate the path exists
- If missing: ask the user "Do you already have CutExperiment installed? If so, provide the path. If not, I will clone it from the Gitee repository."
- If the user does not have it: clone from `https://gitee.com/NBAlexis/CutExperiment.git` into the working directory (e.g., `./CutExperiment`) and use that path
- **Clone command**: `git clone https://gitee.com/NBAlexis/CutExperiment.git`

## Phase -1: Input Collection (Operation Steps)

**This is Step 1 of the workflow. Do NOT skip. Do NOT proceed to Phase 0 until completed.**

**CRITICAL: Phase -1 is the ONLY interactive stage of the entire workflow. Once Step 5 completes, ALL subsequent phases (0–9) execute FULLY AUTOMATICALLY without any user interaction. Do NOT stop, do NOT ask for confirmation, do NOT present options mid-execution.**

When this skill is invoked, immediately execute the following steps in order. No exceptions.

### Step 1: Check Required Inputs

Verify the following are present:
- `madgraph_path`
- `process`
- `model`
- `energy`
- `luminosity`

**DO NOT** check file systems, do NOT create directories, do NOT run any commands before this step completes.

**CRITICAL — Parameter Source Restriction:**
- `process`, `model`, `energy`, `luminosity` — **MUST be explicitly provided by the user in the current conversation**. No defaults, no inference from files or history.
- `madgraph_path`, `cutexperiment_path` — **May use defaults** from historical conversation context, environment variables, or common install paths (e.g., `~/MG5_aMC_v*`, `~/CutExperiment`). However, the user **MUST still be asked to confirm or override** the default. Never silently accept a default without user confirmation.
- **NEVER** infer `process`, `model`, `energy`, or `luminosity` from filesystem state, existing files, code, or cached configs.
- If any of the 5 required parameters are not explicitly provided in the current conversation, they are **MISSING** — proceed to Step 2

**Restart handling — CRITICAL:**
- If the user explicitly requests a restart or re-test (e.g., says "重新测试", "restart", "start over", "重新来", "重来", or any phrase clearly indicating they want to begin from scratch), **treat ALL parameters as MISSING** regardless of prior conversation context. Proceed to Step 2 and re-ask every parameter.
- This rule **OVERRIDES** the "present in current conversation" check above. User intent to restart takes absolute precedence.

### Step 2: If Any Input Is Missing, Ask the User

**ALWAYS ask exactly ONE parameter per message.** After the user answers, move to the next. Never present a list or table of parameters to fill. Never ask "please provide all of the above" or "confirm previous parameters" — even if the user says "start now", "重新测试", or "use the same as before". The user must be able to type paths, process strings, and numeric values directly, one per message. Violating this rule breaks the standardized input collection and leads to workflow failures.

**Question order:**

Each question must include a progress indicator (e.g., `[1/9]`) so the user knows how many inputs remain:

1. `[1/9] madgraph_path` — Ask:
   > "[1/9] What is the absolute path to your MadGraph5 installation? (Press Enter to use `{default_path}`). If you don't have one, type `yes` and I'll install it automatically — this downloads ~31 MB and compiles Pythia8, LHAPDF6, and Delphes (required for PDF systematics). Total time: 20–40 minutes."
   > "请提供 MadGraph5 的绝对路径（按 Enter 使用 `{default_path}`）。如果没有安装，输入 `yes` 我可以自动安装——需下载约 31 MB，编译 Pythia8、LHAPDF6 和 Delphes（用于 PDF 系统误差）。预计耗时 20–40 分钟。"
   - If the user provides a path: use `os.path.expanduser()` and `os.path.abspath()` to resolve it, then validate that `bin/mg5_aMC` exists under it
   - If the user answers `yes`:
     1. Ask for install directory:
        > "[1/9] Where should MG5 be installed? (Press Enter to use `~/HEP_Tools`)"
        > "MG5 应该安装到哪个目录？（按 Enter 使用 `~/HEP_Tools`）"
     2. Fetch `https://launchpad.net/mg5amcnlo` and parse the HTML to find the LTS download URL and the extracted directory name (e.g. `MG5_aMC_v3_5_15`)
     3. Run: `python scripts/install_mg5.py {dir} --url {download_url} --name {extracted_name}`
     4. Use the returned path as `madgraph_path`
     5. Record `auto_installed_mg5 = true` for Phase 0 verification
   - If the user presses Enter without a path and no default exists: treat as `yes` (auto-install)
2. `[2/9] workdir` —
   > "[2/9] Where should results be saved? (Press Enter to use the current directory)"
   > "结果保存到哪个目录？（按 Enter 使用当前目录）"
3. `[3/9] process` —
   > "[3/9] What collider process should be studied? (Provide physics process only, no NP=/QED=/QCD= suffixes)"
   > "要研究什么对撞过程？（仅提供物理过程，不要加 NP=/QED=/QCD= 等后缀）"
   - After the user provides `process`, **immediately inspect the initial state** (particles left of `>`)
   - If the initial state is `e- p`, `e+ p`, `e- p~`, or `e+ p~` (electron-proton collider), **insert an extra required question before continuing**:
     > "[追加] Your process involves an electron-proton collider. What is the proton beam energy in GeV (`ebeam_proton`)?"
     > "您的过程涉及电子-质子对撞机。质子束流能量是多少 GeV（`ebeam_proton`）？"
   - If the initial state is anything else (e+e-, pp, mu+mu-), skip this question
4. `[4/9] model` — Before asking, scan the skill's `dependency/` directory (same directory as `SKILL.md`) at runtime for available UFO models. Do **not** hardcode a list. Present the question as:
   > "[4/9] What SMEFT model name should be used? Models available in the skill dependency folder: {dependency_models}. You may also use any model already installed in `{madgraph_path}/models/`."
   > "使用哪个 SMEFT 模型？skill 依赖文件夹中可用的模型：{dependency_models}。也可以使用已安装在 `{madgraph_path}/models/` 中的任何模型。"
   - After the user provides `model`:
     1. Resolve the path: `mg5_models = os.path.join(os.path.expanduser(madgraph_path), "models", model)`
     2. Check if `mg5_models` exists
     3. If it exists: proceed
     4. If it does **not** exist:
        - Check if `{skill_dir}/dependency/{model}` exists (re-scan at runtime, do not reuse the earlier list)
        - If it exists:
          > "[4/9] Model `{model}` was not found in `{madgraph_path}/models/`. The skill has this model in its dependency folder. Copy it to `{madgraph_path}/models/`? (Type `yes` to copy, or provide an alternative model name:)"
          > "在 `{madgraph_path}/models/` 中未找到模型 `{model}`。skill 依赖文件夹中有此模型。是否复制到 `{madgraph_path}/models/`？（输入 `yes` 复制，或提供其他模型名称：）"
        - If the user answers `yes`: copy `{skill_dir}/dependency/{model}` to `{madgraph_path}/models/{model}`
        - If the user provides a different model name: repeat the check
        - If the model is not in `dependency/` either: report "Model `{model}` not found in MG5 and not available in skill dependencies. Please provide a valid model name or install it manually."
5. `[5/9] energy` —
   > "[5/9] What is the center-of-mass energy in TeV? Provide a single value or a list, e.g. `10` or `[10, 14, 30]`."
   > "质心能量是多少 TeV？提供单个值或列表，例如 `10` 或 `[10, 14, 30]`。"
6. `[6/9] luminosity` —
   > "[6/9] What is the integrated luminosity in fb⁻¹? Provide a single value or a list matching the energy length, e.g. `3000` or `[1000, 3000, 10000]`."
   > "积分亮度是多少 fb⁻¹？提供单个值或与能量长度匹配的列表，例如 `3000` 或 `[1000, 3000, 10000]`。"
7. `[7/9] cutexperiment_path` — If a default exists from context (e.g., previous conversation, `~/CutExperiment`), ask:
   > "[7/9] Do you already have CutExperiment installed? If so, provide the path. If not, press Enter to clone from `https://gitee.com/NBAlexis/CutExperiment.git` into `{default_path}`."
   > "您是否已经安装了 CutExperiment？如果已安装请提供路径。如果未安装，按 Enter 从 `https://gitee.com/NBAlexis/CutExperiment.git` 克隆到 `{default_path}`。"
   If no default exists:
   > "[7/9] Do you already have CutExperiment installed? If so, provide the path. If not, I will clone it from `https://gitee.com/NBAlexis/CutExperiment.git`."
   > "您是否已经安装了 CutExperiment？如果已安装请提供路径。如果未安装，我将从 `https://gitee.com/NBAlexis/CutExperiment.git` 克隆。"
8. `[8/9] Delphes card selection` — After `madgraph_path`, `process`, and `energy` are known:
   - **If the user provided `custom_card`** (absolute path to a `.tcl` file outside `{mg5path}/Delphes/cards/`): skip the scan and use the custom card directly. Validate that the file exists.
   - **Otherwise**, run the auto-recommendation:
     1. Scan `{madgraph_path}/Delphes/cards/` for all `*.tcl` files
     2. **Filter out non-detector cards** — exclude `converter_card.tcl`, `gen_card.tcl`, `validation_card.tcl`, `delphes_card_llptest.tcl`, and any file whose name starts with `trackResolution`, `trkCounting`, or `gen_`
     3. Infer the collider type from the initial state of `process`
     4. Score each remaining card by matching its filename against the collider type
     5. Recommend the highest-scoring card
     6. Present to the user (only showing cards that scored > 0):
        > "[8/9] Scanning detector cards in `{mg5path}/Delphes/cards/`...\n> Based on your process (`{process}`) at `{energy}` TeV, the recommended Delphes card is: **{recommended_card}**\n> Other matching options: {matched_card_list}\n> Press Enter to use the recommended card, or type a different card name to override."
        > "正在扫描 `{mg5path}/Delphes/cards/` 中的探测器卡片...\n> 根据您的过程（`{process}`）在 `{energy}` TeV 下，推荐的 Delphes 卡片是：**{recommended_card}**\n> 其他匹配选项：{matched_card_list}\n> 按 Enter 使用推荐的卡片，或输入其他卡片名称覆盖。"
   - `delphes_card`: the selected `.tcl` card file name (e.g., `delphes_card_CEPC.tcl`) or absolute path (for `custom_card`)
   - If the user presses Enter or provides no answer, use the recommended card
   - If the user types a card name, validate that it exists in `{mg5path}/Delphes/cards/`
   - **If no cards match the collider type** (all scores = 0), show:
     > "[8/9] No detector cards match your collider type. Available cards: {all_filtered_cards}. Please specify one:"
     > "没有探测器卡片匹配您的对撞机类型。可用卡片：{all_filtered_cards}。请指定一个："

9. `[9/9]` — **After all required inputs are collected, also ask**:
   > "[9/9] Are there any other requirements or preferences? Optional settings you can specify:
   > - `debug=true` — divide all event counts by 10 for faster testing (default: false)
   > - `algorithms` — specify which ML algorithms to compare (default: automatically select and test multiple algorithms)
   > - `polarization` — beam polarization as `polbeam1,polbeam2` in range [-1, 1] (default: no polarization)
   > - `custom_card` — absolute path to a custom Delphes card outside `{mg5path}/Delphes/cards/`
   > - Specific operators to focus on, report format preferences, or additional analysis
   > Press Enter to skip and use all defaults."
   > "还有其他要求或偏好吗？可选设置：
   > - `debug=true` — 所有事件数除以 10 以加快测试（默认：false）
   > - `algorithms` — 指定要比较的 ML 算法（默认：自动选择并测试多种算法）
   > - `polarization` — 束流极化，格式为 `polbeam1,polbeam2`，范围 [-1, 1]（默认：无偏振）
   > - `custom_card` — 自定义 Delphes 卡片的绝对路径（在 `{mg5path}/Delphes/cards/` 之外）
   > - 要重点关注的特定算符、报告格式偏好或其他分析需求
   > 按 Enter 跳过并使用所有默认值。"

   This is **NOT optional** — it MUST be asked even if the user is in a hurry. The user can always press Enter to accept defaults, but the question itself must be presented.

**Defaults:**
- `workdir`: the **Working Directory** (shell `pwd`) if user presses Enter or provides no answer
- `cutexperiment_path`: clone from Gitee if user says no or provides no path
- `delphes_card`: auto-recommended based on process initial state and energy (see below)
- `debug`: false
- `algorithms`: automatically select and test multiple algorithms

### Delphes Card Auto-Recommendation Logic

When the user does not specify a `delphes_card`, automatically select one using the following rules:

1. **List available cards**: Scan `{mg5path}/Delphes/cards/` for all `*.tcl` files. Exclude obvious non-detector cards:
   - `converter_card.tcl`
   - `gen_card.tcl`, `gen_*.tcl`
   - `validation_card.tcl`
   - `delphes_card_llptest.tcl`
   - Any file starting with `trackResolution` or `trkCounting`

2. **Extract initial state** from `process_name` (particles left of `>`):
   - `e+ e-` / `e- e+` → electron-positron collider
   - `p p` / `p~ p~` / `p p~` → proton-proton collider
   - `mu+ mu-` / `mu- mu+` → muon collider
   - `e- p` / `e+ p` / `e- p~` / `e+ p~` → electron-proton collider

3. **Score each available card** by matching keywords in its filename against the inferred collider type. The scoring is **flexible** — it operates on whatever filenames actually exist in the user's `Delphes/cards/` directory, not a hardcoded list:
   - For `e+ e-` processes: filenames containing substrings associated with e+e- colliders (e.g., `CEPC`, `CLIC`, `Circular`, `ILC`) score higher
   - For `p p` processes: filenames containing substrings associated with hadron colliders (e.g., `CMS`, `ATLAS`, `LHC`) score higher
   - For `mu+ mu-` processes: filenames containing `Muon` score higher
   - For `e- p` / `e+ p` processes: filenames containing `FCCeh` or `LHeC` score higher
   - Any card whose name does not contain a recognizable substring receives a score of 0
   - **Energy refinement** (optional): for e+e- colliders, if energy < 1 TeV, boost cards with `CEPC` or `Circular` in their name; if > 1 TeV, boost cards with `CLIC`

4. **Select the highest-scoring card** as the recommendation. If multiple cards tie, prefer the one whose name appears first alphabetically.

5. **Filtering for user display**: When presenting options to the user, only show cards with score > 0 (i.e., cards that match the inferred collider type). If no card scores above zero, show all remaining filtered cards and ask the user to specify one. If the directory is empty after filtering, report the error and abort.

### Step 3: Wait for User Response

After asking for missing inputs, **STOP**. Do nothing else. Wait for the user to provide all requested information.

### Step 4: Validate Received Inputs

- `madgraph_path`: verify the directory exists and contains `bin/mg5_aMC`
- `workdir`: if provided, verify the directory exists (create automatically if missing); default to the Working Directory (shell `pwd`). **Verify `workdir` is NOT inside the Skill Directory** (where `SKILL.md` is located). If it is, use the Skill Directory's parent instead.
- `process`: verify it does not contain `NP=`, `QED=`, or `QCD=` suffixes (strip them if present)
- `energy`: all values > 0
- `luminosity`: all values > 0
- `ebeam_proton` (if process is ep collider): verify > 0
- `delphes_card` (if user-specified as a filename): verify the file exists under `{madgraph_path}/Delphes/cards/`
- `custom_card` (if user-specified as an absolute path): verify the file exists at the given path
- `polarization` (if provided): verify format is two comma-separated floats in [-1, 1]
- **List validation**: If `energy` and `luminosity` are both lists, they MUST have the same length. If lengths differ, report the mismatch and ask the user to correct.

If validation fails, report the specific failure and re-ask for that input.

### Step 5: Confirm Phase -1 Completion

Before proceeding to Phase 0, confirm:
- [ ] All 5 required parameters were explicitly provided by the user **in this conversation**
- [ ] No parameter was sourced from files, code, logs, or historical context
- [ ] Input validation passed (Step 4)

**Phase -1 is complete ONLY when the user has explicitly confirmed or provided every parameter through dialogue.**

**After Step 5 passes, the interactive portion of the workflow is OVER. From this point forward, the workflow is FULLY AUTOMATED. Do NOT wait for user confirmation. Do NOT ask "是否继续？" / "Shall I proceed?". Immediately execute Phase 0, then sequentially execute Phases 1–9 without stopping.**

### Step 6: Build Run Configuration List

Convert inputs into a list of run configurations. Each configuration is one `(energy, luminosity)` pair.

| Input Pattern | Run Configurations |
|---------------|-------------------|
| Single energy, single luminosity | `[(energy, luminosity)]` — 1 run |
| List energy `[e1, e2, ...]`, list luminosity `[l1, l2, ...]` | `[(e1, l1), (e2, l2), ...]` — N runs |
| Single energy, list luminosity | **Invalid** — lengths must match |
| List energy, single luminosity | **Invalid** — lengths must match |

Example: `energy = [10, 14, 30]`, `luminosity = [1000, 3000, 10000]` → 3 runs: `(10, 1000)`, `(14, 3000)`, `(30, 10000)`

### Step 6: Prohibited Behaviors (Will Cause Failure)

| Prohibited Behavior | Why |
|---------------------|-----|
| **Asking multiple parameters in one message** | **VIOLATION of Step 2.** One parameter per message, no tables, no "provide all above". |
| Inferring defaults from example1/example2/history | Each run is independent; historical parameters are NOT defaults |
| Using "start now" / "直接开始" as override | User urgency does NOT bypass input collection |
| Proceeding to Phase 0 with missing inputs | Phase -1 must be fully completed first |
| Creating directories before all inputs are validated | Directory creation is a Phase 0 action, not Phase -1 |
| **Stopping mid-execution to ask user whether to continue** | **ONCE STARTED, the workflow MUST run to completion automatically. Only stop on errors or red flags.** |

## Physical Parameter Immutability

The following are **immutable** and must NEVER be modified for any reason, including speed:

- Event counts (`nev_phase1`, `nev_phase2`, `nev_sm`, `nev_np`, `nev_scan`)
- `luminosity`, `energy`
- Any coefficient values or scan ranges from previous phases

**If execution is long, report progress periodically but CONTINUE execution automatically. Do NOT stop to ask whether to proceed. Do NOT self-adjust parameters. The only valid reasons to stop are: (1) an error/red flag occurs, (2) the user explicitly interrupts.**

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

**CRITICAL: Phase -1 is the ONLY interactive stage. Once Phase -1 Step 5 completes, Phases 0–9 execute FULLY AUTOMATICALLY and sequentially without stopping. Do NOT pause to ask the user whether to continue, whether to use debug mode, or to present options. Report progress at natural phase boundaries, then immediately proceed to the next phase. The only valid stop conditions are errors, red flags, or explicit user interrupt.**

### Phase Completion Rule (MANDATORY)

**Every phase MUST run to completion before any red flag check is applied.**

| Situation | Correct Behavior | Wrong Behavior |
|-----------|------------------|----------------|
| Phase 1: first few operators have σ = 0 | **Continue** testing ALL remaining operators. Complete Phase 1 fully. | Stop mid-phase and declare red flag |
| Phase 4: first scan point has issues | **Continue** processing ALL 11 scan points. Complete Phase 4 fully. | Stop after partial scan |
| Phase 5: first algorithm performs poorly | **Continue** testing ALL configured algorithms. Complete Phase 5 fully. | Skip remaining algorithms |

**Red flags are checked AFTER the phase completes, NEVER during execution.** A zero cross-section for an individual operator is a valid Phase 1 result, not a reason to abort. The red flag "Zero non-zero operators after Phase 1" means **ALL operators tested returned σ = 0 after the entire phase finished** — at that point the workflow STOPS because there is no sensitive operator to study. But you MUST NOT stop early because the first few were zero.

### Phase Workflow Reference

The following table summarizes the MG5 invocation for every phase that runs MadGraph. This is the canonical reference — all details in per-phase documents must match this table.

| Phase | `generate` line | Output folder suffix | Coefficient setting | `nevents` | Output files |
|-------|-----------------|----------------------|---------------------|-----------|--------------|
| 1 | `generate {process} NP>0` | `_p1_NP` | One at a time: target = `c0`, all others = `0.0` | `nev_phase1` | `operators.json`, `cross_sections.json` |
| 2 | `generate {process} NP=0` | `_p2_SM` | All `set anoinputs {idx} 0.0` | `nev_phase2` | `sm_baseline.json`, `coefficient_ranges.json` |
| 3 SM | `generate {process} NP=0` | `_p3_SM` | All `set anoinputs {idx} 0.0` | `nev_sm` | `sm_banner.txt`, `sm.lhco` |
| 3 NP | `generate {process} NP>0` | `_p3_NP` | One at a time: target = `c1` (from Phase 2), others = `0.0` | `nev_np` | `np_oi_banner.txt`, `np_oi.lhco` |
| 4 | `generate {process}` | `_p4` | One operator: `set anoinputs {idx} scan:[v0,v1,...]`; all others = `0.0` | `nev_scan` | `np_oi_f0_banner.txt` … `np_oi_f10_banner.txt` and `.lhco` |

**Key rules:**
- Each phase uses a **separate process directory** (independent `output` step). Never reuse a directory from another phase.
- `scan:[...]` syntax is **only used in Phase 4**. Phases 1 and 3 NP test one coefficient at a time with individual `launch` commands.
- Phase 4 output uses **index-based naming** (`f0` … `f10`) mapped by sorted run number, not coefficient value.

### Multi-Run Mode

If `energy` and `luminosity` are both lists, execute Phases 0–9 **once per `(energy, luminosity)` pair**. Each run is independent and uses its own output subdirectory.

| Phase | Purpose | Reference |
|-------|---------|-----------|
| **-1** | **Input Collection** — verify all required inputs; ask user if any missing (see below) | **MANDATORY — see Operation Steps** |
| 0 | Environment validation | [`reference/phase0-env.md`](reference/phase0-env.md) |
| 1 | Identify non-zero operators | [`reference/phase1-validation.md`](reference/phase1-validation.md) |
| 2 | Estimate coefficient ranges `[-c1, c1]` | [`reference/phase2-range.md`](reference/phase2-range.md) |
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
2. **Parameter source is the user ONLY**: Never read inputs from existing files, scripts, logs, or historical context. If a parameter is not explicitly stated in the current conversation, it is missing — ask for it.
3. **MG5 return code**: Every `subprocess.run` invoking MG5 MUST check `returncode != 0`. Never silently ignore failures.
3. **No `runs[-11:]`**: Use set-difference (`new_runs = all_runs - existing_runs`) to track exactly which runs MG5 created. See [`reference/phase4-scan.md`](reference/phase4-scan.md).
4. **No tag_2**: Never delete files from an existing `run_XX` and re-launch. If the entire process directory must be re-run, remove large temps (`*.root`, `*.lhe.gz`, `*.hepmc.gz`) and rename the **process directory** (not individual runs). See [`reference/phase4-scan.md`](reference/phase4-scan.md).
5. **Explicit o1**: Use `ref_op = "o1"` for threshold optimization. Do NOT use `nonzero_ops[0]`.
6. **Pass `nev_scan`**: Read `n_scan` from `sm_baseline.json`. Do NOT hardcode in Phase 6.
7. **param_card parser**: Match `Block` case-insensitively; handle `scan:[...]` syntax; reset `in_block` on every new `Block` header. See [`reference/phase1-validation.md`](reference/phase1-validation.md).
8. **Cleanup after Phase 8**: Move all MG5 process directories from `mg5path` to `results/mg5_processes/` using `mv` (not `cp`). This prevents `mg5path` from accumulating unmanaged folders across runs. See [`reference/cleanup.md`](reference/cleanup.md).
9. **MadGraph conventions**: All MG5 process creation, event generation, Delphes card setup, and ROOT→LHCO conversion follow [`reference/madgraph-reference.md`](reference/madgraph-reference.md). **Reusable scripts** are provided in `scripts/` — use them instead of reimplementing (see [Scripts](#scripts)).
10. **Feature extraction**: LHCO→CSV conversion follows [`reference/cutexperiment-reference.md`](reference/cutexperiment-reference.md) and adapts to the actual final-state particles in `process`.
11. **Run directory prefix (multi-run mode)**: Before Phase 0, compute `RUN_DIR = f"E{energy}_L{luminosity}"` (dots replaced by underscores). ALL file paths in ALL phases MUST prefix `results/` with `RUN_DIR/`. Single-run mode uses `results/` directly. This is NOT optional — verify by checking `results/E{e}_L{l}/` exists before writing any data. See [Output Structure](#output-structure) for examples.
12. **No concurrent MG5 processes**: MadGraph5 internally uses multi-threading (OpenMP) and will saturate all CPU cores. Launching multiple MG5 processes in parallel causes CPU contention and is **slower** than sequential execution. Run MG5 invocations **one at a time** — never parallelize across operators, scan points, or phases.

## Scripts

The skill provides reusable Python scripts in the `scripts/` directory. **Always use the script** instead of reimplementing the logic inline. Each script is a standalone CLI tool that can also be imported as a Python module.

| Script | Purpose | Used By |
|--------|---------|---------|
| `extract_cross_section.py` | Parse MG5 banner → cross-section (pb) | Phases 1, 2, 4, 6 |
| `parse_param_card.py` | Parse `Block anoinputs` from `param_card.dat` | Phase 1, restart |
| `setup_delphes_card.py` | Copy Delphes card + dependencies to process dir | Phases 1–4 |
| `convert_root_to_lhco.py` | Auto-detect jet branch, run `root2lhco`, validate | Phases 1–4 |
| `run_mg5.py` | Run MG5 order file with return-code checking and stage timing | Phases 1–4 |
| `normalize_process_name.py` | Normalize `e+ e- > a a` → `ep_em_to_a_a` | All phases |
| `timing_tracker.py` | Track phase-level and MG5 sub-step timings | All phases |

### CLI Usage

```bash
python scripts/extract_cross_section.py path/to/run_01_tag_1_banner.txt
# Output: 0.0004231

python scripts/parse_param_card.py path/to/param_card.dat
# Output: {"1": 1e-12, "2": 0.0, ...}

python scripts/run_mg5.py /opt/MG5_aMC_v3_5_6 order_p1_20260525_01.txt
```

### Python Import

```python
from scripts.extract_cross_section import extract_cross_section
from scripts.parse_param_card import parse_anoinputs
from scripts.run_mg5 import run_mg5
from scripts.convert_root_to_lhco import convert_root_to_lhco
from scripts.timing_tracker import TimingTracker, phase_timer
# etc.
```

### Timing Tracking

The skill tracks timing at two levels:

1. **Phase-level**: Use `timing_tracker.phase_timer("Phase X: Name")` as a context manager around each phase. This prints a progress banner showing elapsed time and completed phases.
2. **MG5 sub-step**: `run_mg5()` automatically detects and times MadGraph, Pythia8, and Delphes stages by parsing MG5 stdout in real time. Pass a `TimingTracker` instance to integrate:

```python
from scripts.timing_tracker import TimingTracker
from scripts.run_mg5 import run_mg5

tracker = TimingTracker()
with tracker.phase_timer("Phase 4: Coefficient Scan"):
    result = run_mg5(mg5path, order_filename, timing_tracker=tracker)
tracker.print_report()
tracker.save_log("results/timing_log.json")
```

### Script Guarantees

- Each script handles its own error cases and raises descriptive exceptions
- Scripts are tested against MG5_aMC v3.x banner formats
- Scripts auto-detect jet branches and MG5 binary names (mg5_aMC / mg5)

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
| **Wrong MG5 coefficient syntax** | 1, 3, 4 | Bare `set 1 = 0.0` is **silently ignored** in MG5 launch mode. Always use `set anoinputs {idx} {value}`. See [`reference/madgraph-reference.md`](reference/madgraph-reference.md) |
| **Forgetting luminosity conversion** | 6, 7 | `L = luminosity * 1000` (fb⁻¹ → pb⁻¹). Phase 2 uses `L' = n_scan / cs_sm` |
| **Default coefficient = 0** | 1, 3, 4 | Use `c0 = 1.0` if default is `0.0` |
| **Ignoring MG5 return code** | 1-4 | Always check `result.returncode != 0` |
| **Using `runs[-11:]` heuristic** | 4 | Use set-difference. See [`reference/phase4-scan.md`](reference/phase4-scan.md) |
| **param_card case sensitivity** | 1 | MG5 rewrites `Block` as `BLOCK`. Match case-insensitively. See [`reference/phase1-validation.md`](reference/phase1-validation.md) |
| **param_card scan syntax** | 1, restart | After MG5 scan, param_card retains `scan:[...]` for the scanned coefficient. Detect and skip. See [`reference/phase1-validation.md`](reference/phase1-validation.md) |
| **Hardcoding `nev_scan` in Phase 6** | 6 | Read from `sm_baseline.json` |
| **Using `nonzero_ops[0]` for ref** | 6 | Use `ref_op = "o1"` |
| **Confusing `N_sig` with `N_all`** | 7 | `N_sig` excludes SM; `N_all` includes it |
| **Writing to bare `results/` in multi-run mode** | All | Compute `RUN_DIR = f"E{e}_L{l}"` in Phase 0. ALL paths must use `results/{RUN_DIR}/` |

## Red Flags — Stop and Report

| Condition | Phase | Meaning |
|-----------|-------|---------|
| `generate` fails with MG5 error | 1 | Invalid process or model mismatch |
| **Zero non-zero operators** after Phase 1 | 1 | Process insensitive to this SMEFT model |
| `cs_sm = 0` | 2 | SM process has zero cross-section |
| **ML AUC ≤ 0.5** | 5 | Classifier no better than random |
| **Quadratic fit fails** | 6 | Fit coefficients non-physical |
| **No real roots for S=2** | 7 | Insufficient luminosity or selection efficiency |
| **Constraint width increases with S** | 7 | Statistics violation — check fit errors |
| **Tempted to reduce events for speed** | All | STOP. Physical parameters are not tuning knobs |
