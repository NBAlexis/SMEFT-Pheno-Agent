# Phase -1: Input Collection

> **This is Step 1 of the workflow.** Do NOT skip. Do NOT proceed to Phase 0 until completed.
>
> **CRITICAL: Phase -1 is the ONLY interactive stage.** Once all steps complete, ALL subsequent phases (0–9) execute FULLY AUTOMATICALLY without any user interaction. Do NOT stop, do NOT ask for confirmation, do NOT present options mid-execution.

## Prerequisites

All other skill reference documents assume these inputs have been collected and validated. See [`SKILL.md`](../SKILL.md) for the required parameter list.

## Step 1: Check Required Inputs

Verify the following are present:
- `madgraph_path`
- `process`
- `model`
- `energy`
- `luminosity`

**DO NOT** check file systems, do NOT create directories, do NOT run any commands before this step completes.

**CRITICAL — Parameter Source Restriction:**
- `process`, `model`, `energy`, `luminosity` — **MUST be explicitly provided by the user in the current conversation**. No defaults, no inference from files or history.
- `madgraph_path`, `cutexperiment_path` — The user **MUST be asked** for these. You may show a suggested default in the prompt (e.g., a path from historical context or common install location), but the user must actively confirm it (e.g., type `yes` to accept the default) or provide a different value. **Never silently accept a default without asking.**
- **NEVER** infer `process`, `model`, `energy`, or `luminosity` from filesystem state, existing files, code, or cached configs.
- If any of the 5 required parameters are not explicitly provided in the current conversation, they are **MISSING** — proceed to Step 2

**Restart handling — CRITICAL:**
- If the user explicitly requests a restart or re-test (e.g., says "重新测试", "restart", "start over", "重新来", "重来", or any phrase clearly indicating they want to begin from scratch), **treat ALL parameters as MISSING** regardless of prior conversation context. Proceed to Step 2 and re-ask every parameter.
- This rule **OVERRIDES** the "present in current conversation" check above. User intent to restart takes absolute precedence.

## Step 2: If Any Input Is Missing, Ask the User

**ALWAYS ask exactly ONE parameter per message.** After the user answers, move to the next. Never present a list or table of parameters to fill. Never ask "please provide all of the above" or "confirm previous parameters" — even if the user says "start now", "重新测试", or "use the same as before". The user must be able to type paths, process strings, and numeric values directly, one per message. Violating this rule breaks the standardized input collection and leads to workflow failures.

**Question order:**

Each question must include a progress indicator (e.g., `[1/9]`) so the user knows how many inputs remain:

1. `[1/9] madgraph_path` — Ask:
   > "[1/9] What is the absolute path to your MadGraph5 installation? Suggested default: `{default_path}`. Type `yes` to use the default, or provide a different path. If you don't have one installed, type `install` and I'll install it automatically — this downloads ~31 MB and compiles Pythia8, LHAPDF6, and Delphes (required for PDF systematics). Total time: 20–40 minutes."
   > "请提供 MadGraph5 的绝对路径（建议默认：`{default_path}`）。输入 `yes` 使用默认路径，或提供其他路径。如果尚未安装，输入 `install` 我可以自动安装——需下载约 31 MB，编译 Pythia8、LHAPDF6 和 Delphes（用于 PDF 系统误差）。预计耗时 20–40 分钟。"
   - If the user provides a path: use `os.path.expanduser()` and `os.path.abspath()` to resolve it, then validate that `bin/mg5_aMC` exists under it
   - If the user answers `yes`:
     1. Ask for install directory:
        > "[1/9] Where should MG5 be installed? Suggested default: `~/HEP_Tools`. Type `yes` to use it, or provide a different directory:"
        > "MG5 应该安装到哪个目录？建议默认：`~/HEP_Tools`。输入 `yes` 使用默认目录，或提供其他目录："
     2. Fetch `https://launchpad.net/mg5amcnlo` and parse the HTML to find the LTS download URL and the extracted directory name (e.g. `MG5_aMC_v3_5_15`)
     3. Run: `python scripts/install_mg5.py {dir} --url {download_url} --name {extracted_name}`
     4. Use the returned path as `madgraph_path`
     5. Record `auto_installed_mg5 = true` for Phase 0 verification
   - If the user types `install` or provides no path and no default exists: treat as auto-install
