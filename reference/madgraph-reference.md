# MadGraph Reference

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE - once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Overview

This document defines the standardized way to invoke MadGraph5 within the SMEFT-ML workflow. All Phases that use MG5 must follow these conventions.

## Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `mg5path` | Absolute path to MadGraph5 installation | `~/MG5_aMC_v3_5_6` |
| `process_name` | Physics process in MG5 syntax, or a list of such processes | `e+ e- > a a` |
| `model_name` | UFO model name (must exist under `mg5path/models/`) | `gQGC_UFO` |
| `luminosity` | Integrated luminosity in inverse femtobarns | `3000` |
| `ebeam1`, `ebeam2` | Explicit MG5 beam energies in GeV copied from `run_configurations` | `5000.0`, `5000.0` |

**Phase 1 beam conversion (symmetric colliders):**
```
tev_to_gev = 1000.0
ebeam_value = center_of_mass_energy_in_tev * tev_to_gev / 2
```
Example: user input `energy = 13.6` TeV -> `ebeam1 = ebeam2 = 6800.0` GeV
in `run_configurations`.

The factor `1000.0` is only the unit conversion `1 TeV = 1000 GeV`. MG5 run
cards use beam energies in GeV. After Phase 1, event generation reads the
explicit beam energies and does not use `sqrt(s)`.

## Optional Variables

| Variable | Description | When Required |
|----------|-------------|---------------|
| `polbeam1` | Beam 1 polarization, range [-1, 1] | User requests polarization |
| `polbeam2` | Beam 2 polarization, range [-1, 1] | User requests polarization |

## MG5 Config Runner Convention

All workflow phases that generate MG5 events must call `scripts/run_mg5_config.py`
with a JSON configuration. Do not hand-write MG5 order files or call `mg5_aMC`
directly from phase logic. If the runner itself needs maintenance, see the
implementation notes in `scripts/run_mg5.py`.

### Process Name Normalization

**Use the script** (do not reimplement):

```bash
python scripts/normalize_process_name.py "e+ e- > a a"
# Output: ep_em_to_a_a
```

Or import in Python:
```python
from scripts.normalize_process_name import normalize_process_name

folder_base = normalize_process_name(process_name)
```

Rules:
| Character | Replacement |
|-----------|-------------|
| Space ` ` | `_` |
| `+` | `p` |
| `-` | `m` |
| `>` | `to` |
| Other special chars | Remove |

Example: `e+ e- > a a` -> `ep_em_to_a_a`

For `process` lists, do not call `normalize_process_name(config.process)`.
Process-folder naming is runner-owned and returned in the runner result JSON.

### Runner-Owned Files

The runner owns order-file creation, process-folder naming, run tracking, banner
parsing, stdout/stderr log capture, and LHCO count metadata. Phase code should
provide only JSON fields such as `mg5path`, `model`, `process`,
`process_mode`, `target_coefficient`, `c_scan`, `ebeam1`, `ebeam2`, `nevents`,
`run_label`, `output_dir`, and `result_json`.

When building a runner JSON from a `run_configurations` entry:
- pass `ebeam1 = run_config.ebeam1` and `ebeam2 = run_config.ebeam2` for every
  collider type;
- pass `run_label = run_config.run_dir` so MG5 process folders remain
  distinguishable across beam/luminosity configurations;
- do not pass center-of-mass energy fields to runner configs.

`process` may be a string or a list of strings. For a list, the runner writes
one MG5 process folder with:

```text
generate process1 MODE_SUFFIX
add process process2 MODE_SUFFIX
add process process3 MODE_SUFFIX
```

where `MODE_SUFFIX` is owned by the runner, for example `NP=0` for `pure_sm`
or `NP>0` for `pure_np`. Agents should still provide suffix-free process
strings in JSON and should not hand-write this order outside runner
maintenance.

## Process Generation Modes

Depending on the Phase task, use one of these `process_mode` values:

| Mode | Meaning | Used by |
|------|---------|---------|
| `create_np` | Create NP process and parse coefficients without launching events | Phase 3 coefficient discovery |
| `pure_sm` | Generate pure SM sample with NP disabled | Phase 4 baseline, Phase 5 SM |
| `pure_np` | Generate one pure NP sample for one target operator | Phase 3 validation, Phase 5 NP |
| `sm_np` | Generate SM+NP sample without scan syntax | Reserved diagnostic path |
| `scan` | Generate 11 MG5 scan points from one `c_scan` value | Phase 6 scan |

Run a config with:

