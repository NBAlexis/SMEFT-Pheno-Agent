# Phase 1 Deliverables: Intake

Consumes: user answers only.

Must deliver:
- `results/run_config.json` on the selected execution target.
- `results/research_contract.json`, with the immutable scientific objective and
  a valid canonical SHA-256 hash, plus the frozen deliverables-template hash.
- `results/deliverables_contract.json`, bound to the research-objective hash and
  containing the immutable deliverable expansion template and template hash.
- `results/contract_lock.json`, binding the exact research and deliverables
  contract hashes as one immutable set.
- The research contract contains directory-tree SHA-256 identities for every
  selected UFO model and a file SHA-256 identity for the selected Delphes card.
- In SSH/WSL2 mode, identical local-control and target copies of all four JSON
  files.
- A verified MG5 installation on `madgraph_path` with `bin/mg5_aMC` or
  `bin/mg5`, `HEPTools/pythia8/`, `HEPTools/lhapdf6_py3/`, and
  `Delphes/cards/` present.
- Valid `execution`, `madgraph_path`, `workdir`, `process`,
  `process_validation`, `madspin`, `models`, beam energies,
  `run_configurations`, `luminosity`, `cutexperiment_path`, `delphes_card`,
  locked event counts, and optional preferences.

Manuscript dependency: process list, collider type, beam energies, luminosity,
detector card, model list, debug mode, algorithms, polarization, and user notes.

If an input is missing or invalid: re-ask the responsible Phase 1 bilingual
question. If contract initialization fails, repair the configuration or contract
write/sync problem; never overwrite a different existing contract. On restart,
discard prior physics/run fields and ask from `[1/9]`, then create new contracts
for the restarted study.
