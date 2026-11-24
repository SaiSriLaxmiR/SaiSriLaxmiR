# Public Audio Baseline

Auri includes a real noisy speech sample from the public SpeechRecognition tutorial: `jackhammer.wav`.

## Audio

- Reference phrase: **the stale smell of old beer lingers**
- Duration: **3.347 s**
- Sample rate: **44.1 kHz**
- Channels: **2**
- Encoding: **16-bit PCM WAV**
- Peak amplitude: **0.3797**
- Clipping: **0%**

## Recognition baseline

| Condition | Transcript | WER | Word accuracy |
|---|---|---:|---:|
| No ambient calibration | the snail smell of old gear vendors | **42.86%** | **57.14%** |
| 1.0 s calibration | still smell of old beer vendors | **42.86%** | **57.14%** |
| 0.5 s calibration | the snail smell like old Beer Mongers | **42.86%** | **57.14%** |

The recognition outputs are published for this exact WAV sample in Real Python's SpeechRecognition tutorial. Auri recomputes WER against the published reference transcript. This demonstrates the degradation caused by strong background noise without presenting the result as a comparison of Auri's paid-provider adapters.

## Provenance

- Audio: Real Python / SpeechRecognition example repository
- Sentence family: Harvard Sentences
- ASR outputs: Google Web Speech API outputs documented in the tutorial
