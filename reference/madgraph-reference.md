# MadGraph Reference

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE — once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Overview

This document defines the standardized way to invoke MadGraph5 within the SMEFT-ML workflow. All Phases that use MG5 must follow these conventions.

## Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `mg5path` | Absolute path to MadGraph5 installation | `~/MG5_aMC_v3_5_6` |
| `process_name` | Physics process in MG5 syntax | `e+ e- > a a` |
| `model_name` | UFO model name (must exist under `mg5path/models/`) | `gQGC_UFO` |
| `energy` | Center-of-mass energy in TeV | `13.6` |
| `luminosity` | Integrated luminosity in inverse femtobarns | `3000` |
| `ebeam_value` | Single-beam energy in GeV (auto-derived for symmetric colliders) | `6800.0` |

**Energy conversion (symmetric colliders):**
```
ebeam_value = energy * 1000 / 2
```
Example: `energy = 13.6` TeV → `ebeam_value = 6800.0` GeV.

## Optional Variables

| Variable | Description | When Required |
|----------|-------------|---------------|
| `ebeam_proton` | Proton beam energy in GeV (ep colliders only) | Asymmetric ep collisions |
| `polbeam1` | Beam 1 polarization, range [-1, 1] | User requests polarization |
| `polbeam2` | Beam 2 polarization, range [-1, 1] | User requests polarization |

## Order File Convention

MG5 is invoked via a text-based "order file" rather than interactive commands.

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

Example: `e+ e- > a a` → `ep_em_to_a_a`

### File Naming

The order file name and the output folder name **must be auto-generated** by the skill. Do not ask the user to provide them. The folder name is based on the **normalized process name**:

```
order_{phase}_{timestamp}_{random_suffix}.txt
{folder_base}_{phase}_{timestamp}_{random_suffix}
```

Where `folder_base` is the normalized `process_name`.

Example:
```
order_p1_20260525_01.txt
ep_em_to_a_a_p1_20260525_01
```

**Collision avoidance:** Before creating the file or folder, check if a name already exists in `mg5path/`. If so, increment the suffix until unique.

### File Location

The order file is placed **directly under `mg5path/`**:
```
{mg5path}/order_p1_20260525_01.txt
```

The output folder is also placed under `mg5path/`:
```
{mg5path}/{folder_name}/
```

## Process Generation Modes

Depending on the Phase task, there are **three generation modes**. The `generate` line in the order file and the folder naming differ:

| Mode | Order file `generate` line | Folder suffix | Used by |
|------|---------------------------|---------------|---------|
| Default | `generate {process_name}` | (none) | Phase 4 scan |
| Pure SM (NP off) | `generate {process_name} NP=0` | `_SM` | Phase 2 baseline, Phase 3 SM |
| New Physics on | `generate {process_name} NP>0` | `_NP` | Phase 1 validation, Phase 3 NP |

**Folder naming rule:**
- Default: `{folder_base}_{phase}_{timestamp}_{suffix}`
- SM mode: `{folder_base}_{phase}_{timestamp}_{suffix}_SM`
- NP mode: `{folder_base}_{phase}_{timestamp}_{suffix}_NP`

**Phase directory examples:**
- Phase 1: `ep_em_to_a_a_p1_20260525_01_NP`
- Phase 2: `ep_em_to_a_a_p2_20260525_01_SM`
- Phase 3 SM: `ep_em_to_a_a_p3_20260525_01_SM`
- Phase 3 NP: `ep_em_to_a_a_p3_20260525_01_NP`
- Phase 4: `ep_em_to_a_a_p4_20260525_01`

### Minimum Order File for Process Creation

```
import model {model_name}
generate {process_name} [NP=0 | NP>0]
output {folder_name}
```

Example (SM mode):
```
import model gQGC_UFO
generate e+ e- > a a NP=0
output ep_em_to_a_a_p1_20260525_01_SM
```

## Running MadGraph

**Use the script** (do not reimplement):

```bash
python scripts/run_mg5.py {mg5path} {order_filename}
```

