# CutExperiment Reference

> **Contract priority**: Preserve the research objective and deliverables. Apply the technical-failure and `phase_fail` definitions in `SKILL.md`.

## Overview

CutExperiment is a Python package for analyzing collider event data in LHCO format. Within the SMEFT-ML workflow, its primary role is the **LHCO-to-CSV pipeline**: loading event files, applying selection cuts, extracting final-state particle features, and exporting structured CSV data for machine learning training.

## Installation

CutExperiment is expected to be available at `cutexperiment_path` (user-provided). The skill must ensure it is importable, typically by adding it to `PYTHONPATH` or installing via `pip install -e {cutexperiment_path}`.

## Core Modules

| Module | Key Imports | Purpose |
|--------|-------------|---------|
| `Interfaces.LHCOlympics` | `LoadLHCOlympics`, `SaveToLHCO` | Read/write `.lhco` files |
| `CutAndExport.CutEvent` | `CutEvents` | Apply selection cuts to event sets |
| `CutAndExport.CutFunctions` | `PhotonNumberCut`, `JetNumberCut`, `ETMissingCount` | Built-in cut predicates |
| `DataStructure.EventSet` | `EventSet` | Container for event collection |
| `DataStructure.Particles` | `ParticleType` | Enum for particle types (Jet, Photon, etc.) |

## LHCO-to-CSV Pipeline

This 5-step pipeline transforms raw MadGraph/Delphes output into ML-ready feature vectors.

### Step 1: Analyze Final State

From `process_name`, determine the expected final-state particles.

| Process Example | Final State | Visible Particles | Invisible (Missing) |
|-----------------|-------------|-------------------|---------------------|
| `mu+ mu- > a a a` | 3 photons | 3 photons | none |
| `mu+ mu- > vl vl~ a a` | 2 neutrinos + 2 photons | 2 photons | 1 missing momentum |
| `p p > l+ l- j j` | 2 leptons + 2 jets | 2 leptons + 2 jets | none |

**Rule:** Parse one process string to count each particle type in the final
state (right-hand side of `>`). Neutrinos (`vl`, `vl~`, `vm`, `vm~`, `vt`,
`vt~`) are treated as invisible; their combined momentum becomes the missing
momentum vector.

MG5 order parameters (`QED=`, `QCD=`, `NP=`) must be stripped before parsing.

```python
def parse_final_state(process_name):
    """Parse MG5 process string to identify visible and invisible final-state particles.

    Returns:
        visible_types: list of ParticleType enums for visible final-state particles
        has_neutrinos: bool, True if neutrinos are present in final state
    """
    from DataStructure.Particles import ParticleType

    # Strip MG5 order parameters
    proc = process_name.split("QED=")[0].split("QCD=")[0].split("NP=")[0].strip()
    # Extract final state (right of '>')
    final_state = proc.split(">")[-1].strip()
    tokens = final_state.split()

    # Particle type mapping
    type_map = {
        "a": ParticleType.Photon,
        "j": ParticleType.Jet,
        "l+": ParticleType.Electron,  # generic lepton+
        "l-": ParticleType.Electron,  # generic lepton-
        "e+": ParticleType.Electron,
        "e-": ParticleType.Electron,
        "mu+": ParticleType.Muon,
        "mu-": ParticleType.Muon,
    }

    visible_types = []
    has_neutrinos = False
    for tok in tokens:
        if tok in ("vl", "vl~", "vm", "vm~", "vt", "vt~"):
            has_neutrinos = True
        elif tok in type_map:
            visible_types.append(type_map[tok])
    return visible_types, has_neutrinos
```

### Step 2: Load and Clean

Load the `.lhco` file and apply the default multiplicity cut.

```python
from Interfaces.LHCOlympics import LoadLHCOlympics
from CutAndExport.CutEvent import CutEvents
from CutAndExport.CutFunctions import PhotonNumberCut, JetNumberCut

events = LoadLHCOlympics(lhco_file_path)
loaded_event_count = events.GetEventCount()

# Default cut: retain only events with at least the required number
# of final-state particles. Example for 3-photon final state:
photon_cut = PhotonNumberCut(1, [3])  # at least 3 photons
CutEvents(events, photon_cut)
surviving_event_count = events.GetEventCount()
```

**Default behavior:** If the user does not specify custom cuts, always apply the multiplicity cut matching the final state.

**Event-count rule:** `loaded_event_count` must be taken immediately after
`LoadLHCOlympics`. It is the denominator for total selection efficiencies and
cut cross-sections. `surviving_event_count` is the count after final-state
multiplicity cuts. Do not use banner event counts for either value; MG5 banners
may report the requested event target rather than the actual LHCO events.

### Step 3: Select Final-State Particles

After cleaning, select the relevant particles from each surviving event.

**Default selection rule:** Sort the visible final-state particles by energy (descending) and take the first `n`, where `n` is the expected count from Step 1.

Example for 3 photons:
```python
selected_photons = sorted(photons, key=lambda p: p.momentum.values[0], reverse=True)[:3]
```

### Step 4: Assemble Four-Momenta

Extract the four-momentum `(E, px, py, pz)` for each selected particle and concatenate.

If the final state includes neutrinos (invisible particles), append the missing momentum's `(px, py)` components after the visible particles.

**3-photon example (no neutrinos):**
```
[E1, px1, py1, pz1, E2, px2, py2, pz2, E3, px3, py3, pz3]
```

**2-photon + 2-neutrino example:**
```
[E1, px1, py1, pz1, E2, px2, py2, pz2, miss_px, miss_py]
```

### Step 5: Export to CSV

Each event becomes one row in a 2D NumPy array, saved as CSV.

Example for 9,850 loaded LHCO events where 9,000 survive the cut:
- Output shape: `9000 x 12` (3 photons x 4 components each)
- CSV header: none (plain numeric data)
- Row format: `e1, p1x, p1y, p1z, e2, p2x, p2y, p2z, e3, p3x, p3y, p3z`

```python
import numpy as np
np.savetxt(output_csv_path, feature_array, delimiter=',')
```

## Common Cut Functions

| Function | Signature | Meaning |
|----------|-----------|---------|
| `PhotonNumberCut` | `(mode, [min_count])` | `mode=1`: at least `min_count` photons |
| `JetNumberCut` | `(mode, [min_count])` | `mode=1`: at least `min_count` jets |
| `ETMissingCount` | `(mode, [min_ET])` | Missing transverse energy cut |

## EventSet Operations

| Method | Returns | Purpose |
|--------|---------|---------|
| `events.GetEventCount()` | `int` | Number of events in the set |
| `events.events` | `list[EventSample]` | Iterate over individual events |
| `sample.particles` | `list[Particle]` | Iterate over particles in an event |
| `particle.particleType` | `ParticleType` | Type enum (Jet, Photon, etc.) |
| `particle.momentum.values` | `[E, px, py, pz]` | Four-momentum array |
| `particle.index` | `int` | Particle index in the event |

## Validation Checklist

Before running the pipeline:
- [ ] `cutexperiment_path` exists and CutExperiment is importable
- [ ] LHCO file exists and is non-empty
- [ ] Final-state particle types are correctly parsed from `process_name`
- [ ] Multiplicity cut matches the expected final state

After the pipeline:
- [ ] Output CSV file exists and is non-empty
- [ ] Row count equals `events.GetEventCount()` after cuts
- [ ] Column count matches `4 * n_visible + 2 * n_missing_xy`
- [ ] `loaded_event_count` was recorded before cuts
- [ ] Total efficiencies use `loaded_event_count`, not requested `nevents`
