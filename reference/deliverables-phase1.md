# Phase 1 Deliverables: Intake

Consumes: user answers only.

Must deliver:
- `results/run_config.json` on the selected execution target.
- In SSH/WSL2 mode, a local control copy plus the target copy.
- A verified MG5 installation on `madgraph_path` with `bin/mg5_aMC` or
  `bin/mg5`, `HEPTools/pythia8/`, `HEPTools/lhapdf6_py3/`, and
  `Delphes/cards/` present.
- Valid `execution`, `madgraph_path`, `workdir`, `process`,
  `process_validation`, `madspin`, `models`, beam energies,
  `run_configurations`, `luminosity`, `cutexperiment_path`, `delphes_card`,
  locked event counts, and optional preferences.

Manuscript dependency: process list, collider type, beam energies, luminosity,
detector card, model list, debug mode, algorithms, polarization, and user notes.

If missing or invalid: re-ask the responsible Phase 1 bilingual question. On
restart, discard prior physics/run fields and ask from `[1/9]`.
