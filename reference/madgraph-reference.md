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

Before constructing folder names, normalize `process_name` by replacing special characters:

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

| Mode | Order file `generate` line | Folder suffix |
|------|---------------------------|---------------|
| Default | `generate {process_name}` | (none) |
| Pure SM (NP off) | `generate {process_name} NP=0` | `_SM` |
| New Physics on | `generate {process_name} NP>0` | `_NP` |

**Folder naming rule:**
- Default: `{folder_base}_{phase}_{timestamp}_{suffix}`
- SM mode: `{folder_base}_{phase}_{timestamp}_{suffix}_SM`
- NP mode: `{folder_base}_{phase}_{timestamp}_{suffix}_NP`

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

### Primary Command

```bash
cd {mg5path} && ./bin/mg5_aMC {order_filename}
```

### Fallback Command

If the primary command fails (e.g., `mg5_aMC` does not exist in older MG5 versions), try:

```bash
cd {mg5path} && ./bin/mg5 {order_filename}
```

### Execution Logic

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

**(1.1) Locate and copy the `.tcl` card:**

Copy the selected card from:
```
{mg5path}/Delphes/cards/{delphes_card}
```

To the process directory:
```
{mg5path}/{folder_name}/Cards/delphes_card.dat
```

**(1.2) Resolve card dependencies:**

Read the `.tcl` file content to identify any `source` or `include` statements that reference external directories. Locate those dependency **folders** under `{mg5path}/Delphes/cards/` and copy the **entire folder** into:
```
{mg5path}/{folder_name}/Cards/
```

This ensures the Delphes card and all its dependencies are self-contained within the process directory.

**Fallback:** If `delphes_card` was not set in Phase -1 (legacy path), use the auto-recommendation logic from [`SKILL.md`](../SKILL.md) to select a card on-the-fly.

### Step 3: Extract SMEFT Operator Coefficients

Read the parameter card:
```
{mg5path}/{folder_name}/Cards/param_card.dat
```

Locate the block:
```
Block anoinputs
```

Record **every variable name and its default value** in this block. For SMEFT models, these are the Wilson coefficients (operator coefficients) that will be scanned or constrained in later Phases.

Save this mapping for downstream use (e.g., as `operator_coefficients.json`).

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
| Asymmetric (ep) | `ebeam_value` (electron) | `ebeam_proton` (proton) | `ebeam_proton` is an extra user input |

**Note:** The center-of-mass energy is `2 * ebeam_value` for symmetric colliders.

### Coefficient Block

At most **one** coefficient may be non-zero in any given run. All other coefficients in `Block anoinputs` must be explicitly set to `0.0`.

**Rule:** For each coefficient `fi` with default value `fi_default` (read from `param_card.dat`):
- If `fi` is the **target operator**: set to `fi_default` (or `1.0` if `fi_default == 0`)
- If `fi` is **not** the target operator: set to `0.0`

**Example:**

Coefficients: `f1`, `f2`, `f3`, `f4`. Target operator is `f2`, with `f2_default = 1.0e-12`.

```
set f1 = 0.0
set f2 = 1.0e-12
set f3 = 0.0
set f4 = 0.0
```

**Example with zero default:**

If `f2_default = 0.0`, set `f2 = 1.0` instead.

### Polarization (Optional)

If the user requests beam polarization, append after `set ebeam2`:

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

Each generation run creates a subfolder named `run_01`, `run_02`, etc. This section describes how to convert the Delphes ROOT output into `.lhco` format and clean up temporary large files.

### Determine Target Run Folder

After event generation, identify the latest run folder under:
```
{mg5path}/{folder_name}/Events/
```

**Rule:** Select the run folder with the **largest numeric suffix** (e.g., if `run_01` and `run_02` both exist, use `run_02`).

The following steps assume the target folder is `run_02`. Replace with the actual detected folder name.

**Note:** `tag_1` in the filename `tag_1_delphes_events.root` is fixed when using the order template in this workflow.

### Step 1: Detect Jet Branch Name

Read the Delphes card:
```
{mg5path}/{folder_name}/Cards/delphes_card.dat
```

Search for lines matching the pattern:
```
add Branch {finder}/jets {branch_name} Jet
```

Examples:
```
add Branch UniqueObjectFinder/jets Jet Jet
add Branch GenJetFinder/jets GenJet Jet
add Branch FatJetFinder/jets FatJet Jet
```

For each matching line, look at the substring **after the first `/`**, then split by spaces. The **second string** in that split is the branch name.

- `UniqueObjectFinder/jets Jet Jet` → after `/` → `jets Jet Jet` → second string = `Jet`
- `GenJetFinder/jets GenJet Jet` → after `/` → `jets GenJet Jet` → second string = `GenJet`
- `FatJetFinder/jets FatJet Jet` → after `/` → `jets FatJet Jet` → second string = `FatJet`

Determine which case applies:

| Case | Condition | Command |
|------|-----------|---------|
| Jet branch exists | Any branch name equals `Jet` (not `GenJet` or `FatJet`) | Standard `root2lhco` |
| GenJet only | No branch name equals `Jet`, but `GenJet` exists | `root2lhco --jet-branch=GenJet` |

### Step 2: Convert ROOT to LHCO

Change to the Delphes directory and run the converter.

**Case A: Jet branch exists**
```bash
cd {mg5path}/Delphes
./root2lhco ../{folder_name}/Events/{run_folder}/tag_1_delphes_events.root ../{folder_name}/Events/{run_folder}/{run_folder}.lhco
```

**Case B: Only GenJet exists**
```bash
cd {mg5path}/Delphes
./root2lhco --jet-branch=GenJet ../{folder_name}/Events/{run_folder}/tag_1_delphes_events.root ../{folder_name}/Events/{run_folder}/{run_folder}.lhco
```

### Step 3: Validate LHCO Output

Before cleaning up large files, verify the conversion succeeded:

1. Check that `{run_folder}.lhco` exists in `{mg5path}/{folder_name}/Events/{run_folder}/`
2. Check that the file is non-empty (size > 0)

**If either check fails:** Abort the entire workflow and report the `root2lhco` failure reason. Do NOT proceed to cleanup.

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

**Canonical extraction function** (use this in every phase that reads a banner):

```python
import re

def extract_cross_section(banner_path):
    """Extract cross-section in pb from an MG5 banner file.

    Supports both MG5_aMC v3.x and older banner formats.
    Raises ValueError if no cross-section line is found.
    """
    with open(banner_path) as f:
        for line in f:
            # Primary: MG5_aMC v3.x format
            m = re.search(r"Integrated weight \(pb\)\s*:\s*([\d.eE+-]+)", line)
            if m:
                return float(m.group(1))
            # Fallback: older format with uncertainty
            m = re.search(r"([\d.eE+-]+)\s*\+/-\s*([\d.eE+-]+)\s*pb", line)
            if m:
                return float(m.group(1))
    raise ValueError(f"No cross-section found in {banner_path}")
```

**Critical rules:**
- Any positive value — even `1e-10 pb` — is a valid cross-section. Only `0.0` (or parse failure) is invalid.
- Do NOT silently return `0.0` on parse failure. Raise an error so the failure is visible.
- All phases that read banner cross-sections must use this function (or an equivalent).

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
