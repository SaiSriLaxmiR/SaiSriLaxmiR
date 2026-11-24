from hashlib import sha256

from app.models import (
    BenchmarkRequest,
    BenchmarkResponse,
    PipelineMetrics,
    PipelineResult,
)
from app.services.judge import diagnose
from app.services.metrics import bounded_score


def _stable_number(seed: str, low: int, high: int) -> int:
    digest = sha256(seed.encode("utf-8")).hexdigest()
    raw = int(digest[:8], 16)
    return low + raw % (high - low + 1)


def run_benchmark(request: BenchmarkRequest) -> BenchmarkResponse:
    results: list[PipelineResult] = []

    for pipeline in request.pipelines:
        seed = (
            f"{request.conversation_id}|{pipeline.id}|"
            f"{pipeline.vad}|{pipeline.asr}|{pipeline.llm}"
        )

        transcript_score = bounded_score(
            _stable_number(seed + "|asr", 82, 99)
        )
        end_of_turn_ms = _stable_number(seed + "|vad", 180, 820)
        latency_ms = _stable_number(seed + "|latency", 420, 1900)
        interruption_score = bounded_score(
            _stable_number(seed + "|interrupt", 75, 99)
        )
        task_success = _stable_number(seed + "|task", 0, 9) > 1
        cost = round(
            _stable_number(seed + "|cost", 9, 38) / 1000,
            4,
        )

        metrics = PipelineMetrics(
            pipeline_id=pipeline.id,
            transcript_accuracy=transcript_score,
            end_of_turn_ms=end_of_turn_ms,
            response_latency_ms=latency_ms,
            interruption_score=interruption_score,
            task_success=task_success,
            estimated_cost_usd=cost,
        )

        results.append(
            PipelineResult(
                pipeline=pipeline,
                metrics=metrics,
                diagnostic=diagnose(metrics),
            )
        )

    results.sort(
        key=lambda item: (
            not item.metrics.task_success,
            -item.metrics.transcript_accuracy,
            item.metrics.response_latency_ms,
        )
    )

    return BenchmarkResponse(
        conversation_id=request.conversation_id,
        results=results,
    )
