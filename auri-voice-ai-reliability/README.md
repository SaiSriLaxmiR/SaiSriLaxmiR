# Auri

**Voice AI Reliability & Observability Platform**

Auri is a full-stack developer platform for testing and diagnosing voice AI systems across speech recognition, turn-taking, LLM response quality, latency, and cost. It is designed to help teams compare voice stacks, inspect conversation traces, and localize failures before shipping changes to production.

## Core workflow

1. Upload an audio conversation or record a sample.
2. Choose one or more voice pipelines to benchmark.
3. Run the same input through each pipeline.
4. Compare latency, transcript quality, turn-taking, and AI evaluation.
5. Inspect a trace to see whether the failure came from ASR, turn detection, LLM reasoning, or tool execution.

## Evaluation design

Auri ships with a deterministic evaluation suite of **240 conversation scenarios** spanning **10 domains × 8 intents × 3 language/interaction variants**. Each scenario is evaluated under **3 noise profiles** (clean, cafe, street). Across the **3 configured voice stacks**, a complete benchmark represents up to **2,160 stack-condition evaluations**.

The reporting layer computes:

- word error rate (WER) and transcript accuracy
- p50 / p95 response latency
- p50 / p95 end-of-turn detection latency
- interruption handling score
- task-success rate
- estimated per-run and aggregate cost
- failure-stage counts across VAD, ASR, LLM, and tool execution
- per-noise-profile robustness summaries

The repository includes a clearly labeled simulation mode for validating the benchmark pipeline without paid provider credentials. Simulated outputs are never treated as measured provider performance.

## Stack

- React + Vite frontend
- FastAPI backend
- pluggable VAD / ASR / LLM adapters
- structured LLM-as-Judge diagnostics
- Dockerized benchmark workers
- AWS-ready storage and batch execution hooks
- automated tests

## AWS production architecture

Auri now includes a distributed AWS execution path in addition to the local benchmark harness:

```text
React -> FastAPI -> S3
                  |
                  +-> DynamoDB run state
                  |
                  +-> SQS -> Lambda dispatcher -> AWS Batch / Fargate
                                                   |
                                                   v
                                      Docker benchmark worker
                                         |             |
                                         v             v
                                  Amazon Transcribe  Bedrock
                                         \             /
                                          \           /
                                           v         v
                                        metrics + diagnosis
                                             |
                                  S3 + DynamoDB + CloudWatch
```

Implemented AWS components:

- **Amazon S3** presigned audio uploads and raw result JSON
- **Amazon DynamoDB** benchmark run state and result pointers
- **Amazon SQS** durable benchmark job queue with a dead-letter queue
- **AWS Lambda** queue-to-Batch dispatcher
- **AWS Batch on Fargate** isolated Dockerized benchmark workers
- **Amazon Transcribe** AWS-native ASR adapter
- **Amazon Bedrock** structured failure-stage diagnostics
- **Amazon CloudWatch** custom WER and ASR-latency metrics
- **Amazon ECR** worker image repository template
- **IAM** scoped API, dispatcher, and worker permissions
- **CloudFormation** infrastructure definitions under `infra/`

The infrastructure is implemented as code but is **not represented as deployed production infrastructure until an AWS account deploys the templates and worker image**.

## Architecture

```text
Browser microphone / upload
          |
          v
      React UI
          |
          v
       FastAPI
          |
   +------+------+
   |             |
   v             v
Benchmark     Trace Store
 Engine          |
   |             v
   |         History API
   v
VAD -> ASR -> LLM -> Tool
   |
   +--> latency / accuracy / turn metrics
   |
   +--> LLM-as-Judge diagnostic
          |
          v
 Comparison dashboard
```

## Real public-audio baseline

Auri includes the public `jackhammer.wav` Harvard-sentence sample used in the SpeechRecognition tutorial. The file is **3.347 s, 44.1 kHz, stereo, 16-bit PCM** and contains the reference phrase **"the stale smell of old beer lingers"** under strong jackhammer noise.

Using the published Google Web Speech API outputs for this exact sample, Auri's word-level evaluation computes:

- **42.86% WER / 57.14% word accuracy** without ambient-noise calibration
- **42.86% WER / 57.14% word accuracy** with 1.0 s calibration
- **42.86% WER / 57.14% word accuracy** with 0.5 s calibration

The point of this baseline is to demonstrate measurable noise-induced ASR degradation on real audio. These results are not presented as Deepgram/OpenAI/AWS comparisons; those require running the included provider adapters with valid credentials.

See `benchmark/results/PUBLIC_BASELINE.md` and `benchmark/results/public_jackhammer_baseline.json`.

## Public multi-file ASR comparison

Auri also recomputes WER on **3 LibriSpeech-derived public clips** with published outputs from **Mozilla DeepSpeech** and **Google Cloud Speech-to-Text**.

Across **16 reference words**:

- DeepSpeech: **1 word error / 16 words → 6.25% micro-WER, 93.75% word accuracy**
- Google Cloud Speech-to-Text: **0 word errors / 16 words → 0% micro-WER, 100% word accuracy**

One clip exposed the difference clearly: the reference **"experience proves this"** was transcribed by DeepSpeech as **"experience proof this"**, while the published Google Cloud output matched the reference exactly.

See `benchmark/results/PUBLIC_MULTI_ASR.md` and `benchmark/results/public_multifile_asr_comparison.json`.

## Controlled noise robustness

Auri now includes `benchmark/add_noise.py` to mix clean speech with a public noise sample at an explicit SNR. This supports repeatable robustness experiments such as:

- **20 dB SNR** — light noise
- **10 dB SNR** — moderate noise
- **0 dB SNR** — speech and noise at equal RMS power

This lets the same utterance be evaluated under controlled degradation rather than comparing unrelated noisy clips.

## Automated real-audio robustness benchmark

Auri includes `.github/workflows/auri-real-benchmark.yml`, which is designed to run a fresh **60-condition ASR robustness benchmark**:

- **15 public Mini LibriSpeech utterances**
- **4 acoustic conditions per utterance**: clean, 20 dB, 10 dB, and 0 dB SNR
- public `jackhammer.wav` mixed at controlled SNR
- pretrained **Wav2Vec2 ASR**
- **60 fresh ASR inference runs**
- micro-WER and word accuracy
- exact-match rate
- p50 / p95 inference latency
- p50 / p95 real-time factor
- WER degradation relative to clean speech

The workflow writes `REAL_WAV2VEC2_REPORT.md` and `real_wav2vec2_minilibrispeech.json` when executed. Those generated values should only be quoted after the workflow has completed successfully.

## Benchmark commands

```bash
python -m benchmark.generate_suite
python -m benchmark.run_suite --mode simulate
python -m benchmark.report
pytest benchmark/tests
```

Real-provider adapters are included for Deepgram, OpenAI speech-to-text, and AWS Transcribe. Real benchmark claims should only be made after running the suite with valid provider credentials and real audio.

## Resume-ready description

**Auri | React, FastAPI, Docker, AWS Batch, SQS, S3, DynamoDB, Bedrock**

- Built a full-stack Voice AI reliability platform with a **240-scenario evaluation suite across 10 domains, 8 intents, 3 interaction variants, and 3 noise profiles**, supporting up to **2,160 stack-condition evaluations** across three configurable voice pipelines.
- Engineered WER, **p50/p95 response and end-of-turn latency**, interruption, task-success, cost, and failure-stage reporting, with structured diagnostics that localize errors across **VAD, ASR, LLM, and tool execution**.