2. `[2/9] workdir` —
   > "[2/9] Where should results be saved? Suggested default: the current directory. Type `yes` to use it, or provide a different path:"
   > "结果保存到哪个目录？建议默认：当前目录。输入 `yes` 使用默认目录，或提供其他路径："
3. `[3/9] process` —
   > "[3/9] What collider process should be studied? (Provide physics process only, no NP=/QED=/QCD= suffixes)"
   > "要研究什么对撞过程？（仅提供物理过程，不要加 NP=/QED=/QCD= 等后缀）"
   - After the user provides `process`, **immediately inspect the initial state** (particles left of `>`)
   - If the initial state is `e- p`, `e+ p`, `e- p~`, or `e+ p~` (electron-proton collider), **insert an extra required question before continuing**:
     > "[追加] Your process involves an electron-proton collider. What is the proton beam energy in GeV (`ebeam_proton`)?"
     > "您的过程涉及电子-质子对撞机。质子束流能量是多少 GeV（`ebeam_proton`）？"
   - If the initial state is anything else (e+e-, pp, mu+mu-), skip this question
4. `[4/9] model` — Before asking, scan the skill's `dependency/` directory (same directory as `SKILL.md`) at runtime for available UFO models. Do **not** hardcode a list. Present the question as:
   > "[4/9] What SMEFT model name(s) should be used? Provide a single model or a list, e.g. `AQGCm_UFO` or `[AQGCm_UFO, AQGCs_UFO]`. Models available in the skill dependency folder: {dependency_models}. You may also use any model already installed in `{madgraph_path}/models/`."
   > "使用哪个 SMEFT 模型？提供单个模型或列表，例如 `AQGCm_UFO` 或 `[AQGCm_UFO, AQGCs_UFO]`。skill 依赖文件夹中可用的模型：{dependency_models}。也可以使用已安装在 `{madgraph_path}/models/` 中的任何模型。"
   - Parse the user's response:
     - If a single string (no brackets): treat as `[model]`
     - If a list format (e.g., `[AQGCm_UFO, AQGCs_UFO]` or comma-separated): parse into a list
     - **Do NOT accept `"all"`** — user must explicitly list models
   - For **each** model in the parsed list:
     1. Resolve the path: `mg5_models = os.path.join(os.path.expanduser(madgraph_path), "models", model)`
     2. Check if `mg5_models` exists
     3. If it exists: proceed to next model
     4. If it does **not** exist:
        - Check if `{skill_dir}/dependency/{model}` exists (re-scan at runtime, do not reuse the earlier list)
        - If it exists:
          > "[4/9] Model `{model}` was not found in `{madgraph_path}/models/`. The skill has this model in its dependency folder. Copy it to `{madgraph_path}/models/`? (Type `yes` to copy, or provide an alternative model name:)"
          > "在 `{madgraph_path}/models/` 中未找到模型 `{model}`。skill 依赖文件夹中有此模型。是否复制到 `{madgraph_path}/models/`？（输入 `yes` 复制，或提供其他模型名称：）"
        - If the user answers `yes`: copy `{skill_dir}/dependency/{model}` to `{madgraph_path}/models/{model}`
        - If the user provides a different model name: replace this model in the list and repeat the check
        - If the model is not in `dependency/` either: report "Model `{model}` not found in MG5 and not available in skill dependencies. Please provide a valid model name or install it manually."
   - Preserve the user-provided order — operators are claimed in this order during Phase 1
5. `[5/9] energy` —
   > "[5/9] What is the center-of-mass energy in TeV? Provide a single value or a list, e.g. `10` or `[10, 14, 30]`."
   > "质心能量是多少 TeV？提供单个值或列表，例如 `10` 或 `[10, 14, 30]`。"
