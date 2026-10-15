#!/usr/bin/env bash
# One-command numerical replay of phases 2-9 of this study.
# Usage: ./replay.sh [--output DIR] [--resume]
#   --output DIR   output root (default: ./replayed-results next to this script)
#   --resume       allow reusing a previous output whose step checksums match
set -euo pipefail
PKG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT=""
RESUME=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --output) OUTPUT="$2"; shift 2 ;;
    --resume) RESUME=1; shift ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done
[[ -z "$OUTPUT" ]] && OUTPUT="$PKG_DIR/replayed-results"
if [[ -e "$OUTPUT" ]]; then
  if [[ "$RESUME" != "1" ]]; then
    echo "refusing to overwrite non-empty output directory: $OUTPUT" >&2
    exit 3
  fi
  if [[ ! -f "$OUTPUT/.replay_state.json" ]]; then
    echo "cannot resume: $OUTPUT/.replay_state.json missing" >&2
    exit 3
  fi
fi
PYTHON="${SMEFT_PYTHON:-/mnt/e/SMEFT-Pheno-Agent-GLM-test/venv/bin/python}"
command -v sha256sum >/dev/null
[[ -x "$PYTHON" ]] || { echo "python not found: $PYTHON (set SMEFT_PYTHON)" >&2; exit 4; }
MG5_PATH="$( "$PYTHON" -c 'import json,sys; print(json.load(open("'"$PKG_DIR"'/run_config.json"))["madgraph_path"])' )"
[[ -x "$MG5_PATH/bin/mg5_aMC" ]] || { echo "MadGraph not found: $MG5_PATH" >&2; exit 4; }
"$PYTHON" - "$PKG_DIR" <<'PYEOF'
import hashlib, json, os, sys
pkg = sys.argv[1]
mani = json.load(open(os.path.join(pkg, "replay_manifest.json"), encoding="utf-8"))
bad = []
for rel, expected in mani["package_sha256"].items():
    path = os.path.join(pkg, rel)
    if not os.path.isfile(path) or hashlib.sha256(open(path, "rb").read()).hexdigest() != expected:
        bad.append(rel)
if bad:
    print("package checksum mismatch: " + ", ".join(bad[:5]), file=sys.stderr)
    sys.exit(5)
print("package checksums OK:", len(mani["package_sha256"]), "files")
PYEOF
mkdir -p "$OUTPUT/results" "$OUTPUT/.smeft-skill/scripts"          "$OUTPUT/.smeft-skill/reference" "$OUTPUT/.smeft-skill/project"          "$OUTPUT/replay_logs"
for name in run_config.json research_contract.json deliverables_contract.json contract_lock.json; do
  [[ -f "$OUTPUT/results/$name" ]] || cp "$PKG_DIR/$name" "$OUTPUT/results/$name"
done
cp "$PKG_DIR"/support/*.py "$OUTPUT/.smeft-skill/scripts/"
cp "$PKG_DIR"/support/reference/* "$OUTPUT/.smeft-skill/reference/"
cp "$PKG_DIR"/support/project/*.py "$OUTPUT/.smeft-skill/project/" 2>/dev/null || true
export SMEFT_WORKDIR="$OUTPUT"
STATE="$OUTPUT/.replay_state.json"
"$PYTHON" - "$STATE" <<'PYEOF'
import json, os, sys
path = sys.argv[1]
state = {"completed": {}}
if os.path.isfile(path):
    state = json.load(open(path, encoding="utf-8"))
else:
    json.dump(state, open(path, "w", encoding="utf-8"), indent=1)
PYEOF
for entry in 2 3 4 5 6 7 8 9; do
  driver="$("$PYTHON" -c 'import json;print([s for s in json.load(open("'"$PKG_DIR"'/replay_manifest.json"))["steps"] if s["phase"]=="'"$entry"'"][0]["command"][1])')"
  DONE="$("$PYTHON" - "$STATE" "$PKG_DIR/$driver" <<'PYEOF'
import hashlib, json, sys
state_path, path = sys.argv[1], sys.argv[2]
state = json.load(open(state_path, encoding="utf-8"))
rec = (state.get("completed") or {}).get(path)
if (rec and rec.get("returncode") == 0
        and hashlib.sha256(open(path, "rb").read()).hexdigest() == rec["sha256"]):
    print("yes")
else:
    print("no")
PYEOF
)"
  if [[ "$DONE" == "yes" ]]; then
    echo "== phase $entry already complete (checksums match), skipping"
    continue
  fi
  echo "== replaying phase $entry: $driver"
  set +e
  if [[ "$driver" == *.sh ]]; then
    (cd "$OUTPUT" && bash "$PKG_DIR/$driver"        > "$OUTPUT/replay_logs/phase${entry}.out"        2> "$OUTPUT/replay_logs/phase${entry}.err")
  else
    (cd "$OUTPUT" && "$PYTHON" "$PKG_DIR/$driver"        > "$OUTPUT/replay_logs/phase${entry}.out"        2> "$OUTPUT/replay_logs/phase${entry}.err")
  fi
  rc=$?
  set -e
  "$PYTHON" - "$STATE" "$PKG_DIR/$driver" "$rc" <<'PYEOF'
import hashlib, json, sys
state_path, path, rc = sys.argv[1], sys.argv[2], int(sys.argv[3])
state = json.load(open(state_path, encoding="utf-8"))
state["completed"][path] = {
    "sha256": hashlib.sha256(open(path, "rb").read()).hexdigest(),
    "returncode": rc,
}
json.dump(state, open(state_path, "w", encoding="utf-8"), indent=1)
PYEOF
  if [[ "$rc" != "0" ]]; then
    recovery="steps/phase${entry}_recovery.py"
    if [[ -f "$PKG_DIR/$recovery" ]]; then
      echo "== phase $entry failed (rc=$rc); running recovery companion: $recovery"
      set +e
      (cd "$OUTPUT" && "$PYTHON" "$PKG_DIR/$recovery"          >> "$OUTPUT/replay_logs/phase${entry}.out"          2>> "$OUTPUT/replay_logs/phase${entry}.err")
      rrc=$?
      set -e
      if [[ "$rrc" == "0" ]]; then
        echo "== recovery companion completed phase $entry; continuing"
        rc=0
      else
        echo "recovery companion for phase $entry failed with rc=$rrc" >&2
        exit 6
      fi
    else
      echo "phase $entry failed with rc=$rc; see $OUTPUT/replay_logs/phase${entry}.err" >&2
      exit 6
    fi
  fi
  "$PYTHON" - "$STATE" "$PKG_DIR/$driver" "$rc" <<'PYEOF'
import hashlib, json, sys
state_path, path, rc = sys.argv[1], sys.argv[2], int(sys.argv[3])
state = json.load(open(state_path, encoding="utf-8"))
state["completed"][path] = {
    "sha256": hashlib.sha256(open(path, "rb").read()).hexdigest(),
    "returncode": rc,
}
json.dump(state, open(state_path, "w", encoding="utf-8"), indent=1)
PYEOF
done
echo "replay complete; outputs under $OUTPUT (per-step logs in replay_logs/)"
