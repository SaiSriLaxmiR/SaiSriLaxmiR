# Auri

**Voice AI Reliability & Observability Platform**

Auri is a full-stack developer platform for testing and diagnosing voice AI systems across speech recognition, turn-taking, LLM response quality, latency, and cost. It is designed to help teams compare voice stacks, inspect conversation traces, and localize failures before shipping changes to production.

## Core workflow

1. Upload an audio conversation or record a sample.
2. Choose one or more voice pipelines to benchmark.
3. Run the same input through each pipeline.
4. Compare latency, transcript quality, turn-taking, and AI evaluation.
5. Inspect a trace to see whether the failure came from ASR, turn detection, LLM reasoning, or tool execution.

## Stack

- React + Vite frontend
- FastAPI backend
- pluggable VAD / ASR / LLM adapters
- structured LLM-as-Judge diagnostics
- Dockerized benchmark workers
- AWS-ready storage and batch execution hooks
- automated tests

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

## Resume-ready description

**Auri | React, FastAPI, WebSockets, Docker, AWS, LLM APIs**

- Built a full-stack Voice AI reliability platform for benchmarking ASR, turn-taking, and LLM pipelines on latency, transcript quality, interruption handling, and end-to-end task performance.
- Added conversation tracing and structured LLM-as-Judge diagnostics to localize failures across speech recognition, turn detection, model reasoning, and tool execution.
