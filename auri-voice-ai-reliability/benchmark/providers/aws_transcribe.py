from __future__ import annotations

import json
import os
import time
import urllib.request
import uuid
from pathlib import Path

import boto3

from benchmark.providers.base import TranscriptResult


class AWSTranscribeASR:
    def __init__(self):
        self.bucket = os.environ["AURI_AUDIO_BUCKET"]
        self.region = os.environ.get("AWS_REGION", "us-west-2")
        self.s3 = boto3.client("s3", region_name=self.region)
        self.transcribe = boto3.client(
            "transcribe",
            region_name=self.region,
        )

    def transcribe_audio(self, audio_path: Path) -> TranscriptResult:
        object_key = f"auri-benchmarks/{uuid.uuid4().hex}/{audio_path.name}"
        self.s3.upload_file(str(audio_path), self.bucket, object_key)

        job_name = f"auri-{uuid.uuid4().hex}"
        media_uri = f"s3://{self.bucket}/{object_key}"
        started = time.perf_counter()

        self.transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": media_uri},
            MediaFormat="wav",
            LanguageCode="en-US",
        )

        while True:
            status = self.transcribe.get_transcription_job(
                TranscriptionJobName=job_name
            )["TranscriptionJob"]
            if status["TranscriptionJobStatus"] in {
                "COMPLETED",
                "FAILED",
            }:
                break
            time.sleep(2)

        if status["TranscriptionJobStatus"] != "COMPLETED":
            raise RuntimeError(
                status.get("FailureReason", "AWS Transcribe job failed")
            )

        with urllib.request.urlopen(
            status["Transcript"]["TranscriptFileUri"]
        ) as response:
            payload = json.load(response)

        latency_ms = int((time.perf_counter() - started) * 1000)
        transcript = payload["results"]["transcripts"][0]["transcript"]

        return TranscriptResult(
            text=transcript,
            latency_ms=latency_ms,
            estimated_cost_usd=float(
                os.environ.get("AWS_TRANSCRIBE_COST_OVERRIDE", "0")
            ),
            provider="aws-transcribe",
        )

    def transcribe(self, audio_path: Path) -> TranscriptResult:
        return self.transcribe_audio(audio_path)
