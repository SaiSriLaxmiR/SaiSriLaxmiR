from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass
class TranscriptResult:
    text: str
    latency_ms: int
    estimated_cost_usd: float
    provider: str


class ASRProvider(Protocol):
    def transcribe(self, audio_path: Path) -> TranscriptResult:
        ...