6. `[6/9] luminosity` —
   > "[6/9] What is the integrated luminosity in fb⁻¹? Provide a single value or a list matching the energy length, e.g. `3000` or `[1000, 3000, 10000]`."
   > "积分亮度是多少 fb⁻¹？提供单个值或与能量长度匹配的列表，例如 `3000` 或 `[1000, 3000, 10000]`。"
7. `[7/9] cutexperiment_path` — If a default exists from context (e.g., previous conversation, `~/CutExperiment`), ask:
   > "[7/9] Do you already have CutExperiment installed? If so, provide the path. If not, type `clone` to clone from `https://gitee.com/NBAlexis/CutExperiment.git` into `{default_path}`."
   > "您是否已经安装了 CutExperiment？如果已安装请提供路径。如果未安装，输入 `clone` 从 `https://gitee.com/NBAlexis/CutExperiment.git` 克隆到 `{default_path}`。"
   If no default exists:
   > "[7/9] Do you already have CutExperiment installed? If so, provide the path. If not, type `clone` and I will clone it from `https://gitee.com/NBAlexis/CutExperiment.git`."
   > "您是否已经安装了 CutExperiment？如果已安装请提供路径。如果未安装，输入 `clone`，我将从 `https://gitee.com/NBAlexis/CutExperiment.git` 克隆。"
8. `[8/9] Delphes card selection` — After `madgraph_path`, `process`, and `energy` are known:
   - Run the auto-recommendation:
     1. Scan `{madgraph_path}/Delphes/cards/` for all `*.tcl` files
     2. **Filter out non-detector cards** — exclude `converter_card.tcl`, `gen_card.tcl`, `validation_card.tcl`, `delphes_card_llptest.tcl`, and any file whose name starts with `trackResolution`, `trkCounting`, or `gen_`
     3. Infer the collider type from the initial state of `process`
     4. Score each remaining card by matching its filename against the collider type
     5. Recommend the highest-scoring card
     6. Present to the user (only showing cards that scored > 0):
        > "[8/9] Scanning detector cards in `{mg5path}/Delphes/cards/`...\n> Based on your process (`{process}`) at `{energy}` TeV, the recommended Delphes card is: **{recommended_card}**\n> Other matching options: {matched_card_list}\n> Type `yes` to use the recommended card, type a different card name to override, or provide an absolute path to a custom `.tcl` card outside `{mg5path}/Delphes/cards/`."
        > "正在扫描 `{mg5path}/Delphes/cards/` 中的探测器卡片...\n> 根据您的过程（`{process}`）在 `{energy}` TeV 下，推荐的 Delphes 卡片是：**{recommended_card}**\n> 其他匹配选项：{matched_card_list}\n> 输入 `yes` 使用推荐的卡片，输入其他卡片名称覆盖，或提供自定义 `.tcl` 卡片的绝对路径（在 `{mg5path}/Delphes/cards/` 之外）。"
   - **If the user provides an absolute path** (starts with `/` or `~`): treat as `custom_card`. Validate the file exists and record the absolute path as `delphes_card`.
   - **If the user types a card name** (not an absolute path): validate it exists in `{mg5path}/Delphes/cards/` and use it as `delphes_card`.
   - **If the user types `yes`**: use the recommended card as `delphes_card`.
   - **If no cards match the collider type** (all scores = 0), show:
     > "[8/9] No detector cards match your collider type. Available cards: {all_filtered_cards}. Please specify one (card name or absolute path to custom card):"
     > "没有探测器卡片匹配您的对撞机类型。可用卡片：{all_filtered_cards}。请指定一个（卡片名称或自定义卡片的绝对路径）："

