# Phase 1: Input Collection

Phase 1 is a strict bilingual intake state machine. It collects all user-controlled inputs, validates them, writes `{workdir}/results/run_config.json`, and then hands control to Phase 2.

## Core Rule

Ask exactly the next question indicated by the intake cursor. After asking, stop and wait for the user's reply.

Do not ask future questions early. Do not skip a question. Do not summarize the full form. Do not proceed to Phase 2 until every field has been collected and validated.

## Restart Semantics

If the latest user message clearly requests a restart/retest/new study, including `restart`, `start over`, `rerun`, `重新开始`, `重新测试`, `重来`, or `换一个过程`, reset the intake cursor to `[1/9]`.

On restart:
- Discard all prior physics/run fields: `process`, `models`, `energy`, `luminosity`, `ebeam_proton`, `delphes_card`, `preferences`, `debug`, `algorithms`, `polarization`.
- Ignore old `run_config.json` values for physics/run fields.
- Keep known `madgraph_path` and `cutexperiment_path` only as suggested defaults.
- Still ask `[1/9]` and `[7/9]`; never silently accept remembered paths.

## Bilingual Question Format

Every intake question must be emitted exactly as:

```text
[N/9] English question...
中文问题……
```

Allowed exception: `[3a/9]` for `ebeam_proton` when the process is an electron-proton collider.

Rules:
- English first, Chinese on the next line.
- Include the progress marker.
- Do not merge languages into one line.
- Do not add any paragraph before or after the question.
- Do not use `AskQuestion`, `askquestion`, `AskUserQuestion`, multiple-choice UI widgets, radio buttons, or constrained-option tools. Ask using plain text only.

## Intake State

Maintain these fields during Phase 1:

```json
{
  "cursor": "1",
  "madgraph_path": null,
  "workdir": null,
  "process": null,
  "ebeam_proton": null,
  "models": null,
  "energy": null,
  "luminosity": null,
  "cutexperiment_path": null,
  "delphes_card": null,
  "debug": false,
  "algorithms": null,
  "polarization": null,
  "auto_installed_mg5": false
}
```

If a user provides several fields in one reply, extract only the field required by the current cursor. You may remember extra text as a candidate answer, but every later cursor must still be asked and explicitly answered when reached. Only `madgraph_path` and `cutexperiment_path` may use earlier/local knowledge as suggested defaults.

## Question Cursor

### [1/9] `madgraph_path`

before_ask:
- Determine whether a known MG5 installation path exists from local/default context.
- If a known path exists, show it only as a suggested default.
- Do not validate or accept it until the user types `yes`.

ask, with default:

```text
[1/9] What is the absolute path to your MadGraph5 installation? Suggested default: `{default_path}`. Type `yes` to use it, provide a different path, or type `install` to auto-install MadGraph5 with Pythia8, LHAPDF6, and Delphes.
请提供 MadGraph5 的绝对路径。建议默认：`{default_path}`。输入 `yes` 使用默认路径，输入其他路径，或输入 `install` 自动安装 MadGraph5、Pythia8、LHAPDF6 和 Delphes。
```

ask, without default:

```text
[1/9] What is the absolute path to your MadGraph5 installation? Provide the path, or type `install` to auto-install MadGraph5 with Pythia8, LHAPDF6, and Delphes.
请提供 MadGraph5 的绝对路径，或输入 `install` 自动安装 MadGraph5、Pythia8、LHAPDF6 和 Delphes。
```

handle:
- `yes`: valid only if a suggested default was shown; validate `{default_path}/bin/mg5_aMC` or `{default_path}/bin/mg5`.
- path: expand `~`, resolve absolute path, validate `bin/mg5_aMC` or `bin/mg5`.
- `install`: run the MG5 auto-install flow below.
- invalid: report the concrete failure and re-ask `[1/9]`.

MG5 auto-install flow:
1. Ask the install-directory subquestion using `[1/9]`:
   ```text
   [1/9] Where should MadGraph5 be installed? Suggested default: `~/MG5_aMC`. Type `yes` to use it, or provide a different directory.
   MadGraph5 应该安装到哪里？建议默认：`~/MG5_aMC`。输入 `yes` 使用默认目录，或提供其他目录。
   ```
2. Fetch `https://launchpad.net/mg5amcnlo` and dynamically identify the recommended LTS tarball URL and extracted directory name.
3. If parsing fails, ask the user to provide a direct MG5 tarball URL and expected extracted directory name.
4. Run `python scripts/install_mg5.py {install_dir} --url {download_url} --name {extracted_name}`.
5. If exit code `1`, show the missing system dependency command and wait for the user to reply `continue`; then retry.
6. If exit code `2`, retry download up to three times with exponential backoff.
7. If exit code `3` or `4`, report the specific log/component and abort Phase 1.
8. Store the printed `MadGraph5 path:` as `madgraph_path` and set `auto_installed_mg5=true`.

### [2/9] `workdir`

before_ask:
- Suggested default is the shell working directory where the user started the workflow.

ask:

