from __future__ import annotations

import math
import re
from collections import Counter
from typing import Iterable


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", text.lower())


def word_error_rate(reference: str, hypothesis: str) -> float:
    ref = _tokens(reference)
    hyp = _tokens(hypothesis)

    if not ref:
        return 0.0 if not hyp else 1.0

    previous = list(range(len(hyp) + 1))
    for i, ref_word in enumerate(ref, start=1):
        current = [i]
        for j, hyp_word in enumerate(hyp, start=1):
            substitution = previous[j - 1] + (ref_word != hyp_word)
            insertion = current[j - 1] + 1
            deletion = previous[j] + 1
            current.append(min(substitution, insertion, deletion))
        previous = current

    return previous[-1] / len(ref)


def transcript_accuracy(reference: str, hypothesis: str) -> float:
    return round(max(0.0, 1.0 - word_error_rate(reference, hypothesis)) * 100, 2)


def percentile(values: Iterable[float], q: float) -> float:
    values = sorted(float(value) for value in values)
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]

    position = (len(values) - 1) * q
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return values[lower]

    weight = position - lower
    return values[lower] * (1 - weight) + values[upper] * weight


def summarize(rows: list[dict]) -> dict:
    if not rows:
        return {}

    latencies = [row["response_latency_ms"] for row in rows]
    turn_latencies = [row["end_of_turn_ms"] for row in rows]
    wers = [row["wer"] for row in rows]
    success = [bool(row["task_success"]) for row in rows]
    costs = [float(row["estimated_cost_usd"]) for row in rows]

    failure_counts = Counter(
        row.get("failure_stage", "none") for row in rows
    )

    return {
        "runs": len(rows),
        "mean_wer": round(sum(wers) / len(wers), 4),
        "p50_response_latency_ms": round(percentile(latencies, 0.50), 1),
        "p95_response_latency_ms": round(percentile(latencies, 0.95), 1),
        "p50_end_of_turn_ms": round(percentile(turn_latencies, 0.50), 1),
        "p95_end_of_turn_ms": round(percentile(turn_latencies, 0.95), 1),
        "task_success_rate": round(sum(success) / len(success) * 100, 2),
        "total_estimated_cost_usd": round(sum(costs), 4),
        "failure_stage_counts": dict(failure_counts),
    }