9. `[9/9]` — **After all required inputs are collected, also ask**:
   > "[9/9] Are there any other requirements or preferences? Optional settings you can specify:
   > - `debug=true` — divide all event counts by 10 for faster testing (default: false)
   > - `algorithms` — specify which ML algorithms to compare (default: automatically select and test multiple algorithms)
   > - `polarization` — beam polarization as `polbeam1,polbeam2` in range [-1, 1] (default: no polarization)
   > - `custom_card` — absolute path to a custom Delphes card outside `{mg5path}/Delphes/cards/`
   > - Specific operators to focus on, report format preferences, or additional analysis
   > Type `skip` to use all defaults, or specify any settings above."
   > "还有其他要求或偏好吗？可选设置：
   > - `debug=true` — 所有事件数除以 10 以加快测试（默认：false）
   > - `algorithms` — 指定要比较的 ML 算法（默认：自动选择并测试多种算法）
   > - `polarization` — 束流极化，格式为 `polbeam1,polbeam2`，范围 [-1, 1]（默认：无偏振）
   > - `custom_card` — 自定义 Delphes 卡片的绝对路径（在 `{mg5path}/Delphes/cards/` 之外）
   > - 要重点关注的特定算符、报告格式偏好或其他分析需求
   > 输入 `skip` 使用所有默认值，或指定上述任何设置。"

   This is **NOT optional** — it MUST be asked even if the user is in a hurry. The user can always type `skip` to accept defaults, but the question itself must be presented.

**Defaults:**
- `workdir`: the **Working Directory** (shell `pwd`) if user types `yes` or provides no answer
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

## Step 3: Wait for User Response

After asking for missing inputs, **STOP**. Do nothing else. Wait for the user to provide all requested information.

## Step 4: Validate Received Inputs

- `madgraph_path`: verify the directory exists and contains `bin/mg5_aMC`
- `workdir`: if provided, verify the directory exists (create automatically if missing); default to the Working Directory (shell `pwd`). **Verify `workdir` is NOT inside the Skill Directory** (where `SKILL.md` is located). If it is, use the Skill Directory's parent instead.
- `process`: verify it does not contain `NP=`, `QED=`, or `QCD=` suffixes (strip them if present)
- `model`: verify it is a non-empty string or a non-empty list of strings. If list, each element must be a valid model name.
- `energy`: must be a non-empty list; all values > 0
- `luminosity`: must be a non-empty list; all values > 0
- `ebeam_proton` (if process is ep collider): verify > 0
- `delphes_card`: verify the file exists (either under `{madgraph_path}/Delphes/cards/` or at the absolute path if custom)
- `polarization` (if provided): verify format is two comma-separated floats in [-1, 1]
- **List validation**: `energy` and `luminosity` MUST have the same length. If lengths differ, report the mismatch and ask the user to correct.
- **Non-empty validation**: `models`, `energy`, `luminosity`, and `run_configurations` must all be non-empty. Phase -1 must guarantee valid inputs before writing `run_config.json`; Phase 0 assumes these are already validated.

If validation fails, report the specific failure and re-ask for that input.

## Step 5: Confirm Phase -1 Completion

Before proceeding to Phase 0, confirm:
- [ ] All 5 required parameters were explicitly provided by the user **in this conversation**
- [ ] No parameter was sourced from files, code, logs, or historical context
- [ ] Input validation passed (Step 4)

**Phase -1 is complete ONLY when the user has explicitly confirmed or provided every parameter through dialogue.**

**After Step 5 passes, the interactive portion of the workflow is OVER. From this point forward, the workflow is FULLY AUTOMATED. Do NOT wait for user confirmation. Do NOT ask "是否继续？" / "Shall I proceed?". Immediately execute Phase 0, then sequentially execute Phases 1–9 without stopping.**

## Step 6: Write `run_config.json`

Write all collected and validated inputs to a single machine-readable configuration file:

```
{workdir}/results/run_config.json
```

This file is the **single source of truth** for all subsequent phases. No phase should reference Phase -1 directly; they must read this file.

### Schema

