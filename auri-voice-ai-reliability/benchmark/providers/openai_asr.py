from __future__ import annotations

import os
import time
from pathlib import Path

import httpx

from benchmark.providers.base import TranscriptResult


class OpenAIASR:
    def __init__(self, model: str = "gpt-4o-mini-transcribe"):
        self.api_key = os.environ["OPENAI_API_KEY"]
        self.model = model

    def transcribe(self, audio_path: Path) -> TranscriptResult:
        started = time.perf_counter()

        with audio_path.open("rb") as audio_file:
            response = httpx.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                },
                data={"model": self.model},
                files={
                    "file": (
                        audio_path.name,
                        audio_file,
                        "audio/wav",
                    )
                },
                timeout=120,
            )
        response.raise_for_status()
        payload = response.json()
        latency_ms = int((time.perf_counter() - started) * 1000)

        # Cost uses measured audio duration from the runner when available.
        # This adapter records request cost as zero unless an override is set.
        request_cost = float(
            os.environ.get("OPENAI_TRANSCRIPTION_COST_OVERRIDE", "0")
        )

        return TranscriptResult(
            text=payload["text"],
            latency_ms=latency_ms,
            estimated_cost_usd=request_cost,
            provider=f"openai:{self.model}",
        )