```bash
python scripts/run_mg5_config.py mg5_attempt.json
```

The runner generates unique order/process names internally, checks MG5 return
codes, and records stdout/stderr log paths in the result JSON.
Automatic process folders include normalized process, model, mode, optional
`run_label`, and timestamp. Do not hand-compute process folder names in phase
logic.


## Pre-Run Preparation (Mandatory Before Event Generation)

After the process directory is created (`output` step completed), the following setup **must** be performed before launching event generation.

### Step 1: Prepare Delphes Card

The Delphes detector card is read from **`run_config.json`** (field `delphes_card`), which was determined during Phase 1 - either user-specified or auto-recommended. See [`reference/phase1-input-collection.md`](phase1-input-collection.md) for the selection logic.

**(1.1) Use the script:**

```bash
python scripts/setup_delphes_card.py {mg5path} {delphes_card} {folder_name}
```

The script:
1. Copies `{mg5path}/Delphes/cards/{delphes_card}` -> `{mg5path}/{folder_name}/Cards/delphes_card.dat`
2. Reads the `.tcl` file to find `source` / `include` dependencies
3. Locates dependency folders under `{mg5path}/Delphes/cards/` and copies them into `Cards/`

Or import in Python:
```python
from scripts.setup_delphes_card import setup_delphes_card

card_path = setup_delphes_card(mg5path, delphes_card, folder_name)
```

**Fallback:** If `delphes_card` is missing from `run_config.json` (legacy path), use the auto-recommendation logic from [`reference/phase1-input-collection.md`](phase1-input-collection.md) to select a card on-the-fly, then write it back to `run_config.json`.

### Step 2: Extract SMEFT Operator Coefficients

Read the parameter card:
```
{mg5path}/{folder_name}/Cards/param_card.dat
```

**Use the script** (do not reimplement):

```bash
python scripts/parse_param_card.py {param_card_path}
```

Output: `{"block_name": "anoinputs", "coefficients": {"1": 1.0e-12, "2": 0.0}}`. The `block_name` field tells you which coefficient block the model uses (e.g. `anoinputs`, `dim8`, `dim6`).

Or import in Python:
```python
from scripts.parse_param_card import parse_anoinputs

result = parse_anoinputs(param_card_path, scan_default=1.0e-12)
block_name = result["block_name"]       # e.g. "anoinputs" or "dim8"
coefficients = result["coefficients"]   # {"1": 1.0e-12, "2": 0.0, ...}
```

The script handles all edge cases:
- Case-insensitive `Block` matching (`Block`, `BLOCK` - MG5 may rewrite in uppercase)
- `scan:[v1,v2,...]` syntax retained after MG5 scan
- Block boundary detection (prevents leaking into `Block mass`, etc.)

Save the mapping for downstream use (e.g., as `operator_coefficients.json`).

## Event Generation Through Runner JSON

After process setup is complete, phase code launches event generation only by
calling `scripts/run_mg5_config.py` or `scripts/recover_lhco_count.py` with JSON
configuration. The runner writes the MG5 order internally.

Agent-controlled fields:
- `process_mode`: `pure_sm`, `pure_np`, `sm_np`, or `scan`
- `target_coefficient`: required for target-operator NP runs and scans
- `coefficient_mode`: `default`, `c_scan`, or `explicit` for non-scan NP runs
- `c_scan`: required for `scan` and `coefficient_mode="c_scan"`
- explicit `ebeam1`/`ebeam2` in GeV; optional `polarization`; and `nevents`
- `madspin`: copied from `run_config.json` after the Phase 1 LLM
  asymptotic-state judgment

The runner handles coefficient-block syntax, beam-energy assignment, Delphes
selection, MadSpin enablement, launch confirmation, run-folder tracking, and
output labels.

### Detector-Level Process Validation

Phase 1 performs the asymptotic-state judgment by LLM physics reasoning and
writes `process_validation` plus `madspin` to `run_config.json`. Do not replace
that judgment with a hard-coded script or particle table.

This workflow uses "asymptotic state" in an operational Delphes/LHCO sense.
Explicit quarks or gluons such as `g`, `u`, `d`, `s`, `c`, or `b` must not
appear directly in initial or final states; use `p` for hadronic beams and `j`
for final-state jets. Initial-state `w+`, `w-`, or `z` must not be accepted.
Final-state `t`, `t~`, `w+`, `w-`, and `z` are the only non-asymptotic
exceptions; they require `madspin.enabled=true` so they decay before
Delphes/LHCO analysis.