```json
{
  "version": "1.0",
  "collected_at": "2026-06-01T10:00:00",
  "madgraph_path": "/opt/MG5_aMC_v3_5_15",
  "workdir": "/home/user/work",
  "process": "e+ e- > a a",
  "models": ["AQGCm_UFO"],
  "energy": [10],
  "luminosity": [1000],
  "ebeam_proton": null,
  "delphes_card": "delphes_card_CEPC.tcl",
  "custom_card": null,
  "polarization": null,
  "debug": false,
  "algorithms": null,
  "cutexperiment_path": "./CutExperiment",
  "run_configurations": [
    {"energy": 10, "luminosity": 1000, "run_dir": "E10_L1000"}
  ],
  "auto_installed_mg5": false
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | string | yes | Schema version, currently `"1.0"` |
| `collected_at` | ISO8601 | yes | Timestamp when Phase -1 completed |
| `madgraph_path` | string | yes | Absolute path to MG5 installation |
| `workdir` | string | yes | Absolute path to working directory |
| `process` | string | yes | Physics process (no NP=/QED=/QCD= suffixes) |
| `models` | list[string] | yes | List of UFO model names |
| `energy` | list[float] | yes | Center-of-mass energy(s) in TeV |
| `luminosity` | list[float] | yes | Integrated luminosity(s) in fb⁻¹ |
| `ebeam_proton` | float \| null | no | Proton beam energy in GeV (ep colliders only) |
| `delphes_card` | string | yes | Selected Delphes `.tcl` card filename or absolute path |
| `custom_card` | string \| null | no | Absolute path to custom Delphes card (if provided) |
| `polarization` | [float, float] \| null | no | `polbeam1, polbeam2` in [-1, 1] |
| `debug` | bool | yes | `true` divides all event counts by 10 |
| `algorithms` | list[string] \| null | no | User-specified ML algorithm names |
| `cutexperiment_path` | string | no | Absolute path to CutExperiment (always set — either user-provided or auto-cloned) |
| `run_configurations` | list[dict] | yes | One entry per `(energy, luminosity)` pair |
| `auto_installed_mg5` | bool | yes | `true` if MG5 was auto-installed in this run |

### Loading the configuration

**Use the script** (do not reimplement):

```bash
python scripts/load_run_config.py results/run_config.json
```

Or import in Python:

```python
from scripts.load_run_config import load_run_config

config = load_run_config("results/run_config.json")
print(config.madgraph_path)
print(config.delphes_card)
# config.run_configurations[0].run_dir → "E10_L1000"
```

## Step 7: Build Run Configuration List

Convert inputs into a list of run configurations. Each configuration is one `(energy, luminosity)` pair.

| Input Pattern | Run Configurations |
|---------------|-------------------|
| Single energy, single luminosity | `[(energy, luminosity)]` — 1 run |
| List energy `[e1, e2, ...]`, list luminosity `[l1, l2, ...]` | `[(e1, l1), (e2, l2), ...]` — N runs |
| Single energy, list luminosity | **Invalid** — lengths must match |
| List energy, single luminosity | **Invalid** — lengths must match |

Example: `energy = [10, 14, 30]`, `luminosity = [1000, 3000, 10000]` → 3 runs: `(10, 1000)`, `(14, 3000)`, `(30, 10000)`

## Phase -1 Output Contract

After Phase -1 completes, the ONLY persistent artifacts needed by downstream phases are:

1. **`{workdir}/results/run_config.json`** — the single source of truth
2. **Models copied** to `{madgraph_path}/models/` (if applicable)
3. **CutExperiment cloned** to `cutexperiment_path` (if applicable)

**No phase after Phase -1 should:**
- Reference "Phase -1" as a data source
- Re-ask the user for any parameter already in `run_config.json`
- Infer parameters from conversation history

All configuration data flows through `run_config.json`.

## Prohibited Behaviors During Phase -1 (Will Cause Failure)

| Prohibited Behavior | Why |
|---------------------|-----|
| **Asking multiple parameters in one message** | **VIOLATION of Step 2.** One parameter per message, no tables, no "provide all above". |
| Inferring defaults from example1/example2/history | Each run is independent; historical parameters are NOT defaults |
| Using "start now" / "直接开始" as override | User urgency does NOT bypass input collection |
| Proceeding to Phase 0 with missing inputs | Phase -1 must be fully completed first |
| Creating directories before all inputs are validated | Directory creation is a Phase 0 action, not Phase -1 |
| **Stopping mid-execution to ask user whether to continue** | **ONCE STARTED, the workflow MUST run to completion automatically. Only stop on errors or red flags.** |
