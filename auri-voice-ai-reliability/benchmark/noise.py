"""PCM WAV noise augmentation utilities for controlled robustness tests."""

from __future__ import annotations

import math
import random
import wave
from array import array
from pathlib import Path

PROFILE_SNR_DB = {
    "clean": None,
    "cafe": 18.0,
    "street": 10.0,
}


def add_white_noise(
    source: str | Path,
    destination: str | Path,
    profile: str,
    seed: int = 42,
) -> None:
    if profile not in PROFILE_SNR_DB:
        raise ValueError(f"Unknown noise profile: {profile}")

    snr_db = PROFILE_SNR_DB[profile]
    source = Path(source)
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)

    with wave.open(str(source), "rb") as reader:
        params = reader.getparams()
        if params.sampwidth != 2:
            raise ValueError("Noise augmentation expects 16-bit PCM WAV")
        frames = reader.readframes(reader.getnframes())

    samples = array("h")
    samples.frombytes(frames)

    if snr_db is None:
        destination.write_bytes(source.read_bytes())
        return

    signal_rms = math.sqrt(
        sum(float(sample) ** 2 for sample in samples)
        / max(len(samples), 1)
    )
    noise_rms = signal_rms / (10 ** (snr_db / 20.0))

    rng = random.Random(seed)
    augmented = array("h")
    for sample in samples:
        noisy = int(sample + rng.gauss(0, noise_rms))
        augmented.append(max(-32768, min(32767, noisy)))

    with wave.open(str(destination), "wb") as writer:
        writer.setparams(params)
        writer.writeframes(augmented.tobytes())
