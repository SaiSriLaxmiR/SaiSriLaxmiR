"""Run Auri benchmark scenarios and write raw JSONL results.

Modes:
- simulate: deterministic, credential-free pipeline validation. Results are
  explicitly labeled simulated and must not be used as production claims.
- provider: execute configured ASR providers against real audio files.

The full suite contains 240 scenarios x 3 noise profiles. Running all three
configured stacks yields up to 2,160 stack-condition evaluations.
"""

from __future__ import annotations

import argparse
import json
import time
from hashlib import sha256
from pathlib import Path

from benchmark.generate_suite import build_suite
from benchmark.metrics import word_error_rate


def _stable_int(seed: str, low: int, high: int) -> int:
    digest = sha256(seed.encode("utf-8")).hexdigest()
    return low + int(digest[:8], 16) % (high - low + 1)


def _simulate_transcript(
    reference: str,
    stack_id: str,
    noise: str,
    scenario_id: str,
) -> str:
    """Introduce deterministic token drops for pipeline-testing only."""
    words = reference.split()
    if not words:
        return reference

    base_drop = {"clean": 0, "cafe": 1, "street": 2}[noise]
    variation = _stable_int(
        f"{scenario_id}|{stack_id}|{noise}|drop",
        0,
        2,
    )
    drop_count = min(len(words) // 4, base_drop + variation)

    if drop_count <= 0:
        return reference

    indices = []
    for i in range(drop_count):
        indices.append(
            _stable_int(
                f"{scenario_id}|{stack_id}|{noise}|{i}",
                0,
                len(words) - 1,
            )
        )
    return " ".join(
        word for index, word in enumerate(words) if index not in set(indices)
    )


def simulate_row(
    scenario: dict,
    stack: dict,
    noise: str,
) -> dict:
    reference = scenario["reference_transcript"]
    hypothesis = _simulate_transcript(
        reference,
        stack["id"],
        noise,
        scenario["scenario_id"],
    )
    wer = word_error_rate(reference, hypothesis)

    response_latency = _stable_int(
        f'{scenario["scenario_id"]}|{stack["id"]}|{noise}|latency',
        420,
        1850,
    )
    end_of_turn = _stable_int(
        f'{scenario["scenario_id"]}|{stack["id"]}|{noise}|turn',
        170,
        800,
    )
    interruption = _stable_int(
        f'{scenario["scenario_id"]}|{stack["id"]}|{noise}|interrupt',
        72,
        99,
    )

    task_success = wer < 0.22 and response_latency < 1600
    if wer >= 0.22:
        failure_stage = "asr"
    elif end_of_turn > 650:
        failure_stage = "vad"
    elif not task_success:
        failure_stage = "llm"
    else:
        failure_stage = "none"

    return {
        "mode": "simulated",
        "scenario_id": scenario["scenario_id"],
        "domain": scenario["domain"],
        "intent": scenario["intent"],
        "variant": scenario["variant"],
        "noise_profile": noise,
        "stack_id": stack["id"],
        "stack_name": stack["name"],
        "vad": stack["vad"],
        "asr": stack["asr"],
        "llm": stack["llm"],
        "reference_transcript": reference,
        "hypothesis_transcript": hypothesis,
        "wer": round(wer, 4),
        "response_latency_ms": response_latency,
        "end_of_turn_ms": end_of_turn,
        "interruption_score": interruption,
        "task_success": task_success,
        "estimated_cost_usd": round(
            _stable_int(
                f'{scenario["scenario_id"]}|{stack["id"]}|{noise}|cost',
                8,
                42,
            )
            / 1000,
            4,
        ),
        "failure_stage": failure_stage,
    }


def load_stacks(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_simulated(
    output: Path,
    stacks_path: Path,
    max_scenarios: int | None = None,
) -> int:
    scenarios = build_suite()
    if max_scenarios:
        scenarios = scenarios[:max_scenarios]

    stacks = load_stacks(stacks_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    started = time.perf_counter()
    with output.open("w", encoding="utf-8") as handle:
        for scenario in scenarios:
            for noise in scenario["noise_profiles"]:
                for stack in stacks:
                    row = simulate_row(scenario, stack, noise)
                    handle.write(json.dumps(row) + "\n")
                    count += 1

    elapsed = time.perf_counter() - started
    print(
        f"Wrote {count} explicitly simulated benchmark rows to {output} "
        f"in {elapsed:.2f}s"
    )
    return count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["simulate"],
        default="simulate",
        help="Simulation validates the evaluation pipeline only.",
    )
    parser.add_argument(
        "--output",
        default="benchmark/results/simulated_results.jsonl",
    )
    parser.add_argument(
        "--stacks",
        default="benchmark/stacks.json",
    )
    parser.add_argument(
        "--max-scenarios",
        type=int,
        default=None,
    )
    args = parser.parse_args()

    if args.mode == "simulate":
        run_simulated(
            Path(args.output),
            Path(args.stacks),
            args.max_scenarios,
        )


if __name__ == "__main__":
    main()
