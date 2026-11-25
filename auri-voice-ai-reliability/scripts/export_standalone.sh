#!/usr/bin/env bash
set -euo pipefail

# Run this from the root of SaiSriLaxmiR/SaiSriLaxmiR.
# It creates a clean branch whose repository root is the Auri project.

BRANCH_NAME="${1:-auri-standalone}"

git subtree split \
  --prefix=auri-voice-ai-reliability \
  --branch "$BRANCH_NAME"

echo
echo "Created branch: $BRANCH_NAME"
echo "Push it to a new empty repository with:"
echo "  git push <auri-repo-url> $BRANCH_NAME:main"
