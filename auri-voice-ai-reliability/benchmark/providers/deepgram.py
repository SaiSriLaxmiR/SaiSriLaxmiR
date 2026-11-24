from __future__ import annotations

import os
import time
from pathlib import Path

import httpx

from benchmark.providers.base import TranscriptResult


class DeepgramASR:
    def __init__(self, model: str = "nova-3"):
        self.api_key = os.environ["DEEPGRAM_API_KEY"]
        self.model = model

    def transcribe(self, audio_path: Path) -> TranscriptResult:
        started = time.perf_counter()
        audio = audio_path.read_bytes()

        response = httpx.post(
            "https://api.deepgram.com/v1/listen",
            params={
                "model": self.model,
                "smart_format": "true",
            },
            headers={
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "audio/wav",
            },
            content=audio,
            timeout=120,
        )
        response.raise_for_status()
        payload = response.json()

        transcript = (
            payload["results"]["channels"][0]["alternatives"][0]["transcript"]
        )
        duration_s = float(payload.get("metadata", {}).get("duration", 0) or 0)
        latency_ms = int((time.perf_counter() - started) * 1000)

        # Pricing is intentionally configurable rather than hard-coded because
        # provider prices change. Set DEEPGRAM_COST_PER_MINUTE for cost metrics.
        cost_per_min = float(os.environ.get("DEEPGRAM_COST_PER_MINUTE", "0"))
        cost = duration_s / 60.0 * cost_per_min

        return TranscriptResult(
            text=transcript,
            latency_ms=latency_ms,
            estimated_cost_usd=round(cost, 6),
            provider=f"deepgram:{self.model}",
        )
