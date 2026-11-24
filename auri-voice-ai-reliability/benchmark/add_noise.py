"""Mix clean speech with a noise WAV at a target SNR.

This lets Auri evaluate the same utterance at controlled 20/10/0 dB conditions
using public noise sources such as MUSAN.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import soundfile as sf


def _mono(signal: np.ndarray) -> np.ndarray:
    if signal.ndim == 1:
        return signal.astype(np.float32)
    return signal.mean(axis=1).astype(np.float32)


def mix_at_snr(
    speech: np.ndarray,
    noise: np.ndarray,
    snr_db: float,
) -> np.ndarray:
    speech = _mono(speech)
    noise = _mono(noise)

    if len(noise) < len(speech):
        repeats = int(np.ceil(len(speech) / len(noise)))
        noise = np.tile(noise, repeats)
    noise = noise[: len(speech)]

    speech_rms = np.sqrt(np.mean(speech**2) + 1e-12)
    noise_rms = np.sqrt(np.mean(noise**2) + 1e-12)
    target_noise_rms = speech_rms / (10 ** (snr_db / 20))
    scaled_noise = noise * (target_noise_rms / noise_rms)

    mixed = speech + scaled_noise
    peak = np.max(np.abs(mixed))
    if peak > 1.0:
        mixed = mixed / peak
    return mixed.astype(np.float32)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("speech")
    parser.add_argument("noise")
    parser.add_argument("output")
    parser.add_argument("--snr-db", type=float, required=True)
    args = parser.parse_args()

    speech, speech_rate = sf.read(args.speech)
    noise, noise_rate = sf.read(args.noise)
    if speech_rate != noise_rate:
        raise ValueError(
            f"sample-rate mismatch: speech={speech_rate}, noise={noise_rate}"
        )

    mixed = mix_at_snr(speech, noise, args.snr_db)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    sf.write(args.output, mixed, speech_rate)


if __name__ == "__main__":
    main()
