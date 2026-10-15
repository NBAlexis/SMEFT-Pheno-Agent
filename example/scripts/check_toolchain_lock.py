"""Capture installed tool identities or compare them to a frozen replay lock."""
import argparse
import hashlib
import importlib.metadata
import json
import platform
import re
import subprocess
from pathlib import Path


def file_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def capture(mg5, cutexperiment, detector_card=None):
    version_file = Path(mg5) / "VERSION"
    text = version_file.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"(?m)^\s*version\s*=\s*['\"]?([^\s'\"]+)", text)
    if not match:
        raise ValueError("Cannot parse MG5 VERSION file")
    commit = subprocess.check_output(["git", "-C", str(cutexperiment), "rev-parse", "HEAD"], text=True).strip()
    packages = {}
    for name in ("numpy", "scipy", "scikit-learn", "joblib", "matplotlib"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    result = {"schema_version": "1.0", "madgraph_version": match.group(1), "cutexperiment_commit": commit,
              "python_version": platform.python_version(), "packages": packages,
              "madgraph_version_file_sha256": file_sha(version_file)}
    if detector_card:
        result["detector_card_sha256"] = file_sha(detector_card)
    return result


def compare(expected, observed):
    mismatches = []
    for field in ("madgraph_version", "cutexperiment_commit", "python_version", "detector_card_sha256"):
        value = expected.get(field)
        if value is None:
            continue
        current = observed.get(field)
        # Legacy short commit IDs identify the same full commit if it starts with that ID.
        equal = isinstance(current, str) and current.startswith(value) if field == "cutexperiment_commit" else value == current
        if not equal:
            mismatches.append({"field": field, "expected": value, "observed": current})
    for name, value in expected.get("packages", {}).items():
        current = observed.get("packages", {}).get(name)
        if value != current:
            mismatches.append({"field": "packages." + name, "expected": value, "observed": current})
    return mismatches


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected", type=Path)
    parser.add_argument("--observed", type=Path)
    parser.add_argument("--mg5", type=Path)
    parser.add_argument("--cutexperiment", type=Path)
    parser.add_argument("--detector-card", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.observed:
        observed = json.loads(args.observed.read_text(encoding="utf-8-sig"))
    else:
        if not args.mg5 or not args.cutexperiment:
            parser.error("capture requires --mg5 and --cutexperiment")
        observed = capture(args.mg5, args.cutexperiment, args.detector_card)
    if args.expected:
        expected = json.loads(args.expected.read_text(encoding="utf-8-sig"))
        mismatches = compare(expected, observed)
        result = {"status": "FAIL" if mismatches else "PASS", "mismatches": mismatches, "observed": observed,
                  "scope": "installation identity; not cross-version physics certification"}
    else:
        result = observed
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 2 if result.get("status") == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