`scripts/run_mg5_config.py` does not make this physics judgment. It only reads
`madspin.enabled` from config and writes `madspin=ON` into the MG5 launch order
when requested.

### Event Count Recovery

MG5 may produce fewer LHCO events than the requested `nevents`. This is not a
serious problem unless the actual LHCO count is clearly insufficient. Follow
[`event-count-recovery.md`](event-count-recovery.md) for thresholds, recovery
profiles, LHCO merging, and efficiency denominators.

The recovery orchestrator applies survey profiles through the runner. Agents
select only the recovery wrapper; do not write recovery launch-order lines.

Prefer the config-driven runner and recovery orchestrator:

```bash
python scripts/run_mg5_config.py run_config_for_one_attempt.json
python scripts/recover_lhco_count.py recovery_config.json
```

The MG5 config runner validates that the UFO model already exists under
`{mg5path}/models/{model_name}`. It does not copy UFO models; model sync/install
belongs to Phase 1/2 target setup. The runner copies only the Delphes card and
Delphes card dependencies into the generated process folder.

### Config-Driven Runner Examples

Phase 5 SM attempt:

```json
{
  "mg5path": "/opt/MG5_aMC",
  "model": "AQGCm_UFO",
  "process": "mu+ mu- > a j j",
  "madspin": {"enabled": false},
  "process_mode": "pure_sm",
  "run_label": "E10_L1000",
  "ebeam1": 5000.0,
  "ebeam2": 5000.0,
  "nevents": 500000,
  "delphes_card": "delphes_card_MuonColliderDet.tcl",
  "cutexperiment_path": "/opt/CutExperiment",
  "output_label": "sm",
  "output_dir": "/work/results/data/phase5",
  "result_json": "/work/results/data/phase5/sm_mg5_result.json"
}
```

Equivalent multi-process example:

```json
{
  "mg5path": "/opt/MG5_aMC",
  "model": "AQGCm_UFO",
  "process": ["mu+ mu- > l+ vl j j", "mu+ mu- > l- vl~ j j"],
  "madspin": {"enabled": false},
  "process_mode": "pure_sm",
  "run_label": "E10_L1000",
  "ebeam1": 5000.0,
  "ebeam2": 5000.0,
  "nevents": 500000,
  "delphes_card": "delphes_card_MuonColliderDet.tcl",
  "output_dir": "/work/results/phase5",
  "result_json": "/work/results/phase5/sm_attempt.json"
}
```

Phase 5 pure NP attempt:

```json
{
  "mg5path": "/opt/MG5_aMC",
  "model": "AQGCm_UFO",
  "process": "mu+ mu- > a j j",
  "madspin": {"enabled": false},
  "process_mode": "pure_np",
  "operator": "o_3",
  "target_coefficient": {"index": 3},
  "coefficient_mode": "c_scan",
  "c_scan": 1.2e-12,
  "run_label": "E10_L1000",
  "ebeam1": 5000.0,
  "ebeam2": 5000.0,
  "nevents": 100000,
  "delphes_card": "delphes_card_MuonColliderDet.tcl",
  "cutexperiment_path": "/opt/CutExperiment",
  "output_dir": "/work/results/data/phase5",
  "result_json": "/work/results/data/phase5/np_o_3_mg5_result.json"
}
```

Phase 6 scan attempt:

```json
{
  "mg5path": "/opt/MG5_aMC",
  "model": "AQGCm_UFO",
  "process": "mu+ mu- > a j j",
  "madspin": {"enabled": false},
  "process_mode": "scan",
  "operator": "o_3",
  "target_coefficient": {"index": 3},
  "c_scan": 1.2e-12,
  "run_label": "E10_L1000",
  "ebeam1": 5000.0,
  "ebeam2": 5000.0,
  "nevents": 1000000,
  "delphes_card": "delphes_card_MuonColliderDet.tcl",
  "cutexperiment_path": "/opt/CutExperiment",
  "output_dir": "/work/results/data/phase6",
  "result_json": "/work/results/data/phase6/np_o_3_scan_mg5_result.json"
}
```

Recovery wrapper for the Phase 6 scan above:

