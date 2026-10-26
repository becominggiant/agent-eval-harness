"""Scoring primitives: JSON validity, exact/fuzzy accuracy, cost."""
from __future__ import annotations
import json
from difflib import SequenceMatcher
from typing import Any

# USD per 1M tokens (input, output). Update as provider pricing changes.
PRICING = {"fixture": (0.0, 0.0), "gpt-4o-mini": (0.15, 0.60), "gpt-4o": (2.50, 10.00)}
FUZZY_THRESHOLD = 0.85
NUM_TOLERANCE = 0.01  # relative


def parse_json(raw: Any) -> tuple[bool, dict | None]:
    if isinstance(raw, dict):
        return True, raw
    try:
        obj = json.loads(raw)
        return isinstance(obj, dict), obj if isinstance(obj, dict) else None
    except (TypeError, ValueError):
        return False, None


def field_match(expected: Any, actual: Any) -> float:
    if isinstance(expected, (int, float)) and not isinstance(expected, bool):
        try:
            a = float(actual)
        except (TypeError, ValueError):
            return 0.0
        tol = max(abs(expected) * NUM_TOLERANCE, 0.011)
        return 1.0 if abs(a - expected) <= tol else 0.0
    e, a = str(expected).strip().lower(), str(actual).strip().lower()
    if e == a:
        return 1.0
    return 1.0 if SequenceMatcher(None, e, a).ratio() >= FUZZY_THRESHOLD else 0.0


def score_case(expected: dict, raw_output: Any) -> dict:
    valid, obj = parse_json(raw_output)
    if not valid:
        return {"json_valid": False, "field_accuracy": 0.0, "exact": False, "field_results": {}}
    results = {k: field_match(v, obj.get(k)) for k, v in expected.items()}
    acc = sum(results.values()) / len(results) if results else 1.0
    return {"json_valid": True, "field_accuracy": acc, "exact": acc == 1.0, "field_results": results}


def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    pin, pout = PRICING.get(model, (0.0, 0.0))
    return (prompt_tokens * pin + completion_tokens * pout) / 1_000_000
