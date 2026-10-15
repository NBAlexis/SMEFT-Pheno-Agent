# Local EPJC revision candidate

Base repository commit: `5d0f1d992589c4acc71c7d469029536366c639ff`.
Local proposed version: `0.43-rc1`. No release tag, remote upload or DOI was
created by this preparation. Confirm creator order, affiliations, licence and
final version before release; ORCIDs are omitted because none was supplied.

The reference example comes from the September 2026 GLM/ZCode run. Historical
JSON and session code are preserved byte-for-byte. Supplementary locks,
diagnostics and comparison reports are separately named. The historical full
regeneration changed its algorithm draw and does not demonstrate exact replay.
The compact numerical replay and tests state their narrower input/output scope.

Before submission:

1. Upload the reviewed files and synchronize the GitHub mirror.
2. Commit the local changes; create the final immutable tag/release.
3. Connect/enable the repository in Zenodo, then archive that release.
4. Inspect creators, licence, files and version DOI.
   Replace the local-candidate description in `.zenodo.json` and `CITATION.cff`
   with the actual release description/version and DOI; their present wording
   is intentionally not a claim of publication.
5. Replace the explicitly marked release/DOI fields in the manuscript and
   response letter. Do not submit them while they still say PENDING.

No bulk LHE, ROOT, HEPMC, LHCO or feature/score CSV data are included. Full event
regeneration uses the archived generation configs and recorded external tools;
it is a statistical regeneration, not a bitwise reproduction of absent samples.