```json
{
  "requested_event_count": 1000000,
  "attempt_root": "/work/results/data/phase6/recovery_attempts/np_o_3",
  "merged_output_dir": "/work/results/data/phase6",
  "metadata_path": "/work/results/data/phase6/event_count_recovery_np_o_3.json",
  "base_mg5_config": {
    "mg5path": "/opt/MG5_aMC",
    "model": "AQGCm_UFO",
    "process": "mu+ mu- > a j j",
    "madspin": {"enabled": false},
    "process_mode": "scan",
    "operator": "o_3",
    "target_coefficient": {"index": 3},
    "c_scan": 1.2e-12,
    "run_label": "E10_L1000",
    "ebeam1": 5000.0,
    "ebeam2": 5000.0,
    "nevents": 1000000,
    "delphes_card": "delphes_card_MuonColliderDet.tcl",
    "cutexperiment_path": "/opt/CutExperiment"
  }
}
```

### Beam Assignment

| Collider Type | `ebeam1` | `ebeam2` | Derivation |
|---------------|----------|----------|------------|
| Symmetric (ee, pp, mu-mu) | explicit beam energy in GeV | same as `ebeam1` | computed once in Phase 1 from the user center-of-mass energy |
| Asymmetric (ep) | explicit electron beam energy in GeV | explicit proton beam energy in GeV | copied from the user beam-energy pair |

**Note:** `sqrt(s)` is not a runner input. For manuscript metadata, call
`scripts/beam_energy.py` and read `sqrt_s_tev` from its JSON output. Do not
derive `sqrt(s)` inline in phase code or prose.

### Coefficient Block

At most **one** coefficient may be non-zero in any given run. All other coefficients in the coefficient block must be explicitly set to `0.0`.

**Rule:** For each coefficient `fi` with default value `fi_default` (read from `param_card.dat`):
- If `fi` is the **target operator**: set to `fi_default` (or `1.0` if `fi_default == 0`)
- If `fi` is **not** the target operator: set to `0.0`

**Critical:** In MG5 `launch` mode, parameter values must be set via `set {block_name} {lha_code} {value}`. The bare `set {number} = {value}` syntax is silently ignored. The `{block_name}` (e.g. `anoinputs`, `dim8`) is obtained from `parse_param_card.py` output. Use:

```
set {block_name} {idx} {value}
```

**Example:**

Assume the model uses `Block anoinputs` (`block_name = "anoinputs"`). Coefficients: `f1` (LHA code 1), `f2` (LHA code 2), `f3` (3), `f4` (4). Target operator is `f2`, with `f2_default = 1.0e-12`.

```
set anoinputs 1 0.0
set anoinputs 2 1.0e-12
set anoinputs 3 0.0
set anoinputs 4 0.0
```

**Example with zero default:**

If `f2_default = 0.0`, set `anoinputs 2 1.0` instead.

### Polarization (Optional)

If polarization is enabled (read `polarization` from **`run_config.json`**), append after `set ebeam2`:

```
set polbeam1 = {polbeam1_value}
set polbeam2 = {polbeam2_value}
```

Polarization values are typically in the range [-1, 1]. Omit these lines if polarization is not requested.

## Post-Processing: ROOT to LHCO Conversion

After event generation completes, MadGraph produces output under:
```
{mg5path}/{folder_name}/Events/
```

Each generation run creates a subfolder named `run_01`, `run_02`, etc.

### Determine Target Run Folder

**Rule:** Select the run folder with the **largest numeric suffix** (e.g., if `run_01` and `run_02` both exist, use `run_02`).

**Note:** `tag_1` in the filename `tag_1_delphes_events.root` is fixed when using the order template in this workflow.

### Convert ROOT to LHCO (Use the Script)

**Use the script** (do not reimplement):

```bash
python scripts/convert_root_to_lhco.py {mg5path} {folder_name} {run_folder}
```

The script:
1. Auto-detects the jet branch (`Jet`, `GenJet`, `FatJet`) from `delphes_card.dat`
2. Invokes `root2lhco` with the correct `--jet-branch=` flag
3. Captures stdout/stderr to `run_XX/root2lhco.log`
4. Validates output: aborts if `.lhco` is empty or suspiciously small compared to `.root`
5. Reports the specific error from the log on failure

Or import in Python:
```python
from scripts.convert_root_to_lhco import convert_root_to_lhco

lhco_path = convert_root_to_lhco(mg5path, folder_name, run_folder)
```

**Validation rules:**
- `.lhco` must exist and be non-empty
- If `.lhco` < 1 KB but `.root` > 1 MB -> `root2lhco` failed silently; **check the log**
- Do NOT proceed to cleanup if `.lhco` is invalid

### Step 3: Retain and Clean Files

After successful LHCO conversion, the run folder contains:

