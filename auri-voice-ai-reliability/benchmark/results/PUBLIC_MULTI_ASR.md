# Public Multi-File ASR Comparison

Auri recomputes word error rate on three public LibriSpeech-derived test clips for which ground-truth transcripts and published recognizer outputs are available.

| Clip | Reference words | DeepSpeech WER | Google Cloud WER |
|---|---:|---:|---:|
| 8455-210777-0068.wav | 6 | 0.00% | 0.00% |
| 4507-16021-0012.wav | 7 | 0.00% | 0.00% |
| 2830-3980-0043.wav | 3 | 33.33% | 0.00% |
| **Micro-average** | **16** | **6.25%** | **0.00%** |

Across the three clips, the published DeepSpeech outputs contain **1 word error across 16 reference words** (micro-WER **6.25%**, word accuracy **93.75%**). The published Google Cloud outputs match all **16/16** reference words (micro-WER **0%**).

This file reports Auri's metric computation over public transcripts. It does not claim that Auri itself invoked these historical cloud/model versions.
