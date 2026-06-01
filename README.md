# Automated SMEFT ML Phenomenology

Reusable skill for automated SMEFT collider phenomenology studies with MadGraph5,
Delphes/root2lhco processing, CutExperiment feature extraction, ML event
selection, coefficient scans, expected Wilson-coefficient constraints, and a
publication-style report.

## Agent Contract

This skill is intended to be usable across agents. The controlling behavior is in
`SKILL.md` and the phase references under `reference/`.

Key contracts:

- Phase 1 is the only interactive stage.
- Phase 1 asks one bilingual plain-text question at a time.
- Phase 1 must not use AskQuestion, askquestion, AskUserQuestion, radio buttons,
  or multiple-choice UI tools.
- `madgraph_path` and `cutexperiment_path` must always be asked, but known paths
  may be shown as suggested defaults.
- Restart/retest requests reset the physics/run fields and begin again at
  `[1/9]`.
- After `run_config.json` is written, Phases 2-11 run without user interaction
  unless an unrecoverable error, documented red flag, or explicit user stop
  occurs.
- Event counts are locked in `run_config.json`; later phases must not resize
  them for speed.

## Important Files

- `SKILL.md` - trigger metadata and top-level operating contracts
- `reference/phase1-input-collection.md` - intake state machine
- `reference/phase2-env.md` - environment validation
- `reference/phase3-validation.md` - operator loop completion contract
- `scripts/install_mg5.py` - MG5 installer after the agent resolves the dynamic
  Launchpad URL
- `scripts/install_cutexperiment.py` - CutExperiment clone/validation helper
- `scripts/load_run_config.py` - run configuration loader and event-count lock
  validator

## Runtime Inputs

Phase 1 collects:

- MadGraph5 path or auto-install request
- Work directory
- Physics process
- UFO model list
- Energy list
- Luminosity list
- CutExperiment path or clone request
- Delphes card name or absolute path
- Optional preferences such as debug mode, polarization, algorithms, focused
  operators, and report preferences

## Notes

The MadGraph5 download URL is not hardcoded. During auto-install, the agent
fetches Launchpad and resolves the current recommended LTS tarball before
calling `scripts/install_mg5.py`.
