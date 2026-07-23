# Phase 1: Input Collection

Phase 1 is a strict bilingual intake state machine. It collects all user-controlled inputs, validates them, writes `run_config.json`, and then hands control to Phase 2.

In local mode, `{workdir}/results/run_config.json` is both the control config and the workflow config. In SSH/WSL2 mode, write the same JSON to both:
- a local control copy readable by the agent for `scripts/remote_exec.py --config ...`;
- the target copy at `{workdir}/results/run_config.json` on the SSH/WSL2 target.

Native Windows is not a valid local execution target for this workflow. If the agent is running on Windows, Phase 1 must use `wsl2` or `ssh`.

## Core Rule

Ask exactly the next question indicated by the intake cursor. After asking, stop and wait for the user's reply.

Do not ask future questions early. Do not skip a question. Do not summarize the full form. Do not proceed to Phase 2 until every field has been collected and validated.

## Restart Semantics

If the latest user message clearly requests a restart/retest/new study, including `restart`, `start over`, `rerun`, `重新开始`, `重新测试`, `重来`, or `换一个过程`, reset the intake cursor to `[1/9]`.

On restart:
- Discard all prior target/physics/run fields: `execution`, `process`, `collider_type`, `models`, `energy`, `luminosity`, `ebeam_electron`, `ebeam_proton`, `delphes_card`, `debug`, `algorithms`, `polarization`, `analysis_notes`.
- Ignore old `run_config.json` values for target/physics/run fields.
- Keep known `madgraph_path` and `cutexperiment_path` only as suggested defaults.
- Still ask `[1/9]` and `[7/9]`; never silently accept remembered paths.

## Bilingual Question Format

Every intake question must be emitted exactly as:

