# Frozen algorithm replay revision

This is a separately named correction of the historical replay package.
The historical package is preserved in `../historical_replay/`.

Corrections: Phase 7 reads the original algorithm list and all four seed
families from packaged `analysis_lock.json`; it aborts without that lock and does
not draw replacement seeds. Feature CSV headers are restored before the
delivery audit, incorporating the repair needed in the original execution.
Phase 7 rejects a changed feature-schema hash, and Phase 9 refuses to accept
a changed production algorithm/threshold as a frozen-methodology replay.
If MC fluctuations change the apparent optimum, this entry point stops rather
than silently substituting a newly tuned strategy.
Package checksums have been recalculated for these changed sources.

Before event generation, the shell entry point invokes the installed-tool
identity checker against the packaged `toolchain_lock.json`. The invoking
Python environment must already match that lock. Phase 2 installs the same
recorded package versions into its new output environment, rather than
resolving the latest numerical libraries. Analysis and toolchain locks are
included in the package checksum list.

Use `bash replay.sh --check-only --output NEW_DIRECTORY` to run these
preflight checks without generation. A preflight PASS certifies only package
integrity and installed identities, not table reproduction.

This package regenerates events and therefore still has Monte Carlo variation.
It is not an exact rerun of the unavailable original event sample. The amended
full workflow has been statically checked and its seed resolver unit-tested;
it has not been run through a second complete generation during manuscript
revision. Use the compact numerical replay for the tested table reconstruction.

Full regeneration requires the recorded MG5/CutExperiment installations and
substantial computing/storage resources. The bulk event samples are excluded.
