from app.models import BenchmarkRequest, PipelineSpec
from app.services.benchmark import run_benchmark


def test_benchmark_returns_one_result_per_pipeline():
    request = BenchmarkRequest(
        conversation_id="demo-1",
        transcript_reference="I need to change my delivery address.",
        pipelines=[
            PipelineSpec(
                id="stack-a",
                name="Stack A",
                vad="webrtc",
                asr="deepgram",
                llm="gpt",
            ),
            PipelineSpec(
                id="stack-b",
                name="Stack B",
                vad="silero",
                asr="whisper",
                llm="bedrock",
            ),
        ],
    )

    response = run_benchmark(request)

    assert response.conversation_id == "demo-1"
    assert len(response.results) == 2


def test_benchmark_is_deterministic():
    request = BenchmarkRequest(
        conversation_id="demo-2",
        transcript_reference="Cancel my reservation.",
        pipelines=[
            PipelineSpec(
                id="stack-a",
                name="Stack A",
                vad="webrtc",
                asr="deepgram",
                llm="gpt",
            )
        ],
    )

    first = run_benchmark(request)
    second = run_benchmark(request)

    assert first == second