The script:
1. Tries `./bin/mg5_aMC` first, falls back to `./bin/mg5`
2. Checks return code; on failure prints stdout/stderr and exits with error
3. **Parses MG5 stdout in real time** to detect stage transitions (MadGraph → Pythia8 → Delphes) and records internal step timings

Or import in Python:
```python
from scripts.run_mg5 import run_mg5
from scripts.timing_tracker import TimingTracker

tracker = TimingTracker()
result = run_mg5(mg5path, order_filename, timing_tracker=tracker)
# result["mg5_steps"] contains timing for madgraph, pythia8, delphes
```

**Execution Logic:**
```
1. Write order file to {mg5path}/{order_filename}
2. Attempt: cd {mg5path} && ./bin/mg5_aMC {order_filename}
3. If step 2 fails (exit code != 0 or binary not found):
   Attempt: cd {mg5path} && ./bin/mg5 {order_filename}
4. If both fail: abort and report MG5 invocation error
```

## Pre-Run Preparation (Mandatory Before Event Generation)

After the process directory is created (`output` step completed), the following setup **must** be performed before launching event generation.

### Step 1: Prepare Delphes Card

The Delphes detector card is selected during **Phase -1** (see [`SKILL.md`](../SKILL.md) Delphes Card Auto-Recommendation). By the time this phase runs, `delphes_card` is already determined — either user-specified or auto-recommended.

**(1.1) Use the script:**

```bash
python scripts/setup_delphes_card.py {mg5path} {delphes_card} {folder_name}
```

The script:
1. Copies `{mg5path}/Delphes/cards/{delphes_card}` → `{mg5path}/{folder_name}/Cards/delphes_card.dat`
2. Reads the `.tcl` file to find `source` / `include` dependencies
3. Locates dependency folders under `{mg5path}/Delphes/cards/` and copies them into `Cards/`

Or import in Python:
```python
from scripts.setup_delphes_card import setup_delphes_card

card_path = setup_delphes_card(mg5path, delphes_card, folder_name)
```

**Fallback:** If `delphes_card` was not set in Phase -1 (legacy path), use the auto-recommendation logic from [`SKILL.md`](../SKILL.md) to select a card on-the-fly.

### Step 3: Extract SMEFT Operator Coefficients

Read the parameter card:
```
{mg5path}/{folder_name}/Cards/param_card.dat
```

**Use the script** (do not reimplement):

```bash
python scripts/parse_param_card.py {param_card_path}
```

Output: JSON dict mapping LHA index → coefficient value, e.g. `{"1": 1.0e-12, "2": 0.0}`.

Or import in Python:
```python
from scripts.parse_param_card import parse_anoinputs

coefficients = parse_anoinputs(param_card_path, scan_default=1.0e-12)
```

The script handles all edge cases:
- Case-insensitive `Block` matching (`Block`, `BLOCK` — MG5 may rewrite in uppercase)
- `scan:[v1,v2,...]` syntax retained after MG5 scan
- Block boundary detection (prevents leaking into `Block mass`, etc.)

Save the mapping for downstream use (e.g., as `operator_coefficients.json`).

## Event Generation Order

After the process directory is created and pre-run preparation is complete, write a **second order file** to launch event generation.

### Order File Template

```
launch {folder_name}
detector = Delphes
analysis = OFF
0
{coefficient_block}
set ebeam1 = {ebeam1_value}
set ebeam2 = {ebeam2_value}
{polarization_block}
set nevents = {event_number}
0
```

### Field Rules

| Line | Rule |
|------|------|
| `launch {folder_name}` | Must match the folder created in the `output` step |
| `detector = Delphes` | Fixed; Delphes fast simulation is always used |
| `analysis = OFF` | Fixed; no built-in analysis histograms |
| First `0` | Confirms detector/analysis selection in MG5 interactive menu |
| `{coefficient_block}` | See Coefficient Block section below |
| `set ebeam1` / `set ebeam2` | Beam energy in GeV; see Energy Assignment below |
| `{polarization_block}` | Optional; see Polarization section below |
| `set nevents` | Total number of events to generate |
| Second `0` | Confirms run card settings and starts generation |

### Energy Assignment

