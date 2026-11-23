#!/usr/bin/env python3
import argparse
import base64
from pathlib import Path

parser = argparse.ArgumentParser(description="Base64-encode an image for API requests.")
parser.add_argument("image", type=Path)
args = parser.parse_args()
print(base64.b64encode(args.image.read_bytes()).decode())