```text
[N/9] English question...
中文问题...
```

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
  "execution": {"mode": null},
  "madgraph_path": null,
  "workdir": null,
  "process": null,
  "collider_type": null,
  "process_validation": null,
  "madspin": {"enabled": false},
  "ebeam_electron": null,
  "ebeam_proton": null,
  "models": null,
  "energy": null,
  "luminosity": null,
  "cutexperiment_path": null,
  "delphes_card": null,
  "debug": false,
  "algorithms": null,
  "polarization": null,
  "analysis_notes": {
    "focused_operators": [],
    "manuscript_preferences": [],
    "additional_requirements": []
  },
  "auto_installed_mg5": false
}
```

If a user provides several fields in one reply, extract only the field required by the current cursor. You may remember extra text as a candidate answer, but every later cursor must still be asked and explicitly answered when reached. Only `madgraph_path` and `cutexperiment_path` may use earlier/local knowledge as suggested defaults.

## Question Cursor

### [1/9] `execution` and `madgraph_path`

This cursor determines both where commands run and where MadGraph5 lives. Keep the main question count at 9; use subquestions only when the user selects SSH or WSL2 but omits required target details.

before_ask:
- Determine whether a known MG5 installation path exists from local/default context.
- If a known path exists, show it only as a suggested default.
- If the agent is running on native Windows, do not offer a bare local path as an accepted answer. Offer `wsl2:/path/to/MG5`, the WSL2 discovery subflow, SSH, or install on WSL2/SSH.
- If WSL2 is installed on Windows and no MG5 default is known, mention the `wsl2:/path/to/MG5` form.
- Do not validate or accept a default until the user types `yes`.

ask, with default:

```text
[1/9] Where should MadGraph5 run, and what is its absolute path? Suggested default: `{default_path}`. Type `yes` to use it, provide a Linux local path, provide `ssh user@host:/absolute/MG5/path`, provide `wsl2:/absolute/MG5/path`, or type `install`.
MadGraph5 应该在哪里运行，它的绝对路径是什么？建议默认值：`{default_path}`。输入 `yes` 使用默认值，提供 Linux 本地路径，提供 `ssh user@host:/absolute/MG5/path`，提供 `wsl2:/absolute/MG5/path`，或输入 `install`。
```

ask, without default:

```text
[1/9] Where should MadGraph5 run, and what is its absolute path? Provide a Linux local path, `ssh user@host:/absolute/MG5/path`, `wsl2:/absolute/MG5/path`, `wsl2` to use a WSL2 subquestion, or `install`.
MadGraph5 应该在哪里运行，它的绝对路径是什么？请提供 Linux 本地路径、`ssh user@host:/absolute/MG5/path`、`wsl2:/absolute/MG5/path`，输入 `wsl2` 进入 WSL2 子问题，或输入 `install`。
```

handle:
- `yes`: valid only if a suggested default was shown; validate `{default_path}/bin/mg5_aMC` or `{default_path}/bin/mg5` on the selected target.
- Linux local path: set `execution={"mode":"local"}`, expand `~`, resolve absolute path, validate `bin/mg5_aMC` or `bin/mg5`. Reject Windows paths such as `C:\...` or `E:\...` and re-ask for WSL2/SSH.
- `ssh user@host:/absolute/MG5/path`: set `execution={"mode":"ssh","ssh_target":"user@host"}` and `madgraph_path="/absolute/MG5/path"`. Validate with `scripts/remote_exec.py --mode ssh --ssh-target user@host -- test -x /absolute/MG5/path/bin/mg5_aMC -o -x /absolute/MG5/path/bin/mg5`.
- `wsl2:/absolute/MG5/path`: set `execution={"mode":"wsl2"}` and `madgraph_path="/absolute/MG5/path"`. Validate with `scripts/remote_exec.py --mode wsl2 -- test -x /absolute/MG5/path/bin/mg5_aMC -o -x /absolute/MG5/path/bin/mg5`.
- `wsl2`: run the WSL2 discovery subflow below.
- WSL2/Git Bash caution: Git Bash on Windows may rewrite Linux paths such as `/home/...` or `/opt/...`; validate and run WSL2 target commands through `scripts/remote_exec.py`, not ad-hoc `wsl` shell snippets.
- Regardless of how `madgraph_path` is obtained, Phase 1 must verify the full MG5 stack before accepting it: `bin/mg5_aMC` or `bin/mg5`, `HEPTools/pythia8/`, `HEPTools/lhapdf6_py3/`, and `Delphes/cards/` on the selected target. If any piece is missing, treat the installation as incomplete and re-ask or reinstall.
- `install`: run the MG5 auto-install flow below on the selected target. If no target was selected and the agent is on Windows, first ask the WSL2 discovery subflow or ask for SSH target details; otherwise default to local Linux mode.
- invalid: report the concrete failure and re-ask `[1/9]`.

WSL2 discovery subflow:
1. Run `wsl.exe -l -q` when available.
2. If one distro is listed, set `execution={"mode":"wsl2","wsl_distro":"<name>"}` and ask:
   ```text
   [1/9] WSL2 distro `{distro}` was found. What is the absolute MadGraph5 path inside WSL2, or type `install`?
   已找到 WSL2 发行版 `{distro}`。请提供 WSL2 内部的 MadGraph5 绝对路径，或输入 `install`。
   ```
3. If multiple distros are listed, ask the user to provide `distro:/absolute/MG5/path` or `distro install`.
4. Do not require the user to know an SSH target for WSL2. Prefer `execution.mode="wsl2"` over SSH for WSL2 unless the user explicitly provides an SSH target.

WSL2 SSH target analysis:
- If the user explicitly wants SSH into WSL2, the target is usually `{wsl_user}@localhost` plus an SSH port exposed by WSL2.
- Port 22 may conflict with Windows OpenSSH. If WSL2 sshd is configured on another port, store it as `execution.ssh_port`, e.g. `{"mode":"ssh","ssh_target":"alice@localhost","ssh_port":2222}`.
- `ssh {wsl_user}@{wsl_ip}` can work, where `{wsl_ip}` comes from `hostname -I` inside WSL2, but WSL2 IPs change after restart. Prefer `wsl2` mode or `localhost` with a stable forwarded port.

MG5 auto-install flow:
1. Ask the install-directory subquestion using `[1/9]`; the directory must be on the selected execution target.
2. Fetch `https://launchpad.net/mg5amcnlo` and dynamically identify the recommended LTS tarball URL and extracted directory name.
3. If parsing fails, ask the user to provide a direct MG5 tarball URL and expected extracted directory name.
4. Run `python scripts/install_mg5.py {install_dir} --url {download_url} --name {extracted_name}` through the selected execution target.
5. If exit code `1`, show the missing system dependency command and wait for the user to reply `continue`; then retry.
6. If exit code `2`, retry download up to three times with exponential backoff.
7. If exit code `3` or `4`, inspect the specific log/component, repair the
   installer or use an equivalent installation path, and rerun the full stack
   validation. Re-ask for a different target only when the current target is
   proven unable to host the required stack.
