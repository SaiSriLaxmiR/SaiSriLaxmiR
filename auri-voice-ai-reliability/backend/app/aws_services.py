from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone

import boto3

REGION = os.environ.get("AWS_REGION", "us-west-2")
AUDIO_BUCKET = os.environ.get("AURI_AUDIO_BUCKET", "")
RUNS_TABLE = os.environ.get("AURI_RUNS_TABLE", "")
RUN_QUEUE_URL = os.environ.get("AURI_RUN_QUEUE_URL", "")

s3 = boto3.client("s3", region_name=REGION)
sqs = boto3.client("sqs", region_name=REGION)
dynamodb = boto3.resource("dynamodb", region_name=REGION)


def _table():
    if not RUNS_TABLE:
        raise RuntimeError("AURI_RUNS_TABLE is not configured")
    return dynamodb.Table(RUNS_TABLE)


def create_upload_url(filename: str, content_type: str) -> dict:
    if not AUDIO_BUCKET:
        raise RuntimeError("AURI_AUDIO_BUCKET is not configured")

    object_key = f"uploads/{uuid.uuid4().hex}/{filename}"
    url = s3.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": AUDIO_BUCKET,
            "Key": object_key,
            "ContentType": content_type,
        },
        ExpiresIn=900,
    )
    return {
        "upload_url": url,
        "bucket": AUDIO_BUCKET,
        "object_key": object_key,
        "expires_in_seconds": 900,
    }


def enqueue_run(payload: dict) -> dict:
    if not RUN_QUEUE_URL:
        raise RuntimeError("AURI_RUN_QUEUE_URL is not configured")

    run_id = payload.get("run_id") or uuid.uuid4().hex
    now = datetime.now(timezone.utc).isoformat()

    item = {
        "run_id": run_id,
        "status": "QUEUED",
        "created_at": now,
        "updated_at": now,
        "audio_s3_key": payload["audio_s3_key"],
        "reference_transcript": payload["reference_transcript"],
        "selected_stacks": payload["selected_stacks"],
    }
    _table().put_item(Item=item)

    sqs.send_message(
        QueueUrl=RUN_QUEUE_URL,
        MessageBody=json.dumps({**payload, "run_id": run_id}),
    )
    return item


def get_run(run_id: str) -> dict | None:
    response = _table().get_item(Key={"run_id": run_id})
    return response.get("Item")
