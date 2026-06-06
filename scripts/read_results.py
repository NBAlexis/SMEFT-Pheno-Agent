#!/usr/bin/env python3
"""Read result files produced by the SMEFT-ML workflow.

All phases write structured JSON output to results/{run_dir}/data/phase{ N }/.
This module provides typed helper functions so downstream code never needs to
reimplement path construction or field parsing.

Usage:
    from scripts.read_results import read_anchor, read_sm_baseline
    anchor = read_anchor("/path/to/workdir")
    baseline = read_sm_baseline("/path/to/workdir", run_dir="E10_L1000")
"""

import json
import os
from typing import Any, Dict, Optional


def _result_path(workdir: str, run_dir: Optional[str], rel_path: str) -> str:
    """Construct absolute path: workdir/results/[run_dir/]rel_path."""
    if run_dir:
        return os.path.join(workdir, "results", run_dir, rel_path)
    return os.path.join(workdir, "results", rel_path)


def _load_json(path: str) -> Any:
    """Load JSON file, raising FileNotFoundError with the path if missing."""
    with open(path, "r") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Phase 3
# ---------------------------------------------------------------------------

def read_operator_claims(workdir: str, run_dir: Optional[str] = None) -> Dict[str, Any]:
    """Read operator_claims.json: {global_idx: {model, anoinput_idx, name}}."""
    return _load_json(_result_path(workdir, run_dir, "data/phase3/operator_claims.json"))


def read_cross_sections(workdir: str, run_dir: Optional[str] = None) -> Dict[str, Any]:
    """Read cross_sections.json: {fi: {sigma, c_default, model, global_idx}}."""
    return _load_json(_result_path(workdir, run_dir, "data/phase3/cross_sections.json"))


def read_anchor(workdir: str, run_dir: Optional[str] = None) -> Dict[str, Any]:
    """Read anchor.json: {global_idx, model, anoinput_idx, name}."""
    return _load_json(_result_path(workdir, run_dir, "data/phase3/anchor.json"))


# ---------------------------------------------------------------------------
# Phase 4
# ---------------------------------------------------------------------------

def read_coefficient_ranges(workdir: str, run_dir: Optional[str] = None) -> Dict[str, Any]:
    """Read coefficient_ranges.json: per-operator scan ranges."""
    return _load_json(_result_path(workdir, run_dir, "data/phase4/coefficient_ranges.json"))


def read_sm_baseline(workdir: str, run_dir: Optional[str] = None) -> Dict[str, Any]:
    """Read sm_baseline.json: {cs_sm, n_scan, L_prime, anchor_model, range_scope}."""
    return _load_json(_result_path(workdir, run_dir, "data/phase4/sm_baseline.json"))


# ---------------------------------------------------------------------------
# Phase 7
# ---------------------------------------------------------------------------

def read_algorithm_comparison(workdir: str, run_dir: Optional[str] = None) -> Dict[str, Any]:
    """Read algorithm_comparison.json: {anchor: {alg: {auc, algorithm_path}}, ...}."""
    return _load_json(_result_path(workdir, run_dir, "data/phase7/algorithm_comparison.json"))


# ---------------------------------------------------------------------------
# Phase 8
# ---------------------------------------------------------------------------

def read_threshold_optimization(workdir: str, run_dir: Optional[str] = None) -> Dict[str, Any]:
    """Read threshold_optimization.json: per-algorithm optimal thresholds."""
    return _load_json(_result_path(workdir, run_dir, "data/phase8/threshold_optimization.json"))


def read_csfit(workdir: str, operator: str, algorithm: str,
               run_dir: Optional[str] = None) -> Dict[str, Any]:
    """Read csfit_{operator}_{algorithm}.json: quadratic fit coefficients."""
    fname = f"data/phase8/csfit_{operator}_{algorithm}.json"
    return _load_json(_result_path(workdir, run_dir, fname))


# ---------------------------------------------------------------------------
# Phase 9
# ---------------------------------------------------------------------------

def read_constraint_table(workdir: str, run_dir: Optional[str] = None) -> Dict[str, Any]:
    """Read constraint_table.json: best-algorithm constraints for all operators."""
    return _load_json(_result_path(workdir, run_dir, "data/phase9/constraint_table.json"))


def read_algorithm_selection(workdir: str, run_dir: Optional[str] = None) -> Dict[str, Any]:
    """Read algorithm_selection.json: per-operator interval comparison across algorithms."""
    return _load_json(_result_path(workdir, run_dir, "data/phase9/algorithm_selection.json"))


# ---------------------------------------------------------------------------
# Convenience accessors for single fields (never reimplement inline)
# ---------------------------------------------------------------------------

def get_operator_c_scan(workdir: str, operator: str, run_dir: Optional[str] = None) -> float:
    """Return one operator's positive scan bound, e.g. operator='o_1'."""
    data = read_coefficient_ranges(workdir, run_dir)
    return float(data["operators"][operator]["c_scan"])


def get_c_scan(workdir: str, run_dir: Optional[str] = None) -> float:
    """Return legacy global c_scan only for old result folders."""
    data = read_coefficient_ranges(workdir, run_dir)
    if "global" not in data:
        raise ValueError("coefficient_ranges.json is per-operator; use get_operator_c_scan(..., operator='o_N')")
    return float(data["global"][1])


def get_cs_sm(workdir: str, run_dir: Optional[str] = None) -> float:
    """Return SM baseline cross-section in pb."""
    data = read_sm_baseline(workdir, run_dir)
    return float(data["cs_sm"])


def get_nev_scan(workdir: str, run_dir: Optional[str] = None) -> int:
    """Return scan event count (n_scan)."""
    data = read_sm_baseline(workdir, run_dir)
    return int(data["n_scan"])


def get_anchor_operator(workdir: str, run_dir: Optional[str] = None) -> str:
    """Return anchor operator name (e.g. 'fS0')."""
    data = read_anchor(workdir, run_dir)
    return str(data["name"])


def get_anchor_model(workdir: str, run_dir: Optional[str] = None) -> str:
    """Return anchor source model name (e.g. 'AQGCm_UFO')."""
    data = read_anchor(workdir, run_dir)
    return str(data["model"])