```text
[2/9] Where should results be saved? Suggested default: the current working directory. Type `yes` to use it, or provide a different path.
结果保存到哪里？建议默认：当前工作目录。输入 `yes` 使用默认目录，或提供其他路径。
```

handle:
- `yes` or blank: use current working directory.
- path: expand and resolve absolute path.
- If the path is inside the skill directory, use the skill directory's parent instead and tell the user in one sentence.
- Create the directory if needed after validation.

### [3/9] `process`

ask:

```text
[3/9] What collider process should be studied? Provide the physics process only, without `NP=`, `QED=`, or `QCD=` suffixes.
要研究哪个对撞过程？只提供物理过程，不要包含 `NP=`、`QED=` 或 `QCD=` 后缀。
```

handle:
- Strip any `NP=`, `QED=`, or `QCD=` suffix and store the cleaned process.
- Inspect the initial state, i.e. particles left of `>`.
- If the initial state is `e- p`, `e+ p`, `e- p~`, or `e+ p~`, ask `[3a/9]`.

### [3a/9] `ebeam_proton` only for ep colliders

ask:

```text
[3a/9] Your process is an electron-proton collider process. What is the proton beam energy in GeV?
您的过程是电子-质子对撞过程。质子束流能量是多少 GeV？
```

handle:
- Validate positive float.
- Continue to `[4/9]`.

### [4/9] `models`

before_ask:
- Determine `skill_dir` as the directory containing `SKILL.md`.
- Scan `{skill_dir}/dependency/` for subdirectories; this is `dependency_models`.
- If `madgraph_path` is valid, scan `{madgraph_path}/models/` for installed model names when feasible.
- Present bundled models in the question; do not hardcode the list.

ask:

```text
[4/9] What SMEFT model name(s) should be used? Provide one model or a list, for example `AQGCm_UFO` or `[AQGCm_UFO, AQGCs_UFO]`. Bundled models found in the skill dependency folder: {dependency_models}. You may also use models already installed in `{madgraph_path}/models/`.
使用哪些 SMEFT 模型？提供一个模型或列表，例如 `AQGCm_UFO` 或 `[AQGCm_UFO, AQGCs_UFO]`。在 skill 依赖目录中找到的内置模型：{dependency_models}。也可以使用已经安装在 `{madgraph_path}/models/` 中的模型。
```

handle:
- Parse a single model, comma-separated models, or bracketed list into `models`.
- Do not accept `all`; the user must explicitly list models.
- Preserve user order.
- For each model, validate `{madgraph_path}/models/{model}` or `{skill_dir}/dependency/{model}`.
- If found only in dependency, ask the copy subquestion:
  ```text
  [4/9] Model `{model}` was not found in `{madgraph_path}/models/`, but it exists in the skill dependency folder. Type `yes` to copy it into MadGraph5, or provide a replacement model name.
  在 `{madgraph_path}/models/` 中没有找到模型 `{model}`，但 skill 依赖目录中存在该模型。输入 `yes` 将它复制到 MadGraph5，或提供替代模型名称。
  ```
- If the model is missing everywhere, report that and re-ask `[4/9]`.

### [5/9] `energy`

ask:

```text
[5/9] What is the center-of-mass energy in TeV? Provide a single value or a list, for example `10` or `[10, 14, 30]`.
质心能量是多少 TeV？提供单个值或列表，例如 `10` 或 `[10, 14, 30]`。
```

handle:
- Parse into a non-empty list of positive floats.

### [6/9] `luminosity`

ask:

```text
[6/9] What is the integrated luminosity in fb^-1? Provide a single value or a list matching the energy length, for example `3000` or `[1000, 3000, 10000]`.
积分亮度是多少 fb^-1？提供单个值或与能量列表长度匹配的列表，例如 `3000` 或 `[1000, 3000, 10000]`。
```

handle:
- Parse into a non-empty list of positive floats.
- If `energy` and `luminosity` lengths differ, report the mismatch and re-ask `[6/9]`.

### [7/9] `cutexperiment_path`

before_ask:
- Determine whether a known CutExperiment path exists from local/default context.
- If known, show it only as a suggested default.
- Do not accept it unless the user types `yes`.

ask, with default:

