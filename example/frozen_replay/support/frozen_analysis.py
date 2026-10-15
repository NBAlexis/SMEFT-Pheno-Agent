"""Resolve research randomness or load a mandatory recorded replay lock."""
import json
import secrets


def resolve_randomness(pool, lock_path=None, count=3):
    if not lock_path:
        import random
        seed = secrets.randbits(64)
        chosen = list(pool)
        random.Random(seed).shuffle(chosen)
        chosen = chosen[:count]
        return {"trained_algorithms": chosen, "algorithm_selection_seed": seed,
                "split_seed": secrets.randbits(31), "train_cap_seed": secrets.randbits(31),
                "implementation_seeds": {a: secrets.randbits(31) for a in chosen}, "mode": "new_research"}
    with open(lock_path, encoding="utf-8-sig") as handle:
        lock = json.load(handle)
    required = {"trained_algorithms", "algorithm_selection_seed", "split_seed", "train_cap_seed", "implementation_seeds"}
    missing = sorted(required - lock.keys())
    if missing:
        raise ValueError("Incomplete frozen analysis lock: " + ", ".join(missing))
    chosen = lock["trained_algorithms"]
    if not chosen or len(chosen) != len(set(chosen)):
        raise ValueError("Frozen algorithm list is empty or contains duplicates")
    unknown = set(chosen) - set(pool)
    if unknown:
        raise ValueError("Frozen algorithms unavailable in this implementation: " + ", ".join(sorted(unknown)))
    for name in chosen:
        if not isinstance(lock["implementation_seeds"].get(name), int):
            raise ValueError("Missing implementation seed for " + name)
    for field in ("algorithm_selection_seed", "split_seed", "train_cap_seed"):
        if not isinstance(lock[field], int):
            raise ValueError("Invalid integer seed: " + field)
    return dict(lock, mode="frozen_replay")


def compare_methodology(expected, observed):
    """Fail closed on a changed replay decision; do not silently adapt it."""
    fields = ("trained_algorithms", "algorithm_selection_seed", "split_seed", "implementation_seeds",
              "train_cap_seed", "feature_schema_sha256", "production_algorithm", "threshold")
    return [{"field": field, "expected": expected.get(field), "observed": observed.get(field)}
            for field in fields if expected.get(field) != observed.get(field)]
