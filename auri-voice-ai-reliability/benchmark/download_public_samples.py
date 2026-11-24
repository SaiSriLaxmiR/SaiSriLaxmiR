"""Download provenance-linked public ASR samples used by Auri.

The Mozilla DeepSpeech 0.9.3 release publishes a small audio archive containing
three LibriSpeech-derived WAV files used by many speech-recognition examples.

Usage:
    python -m benchmark.download_public_samples --output benchmark/data/public/deepspeech

The script intentionally keeps the audio external to normal source control and
records the download URL so the benchmark is reproducible.
"""

from __future__ import annotations

import argparse
import io
import tarfile
import urllib.request
from pathlib import Path

ARCHIVE_URL = (
    "https://github.com/mozilla/DeepSpeech/releases/download/"
    "v0.9.3/audio-0.9.3.tar.gz"
)

KEEP = {
    "audio/8455-210777-0068.wav",
    "audio/4507-16021-0012.wav",
    "audio/2830-3980-0043.wav",
    "audio/Attribution.txt",
    "audio/License.txt",
}


def download(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(ARCHIVE_URL) as response:
        payload = response.read()

    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as archive:
        for member in archive.getmembers():
            if member.name not in KEEP:
                continue
            member.name = Path(member.name).name
            archive.extract(member, output)

    (output / "SOURCE.txt").write_text(
        ARCHIVE_URL + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="benchmark/data/public/deepspeech",
    )
    args = parser.parse_args()
    download(Path(args.output))
    print(f"Downloaded public benchmark samples to {args.output}")
