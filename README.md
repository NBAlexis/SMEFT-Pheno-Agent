# Automated SMEFT ML Phenomenology

Reusable skill for automated SMEFT collider phenomenology studies with MadGraph5,
Delphes/root2lhco processing, CutExperiment feature extraction, ML event
selection, coefficient scans, expected Wilson-coefficient constraints, and a
publication-style manuscript.

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
- Execution can be local, SSH remote, or WSL2. In SSH/WSL2 mode, paths are paths
  on the target Linux environment, not Windows host paths.
- Restart/retest requests reset the physics/run fields and begin again at
  `[1/9]`.
- After `run_config.json` is written, Phases 2-11 run without user interaction
  unless an unrecoverable error, documented red flag, or explicit user stop
  occurs.
- Event counts are locked in `run_config.json`; later phases must not resize
  them for speed.
- Actual LHCO counts must come from CutExperiment
  `LoadLHCOlympics(...).GetEventCount()`. Banner event counts and planned
  `nevents` are not valid efficiency denominators.
- Event-count recovery, LHCO merging, and merged cross-section weighting are
  centralized in `reference/event-count-recovery.md`.
- Long MadGraph/Delphes runtimes are normal. Hours, days, weeks, or months are
  not stop conditions; use durable execution and status files instead of asking
  whether to continue or reducing statistics.
- On Windows hosts, use WSL2 or SSH for long MG5/Delphes jobs instead of native
  Windows local background execution.
- `results/workflow.log` is mandatory from Phase 2 onward and doubles as the
  bug-report log. Do not use heredoc `EOF` or shell `!` clobber patterns to
  create workflow files.

## Important Files

- `SKILL.md` - trigger metadata and top-level operating contracts
- `reference/phase1-input-collection.md` - intake state machine
- `reference/phase2-env.md` - environment validation
- `reference/phase3-validation.md` - operator loop completion contract
- `scripts/install_mg5.py` - MG5 installer after the agent resolves the dynamic
  Launchpad URL
- `scripts/install_cutexperiment.py` - CutExperiment clone/validation helper
- `scripts/remote_exec.py` - local/SSH/WSL2 command execution helper
- `scripts/durable_exec.py` - start/status helper for jobs that may outlive the
  current agent session
- `scripts/workflow_logger.py` - JSONL phase/step logger and log bootstrap
- `scripts/load_run_config.py` - run configuration loader and event-count lock
  validator
- `scripts/run_mg5_config.py` - config-driven MG5 attempt runner
- `scripts/count_lhco_events.py` - CutExperiment-backed LHCO event counter
- `scripts/merge_lhco.py` - LHCO merge helper with weighted cross-sections
- `scripts/recover_lhco_count.py` - event-count recovery orchestrator
- `scripts/audit_expected_outputs.py` - manifest-driven Phase 11 audit helper

## Runtime Inputs

Phase 1 collects:

- MadGraph5 path or auto-install request
- Execution target inferred from the MadGraph5 answer: local path,
  `ssh user@host:/path/to/MG5`, or `wsl2:/path/to/MG5`
- Work directory
- Physics process
- UFO model list
- Energy list
- Luminosity list
- CutExperiment path or clone request
- Delphes card name or absolute path
- Optional preferences such as debug mode, polarization, algorithms, focused
  operators, and manuscript preferences

## Notes

The MadGraph5 download URL is not hardcoded. During auto-install, the agent
fetches Launchpad and resolves the current recommended LTS tarball before
calling `scripts/install_mg5.py`.
