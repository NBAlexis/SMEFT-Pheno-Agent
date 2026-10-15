"""Recompute Tables II-IV from compact recorded sufficient statistics.

This checks numerical fitting/inversion, not event generation, feature
extraction, classifier retraining or event-by-event scoring.
"""
import argparse
import hashlib
import json
import math
import platform
from pathlib import Path


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def signal_for_significance(background, significance):
    def z(s):
        return math.sqrt(max(2 * ((background + s) * math.log1p(s / background) - s), 0))
    low, high = 0.0, max(background, 1.0)
    while z(high) < significance:
        high *= 2
    for _ in range(150):
        mid = (low + high) / 2
        if z(mid) < significance:
            low = mid
        else:
            high = mid
    return (low + high) / 2


def bounds(a, b, sigma0, luminosity, significance):
    excess = signal_for_significance(sigma0 * luminosity, significance) / luminosity
    discriminant = math.sqrt(a * a + 4 * b * excess)
    return [(-a - discriminant) / (2 * b), (-a + discriminant) / (2 * b)]


def refit(points, sigma0):
    scale = max(abs(p["coefficient"]) for p in points)
    rows = [(p["coefficient"] / scale, p["cs_cut_x_pb"] - sigma0) for p in points]
    s2 = math.fsum(x ** 2 for x, _ in rows)
    s3 = math.fsum(x ** 3 for x, _ in rows)
    s4 = math.fsum(x ** 4 for x, _ in rows)
    t1 = math.fsum(x * y for x, y in rows)
    t2 = math.fsum(x ** 2 * y for x, y in rows)
    determinant = s2 * s4 - s3 * s3
    aa = (t1 * s4 - t2 * s3) / determinant
    bb = (t2 * s2 - t1 * s3) / determinant
    if bb < 0:
        aa, bb = t1 / s2, 0.0
    return aa / scale, bb / scale ** 2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("example", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    example = args.example.resolve()
    if args.output.exists() and any(args.output.iterdir()):
        parser.error("Output directory must be new or empty")
    args.output.mkdir(parents=True, exist_ok=True)
    original = read(example / "results/data/phase9/constraint_table.json")
    selection = read(example / "results/data/phase9/algorithm_selection.json")
    lock = read(example / "analysis_lock.json")
    phase7 = read(example / "results/data/phase7/algorithm_comparison.json")
    if lock["trained_algorithms"] != list(phase7["anchor"]) or lock["production_algorithm"] != selection["selected_algorithm"] or lock["threshold"] != selection["selected_threshold"]:
        raise ValueError("Frozen methodology and archived manifests disagree")
    schema_sha = hashlib.sha256((example / "results/data/phase7/feature_schema.json").read_bytes()).hexdigest()
    if schema_sha != lock["feature_schema_sha256"]:
        raise ValueError("Feature schema checksum differs")
    luminosity = original["luminosity_pb_inv"]
    results, differences = {}, []
    for op, stored in original["constraints"].items():
        fit = read(example / f"results/data/phase8/csfit_{op}_{selection['selected_algorithm']}.json")
        a, b = refit(fit["points"], fit["sigma0_after_cut_pb"])
        row = {"csfit_int": a, "csfit_np": b, "sigma0_after_cut_pb": fit["sigma0_after_cut_pb"]}
        for level in (2, 3, 5):
            values = bounds(a, b, fit["sigma0_after_cut_pb"], luminosity, level)
            row[f"S{level}"] = values
            for calculated, expected in zip(values, stored[f"S{level}"]):
                if not math.isclose(calculated, expected, rel_tol=1e-8, abs_tol=1e-22):
                    differences.append({"operator": op, "level": level, "expected": expected, "calculated": calculated})
        for field in ("csfit_int", "csfit_np"):
            if not math.isclose(row[field], fit[field], rel_tol=1e-8, abs_tol=1e-8):
                differences.append({"operator": op, "field": field, "expected": fit[field], "calculated": row[field]})
        results[op] = row
    table_ii = {}
    for algorithm, expected in selection["anchor_intervals_by_algorithm"].items():
        fit = read(example / f"results/data/phase8/csfit_o_1_{algorithm}.json")
        ends = bounds(fit["csfit_int"], fit["csfit_np"], fit["sigma0_after_cut_pb"], luminosity, 2)
        table_ii[algorithm] = {"threshold": expected["threshold"], "width": ends[1] - ends[0]}
        if not math.isclose(table_ii[algorithm]["width"], expected["width"], rel_tol=1e-8, abs_tol=1e-22):
            differences.append({"algorithm": algorithm, "field": "Table II width"})
    selected = min(table_ii, key=lambda a: table_ii[a]["width"])
    if selected != lock["production_algorithm"]:
        differences.append({"field": "production_algorithm", "calculated": selected})
    report = {"status": "FAIL" if differences else "PASS", "scope": "compact_numerical_replay_from_recorded_selected_counts_and_threshold_fits",
              "retrained_classifiers": False, "regenerated_events": False, "rescored_events": False,
              "platform": platform.platform(), "python_version": platform.python_version(),
              "relative_tolerance": 1e-8, "endpoint_absolute_tolerance_GeV_m4": 1e-22,
              "intervals_compared": 24, "fit_coefficients_compared": 16,
              "selection": {"algorithm": selected, "threshold": lock["threshold"]},
              "table_ii": table_ii, "constraints": results, "differences": differences}
    (args.output / "numerical_replay_validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k not in {"constraints", "table_ii"}}, indent=2))
    return 1 if differences else 0


if __name__ == "__main__":
    raise SystemExit(main())
