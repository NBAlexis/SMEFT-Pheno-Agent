# MadGraph5 Automatic Installation

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE — once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Overview

This document describes how to automatically install a complete MadGraph5_aMC@NLO (MG5) environment including Pythia8, LHAPDF6, and Delphes — everything required for the SMEFT-ML workflow.

**Why LHAPDF6 matters:** Without LHAPDF6, MG5 cannot compute Parton Distribution Function (PDF) systematic uncertainties. This is a core physics requirement for hadron-collider processes.

---

## System Dependencies

Before installing MG5, the following system packages must be present. The auto-installer **detects** them; if any are missing, it prints the install command and aborts.

| Package | Purpose | Check Command |
|---------|---------|---------------|
| `build-essential` | gcc/g++ compilers | `which gcc` |
| `gfortran` | Fortran compiler | `which gfortran` |
| `libboost-all-dev` | Boost C++ libraries | `dpkg -l \| grep libboost` |
| `python3` | Python runtime | `which python3` |
| `curl` or `wget` | Download tool | `which curl` |

**Install command (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install -y build-essential gfortran libboost-all-dev python3 curl
```

> **Note:** The installer does **not** run `sudo` automatically (password may be required). It detects missing packages and tells the user what to run.

---

## MG5 Download Sources

The **LLM/skill** fetches `https://launchpad.net/mg5amcnlo` at runtime, parses the HTML, and extracts the latest download URL and directory name. The script itself does **not** scrape launchpad.

As of this writing, the available versions are:

| Type | Version | URL | Size |
|------|---------|-----|------|
| **LTS** (recommended) | v3.5.15 | `https://launchpad.net/mg5amcnlo/3.0/3.7.x/+download/LTS_MG5aMC_v3.5.15.tgz` | ~31 MB |
| Latest stable | v3.7.1 | `https://launchpad.net/mg5amcnlo/3.0/3.7.x/+download/MG5_aMC_v3.7.1.tar.gz` | ~TBD |

The LTS version is preferred for reproducibility. Launchpad redirects to `launchpadlibrarian.net` (HTTP 303); the downloader must follow redirects.

---

## Installation Steps

### Step 1: LLM Parses Launchpad

The skill fetches `https://launchpad.net/mg5amcnlo` and parses the HTML to find:
- The **download URL** for the selected version (LTS or latest stable)
- The **extracted directory name** (e.g. `MG5_aMC_v3_5_15`)

> **Rationale:** Launchpad page structure and naming conventions change over time. The LLM adapts to whatever structure is present, rather than relying on brittle regexes in a script.

### Step 2: Download and Extract

```bash
curl -L -o /tmp/LTS_MG5aMC_v3.5.15.tgz \
  "https://launchpad.net/mg5amcnlo/3.0/3.7.x/+download/LTS_MG5aMC_v3.5.15.tgz"

tar -xzf /tmp/LTS_MG5aMC_v3.5.15.tgz -C {install_dir}
```

Result: `{install_dir}/MG5_aMC_v3_5_15/` with `bin/mg5_aMC` inside.

### Step 3: Install MG5 Internal Dependencies

Run MG5 with an order file containing the `install` commands:

```
install pythia8
install lhapdf6
install delphes
```

MG5 will:
- Download and compile Pythia8 under `HEPTools/pythia8/`
- Download and compile LHAPDF6 under `HEPTools/lhapdf6_py3/`
- Download and compile Delphes under `Delphes/`

**Critical:** These installs are CPU-intensive (compilation of C++ code). Each takes 5–20 minutes depending on the machine.

### Step 4: Verify Installation

After all installs complete, verify:

```bash
ls {mg5path}/bin/mg5_aMC
ls {mg5path}/HEPTools/pythia8/lib/libpythia8.so
ls {mg5path}/HEPTools/lhapdf6_py3/bin/lhapdf-config
ls {mg5path}/Delphes/cards/delphes_card_default.dat
```

### Step 5: Environment Variables

MG5 writes paths to `{mg5path}/input/mg5_configuration.txt` during install. However, **runtime** requires two environment variables:

| Variable | Path | Purpose |
|----------|------|---------|
| `PATH` | `{mg5path}/HEPTools/bin` | Find `lhapdf-config` and other HEPTools binaries |
| `LD_LIBRARY_PATH` | `{mg5path}/HEPTools/lib` | Load `libpythia8.so` and other shared libraries |

```bash
export PATH={mg5path}/HEPTools/bin:$PATH
export LD_LIBRARY_PATH={mg5path}/HEPTools/lib:$LD_LIBRARY_PATH
```

**The script does NOT modify any environment variable.** It prints a report at the end showing:
- The current `PATH` and `LD_LIBRARY_PATH` values
- The recommended `export` commands

The **LLM/skill inspects this report** and decides:
1. Whether the current session already has the required paths
2. Whether to run the export commands for the current session
3. Whether to append them to `~/.bashrc` for persistence (with comment markers `# MG5_auto_install_PATH` / `# MG5_auto_install_LD_LIBRARY_PATH`)

---

## Reusable Script

**Use the script** (do not reimplement):

```bash
python scripts/install_mg5.py {install_dir} --url {download_url} --name {extracted_name}
```

| Argument | Description | Required |
|----------|-------------|----------|
| `install_dir` | Directory where MG5 will be extracted | yes |
| `--url` | Direct download URL for the MG5 tarball | yes |
| `--name` | Name of the top-level directory inside the tarball (e.g. `MG5_aMC_v3_5_15`) | yes |

**Example:**
```bash
python scripts/install_mg5.py ~/HEP_Tools \
  --url "https://launchpad.net/mg5amcnlo/3.0/3.7.x/+download/LTS_MG5aMC_v3.5.15.tgz" \
  --name MG5_aMC_v3_5_15
# Result: ~/HEP_Tools/MG5_aMC_v3_5_15/
```

**What the script does:**
1. Checks system dependencies (gcc, gfortran, libboost, python3, curl)
2. Downloads the MG5 tarball from the provided URL (follows redirects)
3. Extracts it
4. Runs MG5 `install pythia8`, `install lhapdf6`, `install delphes`
5. Verifies all components exist
6. Prints an environment report (current PATH / LD_LIBRARY_PATH + recommended exports) for the LLM to inspect and decide on
7. Returns the absolute path to `mg5_aMC`

**Exit codes:**
- `0` — success
- `1` — missing system dependency
- `2` — download failed
- `3` — MG5 install command failed
- `4` — verification failed (component missing after install)

---

## Integration with SKILL.md

### Phase -1: Input Collection

If the user does **not** provide `madgraph_path` (or presses Enter without a path), and no default exists from context, the skill should:

1. **Ask the user:**
   > "[1/9] MadGraph5 not found. Do you want me to automatically install it? (This will download ~31 MB, compile Pythia8, LHAPDF6, and Delphes — may take 20–40 minutes). Type `yes` to install, or provide an existing path:"

2. If the user answers `yes`:
   - Ask for install directory (default: `~/HEP_Tools`)
   - Fetch `https://launchpad.net/mg5amcnlo` and parse the HTML to find the LTS download URL and extracted directory name
   - Run `scripts/install_mg5.py {dir} --url {url} --name {name}`
   - Use the returned path as `madgraph_path`

### Phase 0: Environment Validation

If `config.auto_installed_mg5` is true in `run_config.json`, Phase 0 skips the existence check for `bin/mg5_aMC` (it was just verified by the installer). It still checks:
- `HEPTools/pythia8/` exists
- `HEPTools/lhapdf6_py3/` exists
- `Delphes/cards/` exists

If any of these are missing, report: "MG5 auto-install incomplete — {component} missing. Re-run installer or provide a manual path."

**Environment decision:** The script does **not** modify any environment variable. It prints a report showing the current `PATH` / `LD_LIBRARY_PATH` and the recommended exports. The LLM/skill should:
1. Inspect the printed report to see whether the MG5 paths are already in the current session
2. Inspect `~/.bashrc` to see whether the exports are already persisted there
3. Decide whether to set them for the current session and/or append them to `~/.bashrc` (with `# MG5_auto_install` markers)

---

## Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| `gfortran: command not found` | Missing Fortran compiler | `sudo apt-get install gfortran` |
| `boost/...: No such file` | Missing Boost headers | `sudo apt-get install libboost-all-dev` |
| `libpythia8.so: cannot open` | `LD_LIBRARY_PATH` not set | `export LD_LIBRARY_PATH={mg5path}/HEPTools/lib:$LD_LIBRARY_PATH` |
| `lhapdf-config: command not found` | `PATH` not set | `export PATH={mg5path}/HEPTools/bin:$PATH` |
| Pythia8 install hangs | Network timeout | Retry; check internet connection |
| Delphes install fails | ROOT not found | Delphes does not require full ROOT; MG5 bundles minimal ROOT libraries |

---

## Reference

- MG5 launchpad: https://launchpad.net/mg5amcnlo
- MG5 GitHub (dev): https://github.com/mg5amcnlo/mg5amcnlo
- LHAPDF6: https://lhapdf.hepforge.org/
- Pythia8: https://pythia.org/
- Delphes: https://github.com/delphes/delphes
