from __future__ import annotations

import json
import os

import boto3

batch = boto3.client("batch")
JOB_QUEUE = os.environ["AURI_BATCH_JOB_QUEUE"]
JOB_DEFINITION = os.environ["AURI_BATCH_JOB_DEFINITION"]


def handler(event, _context):
    failures = []
    for record in event.get("Records", []):
        try:
            payload = json.loads(record["body"])
            run_id = payload["run_id"]
            batch.submit_job(
                jobName=f"auri-{run_id[:32]}",
                jobQueue=JOB_QUEUE,
                jobDefinition=JOB_DEFINITION,
                containerOverrides={
                    "environment": [
                        {
                            "name": "AURI_JOB_PAYLOAD",
                            "value": json.dumps(payload),
                        }
                    ]
                },
            )
        except Exception:
            failures.append({"itemIdentifier": record.get("messageId", "unknown")})
    return {"batchItemFailures": failures}
