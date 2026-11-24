from typing import Literal

from pydantic import BaseModel, Field


class PipelineSpec(BaseModel):
    id: str
    name: str
    vad: str
    asr: str
    llm: str


class BenchmarkRequest(BaseModel):
    conversation_id: str
    transcript_reference: str
    pipelines: list[PipelineSpec]


class PipelineMetrics(BaseModel):
    pipeline_id: str
    transcript_accuracy: float = Field(ge=0, le=100)
    end_of_turn_ms: int = Field(ge=0)
    response_latency_ms: int = Field(ge=0)
    interruption_score: float = Field(ge=0, le=100)
    task_success: bool
    estimated_cost_usd: float = Field(ge=0)


class JudgeDiagnostic(BaseModel):
    stage: Literal["vad", "asr", "llm", "tool", "none"]
    severity: Literal["low", "medium", "high"]
    summary: str
    recommendation: str
    grounded: bool = True


class PipelineResult(BaseModel):
    pipeline: PipelineSpec
    metrics: PipelineMetrics
    diagnostic: JudgeDiagnostic


class BenchmarkResponse(BaseModel):
    conversation_id: str
    results: list[PipelineResult]