8. Store the printed `MadGraph5 path:` as `madgraph_path` and set `auto_installed_mg5=true`.

### [2/9] `workdir`

before_ask:
- In local Linux mode, suggested default is the shell working directory where the user started the workflow.
- In SSH mode, `workdir` must be an absolute directory on the SSH host.
- In WSL2 mode, `workdir` must be an absolute Linux path inside WSL2.

ask:

```text
[2/9] Where should results be saved on the selected execution target? Suggested default: the current target working directory. Type `yes` to use it, or provide a different absolute path.
结果应该保存到所选执行目标的哪里？建议默认值：当前目标工作目录。输入 `yes` 使用默认目录，或提供其他绝对路径。
```

handle:
- `yes` or blank: use current target working directory.
- local path: expand and resolve absolute path. Reject Windows paths if the selected target is WSL2/SSH.
- SSH/WSL2 path: require an absolute Linux path and validate/create it on the target with `scripts/remote_exec.py`.
- If local `workdir` is inside the skill directory, use the skill directory's parent instead and tell the user in one sentence.
- Create the directory if needed after validation on the selected target.

### [3/9] `process`

```text
[3/9] What collider process should be studied? Provide one physics process, or a bracketed list such as `[mu+ mu- > l+ vl j j, mu+ mu- > l- vl~ j j]`. Do not add quotes and do not include `NP=`, `QED=`, or `QCD=` suffixes.
要研究哪个对撞过程？请提供一个物理过程，或一个方括号列表，例如 `[mu+ mu- > l+ vl j j, mu+ mu- > l- vl~ j j]`。不要加引号，也不要包含 `NP=`、`QED=` 或 `QCD=` 后缀。
```

handle:
- Parse either one process string or a bracketed process list into `process`.
  For a list, split on commas at the top level and preserve user order; do not
  require or insert quotes around process strings.
- Strip any `NP=`, `QED=`, or `QCD=` suffix from every process and store the
  cleaned string or cleaned list.
- The LLM must judge whether the initial and final particles are valid
  **asymptotic states** for this Delphes/LHCO/CutExperiment workflow. Do not
  call a hard-coded script for this judgment.
- Do not accept explicit quarks or gluons such as `g`, `u`, `d`, `s`, `c`,
  `b` directly in initial or final states: use `p` for hadronic beams and `j`
  for final-state jets. Do not accept initial-state `w+`, `w-`, or `z`.
- If every remaining non-asymptotic object is a final-state `t`, `t~`, `w+`,
  `w-`, or `z`, accept the process, set `madspin.enabled=true`, record the
  reason in `process_validation`, and continue. Add one short bilingual
  warning before the next intake question:
  ```text
  Warning: final-state t/t~/w+/w-/z are not asymptotic states for this workflow and must decay before analysis, so MadSpin will be enabled automatically.
  警告：末态 t/t~/w+/w-/z 不是本 workflow 的渐进态，需要在分析前继续衰变，因此将自动开启 MadSpin。
  ```