| File | Action | Reason |
|------|--------|--------|
| `{run_folder}_tag_1_banner.txt` | **Retain** | Contains run metadata and cross-section info |
| `{run_folder}.lhco` | **Retain** | Converted event data for downstream analysis |
| `unweighted_events.lhe.gz` | **Delete** | Large raw event file; LHCO replaces it |
| `tag_1_pythia8_events.hepmc.gz` | **Delete** | Large intermediate HepMC file |
| `tag_1_delphes_events.root` | **Delete** | Large ROOT file; LHCO replaces it |

**Cleanup command example:**
```bash
cd {mg5path}/{folder_name}/Events/{run_folder}
rm unweighted_events.lhe.gz tag_1_pythia8_events.hepmc.gz tag_1_delphes_events.root
```

## Cross-Section Extraction

For normal workflow event generation, read cross-sections from
`scripts/run_mg5_config.py` result JSON (`outputs[*].cross_section_pb`). The
runner uses the canonical banner parser internally and records stdout/stderr
paths for debugging.

The lower-level banner parser is for runner maintenance and diagnostics only.
If you need it, pass the banner path recorded in the runner result JSON:

```bash
python scripts/extract_cross_section.py /path/from/runner_result_banner_path.txt
```

The cross-section is recorded in the banner text file produced after each MadGraph run:
```
{mg5path}/{folder_name}/Events/{run_folder}/{run_folder}_tag_1_banner.txt
```

Do not infer banner filenames in phase logic. If importing inside a script:

```python
from scripts.extract_cross_section import extract_cross_section

cs = extract_cross_section(banner_path)  # returns float in pb
```

The script supports both MG5_aMC v3.x (`Integrated weight (pb) : X.XXXX`) and older (`X +/- Y pb`) formats. Raises `ValueError` on parse failure.

**Critical rules:**
- Any positive value, even `1e-10 pb`, is a valid cross-section.
- Do NOT silently return `0.0` on parse failure. Raise an error so the failure is visible.
- All phases that read cross-sections must use the runner result JSON. Low-level
  scripts may import `extract_cross_section()`.
- A parsed `0.0` banner cross-section, or a missing banner, is not enough to
  prove a true zero cross section. Run `scripts/double_check_zero_cross_section.py`
  or use `scripts/run_mg5_config.py`, which calls it automatically. Accept zero
  cross section only when all three conditions hold: banner evidence is exactly
  `0.0` or missing, MG5 stdout/stderr contains `zero cross section`,
  `zero crosssection`, or `zero cross-section`, and the run directory contains
  no substantial LHE-like event payload (`.lhe`, `.lhe.gz`, or tar archives
  containing `.lhe`).
- During Phase 3 process creation, MG5 "no Feynman diagrams" is a separate,
  explicit zero-contribution result for that model/process. Record it in
  `model_status` and continue to the next model; do not require banner/LHE
  evidence because no event run was launched.
- Use banners for cross-sections only. Do not read event counts from banners for
  efficiencies or normalization; banner event counts may be requested targets,
  not actual LHCO output. Actual event counts must come from
  `LoadLHCOlympics(...).GetEventCount()`.

## Validation Checklist

Before writing/running a runner config:
- [ ] `mg5path` exists and is an absolute path
- [ ] `{mg5path}/bin/mg5_aMC` or `{mg5path}/bin/mg5` exists
- [ ] `{mg5path}/models/{model_name}` exists
- [ ] `process_name` uses valid MG5 syntax
- [ ] `process_validation` from Phase 1 records the LLM asymptotic-state
      judgment; explicit quark/gluon states use `p` or `j`, and allowed
      final-state `t/t~/w+/w-/z` have MadSpin enabled
- [ ] runner config includes positive `ebeam1`, positive `ebeam2`, positive luminosity metadata when applicable, and `run_label` copied from `run_configurations[*].run_dir`
- [ ] `process_mode`, `target_coefficient`, `c_scan`, and `nevents` match the phase task

After process creation (`output` step), before event generation:
- [ ] Collider type is identified; default applied if user did not specify
- [ ] For ep collisions: each runner config includes positive `ebeam1` and `ebeam2`
- [ ] Delphes `.tcl` card is copied to `Cards/delphes_card.dat`
- [ ] All `.tcl` dependency folders are copied to `Cards/`
- [ ] A coefficient block is found in `param_card.dat` (e.g. `anoinputs`, `dim8`) and coefficients are recorded
- [ ] If polarization requested: `polbeam1` and `polbeam2` are in [-1, 1]

After event generation, before cleanup:
- [ ] Latest `run_XX` folder is identified (largest numeric suffix)
- [ ] `root2lhco` produces a valid, non-empty `.lhco` file
