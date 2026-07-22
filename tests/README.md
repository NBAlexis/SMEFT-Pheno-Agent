# Tests

Run the fast default suite from the repository root:

```powershell
python -m unittest discover -s tests -v
```

The full local suite includes a short real MadGraph smoke test. It reads
`tests/external_tools.json` by default:

```json
{
  "wsl_distro": "Ubuntu-22.04",
  "madgraph_path": "wsl2:/home/nbalexis/MG5_aMC_v3_5_6",
  "cutexperiment_path": "wsl2:/home/nbalexis/CutExp/CutExperiment"
}
```

The smoke test only runs MG5 process generation for `e+ e- > mu+ mu-`. It does
not launch event generation, Pythia, Delphes, or long numerical scans.

You can override the config without editing the file:

```powershell
$env:SMEFT_EXTERNAL_TOOLS_CONFIG='E:\path\to\external_tools.json'
python -m unittest discover -s tests -v
```

Or override individual values:

```powershell
$env:SMEFT_MG5_WSL_DISTRO='Ubuntu-22.04'
$env:SMEFT_MG5_WSL_PATH='/home/nbalexis/MG5_aMC_v3_5_6'
$env:SMEFT_CUTEXPERIMENT_WSL_PATH='/home/nbalexis/CutExp/CutExperiment'
python -m unittest discover -s tests -v
```

If neither the config nor environment variables are available, real external
tool smoke tests are skipped while pure Python mechanism tests still run.