- Otherwise, if any non-asymptotic object remains, do not accept the process.
  Ask the user to re-enter `[3/9]` with this exact bilingual warning:
  ```text
  [3/9] The process `{process}` contains states this Delphes/LHCO workflow cannot directly analyze. Use `p` for hadronic initial states and `j` for final-state jets. Only final-state `t`, `t~`, `w+`, `w-`, `z` can be accepted automatically with MadSpin. Please provide a corrected physics process.
  [3/9] 过程 `{process}` 含有本 Delphes/LHCO workflow 不能直接分析的对象。强子初态请用 `p`，末态喷注请用 `j`。只有末态 `t`、`t~`、`w+`、`w-`、`z` 可以通过自动开启 MadSpin 接受。请重新提供修正后的物理过程。
  ```
- For custom UFO labels or ambiguous multiparticle labels, be conservative:
  accept only if the label is clearly an asymptotic state that CutExperiment
  and the selected Delphes card can analyze. Otherwise re-ask `[3/9]`.
- Inspect the initial state of every process, i.e. particles left of `>`.
- If any initial state is `e- p`, `e+ p`, `e- p~`, or `e+ p~`, set
  `collider_type="ep"` and continue to `[4/9]`. Do not ask a subquestion.
- Otherwise infer `collider_type` as `ee`, `pp`, or `mumu`.

### [4/9] `models`

before_ask:
- Determine `skill_dir` as the directory containing `SKILL.md`.
- Scan `{skill_dir}/dependency/` at the time the question is asked. Treat every
  immediate child directory as one available bundled model, including
  user-added directories. Sort names case-insensitively for display.
- If `madgraph_path` is valid, scan `{madgraph_path}/models/` on the selected target when feasible.
- Present every bundled model directory name in the question. Never abbreviate
  with `...`, `etc.`, "and more", or a partial list.
- Do not use a model list copied from this document or a previous run. If the
  directory is empty, say explicitly that no bundled models were found.

```text
[4/9] What SMEFT model name(s) should be used? Provide one model or a list, for example `AQGCm_UFO` or `[AQGCm_UFO, AQGCs_UFO]`. Bundled models found in the skill dependency folder: {dependency_models}. You may also use models already installed in `{madgraph_path}/models/`.
要使用哪些 SMEFT 模型？请提供一个模型或一个列表，例如 `AQGCm_UFO` 或 `[AQGCm_UFO, AQGCs_UFO]`。skill 依赖目录中发现的内置模型：{dependency_models}。也可以使用已经安装在 `{madgraph_path}/models/` 中的模型。
```

handle:
- Parse a single model, comma-separated models, or bracketed list into `models`.
- Do not accept `all`; the user must explicitly list models.
- Preserve user order.
- For each model, validate `{madgraph_path}/models/{model}` on the target or `{skill_dir}/dependency/{model}` locally.
- If found only in dependency, ask whether to copy it into MadGraph5. Use `scripts/sync_to_target.py` for SSH/WSL2 targets.
- If the model is missing everywhere, report that and re-ask `[4/9]`.

### [5/9] beam energies

For non-ep colliders:

```text
[5/9] What is the center-of-mass energy in TeV? Provide a single value or a list, for example `10` or `[10, 14, 30]`.
质心能量是多少 TeV？请提供单个值或列表，例如 `10` 或 `[10, 14, 30]`。
```

For ep colliders:

```text
[5/9] What are the electron and proton beam energies in GeV? Provide one pair `Ee, Ep` or a list of pairs, for example `60, 7000` or `[(60, 7000), (140, 7000)]`.
电子束流和质子束流能量分别是多少 GeV？请提供一组 `Ee, Ep` 或多组列表，例如 `60, 7000` 或 `[(60, 7000), (140, 7000)]`。
```

Handle:
- For non-ep colliders, parse the user-provided center-of-mass energies into
  `energy`, a non-empty list of positive TeV values. For each value, compute
  `ebeam1 = ebeam2 = energy * 1000 / 2`, where `1000` is the TeV-to-GeV
  conversion. Store the beam energies in `run_configurations`; set
  `ebeam_electron=null` and `ebeam_proton=null`. Event generation uses only
  the stored `ebeam1`/`ebeam2`; `energy` is metadata for labels and the
  manuscript.
