from benchmark.report import build_report


def test_report_groups_stack_and_noise():
    rows = [
        {
            "mode": "simulated",
            "scenario_id": "a-1",
            "noise_profile": "clean",
            "stack_id": "s1",
            "stack_name": "Stack 1",
            "wer": 0.1,
            "response_latency_ms": 500,
            "end_of_turn_ms": 250,
            "task_success": True,
            "estimated_cost_usd": 0.01,
            "failure_stage": "none",
        },
        {
            "mode": "simulated",
            "scenario_id": "a-1",
            "noise_profile": "cafe",
            "stack_id": "s1",
            "stack_name": "Stack 1",
            "wer": 0.2,
            "response_latency_ms": 700,
            "end_of_turn_ms": 350,
            "task_success": False,
            "estimated_cost_usd": 0.01,
            "failure_stage": "asr",
        },
    ]

    report = build_report(rows)

    assert report["total_rows"] == 2
    assert report["unique_scenarios"] == 1
    assert report["stacks"]["s1"]["overall"]["runs"] == 2
    assert report["stacks"]["s1"]["overall"]["task_success_rate"] == 50.0
    assert "simulated" in report["result_mode"]
