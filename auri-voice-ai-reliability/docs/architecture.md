# Auri architecture

## Request lifecycle

1. React requests a presigned S3 upload URL from FastAPI.
2. Audio uploads directly to S3.
3. FastAPI creates a DynamoDB run record and publishes a job to SQS.
4. SQS triggers the dispatcher Lambda.
5. Lambda submits the workload to AWS Batch on Fargate.
6. The worker downloads audio from S3.
7. The AWS-native pipeline invokes Amazon Transcribe.
8. Auri computes WER and transcript accuracy.
9. Amazon Bedrock generates structured failure diagnostics.
10. Raw results are written to S3 and run state is updated in DynamoDB.
11. WER and latency are emitted to CloudWatch.
12. The React client polls the run endpoint to render results.

## Failure isolation

Auri separates infrastructure failure from model-quality failure:

- queue / dispatch: SQS + Lambda
- execution: AWS Batch / Fargate
- ASR: Amazon Transcribe + WER
- diagnosis: Amazon Bedrock
- persistence: S3 + DynamoDB
- observability: CloudWatch