- For ep colliders, parse into equal-length positive GeV lists
  `ebeam_electron` and `ebeam_proton`. Store them directly as
  `run_configurations[*].ebeam1` and `run_configurations[*].ebeam2`.
  Do not derive or store `sqrt(s)` during Phase 1; Phase 10 uses
  `scripts/beam_energy.py` for manuscript-only display metadata.

### [6/9] `luminosity`

```text
[6/9] What is the integrated luminosity in fb^-1? Provide a single value or a list matching the number of energy points or ep beam-energy pairs, for example `3000` or `[1000, 3000, 10000]`.
积分亮度是多少 fb^-1？请提供单个值，或与能量点/ep 束流能量组合数量匹配的列表，例如 `3000` 或 `[1000, 3000, 10000]`。
```

Parse into a non-empty list of positive floats. For non-ep colliders,
`luminosity` length must match `energy` length. For ep colliders, `luminosity`
length must match the number of `(ebeam_electron, ebeam_proton)` pairs. After
luminosity is known, create one `run_configurations` entry per run with
positive `ebeam1`, `ebeam2`, `luminosity`, and `run_dir`. If lengths differ,
report the mismatch and re-ask `[6/9]`.

### [7/9] `cutexperiment_path`

before_ask:
- Determine whether a known CutExperiment path exists from local/default context.
- If known, show it only as a suggested default.
- Do not accept it unless the user types `yes`.