| Collider Type | `ebeam1` | `ebeam2` | Derivation |
|---------------|----------|----------|------------|
| Symmetric (ee, pp, mu-mu) | `ebeam_value` | `ebeam_value` | `ebeam_value = energy * 1000 / 2` |
| Asymmetric (ep) | `ebeam_value` (electron) | `ebeam_proton` (proton) | `ebeam_proton` is collected in **Phase -1** (see [`SKILL.md`](../SKILL.md)) |

**Note:** The center-of-mass energy is `2 * ebeam_value` for symmetric colliders.

### Coefficient Block

At most **one** coefficient may be non-zero in any given run. All other coefficients in `Block anoinputs` must be explicitly set to `0.0`.

**Rule:** For each coefficient `fi` with default value `fi_default` (read from `param_card.dat`):
- If `fi` is the **target operator**: set to `fi_default` (or `1.0` if `fi_default == 0`)
- If `fi` is **not** the target operator: set to `0.0`

**Critical:** In MG5 `launch` mode, parameter values must be set via `set {block} {lha_code} {value}`. The bare `set {number} = {value}` syntax is silently ignored. For SMEFT models, use:

```
set anoinputs {idx} {value}
```

**Example:**

Coefficients in `Block anoinputs`: `f1` (LHA code 1), `f2` (LHA code 2), `f3` (3), `f4` (4). Target operator is `f2`, with `f2_default = 1.0e-12`.

```
set anoinputs 1 0.0
set anoinputs 2 1.0e-12
set anoinputs 3 0.0
set anoinputs 4 0.0
```

**Example with zero default:**

If `f2_default = 0.0`, set `anoinputs 2 1.0` instead.

### Polarization (Optional)

If the user requested beam polarization in **Phase -1** (see [`SKILL.md`](../SKILL.md) Optional Inputs), append after `set ebeam2`:

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
- If `.lhco` < 1 KB but `.root` > 1 MB → `root2lhco` failed silently; **check the log**
- Do NOT proceed to cleanup if `.lhco` is invalid

### Step 4: Retain and Clean Files

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

## Cross-Section Extraction from Banner

The cross-section is recorded in the banner text file produced after each MadGraph run:
```
{mg5path}/{folder_name}/Events/{run_folder}/{run_folder}_tag_1_banner.txt
```

**Use the script** (do not reimplement):

```bash
python scripts/extract_cross_section.py {banner_path}
```

Or import in Python:

```python
from scripts.extract_cross_section import extract_cross_section

cs = extract_cross_section(banner_path)  # returns float in pb
```

The script supports both MG5_aMC v3.x (`Integrated weight (pb) : X.XXXX`) and older (`X +/- Y pb`) formats. Raises `ValueError` on parse failure.

**Critical rules:**
- Any positive value — even `1e-10 pb` — is a valid cross-section. Only `0.0` (or parse failure) is invalid.
- Do NOT silently return `0.0` on parse failure. Raise an error so the failure is visible.
- All phases that read banner cross-sections must use the script (or an equivalent).

## Validation Checklist

Before writing an order file:
- [ ] `mg5path` exists and is an absolute path
- [ ] `{mg5path}/bin/mg5_aMC` or `{mg5path}/bin/mg5` exists
- [ ] `{mg5path}/models/{model_name}` exists
- [ ] `process_name` uses valid MG5 syntax
- [ ] `energy` > 0 and `luminosity` > 0
- [ ] Auto-generated `folder_name` does not already exist in `mg5path/`

After process creation (`output` step), before event generation:
- [ ] Collider type is identified; default applied if user did not specify
- [ ] For ep collisions: `ebeam_proton` is provided
- [ ] Delphes `.tcl` card is copied to `Cards/delphes_card.dat`
- [ ] All `.tcl` dependency folders are copied to `Cards/`
- [ ] `Block anoinputs` is found in `param_card.dat` and coefficients are recorded
- [ ] If polarization requested: `polbeam1` and `polbeam2` are in [-1, 1]

After event generation, before cleanup:
- [ ] Latest `run_XX` folder is identified (largest numeric suffix)
- [ ] `root2lhco` produces a valid, non-empty `.lhco` file
