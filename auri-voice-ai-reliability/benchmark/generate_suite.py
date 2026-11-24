"""Generate Auri's deterministic 240-scenario evaluation suite.

10 domains x 8 intents x 3 language variants = 240 conversation scenarios.
Each scenario is evaluated under clean, cafe, and street noise profiles,
creating 720 audio-condition evaluations when all profiles are enabled.
"""

from __future__ import annotations

import json
from pathlib import Path

DOMAINS = [
    "retail",
    "banking",
    "travel",
    "healthcare",
    "telecom",
    "food_delivery",
    "insurance",
    "utilities",
    "hospitality",
    "appointments",
]

INTENTS = [
    ("change_address", "change the delivery address on my account"),
    ("cancel", "cancel my current request"),
    ("refund", "request a refund for the latest charge"),
    ("reschedule", "reschedule my appointment to tomorrow"),
    ("status", "check the status of my request"),
    ("update_payment", "update the payment method on file"),
    ("speak_to_agent", "speak with a human agent"),
    ("confirm_details", "confirm the details before you continue"),
]

VARIANTS = [
    ("direct", "I need to {intent}."),
    ("polite", "Hi, could you please help me {intent}?"),
    ("self_correction", "I want to {intent}—actually, please make sure you confirm it with me first."),
]

NOISE_PROFILES = ["clean", "cafe", "street"]


def build_suite() -> list[dict]:
    rows: list[dict] = []
    index = 1

    for domain in DOMAINS:
        for intent_id, intent_text in INTENTS:
            for variant_id, template in VARIANTS:
                transcript = template.format(intent=intent_text)
                rows.append(
                    {
                        "scenario_id": f"auri-{index:03d}",
                        "domain": domain,
                        "intent": intent_id,
                        "variant": variant_id,
                        "reference_transcript": transcript,
                        "expected_action": intent_id,
                        "noise_profiles": NOISE_PROFILES,
                    }
                )
                index += 1

    assert len(rows) == 240
    return rows


def write_suite(path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = build_suite()
    path.write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    output = Path("benchmark/data/scenarios.jsonl")
    write_suite(output)
    print(f"Wrote 240 scenarios to {output}")
    print("With 3 noise profiles: 720 evaluation conditions")