```text
[7/9] Do you already have CutExperiment installed on the selected execution target? Suggested default: `{default_path}`. Type `yes` to use it, provide a different path, or type `clone` to clone it from `https://gitee.com/NBAlexis/CutExperiment.git`.
所选执行目标上是否已经安装 CutExperiment？建议默认值：`{default_path}`。输入 `yes` 使用默认路径，提供其他路径，或输入 `clone` 从 `https://gitee.com/NBAlexis/CutExperiment.git` 克隆。
```

handle:
- `yes`: valid only if a suggested default was shown; validate the path.
- path: expand and validate directory exists on the selected execution target.
- `clone`: run `python scripts/install_cutexperiment.py {workdir}/CutExperiment` on the selected execution target; store the returned path.
- invalid: report the failure and re-ask `[7/9]`.

### [8/9] `delphes_card`

before_ask:
- Scan `{madgraph_path}/Delphes/cards/` on the selected execution target.
- Include `.tcl` and `.dat` files.
- Exclude `converter_card.*`, `gen_card.*`, `validation_card.*`, `delphes_card_llptest.*`, and files starting with `trackResolution`, `trkCounting`, or `gen_`.
- Infer collider type from `process`: `ee`, `pp`, `mumu`, or `ep`.
- Score card filenames by collider keywords: `ee`: `CEPC`, `CLIC`, `Circular`, `ILC`; `pp`: `CMS`, `ATLAS`, `LHC`; `mumu`: `Muon`; `ep`: `FCCeh`, `LHeC`.

```text
[8/9] Scanning detector cards in `{madgraph_path}/Delphes/cards/` found this recommendation for `{process}` with `{beam_summary}`: `{recommended_card}`. Other matching cards: {matched_cards}. Type `yes` to use the recommendation, provide another card name, or provide an absolute path to a custom card.
扫描 `{madgraph_path}/Delphes/cards/` 中的探测器卡片后，针对 `{process}` 和 `{beam_summary}` 的推荐卡片是：`{recommended_card}`。其他匹配卡片：{matched_cards}。输入 `yes` 使用推荐卡片，提供其他卡片名，或提供自定义卡片的绝对路径。
```

handle:
- `yes`: use `recommended_card`.
- card name: validate under `{madgraph_path}/Delphes/cards/`.
- absolute path: validate it on the selected execution target and store the absolute path directly as `delphes_card`.
- invalid: report and re-ask `[8/9]`.

### [9/9] `analysis_notes` and optional preferences

This question is a preferences gateway. It exists so the user can personalize the run before execution. Do not mention Delphes card here because it was already selected in `[8/9]`.

```text
[9/9] Are there any other requirements or preferences? You may specify `debug=true`, `polarization=polbeam1,polbeam2`, `algorithms=[...]`, focused operators, manuscript format preferences, or additional analysis notes. Type `skip` to use defaults.
还有其他要求或偏好吗？可以指定 `debug=true`、`polarization=polbeam1,polbeam2`、`algorithms=[...]`、重点关注的算符、报告格式偏好或其他分析说明。输入 `skip` 使用默认设置。
```

handle:
- `skip`: keep defaults.
- `debug=true`: select the reduced event counts defined in `SKILL.md` to test the
  complete workflow. Preserve all fixed analysis methods and deliverable paths,
  but do not present the resulting numbers as a strict scientific study.
- `polarization=a,b`: validate two floats in [-1, 1] and store
  `{"polbeam1": a, "polbeam2": b}`. Do not store a list or comma-separated
  string.
- `algorithms=[...]`: store requested algorithm names.
- Store other input as the exact object
  `analysis_notes={"focused_operators": [...], "manuscript_preferences": [...],
  "additional_requirements": [...]}`. Each additional requirement is
  `{"id": "requirement_N", "text": "...", "applies_to_phases": ["..."]}`.
  Ask a follow-up during Phase 1 if the applicable phases cannot be determined.
  `skip` stores three empty lists.

## Final Validation

Before writing `run_config.json`, satisfy
[`deliverables-phase1.md`](deliverables-phase1.md). If any required field is
missing or invalid, re-ask the responsible bilingual intake question.

Before writing `run_config.json`, validate:
- `execution.mode` is `local`, `ssh`, or `wsl2`.
- If the agent is running on native Windows, `execution.mode` is `ssh` or `wsl2`.
- `execution.ssh_target` is present for SSH mode.
- `madgraph_path` contains `bin/mg5_aMC` or `bin/mg5` on the selected execution target.
- `madgraph_path` also contains `HEPTools/pythia8/`, `HEPTools/lhapdf6_py3/`,
  and `Delphes/cards/` on the selected execution target.
- `workdir` is absolute on the selected execution target and not inside the skill directory in local mode.
- `process` is a non-empty string or non-empty list of strings. No process
  entry contains an `NP=`, `QED=`, or `QCD=` suffix.
- `process_validation` records the LLM asymptotic-state judgment. If accepted
  final-state `t`, `t~`, `w+`, `w-`, or `z` appear as non-asymptotic objects,
  `madspin.enabled` must be true.
- `models`, `luminosity`, and `run_configurations` are non-empty.
- For non-ep colliders, `energy` is a non-empty list of positive TeV values and
  `len(energy) == len(luminosity)`.
- For ep colliders, `energy` is null, `ebeam_electron` and `ebeam_proton` are
  positive GeV lists with the same length as `luminosity`, and every
  `run_configurations` entry has `ebeam1=ebeam_electron[i]` and
  `ebeam2=ebeam_proton[i]`.
- `delphes_card` exists either under `{madgraph_path}/Delphes/cards/` or as an absolute path on the selected execution target.
- `cutexperiment_path` exists on the selected execution target.
- `polarization` is `null` or exactly
  `{"polbeam1": number_in_[-1,1], "polbeam2": number_in_[-1,1]}`.
- `analysis_notes` has exactly the three list fields defined in `[9/9]`; every
  additional requirement has a unique `id`, non-empty `text`, and non-empty
  `applies_to_phases` list.

If validation fails, re-ask the field responsible for the failure.

## Run Configuration

Write `run_config.json` with this schema. `process` may be a string or a list
of process strings. In SSH/WSL2 mode, write both the local control copy and the
target copy at `{workdir}/results/run_config.json`.

```json
{
  "version": "1.0",
  "collected_at": "2026-06-01T10:00:00Z",
  "execution": {
    "mode": "wsl2",
    "ssh_target": null,
    "ssh_port": null,
    "wsl_distro": null
  },
  "madgraph_path": "/opt/MG5_aMC_v3_5_15",
  "workdir": "/home/user/study",
  "process": "e+ e- > a a",
  "collider_type": "ee",
  "process_validation": {
    "status": "ok",
    "initial": ["e+", "e-"],
    "final": ["a", "a"]
  },
  "madspin": {"enabled": false},
  "models": ["AQGCm_UFO"],
  "energy": [10.0],
  "luminosity": [1000.0],
  "ebeam_electron": null,
  "ebeam_proton": null,
  "delphes_card": "delphes_card_CEPC.tcl",
  "cutexperiment_path": "/home/user/study/CutExperiment",
  "debug": false,
  "algorithms": null,
  "polarization": null,
  "analysis_notes": {
    "focused_operators": [],
    "manuscript_preferences": [],
    "additional_requirements": []
  },
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
    {
      "energy": 10.0,
      "luminosity": 1000.0,
      "ebeam1": 5000.0,
      "ebeam2": 5000.0,
      "run_dir": "E10_L1000"
    }
  ]
}
```

This example is for `debug=false`. For `debug=true`, write the five reduced
values from the `SKILL.md` Locked Runtime Contract instead; do not copy the
formal counts from this example.

Every `run_configurations` entry must include explicit MG5 beam energies in GeV.
For ep colliders, `energy` remains null because `sqrt(s)` is not used for
event generation and is produced only by `scripts/beam_energy.py` in Phase 10:

```json
{
  "collider_type": "ep",
  "energy": null,
  "ebeam_electron": [60.0],
  "ebeam_proton": [7000.0],
  "run_configurations": [
    {
      "luminosity": 1000.0,
      "ebeam1": 60.0,
      "ebeam2": 7000.0,
      "run_dir": "Ee60_Ep7000_L1000"
    }
  ]
}
```

Run directory naming:
- Non-ep: `run_dir = "E{energy}_L{luminosity}"`
- ep: `run_dir = "Ee{ebeam_electron}_Ep{ebeam_proton}_L{luminosity}"`
- Replace decimal points with underscores.
- Example: `13.6, 3000` -> `E13_6_L3000`.

After writing `run_config.json`, verify it is valid JSON, then freeze the task:

For SSH/WSL2, first copy the complete script directory and the deliverables
template from the local skill checkout to a target-side runtime directory:

```bash
python scripts/sync_to_target.py --config {local_run_config} scripts {workdir}/.smeft-skill/scripts
python scripts/sync_to_target.py --config {local_run_config} reference/deliverables-contract-template.json {workdir}/.smeft-skill/reference/deliverables-contract-template.json
```

Repeat the first command after modifying any bundled script. This complete
directory copy is the defined source of companion scripts for later target-side
commands; do not guess an individual dependency list.

```bash
python {target_skill_runtime}/scripts/research_contract.py init {workdir}/results/run_config.json
```

Use `target_skill_runtime={workdir}/.smeft-skill` for SSH/WSL2 and the actual
skill directory for Linux local mode.

Run this command on the selected execution target so it can hash the actual UFO
model directories and selected Delphes card. This writes
`research_contract.json`, `deliverables_contract.json`, and `contract_lock.json`
beside `run_config.json`. The research contract includes scientific choices and
content hashes for the selected UFO models and detector card; it
does not freeze execution mode, host names, MG5/CutExperiment/workdir paths,
virtual environments, schedulers, or implementation scripts. The deliverables
contract freezes both fixed outputs and deterministic expansion rules for each
run, claimed operator, scan label, and trained algorithm.

If either contract or the lock already exists, `init` must verify identical
content and refuse to overwrite a different file. In SSH/WSL2 mode, initialize
on the target, then sync the same four JSON files to the local control
`{workdir}/results/` directory. Verify their SHA-256 fields on both sides.

Do not proceed to Phase 2 until `run_config.json`, `research_contract.json`,
`deliverables_contract.json`, and `contract_lock.json` all exist and agree
locally and on the selected target. Then proceed immediately without asking for
confirmation.
