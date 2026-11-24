from app.models import JudgeDiagnostic, PipelineMetrics


def diagnose(metrics: PipelineMetrics) -> JudgeDiagnostic:
    if metrics.transcript_accuracy < 85:
        return JudgeDiagnostic(
            stage="asr",
            severity="high",
            summary="Transcript quality is the primary reliability bottleneck.",
            recommendation="Review the ASR provider, microphone quality, and noise handling before tuning the LLM.",
        )

    if metrics.end_of_turn_ms > 650:
        return JudgeDiagnostic(
            stage="vad",
            severity="medium",
            summary="Turn completion is detected too slowly, making the agent feel unresponsive.",
            recommendation="Reduce silence thresholds or compare an alternate VAD configuration.",
        )

    if not metrics.task_success:
        return JudgeDiagnostic(
            stage="llm",
            severity="high",
            summary="The transcript is usable, but the downstream agent did not complete the intended task.",
            recommendation="Inspect the prompt, tool-selection trace, and task-verification logic.",
        )

    if metrics.response_latency_ms > 1500:
        return JudgeDiagnostic(
            stage="llm",
            severity="medium",
            summary="End-to-end response latency is high despite acceptable speech recognition.",
            recommendation="Profile model inference, tool calls, and network hops.",
        )

    return JudgeDiagnostic(
        stage="none",
        severity="low",
        summary="No dominant reliability failure was detected in this run.",
        recommendation="Keep this stack as a baseline and monitor regressions across new audio conditions.",
    )