```text
[7/9] Do you already have CutExperiment installed? Suggested default: `{default_path}`. Type `yes` to use it, provide a different path, or type `clone` to clone it from `https://gitee.com/NBAlexis/CutExperiment.git`.
您是否已经安装 CutExperiment？建议默认：`{default_path}`。输入 `yes` 使用默认路径，输入其他路径，或输入 `clone` 从 `https://gitee.com/NBAlexis/CutExperiment.git` 克隆。
```

ask, without default:

```text
[7/9] Do you already have CutExperiment installed? Provide the path, or type `clone` to clone it from `https://gitee.com/NBAlexis/CutExperiment.git`.
您是否已经安装 CutExperiment？请提供路径，或输入 `clone` 从 `https://gitee.com/NBAlexis/CutExperiment.git` 克隆。
```

handle:
- `yes`: valid only if a suggested default was shown; validate the path.
- path: expand and validate directory exists.
- `clone`: run `python scripts/install_cutexperiment.py {workdir}/CutExperiment`; store the returned path.
- invalid: report the failure and re-ask `[7/9]`.

### [8/9] `delphes_card`

before_ask:
- Scan `{madgraph_path}/Delphes/cards/` for detector cards.
- Include `.tcl` and `.dat` files.
- Exclude `converter_card.*`, `gen_card.*`, `validation_card.*`, `delphes_card_llptest.*`, and files starting with `trackResolution`, `trkCounting`, or `gen_`.
- Infer collider type from `process`: `ee`, `pp`, `mumu`, or `ep`.
- Score card filenames by collider keywords:
  - `ee`: `CEPC`, `CLIC`, `Circular`, `ILC`
  - `pp`: `CMS`, `ATLAS`, `LHC`
  - `mumu`: `Muon`
  - `ep`: `FCCeh`, `LHeC`
- Recommend the highest-scoring card. If all scores are zero, show all filtered cards and ask the user to choose.

ask, with recommendation:

```text
[8/9] Scanning detector cards in `{madgraph_path}/Delphes/cards/` found this recommendation for `{process}` at `{energy}` TeV: `{recommended_card}`. Other matching cards: {matched_cards}. Type `yes` to use the recommendation, provide another card name, or provide an absolute path to a custom card.
在 `{madgraph_path}/Delphes/cards/` 中扫描探测器卡片后，针对 `{process}`、`{energy}` TeV 的推荐卡片是：`{recommended_card}`。其他匹配卡片：{matched_cards}。输入 `yes` 使用推荐卡片，提供其他卡片名，或提供自定义卡片的绝对路径。
```

ask, no recommendation:

```text
[8/9] No detector card clearly matches the collider type. Available detector cards: {filtered_cards}. Please provide a card name or an absolute path to a custom card.
没有探测器卡片能明确匹配该对撞机类型。可用探测器卡片：{filtered_cards}。请提供卡片名或自定义卡片的绝对路径。
```

handle:
- `yes`: use `recommended_card`.
- card name: validate under `{madgraph_path}/Delphes/cards/`.
- absolute path: validate it and store the absolute path directly as `delphes_card`.
- invalid: report and re-ask `[8/9]`.

### [9/9] `preferences`

This question is a preferences gateway, not a single scalar parameter. It exists so the user can personalize the run before execution. Do not mention Delphes card here because it was already selected in `[8/9]`.

ask:

```text
[9/9] Are there any other requirements or preferences? You may specify `debug=true`, `polarization=polbeam1,polbeam2`, `algorithms=[...]`, focused operators, report format preferences, or additional analysis notes. Type `skip` to use defaults.
还有其他要求或偏好吗？可以指定 `debug=true`、`polarization=polbeam1,polbeam2`、`algorithms=[...]`、重点关注的算符、报告格式偏好或其他分析说明。输入 `skip` 使用默认设置。
```

handle:
- `skip`: keep defaults.
- `debug=true`: use debug event counts.
- `polarization=a,b`: validate two floats in [-1, 1].
- `algorithms=[...]`: store requested algorithm names.
- Store other notes as `analysis_notes`.

## Final Validation

Before writing `run_config.json`, validate:
- `madgraph_path` contains `bin/mg5_aMC` or `bin/mg5`.
- `workdir` is absolute and not inside the skill directory.
- `process` is non-empty and contains no `NP=`, `QED=`, or `QCD=` suffix.
- `models`, `energy`, `luminosity`, and `run_configurations` are non-empty.
- `len(energy) == len(luminosity)`.
- `delphes_card` exists either under `{madgraph_path}/Delphes/cards/` or as an absolute path.
- `cutexperiment_path` exists.
- `ebeam_proton` is present for ep colliders.

If validation fails, re-ask the field responsible for the failure.

## Run Configuration

Write `{workdir}/results/run_config.json` with this schema:

```json
{
  "version": "1.0",
  "collected_at": "2026-06-01T10:00:00Z",
  "madgraph_path": "/opt/MG5_aMC_v3_5_15",
  "workdir": "/home/user/study",
  "process": "e+ e- > a a",
  "models": ["AQGCm_UFO"],
  "energy": [10.0],
  "luminosity": [1000.0],
  "ebeam_proton": null,
  "delphes_card": "delphes_card_CEPC.tcl",
  "cutexperiment_path": "/home/user/study/CutExperiment",
  "debug": false,
  "algorithms": null,
  "polarization": null,
  "analysis_notes": null,
  "auto_installed_mg5": false,
  "event_counts_locked": true,
  "locked_event_counts": {
    "nev_phase3": 10000,
    "nev_phase4": 10000,
    "nev_sm": 500000,
    "nev_np": 100000,
    "nev_scan": 1000000
  },
  "run_configurations": [
    {"energy": 10.0, "luminosity": 1000.0, "run_dir": "E10_L1000"}
  ]
}
```

Run directory naming:
- `run_dir = "E{energy}_L{luminosity}"`
- Replace decimal points with underscores.
- Example: `13.6, 3000` -> `E13_6_L3000`.

After writing `run_config.json`, verify it is valid JSON and proceed immediately to Phase 2. Do not ask for confirmation.
