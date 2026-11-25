from __future__ import annotations

import json
import os
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import boto3

from benchmark.metrics import word_error_rate
from benchmark.providers.aws_transcribe import AWSTranscribeASR

REGION = os.environ.get("AWS_REGION", "us-west-2")
AUDIO_BUCKET = os.environ["AURI_AUDIO_BUCKET"]
RESULTS_BUCKET = os.environ.get("AURI_RESULTS_BUCKET", AUDIO_BUCKET)
RUNS_TABLE = os.environ["AURI_RUNS_TABLE"]
BEDROCK_MODEL_ID = os.environ.get(
    "AURI_BEDROCK_MODEL_ID",
    "anthropic.claude-3-5-haiku-20241022-v1:0",
)

s3 = boto3.client("s3", region_name=REGION)
cloudwatch = boto3.client("cloudwatch", region_name=REGION)
bedrock = boto3.client("bedrock-runtime", region_name=REGION)
ddb = boto3.resource("dynamodb", region_name=REGION).Table(RUNS_TABLE)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def update_run(run_id: str, **values):
    names = {}
    value_map = {}
    expressions = []
    for i, (key, value) in enumerate(values.items()):
        name_key = f"#n{i}"
        value_key = f":v{i}"
        names[name_key] = key
        value_map[value_key] = value
        expressions.append(f"{name_key} = {value_key}")

    ddb.update_item(
        Key={"run_id": run_id},
        UpdateExpression="SET " + ", ".join(expressions),
        ExpressionAttributeNames=names,
        ExpressionAttributeValues=value_map,
    )


def bedrock_diagnostic(reference: str, transcript: str, wer: float) -> dict:
    prompt = {
        "reference": reference,
        "transcript": transcript,
        "wer": round(wer, 4),
        "task": (
            "Return JSON only with keys failure_stage, severity, summary, "
            "recommendation. failure_stage must be one of vad, asr, llm, "
            "tool, none."
        ),
    }
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 350,
        "temperature": 0,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": json.dumps(prompt)}],
            }
        ],
    }
    response = bedrock.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json",
    )
    payload = json.loads(response["body"].read())
    text = payload["content"][0]["text"]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "failure_stage": "asr" if wer > 0.2 else "none",
            "severity": "high" if wer > 0.4 else "medium",
            "summary": text[:500],
            "recommendation": "Inspect the transcript and provider trace.",
        }


def emit_metrics(stack_id: str, wer: float, latency_ms: int):
    cloudwatch.put_metric_data(
        Namespace="Auri/Benchmarks",
        MetricData=[
            {
                "MetricName": "WER",
                "Dimensions": [{"Name": "Stack", "Value": stack_id}],
                "Value": float(wer),
                "Unit": "None",
            },
            {
                "MetricName": "ASRLatency",
                "Dimensions": [{"Name": "Stack", "Value": stack_id}],
                "Value": float(latency_ms),
                "Unit": "Milliseconds",
            },
        ],
    )


def run():
    payload = json.loads(os.environ["AURI_JOB_PAYLOAD"])
    run_id = payload["run_id"]
    reference = payload["reference_transcript"]
    selected_stacks = payload["selected_stacks"]

    update_run(run_id, status="RUNNING", updated_at=now())

    with tempfile.TemporaryDirectory() as tmp:
        audio_path = Path(tmp) / "input.wav"
        s3.download_file(AUDIO_BUCKET, payload["audio_s3_key"], str(audio_path))

        results = []
        for stack_id in selected_stacks:
            if stack_id != "aws-native":
                results.append(
                    {
                        "stack_id": stack_id,
                        "status": "SKIPPED",
                        "reason": "Provider credentials not configured in this worker.",
                    }
                )
                continue

            started = time.perf_counter()
            transcript = AWSTranscribeASR().transcribe(audio_path)
            wer = word_error_rate(reference, transcript.text)
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            diagnostic = bedrock_diagnostic(reference, transcript.text, wer)
            emit_metrics(stack_id, wer, transcript.latency_ms)

            results.append(
                {
                    "stack_id": stack_id,
                    "status": "COMPLETED",
                    "transcript": transcript.text,
                    "wer": round(wer, 4),
                    "transcript_accuracy_percent": round(
                        max(0.0, 1.0 - wer) * 100,
                        2,
                    ),
                    "asr_latency_ms": transcript.latency_ms,
                    "worker_elapsed_ms": elapsed_ms,
                    "diagnostic": diagnostic,
                }
            )

    result = {
        "run_id": run_id,
        "completed_at": now(),
        "reference_transcript": reference,
        "results": results,
    }
    result_key = f"results/{run_id}/result.json"
    s3.put_object(
        Bucket=RESULTS_BUCKET,
        Key=result_key,
        Body=json.dumps(result, indent=2).encode("utf-8"),
        ContentType="application/json",
        ServerSideEncryption="AES256",
    )
    update_run(
        run_id,
        status="COMPLETED",
        updated_at=now(),
        result_s3_key=result_key,
        result_summary=json.dumps(results),
    )


if __name__ == "__main__":
    try:
        run()
    except Exception as exc:
        payload = json.loads(os.environ.get("AURI_JOB_PAYLOAD", "{}"))
        run_id = payload.get("run_id")
        if run_id:
            update_run(
                run_id,
                status="FAILED",
                updated_at=now(),
                error_message=str(exc)[:1000],
            )
        raise
