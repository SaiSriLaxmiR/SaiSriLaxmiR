# Auri AWS infrastructure

Production path:

React / FastAPI -> S3 upload -> DynamoDB run record -> SQS -> Lambda dispatcher -> AWS Batch/Fargate -> Transcribe + Bedrock -> S3/DynamoDB -> CloudWatch.

## Services

- S3: raw audio and result JSON
- DynamoDB: run state and result pointers
- SQS: durable benchmark queue
- Lambda: queue-to-Batch dispatcher
- AWS Batch/Fargate: isolated Docker workers
- Amazon Transcribe: AWS-native ASR
- Amazon Bedrock: structured failure diagnosis
- CloudWatch: WER and latency metrics
- IAM: least-privilege service roles
