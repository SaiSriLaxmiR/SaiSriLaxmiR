"""Aggregate Auri raw benchmark results into stack-level reports."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from benchmark.metrics import summarize


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def build_report(rows: list[dict]) -> dict:
    by_stack: dict[str, list[dict]] = defaultdict(list)
    by_stack_noise: dict[tuple[str, str], list[dict]] = defaultdict(list)

    for row in rows:
        by_stack[row["stack_id"]].append(row)
        by_stack_noise[
            (row["stack_id"], row["noise_profile"])
        ].append(row)

    mode_values = sorted({row.get("mode", "unknown") for row in rows})

    stacks = {}
    for stack_id, stack_rows in by_stack.items():
        stack_name = stack_rows[0].get("stack_name", stack_id)
        stacks[stack_id] = {
            "name": stack_name,
            "overall": summarize(stack_rows),
            "by_noise": {
                noise: summarize(by_stack_noise[(stack_id, noise)])
                for noise in ("clean", "cafe", "street")
                if by_stack_noise[(stack_id, noise)]
            },
        }

    return {
        "result_mode": mode_values,
        "claim_safety": (
            "Simulated results validate the benchmark pipeline and must not "
            "be presented as measured provider performance."
            if "simulated" in mode_values
            else "Measured results. Verify provider configuration and dataset provenance."
        ),
        "total_rows": len(rows),
        "unique_scenarios": len({row["scenario_id"] for row in rows}),
        "noise_profiles": sorted({row["noise_profile"] for row in rows}),
        "stacks": stacks,
    }


def write_markdown(report: dict, path: Path) -> None:
    lines = [
        "# Auri Benchmark Report",
        "",
        f"**Mode:** {', '.join(report['result_mode'])}",
        "",
        f"> {report['claim_safety']}",
        "",
        f"- Evaluation rows: **{report['total_rows']}**",
        f"- Unique scenarios: **{report['unique_scenarios']}**",
        f"- Noise profiles: **{len(report['noise_profiles'])}**",
        "",
        "## Stack summary",
        "",
        "| Stack | Runs | Mean WER | p50 latency | p95 latency | Task success | Cost |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]

    for stack in report["stacks"].values():
        s = stack["overall"]
        lines.append(
            f"| {stack['name']} | {s['runs']} | {s['mean_wer']:.3f} | "
            f"{s['p50_response_latency_ms']:.0f} ms | "
            f"{s['p95_response_latency_ms']:.0f} ms | "
            f"{s['task_success_rate']:.1f}% | "
            f"${s['total_estimated_cost_usd']:.3f} |"
        )

    lines.extend(
        [
            "",
            "## Noise robustness",
            "",
            "| Stack | Noise | Mean WER | p95 latency | Task success |",
            "|---|---|---:|---:|---:|",
        ]
    )

    for stack in report["stacks"].values():
        for noise, s in stack["by_noise"].items():
            lines.append(
                f"| {stack['name']} | {noise} | {s['mean_wer']:.3f} | "
                f"{s['p95_response_latency_ms']:.0f} ms | "
                f"{s['task_success_rate']:.1f}% |"
            )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input",
        nargs="?",
        default="benchmark/results/simulated_results.jsonl",
    )
    parser.add_argument(
        "--json-output",
        default="benchmark/results/summary.json",
    )
    parser.add_argument(
        "--markdown-output",
        default="benchmark/results/REPORT.md",
    )
    args = parser.parse_args()

    rows = read_jsonl(Path(args.input))
    report = build_report(rows)

    json_path = Path(args.json_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    write_markdown(report, Path(args.markdown_output))

    print(f"Wrote {json_path} and {args.markdown_output}")


if __name__ == "__main__":
    main()
